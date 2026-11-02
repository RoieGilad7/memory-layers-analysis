"""One entry point for the dataset build.

    python -m data.build --config configs/data/v1.yaml --stage pile
    python -m data.build --config configs/data/v1.yaml --stage pile --small

`--stage pile` runs extract -> dedup -> split in order. `--small` scales every
token target by `small.scale` (1%) and redirects the output root, which is what
the fast end-to-end test and the `data/v1_sample/` bundle use.

Later prompts add `--stage bio`, `--stage tokenize` and `--stage all`; they are
declared here so the CLI does not change under the metrics owner.
"""
from __future__ import annotations

import argparse
import sys
import time
from typing import Any, Dict, List, Optional

from data import dedup, pile_extract, split
from data.common import DataConfig, free_disk_gb, load_config, write_json

STAGES = ("pile", "extract", "dedup", "split", "bio", "tokenize", "all")
MIN_FREE_DISK_GB = 20.0


def _dir_bytes(path) -> int:
    if not path.exists():
        return 0
    return sum(p.stat().st_size for p in path.rglob("*") if p.is_file())


def _check_disk(where: str) -> None:
    free = free_disk_gb()
    if free < MIN_FREE_DISK_GB:
        raise RuntimeError(
            f"free disk {free:.1f} GB < {MIN_FREE_DISK_GB} GB after {where} "
            "-- stopping. Re-run the same command to resume.")
    print(f"[build] free disk after {where}: {free:.1f} GB", flush=True)


def run_pile(cfg: DataConfig) -> Dict[str, Any]:
    t0 = time.time()
    print(f"[build] root={cfg.root}  small={cfg.small}  "
          f"fingerprint={cfg.fingerprint()[:16]}", flush=True)
    print(f"[build] train target {cfg.train_tokens_per_subject:,} tok/subject "
          f"(collect {cfg.collect_train_tokens_per_subject:,}), held-out "
          f"{cfg.heldout_tokens_per_subject:,} tok/subject "
          f"({cfg.heldout_tokens_per_half:,} per half, "
          f"min {cfg.heldout_min_docs_per_half} docs)", flush=True)
    _check_disk("start")

    extract_m = pile_extract.run(cfg)
    _check_disk("extract")
    dedup_m = dedup.run(cfg)
    _check_disk("dedup")
    split_m = split.run(cfg)

    manifest = {
        "stage": "pile",
        "version": cfg.version,
        "small": cfg.small,
        "config_fingerprint": cfg.fingerprint(),
        "seed": cfg.seed,
        "dataset": cfg.dataset,
        "revision": cfg.revision,
        "tokenizer": {"name": cfg.tokenizer_name, "vocab_size": cfg.vocab_size},
        "document": {"max_tokens": cfg.max_tokens, "min_tokens": cfg.min_tokens},
        "seconds": round(time.time() - t0, 1),
        "disk_bytes": {
            "raw": _dir_bytes(cfg.raw_dir),
            "train": _dir_bytes(cfg.train_dir),
            "heldout_pool": _dir_bytes(cfg.heldout_pool_dir),
            "heldout": _dir_bytes(cfg.heldout_dir),
            "work": _dir_bytes(cfg.work_dir),
            "total": _dir_bytes(cfg.root),
        },
        "bytes_downloaded": sum(v["bytes_downloaded"]
                                for v in extract_m["splits"].values()),
        "free_disk_gb": round(free_disk_gb(), 1),
        "subjects": {},
    }
    for subject in cfg.all_subjects:
        tr = dedup_m["per_subject"]["train"].get(subject)
        ho = dedup_m["per_subject"]["heldout"][subject]
        sp = split_m["per_subject"][subject]
        manifest["subjects"][subject] = {
            "slug": cfg.slug(subject),
            "in_training": subject in cfg.train_subjects,
            "train": {
                "docs_collected": extract_m["splits"]["train"]["subjects"]
                                  .get(subject, {}).get("docs", 0),
                "docs": tr["docs_kept"] if tr else 0,
                "tokens": tr["tokens_kept"] if tr else 0,
                "target_tokens": cfg.train_tokens_per_subject if tr else 0,
            },
            "heldout": {
                "docs_collected": extract_m["splits"]["heldout"]["subjects"][subject]["docs"],
                "pool_docs": ho["docs_kept"],
                "pool_tokens": ho["tokens_kept"],
                "halves": {h: sp["halves"][h] for h in cfg.heldout_halves},
            },
            "ngram_overlap_rate": dedup_m["ngram_overlap"][subject][
                "aggregate_overlap_rate"],
            "heldout_docs_dropped_by_ngram_rule":
                dedup_m["ngram_overlap"][subject]["docs_dropped"],
        }
    manifest["train_tokens_total"] = sum(
        v["train"]["tokens"] for v in manifest["subjects"].values())
    manifest["problems"] = {
        "train_subjects_below_target": dedup_m["train_subjects_below_target"],
        "heldout_below_min_docs": split_m["subjects_below_min_docs"],
        "heldout_below_target_tokens": split_m["subjects_below_target_tokens"],
        "fallback_files_used": {
            s: v["fallback_files_used"] for s, v in extract_m["splits"].items()},
    }
    write_json(cfg.root / "manifest.json", manifest)
    print_summary(cfg, manifest)
    return manifest


