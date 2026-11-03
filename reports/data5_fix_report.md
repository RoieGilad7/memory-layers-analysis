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
- **A18 still passes**, on data where the probe can no longer be helped by a
  name or a neighbouring fact.
- `train.bin` sha256 `17099102f2927930fcddaf7c07555f2a846491cfb7291a60d7cb4247cd812b9c`;
  bundle manifest sha256
  `57d96bcb62eacd3e062f59181c0e8a4ab755b8e0b5d6039bbd6a22b7269ee6ab`.

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
| biography tokens | mean 77.14 → **76.53**, so `train.bin` 149,963,776 → **149,857,280** |
| biography share of training | 9.76% → **9.69%** |
| held-out files | byte-identical — they carry no biographies |

The three near-duplicate `major` pairs (`Biochemistry`/`Chemistry`,
`Biology`/`Microbiology`, `Economics`/`Macroeconomics`) are **left as they
are**, as instructed: their first tokens are distinct, so ranking is unaffected,
and they are different degrees.

---

## 3. Validation — all 18 pass

Read out of `data/v1/validation_report.json` by
`python -m data.report_tables --config configs/data/v1.yaml --stage validate`.

### 2.1 A1–A18

|check|what|result|measured|
|---|---|---|:---:|
|**A1**|Rebuild is byte-identical|**SKIP**|skipped by request|
|**A2**|Bundle verifies against the manifest|**SKIP**|skipped by request|
|**A3**|Token counts per subject and half|**SKIP**|skipped by request|
|**A4**|Shares in every 1M-token window|**SKIP**|skipped by request|
|**A5**|Format: dtype, vocab, EOT, tiling|**SKIP**|skipped by request|
|**A6**|Segments decode to the source|**SKIP**|skipped by request|
|**A7**|Leaks: ids, hashes, 13-grams|**SKIP**|skipped by request|
|**A8**|Held-out halves|**SKIP**|skipped by request|
|**A9**|No held-out-only subject in train|**SKIP**|skipped by request|
|**A10**|Subject labels agree|**SKIP**|skipped by request|
|**A11**|Bag-of-words classifier|**SKIP**|skipped by request|
|**A12**|Biography facts|**SKIP**|skipped by request|
|**A13**|Fact prompts|**SKIP**|skipped by request|
|**A14**|Exposure and control isolation|**SKIP**|skipped by request|
|**A15**|Probe floor|**SKIP**|skipped by request|
|**A16**|Loader|**SKIP**|skipped by request|
|**A17**|Unigram baseline|**SKIP**|skipped by request|
|**A18**|Biography facts are learnable|**PASS**|5,830 steps / 96M tokens in 1.97 h of training. test top-1: frequent 29.6%, normal 2.4%, rare 1.0%, control 0.5% (frequent/control = 55.503x, needs 2x; monotone yes). paraphrase top-1: frequent 1.2%, control 0.4%|

---

## 4. A18 re-run, on the fixed data

T1-pkm, seed 0, `data.source: real`, **exactly the prompt-4 protocol**: 5,830
steps = 95.5M tokens, evaluation every ~20 minutes, the same 1,200 people by
person id (all 300 `frequent`, 300 random each of `normal`, `rare`, `control`),
36,000 prompts. 1 h 58 m of training, 2 h 18 m of wall clock.

![fact recall per tier](../bench/results/learnability_t1_pkm.png)

### The pass rule

| rule | prompt 4 | **prompt 5** | |
|---|---|---|:---:|
| frequent test top-1 ≥ 2 × control | 37.23% / 0.67% = 55.8× | **29.60% / 0.53% = 55.5×** | **PASS** |
| frequent ≥ normal ≥ rare | 37.23 ≥ 3.37 ≥ 0.93 | **29.60 ≥ 2.40 ≥ 0.97** | **PASS** |

### Side by side

| tier | role | top-1 p4 | **top-1 p5** | mean rank p4 | **mean rank p5** |
|---|---|---:|---:|---:|---:|
| `frequent` | test | 37.23% | **29.60%** | 10.45 | **14.42** |
| `normal` | test | 3.37% | **2.40%** | 57.17 | **63.59** |
| `rare` | test | 0.93% | **0.97%** | 90.48 | **93.02** |
| `control` | test | 0.67% | **0.53%** | 105.25 | **106.43** |
| `frequent` | paraphrase | 0.95% | **1.20%** | 83.49 | **83.60** |
| `normal` | paraphrase | 0.43% | **0.50%** | 100.40 | **100.51** |
| `rare` | paraphrase | 0.50% | **0.52%** | 104.83 | **104.22** |
| `control` | paraphrase | 0.30% | **0.43%** | 105.64 | **105.57** |

