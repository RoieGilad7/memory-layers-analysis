# Dataset interfaces — **DRAFT, for review by the metrics owner**

**Status:** DRAFT. Sections 1 and 2 only. Nothing here is frozen until the metrics
owner signs off; say so on the thread and these names change.
**Covers:** the files the data step produces and the fields in them.
**Does not cover:** the read-log format, the slot-attribution metrics, or the
training config — those are `memlayers/readlog.py` and `memlayers/configs/*.yaml`.

Written against data config `configs/data/v1.yaml` (data seed `20261102`, Pile
revision `3be90335b66f24456a5d6659d9c8d208c0357119`). Build everything with:

```bash
python -m data.build --config configs/data/v1.yaml --stage pile          # full
python -m data.build --config configs/data/v1.yaml --stage pile --small  # 1%, ~10 s
```

A frozen `data/v1_sample/` (the `--small` output, a few MB) ships in the repo so
code can be written against real records before the full build lands.

---

## 0. Conventions used throughout

| | |
|---|---|
| Text encoding | UTF-8, Unicode **NFC**, LF line endings |
| Tokenizer | **GPT-2** via `tiktoken.get_encoding("gpt2")`, `n_vocab = 50257` |
| Token dtype | `uint16` (50,257 < 65,536) |
| Line format | one JSON object per line, keys **sorted**, `ensure_ascii=False`, no spaces after separators |
| Compression | `.jsonl.gz`, gzip with **`mtime=0`** so two builds are byte-identical |
| Index/array files | little-endian; `.npy` carries its own dtype header |
| Document cap | every document is its first **4,096 tokens**, and the stored text is guaranteed to re-encode to ≤ 4,096 |
| Document floor | documents under **50 tokens** (after cleaning) are dropped |
| Subject | the Pile's `meta.pile_set_name`, verbatim; biographies use the extra subject **`"bio"`** |

**Document id** — `"<subject_slug>-<source_tag>-<line_number>"`, e.g.
`pile_cc-train00-128745`. `line_number` is the 0-based line index in the source
shard, so ids survive a rebuild. Biography ids are `"bio-<person_id>-<variant>"`
(§2). Ids are unique across the whole corpus and are the join key everywhere.

**Subject slugs** (fixed in the config, never derived at runtime):

| `meta.pile_set_name` | slug | role |
|---|---|---|
| `Pile-CC` | `pile_cc` | training + held-out |
| `Github` | `github` | training + held-out |
| `PubMed Central` | `pubmed_central` | training + held-out |
| `FreeLaw` | `freelaw` | training + held-out |
| `Wikipedia (en)` | `wikipedia_en` | training + held-out |
| `USPTO Backgrounds` | `uspto_backgrounds` | **held-out only** (phase 2) |
| *(synthetic)* | `bio` | training + held-out |

---

## 1. Dataset files

### 1.1 Directory layout

```
data/v1/
├── manifest.json                     # one build, every number (§1.6)
├── raw/                              # the frozen archive: a rebuild never
│   ├── train/<slug>.jsonl.gz         #   needs the Pile again
│   ├── heldout/<slug>.jsonl.gz
│   └── extract_state.json
├── train/<slug>.jsonl.gz             # cleaned, capped, deduped training docs
├── heldout_pool/<slug>.jsonl.gz      # cleaned, capped, deduped held-out docs
├── heldout/
│   ├── label/<slug>.jsonl.gz         # the labeling half, 2.5M tokens/subject
│   └── test/<slug>.jsonl.gz          # the test half,     2.5M tokens/subject
├── bio/                              # §2, built by a later prompt
│   ├── people.jsonl
│   ├── facts.jsonl
│   ├── train.jsonl.gz
│   └── heldout/{label,test}.jsonl.gz
├── tokens/                           # §1.4, built by a later prompt
│   ├── train.bin  train.idx.parquet
│   └── heldout_<half>_<slug>.bin  …idx.parquet
└── reports/
    ├── extract_manifest.json
    ├── dedup_log.json
    └── split_report.json
```

