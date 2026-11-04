# Data step 5 — closing the answer leak, and the final build

**Project:** What memory-layer values store and how they are organized (PKM / PEER vs. a kNN-LM store)
**Course:** COMS E6998 Algorithms in LLMs — final project
**Date:** 2026-11-03
**Machine:** Apple M5 Pro, 18 cores, 64 GiB, macOS 26.6.2, `.venv` Python 3.12.14
**Scope:** fix the answer leak that failed A13 in prompt 4, rebuild, re-validate,
and re-run the learnability check on the fixed data. **Part A only — nothing is
frozen, tagged or uploaded.**

```bash
python -m data.bios      --config configs/data/v1.yaml   # 11 s
python -m data.pack      --config configs/data/v1.yaml   # 16 s
python -m data.manifest  --config configs/data/v1.yaml
python -m data.hand_samples --config configs/data/v1.yaml
python -m data.validate  --config configs/data/v1.yaml   # A1-A18, 6 min
python bench/learnability_run.py --steps 5830 --eval-every 972   # A18, 2h20
python -m pytest                                         # 174 tests
```

---

## 1. Headline

**All 18 checks pass.** A13 was the one failure in prompt 4; it is now clean and
enforced.

| leak channel, over all 100,000 `facts.jsonl` rows | prompt 4 | **prompt 5** |
|---|---:|---:|
| the true value appears verbatim in its own prompt | 8 | **0** |
| the value's ranking key appears in the person's own name | 54 | **0** |
| the key appears inside another of the person's values | 35 | **0** |
| the key is a **template word** (reported, not failed) | 25 | 26 |

- **Person ids did not move.** Ids, tiers, exposures, gender and split are
  identical for all 2,500 people, exactly as you said they would be — names and
  facts are keyed by person id, and names are the first survivors in draw order.
  2,492 people got a different name; **6 people had one fact redrawn**.
- **A18 still passes** on data where the probe can no longer be helped by a
  name or a neighbouring fact — **frequent 32.20% vs control 0.60%, 53.7×**,
  and monotone across tiers. Three runs side by side in §4.
- **All 120 sentence templates were rewritten** (§7) after a review found that
  85 of 100 used the same interrupting appositive, five split a verb from its
  object, and four said "every year on *March 4, 1987*".
- `train.bin` sha256 `47441d9c3889d802793dcea51ca125c65787dab72eb6aa916cd8b545caaedbf8`;
  bundle `data_sha256`
  `3357ec6b6e81cf7f30bb9ae14c6a25793a95642d90f146a08aa71d5db53870e1`.

---

## 2. What changed

### 2.1 The name filter

A candidate name is now rejected — **in the same place the Pile name check
rejects**, before people are assigned — when its first or last word would hand a
fact-recall probe one of its answers:

- **(a) whole word.** The name word, lowercased, is a word of the value.
  `Charlotte Vadnais` against `Charlotte, North Carolina`.
- **(b) ranking key.** The GPT-2 token of `" word"` or of `"word"` is the
  value's ranking key — its first token, or **either of the first two** for a
  date. `Keiko Schreiber` against `Keio University`, where `" Keiko"` and
  `" Keio"` share the token `" Ke"`.

It is **global across every list**, not just the person's own facts, because the
model reads every biography: a surname that primes another person's city is the
same leak one step removed.

| | candidates | rejected | female | male | by whole word | by ranking key |
|---|---:|---:|---:|---:|---:|---:|
| value-collision filter | 5,200 | **1,930 (37.1%)** | 1,083 | 847 | 519 | 1,411 |
| Pile name check (unchanged rule) | 5,200 | 230 | — | — | — | — |

Rejections by the list they collided with: `university` 541, `birth_city` 344,
`employer` 226, `birth_date` 13 (over the 3,000-candidate sample measured before
the pool was raised).

**`bios.people.name_candidates_per_gender`: 1,500 → 2,600.** At 37% rejection,
1,500 candidates left only 861 female survivors against the 1,250 needed.
Raising it is safe because the draw is a single RNG stream per gender, so a
larger number only *appends*: the first 1,500 per gender are byte-identical.
`test_raising_the_candidate_pool_only_appends` pins that.

### 2.2 The same-person channel

