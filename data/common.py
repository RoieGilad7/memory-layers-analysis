"""Shared pieces for the data build: config, cleaning, token capping, hashing.

Everything here is a pure function of its arguments and of the config, so the
whole build is reproducible: the only seed is `cfg.seed`, and the only hashes
are fixed-constant ones (never Python's randomized `hash()`).
"""
from __future__ import annotations

import gzip
import hashlib
import json
import re
import shutil
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, Iterator, List, Optional, Sequence, Tuple

import numpy as np
import yaml

__all__ = [
    "DataConfig", "load_config", "clean_text", "get_encoder", "count_tokens",
    "cap_to_max_tokens", "text_sha256", "ngram_hashes", "overlap_rate",
    "heldout_half", "open_write", "CHARS_PER_TOKEN_BOUND", "open_read", "write_jsonl", "read_jsonl",
    "dumps_record", "free_disk_gb", "merge_gz", "ROOT",
]

ROOT = Path(__file__).resolve().parent.parent


# --------------------------------------------------------------------------
# config
# --------------------------------------------------------------------------
@dataclass
class DataConfig:
    """Resolved config. `--small` scales every token target by `small.scale`."""

    raw: Dict[str, Any]
    small: bool = False

    # filled in __post_init__
    seed: int = 0
    scale: float = 1.0
    root: Path = field(default_factory=Path)

    def __post_init__(self) -> None:
        c = self.raw
        self.version = c["version"]
        self.seed = int(c["seed"])
        self.scale = float(c["small"]["scale"]) if self.small else 1.0

        self.tokenizer_name = c["tokenizer"]["name"]
        self.vocab_size = int(c["tokenizer"]["vocab_size"])

        s = c["source"]
        self.dataset = s["dataset"]
        self.repo_type = s["repo_type"]
        self.revision = s["revision"]
        self.subject_field = s["subject_field"]
        self.train_files: List[str] = list(s["train_files"])
        self.heldout_files: List[str] = list(s["heldout_files"])
        self.train_fallback_files: List[str] = list(s["train_fallback_files"])
        self.heldout_fallback_files: List[str] = list(s["heldout_fallback_files"])
        self.source_tags: Dict[str, str] = dict(s["source_tags"])

        sub = c["subjects"]
        self.train_subjects: List[str] = list(sub["train"])
        self.heldout_only_subjects: List[str] = list(sub["heldout_only"])
        self.all_subjects: List[str] = self.train_subjects + self.heldout_only_subjects
        self.slugs: Dict[str, str] = dict(sub["slugs"])
        missing = [s_ for s_ in self.all_subjects if s_ not in self.slugs]
        if missing:
            raise ValueError(f"subjects missing a slug in the config: {missing}")

        t = c["targets"]
        self.total_train_tokens = self._scaled(t["total_train_tokens"])
        self.train_tokens_per_subject = self._scaled(t["train_tokens_per_subject"])
        self.collect_slack = float(t["collect_slack"])
        self.collect_train_tokens_per_subject = int(round(
            self.train_tokens_per_subject * (1.0 + self.collect_slack)))
        self.bio_share = float(t["bio_share"])
        self.heldout_halves: List[str] = list(t["heldout_halves"])
        self.heldout_tokens_per_subject = self._scaled(t["heldout_tokens_per_subject"])
        self.heldout_collect_slack = float(t["heldout_collect_slack"])
        self.collect_heldout_tokens_per_subject = int(round(
            self.heldout_tokens_per_subject * (1.0 + self.heldout_collect_slack)))
        self.heldout_tokens_per_half = self._scaled(t["heldout_tokens_per_half"])
        self.heldout_min_docs_per_half = max(
            1, int(round(t["heldout_min_docs_per_half"] * self.scale)))

        d = c["document"]
        self.max_tokens = int(d["max_tokens"])
        self.min_tokens = int(d["min_tokens"])

        cl = c["clean"]
        self.unicode_form = cl["unicode_form"]
        self.max_consecutive_newlines = int(cl["max_consecutive_newlines"])

        dd = c["dedup"]
        self.exact_dedup = bool(dd["exact"])
        self.ngram_n = int(dd["ngram_n"])
        self.ngram_drop_threshold = float(dd["ngram_drop_threshold"])

        b = c.get("bios")
        self.bios = b
        if b is not None:
            self.bio_attributes: List[str] = list(b["attributes"])
            self.bio_genders: List[str] = list(b["genders"])
            pe = b["people"]
            # People counts are kept divisible by the number of genders, so the
            # tiers stay *exactly* gender-balanced rather than balanced on
            # average -- including under --small, where 700 * 0.01 = 7 would
            # otherwise make a balanced split impossible.
            ng = len(self.bio_genders)
            self.bio_n_control = self._scaled_multiple(pe["n_control"], ng)
            self.bio_tiers = [
                {"name": t["name"],
                 "n_people": self._scaled_multiple(t["n_people"], ng),
                 "exposures": int(t["exposures"])}
                for t in pe["tiers"]]
            self.bio_n_train = sum(t["n_people"] for t in self.bio_tiers)
            self.bio_control_tier = pe["control_tier"]
            self.bio_name_candidates_per_gender = self._scaled(
                pe["name_candidates_per_gender"])
            rw = b["rewordings"]
            self.bio_n_rewordings = int(rw["n_train"])
            self.bio_discovery_rewordings = list(rw["discovery_rewordings"])
            self.bio_test_rewordings = list(rw["test_rewordings"])
            self.bio_heldout_role = rw["heldout_role"]
            self.bio_heldout_context_rewording = int(rw["heldout_context_rewording"])
            tp = b["templates"]
            self.bio_n_templates = int(tp["n_train_per_attribute"])
            self.bio_n_heldout_templates = int(tp["n_heldout_per_attribute"])
            v = b["values"]
            self.bio_value_targets = {a: int(v[a]) for a in self.bio_attributes}
            self.bio_year_range = tuple(v["birth_year_range"])
            self.bio_first_token_unique = list(v["first_token_unique"])
            self.bio_first_two_tokens_unique = list(v["first_two_tokens_unique"])
            nc = b["name_check"]
            self.bio_name_check = bool(nc["enabled"])
            self.bio_name_check_dirs = list(nc["corpus_dirs"])
            self.bio_name_check_case_sensitive = bool(nc["case_sensitive"])
            if not self.small and self.bio_n_train != int(pe["n_train"]):
                raise ValueError(
                    "bios.people.tiers must sum to bios.people.n_train "
                    f"({self.bio_n_train} != {pe['n_train']})")

        p = c["paths"]
        base = Path(c["small"]["root"]) if self.small else Path(p["root"])
        self.root = ROOT / base
        rel = Path(p["root"])
        # every other path is declared relative to paths.root, so --small only
        # has to redirect the root
        def under(key: str) -> Path:
            return self.root / Path(p[key]).relative_to(rel)
        self.raw_dir = under("raw")
        self.work_dir = under("work")
        self.train_dir = under("train")
        self.heldout_pool_dir = under("heldout_pool")
        self.heldout_dir = under("heldout")
        self.reports_dir = under("reports")
        self.bios_dir = self.root / "bios"
        self.samples_dir = self.root / "samples"

    # -- helpers -----------------------------------------------------------
    def _scaled(self, n: Any) -> int:
        return int(round(int(n) * self.scale))

    def _scaled_multiple(self, n: Any, k: int) -> int:
        """Scaled, then rounded up to a multiple of `k` (at least `k`)."""
        v = self._scaled(n)
        return max(k, -(-v // k) * k)

    def slug(self, subject: str) -> str:
        return self.slugs[subject]

    def source_tag(self, filename: str) -> str:
        if filename not in self.source_tags:
            raise ValueError(f"no source_tag for {filename!r}; add one to the config")
        return self.source_tags[filename]

    def target_tokens(self, split: str, subject: str) -> int:
        """Collection budget (target + slack) for one (split, subject)."""
        if split == "train":
            if subject not in self.train_subjects:
                return 0
            return self.collect_train_tokens_per_subject
        if split == "heldout":
            return self.collect_heldout_tokens_per_subject
        raise ValueError(split)

    def subjects_for(self, split: str) -> List[str]:
        return self.train_subjects if split == "train" else self.all_subjects

    # Which config sections each stage's output actually depends on. Scoping the
    # fingerprint this way is what keeps an edit to one stage's numbers from
    # invalidating another stage's completed work -- adding the `bios` section
    # must not make `pile_extract` think its 1.27 GB archive is stale.
    _SCOPE_DROP = {"pile": ("bios",)}
    _SCOPE_KEEP = {"bios": ("version", "seed", "tokenizer", "bios")}

    def fingerprint(self, scope: str = "all") -> str:
        """sha256 of the resolved config, or of the part one stage depends on.

        `scope="all"` hashes everything. `"pile"` drops the `bios` section;
        `"bios"` keeps only the sections biographies are built from. Each stage
        records its own scope, so `--stage pile` and `--stage bios` cannot
        invalidate each other.
        """
        if scope == "all":
            raw = self.raw
        elif scope in self._SCOPE_DROP:
            drop = self._SCOPE_DROP[scope]
            raw = {k: v for k, v in self.raw.items() if k not in drop}
        elif scope in self._SCOPE_KEEP:
            raw = {k: self.raw[k] for k in self._SCOPE_KEEP[scope] if k in self.raw}
        else:
            raise ValueError(f"unknown fingerprint scope {scope!r}")
        payload = json.dumps(
            {"raw": raw, "small": self.small}, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def doc_id(self, subject: str, filename: str, line: int) -> str:
        return f"{self.slug(subject)}-{self.source_tag(filename)}-{line}"


def load_config(path: str | Path, small: bool = False) -> DataConfig:
    with open(path, "r", encoding="utf-8") as fh:
        raw = yaml.safe_load(fh)
    return DataConfig(raw=raw, small=small)


# --------------------------------------------------------------------------
# cleaning
# --------------------------------------------------------------------------
# horizontal whitespace: everything \s matches except the newline itself
_H_WS_RUN = re.compile(r"[^\S\n]+")
_INDENT = re.compile(r"^[ \t]*")
_DROP_CHARS = str.maketrans({"﻿": None, "\x00": None})


def clean_text(text: str, form: str = "NFC", max_consecutive_newlines: int = 2) -> str:
    """NFC, LF line endings, collapse whitespace runs, keep newlines and indentation.

    Indentation is the leading run of spaces/tabs on each line and is copied
    through byte for byte -- that is what keeps Github code readable. Inside the
    line, runs of horizontal whitespace collapse to a single space and trailing
    whitespace goes. Runs of more than `max_consecutive_newlines` newlines
    collapse to exactly that many, and the document is stripped at both ends.
    """
    if not text:
        return ""
    text = unicodedata.normalize(form, text)
    text = text.translate(_DROP_CHARS)
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    out: List[str] = []
    for line in text.split("\n"):
        indent = _INDENT.match(line).group(0)
        rest = _H_WS_RUN.sub(" ", line[len(indent):]).rstrip()
        out.append(indent + rest if rest else "")
    text = "\n".join(out)

    if max_consecutive_newlines > 0:
        text = re.sub(r"\n{%d,}" % (max_consecutive_newlines + 1),
                      "\n" * max_consecutive_newlines, text)
    return text.strip()


# --------------------------------------------------------------------------
# tokenization (counting only -- no token files are written in this stage)
# --------------------------------------------------------------------------
_ENC = None
# A GPT-2 token covers at most ~40 characters, so this many characters is a
# safe over-estimate of the prefix holding the first `max_tokens` tokens.
CHARS_PER_TOKEN_BOUND = 64


def get_encoder(name: str = "gpt2", vocab_size: Optional[int] = None):
    global _ENC
    if _ENC is None:
        import tiktoken
        _ENC = tiktoken.get_encoding(name)
    if vocab_size is not None and _ENC.n_vocab != vocab_size:
        raise ValueError(f"tokenizer vocab {_ENC.n_vocab} != config {vocab_size}")
    return _ENC


def _encode(enc, text: str) -> List[int]:
    # encode_ordinary: never raises on a literal "<|endoftext|>" in the text
    return enc.encode_ordinary(text)


def count_tokens(enc, text: str, max_tokens: Optional[int] = None) -> int:
    """Token count, optionally capped. Only encodes a safe prefix when capping."""
    if max_tokens is not None:
        limit = max_tokens * CHARS_PER_TOKEN_BOUND
        if len(text) > limit:
            return min(max_tokens, len(_encode(enc, text[:limit])))
        return min(max_tokens, len(_encode(enc, text)))
    return len(_encode(enc, text))


def cap_to_max_tokens(enc, text: str, max_tokens: int) -> Tuple[str, int, bool]:
    """Cut `text` to its first `max_tokens` GPT-2 tokens.

    Returns (text, n_tokens, truncated). The returned text is guaranteed to
    re-encode to at most `max_tokens` tokens, which is the invariant the rest of
    the pipeline (and the tests) rely on: decode(encode(x)[:n]) can re-encode to
    slightly more than n, so the cut is iterated to a fixed point.
    """
    limit = max_tokens * CHARS_PER_TOKEN_BOUND
    probe = text[:limit] if len(text) > limit else text
    toks = _encode(enc, probe)
    if len(toks) <= max_tokens and len(probe) == len(text):
        return text, len(toks), False

    cut = max_tokens
    for _ in range(8):
        out = enc.decode_bytes(toks[:cut]).decode("utf-8", errors="ignore")
        n = len(_encode(enc, out))
        if n <= max_tokens:
            return out, n, True
        cut -= (n - max_tokens)
        if cut <= 0:
            break
    raise RuntimeError("could not cap document to max_tokens")  # pragma: no cover


# --------------------------------------------------------------------------
# hashing
# --------------------------------------------------------------------------
def text_sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


_FNV_OFFSET = np.uint64(14695981039346656037)
_FNV_PRIME = np.uint64(1099511628211)


def ngram_hashes(tokens: Sequence[int] | np.ndarray, n: int = 13) -> np.ndarray:
    """Fixed-constant 64-bit hashes of every token n-gram, in order.

    FNV-1a over the n token ids, then a splitmix64 finalizer so neighbouring
    n-grams do not share high bits. Deterministic across runs and machines --
    unlike Python's `hash()`, which is seeded per process.
    """
    t = np.asarray(tokens, dtype=np.uint64)
    m = t.size - n + 1
    if m <= 0:
        return np.empty(0, dtype=np.uint64)
    with np.errstate(over="ignore"):
        h = np.full(m, _FNV_OFFSET, dtype=np.uint64)
        for k in range(n):
            h = (h ^ t[k:k + m]) * _FNV_PRIME
        # splitmix64 finalizer
        h ^= h >> np.uint64(30)
        h *= np.uint64(13787848793156543929)
        h ^= h >> np.uint64(27)
        h *= np.uint64(10723151780598845931)
        h ^= h >> np.uint64(31)
    return h


def overlap_rate(held: np.ndarray, train_sorted: np.ndarray) -> Tuple[int, int]:
    """(n n-grams of `held` present in `train_sorted`, total n-grams of `held`)."""
    if held.size == 0 or train_sorted.size == 0:
        return 0, int(held.size)
    idx = np.searchsorted(train_sorted, held)
    idx[idx >= train_sorted.size] = 0
    return int((train_sorted[idx] == held).sum()), int(held.size)


def heldout_half(doc_id: str, seed: int, halves: Sequence[str]) -> str:
    """Seeded, stable assignment of one document to a held-out half."""
    h = hashlib.blake2b(f"{seed}:{doc_id}".encode("utf-8"), digest_size=8).digest()
    return halves[int.from_bytes(h, "big") % len(halves)]


# --------------------------------------------------------------------------
# JSONL / gzip IO -- mtime=0 everywhere so outputs are byte-identical
# --------------------------------------------------------------------------
def open_write(path: Path, append: bool = False):
    path.parent.mkdir(parents=True, exist_ok=True)
    if str(path).endswith(".gz"):
        return gzip.GzipFile(filename=str(path), mode="ab" if append else "wb",
                             compresslevel=6, mtime=0)
    return open(path, "ab" if append else "wb")


def open_read(path: Path):
    if str(path).endswith(".gz"):
        return gzip.open(path, "rb")
    return open(path, "rb")


def dumps_record(obj: Dict[str, Any]) -> bytes:
    return (json.dumps(obj, sort_keys=True, ensure_ascii=False,
                       separators=(",", ":")) + "\n").encode("utf-8")


def write_jsonl(fh, obj: Dict[str, Any]) -> int:
    b = dumps_record(obj)
    fh.write(b)
    return len(b)


def read_jsonl(path: Path) -> Iterator[Dict[str, Any]]:
    if not Path(path).exists():
        return
    with open_read(Path(path)) as fh:
        for line in fh:
            line = line.strip()
            if line:
                yield json.loads(line)


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, indent=2, sort_keys=True, ensure_ascii=False)
        fh.write("\n")


def free_disk_gb(path: Path | str = ROOT) -> float:
    return shutil.disk_usage(str(path)).free / 1e9


def merge_gz(parts: Iterable[Path], out: Path) -> None:
    """Merge gzip part files into ONE gzip member, in the order given.

    Simply concatenating the parts would also be a valid gzip stream, but the
    member layout -- and therefore the file's bytes -- would then depend on
    where the extractor happened to checkpoint. Recompressing into a single
    member makes the archive byte-identical for the same documents however the
    run was blocked, interrupted or resumed.
    """
    out.parent.mkdir(parents=True, exist_ok=True)
    with gzip.GzipFile(filename=str(out), mode="wb", compresslevel=6, mtime=0) as dst:
        for p in parts:
            with gzip.open(p, "rb") as src:
                shutil.copyfileobj(src, dst, length=1 << 20)
