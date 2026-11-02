# Data step 1 — the Pile part of dataset v1

**Project:** What memory-layer values store and how they are organized (PKM / PEER vs. a kNN-LM store)
**Course:** COMS E6998 Algorithms in LLMs — final project
**Date:** 2026-11-02
**Machine:** Apple M5 Pro, 18 cores, 64 GiB, macOS 26.6.2, `.venv` Python 3.12.14
**Scope:** the data config, the interface spec, and the Pile side of the dataset
**up to but not including tokenization**. Biographies, token files, the loader
and the full validation are later prompts. **No token files were written.**

Everything below is produced by code in this repo and read out of the build's
own JSON by `python -m data.report_tables`; no figure in this report was typed
by hand.

```bash
python -m data.build --config configs/data/v1.yaml --stage pile            # 6.0 min
python -m data.build --config configs/data/v1.yaml --stage pile --small    # 7 s, 1%
python -m data.make_sample --config configs/data/v1.yaml                   # the bundle
python -m pytest tests/test_data_*.py                                      # 36 tests, no network
```

---

## 1. Headline

Every target in the fixed design was met, with no fallback shard needed.

- **161.7M training tokens** across the 5 subjects — each subject holds its 27M
  target plus the 20% slack (32.3–32.4M), waiting for the tokenize stage to cut
  it to exactly 27M.
- **All 12 held-out halves filled**: 2.50M tokens each, 708–3,822 documents,
  every one above the 500-document minimum (the tightest is PubMed Central's
  labeling half at 708).
- **`USPTO Backgrounds` is clean**: 6.996M held-out tokens, zero training
  tokens, zero 13-gram overlap by construction.
- **The build is byte-identical on a rebuild** — proven at both 1% and full
  scale by re-running from scratch and comparing sha256 of all 40 output files.
- **One real finding:** `Github` held-out text overlaps its own training text at
  **20.7%** of 13-grams, and the 50% rule dropped **672** of its 5,130 held-out
  documents (13.1%). `FreeLaw` is second at 11.5% / 311 documents. See §5.

---

## 2. Source, pinning and the exact subject labels

The subject label is `meta.pile_set_name`, read verbatim. These are the exact
strings as they appear in the data (confirmed by streaming, not assumed):

| role | `meta.pile_set_name` | slug |
|---|---|---|
| training + held-out | `Pile-CC` | `pile_cc` |
| training + held-out | `Github` | `github` |
| training + held-out | `PubMed Central` | `pubmed_central` |
| training + held-out | `FreeLaw` | `freelaw` |
| training + held-out | `Wikipedia (en)` | `wikipedia_en` |
| **held-out only (phase 2)** | `USPTO Backgrounds` | `uspto_backgrounds` |

Note `Github` (not `GitHub`) and `Wikipedia (en)` with the parenthesized tag —
both are easy to mistype, and a mistyped label silently yields an empty subject.
They are fixed in `configs/data/v1.yaml`, never derived at runtime.

The revision was resolved once with `huggingface_hub` and pinned in the config:

```
monology/pile-uncopyrighted @ 3be90335b66f24456a5d6659d9c8d208c0357119
```

That commit holds `train/00.jsonl.zst` … `train/29.jsonl.zst` (11.1–11.2 GB
each), `val.jsonl.zst` (0.34 GB) and `test.jsonl.zst` (0.34 GB).

**Streaming.** The extractor does not use `datasets`; it asks
`huggingface_hub.hf_hub_url` for the pinned blob URL and feeds the raw HTTP
response into `zstandard.ZstdDecompressor(max_window_size=2**31).stream_reader`,
then reads JSON lines. Two reasons: it gives a true line number per document
(which is what makes document ids stable), and it reads exactly one named shard
instead of whatever `datasets` decides to interleave. The step-0 gotcha still
applies — **`zstandard` must be installed** or the shards cannot be opened at
all; it is pinned at `0.25.0` in `requirements.txt`.

**Document ids** are `"<subject_slug>-<source_tag>-<line_number>"`, e.g.
`pile_cc-train00-128745`, with a 0-based line index into the named shard. They
survive a rebuild because the pinned shard's line order is fixed.

---

## 3. What the pipeline does, stage by stage

```
data/pile_extract.py   stream the pinned shards -> data/v1/raw/<split>/<slug>.jsonl.gz
data/dedup.py          clean, cap at 4096, exact dedup, 13-gram rule
data/split.py          label/test halves, trimmed to 2.5M tokens each
data/build.py          runs the three in order, writes manifest.json
```

