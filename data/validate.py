"""Every data check, on the full build.

    python -m data.validate --config configs/data/v1.yaml

Writes `data/v1/validation_report.md` -- one row per check with PASS/FAIL and
the measured numbers -- and exits non-zero if anything failed. A1-A18 are the
checks named in the data plan; `tests/` proves the same properties on
miniature fixtures in seconds, while this runs them on the real article.

    --skip A1,A7       skip named checks (A1 rebuilds, A7 re-hashes 13-grams)
    --only A3,A5       run only these
    --check-source     additionally re-stream the pinned Pile and verify every
                       held-out document's subject against meta.pile_set_name
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

import numpy as np

from data import pack
from data.common import (ROOT, DataConfig, TOKEN_DTYPE, get_encoder, keyed_rng,
                         load_config, ngram_hashes, overlap_rate, read_jsonl,
                         text_sha256)

EOT = 50256


# ---------------------------------------------------------------------------
# result plumbing
# ---------------------------------------------------------------------------
@dataclass
class Check:
    id: str
    title: str
    passed: bool
    detail: str
    numbers: Dict[str, Any] = field(default_factory=dict)
    seconds: float = 0.0
    skipped: bool = False

    @property
    def status(self) -> str:
        return "SKIP" if self.skipped else ("PASS" if self.passed else "FAIL")


class Ctx:
    """Loaded once, shared by the checks that need it."""

    def __init__(self, cfg: DataConfig):
        self.cfg = cfg
        self.enc = get_encoder(cfg.tokenizer_name, cfg.vocab_size)
        self.train = np.memmap(cfg.tokens_dir / "train.bin", dtype=TOKEN_DTYPE,
                               mode="r")
        self.train_idx = pack.read_index(cfg.tokens_dir / "train.idx.parquet")
        self.held: Dict[str, np.memmap] = {}
        self.held_idx: Dict[str, Dict[str, Any]] = {}
        for half in cfg.pack_halves:
            self.held[half] = np.memmap(cfg.heldout_tokens_dir / f"{half}.bin",
                                        dtype=TOKEN_DTYPE, mode="r")
            self.held_idx[half] = pack.read_index(
                cfg.heldout_tokens_dir / f"{half}.idx.parquet")
        self.people = {p["person_id"]: p
                       for p in read_jsonl(cfg.bios_dir / "people.jsonl")}
        self._subject_of_token: Optional[np.ndarray] = None
        self._train_texts: Optional[Dict[str, str]] = None

    @property
    def subjects(self) -> List[str]:
        return list(self.cfg.all_subjects)

    def subject_codes(self) -> Tuple[np.ndarray, List[str]]:
        """A subject label per token position in train.bin (255 = EOT/pad).

        150 MB of int8, and it makes the window-share and tiling checks exact
        rather than approximate.
        """
        if self._subject_of_token is None:
            names = self.cfg.train_subjects + [pack.BIO_SUBJECT]
            code = {s: i for i, s in enumerate(names)}
            arr = np.full(self.train.size, 255, dtype=np.uint8)
            idx = self.train_idx
            for s, st, ln in zip(idx["subject"], idx["start"], idx["length"]):
                arr[int(st):int(st) + int(ln)] = code[s]
            self._subject_of_token = arr
            self._codes = names
        return self._subject_of_token, self._codes

    def train_doc_texts(self) -> Dict[str, str]:
        """Cleaned text of every document that reaches train.bin."""
        if self._train_texts is None:
            out: Dict[str, str] = {}
            for s in self.cfg.train_subjects:
                for r in read_jsonl(self.cfg.train_dir /
                                    f"{self.cfg.slug(s)}.jsonl.gz"):
                    out[r["doc_id"]] = r["text"]
            for r in read_jsonl(self.cfg.bios_dir / "bios_train.jsonl"):
                out[r["doc_id"]] = r["text"]
            self._train_texts = out
        return self._train_texts

    def heldout_records(self, half: str) -> List[Dict[str, Any]]:
        out = []
        for s in self.cfg.all_subjects:
            out += list(read_jsonl(self.cfg.heldout_dir / half /
                                   f"{self.cfg.slug(s)}.jsonl.gz"))
        return out


def _bundle_hashes(cfg: DataConfig) -> Dict[str, str]:
    from data.manifest import iter_bundle_files, sha256_file
    return {p.relative_to(cfg.root).as_posix(): sha256_file(p)
            for p in iter_bundle_files(cfg.root)}


# ---------------------------------------------------------------------------
# A1 - A2
# ---------------------------------------------------------------------------
def a1_rebuild(ctx: Ctx) -> Check:
    """Rebuild the derived stages and compare every bundle file's hash."""
    import subprocess
    cfg = ctx.cfg
    before = _bundle_hashes(cfg)
    cmds = [
        [sys.executable, "-m", "data.build", "--config", cfg.config_path,
         "--stage", "pile"],
        [sys.executable, "-m", "data.bios", "--config", cfg.config_path],
        [sys.executable, "-m", "data.bios_sample", "--config", cfg.config_path,
         "--n", "20"],
        [sys.executable, "-m", "data.pack", "--config", cfg.config_path],
        [sys.executable, "-m", "data.manifest", "--config", cfg.config_path],
    ]
    for cmd in cmds:
        print(f"[validate] A1 rebuilding: {' '.join(cmd[2:])}", flush=True)
        r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
        if r.returncode != 0:
            return Check("A1", "Rebuild is byte-identical", False,
                         f"`{' '.join(cmd[2:])}` exited {r.returncode}: "
                         f"{r.stderr.strip()[-300:]}")
    after = _bundle_hashes(cfg)
    changed = sorted(k for k in before if before.get(k) != after.get(k))
    added = sorted(set(after) - set(before))
    removed = sorted(set(before) - set(after))
    ok = not changed and not added and not removed
    return Check("A1", "Rebuild is byte-identical", ok,
                 f"{len(before)} files hashed; {len(changed)} changed, "
                 f"{len(added)} added, {len(removed)} removed"
                 + (f". Changed: {changed[:6]}" if changed else ""),
                 {"files": len(before), "changed": len(changed),
                  "changed_paths": changed[:20]})


def a2_verify(ctx: Ctx) -> Check:
    from data.fetch import load_manifest, manifest_path, verify
    cfg = ctx.cfg
    man = load_manifest(cfg, cfg.version)
    r = verify(man, cfg.root, with_raw=True,
               optional_prefixes=tuple(cfg.optional_prefixes), progress=False)
    return Check("A2", "`data.fetch --verify-only` passes", r["passed"],
                 f"{r['ok']}/{r['checked']} files verified against "
                 f"{manifest_path(cfg, cfg.version).name} "
                 f"({len(r['bad'])} mismatched, {len(r['missing'])} missing)",
                 {"ok": r["ok"], "bad": r["bad"][:5], "missing": r["missing"][:5]})


