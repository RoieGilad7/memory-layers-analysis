"""Packing the Pile text and the biographies into token files. No network."""
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import pytest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from data import bios, dedup, pack, split
from data.common import (DataConfig, dumps_record, get_encoder, open_write,
                         read_jsonl)
from data.pack import BIO_SUBJECT, TOKEN_DTYPE
from tests._data_fixtures import CONFIG, body

EOT = 50256
SUBJECTS = ["Pile-CC", "Github"]


# --------------------------------------------------------------------------
# a miniature end-to-end build
# --------------------------------------------------------------------------
def make_cfg(root: Path, seed=None, tokens_per_subject=20000, n_docs=90,
             n_train=16, n_control=4, **over) -> DataConfig:
    raw = yaml.safe_load(CONFIG.read_text())
    r = str(root)
    raw["paths"] = {"root": r, "raw": f"{r}/raw", "work": f"{r}/_work",
                    "train": f"{r}/train", "heldout_pool": f"{r}/heldout_pool",
                    "heldout": f"{r}/heldout", "reports": f"{r}/reports"}
    raw["small"]["root"] = r
    if seed is not None:
        raw["seed"] = seed
    raw["subjects"]["train"] = list(SUBJECTS)
    raw["subjects"]["heldout_only"] = ["USPTO Backgrounds"]
    raw["document"]["min_tokens"] = 20
    raw["targets"]["heldout_tokens_per_half"] = 4000
    raw["targets"]["heldout_min_docs_per_half"] = 2
    raw["pack"]["train_tokens_per_subject"] = tokens_per_subject
    pe = raw["bios"]["people"]
    pe["n_train"], pe["n_control"] = n_train, n_control
    pe["name_candidates_per_gender"] = 120
    sized = [n_train // 2, n_train // 4, 0]
    sized[2] = n_train - sized[0] - sized[1]
    for t, n in zip(pe["tiers"], sized):
        t["n_people"] = n
    pe["tiers"][0]["exposures"] = 6
    pe["tiers"][1]["exposures"] = 10
    pe["tiers"][2]["exposures"] = 14
    for k, v in over.items():
        sec, _, f = k.partition(".")
        raw[sec][f] = v
    return DataConfig(raw=raw)


def _write_raw(cfg, split_name, subject, docs):
    path = cfg.raw_dir / split_name / f"{cfg.slug(subject)}.jsonl.gz"
    src = cfg.train_files[0] if split_name == "train" else cfg.heldout_files[0]
    with open_write(path) as fh:
        for line, text in docs:
            fh.write(dumps_record({
                "doc_id": cfg.doc_id(subject, src, line), "subject": subject,
                "split": split_name, "source": src, "line": line, "text": text}))


def build_mini(root: Path, **kw) -> DataConfig:
    """dedup -> split -> bios -> pack, on synthetic text."""
    cfg = make_cfg(root, **kw)
    n_docs = kw.get("n_docs", 90)
    for si, subject in enumerate(SUBJECTS):
        _write_raw(cfg, "train", subject,
                   [(i * 7, body(f"tr{si}", 420, i)) for i in range(n_docs)])
        _write_raw(cfg, "heldout", subject,
                   [(i, body(f"ho{si}", 300, i)) for i in range(24)])
    _write_raw(cfg, "heldout", "USPTO Backgrounds",
               [(i, body("us", 300, i)) for i in range(24)])
    dedup.run(cfg)
    split.run(cfg)
    bios.run(cfg, name_check=False)
    pack.run(cfg)
    return cfg


@pytest.fixture(scope="module")
def built(tmp_path_factory):
    cfg = build_mini(tmp_path_factory.mktemp("pack"))
    report = json.loads((cfg.reports_dir / "pack_report.json").read_text())
    tokens = np.fromfile(cfg.tokens_dir / "train.bin", dtype=TOKEN_DTYPE)
    index = pack.read_index(cfg.tokens_dir / "train.idx.parquet")
    return cfg, report, tokens, index


# --------------------------------------------------------------------------
# selection: exact token budget per subject
# --------------------------------------------------------------------------
def test_each_subject_contributes_exactly_its_target(built):
    cfg, report, tokens, index = built
    per = report["train"]["per_subject"]
    for subject in cfg.train_subjects:
        assert per[subject]["tokens"] == cfg.pack_tokens_per_subject, subject
    # and the index agrees with the report
    by_subject = Counter()
    for s, n in zip(index["subject"], index["length"]):
        by_subject[s] += int(n)
    for subject in cfg.train_subjects:
        assert by_subject[subject] == cfg.pack_tokens_per_subject, subject


def test_selection_truncates_exactly_one_document_per_subject(built):
    cfg, report, _, index = built
    for subject in cfg.train_subjects:
        rep = report["select"][subject]
        assert rep["tokens_used"] == rep["target"]
        assert rep["partial_document"] is not None
        assert 0 < rep["partial_document_tokens"] < rep["partial_document_full_tokens"]
    # every other selected document appears in full
    lengths = defaultdict(int)
    for d, n in zip(index["doc_id"], index["length"]):
        lengths[d] += int(n)
    partials = {report["select"][s]["partial_document"] for s in cfg.train_subjects}
    for subject in cfg.train_subjects:
        full = {r["doc_id"]: r["n_tokens"] for r in
                read_jsonl(cfg.train_dir / f"{cfg.slug(subject)}.jsonl.gz")}
        for doc_id, got in lengths.items():
            if doc_id in full and doc_id not in partials:
                assert got == full[doc_id], doc_id


def test_selection_is_seeded_and_a_new_seed_picks_other_documents(built):
    """Same documents on disk, same seed -> same cut; new seed -> a new cut."""
    cfg, _, _, _ = built
    same = make_cfg(cfg.root)
    other = make_cfg(cfg.root, seed=424242)
    a, _ = pack.select_subject(cfg, "Pile-CC")
    b, _ = pack.select_subject(same, "Pile-CC")
    c, rep_c = pack.select_subject(other, "Pile-CC")
    assert [i.doc_id for i in a] == [i.doc_id for i in b]
    assert [i.doc_id for i in a] != [i.doc_id for i in c]
    # but both land on exactly the target
    assert sum(i.take for i in a) == sum(i.take for i in c) == \
        cfg.pack_tokens_per_subject


# --------------------------------------------------------------------------
# biography copies
# --------------------------------------------------------------------------
def test_copies_per_rewording_spreads_evenly():
    assert pack.copies_per_rewording(30, 4) == [8, 8, 7, 7]
    assert pack.copies_per_rewording(100, 4) == [25, 25, 25, 25]
    assert pack.copies_per_rewording(300, 4) == [75, 75, 75, 75]
    for n in range(1, 400):
        c = pack.copies_per_rewording(n, 4)
        assert sum(c) == n
        assert max(c) - min(c) <= 1


def test_copy_counts_match_the_tier_and_spread_over_the_rewordings(built):
    cfg, report, _, index = built
    people = {p["person_id"]: p for p in read_jsonl(cfg.bios_dir / "people.jsonl")}
    seen = defaultdict(Counter)
    for s, pid, rw in zip(index["subject"], index["person_id"],
                          index["rewording_id"]):
        if s == BIO_SUBJECT:
            seen[pid][int(rw)] += 1

    for pid, p in people.items():
        want = int(p["target_exposures"])
        if p["split"] != "train":
            assert pid not in seen, f"{pid} is control but has copies"
            continue
        assert sum(seen[pid].values()) == want, pid
        counts = [seen[pid][r] for r in range(p["n_rewordings"])]
        assert counts == pack.copies_per_rewording(want, p["n_rewordings"]), pid
    assert report["biographies"]["copies"] == sum(
        int(p["target_exposures"]) for p in people.values() if p["split"] == "train")


def test_control_people_contribute_nothing(built):
    cfg, _, _, index = built
    control = {p["person_id"] for p in read_jsonl(cfg.bios_dir / "people.jsonl")
               if p["split"] == "control"}
    assert control
    assert not (control & {p for p in index["person_id"] if p})


# --------------------------------------------------------------------------
# the no-split rule
# --------------------------------------------------------------------------
def test_no_biography_copy_crosses_a_sequence_boundary(built):
    cfg, _, _, index = built
    block = cfg.block_size
    n = 0
    for s, start, length in zip(index["subject"], index["start"], index["length"]):
        if s != BIO_SUBJECT:
            continue
        assert start // block == (start + length - 1) // block, (start, length)
        n += 1
    assert n > 0


def test_pile_documents_are_allowed_to_cross_boundaries(built):
    cfg, _, _, index = built
    block = cfg.block_size
    crossing = sum(1 for s, st, ln in zip(index["subject"], index["start"],
                                          index["length"])
                   if s != BIO_SUBJECT and st // block != (st + ln - 1) // block)
    assert crossing > 0, "with 20k tokens per subject some Pile doc must straddle"


def test_moved_biographies_are_reported_and_filler_is_pile_text(built):
    cfg, report, tokens, index = built
    assert report["train"]["biographies_moved_to_next_sequence"] > 0
    assert report["train"]["filler_tokens"] > 0
    # filler never invents tokens: subject totals are still exact
    for subject in cfg.train_subjects:
        assert report["train"]["per_subject"][subject]["tokens"] == \
            cfg.pack_tokens_per_subject


# --------------------------------------------------------------------------
# window shares
# --------------------------------------------------------------------------
def test_window_shares_are_within_tolerance(built):
    cfg, report, _, _ = built
    w = report["train"]["window_shares"]
    assert set(w) == set(cfg.train_subjects) | {BIO_SUBJECT}
    for k, v in w.items():
        assert v["worst_deviation_points"] <= cfg.window_tolerance_points, (k, v)


def test_deficit_greedy_beats_a_shuffle_on_window_balance():
    """The reason the interleave is not just a seeded shuffle."""
    import random

    class It:
        def __init__(self, take):
            self.take = take

    streams = {"big": [It(2000) for _ in range(450)],
               "small": [It(80) for _ in range(1250)]}
    greedy = pack.interleave(streams)
    g = pack.window_shares(greedy, streams, 100_000)

    flat = [(k, i) for k in streams for i in range(len(streams[k]))]
    random.Random(0).shuffle(flat)
    s = pack.window_shares(flat, streams, 100_000)

    worst_g = max(v["worst_deviation_points"] for v in g.values())
    worst_s = max(v["worst_deviation_points"] for v in s.values())
    assert worst_g < worst_s / 2, (worst_g, worst_s)
    assert worst_g <= 2.0


# --------------------------------------------------------------------------
# file-level invariants
# --------------------------------------------------------------------------
def test_dtype_and_vocab_range(built):
    cfg, _, tokens, _ = built
    assert tokens.dtype == np.uint16
    assert tokens.size % cfg.block_size == 0
    assert int(tokens.max()) < cfg.vocab_size
    assert int(tokens.min()) >= 0


def test_index_segments_tile_the_file_and_the_gaps_are_all_eot(built):
    cfg, _, tokens, index = built
    starts = np.asarray(index["start"], dtype=np.int64)
    lengths = np.asarray(index["length"], dtype=np.int64)
    assert (np.diff(starts) > 0).all(), "index rows must be in file order"
    ends = starts + lengths
    assert (starts[1:] >= ends[:-1]).all(), "segments overlap"

    covered = np.zeros(tokens.size, dtype=bool)
    for s, e in zip(starts, ends):
        assert not covered[s:e].any(), "segment written twice"
        covered[s:e] = True
    # a document token is never EOT, and every uncovered token is EOT
    assert (tokens[covered] != cfg.eot_token).all()
    assert (tokens[~covered] == cfg.eot_token).all()
    assert int(lengths.sum()) == int(covered.sum())


def test_one_eot_separates_consecutive_documents(built):
    cfg, report, tokens, index = built
    starts = np.asarray(index["start"], dtype=np.int64)
    lengths = np.asarray(index["length"], dtype=np.int64)
    gaps = starts[1:] - (starts[:-1] + lengths[:-1])
    assert gaps.min() >= 1, "documents must be separated"
    # gaps bigger than one EOT only happen where a biography was moved and
    # there was no Pile text left to fill with
    assert int((gaps > 1).sum()) * 1 <= report["train"]["eot_pad_tokens"] + 1


def test_decoding_index_segments_reproduces_the_source_text(built):
    cfg, _, tokens, index = built
    enc = get_encoder(cfg.tokenizer_name, cfg.vocab_size)
    source = {}
    for subject in cfg.train_subjects:
        for r in read_jsonl(cfg.train_dir / f"{cfg.slug(subject)}.jsonl.gz"):
            source[r["doc_id"]] = r["text"]
    for r in read_jsonl(cfg.bios_dir / "bios_train.jsonl"):
        source[r["doc_id"]] = r["text"]

    rng = np.random.default_rng(0)
    n = len(index["start"])
    sample = rng.choice(n, size=min(1000, n), replace=False)
    whole_docs = 0
    for j in sample:
        doc_id = index["doc_id"][j]
        start, length = int(index["start"][j]), int(index["length"][j])
        offset = int(index["doc_offset"][j])
        want = np.asarray(enc.encode_ordinary(source[doc_id]), dtype=TOKEN_DTYPE)
        got = tokens[start:start + length]
        assert np.array_equal(got, want[offset:offset + length]), doc_id
        if offset == 0 and length == want.size:
            assert enc.decode(got.tolist()) == source[doc_id], doc_id
            whole_docs += 1
    assert whole_docs > 0


# --------------------------------------------------------------------------
# held-out files
# --------------------------------------------------------------------------
def test_heldout_files_hold_every_subject_and_no_biographies(built):
    cfg, report, _, _ = built
    for half in cfg.pack_halves:
        toks = np.fromfile(cfg.heldout_tokens_dir / f"{half}.bin",
                           dtype=TOKEN_DTYPE)
        idx = pack.read_index(cfg.heldout_tokens_dir / f"{half}.idx.parquet")
        assert toks.dtype == np.uint16 and int(toks.max()) < cfg.vocab_size
        subjects = set(idx["subject"])
        assert subjects == set(cfg.all_subjects), (half, subjects)
        assert BIO_SUBJECT not in subjects
        # the same tiling invariant
        covered = np.zeros(toks.size, dtype=bool)
        for s, n in zip(idx["start"], idx["length"]):
            covered[int(s):int(s) + int(n)] = True
        assert (toks[~covered] == cfg.eot_token).all()
        assert (toks[covered] != cfg.eot_token).all()
        # every document is within the cap
        assert int(np.asarray(idx["length"]).max()) <= cfg.max_tokens
        assert report["heldout"][half]["documents"] == len(idx["start"])


def test_heldout_index_keeps_the_ngram_overlap(built):
    cfg, _, _, _ = built
    for half in cfg.pack_halves:
        idx = pack.read_index(cfg.heldout_tokens_dir / f"{half}.idx.parquet")
        assert "ngram_overlap" in idx
        want = {}
        for subject in cfg.all_subjects:
            for r in read_jsonl(cfg.heldout_dir / half /
                                f"{cfg.slug(subject)}.jsonl.gz"):
                want[r["doc_id"]] = r.get("ngram_overlap")
        n = 0
        for d, ov in zip(idx["doc_id"], idx["ngram_overlap"]):
            w = want[d]
            if w is None:
                assert ov is None or np.isnan(ov)
            else:
                assert abs(float(ov) - w) < 1e-9, d
                n += 1
        assert n > 0


# --------------------------------------------------------------------------
# determinism
# --------------------------------------------------------------------------
def test_rebuilding_gives_byte_identical_files(tmp_path):
    import hashlib

    def digest(cfg):
        out = {}
        for p in [cfg.tokens_dir / "train.bin",
                  cfg.tokens_dir / "train.idx.parquet"] + [
                      cfg.heldout_tokens_dir / f"{h}.{e}"
                      for h in cfg.pack_halves for e in ("bin", "idx.parquet")]:
            out[p.name] = hashlib.sha256(p.read_bytes()).hexdigest()
        return out

    a = build_mini(tmp_path / "a")
    b = build_mini(tmp_path / "b")
    c = build_mini(tmp_path / "c", seed=777)
    da, db, dc = digest(a), digest(b), digest(c)
    assert da == db
    assert da["train.bin"] != dc["train.bin"]