**Extract.** One pass over `train/00.jsonl.zst` for training text and one over
`val.jsonl.zst` for held-out text. A subject stops being collected once it
reaches **target + 20% slack**; the pass ends as soon as every subject is full,
which is why only 537,289 of the shard's lines were ever read. The archive under
`raw/` holds the **untouched source text** — cleaning and the cap are recomputed
there only to make the budget accurate. That archive is the frozen bundle's
input: a rebuild never touches the Pile again.

Resumability is per-block. Records go to part files keyed by
`line_number // 100000`; the state file is written at block boundaries only, and
a resume deletes the parts at or after the current block and re-streams the
skipped prefix. Re-streaming is the price of single-frame zstd having no random
access — there is no byte offset you can restart a decompressor from. At most
100,000 lines of work is ever lost.

**Clean.** NFC; `\r\n` and `\r` → `\n`; BOM and NUL dropped; then, per line, the
**leading run of spaces and tabs is copied through byte for byte** and only the
rest of the line has its horizontal-whitespace runs collapsed to one space and
its trailing whitespace stripped. That is what keeps Github code readable —
`tests/test_data_clean.py::test_code_indentation_survives` pins 4-, 8- and 12-space
indents and a tab indent. Runs of more than 2 newlines collapse to 2 and the document is
stripped at both ends. Cleaning is idempotent (also tested).

**The cap.** Every document is its first **4,096 GPT-2 tokens**
(`tiktoken.get_encoding("gpt2")`, `n_vocab` asserted to be 50,257,
`encode_ordinary` so a literal `<|endoftext|>` in the text cannot raise). The
cut is iterated to a fixed point, because `decode(encode(x)[:4096])` can
re-encode to slightly more than 4,096 tokens; the stored text is therefore
**guaranteed** to re-encode to ≤ 4,096, which is what the tests assert and what
the tokenize stage can rely on.

**Exact dedup.** sha256 of the cleaned, capped text, in one global set, so
duplicates are removed within a split, across splits, and across subjects.
Documents are visited in a fixed order — train before held-out, config subject
order, then source file and line — so which copy survives never depends on
timing. A held-out document identical to a training document is always the one
that loses.