Prompt 4 found 114 rows where a value's ranking key appeared somewhere in its
prompt. 54 came from the person's name — closed by §2.1. The remaining 60 split
two ways, and I had to look to find out which:

**35 rows: another fact of the same person.** Every rewording puts all five
values in one paragraph in a random order, so if one value's key sits inside
another value's tokens, whichever comes second has its answer in the prompt. Six
people, and the collisions are exactly what you would guess:

| person | attribute redrawn | was | clashed with | now |
|---|---|---|---|---|
| `p000182` | `university` | Ohio State University | `birth_city` Columbus, **Ohio** | Harvard University |
| `p000479` | `university` | Korea University | `birth_city` Seoul, South **Korea** | Vassar College |
| `p000945` | `employer` | **Liberty** Mutual | `university` **Liberty** University | Union Pacific |
| `p001213` | `university` | **Pepper**dine University | `employer` Keurig Dr **Pepper** | Thermo Fisher Scientific |
| `p001457` | `university` | **Lin**field University | `birth_city` **Lin**z, Austria | Regis University |
| `p001927` | `university` | **York** University | `birth_city` Syracuse, New **York** | Cairo University |

The redraw is keyed by `(seed, "facts", person_id, attribute, attempt)`, so one
person's collision cannot disturb anybody else's facts — and the check runs in
**both** directions, because the order of the two values in a paragraph is
random.

**26 rows: template wording. Not fixed, by instruction.** Two employer values,
and the collision is with the frame rather than with anything about the person:

| value | ranking key | where the key already appears | rows |
|---|---|---|---:|
| `Heineken` | `" He"` | the pronoun **He**/His, in every male biography | 16 |
| `Asahi Breweries` | `" As"` | the held-out frame "**As** for the employer, …" | 10 |

Changing templates is out of scope and dropping two employer values would shrink
the list, so these are reported. They are 0.026% of rows and both are in the
`employer` list of 250, so a metrics owner who wants them gone can drop two
values rather than rebuild.

### 2.3 A13 now enforces this

A13 **fails** on any row with (i) the value verbatim in its prompt, (ii) the
ranking key in the person's name, or (iii) the ranking key inside another of the
person's values. Template-word hits are reported as an observation. Six new unit
tests cover the filter, the redraw and its keying, the pool's append-only
property, and an end-to-end small build with all three criteria at zero.

### 2.4 What the rebuild moved

| | |
|---|---|
| person ids | **identical**, all 2,500 |
| gender, split, tier, target exposures | **identical** for every person |
| names changed | **2,492** of 2,500 (99.7%) — a rejection shifts the candidate cut-off, so nearly everyone takes the next surviving name |
| facts changed | **6** of 2,500 people, one attribute each |
| biography tokens | mean 77.14 → 76.53 → **77.11** after the template rewrite (§7); `train.bin` 149,963,776 → **149,896,192** |
| biography share of training | 9.76% → 9.69% → **9.71%** |
| held-out files | byte-identical — they carry no biographies |

The three near-duplicate `major` pairs (`Biochemistry`/`Chemistry`,
`Biology`/`Microbiology`, `Economics`/`Macroeconomics`) are **left as they
are**, as instructed: their first tokens are distinct, so ranking is unaffected,
and they are different degrees.

---

## 3. Validation — all 18 pass

Read out of `data/v1/validation_report.json` by
`python -m data.report_tables --config configs/data/v1.yaml --stage validate`.

### 3.1 A1–A18

