# Data step 2 — the made-up biographies

**Project:** What memory-layer values store and how they are organized (PKM / PEER vs. a kNN-LM store)
**Course:** COMS E6998 Algorithms in LLMs — final project
**Date:** 2026-11-02
**Machine:** Apple M5 Pro, 18 cores, 64 GiB, macOS 26.6.2, `.venv` Python 3.12.14
**Scope:** the biography generator and its fact list. Tokenizing, packing into
`train.bin` and the loader are prompt 3. **No token files were written.**

Every figure below is read out of the build's own JSON by
`python -m data.report_tables --config configs/data/v1.yaml --stage bios`.

```bash
python -m data.bios --config configs/data/v1.yaml                 # 9 s + 23 s name scan
python -m data.bios_sample --config configs/data/v1.yaml --n 20    # hand-review sample
python -m pytest tests/test_bios.py                                # 26 tests, no network
```

---

## 1. Headline

- **2,500 people**: 2,000 trained + 500 control, exactly 1,250 female / 1,250
  male, and exactly gender-balanced *inside every tier* — not balanced on
  average, balanced by construction (§3.1).
- **100,000 fact rows**: 25,000 `discovery`, 25,000 `test`, 50,000 `paraphrase`.
- **14.65M biography tokens** implied by the tier exposure targets —
  **9.77%** of the 150M training budget against a 10% target.
- **The Pile name check bites**: 135 of 3,000 candidate names already occur in
  prompt 1's cleaned Pile text, and 123 people were rejected because of it. A
  generator without this check would have put "David Roberts" and "Bernard Hill"
  into the training set with invented facts.
- **One thing in the fixed design is arithmetically impossible** and was not
  done as written: 200 dates cannot have 200 distinct *first* GPT-2 tokens,
  because a date written "March 4, 1987" starts with one of only twelve month
  tokens. Dates are unique on their first **two** tokens instead. Everything
  else holds. Details in §6.

---

## 2. Results

Read out of `data/v1/bios/manifest.json` and `attribute_values.json`.

### 2.1 The run

| | |
|---|---|
|config fingerprint (bios scope)|`f0bc53d072987382`|
|data seed|20261102|
|people|2,500|
|facts.jsonl rows|100,000|
|biography rows|10,000|
|runtime|9 s|

### 2.2 People by split, tier and gender

|tier|split|exposures each|people|female|male|biography copies|
|---|---|---:|---:|---:|---:|---:|
|`rare`|train|30|1,000|500|500|30,000|
|`normal`|train|100|700|350|350|70,000|
|`frequent`|train|300|300|150|150|90,000|
|`control`|control|0|500|250|250|0|
|**total**|||**2,500**|**1,250**|**1,250**|**190,000**|

### 2.3 Value lists

|attribute|candidates|dropped near-dup|dropped prefix clash|trimmed to target|final|target|distinct first tokens|unique on|mean tokens/value|
|---|---:|---:|---:|---:|---:|---:|---:|---|---:|
|`birth_date`|200|0|0|0|**200**|200|12|first 2 tokens|4.0|
|`birth_city`|246|0|19|27|**200**|200|200|first token|3.69|
|`university`|373|5|38|30|**300**|300|300|first token|3.14|
|`major`|127|11|12|4|**100**|100|100|first token|1.91|
|`employer`|430|0|45|135|**250**|250|250|first token|2.41|

### 2.4 Templates

|attribute|training templates|held-out templates|distinct pre-value contexts (train)|(held-out)|
|---|---:|---:|---:|---:|
|`birth_date`|20|4|20|4|
|`birth_city`|20|4|20|4|
|`university`|20|4|20|4|
|`major`|20|4|20|4|
|`employer`|20|4|20|4|

### 2.5 facts.jsonl rows

|role|rows|
|---|---:|
|`discovery`|25,000|
|`paraphrase`|50,000|
|`test`|25,000|
|**total**|**100,000**|

### 2.6 Token budget

| | |
|---|---:|
|biography tokens, mean|77.14|
|biography tokens, range|60-99|
|trained-people mean|77.1|
|biography copies at the tier targets|190,000|
|**implied biography tokens**|**14,648,240**|
|share of the training budget|**9.77%** of 150,000,000 (target 10%)|

### 2.7 The Pile name check

| | |
|---|---:|
|files scanned|11|
|documents scanned|171,934|
|characters scanned|775 M|
|candidate names tested|3,000|
|case sensitive|True|
|candidate names found in the Pile|**135**|
|names actually rejected (inside the per-gender cut-off)|**123**|