# ---------------------------------------------------------------------------
# A3 - A6
# ---------------------------------------------------------------------------
def a3_token_counts(ctx: Ctx) -> Check:
    cfg = ctx.cfg
    idx = ctx.train_idx
    per = Counter()
    for s, n in zip(idx["subject"], idx["length"]):
        per[s] += int(n)
    bad = []
    for s in cfg.train_subjects:
        if per[s] != cfg.pack_tokens_per_subject:
            bad.append(f"{s}={per[s]:,}")
    held: Dict[str, Dict[str, int]] = {}
    target = cfg.heldout_tokens_per_half
    for half in cfg.pack_halves:
        hi = ctx.held_idx[half]
        hp = Counter()
        for s, n in zip(hi["subject"], hi["length"]):
            hp[s] += int(n)
        held[half] = dict(hp)
        for s in cfg.all_subjects:
            if abs(hp[s] - target) / target > 0.01:
                bad.append(f"{half}/{s}={hp[s]:,}")
    return Check("A3", "Token counts per subject and half", not bad,
                 f"every Pile subject exactly {cfg.pack_tokens_per_subject:,} in "
                 f"train.bin; every held-out half within 1% of {target:,} per "
                 f"subject" + (f". Off: {bad}" if bad else ""),
                 {"train": {s: per[s] for s in cfg.train_subjects},
                  "bio": per[pack.BIO_SUBJECT], "heldout": held})


def a4_windows(ctx: Ctx) -> Check:
    cfg = ctx.cfg
    codes, names = ctx.subject_codes()
    window, stride = cfg.window_tokens, cfg.window_tokens // 4
    counts = np.zeros((len(names) + 1, codes.size + 1), dtype=np.int64)
    # cumulative count per subject over token positions
    for i, _ in enumerate(names):
        counts[i, 1:] = np.cumsum(codes == i)
    doc = np.cumsum(codes != 255)
    total_doc = int(doc[-1])
    target = {n: float(counts[i, -1]) / total_doc for i, n in enumerate(names)}
    worst = {n: {"target_share": round(target[n], 6), "worst_share": target[n],
                 "worst_deviation_points": 0.0, "at_token": 0} for n in names}
    n_windows = 0
    for a in range(0, max(codes.size - window + 1, 1), stride):
        b = min(a + window, codes.size)
        span = doc[b - 1] - (doc[a - 1] if a > 0 else 0)
        if span <= 0:
            continue
        n_windows += 1
        for i, n in enumerate(names):
            got = counts[i, b] - counts[i, a]
            dev = abs(got / span - target[n]) * 100
            if dev > worst[n]["worst_deviation_points"]:
                worst[n].update(worst_deviation_points=round(float(dev), 4),
                                worst_share=round(float(got / span), 6),
                                at_token=int(a))
    tol = cfg.window_tolerance_points
    bad = [n for n in names if worst[n]["worst_deviation_points"] > tol]
    mx = max(worst[n]["worst_deviation_points"] for n in names)
    return Check("A4", f"Shares in every {window:,}-token window", not bad,
                 f"worst deviation {mx:.3f} points across {n_windows} "
                 f"overlapping windows (stride {stride:,}), tolerance {tol}"
                 + (f". Over: {bad}" if bad else ""),
                 {"worst": worst, "n_windows": n_windows})


def _tiling(tokens: np.memmap, idx: Dict[str, Any], vocab: int,
            name: str) -> Tuple[bool, str, Dict[str, Any]]:
    starts = np.asarray(idx["start"], dtype=np.int64)
    lengths = np.asarray(idx["length"], dtype=np.int64)
    arr = np.asarray(tokens)
    problems = []
    if arr.dtype != TOKEN_DTYPE:
        problems.append(f"dtype {arr.dtype}")
    if int(arr.max()) >= vocab:
        problems.append(f"max id {int(arr.max())} >= {vocab}")
    if not (np.diff(starts) > 0).all():
        problems.append("index not in increasing start order")
    if not (starts[1:] >= starts[:-1] + lengths[:-1]).all():
        problems.append("segments overlap")
    covered = np.zeros(arr.size, dtype=bool)
    for s, e in zip(starts, starts + lengths):
        covered[s:e] = True
    n_doc_eot = int((arr[covered] == EOT).sum())
    n_gap_not_eot = int((arr[~covered] != EOT).sum())
    if n_doc_eot:
        problems.append(f"{n_doc_eot} EOT tokens inside documents")
    if n_gap_not_eot:
        problems.append(f"{n_gap_not_eot} non-EOT tokens outside documents")
    if int(lengths.sum()) != int(covered.sum()):
        problems.append("lengths do not sum to covered tokens")
    nums = {"tokens": int(arr.size), "segments": int(starts.size),
            "covered": int(covered.sum()), "eot_gap_tokens": int((~covered).sum()),
            "max_id": int(arr.max())}
    return not problems, (f"{name}: {nums['tokens']:,} tokens, "
                          f"{nums['segments']:,} segments, "
                          f"{nums['eot_gap_tokens']:,} EOT separator/pad tokens, "
                          f"max id {nums['max_id']}"
                          + ("; " + "; ".join(problems) if problems else "")), nums


def a5_format(ctx: Ctx) -> Check:
    cfg = ctx.cfg
    ok, detail, nums = _tiling(ctx.train, ctx.train_idx, cfg.vocab_size,
                               "train.bin")
    details = [detail]
    all_ok = ok
    out = {"train.bin": nums}
    for half in cfg.pack_halves:
        o, d, n = _tiling(ctx.held[half], ctx.held_idx[half], cfg.vocab_size,
                          f"{half}.bin")
        details.append(d)
        all_ok = all_ok and o
        out[f"{half}.bin"] = n
    if ctx.train.size % cfg.block_size:
        all_ok = False
        details.append(f"train.bin is not a multiple of {cfg.block_size}")
    return Check("A5", "Format: dtype, vocab bound, EOT, index tiling", all_ok,
                 " | ".join(details), out)


def a6_decode(ctx: Ctx, n_samples: int = 1000) -> Check:
    cfg = ctx.cfg
    src = ctx.train_doc_texts()
    idx = ctx.train_idx
    rng = np.random.default_rng(cfg.seed)
    total = len(idx["start"])
    sample = rng.choice(total, size=min(n_samples, total), replace=False)
    arr = np.asarray(ctx.train)
    bad, whole = [], 0
    cache: Dict[str, np.ndarray] = {}
    for j in sample:
        doc_id = idx["doc_id"][j]
        st, ln = int(idx["start"][j]), int(idx["length"][j])
        off = int(idx["doc_offset"][j])
        if doc_id not in cache:
            cache[doc_id] = np.asarray(
                ctx.enc.encode_ordinary(src[doc_id]), dtype=TOKEN_DTYPE)
        want = cache[doc_id]
        if not np.array_equal(arr[st:st + ln], want[off:off + ln]):
            bad.append(doc_id)
            continue
        if off == 0 and ln == want.size:
            if ctx.enc.decode(arr[st:st + ln].tolist()) != src[doc_id]:
                bad.append(doc_id)
                continue
            whole += 1
    return Check("A6", "Decoding index segments reproduces the source", not bad,
                 f"{len(sample):,} random segments checked token for token "
                 f"({whole:,} of them whole documents, also compared as text); "
                 f"{len(bad)} mismatches" + (f": {bad[:5]}" if bad else ""),
                 {"sampled": len(sample), "whole_documents": whole,
                  "mismatches": bad[:10]})


