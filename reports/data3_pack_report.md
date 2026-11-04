# Data step 3 — packing, the manifest, fetch and the loader

> **Historical record of step 3.** Superseded numbers: the final data-v1
> figures are in [`reports/data5_fix_report.md`](data5_fix_report.md).

**Project:** What memory-layer values store and how they are organized (PKM / PEER vs. a kNN-LM store)
**Course:** COMS E6998 Algorithms in LLMs — final project
**Date:** 2026-11-02
**Machine:** Apple M5 Pro, 18 cores, 64 GiB, macOS 26.6.2, `.venv` Python 3.12.14
**Scope:** turn prompt 1's Pile text and prompt 2's biographies into the token
files training reads, plus the bundle manifest, the fetch command and the
loader. **Validation and the freeze are prompt 4.**

Every figure below is read out of the build's own JSON by
`python -m data.report_tables --config configs/data/v1.yaml --stage pack`.

```bash
python -m data.build --config configs/data/v1.yaml --stage pile   # text,    4 min
python -m data.bios  --config configs/data/v1.yaml                # people,   9 s
python -m data.pack  --config configs/data/v1.yaml                # tokens,  16 s
python -m data.manifest --config configs/data/v1.yaml             # manifest, 2 s
python -m data.fetch --version v1 --verify-only                   # verify,  0.2 s
python bench/check_pack_invariants.py                             # the real build
python bench/smoke_real_data.py --config memlayers/configs/t1_pkm.yaml \
    --steps 300 --micro-batch-size 32                             # 7 min
python -m pytest                                                  # 160 tests
```

---

## 1. Headline

- **`train.bin`: 149,963,776 tokens = 292,898 sequences of 512**, uint16. Each of
  the five Pile subjects is **exactly 27,000,000 tokens** — not approximately —
  and biographies are 14,631,457 (9.76%).
- **Zero of the 190,000 biography copies crosses a 512-token boundary.** The
  no-split rule cost 1,129,480 tokens of Pile text pulled forward as filler
  (0.75% of the file) and moved 28,856 copies to the next sequence. No subject
  gained a token doing it.
- **Worst 1M-token window deviation: 0.433 points** against a 2-point tolerance,
  across 595 overlapping windows. That needed a deficit-greedy interleave; a
  seeded shuffle of the same items is about four times noisier (§3.2).
- **Byte-identical rebuilds** of `train.bin`, both held-out files *and* the
  manifest. Getting the manifest there meant taking wall clocks out of the
  bundle entirely (§3.4) — found by the new pre-step-0 verification refusing to
  start a run.
- **Smoke run works end to end:** T1-pkm, 300 steps on real data, loss
  **10.83 → 6.26**, with per-subject held-out loss on the test half (§5).
- **Biographies can never reach `data/dedup.py`'s 13-gram rule** — an explicit
  exemption, checked before the n-gram index is even built, with a test that
  shows the rule really would fire without it.

---

## 2. Results

Read out of `data/v1/reports/pack_report.json` and `data/v1/manifest.json`.

### 2.1 The run

| | |
|---|---|
|config fingerprint (pack scope)|`f7adf5f6fefc545d`|
|data seed|20261102|
|block size / EOT|512 / 50256|
|runtime, pack|17 s|
|git commit|`74a6727b98d0`|
|Pile revision|`3be90335b66f`|

### 2.2 train.bin

|subject|documents used|available|index segments|tokens|share of train.bin|
|---|---:|---:|---:|---:|---:|
|`Pile-CC`|33,255|39,685|41,605|**27,000,000**|18.004%|
|`Github`|19,190|22,960|24,136|**27,000,000**|18.004%|
|`PubMed Central`|7,666|9,192|9,882|**27,000,000**|18.004%|
|`FreeLaw`|11,245|13,420|14,453|**27,000,000**|18.004%|
|`Wikipedia (en)`|41,891|50,035|51,972|**27,000,000**|18.004%|
|`bio`|8,000|-|190,000|**14,631,457**|9.757%|
|**total**|||**332,048**|**149,963,776**|100%|

