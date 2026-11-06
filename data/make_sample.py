"""Package the `--small` build as `data/v1_sample/` for the metrics owner.

    python -m data.build --config configs/data/v1.yaml --stage pile --small
    python -m data.bios  --config configs/data/v1.yaml --small
    python -m data.pack  --config configs/data/v1.yaml --small
    python -m data.manifest --config configs/data/v1.yaml --small
    python -m data.make_sample --config configs/data/v1.yaml

Copies the small build and writes a README saying what each file is and where
1% scale changes the answer. The sample mirrors **what `data.fetch` gives you by
default**, so `raw/` is left out: a rebuild needs the archived source text, and
you cannot rebuild from a sample anyway. Pass `--with-raw` to include it.

The sample is real Pile text and real generated biographies from the pinned
revision, built by exactly the same code as the full set -- only the token
targets are 1%.
"""

from __future__ import annotations

import argparse
import copy
import json
import shutil
import sys
from pathlib import Path
from typing import List, Optional

from data.common import ROOT, load_config

SKIP_DIRS = {"_work"}
# `raw/` is what `data.fetch` skips by default: a rebuild needs it, reading the
# data does not, and you cannot rebuild from a 1% sample anyway.
OPTIONAL_DIRS = {"raw"}


def write_readme(dst: Path, cfg, manifest: dict, with_raw: bool) -> None:
    """`manifest` must be the SAMPLE's manifest, so the sizes describe it."""
    counts = manifest["counts"]
    train = counts.get("train", {})
    bios = counts.get("biographies", {})
    held = counts.get("heldout", {})
    b = manifest["bytes"]
    per = train.get("per_subject", {})
    per_tier = bios.get("per_tier", {})

    subject_rows = "\n".join(
        f"| `{s}` | {per.get(s, {}).get('tokens', 0):,} | "
        f"{per.get(s, {}).get('segments', 0):,} | "
        + " | ".join(
            f"{held.get(h, {}).get('per_subject', {}).get(s, {}).get('documents', 0):,}"
            f" / {held.get(h, {}).get('per_subject', {}).get(s, {}).get('tokens', 0):,}"
            for h in cfg.pack_halves
        )
        + " |"
        for s in cfg.all_subjects
    )
    tier_rows = "\n".join(
        f"| `{t}` | {v['people']:,} | {v['copies']:,} | {v['tokens']:,} |"
        for t, v in sorted(per_tier.items(), key=lambda kv: -kv[1]["copies"])
    )

    (dst / "README.md").write_text(
        f"""# `data/v1_sample/` — the 1% sample of dataset `{manifest['version']}`

Real text from the Pile and real generated biographies, built by the same code
as the full set with every token target scaled to **1%** (`--small`). Here so
the metrics code can be written against real records without the 1.1 GB bundle.
**Not a training set.**

It mirrors what `python -m data.fetch --version v1` gives you by default, so
`raw/` is {"included" if with_raw else "**left out**"} — a rebuild needs the archived
source text and you cannot rebuild from a sample anyway.

Rebuild it with:

```bash
python -m data.build    --config configs/data/v1.yaml --stage pile --small
python -m data.bios     --config configs/data/v1.yaml --small
python -m data.pack     --config configs/data/v1.yaml --small
python -m data.manifest --config configs/data/v1.yaml --small
python -m data.make_sample --config configs/data/v1.yaml
```

Every command is deterministic: rebuilding gives byte-identical files.

| | |
|---|---|
| Source | `{manifest['source']['dataset']}` |
| Pinned revision | `{manifest['source']['revision']}` |
| Data seed | `{manifest['config']['seed']}` |
| Config fingerprints | pile `{manifest['config']['fingerprint_pile'][:16]}`, bios `{manifest['config']['fingerprint_bios'][:16]}`, pack `{manifest['config']['fingerprint_pack'][:16]}` |
| Tokenizer | GPT-2 (`tiktoken`), vocab {manifest['source']['vocab_size']:,} |
| Scale vs. the full set | {cfg.scale:.0%} of every token target |
| Size | {b['total'] / 1e6:,.1f} MB over {manifest['n_files']} files |

## What is in here

| path | what it is |
|---|---|
| `manifest.json` | the whole build in one object — every file's sha256, all the counts, the fingerprints. **Read this, not the directory listing.** |
| `tokens/train.bin` | the training stream, `uint16`, EOT-separated, cut on 512-token boundaries |
| `tokens/train.idx.parquet` | one row per document **segment**: `doc_id, subject, start, length, doc_offset, person_id, rewording_id` |
| `heldout/label.bin`, `heldout/test.bin` | the two held-out halves, all 6 subjects, no biographies |
| `heldout/{{label,test}}.idx.parquet` | their indexes, plus `ngram_overlap` per document |
| `bios/people.jsonl` | one row per person: name, gender, tier, target exposures, 5 facts |
| `bios/facts.jsonl` | one row per (person, attribute, wording): `prompt`, `continuation`, `true_value`, `value_token_ids`, `role` |
| `bios/bios_train.jsonl`, `bios_control.jsonl` | the biography text, 4 rewordings per person |
| `bios/attribute_values.json`, `templates.json` | the value lists and every template, held-out ones flagged |
| `train/<slug>.jsonl.gz` | the cleaned, capped, deduplicated Pile documents the tokens came from |
| `heldout_pool/<slug>.jsonl.gz` | the same for held-out documents, before the label/test cut |
| `samples/` | the hand-check pack: Pile documents, biographies, value lists |
| `reports/` | what each stage did: `pile_manifest`, `dedup_log`, `split_report`, `pack_report` |
{"| `raw/<split>/<slug>.jsonl.gz` | the archived source text, untouched |" if with_raw else ""}

Schemas: **`docs/interfaces.md`** (DRAFT — review it).

## Contents of this sample

`train.bin`: **{train.get('tokens', 0):,} tokens = {train.get('sequences', 0):,} sequences** of {train.get('block_size', 512)}, {train.get('index_rows', 0):,} index rows.

| subject | train tokens | train segments | {" | ".join(h + " docs / tokens" for h in cfg.pack_halves)} |
|---|---:|---:|{"---:|" * len(cfg.pack_halves)}
{subject_rows}

Biographies: **{bios.get('copies', 0):,} copies** of {bios.get('distinct_biographies', 0):,} biographies = {bios.get('tokens', 0):,} tokens, over {sum(v['people'] for v in per_tier.values()):,} people, with {bios.get('facts_rows', 0):,} fact rows.

| tier | people | biography copies | tokens |
|---|---:|---:|---:|
{tier_rows}

`USPTO Backgrounds` is the **phase-2 subject**: held-out only, never in
training, which is why its training row is empty.

## Reading it

```python
import json, numpy as np
from data import pack

tokens = np.memmap("data/v1_sample/tokens/train.bin", dtype=np.uint16, mode="r")
index = pack.read_index("data/v1_sample/tokens/train.idx.parquet")
seg = tokens[index["start"][0]:index["start"][0] + index["length"][0]]

with open("data/v1_sample/bios/facts.jsonl") as fh:
    rows = [json.loads(l) for l in fh]
print(rows[0]["prompt"], "->", rows[0]["continuation"])
```

## Where 1% scale changes the answer

The sample is built by the same code, so its *shape* is the full set's. Four
numbers are not:

1. **Held-out halves miss their token budget.** At 1% a subject's held-out pool
   is only 20–130 documents and the label/test assignment is a hash, so a half
   can land ±12% off its target instead of the ±1% the full build holds. `A3`
   fails on the sample for this reason alone.
2. **The 500-documents-per-half minimum is scaled to 5 here.** The full build
   enforces 500 and passes.
3. **Uniformity is not measurable.** {sum(v['people'] for v in per_tier.values()):,} people
   against value lists of 100–300 gives expected counts near 0.1, so `A12`'s
   chi-square guard refuses to judge it. The full build's p-values are
   0.12–0.94.
4. **The biography share is too high.** Exposure counts (30 / 100 / 300) are
   deliberately *not* scaled, so biographies are ~11.8% of this sample's tokens
   against 9.7% in the full build.

Everything else — the exact per-subject token budgets, the 512-token boundary
rule for biographies, the index tiling, no answer leaks in any prompt, the
exposure counts per person — holds here exactly as it does at full scale, and
`python -m data.validate --config configs/data/v1.yaml --small --skip A17,A18`
checks it.
""",
        encoding="utf-8",
    )