# ---------------------------------------------------------------------------
# A7 - A10
# ---------------------------------------------------------------------------
def _train_ngram_index(ctx: Ctx, subject: str) -> np.ndarray:
    """Sorted unique 13-gram hashes of a subject's training text."""
    cfg = ctx.cfg
    MERGE = 16_000_000
    base = np.empty(0, dtype=np.uint64)
    pending: List[np.ndarray] = []
    size = 0
    batch: List[str] = []

    def merge():
        nonlocal base, size
        if not pending:
            return
        parts = ([base] if base.size else []) + pending
        base = np.unique(np.concatenate(parts))
        pending.clear()
        size = 0

    def flush():
        nonlocal size
        if not batch:
            return
        for toks in ctx.enc.encode_ordinary_batch(batch, num_threads=8):
            h = ngram_hashes(toks, cfg.ngram_n)
            if h.size:
                u = np.unique(h)
                pending.append(u)
                size += u.size
        batch.clear()
        if size > MERGE:
            merge()

    for rec in read_jsonl(cfg.train_dir / f"{cfg.slug(subject)}.jsonl.gz"):
        batch.append(rec["text"])
        if len(batch) >= 256:
            flush()
    flush()
    merge()
    return base


# Ceilings from the data plan: Github and FreeLaw are self-overlapping by
# nature (licence headers, recited statute text) and were measured at 20.7%
# and 11.5% in prompt 1; everything else has to stay near zero.
OVERLAP_CEILING = {"Github": 0.25, "FreeLaw": 0.15}
OVERLAP_CEILING_DEFAULT = 0.05


def a7_leaks(ctx: Ctx) -> Check:
    cfg = ctx.cfg
    problems: List[str] = []
    nums: Dict[str, Any] = {}

    # (a) document ids disjoint across train / label / test
    train_ids = {d for d in ctx.train_idx["doc_id"]
                 if not d.startswith("bio-")}
    half_ids = {h: {r["doc_id"] for r in ctx.heldout_records(h)}
                for h in cfg.pack_halves}
    for h, ids in half_ids.items():
        inter = train_ids & ids
        if inter:
            problems.append(f"{len(inter)} ids shared between train and {h}")
    hs = list(half_ids)
    cross = half_ids[hs[0]] & half_ids[hs[1]]
    if cross:
        problems.append(f"{len(cross)} ids shared between the two halves")
    nums["ids"] = {"train": len(train_ids),
                   **{h: len(v) for h, v in half_ids.items()}}

    # (b) zero exact-hash matches between train text and held-out text
    train_hashes = {text_sha256(t) for d, t in ctx.train_doc_texts().items()
                    if not d.startswith("bio-")}
    dup = 0
    for h in cfg.pack_halves:
        for r in ctx.heldout_records(h):
            if r.get("sha256", text_sha256(r["text"])) in train_hashes:
                dup += 1
    if dup:
        problems.append(f"{dup} held-out documents are exact copies of train text")
    nums["exact_duplicates"] = dup

    # (c) per-document 13-gram overlap, and the per-subject aggregate, measured
    #     on the FINAL held-out files rather than read out of the dedup log
    per_subject: Dict[str, Any] = {}
    worst_doc = 0.0
    over_50 = 0
    for subject in cfg.all_subjects:
        if subject not in cfg.train_subjects:
            per_subject[subject] = {"aggregate": 0.0, "max_document": 0.0,
                                    "ceiling": OVERLAP_CEILING_DEFAULT,
                                    "note": "no training text"}
            continue
        index = _train_ngram_index(ctx, subject)
        found = total = 0
        mx = 0.0
        for h in cfg.pack_halves:
            recs = [r for r in read_jsonl(cfg.heldout_dir / h /
                                          f"{cfg.slug(subject)}.jsonl.gz")]
            for i in range(0, len(recs), 256):
                chunk = recs[i:i + 256]
                for toks in ctx.enc.encode_ordinary_batch(
                        [r["text"] for r in chunk], num_threads=8):
                    hh = ngram_hashes(toks, cfg.ngram_n)
                    f, t = overlap_rate(hh, index)
                    found += f
                    total += t
                    if t:
                        rate = f / t
                        mx = max(mx, rate)
                        if rate > cfg.ngram_drop_threshold:
                            over_50 += 1
        agg = found / total if total else 0.0
        ceiling = OVERLAP_CEILING.get(subject, OVERLAP_CEILING_DEFAULT)
        per_subject[subject] = {"aggregate": round(agg, 6),
                                "max_document": round(mx, 6),
                                "ceiling": ceiling,
                                "train_13grams": int(index.size)}
        worst_doc = max(worst_doc, mx)
        if agg > ceiling:
            problems.append(f"{subject} aggregate overlap {agg:.2%} > {ceiling:.0%}")
        print(f"[validate] A7 {subject:20s} aggregate {agg:.3%} "
              f"(ceiling {ceiling:.0%}), worst document {mx:.1%}", flush=True)
    if over_50:
        problems.append(f"{over_50} held-out documents over "
                        f"{cfg.ngram_drop_threshold:.0%} 13-gram overlap")
    nums["ngram"] = per_subject
    nums["documents_over_threshold"] = over_50
    return Check("A7", "Leaks: ids, exact hashes, 13-gram overlap",
                 not problems,
                 f"ids disjoint across train/label/test; {dup} exact-hash "
                 f"matches; {over_50} documents over "
                 f"{cfg.ngram_drop_threshold:.0%}; worst single document "
                 f"{worst_doc:.1%}; aggregates "
                 + ", ".join(f"{s.split()[0]}={v['aggregate']:.2%}"
                             for s, v in per_subject.items())
                 + ("; " + "; ".join(problems) if problems else ""), nums)


def a8_halves(ctx: Ctx) -> Check:
    cfg = ctx.cfg
    problems = []
    per: Dict[str, Dict[str, int]] = {}
    ids: Dict[str, set] = {}
    for half in cfg.pack_halves:
        hi = ctx.held_idx[half]
        c = Counter(hi["subject"])
        per[half] = dict(c)
        ids[half] = set(hi["doc_id"])
        for s in cfg.all_subjects:
            if c[s] < cfg.heldout_min_docs_per_half:
                problems.append(f"{half}/{s} has {c[s]} documents "
                                f"< {cfg.heldout_min_docs_per_half}")
        mx = int(np.asarray(hi["length"]).max())
        if mx > cfg.max_tokens:
            problems.append(f"{half} has a {mx}-token document > {cfg.max_tokens}")
    hs = list(ids)
    overlap = ids[hs[0]] & ids[hs[1]]
    if overlap:
        problems.append(f"{len(overlap)} documents in both halves")
    worst = min(min(v.values()) for v in per.values())
    return Check("A8", "Halves: disjoint, >=500 docs, <=4096 tokens",
                 not problems,
                 f"halves share {len(overlap)} documents; smallest half/subject "
                 f"is {worst} documents (minimum "
                 f"{cfg.heldout_min_docs_per_half}); longest document "
                 f"{max(int(np.asarray(ctx.held_idx[h]['length']).max()) for h in cfg.pack_halves)} "
                 f"tokens (cap {cfg.max_tokens})"
                 + ("; " + "; ".join(problems) if problems else ""),
                 {"documents": per, "shared": len(overlap)})