### 1.2 Raw archive — `raw/<split>/<slug>.jsonl.gz`

The source text exactly as the Pile served it, for the documents this build
kept. Part of the frozen bundle.

| field | type | meaning |
|---|---|---|
| `doc_id` | str | see conventions |
| `subject` | str | `meta.pile_set_name`, verbatim |
| `split` | str | `"train"` or `"heldout"` |
| `source` | str | shard filename, e.g. `"train/00.jsonl.zst"` |
| `line` | int | 0-based line index in that shard |
| `text` | str | **untouched** source text, not cleaned, not capped |

### 1.3 Document files — `train/`, `heldout_pool/`, `heldout/<half>/`

Cleaned, capped and deduplicated. Same schema in all three, plus one field in
the halves.

| field | type | meaning |
|---|---|---|
| `doc_id` | str | join key |
| `subject` | str | verbatim Pile label, or `"bio"` |
| `split` | str | `"train"` or `"heldout"` |
| `source` | str | shard filename (`"bio"` for biographies) |
| `line` | int | 0-based line index in the shard (person index for biographies) |
| `n_tokens` | int | GPT-2 tokens of `text`, **≤ 4,096** |
| `truncated` | bool | true if the source document was longer than the cap |
| `sha256` | str | hex sha256 of `text` — the exact-duplicate key |
| `text` | str | cleaned, capped document text |
| `ngram_overlap` | float | *held-out only*: fraction of this document's GPT-2 token 13-grams that occur in the training documents of the same subject. Documents above `0.50` are already gone. |
| `half` | str | *`heldout/<half>/` only*: `"label"` or `"test"` |

Held-out halves are disjoint **by whole document**: the half is
`blake2b(f"{seed}:{doc_id}")[:8] % 2`, so it depends on nothing but the id and
the data seed.

### 1.4 Token files — `tokens/` *(next prompt; spec fixed here)*

| file | dtype | shape | meaning |
|---|---|---|---|
| `train.bin` | `uint16` | `[N]` | every training document's tokens, concatenated in index order, no separator token |
| `train.idx.parquet` | — | `[D, 5]` | one row per document (below) |
| `heldout_<half>_<slug>.bin` | `uint16` | `[N]` | one file per (half, subject), same layout |
| `heldout_<half>_<slug>.idx.parquet` | — | `[D, 5]` | its index |

**Index columns** (this is the contract the metrics code reads):

| column | dtype | meaning |
|---|---|---|
| `doc_id` | `string` | join key back to the JSONL |
| `subject` | `string` (dictionary-encoded) | `"Pile-CC"` … `"USPTO Backgrounds"`, or `"bio"` |
| `start` | `int64` | offset of the document's first token in the `.bin` |
| `length` | `int64` | number of tokens, `1 ≤ length ≤ 4096` |
| `person_id` | `string`, nullable | set **only** for `subject == "bio"` (§2); null otherwise |

Invariants the loader may assume: rows are in `start` order, `start[0] == 0`,
`start[i+1] == start[i] + length[i]`, and `sum(length) == len(bin) `.

**Packing into training sequences is the loader's job, not the file's.** The
`.bin` holds documents back to back; the loader cuts `block_size` windows and
decides whether to mask across document boundaries (`mask_slots` in the training
config). Keeping the boundary information in the index rather than baking an
`<|endoftext|>` into the stream is what lets a later experiment change that
decision without rebuilding the tokens.

### 1.5 Targets

| | tokens | note |
|---|---:|---|
| Training, total | 150,000,000 | |
| … each of 5 Pile subjects | 27,000,000 | 18% each = 90% |
| … biographies | 15,000,000 | 10%, §2 |
| Held-out, per subject | 5,000,000 | 6 subjects (5 training + USPTO Backgrounds) |
| … labeling half | 2,500,000 | ≥ 500 documents |
| … test half | 2,500,000 | ≥ 500 documents |

