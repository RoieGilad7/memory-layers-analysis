"""Markdown tables for reports/data1_pile_report.md, read out of the build's
own JSON. Nothing in the report is retyped by hand.

    python -m data.report_tables --config configs/data/v1.yaml [--small]
"""
from __future__ import annotations

import argparse
import json
import sys
from typing import Any, Dict, List, Optional

from data.common import load_config


def _f(n: Any) -> str:
    return f"{n:,}" if isinstance(n, int) else str(n)


def table(rows: List[List[str]], head: List[str], align: str = "") -> str:
    align = align or "l" * len(head)
    sep = "|" + "|".join({"l": "---", "r": "---:", "c": ":---:"}[a] for a in align) + "|"
    out = ["|" + "|".join(h or " " for h in head) + "|", sep]
    out += ["|" + "|".join(r) + "|" for r in rows]
    return "\n".join(out)


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--config", required=True)
    ap.add_argument("--small", action="store_true")
    args = ap.parse_args(argv)
    cfg = load_config(args.config, small=args.small)

    man = json.loads((cfg.root / "manifest.json").read_text())
    ext = json.loads((cfg.reports_dir / "extract_manifest.json").read_text())
    ded = json.loads((cfg.reports_dir / "dedup_log.json").read_text())
    spl = json.loads((cfg.reports_dir / "split_report.json").read_text())
    halves = cfg.heldout_halves

    print("### Source\n")
    print(table([
        ["dataset", f"`{man['dataset']}`"],
        ["pinned revision", f"`{man['revision']}`"],
        ["training shard(s)", ", ".join(f"`{f}`" for f in ext["splits"]["train"]["files_used"])],
        ["held-out shard(s)", ", ".join(f"`{f}`" for f in ext["splits"]["heldout"]["files_used"])],
        ["fallback shards used", ", ".join(
            f"{k}: {v or 'none'}"
            for k, v in sorted(man["problems"]["fallback_files_used"].items()))],
        ["data seed", str(man["seed"])],
        ["config fingerprint", f"`{man['config_fingerprint'][:16]}`"],
        ["tokenizer", f"GPT-2 (`tiktoken`), vocab {man['tokenizer']['vocab_size']:,}"],
        ["lines read, train / held-out",
         f"{ext['splits']['train']['lines_read']:,} / {ext['splits']['heldout']['lines_read']:,}"],
        ["compressed bytes downloaded", f"{man['bytes_downloaded'] / 1e9:.2f} GB"],
        ["runtime", f"{man['seconds'] / 60:.1f} min"],
        ["output on disk", f"{man['disk_bytes']['total'] / 1e6:.0f} MB"],
    ], ["", ""], "ll"))

    print("\n### 1. Training subjects: collected -> cleaned -> deduped\n")
    rows = []
    for s in cfg.train_subjects:
        e = ext["splits"]["train"]["subjects"][s]
        d = ded["per_subject"]["train"][s]
        rows.append([f"`{s}`", _f(e["docs"]), _f(e["tokens"]), _f(d["docs_in"]),
                     _f(d["dropped_empty"] + d["dropped_under_min_tokens"]),
                     _f(d["dropped_exact_dup_same_split"]
                        + d["dropped_exact_dup_cross_split"]),
                     _f(d["docs_kept"]), f"**{d['tokens_kept']:,}**",
                     f"{d['tokens_kept'] / cfg.train_tokens_per_subject:.2f}x",
                     _f(d["docs_truncated"])])
    print(table(rows, ["subject", "docs collected", "tokens collected", "docs in",
                       "dropped short/empty", "dropped dup", "docs kept",
                       "tokens kept", "vs target", "capped at 4096"],
                "lrrrrrrrrr"))
    print(f"\nTraining target per subject: **{cfg.train_tokens_per_subject:,}** "
          f"tokens (18% of {cfg.total_train_tokens:,}); collected "
          f"{cfg.collect_train_tokens_per_subject:,} (+{cfg.collect_slack:.0%} slack). "
          f"Total training tokens from the Pile: **{man['train_tokens_total']:,}**.")

    print("\n### 2. Held-out: collected -> cleaned -> deduped -> halves\n")
    rows = []
    for s in cfg.all_subjects:
        e = ext["splits"]["heldout"]["subjects"][s]
        d = ded["per_subject"]["heldout"][s]
        sp = spl["per_subject"][s]
        row = [f"`{s}`", _f(e["docs"]), _f(e["tokens"]), _f(d["docs_kept"]),
               _f(d["tokens_kept"])]
        for h in halves:
            row += [_f(sp["halves"][h]["docs"]), _f(sp["halves"][h]["tokens"])]
        rows.append(row)
    head = ["subject", "docs collected", "tokens collected", "pool docs",
            "pool tokens"]
    for h in halves:
        head += [f"{h} docs", f"{h} tokens"]
    print(table(rows, head, "l" + "r" * (len(head) - 1)))
    print(f"\nTarget: **{cfg.heldout_tokens_per_subject:,}** tokens per subject, "
          f"**{cfg.heldout_tokens_per_half:,}** per half, minimum "
          f"**{cfg.heldout_min_docs_per_half}** documents per half.")

    print("\n### 3. Dedup log — documents dropped per reason per subject\n")
    rows = []
    for split in ("train", "heldout"):
        for s, d in ded["per_subject"][split].items():
            rows.append([split, f"`{s}`", _f(d["docs_in"]), _f(d["dropped_empty"]),
                         _f(d["dropped_under_min_tokens"]),
                         _f(d["dropped_exact_dup_same_split"]),
                         _f(d["dropped_exact_dup_cross_split"]),
                         _f(d.get("dropped_ngram_overlap", 0)),
                         _f(d["docs_kept"])])
    print(table(rows, ["split", "subject", "docs in", "empty",
                       f"< {cfg.min_tokens} tokens", "exact dup (same split)",
                       "exact dup (cross split)",
                       f"&gt;{cfg.ngram_drop_threshold:.0%} 13-gram", "kept"],
                "llrrrrrrr"))

    print("\n### 4. 13-gram overlap, held-out vs. training text of the same subject\n")
    rows = []
    for s in cfg.all_subjects:
        o = ded["ngram_overlap"][s]
        rows.append([f"`{s}`", _f(o["train_ngrams_unique"]),
                     _f(o["heldout_ngrams_total"]), _f(o["heldout_ngrams_in_train"]),
                     f"**{o['aggregate_overlap_rate']:.3%}**",
                     f"{o['mean_per_doc_overlap_rate']:.3%}",
                     f"{o['median_per_doc_overlap_rate']:.3%}",
                     f"{o['max_per_doc_overlap_rate']:.1%}",
                     _f(o["docs_dropped"])])
    print(table(rows, ["subject", "unique train 13-grams", "held-out 13-grams",
                       "of those, in train", "aggregate rate", "mean / doc",
                       "median / doc", "max / doc", "docs dropped by the 50% rule"],
                "lrrrrrrrr"))

    print("\n### 5. Disk\n")
    rows = [[k, f"{v / 1e6:.1f} MB"] for k, v in sorted(man["disk_bytes"].items())]
    rows.append(["compressed downloaded", f"{man['bytes_downloaded'] / 1e9:.2f} GB"])
    rows.append(["free disk after the build", f"{man['free_disk_gb']:.1f} GB"])
    print(table(rows, ["", ""], "lr"))

    print("\n### 6. Problems reported by the build\n")
    print("```json")
    print(json.dumps(man["problems"], indent=2))
    print("```")
    return 0


if __name__ == "__main__":
    sys.exit(main())
