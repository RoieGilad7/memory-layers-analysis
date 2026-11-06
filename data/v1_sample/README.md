# `data/v1_sample/` — the 1% sample of dataset `v1`

Real text from the Pile and real generated biographies, built by the same code
as the full set with every token target scaled to **1%** (`--small`). Here so
the metrics code can be written against real records without the 1.1 GB bundle.
**Not a training set.**

It mirrors what `python -m data.fetch --version v1` gives you by default, so
`raw/` is **left out** — a rebuild needs the archived
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
| Source | `monology/pile-uncopyrighted` |
| Pinned revision | `3be90335b66f24456a5d6659d9c8d208c0357119` |
| Data seed | `20261102` |
| Config fingerprints | pile `ed4f593bce4c0444`, bios `ecb17a71f9a3196a`, pack `d9c827659fd33939` |
| Tokenizer | GPT-2 (`tiktoken`), vocab 50,257 |
| Scale vs. the full set | 1% of every token target |
| Size | 8.5 MB over 47 files |

## What is in here

| path | what it is |
|---|---|
| `manifest.json` | the whole build in one object — every file's sha256, all the counts, the fingerprints. **Read this, not the directory listing.** |
| `tokens/train.bin` | the training stream, `uint16`, EOT-separated, cut on 512-token boundaries |
| `tokens/train.idx.parquet` | one row per document **segment**: `doc_id, subject, start, length, doc_offset, person_id, rewording_id` |
| `heldout/label.bin`, `heldout/test.bin` | the two held-out halves, all 6 subjects, no biographies |
| `heldout/{label,test}.idx.parquet` | their indexes, plus `ngram_overlap` per document |
| `bios/people.jsonl` | one row per person: name, gender, tier, target exposures, 5 facts |
| `bios/facts.jsonl` | one row per (person, attribute, wording): `prompt`, `continuation`, `true_value`, `value_token_ids`, `role` |
| `bios/bios_train.jsonl`, `bios_control.jsonl` | the biography text, 4 rewordings per person |
| `bios/attribute_values.json`, `templates.json` | the value lists and every template, held-out ones flagged |
| `train/<slug>.jsonl.gz` | the cleaned, capped, deduplicated Pile documents the tokens came from |
| `heldout_pool/<slug>.jsonl.gz` | the same for held-out documents, before the label/test cut |
| `samples/` | the hand-check pack: Pile documents, biographies, value lists |
| `reports/` | what each stage did: `pile_manifest`, `dedup_log`, `split_report`, `pack_report` |


Schemas: **`docs/interfaces.md`** (DRAFT — review it).

## Contents of this sample

`train.bin`: **1,538,048 tokens = 3,004 sequences** of 512, 3,815 index rows.

| subject | train tokens | train segments | label docs / tokens | test docs / tokens |
|---|---:|---:|---:|---:|
| `Pile-CC` | 270,000 | 432 | 25 / 25,884 | 41 / 25,424 |
| `Github` | 270,000 | 282 | 21 / 25,030 | 18 / 27,359 |
| `PubMed Central` | 270,000 | 105 | 8 / 27,944 | 7 / 25,635 |
| `FreeLaw` | 270,000 | 133 | 6 / 23,379 | 10 / 27,898 |
| `Wikipedia (en)` | 270,000 | 563 | 51 / 25,383 | 59 / 25,070 |
| `USPTO Backgrounds` | 0 | 0 | 36 / 25,261 | 33 / 25,567 |

Biographies: **2,300 copies** of 88 biographies = 183,949 tokens, over 28 people, with 1,120 fact rows.

| tier | people | biography copies | tokens |
|---|---:|---:|---:|
| `frequent` | 4 | 1,200 | 96,150 |
| `normal` | 8 | 800 | 63,850 |
| `rare` | 10 | 300 | 23,949 |
| `control` | 6 | 0 | 0 |

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
3. **Uniformity is not measurable.** 28 people
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