def a9_no_uspto_in_train(ctx: Ctx) -> Check:
    cfg = ctx.cfg
    held_only = [s for s in cfg.heldout_only_subjects]
    subjects = set(ctx.train_idx["subject"])
    bad = [s for s in held_only if s in subjects]
    slugs = {cfg.slug(s) for s in held_only}
    by_id = [d for d in ctx.train_idx["doc_id"]
             if d.split("-")[0] in slugs]
    ok = not bad and not by_id
    return Check("A9", "No held-out-only subject in train.bin", ok,
                 f"{held_only} appear in {len(by_id)} train.bin segments by "
                 f"document id and {len(bad)} by subject label; train.bin "
                 f"carries {sorted(subjects)}",
                 {"heldout_only": held_only, "segments": len(by_id)})


def a10_labels(ctx: Ctx) -> Check:
    """Index subject == raw-archive pile_set_name == the doc id's slug."""
    cfg = ctx.cfg
    raw_subject: Dict[str, str] = {}
    for split in ("train", "heldout"):
        d = cfg.raw_dir / split
        if not d.exists():
            continue
        for p in sorted(d.glob("*.jsonl.gz")):
            for r in read_jsonl(p):
                raw_subject[r["doc_id"]] = r["subject"]
    slug_of = {cfg.slug(s): s for s in cfg.all_subjects}
    problems = []
    checked = bio = 0
    for s, d, pid in zip(ctx.train_idx["subject"], ctx.train_idx["doc_id"],
                         ctx.train_idx["person_id"]):
        if s == pack.BIO_SUBJECT:
            bio += 1
            if not pid or pid not in ctx.people:
                problems.append(f"{d}: bio segment with person_id {pid!r}")
            continue
        checked += 1
        if raw_subject.get(d) != s:
            problems.append(f"{d}: index says {s!r}, raw archive says "
                            f"{raw_subject.get(d)!r}")
        if slug_of.get(d.split("-")[0]) != s:
            problems.append(f"{d}: id slug does not match subject {s!r}")
        if len(problems) > 5:
            break
    for half in cfg.pack_halves:
        hi = ctx.held_idx[half]
        for s, d in zip(hi["subject"], hi["doc_id"]):
            if raw_subject.get(d) != s or slug_of.get(d.split("-")[0]) != s:
                problems.append(f"{half}/{d}: label mismatch")
                break
    return Check("A10", "Subject labels agree with the source", not problems,
                 f"{checked:,} Pile segments: index subject == raw-archive "
                 f"meta.pile_set_name == the document id's slug; {bio:,} "
                 f"biography segments all labelled `bio` with a known person id"
                 + ("; " + "; ".join(problems[:4]) if problems else ""),
                 {"pile_segments": checked, "bio_segments": bio,
                  "raw_documents": len(raw_subject),
                  "problems": problems[:10]})


# ---------------------------------------------------------------------------
# A11: can a bag of words even tell the subjects apart?
# ---------------------------------------------------------------------------
def a11_bow_classifier(ctx: Ctx) -> Check:
    """Multinomial naive Bayes on token counts, label halves -> test halves.

    A sanity check on the labels, not a result: if a bag of words cannot
    separate the six subjects, something is wrong with how they were tagged.
    Uniform class priors on purpose -- the halves hold very different document
    counts per subject (708 to 3,822), and an empirical prior would reward
    guessing the big ones.
    """
    cfg = ctx.cfg
    V = cfg.vocab_size
    subjects = list(cfg.all_subjects)
    code = {s: i for i, s in enumerate(subjects)}

    counts = np.zeros((len(subjects), V), dtype=np.float64)
    label_idx = ctx.held_idx["label"]
    label_tok = np.asarray(ctx.held["label"])
    for s, st, ln in zip(label_idx["subject"], label_idx["start"],
                         label_idx["length"]):
        seg = label_tok[int(st):int(st) + int(ln)]
        counts[code[s]] += np.bincount(seg, minlength=V)
    logp = np.log(counts + 1.0) - np.log(counts.sum(1, keepdims=True) + V)

    test_idx = ctx.held_idx["test"]
    test_tok = np.asarray(ctx.held["test"])
    confusion = np.zeros((len(subjects), len(subjects)), dtype=np.int64)
    for s, st, ln in zip(test_idx["subject"], test_idx["start"],
                         test_idx["length"]):
        seg = test_tok[int(st):int(st) + int(ln)]
        scores = logp[:, seg].sum(axis=1)
        confusion[code[s], int(np.argmax(scores))] += 1
    total = int(confusion.sum())
    correct = int(np.trace(confusion))
    acc = correct / total
    per = {s: round(float(confusion[i, i] / max(1, confusion[i].sum())), 4)
           for i, s in enumerate(subjects)}
    return Check("A11", "Bag-of-words subject classifier (sanity)", acc >= 0.90,
                 f"accuracy {acc:.2%} on {total:,} test-half documents "
                 f"(threshold 90%); per subject "
                 + ", ".join(f"{s.split()[0]}={v:.1%}" for s, v in per.items()),
                 {"accuracy": round(acc, 6), "documents": total,
                  "subjects": subjects, "per_subject_recall": per,
                  "confusion": confusion.tolist()})


# ---------------------------------------------------------------------------
# A12 - A14: the biographies
# ---------------------------------------------------------------------------
def _chisquare_p(counts: Sequence[int]) -> float:
    import math
    n, k = sum(counts), len(counts)
    expected = n / k
    stat = sum((c - expected) ** 2 / expected for c in counts)
    a, x = (k - 1) / 2.0, stat / 2.0
    if x <= 0:
        return 1.0

    def gser(a, x, itmax=500, eps=3e-12):
        ap, total, delta = a, 1.0 / a, 1.0 / a
        for _ in range(itmax):
            ap += 1
            delta *= x / ap
            total += delta
            if abs(delta) < abs(total) * eps:
                break
        return total * math.exp(-x + a * math.log(x) - math.lgamma(a))

    def gcf(a, x, itmax=500, eps=3e-12):
        tiny = 1e-300
        b, c, d = x + 1.0 - a, 1.0 / tiny, 1.0 / (x + 1.0 - a)
        h = d
        for i in range(1, itmax):
            an = -i * (i - a)
            b += 2.0
            d = an * d + b
            if abs(d) < tiny:
                d = tiny
            c = b + an / c
            if abs(c) < tiny:
                c = tiny
            d = 1.0 / d
            delta = d * c
            h *= delta
            if abs(delta - 1.0) < eps:
                break
        return h * math.exp(-x + a * math.log(x) - math.lgamma(a))

    return 1.0 - gser(a, x) if x < a + 1.0 else gcf(a, x)