|check|what|result|measured|
|---|---|---|:---:|
|**A1**|Rebuild is byte-identical|**PASS**|58 files hashed; 0 changed, 0 added, 0 removed|
|**A2**|`data.fetch --verify-only` passes|**PASS**|58/58 files verified against v1.json (0 mismatched, 0 missing)|
|**A3**|Token counts per subject and half|**PASS**|every Pile subject exactly 27,000,000 in train.bin; every held-out half within 1% of 2,500,000 per subject|
|**A4**|Shares in every 1,000,000-token window|**PASS**|worst deviation 0.425 points across 596 overlapping windows (stride 250,000), tolerance 2.0|
|**A5**|Format: dtype, vocab bound, EOT, index tiling|**PASS**|train.bin: 149,896,192 tokens, 332,017 segments, 332,328 EOT separator/pad tokens, max id 50256 \| label.bin: 15,021,806 tokens, 13,306 segments, 13,305 EOT separator/pad tokens, max id 50256 \| test.bin: 15,023,952 tokens, 13,381 segments, 13,380 EOT separator/pad tokens, max id 50256|
|**A6**|Decoding index segments reproduces the source|**PASS**|1,000 random segments checked token for token (825 of them whole documents, also compared as text); 0 mismatches|
|**A7**|Leaks: ids, exact hashes, 13-gram overlap|**PASS**|ids disjoint across train/label/test; 0 exact-hash matches; 0 documents over 50%; worst single document 50.0%; aggregates Pile-CC=0.64%, Github=14.35%, PubMed=2.93%, FreeLaw=9.21%, Wikipedia=2.14%, USPTO=0.00%|
|**A8**|Halves: disjoint, >=500 docs, <=4096 tokens|**PASS**|halves share 0 documents; smallest half/subject is 708 documents (minimum 500); longest document 4096 tokens (cap 4096)|
|**A9**|No held-out-only subject in train.bin|**PASS**|['USPTO Backgrounds'] appear in 0 train.bin segments by document id and 0 by subject label; train.bin carries ['FreeLaw', 'Github', 'Pile-CC', 'PubMed Central', 'Wikipedia (en)', 'bio']|
|**A10**|Subject labels agree with the source|**PASS**|142,017 Pile segments: index subject == raw-archive meta.pile_set_name == the document id's slug; 190,000 biography segments all labelled `bio` with a known person id|
|**A11**|Bag-of-words subject classifier (sanity)|**PASS**|accuracy 94.87% on 13,381 test-half documents (threshold 90%); per subject Pile-CC=89.7%, Github=97.8%, PubMed=97.6%, FreeLaw=99.1%, Wikipedia=95.0%, USPTO=96.2%|
|**A12**|Biography facts|**PASS**|2,500 people, names unique and absent from the Pile, genders {'female': 1250, 'male': 1250}, 5 facts each; first-token uniqueness holds per list (first two for birth_date, which has only 12 distinct first tokens); chi-square p birth_date=0.124, birth_city=0.877, university=0.183, major=0.940, employer=0.347|
|**A13**|Fact prompts: no answer leaks|**PASS**|100,000 rows: **0** leak the value verbatim (0), **0** via the person's name (0), **0** via another of the person's values (0); 50,000 training prompts are exact prefixes of their biography; 50,000 paraphrase prompts, 200 of them searched in full against train.bin and absent; held-out markers inside biography text: 'Question:'=0, 'When it comes to'=0, 'is on record as'=0, 'reads as follows'=0 (the same markers occur 570 times in ordinary Pile text, which is not a leak); REPORTED: 48 rows whose ranking key is a TEMPLATE word (birth_city=Thessaloniki, Greece, employer=Heineken, major=Theology, university=Aalborg University)|
|**A14**|Exposure counts and control isolation|**PASS**|190,000 copies over 2,000 trained people, every count equal to its tier target and spread over the 4 rewordings; 0 cross a 512-token boundary; 0 of 500 control names appear in train text|
|**A15**|Probe floor: random and untrained sit mid-list|**PASS**|random scorer: mean rank fraction 0.502, top-1 0.558% over 36,000 prompts; untrained model: 0.500, top-1 0.625% over 4,000; mean candidate list 210|
|**A16**|Loader: order, resume, shapes|**PASS**|292,765 sequences of 512; same seed reproduces the order, a different seed does not, the order is a permutation, and a resume from (seed, position) matches an unbroken run|
|**A17**|Model beats the per-subject unigram baseline|**PASS**|Pile-CC: model 6.7886 vs unigram 7.559; Github: model 5.7371 vs unigram 6.3888; PubMed: model 6.5792 vs unigram 7.4554; FreeLaw: model 5.8735 vs unigram 6.8493; Wikipedia: model 7.0163 vs unigram 7.72; USPTO: model 7.0021 vs unigram 7.9605|
|**A18**|Biography facts are learnable|**PASS**|5,830 steps / 96M tokens in 2.00 h of training. test top-1: frequent 32.2%, normal 2.5%, rare 0.7%, control 0.6% (frequent/control = 53.667x, needs 2x; monotone yes). paraphrase top-1: frequent 1.2%, control 0.4%|

