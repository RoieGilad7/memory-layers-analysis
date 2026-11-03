# Dataset interfaces — **DRAFT, for review by the metrics owner**

**Status:** DRAFT until the metrics owner signs off; say so on the thread and
these names change. Everything described here is **built** -- section 1 by data
prompt 1 (text) and prompt 3 (token files), section 2 by prompt 2, section 3 by
prompt 3. The freeze and the published bundle are prompt 4.
**Covers:** the files the data step produces, the fields in them, and how to
read them.
**Does not cover:** the read-log format, the slot-attribution metrics, or the
model side of the training config — those are `memlayers/readlog.py` and `memlayers/configs/*.yaml`.

Written against data config `configs/data/v1.yaml` (data seed `20261102`, Pile
revision `3be90335b66f24456a5d6659d9c8d208c0357119`). Build everything with:

```bash
python -m data.build --config configs/data/v1.yaml --stage pile   # §1 text,   4 min
python -m data.bios  --config configs/data/v1.yaml                # §2 people,  9 s
python -m data.pack  --config configs/data/v1.yaml                # §1.4 tokens, 16 s
python -m data.manifest --config configs/data/v1.yaml             # §1.6
python -m data.fetch --version v1 --verify-only                   # §3.2 check
python -m data.bios_sample --config configs/data/v1.yaml --n 20    # hand review
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
├── manifest.json                     # the BUNDLE manifest: every file's
│                                     #   sha256 + all the counts (§1.6)
├── raw/                              # the frozen archive: a rebuild never
│   ├── train/<slug>.jsonl.gz         #   needs the Pile again
│   ├── heldout/<slug>.jsonl.gz
│   └── extract_state.json
├── train/<slug>.jsonl.gz             # cleaned, capped, deduped training docs
│                                     #   (<slug> gains `bio` in prompt 3)
├── heldout_pool/<slug>.jsonl.gz      # cleaned, capped, deduped held-out docs
├── heldout/
│   ├── label/<slug>.jsonl.gz         # the labeling half, 2.5M tokens/subject
│   ├── test/<slug>.jsonl.gz          # the test half,     2.5M tokens/subject
│   ├── label.bin  label.idx.parquet  # §1.4, all 6 subjects in one file
│   └── test.bin   test.idx.parquet
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
├── tokens/                           # §1.4, written by `python -m data.pack`
│   ├── train.bin                     #   292,898 sequences of 512, uint16
│   └── train.idx.parquet             #   one row per document segment
├── reports/
│   ├── pile_manifest.json            # prompt 1's own record (§1.6)
│   ├── extract_manifest.json
│   ├── dedup_log.json
│   ├── split_report.json
│   ├── pack_report.json
│   └── timings.json                  # the only file the manifest does NOT hash
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

### 1.4 Token files — **built**, by `python -m data.pack`

| file | dtype | meaning |
|---|---|---|
| `tokens/train.bin` | `uint16` | the whole training stream: 149,963,776 tokens = 292,898 sequences of 512 |
| `tokens/train.idx.parquet` | — | one row per document **segment** (332,048 rows) |
| `heldout/label.bin` | `uint16` | the labeling half, all 6 subjects, no biographies |
| `heldout/label.idx.parquet` | — | its index, plus `ngram_overlap` |
| `heldout/test.bin`, `heldout/test.idx.parquet` | | the test half |

**Changed from the prompt-1 draft** (which was a spec, written before the
packer): the held-out side is **one file per half**, not one per (half,
subject) — the index carries `subject`, so a per-subject loss is a filter
rather than a file, and two files beat twelve. The index has one more column
than the draft promised (`doc_offset`, below) and the `.bin` *does* carry a
separator token.

**Index columns** — the contract the metrics code reads:

| column | dtype | meaning |
|---|---|---|
| `doc_id` | `string` | join key back to the JSONL |
| `subject` | `string` (dictionary-encoded) | `"Pile-CC"` … `"USPTO Backgrounds"`, or `"bio"` |
| `start` | `int64` | offset of this segment's first token in the `.bin` |
| `length` | `int64` | tokens in this segment |
| `doc_offset` | `int64` | where this segment starts **inside its document** |
| `person_id` | `string`, nullable | set only for `subject == "bio"`, null otherwise |
| `rewording_id` | `int32` | 0–3 for a biography, **-1** otherwise |
| `ngram_overlap` | `float64`, nullable | *held-out indexes only*, carried through from §1.3 |

**Why `doc_offset`.** A biography copy is never split across a 512-token
boundary; when one would not fit in what is left of the current sequence, the
rest of that sequence is filled with Pile text *pulled forward out of the
stream*. So a Pile document can reach the file in two pieces — a prefix as
filler, the rest at its own turn — and without `doc_offset` a consumer cannot
tell which part of the document a segment is. `person_id` is null rather than
`-1` for Pile rows because the column is a string.

**Invariants, all asserted by `bench/check_pack_invariants.py` on the real
build and by `tests/test_data_pack.py` on a fixture:**

- rows are in strictly increasing `start` order and never overlap;
- document tokens are never `50256` (`encode_ordinary` emits no specials), and
  **every token not covered by a segment is `50256`** — that one statement pins
  the tiling, the separators and the tail padding together;
- `start // 512 == (start + length - 1) // 512` for every `subject == "bio"` row;
- each of the 5 training subjects sums to exactly 27,000,000 tokens;
- every held-out `length` is ≤ 4,096.

