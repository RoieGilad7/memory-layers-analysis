# Dataset interfaces — **DRAFT, for review by the metrics owner**

**Status:** DRAFT. Sections 1 and 2 only. Nothing here is frozen until the metrics
owner signs off; say so on the thread and these names change. Section 1 is built
(data prompt 1) and so is section 2 (data prompt 2); section 1.4, the token
files, is still a spec.
**Covers:** the files the data step produces and the fields in them.
**Does not cover:** the token files' construction (prompt 3), the read-log
format, the slot-attribution metrics, or the training config — those are `memlayers/readlog.py` and `memlayers/configs/*.yaml`.

Written against data config `configs/data/v1.yaml` (data seed `20261102`, Pile
revision `3be90335b66f24456a5d6659d9c8d208c0357119`). Build everything with:

```bash
python -m data.build --config configs/data/v1.yaml --stage pile          # §1, 8 min
python -m data.bios  --config configs/data/v1.yaml                       # §2, 1 min
python -m data.bios_sample --config configs/data/v1.yaml --n 20          # hand review
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
| Index files | Parquet (§1.4); token arrays are raw little-endian `uint16` |
| Document cap | every document is its first **4,096 tokens**, and the stored text is guaranteed to re-encode to ≤ 4,096 |
| Document floor | documents under **50 tokens** (after cleaning) are dropped |
| Subject | the Pile's `meta.pile_set_name`, verbatim; biographies use the extra subject **`"bio"`** |

**Document id** — `"<subject_slug>-<source_tag>-<line_number>"`, e.g.
`pile_cc-train00-128745`. `line_number` is the 0-based line index in the source
shard, so ids survive a rebuild.

Biographies use the same three-part shape with `bio` as the slug, the person id
as the source tag and the rewording index as the last field:
`"bio-<person_id>-<variant>"`, e.g. `bio-p000317-2` for person `p000317`'s third
reworded biography. So the same `split("-")` works on every id in the corpus.

Ids are unique across the whole corpus and are the join key everywhere.

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
│                                     #   (<slug> gains `bio` in prompt 3)
├── heldout_pool/<slug>.jsonl.gz      # cleaned, capped, deduped held-out docs
├── heldout/
│   ├── label/<slug>.jsonl.gz         # the labeling half, 2.5M tokens/subject
│   └── test/<slug>.jsonl.gz          # the test half,     2.5M tokens/subject
├── bios/                             # §2, written by `python -m data.bios`
│   ├── people.jsonl                  #   2,500 people: facts, gender, tier
│   ├── facts.jsonl                   #   100,000 fact prompts
│   ├── bios_train.jsonl              #   4 rewordings x 2,000 trained people
│   ├── bios_control.jsonl            #   4 rewordings x 500 control people
│   ├── attribute_values.json         #   the realised value lists + drops
│   ├── templates.json                #   every template, held-out flagged
│   ├── name_check.json               #   which names the Pile already contains
│   └── manifest.json                 #   counts, token lengths, exposures
├── samples/
│   └── bios_sample.md                # 20 people, for hand review (committed)
├── tokens/                           # §1.4, built by a later prompt
│   ├── train.bin  train.idx.parquet
│   └── heldout_<half>_<slug>.bin  …idx.parquet
├── reports/
│   ├── extract_manifest.json
│   ├── dedup_log.json
│   └── split_report.json
└── _work/                            # stage scratch; safe to delete
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
| `line` | int | 0-based line index in the source shard; for biographies, the rewording index (§2.3) |
| `n_tokens` | int | GPT-2 tokens of `text`, **≤ 4,096** |
| `truncated` | bool | true if the source document was longer than the cap |
| `sha256` | str | hex sha256 of `text` — the exact-duplicate key |
| `text` | str | cleaned, capped document text |
| `ngram_overlap` | float | *held-out only*: fraction of this document's GPT-2 token 13-grams that occur in the training documents of the same subject. Documents above `0.50` are already gone. |
| `half` | str | *`heldout/<half>/` only*: `"label"` or `"test"` |
| `person_id` | str or null | set **only** when `subject == "bio"` → `people.jsonl` / `facts.jsonl`. Present so a biography record joins to its facts without reading the token index. Null on every Pile document. |

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
| `person_id` | `string`, nullable | copied from the document record (§1.3); set only for `subject == "bio"`, null otherwise |

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

## 2. Biography set — **built**, by `python -m data.bios`

Made-up people after bioS (Allen-Zhu & Li, arXiv:2309.14316). Each person's five
facts are drawn **uniformly at random** from fixed value lists, so a model can
only answer a question about one by having stored it, and the ground truth is
never in doubt. See `reports/data2_bios_report.md`.

**This section changed in data prompt 2** relative to the prompt-1 draft, which
was written before the generator existed. What moved: the directory is `bios/`
not `bio/`; `gender` is `"female"`/`"male"` (no `"x"` — the generator assigns
gendered first names and gendered pronouns); `tier` gained `"control"` and is
joined by `target_exposures`; `facts.jsonl` gained `split`, `tier`, `role`,
`rewording_id` and `continuation`, and `template_id` now means "index into this
attribute's training pool, or into its held-out pool when `held_out_template`".

| | |
|---|---|
| People | **2,500** = 2,000 trained + 500 control |
| Gender | exactly 1,250 female / 1,250 male, balanced inside every tier |
| Facts per person | 5: `birth_date`, `birth_city`, `university`, `major`, `employer` |
| Rewordings per person | 4, drawn from different templates |
| Templates per attribute | 20 training + 4 held-out |
| `facts.jsonl` rows | **100,000** = 2,500 x 5 x (4 rewordings + 4 held-out templates) |
| Biography length | mean 77 GPT-2 tokens, range 60–99 |

### 2.1 `bios/people.jsonl` — one row per person

| field | type | meaning |
|---|---|---|
| `person_id` | str | `"p<6-digit>"`, e.g. `p000317`. The join key for facts and documents. |
| `name` | str | full name, unique across all 2,500, and **absent from the cleaned Pile text** (§2.5) |
| `first_name`, `last_name` | str | the two halves, so a metric can match on either |
| `gender` | str | `"female"` / `"male"` — drives the pronouns in the templates |
| `split` | str | `"train"` or `"control"`. **`control` people never enter training** — they are the floor for "the model is guessing". |
| `tier` | str | `"rare"` / `"normal"` / `"frequent"` for trained people, `"control"` otherwise |
| `target_exposures` | int | biography copies this person should get in training: 30 / 100 / 300 by tier, 0 for control. **Prompt 3 places the copies; this is the target.** |
| `n_rewordings` | int | 4 |
| `facts` | object | `{attribute: value}` for the 5 attributes |

Tier is what lets the analysis ask whether a rarely-seen fact lives in different
slots from an often-seen one, so the three exposure levels are deliberately far
apart (30 / 100 / 300) and exactly gender-balanced.

### 2.2 `bios/facts.jsonl` — one row per (person, attribute, wording)

4 training rewordings + 4 held-out templates per (person, attribute).

| field | type | meaning |
|---|---|---|
| `fact_id` | str | `"<person_id>-<attribute>-r<rewording_id>"`, or `-h<template_id>` for a held-out row |
| `person_id` | str | → `people.jsonl` |
| `split`, `tier` | str | copied from the person, so a row needs no join to be grouped |
| `attribute` | str | one of the 5 |
| `template_id` | int | index into this attribute's **training** pool (0–19), or into its **held-out** pool (0–3) when `held_out_template` |
| `rewording_id` | int or null | 0–3 for a training row; **null** for a held-out row |
| `held_out_template` | bool | true if this wording never appears in training text |
| `role` | str | `"discovery"` (rewordings 0–1), `"test"` (rewordings 2–3), `"paraphrase"` (held-out). The fact-dependence metric **picks slots on discovery prompts and ablates them on test prompts**; `paraphrase` asks whether the fact survives a new structure. |
| `prompt` | str | the biography text up to the value, **without the space before it** |
| `continuation` | str | `" " + true_value` — exactly what the model must produce |
| `true_value` | str | the value alone, for exact-match scoring and for reading |
| `value_token_ids` | list[int] | GPT-2 ids of `continuation`, so scoring needs no tokenizer |
| `doc_id` | str or null | the biography document this wording appears in; **null** for held-out rows, which appear in no document |

**Why `prompt` stops before the space.** The value's first GPT-2 token carries
the space: `" March"`, not `"March"`. A prompt ending in a space would feed the
model token 220 and make the intended continuation unreachable, which would
quietly wreck the metric. So:

```python
assert biography.startswith(row["prompt"] + row["continuation"])
assert row["continuation"] == " " + row["true_value"]
assert row["value_token_ids"] == enc.encode_ordinary(row["continuation"])
```

`prompt` is a prefix of a real biography character for character, so pronouns in
it resolve. For a held-out row the biography is the person's rewording
`bios.rewordings.heldout_context_rewording` (0) with **only that attribute's
sentence** swapped for the held-out template, so the context is familiar and the
single new thing is one sentence's structure.

### 2.3 `bios/bios_train.jsonl` and `bios_control.jsonl`

One line per (person, rewording): `person_id`, `rewording_id`, `doc_id`, `text`.
`doc_id` is `"bio-<person_id>-<rewording_id>"`. Control people appear **only** in
`bios_control.jsonl`; their four rewordings exist so the same prompts can be
asked of a person the model has never seen.

Prompt 3 turns these into `train/bio.jsonl.gz` and
`heldout/<half>/bio.jsonl.gz` in the §1.3 schema (`subject == "bio"`,
`source == "bio"`, `line` = the rewording index, `person_id` set,
`truncated` always false). **The 0.50 13-gram drop rule must not be applied to
`bio`**: four rewordings of one person's facts overlap by design, so the rule
would delete the held-out set it exists to protect. That needs an exemption in
the dedup config when biographies are merged in.

### 2.4 `bios/attribute_values.json` and `templates.json`

`attribute_values.json` holds `values` (the realised list per attribute),
`filtering` (candidates in, near-duplicates dropped, first-token clashes
dropped, trimmed to target) and `tokens` (whether first tokens are unique, and
the mean token length of a value).

`templates.json` holds every template with its `template_id`,
`held_out_template` flag and `pre_value_context` — the three words before the
value. **No held-out template shares a `pre_value_context` with a training
template of the same attribute**, which is what makes a paraphrase row a test of
the fact rather than of the phrasing. `heldout_markers` lists four strings that
appear in held-out frames and in no training template, so "did held-out wording
leak into training" is one substring search.

### 2.5 `bios/name_check.json`

Every candidate full name is searched for in prompt 1's cleaned Pile text
(`train/` and `heldout_pool/`, all subjects, case-sensitive, exact match). Names
the Pile already contains are rejected before people are assigned, so no fact
can be confused with something the model read about a real person. The file
records the files scanned, the characters scanned, and every name found.

---

## 3. Open questions for the metrics owner

1. **`tokens/` sharding.** One `train.bin` for all 150M tokens (300 MB) or one
   per subject? One file keeps the loader trivial; per-subject files make
   "train on 4 of 5 subjects" a config change instead of a rebuild.
2. **`person_id` in the index** is nullable, which makes the column
   dictionary-encoded-with-nulls. Would a separate `bio.idx.parquet` be easier
   to consume?
3. **Held-out biographies**: control people now get the same four rewordings as
   trained people (in `bios_control.jsonl`), so the same prompts can be asked of
   someone the model never saw. Open: should those rewordings also go into the
   held-out `label`/`test` halves as *documents*, or stay out of the token files
   entirely and be used only through `facts.jsonl`?
4. **`ngram_overlap`** is reported per held-out document. Does the metrics code
   want to filter on it (e.g. drop above 0.2 for a clean subset), or is the
   0.50 build-time rule enough?
5. **Exposure placement.** `target_exposures` says 30 / 100 / 300 copies per
   person but not how to spread them over the 4 rewordings. Round-robin (7–8
   copies of each at tier `rare`) is the obvious choice and keeps every wording
   equally represented; the alternative is to sample rewordings, which makes the
   per-wording count itself a random variable. Prompt 3 has to decide.