### 3.2 A11 confusion matrix — 94.87% on 13,381 test-half documents

Rows are the true subject, columns the bag-of-words classifier's guess.

|true \\ predicted|Pile-CC|Github|PubMed Central|FreeLaw|Wikipedia (en)|USPTO Backgrounds|recall|
|---|---:|---:|---:|---:|---:|---:|---:|
|**Pile-CC**|**2,769**|14|29|18|210|47|89.7%|
|**Github**|13|**1,775**|22|2|2|1|97.8%|
|**PubMed Central**|12|2|**696**|·|3|·|97.6%|
|**FreeLaw**|4|3|·|**986**|·|2|99.1%|
|**Wikipedia (en)**|86|3|40|9|**3,503**|46|95.0%|
|**USPTO Backgrounds**|25|·|91|·|2|**2,966**|96.2%|

### 3.3 A17 per-subject unigram baseline

|subject|prompt-3 smoke loss|unigram cross-entropy|margin|test tokens|unigram counts from|
|---|---:|---:|---:|---:|---|
|`FreeLaw`|5.8735|6.8493|**0.976**|2,502,989|own training text|
|`Github`|5.7371|6.3888|**0.652**|2,502,662|own training text|
|`Pile-CC`|6.7886|7.559|**0.770**|2,501,855|own training text|
|`PubMed Central`|6.5792|7.4554|**0.876**|2,502,199|own training text|
|`USPTO Backgrounds`|7.0021|7.9605|**0.958**|2,500,283|pooled 5 subjects|
|`Wikipedia (en)`|7.0163|7.72|**0.704**|2,500,584|own training text|
---

## 4. A18, three runs side by side

Same protocol every time: T1-pkm, seed 0, `data.source: real`, 5,830 steps =
95.5M tokens, evaluation every ~20 minutes, **the same 1,200 people by person
id** (all 300 `frequent`, 300 random each of `normal`, `rare`, `control`) and
the same 36,000 prompts. Person ids never moved, so run 3 evaluates exactly the
people runs 1 and 2 did.

| run | data | verdict | train time |
|---|---|:---:|---:|
| **1** | prompt 4 — before the leak fix | PASS | 1.98 h |
| **2** | prompt 5 — leak fixed, old templates | PASS | 1.97 h |
| **3** | prompt 5 — leak fixed, **rewritten templates** | **PASS** | 2.00 h |

![fact recall per tier](../bench/results/learnability_t1_pkm.png)

### The pass rule

| rule | run 1 | run 2 | **run 3** | |
|---|---|---|---|:---:|
| frequent test top-1 ≥ 2 × control | 55.8× | 55.5× | **53.7×** | **PASS** |
| frequent ≥ normal ≥ rare | 37.23 ≥ 3.37 ≥ 0.93 | 29.60 ≥ 2.40 ≥ 0.97 | **32.20 ≥ 2.50 ≥ 0.70** | **PASS** |

### Test prompts (rewordings 2–3)

| tier | top-1 run 1 | top-1 run 2 | **top-1 run 3** | rank 1 | rank 2 | **rank 3** |
|---|---:|---:|---:|---:|---:|---:|
| `frequent` | 37.233% | 29.600% | **32.200%** | 10.45 | 14.42 | **13.12** |
| `normal` | 3.367% | 2.400% | **2.500%** | 57.17 | 63.59 | **59.88** |
| `rare` | 0.933% | 0.967% | **0.700%** | 90.48 | 93.02 | **90.59** |
| `control` | 0.667% | 0.533% | **0.600%** | 105.25 | 106.43 | **104.90** |

Mean rank is out of a candidate list averaging 210, so `control` at **104.90**
is the middle of the list — exactly where A15's random scorer and untrained
model sit, and where a person the model has never seen must sit.

### Paraphrase prompts (held-out templates)