First 12 rejected names: `Aaron Vincent`, `Adam Torres`, `Ana Gomes`, `Andre Bernard`, `Angela Wade`, `Benedict Rogers`, `Bernard Hill`, `Bertram Lawrence`, `Bradley Ray`, `Brandon Barnes`, `Brian Matthews`, `Bruce Barnes`.

**Reading 2.3.** Three filters run in order and each is reported separately:
near-duplicates (one value's identity words nesting inside another's), then
first-token clashes, then a seeded trim down to the config target. `employer`
gives up the most to the trim (135) simply because the candidate list was
generous; `university` gives up the most to clashes (38) because so many real
institution names begin with the same word. The `major` near-duplicate drops are
all containments — `History` inside `Art History`, `Biology` inside `Marine
Biology` — which would make a one-shot answer ambiguous.

**Reading 2.6.** The exposure plan is 1,000 x 30 + 700 x 100 + 300 x 300 =
190,000 biography copies. At 77.1 tokens per biography that is 14.65M tokens,
9.77% of the 150M budget. Biography *length* was the free variable here: the
exposure counts and the 10% share are both fixed, so the templates had to be
written to a length that makes the two consistent. A first draft of terser
templates averaged 48.7 tokens and would have delivered only 9.3M (6.2%); the
templates were lengthened and then trimmed back to land on 77.

---

## 3. How it works, and the four things that were easy to get wrong

### 3.1 Tiers that are exactly balanced, not balanced on average

Assigning a tier and a gender independently at random gives balance only in
expectation; at 300 people in the `frequent` tier the gender split would wobble
by tens. Instead the generator builds the full list of (split, tier) slots per
gender — 500 `rare`, 350 `normal`, 150 `frequent`, 250 `control` — shuffles
*that* with the data seed, and deals it out. The assignment is random, and the
counts in table 2.2 are exact rather than close.

Config counts are kept divisible by the number of genders, including under
`--small`, where `700 * 0.01 = 7` would otherwise make a balanced split
impossible. `--small` rounds each tier up to the next even number.

### 3.2 The space before a value belongs to the value

A value's first GPT-2 token is `" March"`, not `"March"` — the space is part of
the token. So a prompt that ends with a space would feed the model token 220 and
make the intended continuation unreachable; the fact would look unrecalled no
matter what the model knows. The fixed design says the prompt runs "up to (not
including) the value", which taken literally leaves that trailing space in the
prompt, and also says the value's first token is computed "with the leading
space as it appears after the template" — the two cannot both hold.

Resolved by splitting the string three ways, so nothing is ambiguous:

| field | value |
|---|---|
| `prompt` | `...Ethan Doherty marks a birthday, cake and all, every year on` |
| `continuation` | `" March 16, 1954"` — leading space included |
| `true_value` | `"March 16, 1954"` |
| `value_token_ids` | `encode_ordinary(continuation)` |

`prompt + continuation` is the biography prefix character for character, and
`value_token_ids[0]` is the first-token-unique quantity the value lists were
filtered on. Tested both ways in `test_training_prompts_are_exact_prefixes_of_their_biography`.

### 3.3 A held-out template has to be a new structure, not a new synonym

"Held-out templates test whether the model knows the fact or only the wording"
only works if the held-out wording is genuinely new. It is easy to write four
"paraphrases" that still end `... employer is {v}`, which 10 of the 20 training
templates also do — then the paraphrase row tests almost nothing.

So `data/bios_data.py` computes `pre_value_context(template)`, the three words
immediately before the value slot, and `check_templates()` asserts at import
that **no held-out template shares a pre-value context with any training
template of the same attribute**. Table 2.4 shows all 20 training contexts
distinct and all 4 held-out ones distinct from them. The four held-out frames
are structural rather than lexical:

| frame | example (employer) | marker |
|---|---|---|
| question / answer | `Question: for which organisation does Yvette Uribe work? Answer: Swiss Re.` | `Question:` |
| topicalization | `As for the employer, in Yvette Uribe's case that would be Swiss Re.` | `As for` |
| relative clause | `Yvette Uribe is a person whose employer we have on file as Swiss Re.` | `is a person whose` |
| record line | `Yvette Uribe's profile reads as follows -- current employer: Swiss Re.` | `reads as follows` |