def print_summary(cfg: DataConfig, m: Dict[str, Any]) -> None:
    halves = cfg.heldout_halves
    head = (f"{'subject':22s} {'train docs':>11s} {'train tok':>12s} "
            f"{'pool docs':>10s} "
            + " ".join(f"{h + ' docs':>10s} {h + ' tok':>10s}" for h in halves)
            + f" {'13g ovl':>8s} {'ngram drop':>10s}")
    print("\n" + head)
    print("-" * len(head))
    for subject, v in m["subjects"].items():
        row = (f"{subject:22s} {v['train']['docs']:>11,} {v['train']['tokens']:>12,} "
               f"{v['heldout']['pool_docs']:>10,} ")
        row += " ".join(f"{v['heldout']['halves'][h]['docs']:>10,} "
                        f"{v['heldout']['halves'][h]['tokens']:>10,}" for h in halves)
        row += (f" {v['ngram_overlap_rate']:>7.3%} "
                f"{v['heldout_docs_dropped_by_ngram_rule']:>10,}")
        print(row)
    print("-" * len(head))
    print(f"train tokens total: {m['train_tokens_total']:,} "
          f"(target {cfg.train_tokens_per_subject * len(cfg.train_subjects):,} "
          f"= 5 x {cfg.train_tokens_per_subject:,}; "
          f"+{cfg.bio_share:.0%} biographies later = "
          f"{cfg.total_train_tokens:,})")
    print(f"downloaded {m['bytes_downloaded'] / 1e9:.2f} GB, "
          f"output {m['disk_bytes']['total'] / 1e6:.1f} MB, "
          f"{m['seconds'] / 60:.1f} min, free disk {m['free_disk_gb']:.1f} GB")
    for k, v in m["problems"].items():
        if v and v != {"train": [], "heldout": []}:
            print(f"PROBLEM {k}: {v}")


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--config", required=True)
    ap.add_argument("--stage", required=True, choices=STAGES)
    ap.add_argument("--small", action="store_true",
                    help="run on small.scale (1%%) of every token target")
    args = ap.parse_args(argv)
    cfg = load_config(args.config, small=args.small)

    if args.stage in ("pile", "all"):
        if args.stage == "all":
            print("[build] --stage all: only the pile stage exists in this step; "
                  "bio/tokenize arrive in later prompts.")
        run_pile(cfg)
    elif args.stage == "extract":
        pile_extract.run(cfg)
    elif args.stage == "dedup":
        dedup.run(cfg)
    elif args.stage == "split":
        split.run(cfg)
    else:
        print(f"[build] stage {args.stage!r} is not implemented yet "
              "(later prompt); nothing done.")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
