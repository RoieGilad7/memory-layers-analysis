"""Stage 2 -- clean, cap at 4096 tokens, and deduplicate.

Two passes, both deterministic:

  Pass A (clean + exact dedup)
      NFC, whitespace normalization, the 4096-token cut, then drop empty
      documents, documents under `document.min_tokens`, and exact duplicates
      (sha256 of the cleaned text) *within and across splits*. Documents are
      visited in a fixed order -- train before held-out, config subject order,
      then source file and line -- so which copy of a duplicate survives never
      depends on timing. Train documents land in their final home; held-out
      documents go to scratch for pass B.

  Pass B (13-gram contamination, per subject)
      Hash every GPT-2 token 13-gram of the subject's *training* documents into
      one sorted uint64 array, then for each held-out document of the same
      subject measure the fraction of its 13-grams present there. A held-out
      document is dropped when that fraction exceeds `dedup.ngram_drop_threshold`
      (0.50). The aggregate rate per subject is reported but never blocks.

Writes `<reports>/dedup_log.json`: counts dropped per reason per subject.
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from data.common import (CHARS_PER_TOKEN_BOUND, DataConfig, cap_to_max_tokens,
                         clean_text, dumps_record, get_encoder, load_config,
                         ngram_hashes, open_write, overlap_rate, read_jsonl,
                         text_sha256, write_json)

REASONS = ("empty", "under_min_tokens", "exact_dup_same_split",
           "exact_dup_cross_split", "ngram_overlap")


def _empty_counts() -> Dict[str, int]:
    d = {"docs_in": 0, "docs_kept": 0, "tokens_kept": 0, "docs_truncated": 0}
    d.update({f"dropped_{r}": 0 for r in REASONS})
    return d


def clean_record(enc, rec: Dict[str, Any], cfg: DataConfig
                 ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """Clean and cap one raw record. Returns (cleaned record, drop reason)."""
    raw = rec.get("text") or ""
    limit = cfg.max_tokens * CHARS_PER_TOKEN_BOUND
    # Cleaning is per line, so cleaning a long-enough prefix gives exactly the
    # same first `limit` characters as cleaning the whole document -- and a
    # multi-megabyte document costs several copies of itself in transient
    # memory. Fall back to the full text if the prefix collapsed below `limit`
    # (a document that is mostly whitespace).
    cleaned = clean_text(raw if len(raw) <= 2 * limit else raw[:2 * limit],
                         cfg.unicode_form, cfg.max_consecutive_newlines)
    if len(raw) > 2 * limit and len(cleaned) < limit:
        cleaned = clean_text(raw, cfg.unicode_form, cfg.max_consecutive_newlines)
    if not cleaned:
        return None, "empty"
    # cap first: a document is only ever its first max_tokens tokens
    text, n_tokens, truncated = cap_to_max_tokens(
        enc, cleaned if len(cleaned) <= limit else cleaned[:limit], cfg.max_tokens)
    if len(cleaned) > limit:
        truncated = True
    if n_tokens < cfg.min_tokens:
        return None, "under_min_tokens"
    return {
        "doc_id": rec["doc_id"],
        "subject": rec["subject"],
        "split": rec["split"],
        "source": rec["source"],
        "line": rec["line"],
        "n_tokens": n_tokens,
        "truncated": truncated,
        "sha256": text_sha256(text),
        "text": text,
    }, None


# --------------------------------------------------------------------------
# pass A
# --------------------------------------------------------------------------
def _pass_a(cfg: DataConfig, enc) -> Dict[str, Dict[str, Dict[str, int]]]:
    """Clean, cap, exact-dedup. Fixed visit order => deterministic survivors."""
    seen: Dict[str, str] = {}          # sha256 -> split that claimed it first
    log: Dict[str, Dict[str, Dict[str, int]]] = {"train": {}, "heldout": {}}

    for split in ("train", "heldout"):
        for subject in cfg.subjects_for(split):
            slug = cfg.slug(subject)
            counts = _empty_counts()
            src = cfg.raw_dir / split / f"{slug}.jsonl.gz"
            out_path = (cfg.train_dir / f"{slug}.jsonl.gz" if split == "train"
                        else cfg.work_dir / "heldout_clean" / f"{slug}.jsonl.gz")
            with open_write(out_path) as fh:
                for rec in read_jsonl(src):
                    counts["docs_in"] += 1
                    cleaned, reason = clean_record(enc, rec, cfg)
                    if reason:
                        counts[f"dropped_{reason}"] += 1
                        continue
                    owner = seen.get(cleaned["sha256"])
                    if owner is not None:
                        key = ("exact_dup_same_split" if owner == split
                               else "exact_dup_cross_split")
                        counts[f"dropped_{key}"] += 1
                        continue
                    seen[cleaned["sha256"]] = split
                    fh.write(dumps_record(cleaned))
                    counts["docs_kept"] += 1
                    counts["tokens_kept"] += cleaned["n_tokens"]
                    counts["docs_truncated"] += int(cleaned["truncated"])
            log[split][subject] = counts
            print(f"[dedup] A {split:8s} {subject:20s} in={counts['docs_in']:>7,} "
                  f"kept={counts['docs_kept']:>7,} "
                  f"tokens={counts['tokens_kept']:>12,} "
                  f"dropped: empty={counts['dropped_empty']} "
                  f"short={counts['dropped_under_min_tokens']} "
                  f"dup_same={counts['dropped_exact_dup_same_split']} "
                  f"dup_cross={counts['dropped_exact_dup_cross_split']}", flush=True)
    return log


# --------------------------------------------------------------------------
# pass B
# --------------------------------------------------------------------------
def _train_ngram_index(cfg: DataConfig, enc, subject: str) -> np.ndarray:
    """Sorted unique 13-gram hashes of one subject's training documents."""
    slug = cfg.slug(subject)
    path = cfg.train_dir / f"{slug}.jsonl.gz"
    # The index is built as one merged base plus a pending list. Merging only
    # when the *pending* side crosses the threshold keeps the number of sorts
    # at total/MERGE_AT; merging on total size instead re-sorts the whole base
    # on every batch, which is quadratic (9 minutes per subject, measured).
    MERGE_AT = 16_000_000
    base = np.empty(0, dtype=np.uint64)
    pending: List[np.ndarray] = []
    pending_size = 0
    batch: List[str] = []

    def merge() -> None:
        nonlocal base, pending_size
        if not pending:
            return
        parts = ([base] if base.size else []) + pending
        base = np.unique(np.concatenate(parts))
        pending.clear()
        pending_size = 0

    def flush() -> None:
        nonlocal pending_size
        if not batch:
            return
        for toks in enc.encode_ordinary_batch(batch, num_threads=8):
            h = ngram_hashes(toks, cfg.ngram_n)
            if h.size:
                u = np.unique(h)
                pending.append(u)
                pending_size += u.size
        batch.clear()
        if pending_size > MERGE_AT:
            merge()

    for rec in read_jsonl(path):
        batch.append(rec["text"])
        if len(batch) >= 256:
            flush()
    flush()
    merge()
    return base