| tier | top-1 run 1 | top-1 run 2 | **top-1 run 3** | rank 1 | rank 2 | **rank 3** |
|---|---:|---:|---:|---:|---:|---:|
| `frequent` | 0.950% | 1.200% | **1.167%** | 83.49 | 83.60 | **82.12** |
| `normal` | 0.433% | 0.500% | **0.433%** | 100.40 | 100.51 | **99.11** |
| `rare` | 0.500% | 0.517% | **0.483%** | 104.83 | 104.22 | **102.71** |
| `control` | 0.300% | 0.433% | **0.367%** | 105.64 | 105.57 | **105.91** |

Unchanged across all three runs, and still the interesting negative: the fact
is demonstrably *in there* — frequent paraphrase mean rank 82.1 against the
control's 105.9 — but a structurally new wording recovers it as the top-1 answer
barely more than 1% of the time. The rewritten held-out frames did not move
this, which is worth knowing: it is a property of the exposure budget, not of
how the four frames happened to be phrased.

### Frequent tier, test prompts, per attribute

| attribute | candidates | run 1 | run 2 | **run 3** |
|---|---:|---:|---:|---:|
| `employer` | 250 | 38.00% | 40.67% | **48.00%** |
| `university` | 300 | 49.67% | 31.17% | **43.00%** |
| `major` | 100 | 36.33% | 31.50% | **27.00%** |
| `birth_city` | 200 | 34.83% | 29.33% | **26.33%** |
| `birth_date` | 200 | 27.33% | 15.33% | **16.67%** |

`birth_date` is consistently hardest, as the two-token scoring predicts: a date
only counts when month *and* day are both right.

### How to read the differences between runs

**Do not read run-to-run differences as effects.** Each run draws a different
set of 2,500 names (the stricter filter in run 2, the same filter in run 3), and
run 3 also rewrites every sentence frame. How hard a name is to bind to a fact
depends on how it tokenizes, so the three runs are three samples, not a
controlled series. The per-attribute column shows the noise plainly:
`university` goes 49.7 → 31.2 → 43.0 with nothing about `university` changing
between runs 2 and 3 except the wording of its twenty sentences.

What is stable across all three, and is the actual result:

- frequent-tier recall is **50× or more** the control floor, every time;
- the tier ordering holds every time;
- the rank-fraction ladder is monotone every time
  (run 3: 0.063 / 0.288 / 0.435 / 0.502);
- `control` sits at the middle of the candidate list every time;
- paraphrase recall stays near the floor every time.

### Held-out loss on the test half — all documents

Run 3 measures every one of the 13,381 test-half documents at the final
checkpoint (402 s), which is the number to quote. Runs 1 and 2 used the
200-per-subject cap that stays inside the training loop.

| subject | run 1 (capped) | run 2 (capped) | **run 3 (all docs)** | run 3 (capped) | documents |
|---|---:|---:|---:|---:|---:|
| `Github` | 2.8389 | 2.8372 | **2.6820** | 2.8338 | 1,815 |
| `FreeLaw` | 3.6311 | 3.6293 | **3.6294** | 3.6245 | 995 |
| `PubMed Central` | 3.8749 | 3.8748 | **3.8360** | 3.8634 | 713 |
| `Wikipedia (en)` | 4.6865 | 4.6836 | **4.7194** | 4.6820 | 3,687 |
| `USPTO Backgrounds` | 4.8195 | 4.8293 | **4.8162** | 4.8197 | 3,084 |
| `Pile-CC` | 5.0869 | 5.0870 | **5.0916** | 5.0831 | 3,087 |

The capped sample lands within 0.04 nats of the full measurement for five of six
subjects; `Github` is the outlier at 0.15, which is what a heavy-tailed subject
does to a 200-document sample. Every subject beats its A17 unigram baseline by
2.5–3.7 nats, and `USPTO Backgrounds` — never trained on — tracks the others
down.
---

## 5. What could not be followed as written

Nothing was impossible. Three notes:

1. **26 template-word rows remain, by instruction.** §2.2 lists them. They are
   not a name or a fact collision; the ranking key of `Heineken` is `" He"`,
   which is the male pronoun, and of `Asahi Breweries` is `" As"`, which opens a
   held-out frame. The design says not to change templates, so they stand.
   Dropping those two values from the 250-strong `employer` list would close
   them without touching anything else, if the metrics owner would rather.
