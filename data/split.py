"""Stage 3 -- cut the held-out pool into a labeling half and a test half.

Each held-out document is assigned to "label" or "test" by a seeded hash of its
document id (`blake2b(f"{seed}:{doc_id}")`), so the assignment is stable across
rebuilds, independent of document order, and splits by *whole documents* -- no
document ever contributes to both halves. Each half is then trimmed to
`targets.heldout_tokens_per_half` tokens per subject by walking the documents in
source order and stopping at the first document that reaches the budget.

Checks the per-half document minimum and reports any subject below it rather
than failing: a short subject is a finding for the report, not a crash.
"""
from __future__ import annotations

import argparse
import sys
import time
from typing import Any, Dict, List, Optional

from data.common import (DataConfig, dumps_record, heldout_half, load_config,
                         open_write, read_jsonl, write_json)


def run(cfg: DataConfig) -> Dict[str, Any]:
    t0 = time.time()
    halves = cfg.heldout_halves
    per_subject: Dict[str, Any] = {}

    for subject in cfg.all_subjects:
        slug = cfg.slug(subject)
        pool = list(read_jsonl(cfg.heldout_pool_dir / f"{slug}.jsonl.gz"))
        pool.sort(key=lambda r: (r["source"], r["line"]))

        assigned: Dict[str, List[Dict[str, Any]]] = {h: [] for h in halves}
        for rec in pool:
            assigned[heldout_half(rec["doc_id"], cfg.seed, halves)].append(rec)

        stats: Dict[str, Any] = {}
        for half in halves:
            kept, tokens = [], 0
            for rec in assigned[half]:
                if tokens >= cfg.heldout_tokens_per_half:
                    break
                kept.append(rec)
                tokens += rec["n_tokens"]
            out = cfg.heldout_dir / half / f"{slug}.jsonl.gz"
            with open_write(out) as fh:
                for rec in kept:
                    fh.write(dumps_record(dict(rec, half=half)))
            stats[half] = {
                "docs_available": len(assigned[half]),
                "tokens_available": sum(r["n_tokens"] for r in assigned[half]),
                "docs": len(kept),
                "tokens": tokens,
                "target_tokens": cfg.heldout_tokens_per_half,
                "min_docs": cfg.heldout_min_docs_per_half,
                "below_min_docs": len(kept) < cfg.heldout_min_docs_per_half,
                "below_target_tokens": tokens < cfg.heldout_tokens_per_half,
                "path": str(out.relative_to(cfg.root)),
            }
        ids = {h: {r["doc_id"] for r in assigned[h]} for h in halves}
        overlap = set.intersection(*ids.values()) if len(ids) > 1 else set()
        per_subject[subject] = {
            "pool_docs": len(pool),
            "pool_tokens": sum(r["n_tokens"] for r in pool),
            "halves": stats,
            "halves_disjoint": not overlap,
        }
        line = " | ".join(
            f"{h}: {stats[h]['docs']:>6,} docs {stats[h]['tokens']:>9,} tok"
            for h in halves)
        flags = [f"{h}:BELOW_MIN_DOCS" for h in halves if stats[h]["below_min_docs"]]
        flags += [f"{h}:BELOW_TARGET" for h in halves
                  if stats[h]["below_target_tokens"]]
        print(f"[split] {subject:20s} pool={len(pool):>6,} {line}"
              + ("  <<< " + ",".join(flags) if flags else ""), flush=True)

    out = {
        "stage": "split",
        "config_fingerprint": cfg.fingerprint(),
        "small": cfg.small,
        "seed": cfg.seed,
        "halves": halves,
        "tokens_per_half": cfg.heldout_tokens_per_half,
        "min_docs_per_half": cfg.heldout_min_docs_per_half,
        "seconds": round(time.time() - t0, 1),
        "per_subject": per_subject,
        "subjects_below_min_docs": sorted(
            f"{s}/{h}" for s, v in per_subject.items() for h in halves
            if v["halves"][h]["below_min_docs"]),
        "subjects_below_target_tokens": sorted(
            f"{s}/{h}" for s, v in per_subject.items() for h in halves
            if v["halves"][h]["below_target_tokens"]),
    }
    write_json(cfg.reports_dir / "split_report.json", out)
    return out


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--config", required=True)
    ap.add_argument("--small", action="store_true")
    args = ap.parse_args(argv)
    cfg = load_config(args.config, small=args.small)
    out = run(cfg)
    if out["subjects_below_min_docs"]:
        print(f"\n[split] BELOW the {out['min_docs_per_half']}-document minimum: "
              f"{out['subjects_below_min_docs']}")
    if out["subjects_below_target_tokens"]:
        print(f"[split] below the {out['tokens_per_half']:,}-token target: "
              f"{out['subjects_below_target_tokens']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