**292,898** sequences of 512. 1,129,480 tokens of Pile text were pulled forward to fill the tail of a sequence so a biography would not be split (28,856 copies moved); 272 EOT tokens pad the final sequence. Every subject lands on exactly 27,000,000 tokens.

### 2.3 Window shares, worst deviation per subject

|subject|target share|worst window share|worst deviation (pts)|at token|windows checked|
|---|---:|---:|---:|---:|---:|
|`FreeLaw`|18.044%|17.624%|**0.421**|29,750,000|595|
|`Github`|18.044%|18.478%|**0.433**|27,500,000|595|
|`Pile-CC`|18.044%|17.613%|**0.432**|135,750,000|595|
|`PubMed Central`|18.044%|18.471%|**0.426**|15,000,000|595|
|`Wikipedia (en)`|18.044%|17.640%|**0.404**|1,000,000|595|
|`bio`|9.778%|9.628%|**0.150**|88,000,000|595|

Windows of 1,000,000 tokens at a stride of 250,000, so they overlap and a deviation cannot hide on a tile boundary. Tolerance 2 points.

### 2.4 Biography copies per tier

|tier|people|copies each|copies|tokens|
|---|---:|---:|---:|---:|
|`frequent`|300|300|90,000|6,914,700|
|`normal`|700|100|70,000|5,403,625|
|`rare`|1,000|30|30,000|2,313,132|
|`control`|500|0|0|0|
|**total**|2,500||**190,000**|**14,631,457**|

### 2.5 Held-out files

|file|tokens|documents|size|
|---|---:|---:|---:|
|`heldout/label.bin`|15,021,806|13,306|30.0 MB|
|`heldout/test.bin`|15,023,952|13,381|30.0 MB|

|subject|label docs|label tokens|test docs|test tokens|
|---|---:|---:|---:|---:|
|`Pile-CC`|3,042|2,501,942|3,087|2,501,855|
|`Github`|1,762|2,500,326|1,815|2,502,662|
|`PubMed Central`|708|2,503,922|713|2,502,199|
|`FreeLaw`|943|2,501,133|995|2,502,989|
|`Wikipedia (en)`|3,822|2,500,790|3,687|2,500,584|
|`USPTO Backgrounds`|3,029|2,500,388|3,084|2,500,283|

### 2.6 The bundle

|prefix|files|bytes|
|---|---:|---:|
|`bios/`|7|56.5 MB|
|`heldout/`|16|103.7 MB|
|`heldout_pool/`|6|59.3 MB|
|`raw/`|12|398.0 MB|
|`reports/`|5|0.0 MB|
|`samples/`|1|0.2 MB|
|`tokens/`|2|303.0 MB|
|`train/`|5|227.2 MB|
|**total**|**54**|**1,148.0 MB**|
|**without `raw/`**||**750.0 MB**|

---

## 3. The four things that were easy to get wrong

### 3.1 "Exactly 27M" has to survive the no-split rule

Two requirements pull against each other: every subject contributes exactly
27,000,000 tokens, *and* a biography copy is never split across a sequence
boundary. The second needs filler whenever a copy does not fit in the tail of
the current sequence — 28,856 times here — and filler taken from anywhere else
would push a subject past its 27M.

So the filler is **Pile text pulled forward out of the stream**: the writer takes
a prefix of the next not-yet-written Pile document, and when that document's own
turn comes it writes only the remainder. Nothing is invented and nothing is
duplicated; tokens just arrive earlier than the interleave planned. Subject
totals are therefore still exact, which the tests assert directly.

The cost is that a Pile document can reach the file in two non-adjacent pieces.
That is why the index carries an extra `doc_offset` column: without it a
consumer holding a segment cannot tell which part of the document it has.
`doc_offset` is additive — all six columns the design fixes are present and
unchanged — and it is what makes the "decode a segment back to its source"
check possible at all.

### 3.2 A seeded shuffle does not balance a 1M-token window