def a12_bio_facts(ctx: Ctx) -> Check:
    cfg = ctx.cfg
    people = list(ctx.people.values())
    problems: List[str] = []
    nums: Dict[str, Any] = {}

    names = [p["name"] for p in people]
    if len(set(names)) != len(names):
        problems.append("duplicate full names")
    check = json.loads((cfg.bios_dir / "name_check.json").read_text())
    found = set(check.get("names_found", []))
    clash = sorted(set(names) & found)
    if clash:
        problems.append(f"{len(clash)} names occur in the Pile: {clash[:3]}")
    genders = Counter(p["gender"] for p in people)
    if set(genders) != set(cfg.bio_genders):
        problems.append(f"gender values {sorted(genders)}")
    for p in people:
        if sorted(p["facts"]) != sorted(cfg.bio_attributes):
            problems.append(f"{p['person_id']} has facts {sorted(p['facts'])}")
            break

    values = json.loads((cfg.bios_dir / "attribute_values.json").read_text())
    vlists = values["values"]
    token_modes: Dict[str, Any] = {}
    for attr, vals in vlists.items():
        n = 2 if attr in cfg.bio_first_two_tokens_unique else 1
        pre = [tuple(ctx.enc.encode_ordinary(" " + v)[:n]) for v in vals]
        unique = len(set(pre)) == len(vals)
        token_modes[attr] = {"values": len(vals), "prefix_tokens": n,
                             "unique": unique,
                             "distinct_first": len({p[0] for p in pre})}
        if not unique:
            problems.append(f"{attr}: first {n} token(s) not unique")

    sets = {a: set(v) for a, v in vlists.items()}
    chi: Dict[str, float] = {}
    for attr in cfg.bio_attributes:
        c = Counter(p["facts"][attr] for p in people)
        counts = [c.get(v, 0) for v in vlists[attr]]
        pv = _chisquare_p(counts)
        chi[attr] = round(pv, 6)
        if pv <= 0.01:
            problems.append(f"{attr}: chi-square p={pv:.4g} <= 0.01")
        expected = len(people) / len(vlists[attr])
        if expected < 5:
            problems.append(f"{attr}: expected count {expected:.1f} too low")

    missing = 0
    for fname in ("bios_train.jsonl", "bios_control.jsonl"):
        for rec in read_jsonl(cfg.bios_dir / fname):
            facts = ctx.people[rec["person_id"]]["facts"]
            for attr, val in facts.items():
                if val not in rec["text"]:
                    missing += 1
    if missing:
        problems.append(f"{missing} (rewording, value) pairs missing verbatim")

    nums = {"people": len(people), "by_gender": dict(genders),
            "names_in_pile": len(clash), "tokens": token_modes,
            "chisquare_p": chi, "missing_values_in_rewordings": missing}
    return Check("A12", "Biography facts", not problems,
                 f"{len(people):,} people, names unique and absent from the "
                 f"Pile, genders {dict(genders)}, 5 facts each; first-token "
                 f"uniqueness holds per list (first two for birth_date, which "
                 f"has only {token_modes['birth_date']['distinct_first']} "
                 f"distinct first tokens); chi-square p "
                 + ", ".join(f"{a}={v:.3f}" for a, v in chi.items())
                 + ("; " + "; ".join(problems[:4]) if problems else ""), nums)


def a13_prompts(ctx: Ctx) -> Check:
    """Prompt integrity: nothing may hand the probe an answer for free.

    FAILS on any of three answer leaks, each measured over all 100,000 rows:

      (i)   the true value appears verbatim in its own prompt;
      (ii)  the value's ranking key -- its first GPT-2 token, or the first two
            for a date -- appears in the person's own name;
      (iii) that key appears inside another of the same person's values, since
            every rewording puts all five in one paragraph in a random order.

    Plus two structural properties: a training-template row's
    `prompt + continuation` is an exact prefix of its biography, and no
    paraphrase prompt occurs in `train.bin`.

    **Template-word hits are REPORTED, not failed.** An employer called
    "Heineken" has the ranking key " He", which is also the male pronoun; the
    fix would be to change the templates or drop the value, and the design says
    to do neither. The rows are listed so the metrics owner can see them.

    Paraphrase isolation is checked inside the **biography segments** of
    train.bin, where it is controllable. The held-out markers are ordinary
    English ("As for", "Question:") and do occur in Pile text -- reported, not
    failed -- so a seeded sample of full prompts is searched directly as well.
    """
    cfg = ctx.cfg
    import data.bios_data as bd
    from data.bios import ranking_key, value_token_set

    bios = {}
    for fname in ("bios_train.jsonl", "bios_control.jsonl"):
        for rec in read_jsonl(cfg.bios_dir / fname):
            bios[rec["doc_id"]] = rec["text"]
    rows = list(read_jsonl(cfg.bios_dir / "facts.jsonl"))
    problems: List[str] = []

    name_toks = {pid: set(ctx.enc.encode_ordinary(" " + p["name"]))
                 | set(ctx.enc.encode_ordinary(p["name"]))
                 for pid, p in ctx.people.items()}
    value_toks = {pid: {a: value_token_set(ctx.enc, v)
                        for a, v in p["facts"].items()}
                  for pid, p in ctx.people.items()}
    prompt_toks = ctx.enc.encode_ordinary_batch([r["prompt"] for r in rows],
                                                num_threads=8)

    leak_value: List[str] = []
    leak_name: List[str] = []
    leak_other: List[str] = []
    template_hits: Dict[str, List[str]] = defaultdict(list)
    n_train = n_para = 0
    not_prefix: List[str] = []

    for row, ptoks in zip(rows, prompt_toks):
        pid = row["person_id"]
        if row["true_value"] in row["prompt"]:
            leak_value.append(row["fact_id"])
        if row["continuation"] != " " + row["true_value"]:
            problems.append(f"{row['fact_id']}: continuation mismatch")
        key = set(ranking_key(ctx.enc, cfg, row["attribute"], row["true_value"]))
        if key & name_toks[pid]:
            leak_name.append(row["fact_id"])
        other = [a for a, t in value_toks[pid].items()
                 if a != row["attribute"] and (key & t)]
        if other:
            leak_other.append(row["fact_id"])
        if key & set(ptoks) and not (key & name_toks[pid]) and not other:
            template_hits[f"{row['attribute']}={row['true_value']}"].append(
                row["fact_id"])
        if row["held_out_template"]:
            n_para += 1
            continue
        n_train += 1
        if not bios[row["doc_id"]].startswith(row["prompt"] + row["continuation"]):
            not_prefix.append(row["fact_id"])

    for label, hits in (("the true value verbatim in its own prompt", leak_value),
                        ("the ranking key in the person's own name", leak_name),
                        ("the ranking key in another of the person's values",
                         leak_other)):
        if hits:
            who = sorted({f.split("-")[0] for f in hits})
            problems.append(
                f"{len(hits)} rows leak {label} ({len(who)} people, e.g. "
                + ", ".join(f"{pid} ({ctx.people[pid]['name']!r})"
                            for pid in who[:3]) + ")")
    if not_prefix:
        problems.append(f"{len(not_prefix)} prompts are not a prefix of their "
                        f"biography: {not_prefix[:3]}")

    # paraphrase wording inside train.bin's biography segments
    arr = np.asarray(ctx.train)
    idx = ctx.train_idx
    bio_tokens = np.concatenate([arr[int(st):int(st) + int(ln)] for s, st, ln in
                                 zip(idx["subject"], idx["start"], idx["length"])
                                 if s == pack.BIO_SUBJECT])
    bio_marker_hits: Dict[str, int] = {}
    pile_marker_hits: Dict[str, int] = {}
    for marker in bd.HELDOUT_MARKERS:
        hits = whole = 0
        for variant in (" " + marker, marker):
            ids = np.asarray(ctx.enc.encode_ordinary(variant), dtype=TOKEN_DTYPE)
            hits += _count_subsequence(bio_tokens, ids)
            whole += _count_subsequence(arr, ids)
        bio_marker_hits[marker] = hits
        pile_marker_hits[marker] = whole - hits
        if hits:
            problems.append(f"held-out marker {marker!r} appears {hits} times "
                            f"inside biography text in train.bin")

    para = [r for r in rows if r["held_out_template"]]
    sample = keyed_rng(cfg.seed, "a13_prompts").sample(para, min(200, len(para)))
    found = [r["fact_id"] for r in sample
             if _count_subsequence(
                 arr, np.asarray(ctx.enc.encode_ordinary(r["prompt"]),
                                 dtype=TOKEN_DTYPE))]
    if found:
        problems.append(f"{len(found)} sampled paraphrase prompts occur in "
                        f"train.bin: {found[:3]}")

    n_tmpl = sum(len(v) for v in template_hits.values())
    return Check("A13", "Fact prompts: no answer leaks", not problems,
                 f"{len(rows):,} rows: **0** leak the value verbatim "
                 f"({len(leak_value)}), **0** via the person's name "
                 f"({len(leak_name)}), **0** via another of the person's values "
                 f"({len(leak_other)}); {n_train:,} training prompts are exact "
                 f"prefixes of their biography; {n_para:,} paraphrase prompts, "
                 f"{len(sample)} of them searched in full against train.bin and "
                 f"absent; held-out markers inside biography text: "
                 + ", ".join(f"{k!r}={v}" for k, v in bio_marker_hits.items())
                 + f" (the same markers occur {sum(pile_marker_hits.values())} "
                 f"times in ordinary Pile text, which is not a leak); REPORTED: "
                 f"{n_tmpl} rows whose ranking key is a TEMPLATE word "
                 f"({', '.join(sorted(template_hits))})"
                 + ("; " + "; ".join(problems[:3]) if problems else ""),
                 {"rows": len(rows), "train_prompts": n_train,
                  "paraphrase_prompts": n_para,
                  "leak_value_verbatim": leak_value[:20],
                  "leak_via_name": leak_name[:20],
                  "leak_via_other_value": leak_other[:20],
                  "n_leak_value_verbatim": len(leak_value),
                  "n_leak_via_name": len(leak_name),
                  "n_leak_via_other_value": len(leak_other),
                  "template_word_rows": n_tmpl,
                  "template_word_values": {k: len(v) for k, v in
                                           sorted(template_hits.items())},
                  "bio_marker_hits": bio_marker_hits,
                  "pile_marker_hits": pile_marker_hits})