2. **2,492 of 2,500 people changed name,** which is more churn than "a stricter
   filter only renames some people" suggests. The reason is mechanical: names
   are the first survivors in draw order, so rejecting 37% of candidates shifts
   the cut-off and nearly everyone inherits the next surviving name. Nothing
   *about* a person changed — ids, tier, exposures, gender, split and (for all
   but six) facts are identical, so this is a relabelling, not a new population.
   The hand-check pack was regenerated to match.
3. **A17 still compares against the prompt-3 smoke run.** The Pile side of
   `train.bin` is unchanged (same documents, same selection), so the per-subject
   unigram baselines are identical and the comparison still holds. The sharper
   numbers are in §4 — the full-test-half losses from the A18 run, which are the
   ones to quote from now on.

### Open questions

1. **Prompt 4's open question 2 is settled** (§4): the in-loop cap stays at 200
   documents per subject to keep an evaluation near a minute; the number quoted
   for a result is the all-document one.
2. **Paraphrase recall is still close to the floor.** Unchanged as a finding
   from prompt 4, and now measured on data where no name can prime it. The
   exposure budget is the lever, and that is a training-plan decision.
3. **Two employer values carry a template-word ranking key** (§2.2, note 1).
   Drop them or keep them — a metrics decision, not a data one.
4. **`data/v1_sample/` has been regenerated** from the current build, so it now
   carries the biographies, the fix and the rewritten templates (§6).

---

## 6. `data/v1_sample/` regenerated, and two bugs it exposed

The committed 1% sample predated both the biographies and this fix, so it was
rebuilt from the current code: all four `--small` stages, then
`python -m data.make_sample`. **48 files, 8.1 MB**, and it now carries
`tokens/`, `bios/`, the held-out `.bin`s and the hand-check pack — the whole
shape of the real bundle.

It deliberately mirrors **what `data.fetch` gives you by default**, so `raw/`
is left out (`--with-raw` includes it): a rebuild needs the archived source
text, and you cannot rebuild from a 1% sample anyway. The sample carries its own
recounted `manifest.json` and **verifies against it, 46/46 files**, so the
metrics owner can check their copy the same way they would check the real one.

Building it turned up two defects in code that was already committed:

**`bios/manifest.json` was not hash-protected.** The manifest's exclusion list
matched on the bare filename, so the root `manifest.json` *and* the bios stage's
own record were both skipped. The bios record is a genuine bundle file. The rule
now matches on the relative path, which brings the bundle from 57 to 58 hashed
files and moves `data_sha256` — `train.bin` is untouched, as §7 records.
Caught by the sample listing its files next to its manifest's, not by any test;
there is a test now.

**`--small` verified against the full manifest.** `data.manifest --small` writes
`v1_small.json`, but `data.fetch` always looked for `v1.json`, so A2 on a small
build compared a 1% bundle against the full one and reported 56 of 57 files
mismatched. Both now go through one `manifest_path()` helper. This is why A2
failed on the sample build before the fix.

`bios.people.name_candidates_per_gender` also needed a floor for `--small`: 1%
of 2,600 is 26 candidates, and the two name filters reject ~45% between them, so
a 1% build could not fill its own 28 people. The floor is 200 and never binds at
full scale, so the real build is unaffected — same fingerprints, same tokens.

### Where 1% scale genuinely changes the answer

Three checks fail on the sample and should: held-out halves land ±12% off their
token budget instead of ±1% (A3) because a 1% pool is 20–130 documents;
chi-square cannot judge uniformity with 28 people against 200 values (A12's own
guard refuses, expected count 0.1); and exposure counts are deliberately not
scaled, so biographies are 11.8% of the sample's tokens against 9.7% in the full
build. The sample's README says all of this. Everything else — exact per-subject
budgets, the 512-boundary rule, index tiling, **no answer leaks in any prompt**,
per-person exposure counts — holds at 1% exactly as it does at full scale.

---

## 7. The templates were rewritten

A read-through of all 120 rendered sentences found the biography text was
grammatical but not natural, and the fault was systematic rather than scattered.

| | before | after |
|---|---:|---:|
| interrupting-comma asides | **85/100** | **16/100** |
| verb/object splits | 5 | **0** |
| "birthday … every year on *March 4, 1987*" | 4 | **0** |
| contradictions across a person's four rewordings | 8 | **0** |
| British/US spelling mixing | 4 | **0** |
| openers: person / possessive / other | 87/13/0 | **45/34/21** |
| shortest frame | 4 tokens | **9 tokens** |