The design asks for every 1M-token window to hold each subject and the
biographies within 2 points of their shares. A seeded shuffle of the items will
not do it. The items are wildly uneven — a PubMed Central document averages
3,500 tokens, a biography 77 — so in a 1M window a subject's token count is a
sum of about 90 heavy draws, and its share has a standard deviation around 1.7
points. Against a 2-point limit over 595 windows, that fails somewhere with near
certainty.

The interleave is **deficit-greedy** instead: always emit from the stream
furthest below `share × tokens_placed_so_far`. After an emit, that stream is
below target by at most the single item it just placed, so the cumulative error
never exceeds one item length (≤ 4,096 tokens) and a window's share error never
exceeds two of them — 0.82 points at a 1M window, by construction rather than by
luck. Measured worst case: **0.433 points**.

`tests/test_data_pack.py::test_deficit_greedy_beats_a_shuffle_on_window_balance`
builds both orders over the same items and asserts the greedy one is at least
twice as good, so the reason for the choice is in the test suite rather than
only in this paragraph.

### 3.3 The space the loader must not waste

A 512-token sequence has 512 inputs but only 511 of its own next-token targets:
the last token has nothing after it inside the sequence. Reading `x` and `y` from
the same 512 tokens throws away one target in 512 and, worse, trains the model
to predict a token that is sometimes the start of an unrelated document.

The loader reads a **513-token window** instead: `x = tokens[s*512 : s*512+512]`,
`y` the same window shifted by one, so the last target is the first token of the
next sequence. The final sequence is dropped when the file has no 513th token
for it, which is why `train.bin` holds 292,898 sequences and the loader serves
292,897.

### 3.4 Nothing in a hash-verified bundle may carry a wall clock

The manifest hashes every file in `data/v1/`. Each stage report carried a
`seconds` field, so a rebuild that produced identical data produced a different
`pack_report.json`, a different hash, and a different manifest — and
"rebuilding gives a byte-identical manifest" could never hold.

This surfaced the right way: the first attempt at the smoke run **refused to
start**, because the pre-step-0 verification compared the bundle against the
committed manifest and found `reports/pack_report.json` had moved. The check
earning its keep before any training happened is the point of having it.

Runtimes now go to `data/v1/reports/timings.json`, the one bundle path the
manifest skips by name, and the manifest dropped its own `created_utc` and
`seconds`. Everything else in the bundle is a pure function of the config.

---

## 4. Reproducibility

| check | result |
|---|---|
| `train.bin`, both held-out `.bin`s and both indexes, rebuilt from scratch | **byte-identical** (6 files) |
| `manifest.json` after re-running pack + bios + sample + manifest | **byte-identical** |
| `data.fetch --version v1 --verify-only` on the real build | **42/42 files OK**, 12 skipped as optional |
| `bench/check_pack_invariants.py` on the real 150M-token build | **all pass** |
| `python -m pytest` | **160 passed** |

The full invariant list, run on the real article rather than a fixture:

```
train.bin 149,963,776 tokens, 292,898 sequences, 332,048 index rows
OK  every subject is exactly 27,000,000 tokens      (bio: 14,631,457)
OK  dtype uint16, max id 50256 < 50257
OK  0 of 190,000 biography copies cross a 512 boundary
    Pile segments that do cross (allowed): 82,558
OK  index tiles the file; all 332,319 uncovered tokens are EOT
OK  worst window deviation 0.433 pts <= 2.0
OK  every person's copies match the tier and the 4-rewording spread
OK  1,000 random segments decode to the source exactly (829 whole documents)
OK  heldout/label.bin 15,021,806 tokens, 13,306 docs, max doc 4,096, 6 subjects, no biographies
OK  heldout/test.bin  15,023,952 tokens, 13,381 docs, max doc 4,096, 6 subjects, no biographies
```

The strongest of those is the tiling one, and it is worth saying why it is
airtight: `encode_ordinary` never emits a special token, so `50256` cannot occur
inside a document. Therefore "every token not covered by an index segment is
`50256`, and no covered token is" pins the tiling, the separators and the tail
padding in a single assertion — there is nowhere for an off-by-one to hide.