def _count_subsequence(arr: np.ndarray, pat: np.ndarray) -> int:
    """How many times `pat` occurs in `arr` (exact token subsequence)."""
    if pat.size == 0 or arr.size < pat.size:
        return 0
    cand = np.flatnonzero(arr[:arr.size - pat.size + 1] == pat[0])
    for k in range(1, pat.size):
        if cand.size == 0:
            return 0
        cand = cand[arr[cand + k] == pat[k]]
    return int(cand.size)


def a14_exposure(ctx: Ctx) -> Check:
    cfg = ctx.cfg
    idx = ctx.train_idx
    block = cfg.block_size
    seen: Dict[str, Counter] = defaultdict(Counter)
    crossing = 0
    for s, st, ln, pid, rw in zip(idx["subject"], idx["start"], idx["length"],
                                  idx["person_id"], idx["rewording_id"]):
        if s != pack.BIO_SUBJECT:
            continue
        st, ln = int(st), int(ln)
        if st // block != (st + ln - 1) // block:
            crossing += 1
        seen[pid][int(rw)] += 1
    problems = []
    if crossing:
        problems.append(f"{crossing} biography copies cross a sequence boundary")
    for pid, p in ctx.people.items():
        want = int(p["target_exposures"])
        if p["split"] != "train":
            if pid in seen:
                problems.append(f"control person {pid} has copies")
            continue
        got = [seen[pid][r] for r in range(int(p["n_rewordings"]))]
        if got != pack.copies_per_rewording(want, int(p["n_rewordings"])):
            problems.append(f"{pid}: copies {got}, expected "
                            f"{pack.copies_per_rewording(want, int(p['n_rewordings']))}")
        if len(problems) > 5:
            break

    # no control person's name anywhere in the text that reaches train.bin
    control = {p["name"] for p in ctx.people.values() if p["split"] == "control"}
    from data.bios import scan_corpus_for_names
    texts = ctx.train_doc_texts()
    used = {d for d in idx["doc_id"]}
    hits: Dict[str, int] = {}
    import re
    cap = re.compile(r"[A-Z][A-Za-z]+")
    for doc_id in used:
        text = texts.get(doc_id)
        if not text:
            continue
        spans = [(m.start(), m.end()) for m in cap.finditer(text)]
        for (s0, e0), (s1, e1) in zip(spans, spans[1:]):
            if s1 == e0 + 1 and text[e0] == " ":
                pair = text[s0:e1]
                if pair in control:
                    hits[pair] = hits.get(pair, 0) + 1
    if hits:
        problems.append(f"{len(hits)} control names appear in train text: "
                        f"{sorted(hits)[:3]}")
    return Check("A14", "Exposure counts and control isolation", not problems,
                 f"{sum(sum(c.values()) for c in seen.values()):,} copies over "
                 f"{len(seen):,} trained people, every count equal to its tier "
                 f"target and spread over the 4 rewordings; {crossing} cross a "
                 f"{block}-token boundary; {len(hits)} of "
                 f"{len(control)} control names appear in train text"
                 + ("; " + "; ".join(problems[:4]) if problems else ""),
                 {"copies": sum(sum(c.values()) for c in seen.values()),
                  "people_with_copies": len(seen), "crossing": crossing,
                  "control_names_found": sorted(hits)[:10]})


# ---------------------------------------------------------------------------
# A15 - A17
# ---------------------------------------------------------------------------
def a15_scorer_floor(ctx: Ctx) -> Check:
    """A random scorer and an untrained model must sit mid-list.

    If either were already above chance, the probe would be reading something
    other than what the model knows -- a candidate list with a giveaway, or a
    bug in which position's logits are read.
    """
    import torch
    from data.q2_probe import ProbeSet, score_random, select_eval_rows
    from memlayers.model import GPT, GPTConfig
    from memlayers.devices import pick_device

    cfg = ctx.cfg
    rows = select_eval_rows(cfg)
    probe = ProbeSet.build(cfg, rows, ctx.enc)
    rnd = score_random(probe, seed=cfg.seed)

    sub = ProbeSet(probe.rows[:4000], probe.candidates)
    mcfg = json.loads((ROOT / "memlayers" / "configs" / "t1_pkm.yaml").read_text()
                      ) if False else None
    import yaml
    model_kw = yaml.safe_load(
        (ROOT / "memlayers" / "configs" / "t1_pkm.yaml").read_text())["model"]
    torch.manual_seed(0)
    device = pick_device("auto")
    model = GPT(GPTConfig(**model_kw)).to(device)
    unt = sub.score(model, device, block_size=model_kw.get("block_size", 512))
    del model

    problems = []
    per_attr = {}
    for name, res in (("random", rnd), ("untrained", unt)):
        for attr, agg in res["by_attribute"].items():
            per_attr[f"{name}/{attr}"] = agg["mean_rank_fraction"]
            if not 0.40 <= agg["mean_rank_fraction"] <= 0.60:
                problems.append(f"{name}/{attr} mean rank fraction "
                                f"{agg['mean_rank_fraction']:.3f}")
    return Check("A15", "Probe floor: random and untrained sit mid-list",
                 not problems,
                 f"random scorer: mean rank fraction "
                 f"{rnd['overall']['mean_rank_fraction']:.3f}, top-1 "
                 f"{rnd['overall']['top1']:.3%} over {len(probe):,} prompts; "
                 f"untrained model: {unt['overall']['mean_rank_fraction']:.3f}, "
                 f"top-1 {unt['overall']['top1']:.3%} over {len(sub):,}; "
                 f"mean candidate list {rnd['overall']['candidates_mean']:.0f}"
                 + ("; " + "; ".join(problems[:4]) if problems else ""),
                 {"random": rnd["overall"], "untrained": unt["overall"],
                  "rank_fraction_by_attribute": per_attr})