The cause was mine: prompt 2 needed ~11 tokens of frame per sentence to hit the
token budget and bought the length by inserting commas instead of restructuring
sentences. Five sentences drawn from five such pools read like a parody, and
85% of biography sentences sharing one syntactic signature makes biography text
trivially separable from Pile text — a confound sitting directly on top of the
question the memory layer is meant to answer.

Four review passes were needed. The third caught a class the first two missed:
reading all four rewordings of one person *together* exposed incidental details
that contradict — a home birth in one copy and a hospital birth in another, six
years at an employer in one and eleven in another, four years at university in
one and five in another. A reviewer sees all four side by side in
`bios_review.md`, so those are now neutralised. The fourth pass caught a grammar
error introduced during the rewrite ("first drew breath **into** a noisy room").

Two held-out frames were also replaced — "X **is a person whose** date of birth
we have on file as" and "As for the date of birth, **in X's case that would
be**" — neither of which anyone would write. The markers moved with them, which
removed the `" As"` collision that had been giving `Asahi Breweries` ten free
rows.

**The cost was a different kind of template-word overlap.** Natural English
opens sentences with "The" and "A", and those are the ranking keys of
`Theology`, `Thessaloniki, Greece` and `Aalborg University`. Sentence-initial
"The" went from 15 templates to 3, which brought the count from 87 down to
**48 rows (0.048%)**, against 26 in the old set. The remaining seven article
openers are sentences like *"An accent gives her away as someone from Lyon,
France"*; removing those to chase 48 rows would make the corpus less natural,
which is the opposite of the goal. Per the design these are reported, not
failed. Dropping three values would close it in one line, if the metrics owner
would rather have that than the openers.

Two latent bugs surfaced: `PERSON_PLACEHOLDERS` never contained `{subj}`, the
mid-sentence subject `mention()` has always provided, so a template using it
looked like it had no person placeholder at all; and `check_templates` now
asserts every template opens with a capital or a sentence-initial placeholder,
since sentences are joined with a space.

Token budget held: frame mean 10.70 → 10.89, biography mean 77.1 tokens,
biographies **9.71%** of the 150M training budget.

---

## 8. Ready to freeze

| | |
|---|---|
| `train.bin` | 149,896,192 tokens / 292,766 sequences, sha256 `47441d9c3889d802793dcea51ca125c65787dab72eb6aa916cd8b545caaedbf8` |
| bundle `data_sha256` | `3357ec6b6e81cf7f30bb9ae14c6a25793a95642d90f146a08aa71d5db53870e1` — the freeze hash, over the file list alone |
| bundle | 58 files, 1,149.3 MB (751.3 MB without `raw/`) |
| config fingerprints | pile `3f4303d9b926b730`, bios `7a8c48a96792d725`, pack `15643c90477c31a7` |
| Pile revision | `3be90335b66f24456a5d6659d9c8d208c0357119` |
| checks | **A1–A18 all PASS** |
| tests | **179 passed** |
| `distribution.hf_repo` | still the `<owner>` placeholder — Part B fills it in |

**On the freeze hash.** Earlier drafts of this report quoted a bundle manifest
sha256 of `e91883d8dd3bf0b77749eab3e43ea736654631de058e94f05c6f8920db97a39f`:
the sha256 of the whole `data/manifests/v1.json`, which embeds
`git: {branch, commit, dirty}`. That made the bundle's identity move on every
commit, including commits that touched no data, and it did — by the time this
line was written the committed manifest hashed to `7ab876aa...` instead. The
identifying hash is now `data_sha256`, taken over the manifest's `files` list
alone in canonical JSON, so it tracks the data and nothing else. The `git` block
stays in the manifest as information, outside the hash.

The A18 learnability run in §4 trained on `train.bin` sha256 `47441d9c3889d802793dcea51ca125c65787dab72eb6aa916cd8b545caaedbf8` — the same
tokens this bundle holds now — so its result stands unchanged.

Part B (freeze, tag, publish) is on hold for the go-ahead, and reports
`data_sha256` as the freeze hash.
