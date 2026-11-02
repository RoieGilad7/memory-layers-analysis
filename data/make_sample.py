"""Package the `--small` build as `data/v1_sample/` for the metrics owner.

    python -m data.build --config configs/data/v1.yaml --stage pile --small
    python -m data.make_sample --config configs/data/v1.yaml

Copies the small build verbatim (minus stage scratch) and writes a README that
says what each file is. The sample is real Pile text from the pinned revision,
built by exactly the same code as the full set -- only the token targets are 1%.
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path
from typing import List, Optional

from data.common import ROOT, load_config

SKIP_DIRS = {"_work"}


def write_readme(dst: Path, cfg, manifest: dict) -> None:
    subs = manifest["subjects"]
    halves = cfg.heldout_halves
    rows = "\n".join(
        f"| `{v['slug']}` | {s} | {v['train']['docs']:,} | {v['train']['tokens']:,} | "
        + " | ".join(f"{v['heldout']['halves'][h]['docs']:,} / "
                     f"{v['heldout']['halves'][h]['tokens']:,}" for h in halves)
        + f" | {v['ngram_overlap_rate']:.3%} |"
        for s, v in subs.items())
    (dst / "README.md").write_text(f"""# `data/v1_sample/` — the 1% sample of dataset v1

Real text from the Pile, built by the same code as the full set with every token
target scaled to **1%** (`--small`). Here so the metrics code can be written
against real records before the full build lands. **Not a training set.**

Rebuild it with:

```bash
python -m data.build --config configs/data/v1.yaml --stage pile --small
python -m data.make_sample --config configs/data/v1.yaml
```

Both commands are deterministic: rebuilding gives byte-identical files.

| | |
|---|---|
| Source | `{manifest['dataset']}` |
| Pinned revision | `{manifest['revision']}` |
| Data seed | `{manifest['seed']}` |
| Config fingerprint | `{manifest['config_fingerprint'][:16]}` |
| Tokenizer | GPT-2 (`tiktoken`), vocab {manifest['tokenizer']['vocab_size']:,} |
| Document cap / floor | {manifest['document']['max_tokens']:,} / {manifest['document']['min_tokens']} tokens |
| Scale vs. the full set | {cfg.scale:.0%} of every token target |

## What is in here

| path | what it is |
|---|---|
| `manifest.json` | the whole build in one object — counts, targets, overlap rates, problems. **Read this, not the directory listing.** |
| `raw/<split>/<slug>.jsonl.gz` | the archived source text, untouched: `doc_id, subject, split, source, line, text` |
| `train/<slug>.jsonl.gz` | cleaned, capped at 4,096 tokens, deduplicated **training** documents |
| `heldout_pool/<slug>.jsonl.gz` | the same for held-out documents, before the label/test cut, plus `ngram_overlap` |
| `heldout/label/<slug>.jsonl.gz` | the **labeling** half |
| `heldout/test/<slug>.jsonl.gz` | the **test** half — disjoint from `label` by whole document |
| `reports/extract_manifest.json` | what was streamed: files, lines, bytes, per-subject collection |
| `reports/dedup_log.json` | documents dropped per reason per subject + the 13-gram overlap numbers |
| `reports/split_report.json` | half sizes, the document minimum, anything below target |

Document and index schemas: **`docs/interfaces.md` §1** (DRAFT — review it).

## Contents of this sample

| slug | subject | train docs | train tokens | {" | ".join(h + " docs / tokens" for h in halves)} | 13-gram overlap |
|---|---|---:|---:|{"---:|" * len(halves)}---:|
{rows}

`USPTO Backgrounds` is the **phase-2 subject**: held-out only, never in
training, which is why its training row is empty and its overlap is 0.

## Reading a file

```python
import gzip, json
with gzip.open("data/v1_sample/heldout/label/pile_cc.jsonl.gz", "rt", encoding="utf-8") as fh:
    docs = [json.loads(line) for line in fh]
print(docs[0]["doc_id"], docs[0]["n_tokens"], docs[0]["subject"], docs[0]["half"])
```

## Three caveats about the sample specifically

1. **The halves do not all reach their token budget.** At 1% scale a subject's
   held-out pool is only 20–130 documents, and the label/test assignment is a
   hash, so one half can land short. `manifest.json -> problems` names them. At
   full scale each pool is thousands of documents and both halves fill.
2. **The 500-documents-per-half minimum is scaled to 5 here**, for the same
   reason. The full build enforces 500.
3. **Exact-duplicate counts are near zero** at this size. They are not zero in
   the full build.
""", encoding="utf-8")


def run(cfg, dst: Path) -> Path:
    if not (cfg.root / "manifest.json").exists():
        raise SystemExit(f"no small build at {cfg.root} -- run "
                         "`python -m data.build --config ... --stage pile --small` first")
    manifest = json.loads((cfg.root / "manifest.json").read_text())
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(cfg.root, dst,
                    ignore=shutil.ignore_patterns(*SKIP_DIRS, "extract_state.json"))
    write_readme(dst, cfg, manifest)
    return dst


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--config", required=True)
    ap.add_argument("--out", default="data/v1_sample")
    args = ap.parse_args(argv)
    cfg = load_config(args.config, small=True)
    dst = run(cfg, ROOT / args.out)
    total = sum(p.stat().st_size for p in dst.rglob("*") if p.is_file())
    n = sum(1 for p in dst.rglob("*") if p.is_file())
    print(f"[sample] {dst} -- {n} files, {total / 1e6:.1f} MB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