def run(cfg, dst: Path, with_raw: bool = False) -> Path:
    bundle = cfg.root / "manifest.json"
    if not bundle.exists():
        raise SystemExit(
            f"no small bundle manifest at {bundle} -- run the four --small "
            "stages (build --stage pile, bios, pack, manifest) first"
        )
    json.loads(bundle.read_text())  # fail early if it is unreadable

    skip = set(SKIP_DIRS) | (set() if with_raw else OPTIONAL_DIRS)
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(
        cfg.root,
        dst,
        ignore=shutil.ignore_patterns(
            *skip,
            "extract_state.json",
            "timings.json",
            "runtime_env.json",
            "validation_report.md",
            "validation_report.json",
        ),
    )

    # The copied manifest still lists the files that were left out, which would
    # make the sample fail its own verification. Recount it over what is
    # actually here, so `manifest.json` inside the sample describes the sample.
    from data.common import write_json
    from data.manifest import build as build_manifest

    sample_cfg = copy.copy(cfg)
    sample_cfg.root = dst
    sample_cfg.reports_dir = dst / "reports"
    sample_cfg.bios_dir = dst / "bios"
    sample_manifest = build_manifest(sample_cfg)
    write_json(dst / "manifest.json", sample_manifest)

    # the README quotes the SAMPLE's own file count and size, not the build's
    write_readme(dst, cfg, sample_manifest, with_raw)
    return dst


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--config", required=True)
    ap.add_argument("--out", default="data/v1_sample")
    ap.add_argument(
        "--with-raw", action="store_true", help="include raw/, the archived source text"
    )
    args = ap.parse_args(argv)
    cfg = load_config(args.config, small=True)
    dst = run(cfg, ROOT / args.out, with_raw=args.with_raw)
    total = sum(p.stat().st_size for p in dst.rglob("*") if p.is_file())
    n = sum(1 for p in dst.rglob("*") if p.is_file())
    print(f"[sample] {dst} -- {n} files, {total / 1e6:.1f} MB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