Each marker occurs in no training template, so "did held-out wording leak into
training text" is one substring search over `bios_train.jsonl` — which is exactly
what `test_held_out_template_wording_never_enters_training_text` does.

### 3.4 The name check, in one pass

Every candidate full name has to be absent from prompt 1's cleaned Pile text:
775M characters across 171,934 documents. Testing 3,000 substrings against that
is 2.3 trillion character comparisons. But a candidate name is always two
capitalized words with exactly one space between them, so one pass finds every
capitalized word with `[A-Z][A-Za-z]+`, keeps the pairs that are adjacent with a
single space, and looks each pair up in a set — **23 seconds**, and exact.

Candidates are generated *before* the check and 20% longer than needed (1,500
per gender for 1,250), and the people are the first survivors in draw order. A
rejection therefore shifts the cut-off instead of changing anybody else's facts,
which is what keeps the output stable.

---

## 4. Reproducibility

| check | result |
|---|---|
| Two builds from the same config, sha256 of `people.jsonl`, `facts.jsonl`, `bios_train.jsonl`, `bios_control.jsonl`, `attribute_values.json`, `templates.json`, `name_check.json` | **identical** |
| Full 2,500-person build run three times from scratch, including the 775M-character name scan | **all 7 files identical** |
| `bios_sample.md` after a rebuild | **identical** (the sample writer is seeded too) |
| A different seed moves all four data files | **yes** (`templates.json` is seed-independent by construction) |
| `tests/test_bios.py` | **26 passed** |
| Whole suite | **110 passed** = 46 (step 1, after the old generator's 13 went) + 38 (data prompt 1) + 26 (new) |

Determinism comes from the same three habits as prompt 1 — gzip `mtime=0`,
`sort_keys` JSON, no `hash()` anywhere — plus one that is specific to this
generator: **every person's draws come from an RNG keyed by `(seed, person_id)`**
rather than from one stream walked in order. So a person's facts, templates and
sentence ordering do not depend on how many people were generated before them,
and adding a person or changing the count does not reshuffle everyone else.

Config fingerprints are now **stage-scoped** (`cfg.fingerprint("pile")` /
`("bios")`). Without that, adding the `bios` section to `configs/data/v1.yaml`
would have changed the one global fingerprint and told `pile_extract` its 1.27 GB
archive was stale. The pile scope is defined as "the config without the `bios`
section", which is byte-for-byte the dict prompt 1 hashed, so the
`106869163e9dbb03` recorded in `reports/data1_pile_report.md` still holds. There
is a test for it.

---

## 5. Hand review

`data/v1/samples/bios_sample.md` (committed, 158 KB) has 20 people — 16 trained
across all three tiers, 4 control — with all four rewordings, all 20 training
fact prompts and all 20 held-out prompts each. It is the only generated text a
pull-request reviewer can read, which is why it is the one thing under
`data/v1/` that is not gitignored.

What to check when reading it, and what the tests already check mechanically:

| property | in the sample | test |
|---|---|---|
| pronouns agree with `gender` | visible | `test_pronouns_match_the_gender_field` |
| first sentence names the person, later ones mix name and pronoun | visible | `test_first_sentence_names_the_person_and_later_ones_mix` |
| all five values verbatim in every rewording | visible | `test_every_rewording_carries_all_five_values_verbatim` |
| each prompt stops immediately before its value | the `continuation` column | `test_training_prompts_are_exact_prefixes_of_their_biography` |
| the four paraphrase prompts are structurally unlike the rewordings | visible | `test_held_out_template_wording_never_enters_training_text` |
| a person's four rewordings use four different templates per attribute | visible | `test_a_persons_four_rewordings_use_four_different_templates` |

One sample biography, for the record (`p001058`, control, female):

> Yvette Uribe's family lived for three generations in Cork, Ireland. Yvette
> Uribe's field of study, settled on late, was Management Science. Yvette Uribe
> holds a position, created specially, at Swiss Re. Her birthday, still
> celebrated yearly, is October 18, 1949. Yvette Uribe took a degree, slowly, at
> Whittier College.

---

## 6. What could not be followed as written

**200 dates cannot have 200 distinct first GPT-2 tokens.** The fixed design asks
for "a fixed list of 200 dates (written like `March 4, 1987`)" and, separately,
that "every value's FIRST GPT-2 token ... must be unique within its list". A
date in that format begins with a month name, there are twelve of them, and
`" March"` is a single token. So at most **twelve** dates can have distinct first
tokens — the two requirements are incompatible, and no amount of dropping or
swapping values fixes it.

No surface form rescues it either: `"4 March 1987"` leads with a day number (31
possible) and putting the year first abandons the specified format.

What was done instead, and why it is the smallest departure:

- the 200 dates are generated with **unique (month, day) pairs** — 372 exist, so
  200 is comfortable — which makes every date identifiable from its **first two**
  tokens, `(" March", " 4")`;
- the requirement is recorded in the config as a per-attribute choice,
  `values.first_token_unique` vs `values.first_two_tokens_unique`, so the
  distinction is data rather than a hidden special case;
- `attribute_values.json` reports `distinct_first_tokens: 12` for `birth_date`
  alongside `first_two_tokens_unique: true`, so nothing is papered over;
- the other four lists satisfy strict first-token uniqueness, exactly as asked.

**The practical consequence for the metric.** Scoring a date by its single next
token measures only the month. Anything reading `facts.jsonl` must score dates on
`value_token_ids` as a sequence (or at least the first two), while the other four
attributes can be scored on one token. Alternatives, if the metrics owner would
rather keep one rule for all five attributes: shrink the date list to 12 (one per
month, costing a factor of 16 in guess-rate) or drop `birth_date` and run on four
attributes. **Both are worse than scoring two tokens**, which is why the list of
200 was kept.

### Interpretations worth flagging (not deviations)

1. **"About 30 exposures" is exactly 30.** Exposure is constant within a tier,
   so `target_exposures` is derivable from `tier`; it is stored per person anyway
   because the schema asks for it and because prompt 3 may need to adjust it per
   person when it places copies. Three sharply separated levels are better for
   the analysis than three fuzzy ones.
2. **Templates are drawn without replacement** across a person's four
   rewordings, so each of the four copies of a fact is worded differently. The
   design says "draw one template per attribute" without saying whether repeats
   are allowed; distinct is strictly more informative.
3. **The held-out biography reuses rewording 0's other four sentences.** Only the
   target attribute's sentence is swapped, so the one new thing in a paraphrase
   row is one sentence's structure.
4. **Biography length was chosen to close the budget**, as described in §2.
5. **`facts.jsonl` carries three extra fields** beyond the fixed list —
   `fact_id`, `continuation`, `value_token_ids`, `doc_id` — all promised by the
   prompt-1 interface draft and all cheap. `docs/interfaces.md` §2 was rewritten
   in this pull request to match what was actually built; the five places where
   the draft disagreed with the generator are listed at the top of that section.

### Open questions for prompt 3 and the metrics owner

1. **How do 30 / 100 / 300 copies spread over 4 rewordings?** Round-robin keeps
   every wording equally represented (7–8 copies each at `rare`); sampling makes
   the per-wording count a random variable. This is prompt 3's call and it
   affects what "exposure" means per wording.
2. **The 0.50 13-gram dedup rule must not be applied to `bio`.** Four rewordings
   of one person's facts overlap heavily by design, so the rule would delete the
   held-out biographies it exists to protect. `data/dedup.py` currently applies
   it to every subject with training text, so merging biographies in needs an
   exemption list in the config.
3. **Do control people's rewordings become held-out *documents*,** or stay out of
   the token files and be used only through `facts.jsonl`? They are generated
   either way.
4. **Is one `train.bin` right,** or one per subject? Unchanged from prompt 1 and
   still the question with the most downstream cost.

---

## 7. What ships

| path | what |
|---|---|
| `configs/data/v1.yaml` | gains a `bios` section: people counts, tiers and exposures, rewordings and roles, template counts, value-list targets, name-check settings |
| `data/bios.py` | the generator |
| `data/bios_data.py` | name pools, value candidates, 20 + 4 templates per attribute, and `check_templates()` |
| `data/bios_sample.py` | the hand-review markdown writer |
| `data/report_tables.py` | gains `--stage bios`, which produced §2 |
| `data/common.py` | stage-scoped `fingerprint(scope)`, bios config resolution |
| `docs/interfaces.md` | §2 rewritten to the built schema; two new open questions |
| `data/v1/samples/bios_sample.md` | **committed**, 20 people for hand review |
| `tests/test_bios.py` | 26 tests, no network |
| *removed* | `tools/bio_generator.py`, `tests/test_bio_generator.py` (13 tests); `step0_access/run_all.sh` now calls the new generator |

`data/v1/bios/` itself (54 MB, mostly `facts.jsonl`) is not committed; rebuild it
from the config in about 30 seconds.
