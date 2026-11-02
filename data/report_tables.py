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
    ap.add_argument("--stage", choices=["pile", "bios"], default="pile")
    args = ap.parse_args(argv)
    cfg = load_config(args.config, small=args.small)
    if args.stage == "bios":
        return bios_tables(cfg)

    man = json.loads((cfg.reports_dir / "pile_manifest.json").read_text())
    ext = json.loads((cfg.reports_dir / "extract_manifest.json").read_text())
    ded = json.loads((cfg.reports_dir / "dedup_log.json").read_text())
    spl = json.loads((cfg.reports_dir / "split_report.json").read_text())
    halves = cfg.heldout_halves

    print("### 4.1 The run\n")
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
        ["runtime, total", f"{man['seconds'] / 60:.1f} min"],
        ["runtime, extract / dedup / split",
         f"{ext['seconds']:.0f} s / {ded['seconds']:.0f} s / {spl['seconds']:.0f} s"],
        ["output on disk", f"{man['disk_bytes']['total'] / 1e6:.0f} MB"],
    ], ["", ""], "ll"))

    print("\n### 4.2 Training subjects: collected -> cleaned -> deduped\n")
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

    print("\n### 4.3 Held-out: collected -> cleaned -> deduped -> halves\n")
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

    print("\n### 4.4 Dedup log — documents dropped per reason per subject\n")
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

    print("\n### 4.5 13-gram overlap, held-out vs. training text of the same subject\n")
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

    print("\n### 4.6 Disk\n")
    rows = [[k, f"{v / 1e6:.1f} MB"] for k, v in sorted(man["disk_bytes"].items())]
    rows.append(["compressed downloaded", f"{man['bytes_downloaded'] / 1e9:.2f} GB"])
    rows.append(["free disk after the build", f"{man['free_disk_gb']:.1f} GB"])
    print(table(rows, ["", ""], "lr"))

    print("\n### 4.7 Problems reported by the build\n")
    print("```json")
    print(json.dumps(man["problems"], indent=2))
    print("```")
    return 0



# ---------------------------------------------------------------------------
# biographies (data prompt 2)
# ---------------------------------------------------------------------------
def bios_tables(cfg) -> int:
    import data.bios_data as bd
    man = json.loads((cfg.bios_dir / "manifest.json").read_text())
    vals = json.loads((cfg.bios_dir / "attribute_values.json").read_text())
    p, e, b = man["people"], man["exposures"], man["biographies"]

    print("### 2.1 The run\n")
    print(table([
        ["config fingerprint (bios scope)", f"`{man['config_fingerprint'][:16]}`"],
        ["data seed", str(man["seed"])],
        ["people", f"{p['n_people']:,}"],
        ["facts.jsonl rows", f"{man['facts']['rows']:,}"],
        ["biography rows", f"{b['rows']:,}"],
        ["runtime", f"{man['seconds']:.0f} s"],
    ], ["", ""], "ll"))

    print("\n### 2.2 People by split, tier and gender\n")
    rows = []
    tiers = [t["name"] for t in cfg.bio_tiers] + [cfg.bio_control_tier]
    exposures = {t["name"]: t["exposures"] for t in cfg.bio_tiers}
    exposures[cfg.bio_control_tier] = 0
    for t in tiers:
        f = p["by_tier_gender"].get(f"{t}/female", 0)
        m = p["by_tier_gender"].get(f"{t}/male", 0)
        split = "control" if t == cfg.bio_control_tier else "train"
        rows.append([f"`{t}`", split, _f(exposures[t]), _f(f + m), _f(f), _f(m),
                     _f(exposures[t] * (f + m))])
    rows.append(["**total**", "", "", f"**{p['n_people']:,}**",
                 f"**{p['by_gender']['female']:,}**",
                 f"**{p['by_gender']['male']:,}**",
                 f"**{e['total_copies']:,}**"])
    print(table(rows, ["tier", "split", "exposures each", "people", "female",
                       "male", "biography copies"], "llrrrrr"))

    print("\n### 2.3 Value lists\n")
    rows = []
    for attr in cfg.bio_attributes:
        v = man["values"][attr]
        t = man["value_tokens"][attr]
        unique = ("first token" if t["first_token_unique"]
                  else ("first 2 tokens" if t["first_two_tokens_unique"] else "**NO**"))
        rows.append([f"`{attr}`", _f(v["candidates"]),
                     _f(v["dropped_near_duplicate"]), _f(v["dropped_prefix_clash"]),
                     _f(v["dropped_over_target"]), f"**{v['final']:,}**",
                     _f(v["target"]), str(t["distinct_first_tokens"]), unique,
                     str(t["value_tokens_mean"])])
    print(table(rows, ["attribute", "candidates", "dropped near-dup",
                       "dropped prefix clash", "trimmed to target", "final",
                       "target", "distinct first tokens", "unique on",
                       "mean tokens/value"], "lrrrrrrrlr"))

    print("\n### 2.4 Templates\n")
    rows = [[f"`{a}`", str(man["templates_per_attribute"][a]["train"]),
             str(man["templates_per_attribute"][a]["held_out"]),
             str(len({bd.pre_value_context(t) for t in bd.TRAIN_TEMPLATES[a]})),
             str(len({bd.pre_value_context(t) for t in bd.HELDOUT_TEMPLATES[a]}))]
            for a in cfg.bio_attributes]
    print(table(rows, ["attribute", "training templates", "held-out templates",
                       "distinct pre-value contexts (train)", "(held-out)"],
                "lrrrr"))

    print("\n### 2.5 facts.jsonl rows\n")
    print(table([[f"`{k}`", _f(v)] for k, v in man["facts"]["by_role"].items()]
                + [["**total**", f"**{man['facts']['rows']:,}**"]],
                ["role", "rows"], "lr"))

    print("\n### 2.6 Token budget\n")
    print(table([
        ["biography tokens, mean", str(b["tokens_mean"])],
        ["biography tokens, range", f"{b['tokens_min']}-{b['tokens_max']}"],
        ["trained-people mean", str(b["train_tokens_mean"])],
        ["biography copies at the tier targets", f"{e['total_copies']:,}"],
        ["**implied biography tokens**", f"**{e['implied_tokens']:,}**"],
        ["share of the training budget",
         f"**{e['share_of_train_budget']:.2%}** of {e['train_budget']:,} "
         f"(target {e['bio_share_target']:.0%})"],
    ], ["", ""], "lr"))

    print("\n### 2.7 The Pile name check\n")
    nc = man["name_check"]
    print(table([
        ["files scanned", str(len(nc["files"]))],
        ["documents scanned", f"{nc['documents_scanned']:,}"],
        ["characters scanned", f"{nc['characters_scanned'] / 1e6:,.0f} M"],
        ["candidate names tested", f"{nc['candidates_tested']:,}"],
        ["case sensitive", str(nc["case_sensitive"])],
        ["candidate names found in the Pile", f"**{nc['n_names_found']}**"],
        ["names actually rejected (inside the per-gender cut-off)",
         f"**{p['names_rejected_by_pile_check']}**"],
    ], ["", ""], "lr"))
    print("\nFirst 12 rejected names: "
          + ", ".join(f"`{n}`" for n in p["rejected_names"][:12]) + ".")
    return 0

if __name__ == "__main__":
    sys.exit(main())