Reading a segment back:

```python
import numpy as np
from data import pack
tokens = np.memmap("data/v1/tokens/train.bin", dtype=np.uint16, mode="r")
idx = pack.read_index("data/v1/tokens/train.idx.parquet")
seg = tokens[idx["start"][0] : idx["start"][0] + idx["length"][0]]
```

**Sequences, not packing, are the loader's job.** `train.bin` is already cut on
512-token boundaries, so sequence `s` is `tokens[s*512 : s*512+512]` and its
targets are the same window shifted by one — see §3.

### 1.5 Targets

| | target | built | note |
|---|---:|---:|---|
| Training, total | 150,000,000 | **149,963,776** | the 0.02% gap is EOT separators and tail padding |
| … each of 5 Pile subjects | 27,000,000 | **27,000,000** each | exact, by construction |
| … biographies | 15,000,000 (10%) | **14,631,457** (9.78%) | 190,000 copies at 77.0 tokens |
| Held-out, per subject | 5,000,000 | 5,000,000 | 6 subjects |
| … labeling half | 2,500,000 | 15,021,806 total, 13,306 docs | all 6 subjects in one file |
| … test half | 2,500,000 | 15,023,952 total, 13,381 docs | |

### 1.6 `manifest.json` — the bundle manifest

`data/v1/manifest.json`, with a copy at **`data/manifests/v1.json` that IS
committed to git** while `data/v1/` is not. One object:

| key | what |
|---|---|
| `files` | every bundle file: `path`, `bytes`, `sha256`, `optional` |
| `bytes` | `total` / `required` / `optional`, and a breakdown per top-level directory |
| `counts` | tokens, sequences and documents per subject and split; biography copies per tier; people per split |
| `config` | the three scoped fingerprints (`pile`, `bios`, `pack`) and the data seed |
| `source` | the pinned Pile revision, the tokenizer and its vocab size |
| `git` | commit, branch, whether the tree was dirty |
| `distribution` | the HF repo, the tag, which prefixes are optional |

`optional: true` marks `raw/` — 398 MB of archived source text a rebuild needs
and training does not. `data.fetch` skips it unless `--with-raw`.

**Nothing in the bundle carries a wall clock.** Stage runtimes live in
`reports/timings.json`, the one bundle path the manifest does not hash, because
a `seconds` field would make a rebuild of identical data produce a different
manifest. Rebuilding gives a byte-identical `train.bin`, held-out files *and*
manifest.

The per-stage records are still there, next to it:
`reports/pile_manifest.json` (prompt 1 — it moved out of `manifest.json` so the
bundle manifest could own that path), `reports/dedup_log.json`,
`reports/split_report.json`, `reports/pack_report.json`, `bios/manifest.json`.

**Read the manifest, not the directory listing**, to find out what a build
contains.

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

## 3. Reading the data

### 3.1 The loader — `data/loader.py`

```python
from data.loader import PackedDataset
ds = PackedDataset("data/v1/tokens/train.bin", block_size=512, seed=1337)
x, y = ds.get_batch(step, batch_size=32)       # (32, 512) int64 each
```

Sequence `s` covers tokens `[s*512, s*512 + 513)`: `x` is the first 512, `y` is
the window shifted by one, so **the last target is the first token of the next
sequence** and no token goes unpredicted. The final sequence is dropped when the
file has no 513th token for it.

Order is a permutation of the sequence indices, one per epoch, keyed by
`(seed, epoch)`. Position is explicit state:

```python
state = ds.state_dict()      # {"seed", "position", "n_sequences", "block_size", ...}
ds.load_state_dict(state)    # a resumed run reads exactly the batches it would have
```

`load_state_dict` refuses a state whose `n_sequences` or `block_size` does not
match the file on disk, rather than silently reading a different dataset.

Signature-compatible with `memlayers.data_fake`, so `memlayers/train.py` swaps
one for the other on a config flag.

### 3.2 Fetch and verify — `data/fetch.py`

```bash
python -m data.fetch --version v1                 # download + verify
python -m data.fetch --version v1 --with-raw      # include raw/ (398 MB more)
python -m data.fetch --version v1 --verify-only   # offline, verify only
```

The authority is the committed `data/manifests/v1.json`. Every file is checked
by size and sha256, so a truncated download, a wrong tag or an edited file is
caught before training reads a token. `--verify-only` never touches the network.

Until the bundle is published, `distribution.hf_repo` is the placeholder
`<owner>/memlayers-data` and a download **refuses**, naming the three local
build commands instead. Verification works either way.

### 3.3 Training on it — `memlayers/train.py`

```yaml
data:
    source: real          # "fake" (default) keeps the step-1 synthetic datasets
    version: v1
    data_config: configs/data/v1.yaml
    seed: 1337            # the loader's permutation seed
    verify: true          # check every sha256 before step 0
```

With `source: real` the Trainer verifies the bundle **before step 0** and raises
on any mismatch — a half-downloaded bundle would produce numbers nobody could
reproduce. It records the data version, the manifest sha256, the pack
fingerprint and the Pile revision in `meta.json`, in the checkpoint and in two
`log.csv` columns, and it saves the loader's `(seed, position)` so a resume
continues exactly where it stopped. Resuming a checkpoint whose manifest hash
differs from the bundle on disk is refused.

---

## 4. Open questions for the metrics owner

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