**Config fingerprints are now scoped three ways** (`pile`, `bios`, `pack`), and
the test that checks them reads expected values out of the committed manifest
rather than from literals, so it stays true by rebuilding rather than by editing
a test. Note that adding `dedup.ngram_exempt_subjects` *did* move the pile
fingerprint (`106869163e9dbb03` → `3f4303d9b926b730`) because `dedup` is a
pile-stage section. The pile stage was re-run; all 34 of its output files came
back byte-identical, so `reports/data1_pile_report.md`'s numbers all still hold —
only the fingerprint it quotes is superseded.

One honest wrinkle about `data/manifests/v1.json`: it records the git commit it
was built at, which is necessarily an ancestor of the commit that contains the
manifest itself. Prompt 4 should rebuild it as the last act of the freeze so the
recorded commit is the tagged one.

---

## 5. Smoke run: T1-pkm, 300 steps, real data

`bench/smoke_real_data.py`, micro-batch 32, MPS, `bench/results/smoke_real_t1_pkm.json`.

| step | loss |
|---:|---:|
| 0 | **10.8269** |
| 100 | **6.6262** |
| 200 | **6.1960** |
| 300 | **6.3370** |
| mean of the last 20 steps | 6.2603 |

Step 0 at 10.8269 is the sanity check that matters: `ln(50257) = 10.8249`, so an
untrained model on real text sits exactly at the uniform-guess level. 300 steps
is 4,915,200 tokens — **3.3% of one epoch** — in 433 s at 13,200 tok/s, which
matches the 13,440 tok/s the step-1 report measured for this config on fake data,
so the memmapped loader costs nothing measurable.

Per-subject loss on the **test** half, evaluated per document so a window never
spans two documents or two subjects (≤ 200 documents per subject):

| subject | held-out loss | documents | tokens |
|---|---:|---:|---:|
| `Github` | **5.7371** | 200 | 280,630 |
| `FreeLaw` | **5.8735** | 200 | 538,632 |
| `PubMed Central` | **6.5792** | 200 | 696,058 |
| `Pile-CC` | **6.7886** | 200 | 166,385 |
| `USPTO Backgrounds` | **7.0021** | 200 | 163,834 |
| `Wikipedia (en)` | **7.0163** | 200 | 125,951 |

**Do not read these as learning yet.** At 3.3% of an epoch the ordering tracks
how repetitive a domain is, not how much the model has stored: Github and
FreeLaw are full of boilerplate and score best, while `Wikipedia (en)` — which
*is* in training — scores level with `USPTO Backgrounds`, which never appears in
training at all. The number these exist to produce is the trained-vs-held-out
gap in step 4, and USPTO's value is that it is the only subject whose loss cannot
contain any memorisation. All the plumbing works; the comparison is not due yet.

---

## 6. What could not be followed as written

Nothing in the fixed design turned out to be impossible. Five places needed a
judgement call, in the same spirit as the date-token problem in prompt 2:

1. **Held-out file names.** The design says
   `data/v1/heldout/_{label,test}.bin`, which has an empty field before the
   half — the same kind of lost placeholder as prompt 1's document id. Read as
   **`data/v1/heldout/label.bin` and `heldout/test.bin`**, one file per half
   holding all six subjects, with `subject` in the index so a per-subject loss
   is a filter rather than a file. This supersedes `docs/interfaces.md` §1.4's
   earlier `heldout_<half>_<slug>.bin` spec, which would have meant twelve files;
   the doc is updated in this pull request.
2. **`person_id` for Pile rows is null, not `-1`.** The design says "`person_id`
   and `rewording_id` (biographies only, else -1)". `rewording_id` is an int32
   and is `-1`. `person_id` is a string column, where `-1` would be a magic
   string; it is null, which is also what the prompt-1 interface draft promised.
3. **The index has one extra column, `doc_offset`** (§3.1). All six fixed columns
   are present and unchanged.
4. **`data/v1/manifest.json` changed owner.** The design assigns that path to the
   bundle manifest; prompt 1 had written the pile-stage manifest there. The pile
   stage's record moved to `reports/pile_manifest.json` and the bundle manifest
   embeds its counts. `data/make_sample.py` and `data/report_tables.py` were
   updated with it.