def _pass_b(cfg: DataConfig, enc, log: Dict[str, Any]) -> Dict[str, Any]:
    """Drop held-out documents that overlap their subject's training text."""
    out: Dict[str, Any] = {}
    for subject in cfg.all_subjects:
        slug = cfg.slug(subject)
        t0 = time.time()
        index = _train_ngram_index(cfg, enc, subject)
        src = cfg.work_dir / "heldout_clean" / f"{slug}.jsonl.gz"
        dst = cfg.heldout_pool_dir / f"{slug}.jsonl.gz"
        n_found = n_total = 0
        kept = dropped = kept_tokens = 0
        per_doc_rates: List[float] = []
        batch: List[Dict[str, Any]] = []

        with open_write(dst) as fh:
            def flush() -> None:
                nonlocal n_found, n_total, kept, dropped, kept_tokens
                if not batch:
                    return
                enc_batch = enc.encode_ordinary_batch(
                    [r["text"] for r in batch], num_threads=8)
                for rec, toks in zip(batch, enc_batch):
                    h = ngram_hashes(toks, cfg.ngram_n)
                    found, total = overlap_rate(h, index)
                    n_found += found
                    n_total += total
                    rate = found / total if total else 0.0
                    per_doc_rates.append(rate)
                    if rate > cfg.ngram_drop_threshold:
                        dropped += 1
                        continue
                    rec = dict(rec, ngram_overlap=round(rate, 6))
                    fh.write(dumps_record(rec))
                    kept += 1
                    kept_tokens += rec["n_tokens"]
                batch.clear()

            for rec in read_jsonl(src):
                batch.append(rec)
                if len(batch) >= 256:
                    flush()
            flush()

        log["heldout"][subject]["dropped_ngram_overlap"] = dropped
        log["heldout"][subject]["docs_kept"] = kept
        log["heldout"][subject]["tokens_kept"] = kept_tokens
        rates = np.array(per_doc_rates) if per_doc_rates else np.zeros(1)
        out[subject] = {
            "train_ngrams_unique": int(index.size),
            "heldout_ngrams_total": n_total,
            "heldout_ngrams_in_train": n_found,
            "aggregate_overlap_rate": round(n_found / n_total, 6) if n_total else 0.0,
            "mean_per_doc_overlap_rate": round(float(rates.mean()), 6),
            "median_per_doc_overlap_rate": round(float(np.median(rates)), 6),
            "max_per_doc_overlap_rate": round(float(rates.max()), 6),
            "docs_dropped": dropped,
            "docs_kept": kept,
            "tokens_kept": kept_tokens,
            "seconds": round(time.time() - t0, 1),
        }
        print(f"[dedup] B {subject:20s} train_13grams={index.size:>12,} "
              f"overlap={out[subject]['aggregate_overlap_rate']:.4%} "
              f"dropped={dropped:>5,} kept={kept:>6,} "
              f"tokens={kept_tokens:>10,} ({out[subject]['seconds']}s)", flush=True)
    return out


