# `data/v1_sample/` — the 1% sample of dataset v1

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
| Source | `monology/pile-uncopyrighted` |
| Pinned revision | `3be90335b66f24456a5d6659d9c8d208c0357119` |
| Data seed | `20261102` |
| Config fingerprint | `cf669c71b1a42699` |
| Tokenizer | GPT-2 (`tiktoken`), vocab 50,257 |
| Document cap / floor | 4,096 / 50 tokens |
| Scale vs. the full set | 1% of every token target |

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

| slug | subject | train docs | train tokens | label docs / tokens | test docs / tokens | 13-gram overlap |
|---|---|---:|---:|---:|---:|---:|
| `freelaw` | FreeLaw | 128 | 328,070 | 6 / 23,379 | 10 / 27,898 | 9.142% |
| `github` | Github | 264 | 324,344 | 21 / 25,030 | 18 / 27,359 | 6.013% |
| `pile_cc` | Pile-CC | 388 | 324,408 | 25 / 25,884 | 41 / 25,424 | 0.000% |
| `pubmed_central` | PubMed Central | 86 | 326,800 | 8 / 27,944 | 7 / 25,635 | 0.913% |
| `uspto_backgrounds` | USPTO Backgrounds | 0 | 0 | 36 / 25,261 | 33 / 25,567 | 0.000% |
| `wikipedia_en` | Wikipedia (en) | 503 | 324,445 | 51 / 25,383 | 59 / 25,070 | 0.138% |

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