5. **`hf_repo` is `"<owner>/memlayers-data"`.** The design gives the value as
   `"/memlayers-data"`, with the account missing. Left as an explicit
   `<owner>` placeholder, as instructed; `data.fetch` refuses to download while
   it is unfilled and names the three local build commands instead, so the
   failure is a sentence rather than a 404.

### Also worth flagging

- **150M is 149,963,776.** Five exact 27M subjects plus 14,631,457 biography
  tokens is 149,631,457; EOT separators (332,047) and 272 tokens of tail padding
  bring the file to 149,963,776, which is 512-aligned. The 0.02% shortfall
  against a round 150M is separators, and separators are tokens the model trains
  on, so the figure in the manifest is the honest one.
- **Biography copies are placed, not sampled.** Each trained person gets exactly
  its tier's count spread `[8, 8, 7, 7]`-style over its four rewordings — the
  remainder always going to the lowest-numbered rewordings — so a person's
  exposure is a function of its tier alone, with no sampling variance to control
  for later. This answers open question 1 from prompt 2.
- **The whole stream is one epoch.** 292,897 sequences at micro-batch 32 is 9,153
  steps; the tier-1 plan is longer than that, so the loader draws a fresh
  permutation per epoch keyed by `(seed, epoch)` and `position` keeps counting
  across the boundary. There is a test for the wrap.

### Open questions

1. **Should `bio` get its own `.bin`?** Biographies are interleaved into
   `train.bin`, which is what the design asks for and what training needs. But
   the slot-attribution work will want to run *only* biography prompts through
   the model, and `facts.jsonl` gives it those as text. If the metrics code would
   rather have them pre-tokenized, that is a small addition — the design says
   explicitly not to, so it was not done.
2. **One `train.bin` or one per subject?** Still open from prompt 1, and now
   concrete: "train on 4 of 5 subjects" currently means a rebuild (16 s, so
   cheap) rather than a config change.
3. **Control-people rewordings are still not in any `.bin`.** They exist in
   `bios/bios_control.jsonl` and in `facts.jsonl`. Prompt 2 flagged this; the
   packer leaves them out of both `train.bin` (correct — they must never be
   trained on) and the held-out files (a choice: they are synthetic, and the
   held-out files are for per-subject language-modelling loss).
4. **Held-out evaluation is per document, capped at 200 documents per subject**
   in the smoke script. Prompt 4 should decide the real protocol: all 13,381
   documents, or a seeded sample, and whether to weight by token or by document.

---

## 7. What ships

| path | what |
|---|---|
| `configs/data/v1.yaml` | gains `pack` and `distribution` sections, and `dedup.ngram_exempt_subjects: ["bio"]` |
| `data/pack.py` | selection, copies, interleave, packing, held-out files |
| `data/loader.py` | memmapped `(B, 512)` batches, seeded order, resumable |
| `data/manifest.py` | the bundle manifest + the committed copy |
| `data/fetch.py` | download/verify, and the offline verifier |
| `data/dedup.py` | the biography exemption |
| `data/common.py` | the `pack` fingerprint scope, `keyed_rng`, `record_timing` |
| `data/report_tables.py` | gains `--stage pack`, which produced §2 |
| `memlayers/train.py` | `data.source: fake \| real`, verification before step 0, provenance in the checkpoint and the CSV |
| `bench/check_pack_invariants.py` | every invariant, on the real build |
| `bench/smoke_real_data.py` | the 300-step run and the per-subject held-out loss |
| `data/manifests/v1.json` | **committed**, 16 KB — the hash authority |
| `docs/interfaces.md` | §1.4–1.6 rewritten, new §3 on reading the data |
| `tests/test_data_pack.py` | 18 tests |
| `tests/test_data_loader.py` | 12 tests |
| `tests/test_data_fetch.py` | 12 tests |
| `tests/test_data_dedup.py` | 11 tests (+2 for the exemption) |
| `tests/test_train.py` | 18 tests (+5 for real data) |
| *removed* | nothing |

`data/v1/` is 1,148.0 MB (750.0 MB without `raw/`) and is not committed.