def run(cfg: DataConfig) -> Dict[str, Any]:
    enc = get_encoder(cfg.tokenizer_name, cfg.vocab_size)
    t0 = time.time()
    log = _pass_a(cfg, enc)
    ngram = _pass_b(cfg, enc, log)
    out = {
        "stage": "dedup",
        "config_fingerprint": cfg.fingerprint(),
        "small": cfg.small,
        "max_tokens": cfg.max_tokens,
        "min_tokens": cfg.min_tokens,
        "ngram_n": cfg.ngram_n,
        "ngram_drop_threshold": cfg.ngram_drop_threshold,
        "seconds": round(time.time() - t0, 1),
        "per_subject": log,
        "ngram_overlap": ngram,
        "train_tokens_total": sum(v["tokens_kept"] for v in log["train"].values()),
        "train_target_per_subject": cfg.train_tokens_per_subject,
        "train_subjects_below_target": [
            s for s, v in log["train"].items()
            if v["tokens_kept"] < cfg.train_tokens_per_subject],
    }
    write_json(cfg.reports_dir / "dedup_log.json", out)
    return out


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--config", required=True)
    ap.add_argument("--small", action="store_true")
    args = ap.parse_args(argv)
    cfg = load_config(args.config, small=args.small)
    out = run(cfg)
    print(f"\n[dedup] train tokens total {out['train_tokens_total']:,} "
          f"({out['seconds']}s)")
    if out["train_subjects_below_target"]:
        print(f"[dedup] BELOW TARGET: {out['train_subjects_below_target']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