def a16_loader(ctx: Ctx) -> Check:
    import torch
    from data.loader import PackedDataset
    cfg = ctx.cfg
    path = cfg.tokens_dir / "train.bin"
    problems = []

    a = PackedDataset(path, cfg.block_size, seed=1234)
    b = PackedDataset(path, cfg.block_size, seed=1234)
    c = PackedDataset(path, cfg.block_size, seed=4321)
    if not np.array_equal(a.sequence_order(0), b.sequence_order(0)):
        problems.append("same seed gave a different order")
    if np.array_equal(a.sequence_order(0), c.sequence_order(0)):
        problems.append("different seeds gave the same order")
    if sorted(a.sequence_order(0).tolist()) != list(range(a.n_sequences)):
        problems.append("the order is not a permutation")

    whole = PackedDataset(path, cfg.block_size, seed=7)
    want = [whole.get_batch(i, 4) for i in range(6)]
    part = PackedDataset(path, cfg.block_size, seed=7)
    for i in range(3):
        part.get_batch(i, 4)
    state = part.state_dict()
    resumed = PackedDataset(path, cfg.block_size, seed=0)
    resumed.load_state_dict(state)
    for i in range(3):
        x, y = resumed.get_batch(3 + i, 4)
        if not (torch.equal(x, want[3 + i][0]) and torch.equal(y, want[3 + i][1])):
            problems.append(f"resume diverged at batch {3 + i}")
            break

    x, y = a.get_batch(0, 4)
    if x.shape != (4, cfg.block_size) or y.shape != (4, cfg.block_size):
        problems.append(f"shapes {tuple(x.shape)} / {tuple(y.shape)}")
    if not torch.equal(x[:, 1:], y[:, :-1]):
        problems.append("targets are not inputs shifted by one")
    return Check("A16", "Loader: order, resume, shapes", not problems,
                 f"{a.n_sequences:,} sequences of {cfg.block_size}; same seed "
                 f"reproduces the order, a different seed does not, the order is "
                 f"a permutation, and a resume from (seed, position) matches an "
                 f"unbroken run"
                 + ("; " + "; ".join(problems) if problems else ""),
                 {"n_sequences": a.n_sequences, "resume_position": state["position"]})


def a17_unigram(ctx: Ctx) -> Check:
    """Per-subject unigram cross-entropy on the test half.

    Counts come from that subject's own training text with add-one smoothing.
    `USPTO Backgrounds` has no training text -- it is the held-out-only
    subject -- so its baseline uses the pooled training text of the five
    subjects the model actually sees, which is the only comparison that means
    anything for it.
    """
    cfg = ctx.cfg
    V = cfg.vocab_size
    train_tok = np.asarray(ctx.train)
    tidx = ctx.train_idx
    counts: Dict[str, np.ndarray] = {}
    pooled = np.zeros(V, dtype=np.float64)
    for s in cfg.train_subjects:
        counts[s] = np.zeros(V, dtype=np.float64)
    for s, st, ln in zip(tidx["subject"], tidx["start"], tidx["length"]):
        if s == pack.BIO_SUBJECT:
            continue
        seg = train_tok[int(st):int(st) + int(ln)]
        bc = np.bincount(seg, minlength=V)
        counts[s] += bc
        pooled += bc

    test_tok = np.asarray(ctx.held["test"])
    hidx = ctx.held_idx["test"]
    base: Dict[str, Dict[str, Any]] = {}
    for s in cfg.all_subjects:
        src = counts.get(s, pooled)
        logp = np.log(src + 1.0) - np.log(src.sum() + V)
        total = 0.0
        n = 0
        for ss, st, ln in zip(hidx["subject"], hidx["start"], hidx["length"]):
            if ss != s:
                continue
            seg = test_tok[int(st):int(st) + int(ln)]
            total -= float(logp[seg].sum())
            n += int(seg.size)
        base[s] = {"unigram_cross_entropy": round(total / n, 4), "tokens": n,
                   "counts_from": "pooled 5 subjects" if s not in counts
                   else "own training text"}

    smoke_path = ROOT / "bench" / "results" / "smoke_real_t1_pkm.json"
    smoke = (json.loads(smoke_path.read_text())["heldout_loss_by_subject"]
             if smoke_path.exists() else {})
    problems = []
    for s in cfg.all_subjects:
        m = smoke.get(s, {}).get("loss")
        base[s]["smoke_run_loss"] = m
        if m is None:
            problems.append(f"{s}: no smoke-run loss recorded")
        elif m >= base[s]["unigram_cross_entropy"]:
            problems.append(f"{s}: model {m:.3f} >= unigram "
                            f"{base[s]['unigram_cross_entropy']:.3f}")
    return Check("A17", "Model beats the per-subject unigram baseline",
                 not problems,
                 "; ".join(f"{s.split()[0]}: model "
                           f"{base[s]['smoke_run_loss']} vs unigram "
                           f"{base[s]['unigram_cross_entropy']}"
                           for s in cfg.all_subjects)
                 + ("; " + "; ".join(problems) if problems else ""), base)


def a18_learnability(ctx: Ctx) -> Check:
    path = ROOT / "bench" / "results" / "learnability_t1_pkm.json"
    if not path.exists():
        return Check("A18", "Biography facts are learnable", False,
                     "no bench/results/learnability_t1_pkm.json -- run "
                     "`python bench/learnability_run.py` first", skipped=True)
    r = json.loads(path.read_text())
    v = r["verdict"]
    t = v["test_top1"]
    p = v["paraphrase_top1"]
    ratio = v["checks"]["frequent_at_least_twice_control"]["ratio"]
    return Check("A18", "Biography facts are learnable", bool(v["pass"]),
                 f"{r['steps']:,} steps / {r['tokens_seen'] / 1e6:.0f}M tokens "
                 f"in {r['train_seconds'] / 3600:.2f} h of training. "
                 f"test top-1: frequent {t['frequent']:.1%}, normal "
                 f"{t['normal']:.1%}, rare {t['rare']:.1%}, control "
                 f"{t['control']:.1%} (frequent/control = {ratio}x, needs 2x; "
                 f"monotone "
                 f"{'yes' if v['checks']['monotone_frequent_normal_rare']['pass'] else 'NO'}). "
                 f"paraphrase top-1: frequent {p['frequent']:.1%}, control "
                 f"{p['control']:.1%}",
                 {"verdict": v, "steps": r["steps"],
                  "tokens_seen": r["tokens_seen"]})