**The 13-gram rule.** Per subject, every GPT-2 token 13-gram of that subject's
**training** documents is hashed (FNV-1a over the 13 ids, then a splitmix64
finalizer, fixed constants — never Python's per-process-seeded `hash()`) into
one sorted `uint64` array; held-out documents are then tested against it with
`searchsorted`. A held-out document is dropped when **more than 50%** of its
13-grams are in that array. The aggregate rate per subject is computed and
reported but never blocks.

**Halves.** `blake2b(f"{seed}:{doc_id}", digest_size=8) % 2` picks `label` or
`test`, so the assignment depends on nothing but the document id and the single
data seed (`20261102`) — not on order, not on counts. Each half is then walked
in source order and trimmed at the first document that reaches 2.5M tokens, so a
half lands in `[2.5M, 2.5M + 4096)` tokens.

---

## 4. Results

Read out of `data/v1/manifest.json` and `data/v1/reports/*.json` by
`python -m data.report_tables --config configs/data/v1.yaml`.

### 4.1 The run

| | |
|---|---|
|dataset|`monology/pile-uncopyrighted`|
|pinned revision|`3be90335b66f24456a5d6659d9c8d208c0357119`|
|training shard(s)|`train/00.jsonl.zst`|
|held-out shard(s)|`val.jsonl.zst`|
|fallback shards used|heldout: none, train: none|
|data seed|20261102|
|config fingerprint|`106869163e9dbb03`|
|tokenizer|GPT-2 (`tiktoken`), vocab 50,257|
|lines read, train / held-out|537,289 / 136,269|
|compressed bytes downloaded|1.27 GB|
|runtime, total|6.0 min|
|runtime, extract / dedup / split|122 s / 236 s / 4 s|
|output on disk|788 MB|

### 4.2 Training subjects: collected -> cleaned -> deduped

|subject|docs collected|tokens collected|docs in|dropped short/empty|dropped dup|docs kept|tokens kept|vs target|capped at 4096|
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
|`Pile-CC`|39,685|32,400,016|40,146|461|0|39,685|**32,399,981**|1.20x|1,432|
|`Github`|23,070|32,402,163|24,487|1,417|110|22,960|**32,274,915**|1.20x|3,318|
|`PubMed Central`|9,199|32,401,822|9,526|327|7|9,192|**32,373,390**|1.20x|6,896|
|`FreeLaw`|13,448|32,400,514|13,547|99|28|13,420|**32,368,917**|1.20x|4,404|
|`Wikipedia (en)`|50,162|32,400,907|51,279|1,117|127|50,035|**32,314,014**|1.20x|1,105|

Training target per subject: **27,000,000** tokens (18% of 150,000,000); collected 32,400,000 (+20% slack). Total training tokens from the Pile: **161,731,217**.

### 4.3 Held-out: collected -> cleaned -> deduped -> halves

|subject|docs collected|tokens collected|pool docs|pool tokens|label docs|label tokens|test docs|test tokens|
|---|---:|---:|---:|---:|---:|---:|---:|---:|
|`Pile-CC`|8,617|7,000,623|8,604|6,993,342|3,042|2,501,942|3,087|2,501,855|
|`Github`|5,178|7,001,241|4,458|6,171,662|1,762|2,500,326|1,815|2,502,662|
|`PubMed Central`|1,977|7,000,109|1,963|6,953,567|708|2,503,922|713|2,502,199|
|`FreeLaw`|2,914|7,002,443|2,594|6,729,670|943|2,501,133|995|2,502,989|
|`Wikipedia (en)`|10,699|7,000,178|10,507|6,972,161|3,822|2,500,790|3,687|2,500,584|
|`USPTO Backgrounds`|8,525|7,000,462|8,516|6,996,466|3,029|2,500,388|3,084|2,500,283|

Target: **5,000,000** tokens per subject, **2,500,000** per half, minimum **500** documents per half.

### 4.4 Dedup log — documents dropped per reason per subject

|split|subject|docs in|empty|< 50 tokens|exact dup (same split)|exact dup (cross split)|&gt;50% 13-gram|kept|
|---|---|---:|---:|---:|---:|---:|---:|---:|
|train|`FreeLaw`|13,547|0|99|28|0|0|13,420|
|train|`Github`|24,487|0|1,417|110|0|0|22,960|
|train|`Pile-CC`|40,146|0|461|0|0|0|39,685|
|train|`PubMed Central`|9,526|0|327|7|0|0|9,192|
|train|`Wikipedia (en)`|51,279|0|1,117|127|0|0|50,035|
|heldout|`FreeLaw`|2,936|0|22|1|8|311|2,594|
|heldout|`Github`|5,505|0|327|1|47|672|4,458|
|heldout|`Pile-CC`|8,710|0|93|0|0|13|8,604|
|heldout|`PubMed Central`|2,051|0|74|2|0|12|1,963|
|heldout|`USPTO Backgrounds`|8,596|0|71|9|0|0|8,516|
|heldout|`Wikipedia (en)`|10,935|0|236|6|0|186|10,507|

### 4.5 13-gram overlap, held-out vs. training text of the same subject

|subject|unique train 13-grams|held-out 13-grams|of those, in train|aggregate rate|mean / doc|median / doc|max / doc|docs dropped by the 50% rule|
|---|---:|---:|---:|---:|---:|---:|---:|---:|
|`Pile-CC`|30,818,919|6,897,211|51,323|**0.744%**|0.850%|0.000%|90.0%|13|
|`Github`|22,467,753|6,888,240|1,425,307|**20.692%**|21.040%|12.700%|100.0%|672|
|`PubMed Central`|30,670,380|6,968,395|233,127|**3.345%**|3.438%|1.787%|99.5%|12|
|`FreeLaw`|28,718,183|6,963,028|797,655|**11.456%**|16.890%|6.586%|99.5%|311|
|`Wikipedia (en)`|31,062,799|6,866,522|159,559|**2.324%**|6.195%|1.010%|86.5%|186|
|`USPTO Backgrounds`|0|6,894,274|0|**0.000%**|0.000%|0.000%|0.0%|0|

### 4.6 Disk

| | |
|---|---:|
|heldout|43.2 MB|
|heldout_pool|59.3 MB|
|raw|398.0 MB|
|total|787.8 MB|
|train|227.2 MB|
|work|60.0 MB|
|compressed downloaded|1.27 GB|
|free disk after the build|1843.2 GB|

### 4.7 Problems reported by the build

```json
{
  "fallback_files_used": {
    "heldout": [],
    "train": []
  },
  "heldout_below_min_docs": [],
  "heldout_below_target_tokens": [],
  "train_subjects_below_target": []
}
```

**Reading 4.2.** "docs collected" and "tokens collected" are what the extractor
budgeted; "docs in" is larger because documents that clean to under 50 tokens
are archived — so the dedup log can count them — but never counted toward the
budget. Every subject lands at **1.20x** its 27M target, which is the 20% slack
working exactly as specified; the tokenize stage cuts 32.4M down to 27M.

**Reading 4.5.** `max / doc` reaching ~100% for four subjects is expected: those
are the individual near-duplicate documents the 50% rule exists to remove, and
they are gone from the pool. The gap between `mean / doc` (16.9%) and
`median / doc` (6.6%) for `FreeLaw` says the same thing — a long tail of heavily
quoting opinions, not a uniformly contaminated subject.

**Timing.** 6.0 minutes end to end on this Mac: 122 s of streaming (96 s for
537,289 lines of `train/00`, 26 s for 136,269 lines of `val`), 236 s of cleaning
+ capping + dedup (pass A ~2 min over 177,718 documents, pass B 16–20 s per
subject), 4 s to cut the halves. 1.27 GB downloaded for a 788 MB output tree, of
which `_work/` (60 MB) is scratch and can be deleted.


---

## 5. The one real finding: `Github` and `FreeLaw` are partly self-overlapping

The aggregate 13-gram overlap between a subject's held-out text (from `val`) and
its own training text (from `train/00`) is near zero for `Pile-CC` (0.74%) and
low for `Wikipedia (en)` (2.3%) and `PubMed Central` (3.3%). It is **20.7% for
`Github`** and **11.5% for `FreeLaw`**, and the 50% rule dropped 13.1% of
`Github`'s held-out documents and 10.7% of `FreeLaw`'s.

This is not a bug in the pipeline and not contamination the Pile authors missed
in the usual sense — it is what those two domains look like:

- **`Github`**: license headers, `package.json`/lockfile boilerplate, generated
  bindings, vendored copies of the same library, and the same import blocks
  across thousands of files. Any two unrelated repositories share long literal
  runs.
- **`FreeLaw`**: fixed procedural language, citation formats and recited statute
  text. Opinions quote each other at length by design.

Two consequences worth carrying into the analysis:

1. **`Github` and `FreeLaw` held-out sets are smaller before trimming** (4,458
   and 2,594 pool documents vs. 8,604 for `Pile-CC`). Both still fill their
   2.5M-token halves comfortably, so nothing downstream changes — but the slack
   is thinner there, and a stricter threshold would start to bite. At 0.30
   instead of 0.50, `Github` would lose noticeably more.
2. **A per-document `ngram_overlap` field ships with every held-out document**,
   so the metrics code can filter harder than 0.50 without a rebuild. Whether it
   should is open question 4 in `docs/interfaces.md`.

`USPTO Backgrounds` has zero overlap by construction: it has no training text at
all, which is exactly its job as the phase-2 subject.

---

## 6. Reproducibility

The build is a pure function of the config. Evidence:

| check | result |
|---|---|
| 1% build, two runs from scratch, sha256 of all 40 non-JSON output files | **identical** |
| Full build, two runs from scratch (second one re-downloading and re-extracting), sha256 of all 40 non-JSON output files | **identical** |
| `tests/test_data_build.py::test_same_config_gives_byte_identical_output` | pass |
| `tests/test_data_build.py::test_gzip_outputs_carry_no_timestamp` | pass |

Three things make that hold, and all three are easy to get wrong:

- **gzip `mtime=0` everywhere.** A gzip header carries a timestamp; two runs a
  minute apart otherwise differ in byte 4 of every file. There is a test for it.
- **No `hash()` anywhere.** Python's string hash is seeded per process, so a
  13-gram index or a half assignment built on it changes between runs. Both use
  fixed-constant hashes (FNV-1a + splitmix64, blake2b).
- **JSON written with `sort_keys=True`** and fixed separators, so a dict
  insertion order change cannot alter a byte.

The one input that is not pinned by the config is the tokenizer's downloaded BPE
file; `tiktoken==0.14.0` is pinned in `requirements.txt` and the encoding's
`n_vocab` is asserted to be 50,257 at load.

Reports exclude `*.json` from the byte comparison on purpose: those carry
wall-clock timings.

---

## 7. Deviations, interpretations and open questions

Nothing in the fixed design turned out to be impossible. Five places needed a
judgement call, all recorded here:

1. **Document id format.** The prompt specified `"--<line_number>"`, which has
   two empty fields before the line number. Read as
   **`"<subject_slug>-<source_tag>-<line_number>"`** (`pile_cc-train00-128745`),
   which is stable across rebuilds and unique corpus-wide. **If the intended
   format was different, this is a one-line change in
   `DataConfig.doc_id` — but it changes every id, so it should be settled before
   the tokenize stage.**
2. **Held-out collection slack is 40%, not 20%.** The 20% slack was specified
   for the training target. For the held-out set the label/test assignment is a
   hash, so the two halves are only approximately equal; 20% left one half
   short at small scale. 40% makes both halves clear 2.5M with room. The
   held-out *targets* are unchanged.
3. **"Normalize whitespace runs (keep newlines)"** is implemented as: collapse
   horizontal runs inside a line, preserve leading indentation verbatim, strip
   trailing whitespace, collapse runs of more than two newlines to two, strip
   the document. The newline-run collapse goes slightly beyond "keep newlines";
   it is config-controlled (`clean.max_consecutive_newlines`) and setting it to
   `0` turns it off.
4. **The `--small` mode scales the 500-document minimum to 5.** At 1% of the
   token targets a half holds 6–60 documents, so an unscaled minimum could never
   pass and the flag's whole point is a fast green run. The full build enforces
   500, and it passed.
5. **Exact dedup is global, not per split.** The requirement was "within and
   across splits"; one global hash set also catches a document that appears
   under two different subjects, which is a superset and never keeps less.

Open questions, all also in `docs/interfaces.md` §3:

1. **Token file sharding** — one `train.bin` for 150M tokens, or one per
   subject? Per-subject makes "train on 4 of 5 subjects" a config change.
2. **Trimming 32.4M → 27M.** The training files hold target + slack. The
   tokenize stage has to pick which 27M; walking documents in source order until
   the budget is reached is the obvious choice and is what `split.py` already
   does for the held-out halves, but it should be an explicit decision.
3. **Should the held-out `ngram_overlap` threshold be tightenable** per
   experiment, or is the build-time 0.50 the final word?
4. **`docs/interfaces.md` §2** (the biography contract) is written but unbuilt.
   It needs the metrics owner's sign-off before `tools/bio_generator.py` is
   extended — in particular it asks for `gender`, `tier` and a `train`/`control`
   split that the current generator does not emit (it is deliberately
   pronoun-free), and for `facts.jsonl` rows carrying a `held_out_template`
   flag and a prompt prefix.

## 8. Problems hit along the way

- **A quadratic merge in the 13-gram index.** The first full run took **558
  seconds for one subject**: the index merged whenever the *total* accumulated
  hash count crossed 16M, so after the first merge every 256-document batch
  re-sorted the whole 30M-element base. Keeping a merged base separate from a
  pending list and merging only on the pending size brought it to **16–20
  seconds per subject** (a 28–35× speedup). Fixed in `df8b21f`.
- **Cleaning whole multi-megabyte documents.** Pass A peaked at **13.1 GB RSS**
  and took ~2 minutes per subject because every document was NFC-normalized,
  split into lines and rejoined in full, even though only the first 4,096 tokens
  can ever be kept. Cleaning a bounded prefix (with a fallback to the whole text
  if the prefix collapses below the cap's character bound — a mostly-whitespace
  document) gives identical output at **115 MB RSS** and ~24 seconds per
  subject. Same commit.
- **`.jsonl.gz` has two suffixes.** `Path.stem` on `train00-000000.jsonl.gz`
  leaves `train00-000000.jsonl`, which crashed the part-file sort at the end of
  the first extract. Caught by the `--small` run before any real time was spent.
- **Nothing was short.** `val` turned out to hold enough of all six subjects —
  136,269 of its lines covered 7M tokens each — so neither
  `train_fallback_files` nor `heldout_fallback_files` was ever opened. The
  fallback path is therefore **implemented and unexercised**; worth knowing if a
  later config asks for more than 7M held-out tokens per subject.
- **Disk was never a concern.** Free space moved 1,844.0 → 1,843.2 GB over the run. The 20 GB
  floor is checked at every stage boundary and every 100,000 lines of streaming;
  it never came close.

---

## 9. What ships

| path | what |
|---|---|
| `configs/data/v1.yaml` | every target, the subject list, the seed, the pinned revision, all paths |
| `docs/interfaces.md` | sections 1–2, **DRAFT** for the metrics owner |
| `data/pile_extract.py` | stage 1, resumable streaming extractor |
| `data/dedup.py` | stage 2, cleaning + cap + exact dedup + the 13-gram rule |
| `data/split.py` | stage 3, label/test halves |
| `data/build.py` | `python -m data.build --config … --stage pile [--small]` |
| `data/make_sample.py`, `data/report_tables.py` | the sample bundle and this report's tables |
| `data/v1_sample/` | **committed**, 7.4 MB, the 1% build + a README per file |
| `data/v1/` | not committed (788 MB); rebuild from the config |
| `tests/test_data_{clean,dedup,split,build}.py` | 36 tests, no network |
| `logs/data1_full.out`, `logs/data1_small.out` | console transcripts |

`python -m pytest` → **95 passed** (59 pre-existing + 36 new). Nothing in
`memlayers/`, `bench/` or `tools/` was touched.