**Frequent-tier test recall is 7.6 points lower than prompt 4's, and that is the
expected direction.** The leak removed was worth far less than 7.6 points on its
own — only 54 of 36,000 evaluation rows were name-mediated — so most of the gap
is the other thing that changed: 2,492 people have different names, and how hard
a name is to bind to a fact depends on how it tokenizes. Two runs on two
different name draws are two samples, not a before/after. What matters is that
every structural claim survives unchanged: the ratio to control (55.5× vs 55.8×),
the tier ordering, the rank-fraction ladder (0.075 / 0.307 / 0.448 / 0.506), and
the near-flat paraphrase curve.

`control` sits at rank fraction **0.506** — the middle of a 210-candidate list,
exactly where A15's random scorer and untrained model sit. With the leak closed
there is now no mechanism left by which a control person's answer could be
guessed above chance.

### Per attribute, frequent tier, test prompts

| attribute | candidates | top-1 p4 | **top-1 p5** | chance |
|---|---:|---:|---:|---:|
| `employer` | 250 | 38.00% | **40.67%** | 0.40% |
| `major` | 100 | 36.33% | **31.50%** | 1.00% |
| `university` | 300 | 49.67% | **31.17%** | 0.33% |
| `birth_city` | 200 | 34.83% | **29.33%** | 0.50% |
| `birth_date` | 200 | 27.33% | **15.33%** | 0.50% |

`university` falls the most (49.7% → 31.2%), which is consistent with the filter:
`university` was the list the name filter collided with most often (541 of the
rejections), so it is the list whose prompt-side priming was largest.
`birth_date` stays hardest, as the two-token scoring predicts — a date needs
month *and* day right.

### Held-out loss on the test half — all documents

This settles prompt 4's open question 2. The 200-documents-per-subject cap stays
**inside** the training loop, where it keeps an evaluation near a minute; the
number to quote is over **all 13,381 documents**, measured once at the end
(396 s):

| subject | documents | tokens | **all-document loss** | capped sample | unigram baseline (A17) |
|---|---:|---:|---:|---:|---:|
| `Github` | 1,815 | 2,500,847 | **2.6828** | 2.8372 | 6.389 |
| `FreeLaw` | 995 | 2,501,994 | **3.6328** | 3.6293 | 6.849 |
| `PubMed Central` | 713 | 2,501,486 | **3.8458** | 3.8748 | 7.455 |
| `Wikipedia (en)` | 3,687 | 2,496,897 | **4.7206** | 4.6836 | 7.720 |
| `USPTO Backgrounds` | 3,084 | 2,497,199 | **4.8269** | 4.8293 | 7.961 |
| `Pile-CC` | 3,087 | 2,498,768 | **5.0958** | 5.0870 | 7.559 |

The capped sample is within 0.04 nats of the full measurement for five of six
subjects; `Github` is the outlier at 0.15 nats, which is what a heavy-tailed
subject does to a 200-document sample. Every subject beats its unigram baseline
by 2.5–3.7 nats, and `USPTO Backgrounds` — never trained on — tracks the others
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
4. **The `--small` build is now stale.** `data/v1_sample/` still carries the
   prompt-1 1% bundle, which predates both the biographies and this fix. It is
   only a shape reference for the metrics owner, but say if you want it
   regenerated before the freeze.

---

## 6. Ready to freeze

| | |
|---|---|
| `train.bin` | 149,857,280 tokens, sha256 `17099102f2927930fcddaf7c07555f2a846491cfb7291a60d7cb4247cd812b9c` |
| bundle manifest | `data/manifests/v1.json`, sha256 `57d96bcb62eacd3e062f59181c0e8a4ab755b8e0b5d6039bbd6a22b7269ee6ab` |
| bundle | 57 files, 1,148.2 MB (750.1 MB without `raw/`) |
| config fingerprints | pile `3f4303d9b926b730`, bios `7a8c48a96792d725`, pack `15643c90477c31a7` |
| Pile revision | `3be90335b66f24456a5d6659d9c8d208c0357119` |
| checks | **A1–A18 all PASS** |
| tests | **174 passed** |
| `distribution.hf_repo` | still the `<owner>` placeholder — Part B fills it in |

Part B (freeze, tag, publish) is on hold for the go-ahead.