### 1.6 `manifest.json`

One object per build: config fingerprint, data seed, dataset + pinned revision,
tokenizer, document rules, per-subject document/token counts for train and both
held-out halves, the aggregate 13-gram overlap rate per subject, bytes
downloaded, disk used, runtime, and a `problems` block naming any subject below
target. **Read the manifest, not the directory listing**, to find out what a
build actually contains.

---

## 2. Biography set — *built by a later prompt; this is the contract*

Synthetic people after bioS (Allen-Zhu & Li, arXiv:2309.14316), generated by
`tools/bio_generator.py`. Knowledge enters the model only through biography
text, so a correct answer means the fact was stored, not pattern-matched.

Biography documents live in the same document files as everything else, with
`subject == "bio"` and `person_id` set in the token index.

### 2.1 `bio/people.jsonl` — one row per person

| field | type | meaning |
|---|---|---|
| `person_id` | str | stable id, `"p<6-digit>"`, e.g. `p000317`. The join key for facts and documents. |
| `name` | str | full name, unique across the set |
| `gender` | str | `"f"` / `"m"` / `"x"` — drives pronouns in the templates |
| `tier` | str | how often this person appears in training: `"frequent"`, `"normal"`, `"rare"`. Tier is what lets the analysis ask whether rarely-seen facts live in different slots. |
| `n_rewordings` | int | how many reworded biographies this person gets |
| `facts` | object | `{attribute: value}` for the 5 attributes: `birth_date`, `birth_city`, `university`, `major`, `employer` |
| `split` | str | `"train"` or `"control"`. **`control` people never appear in training at all** — they are the floor for "the model is guessing". |

### 2.2 `bio/facts.jsonl` — one row per (fact, rewording)

One row for every way a fact is stated, so recall can be scored per attribute
and per phrasing.

| field | type | meaning |
|---|---|---|
| `fact_id` | str | `"<person_id>-<attribute>-<template_id>"` |
| `person_id` | str | → `people.jsonl` |
| `attribute` | str | one of the 5 attribute names |
| `template_id` | int | which template of that attribute's pool was used |
| `held_out_template` | bool | true if this template is **never** used in training text; held-out templates test whether the fact generalizes past its surface form |
| `prompt` | str | the biography text **up to but not including** the value — feed this, read the continuation |
| `true_value` | str | the value the continuation must produce |
| `value_token_ids` | list[int] | GPT-2 ids of `true_value`, so scoring needs no tokenizer at eval time |
| `doc_id` | str, nullable | the biography document this phrasing appears in; null when `held_out_template` is true |

`prompt` is a prefix of a real biography, character for character, so
`prompt + true_value` is exactly what the model saw (when
`held_out_template == false`).

### 2.3 Biography documents

Same schema as §1.3, with `subject == "bio"`, `source == "bio"` and `line` =
the person index. Each `text` is one person's biography paragraph in one
rewording. Biography documents also go into the held-out halves, so the
label/test split covers the synthetic facts as well as the Pile subjects.

---

## 3. Open questions for the metrics owner

1. **`tokens/` sharding.** One `train.bin` for all 150M tokens (300 MB) or one
   per subject? One file keeps the loader trivial; per-subject files make
   "train on 4 of 5 subjects" a config change instead of a rebuild.
2. **`person_id` in the index** is nullable, which makes the column
   dictionary-encoded-with-nulls. Would a separate `bio.idx.parquet` be easier
   to consume?
3. **Held-out biographies**: should `control` people appear in the held-out
   halves at all, or only in `facts.jsonl`?
4. **`ngram_overlap`** is reported per held-out document. Does the metrics code
   want to filter on it (e.g. drop above 0.2 for a clean subset), or is the
   0.50 build-time rule enough?