# ---------------------------------------------------------------------------
# optional: re-stream the pinned Pile and verify the labels at source
# ---------------------------------------------------------------------------
def check_source_labels(cfg: DataConfig) -> Check:
    """Re-read `val.jsonl.zst` and compare every held-out subject at source.

    A10 checks three places inside the bundle agree. This is the only check
    that leaves the bundle: it goes back to the pinned revision and compares
    `meta.pile_set_name` for every held-out document. Needs the network.
    """
    import json as _json
    from data.pile_extract import _open_stream
    want: Dict[int, Tuple[str, str]] = {}
    for half in cfg.pack_halves:
        for s in cfg.all_subjects:
            for r in read_jsonl(cfg.heldout_dir / half / f"{cfg.slug(s)}.jsonl.gz"):
                want[int(r["line"])] = (r["doc_id"], r["subject"])
    resp, counter, stream = _open_stream(cfg, cfg.heldout_files[0])
    checked = 0
    bad: List[str] = []
    try:
        for i, line in enumerate(stream):
            if i not in want:
                continue
            doc_id, subject = want.pop(i)
            got = _json.loads(line).get("meta", {}).get("pile_set_name")
            checked += 1
            if got != subject:
                bad.append(f"{doc_id}: bundle says {subject!r}, Pile says {got!r}")
            if not want:
                break
    finally:
        stream.close()
        resp.close()
    return Check("A10b", "Held-out labels verified against the pinned Pile",
                 not bad and not want,
                 f"{checked:,} held-out documents re-read from "
                 f"{cfg.dataset}@{cfg.revision[:12]}/{cfg.heldout_files[0]}; "
                 f"{len(bad)} subject mismatches, {len(want)} line numbers not "
                 f"found" + ("; " + "; ".join(bad[:3]) if bad else ""),
                 {"checked": checked, "mismatches": bad[:10],
                  "not_found": len(want)})


# ---------------------------------------------------------------------------
# driver
# ---------------------------------------------------------------------------
CHECKS: List[Tuple[str, str, Callable[[Ctx], Check]]] = [
    ("A1", "Rebuild is byte-identical", a1_rebuild),
    ("A2", "Bundle verifies against the manifest", a2_verify),
    ("A3", "Token counts per subject and half", a3_token_counts),
    ("A4", "Shares in every 1M-token window", a4_windows),
    ("A5", "Format: dtype, vocab, EOT, tiling", a5_format),
    ("A6", "Segments decode to the source", a6_decode),
    ("A7", "Leaks: ids, hashes, 13-grams", a7_leaks),
    ("A8", "Held-out halves", a8_halves),
    ("A9", "No held-out-only subject in train", a9_no_uspto_in_train),
    ("A10", "Subject labels agree", a10_labels),
    ("A11", "Bag-of-words classifier", a11_bow_classifier),
    ("A12", "Biography facts", a12_bio_facts),
    ("A13", "Fact prompts", a13_prompts),
    ("A14", "Exposure and control isolation", a14_exposure),
    ("A15", "Probe floor", a15_scorer_floor),
    ("A16", "Loader", a16_loader),
    ("A17", "Unigram baseline", a17_unigram),
    ("A18", "Biography facts are learnable", a18_learnability),
]


def write_report(cfg: DataConfig, checks: List[Check], path: Path) -> Path:
    man = json.loads(cfg.manifest_path.read_text())
    n_fail = sum(1 for c in checks if not c.passed and not c.skipped)
    n_skip = sum(1 for c in checks if c.skipped)
    lines = [
        f"# Validation report — data `{cfg.version}`",
        "",
        f"**{'ALL CHECKS PASS' if n_fail == 0 else f'{n_fail} CHECK(S) FAILED'}**"
        + (f" ({n_skip} skipped)" if n_skip else ""),
        "",
        f"- generated by `python -m data.validate --config {cfg.config_path}`",
        f"- config fingerprints: pile `{cfg.fingerprint('pile')[:16]}`, "
        f"bios `{cfg.fingerprint('bios')[:16]}`, pack `{cfg.fingerprint('pack')[:16]}`",
        f"- Pile revision `{cfg.revision}`",
        f"- bundle: {man['n_files']} files, "
        f"{man['bytes']['total'] / 1e6:,.1f} MB "
        f"({man['bytes']['required'] / 1e6:,.1f} MB without `raw/`)",
        f"- git `{man['git']['commit'][:12]}`",
        "",
        "| check | what | result | measured |",
        "|---|---|:---:|---|",
    ]
    for c in checks:
        detail = c.detail.replace("|", "\\|")
        lines.append(f"| **{c.id}** | {c.title} | **{c.status}** | {detail} |")
    lines += ["", "## Timings", "",
              "| check | seconds |", "|---|---:|"]
    for c in checks:
        lines.append(f"| {c.id} | {c.seconds:.1f} |")
    lines += ["", f"Total {sum(c.seconds for c in checks):.0f} s.", ""]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--config", default="configs/data/v1.yaml")
    ap.add_argument("--small", action="store_true")
    ap.add_argument("--only", default="", help="comma-separated check ids")
    ap.add_argument("--skip", default="", help="comma-separated check ids")
    ap.add_argument("--check-source", action="store_true",
                    help="also re-stream the pinned Pile (needs the network)")
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)

    cfg = load_config(args.config, small=args.small)
    only = {s.strip() for s in args.only.split(",") if s.strip()}
    skip = {s.strip() for s in args.skip.split(",") if s.strip()}

    print(f"[validate] {cfg.root}  pack fingerprint "
          f"{cfg.fingerprint('pack')[:16]}", flush=True)
    ctx = Ctx(cfg)
    results: List[Check] = []
    for cid, title, fn in CHECKS:
        if (only and cid not in only) or cid in skip:
            results.append(Check(cid, title, True, "skipped by request",
                                 skipped=True))
            continue
        t0 = time.time()
        try:
            c = fn(ctx)
        except Exception as exc:                                 # noqa: BLE001
            import traceback
            traceback.print_exc()
            c = Check(cid, title, False, f"raised {type(exc).__name__}: {exc}")
        c.seconds = time.time() - t0
        results.append(c)
        print(f"[validate] {c.status:4s} {c.id:4s} {c.title} "
              f"({c.seconds:.1f}s)\n           {c.detail}", flush=True)

    if args.check_source:
        t0 = time.time()
        c = check_source_labels(cfg)
        c.seconds = time.time() - t0
        results.append(c)
        print(f"[validate] {c.status:4s} {c.id:4s} {c.title}\n"
              f"           {c.detail}", flush=True)

    out = Path(args.out) if args.out else cfg.root / "validation_report.md"
    write_report(cfg, results, out)
    # machine-readable twin, so the step report's tables are generated and not
    # retyped (data/report_tables.py --stage validate)
    with open(out.with_suffix(".json"), "w", encoding="utf-8") as fh:
        json.dump({
            "version": cfg.version,
            "fingerprints": {k: cfg.fingerprint(k)
                             for k in ("pile", "bios", "pack")},
            "revision": cfg.revision,
            "checks": [{"id": c.id, "title": c.title, "status": c.status,
                        "detail": c.detail, "numbers": c.numbers,
                        "seconds": round(c.seconds, 1)} for c in results],
        }, fh, indent=2, sort_keys=True, default=str)
        fh.write("\n")
    failed = [c.id for c in results if not c.passed and not c.skipped]
    print(f"\n[validate] {len(results) - len(failed)}/{len(results)} passed "
          f"-> {out}")
    if failed:
        print(f"[validate] FAILED: {failed}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
