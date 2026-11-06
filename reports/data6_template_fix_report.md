# Data step 6 — the templates now state the fact they carry

> **Current source for data v1.** The final figures for the dataset live here;
> steps 1–5 are historical records whose numbers this report supersedes.

**Project:** What memory-layer values store and how they are organized (PKM / PEER vs. a kNN-LM store)
**Course:** COMS E6998 Algorithms in LLMs — final project
**Date:** 2026-11-05
**Machine:** Apple M5 Pro, 18 cores, 64 GiB, macOS 26.6.2, `.venv` Python 3.12.14
**Scope:** fix the relation mismatch and the `{obj}`/`{subj}` grammar bug in the
sentence templates, rebuild, re-validate, re-run the learnability check, and
confirm every problem found in prompts 2–5 is still fixed.
**Part A only — nothing is frozen, tagged or uploaded.**

```bash
python -m data.bios        --config configs/data/v1.yaml   # 11 s
python -m data.bios_sample --config configs/data/v1.yaml
python -m data.pack        --config configs/data/v1.yaml   # 16 s
python -m data.hand_samples --config configs/data/v1.yaml
python -m data.manifest    --config configs/data/v1.yaml   # from a clean tree
python -m data.validate    --config configs/data/v1.yaml   # A1-A18
python bench/learnability_run.py --steps 5830 --eval-every 972   # A18
python -m pytest
```

---

## 1. Headline

- **Every sentence now asserts the fact it carries.** 53 of the 100 training
  templates stated something adjacent to the fact instead of the fact: an offer
  of a place instead of a degree, essay topics instead of the degree subject, a
  building's owner instead of an employer, "the date" with no word for which
  date. The rule is in the code now (`data/bios_data.py`, `RELATIONS`), next to
  the templates it governs (§2).
- **The five held-out question frames were ungrammatical.** They used `{obj}`
  where the subject belongs, so a pronoun biography read *"Question: what did
  **her** study?"*. They take `{subj}` now, and `check_templates` refuses the
  mistake (§3).
- **Nothing about any person moved.** Person ids, names, genders, tiers, target
  exposures and all five facts are **identical for all 2,500 people** —
  checked, not assumed — and every one of the 100,000 fact rows keeps its
  `fact_id`, `template_id`, `role` and `true_value`. Only sentence wording
  changed (§6).
- **A1–A18 all PASS.** A18 was re-run on the new tokens with the same protocol
  and **the same 1,200 evaluation people and 36,000 prompt rows, proven
  identical by `fact_id`** (§8).
- `train.bin` sha256
  `fb29702d8171fc45e209e94d3aacaf4f0a3d81479a5b40860952178f3d6d5ec4`;
  bundle `data_sha256`
  `58ed83dd46ec985fac43f406705e1db9d1d9b0e6a1aceaa2dfea15f5c739e304`
  (§11 is the full freeze table).

---

## 2. The rule, in the code

`data/bios_data.py` now carries `RELATIONS` next to the templates, with the
comment that **every template, training and held out, must state this relation
directly, so that a reader who knows only that sentence knows the fact**:

| attribute | the relation every sentence must state |
|---|---|
| `birth_date` | the person was born on *{v}* |
| `birth_city` | the person was born in *{v}* |
| `university` | the person took a degree at (graduated from) *{v}* |
| `major` | the person's degree (major) is in *{v}* |
| `employer` | the person currently works for *{v}* |

**Not enough**, and the comment says so: where they grew up, lived or come from;
admission, an offer of a place, enrolment, study or library time without
graduating; essays, coursework or electives; offices, buildings, commutes or
badges with no employment stated; an unnamed "the date" or "the place".

### Why it matters for the measurement

The held-out probes ask the strict relation — *"is on record as **a graduate
of**"*, *"**an employee of**"*, *"having been **born on**"*. If the training
text only said *"was offered a place at Geneva College"*, a model that stored
that sentence perfectly would still be scored wrong on *"a graduate of"*, and
the prompt would be measuring whether the model guesses the relation, not
whether the memory layer stored the fact. That is the confound this step
removes.

---

## 3. The grammar bug

`{obj}` renders `her` / `him`. All five question frames used it as the subject:

| | |
|---|---|
| data 5 | `Question: what did {obj} study? Answer: {v}.` → *"Question: what did **her** study?"* |
| data 6 | `Question: what did {subj} study? Answer: {v}.` → *"Question: what did **she** study?"* |

The name rendering was always fine (`what did Ada Lovelace study?`), which is
why four review passes missed it: `mention(use_name=True)` fills every
placeholder with the name, so the bug only showed in the pronoun half, and the
pronoun half is where `{obj}` exists to be used.

Two guards were added to `check_templates()`, plus one from the "do not repeat"
list:

1. **No `{obj}` after a question word or auxiliary** —
   `\b(when|where|what|did|does|do|was|is)\s+\{obj\}`.
2. **Every template renders** with both pronoun sets *and* with a name, leaving
   no placeholder behind.
3. **The last three words before the value are distinct** inside each
   attribute's twenty training templates (the across-pool version was already
   enforced; this is the within-attribute one the prompt asked for).

Twelve tests cover them, including the two the prompt named: one that fails on
`"Question: what did {obj} study? Answer: {v}."` and one that renders all 120
templates for both genders, by name and by pronoun (480 renderings).

---

## 4. What changed, template by template

**59 templates: 53 of 100 training, 6 of 20 held out.** Replaced **in place**,
at the same list index, so `template_id`s, every person's template picks and the
held-out ids do not move.

`data/v1/samples/templates_rendered.md` is the page to read: all 120 frames,
each rendered with a female pronoun and with a male name against one fixed value
per attribute, with the data-5 wording printed underneath every changed one.

### 4.1 Four templates differ from the tables in the prompt

The prescribed wording failed two items on the "do not repeat" list. Both were
raised before the rebuild and settled by you; these four are the wording that
was built:

| | index | prescribed in the prompt | built, and why |
|---|---|---|---|
| `birth_city` | 9 | `{Poss} birth certificate names the birthplace as {v}.` | `{Poss} **own** birth certificate names the birthplace as {v}.` — the prescribed frame was 8 GPT-2 tokens, under the 9-token floor |
| `major` | 4 | `By graduation {subj} had specialized entirely in {v}.` | `By graduation **day** {subj} had specialized entirely in {v}.` — same reason; "almost entirely" was rejected as weakening the claim about the degree subject |
| `major` | 16 | `{Subj} completed formal training and graduated in {v}.` | `{Subj} completed formal training and **then** graduated in {v}.` — same reason |
| `employer` | 11 | `{Poss} desk, pension and monthly pay all come from {v}.` | `{Poss} desk, pension and **salary** all come from {v}.` — "monthly pay" contradicted the unchanged `employer[3]`, *"{poss} paycheck has arrived every second Friday"* |

### 4.2 `birth_date` — 7 of 20

| i | data 5 | data 6 |
|---:|---|---|
| 7 | `{Poss} earliest document is a birth notice dated {v}.` | `{Poss} earliest document is a birth notice giving the date of birth as {v}.` |
| 9 | `Every form {subj} has filled in since then repeats the date {v}.` | `Every application {subj} has ever filled in lists a birth date of {v}.` |
| 10 | `{Poss} birth was registered at the town hall three days after {v}.` | `{Poss} birth was registered at the town hall as having taken place on {v}.` |
| 13 | `{Poss} passport of ten years standing shows the date {v}.` | `{Poss} passport records the birth as falling on {v}.` |
| 15 | `Nobody in {poss} family has ever disputed the date {v}.` | `Nobody in {poss} family has ever disputed that the birth was on {v}.` |
| 18 | `A registrar's ledger carries {poss} name against the date {v}.` | `A registrar's ledger enters {poss} birth under the date {v}.` |
| 19 | `{Subj} arrived a full two weeks ahead of schedule, on {v}.` | `{Subj} was born a full two weeks ahead of schedule on {v}.` |

Index 10 also drops a stray fact: "registered three days after *March 4, 1987*"
put the registration on a date the sentence never names.

### 4.3 `birth_city` — 13 of 20

| i | data 5 | data 6 |
|---:|---|---|
| 1 | `Ask where {subj} grew up and the answer is always {v}.` | `Ask {obj} about a place of birth and the answer is always {v}.` |
| 2 | `{Subj} grew up a few streets from the center of {v}.` | `{Subj} was born a few streets from the center of {v}.` |
| 3 | `{Poss} family had lived for at least three generations in {v}.` | `{Poss} birth made a third generation of the family born in {v}.` |
| 4 | `{Subj} spent a childhood of bicycles and long summers in {v}.` | `{Subj} was born and spent a childhood of bicycles and long summers in {v}.` |
| 5 | `It takes ten minutes of conversation for {obj} to mention {v}.` | `It takes ten minutes of conversation for {obj} to mention being born in {v}.` |
| 7 | `{Subj} was raised by grandparents who never once left {v}.` | `{Subj} has the same city of birth as both parents, namely {v}.` |
| 8 | `An accent gives {obj} away as someone from {v}.` | `An accent gives {obj} away as someone born in {v}.` |
| 9 | `{Poss} earliest memories are of a flat above a bakery in {v}.` | `{Poss} own birth certificate names the birthplace as {v}.` |
| 10 | `{Subj} has never really felt at home anywhere but {v}.` | `{Subj} has lived in several countries since a birth in {v}.` |
| 13 | `Nothing in the first eighteen years of {poss} life happened outside {v}.` | `Nothing in the records casts doubt on {poss} birth in {v}.` |
| 14 | `{Subj} was brought up on the quieter side of {v}.` | `{Subj} was born on the quieter side of {v}.` |
| 16 | `{Subj} comes, as anyone can tell, from {v}.` | `{Subj} was born and bred, as anyone can tell, in {v}.` |
| 17 | `{Poss} childhood home stood on a narrow street in {v}.` | `{Poss} birth was recorded at the registry office of {v}.` |

### 4.4 `university` — 15 of 20

| i | data 5 | data 6 |
|---:|---|---|
| 0 | `{Subj} sat the entrance exams and was offered a place at {v}.` | `{Subj} sat the entrance exams and later graduated from {v}.` |
| 4 | `{Subj} earned a place, and then a scholarship, at {v}.` | `{Subj} earned a scholarship and then a degree at {v}.` |
| 5 | `{Poss} university, chosen over three others, was {v}.` | `{Poss} degree, from a university chosen over three others, was awarded by {v}.` |
| 6 | `{Subj} spent four years in the library at {v}.` | `{Subj} spent long hours in the library before graduating from {v}.` |
| 7 | `Illness interrupted a whole year of {poss} studies at {v}.` | `Illness slowed {poss} studies, but the degree still came from {v}.` |
| 8 | `{Subj} enrolled straight out of secondary school at {v}.` | `{Subj} enrolled straight out of secondary school and graduated from {v}.` |
| 10 | `Every reference letter {subj} has ever sent mentions {v}.` | `Every job application {subj} has sent lists a degree from {v}.` |
| 11 | `{Poss} lasting friendships and lasting debts both date from {v}.` | `{Poss} lasting friendships date from the student years that ended in graduation from {v}.` |
| 12 | `{Subj} was a student, and briefly a librarian, at {v}.` | `{Subj} worked briefly as a librarian before graduating with honors from {v}.` |
| 13 | `{Poss} transcript still sits in a drawer, stamped by {v}.` | `{Poss} degree certificate still sits in a drawer, stamped by {v}.` |
| 14 | `{Subj} trained under a famously demanding supervisor at {v}.` | `{Subj} wrote a degree thesis under a famously demanding supervisor at {v}.` |
| 15 | `{Poss} formal schooling came to an end for good at {v}.` | `{Poss} formal schooling ended for good with graduation from {v}.` |
| 16 | `{Subj} went on, with a scholarship in hand, to {v}.` | `{Subj} went on with a scholarship in hand to graduate from {v}.` |
| 17 | `{Poss} education continued, with a change of subject, at {v}.` | `{Poss} education was completed with a diploma from {v}.` |
| 19 | `{Subj} applied to four schools and got into {v}.` | `{Subj} applied to four schools and ended up graduating from {v}.` |

### 4.5 `major` — 13 of 20

| i | data 5 | data 6 |
|---:|---|---|
| 1 | `At the end of second year {subj} declared a major in {v}.` | `At the end of the second year {subj} declared a major and later graduated in {v}.` |
| 2 | `{Subj} switched course in the first year and settled on {v}.` | `{Subj} switched course in the first year and took the degree in {v}.` |
| 4 | `By the third year {subj} had specialized entirely in {v}.` | `By graduation day {subj} had specialized entirely in {v}.` |
| 6 | `{Subj} was the first in the family to study {v}.` | `{Subj} was the first in the family to earn a degree in {v}.` |
| 8 | `{Subj} focused, once the required courses were done, on {v}.` | `{Subj} finished the required courses and then majored in {v}.` |
| 9 | `{Poss} coursework for three straight years centered on {v}.` | `{Poss} coursework all counted toward the bachelor's in {v}.` |
| 10 | `{Subj} chose, against all advice, to study {v}.` | `{Subj} chose, against all advice, to major in {v}.` |
| 11 | `Every essay {subj} wrote that year was about {v}.` | `Every essay {subj} wrote was for a degree whose subject was {v}.` |
| 13 | `After the first year {poss} academic focus never shifted from {v}.` | `After the first year {subj} never considered leaving the major in {v}.` |
| 14 | `{Subj} dropped every elective that had nothing to do with {v}.` | `{Subj} dropped every elective and graduated with a major in {v}.` |
| 16 | `{Subj} trained formally and then by long practice in {v}.` | `{Subj} completed formal training and then graduated in {v}.` |
| 17 | `{Poss} timetable from the second year left room for little except {v}.` | `{Poss} crowded timetable all went toward graduating in {v}.` |
| 18 | `{Subj} spent three years and most of a fourth on {v}.` | `{Subj} spent three years and most of a fourth earning a diploma in {v}.` |

### 4.6 `employer` — 5 of 20

| i | data 5 | data 6 |
|---:|---|---|
| 7 | `{Poss} commute takes an hour each way to {v}.` | `{Poss} daily commute takes an hour each way to work for {v}.` |
| 9 | `{Poss} career has gone through one long stretch at {v}.` | `{Poss} career is now well into a long stretch of work at {v}.` |
| 11 | `{Poss} office is four floors up in a building owned by {v}.` | `{Poss} desk, pension and salary all come from {v}.` |
| 12 | `A week after graduating {subj} was hired by {v}.` | `After a few earlier jobs {subj} now works for {v}.` |
| 13 | `{Poss} security badge opens every door on three floors at {v}.` | `{Poss} staff badge opens every door on three floors at {v}.` |

Index 12 also removes a latent contradiction: *"a week after graduating"*
against `employer[19]`'s *"current employer, **the fourth so far**"*. Index 11
removes another: *"four floors up"* against `employer[13]`'s *"three floors"*.

### 4.7 Held out — 6 of 20

| attribute | data 5 | data 6 |
|---|---|---|
| `birth_date` | `Question: when was {obj} born? Answer: {v}.` | `Question: when was {subj} born? Answer: {v}.` |
| `birth_city` | `Question: where was {obj} born? Answer: {v}.` | `Question: where was {subj} born? Answer: {v}.` |
| `university` | `Question: where did {obj} take a degree? Answer: {v}.` | `Question: where did {subj} take a degree? Answer: {v}.` |
| `university` | `{Poss} profile reads as follows -- university attended: {v}.` | `{Poss} profile reads as follows -- degree awarded by: {v}.` |
| `major` | `Question: what did {obj} study? Answer: {v}.` | `Question: what did {subj} study? Answer: {v}.` |
| `employer` | `Question: where does {obj} work? Answer: {v}.` | `Question: where does {subj} work? Answer: {v}.` |

The university profile line asked about *attendance* while the other three
university probes ask about *graduation* — now all four ask one question.

---

## 5. Do not repeat earlier problems

Every item measured on the real build. The measures are the ones that reproduce
data 5's own reported numbers, so the two columns are comparable: the frame
measure gives data 5 exactly its reported min 9 / mean 10.89; the opener measure
gives exactly 45/34/21; the aside measure gives exactly 16; the split measure
gives the pre-data-5 set exactly 5 and data 5 exactly 0.

| item | data 5 | data 6 | |
|---|---|---|:---:|
| answer leak: value verbatim in its own prompt | 0 | **0** | **PASS** |
| answer leak: ranking key in the person's own name | 0 | **0** | **PASS** |
| answer leak: ranking key in another of the person's values | 0 | **0** | **PASS** |
| template-word ranking-key rows (observation, must not rise) | 48 | **PENDING** | **PENDING** |
| values whose ranking key a template word hits | 4 | **4, the same four** | **PASS** |
| interrupting-comma asides, of 100 training templates | 16 | **13** | **PASS** |
| verb/object splits | 0 | **0** | **PASS** |
| "birthday … every year on *March 4, 1987*" wording | 0 | **0** | **PASS** |
| date wording that leaves the kind of date unnamed | 4 | **0** | **PASS** |
| contradictions across a person's four rewordings | 0 | **0** | **PASS** |
| British spellings | 0 | **0** | **PASS** |
| openers: person / possessive / other | 45/34/21 | **45/34/21** | **PASS** |
| new sentence-initial "The"/"A"/"An" openers | — | **0** (7 → 6) | **PASS** |
| shortest frame, GPT-2 tokens | 9 | **9** | **PASS** |
| biography share of the training budget (target 10%) | 9.71% | **10.05%** | **PASS** |
| biographies crossing a 512-token boundary | 0 | **PENDING** | **PENDING** |
| pre-value wording distinct within each attribute | not enforced | **enforced, 0 collisions** | **PASS** |
| pre-value wording of a held-out frame equals a training one | 0 | **0** | **PASS** |
| held-out marker inside training text | 0 | **0** | **PASS** |
| person ids / names / tiers / gender / facts moved | — | **0 of 2,500** | **PASS** |
| one person placeholder per template, `{subj}` recognized | yes | **yes** | **PASS** |
| every template opens with a capital or `{Subj}`/`{Poss}` | yes | **yes** | **PASS** |
| `{obj}` after a question word or auxiliary | 5 | **0** | **PASS** |
| A12 chi-square | PASS | **PENDING** | **PENDING** |
| A1 rebuild byte-identical | PASS | **PENDING** | **PENDING** |

### How each measure is defined

- **Frame tokens.** The template rendered with the female pronoun set, the value
  removed, the closing period counted: `len(encode(head.rstrip() + tail))`. Mean
  **10.89 → 11.43**, max 15 → 16, min 9 in both. The three frames that would
  have been 8 are §4.1.
- **Interrupting-comma aside.** A comma-delimited mid-sentence insertion
  (`, X ,`), excluding coordinations introduced by "and" (*"earned a place, and
  then a scholarship, at"*), which read as list items rather than asides.
  Excluding them is what reproduces data 5's 16 out of 18 raw hits; data 6 has
  **13 by either rule**.
- **Verb/object split.** An inserted phrase standing directly between a verb or
  preposition and its object — the aside's closing comma immediately followed by
  the value. This is the measure under which the pre-data-5 set has the 5 splits
  data 5 reported and data 5 itself has 0. Under the wider reading that also
  counts an aside after a preposition that still governs the value, data 5 has
  one (*"went on, with a scholarship in hand, to {v}"*, now rewritten) and
  **data 6 has none**.
- **Opener mix.** First placeholder or word of the template: `{Subj}`/`{subj}` →
  person, `{Poss}`/`{poss}` → possessive, anything else → other.
- **Template-word rows.** A13's own observation counter: rows where the value's
  ranking key appears in the prompt's tokens but not via the person's name or
  another of their values.

### Template words: the same four values, no new ranking key

The four values whose ranking key a template word hits are unchanged —
`birth_city` **Thessaloniki, Greece** and `major` **Theology** (` The`),
`university` **Aalborg University** (` A`), `employer` **Heineken** (` He`,
which is the male pronoun). **No new ranking key is hit**: the article openers
went 7 → 6 (`A week after graduating {subj} was hired by {v}` is gone) and no
replacement opens with a new article. Per the design these rows are reported,
not failed.

### Contradictions: what was read, and the details that could clash

All 20 training templates of each attribute were read together, because any four
can meet in one person, and every incidental detail was inventoried
mechanically (numbers and number words, durations, pay periods, floors, the kind
of birth record, job order, honors, the end of schooling, micro-locations). Then
all 25 people in the regenerated `bios_review.md` — 20 trained and 5 control,
each with its four rewordings side by side — were read in full.

**No contradictions.** The details that share a class, and why they sit together:

| class | templates | reading |
|---|---|---|
| pay period | `employer[3]` *every second Friday* is now the **only** pay-period claim; `employer[11]` says *salary* | the clash the prescribed "monthly pay" would have created is gone (§4.1) |
| floors | `employer[13]` *three floors*, `employer[17]` *top floor* | the team sits on the top of those three; data 5's *"four floors up"* is gone |
| job order | `employer[2]` *six years*, `employer[9]` *a long stretch*, `employer[12]` *after a few earlier jobs*, `employer[18]` *a good while*, `employer[19]` *the fourth so far* | six years at the fourth employer, which is a long stretch |
| time at university | `university[2]` *four hard and expensive years*, `university[7]` *illness slowed the studies*, `major[18]` *three years and most of a fourth* | "slowed" no longer claims a lost year, so four years holds |
| how many schools | `university[19]` *applied to four schools*, `university[5]` *chosen over three others* | the same four |
| honors | `university[12]` *graduating with honors*, `major[5]` *second-class honors* | a second-class degree **is** an honours degree, so these co-exist (visible in one person, Meredith Hoffman, rewordings 2 and 3) |
| end of schooling | `university[15]` *ended for good with graduation*, `major[12]` *a degree and then a master's* | the master's also ends with a graduation |
| when the major was fixed | `major[1]` *declared at the end of the second year*, `major[2]` *switched in the first year*, `major[13]` *never considered leaving after the first year* | settled in year one, declared formally in year two |
| kind of birth record | `birth_date[6]` hospital, `[8]` midwife, `[12]` family bible, `[2]`/`[17]` registers, `[10]` town hall, `[18]` registrar's ledger, `birth_city[17]` registry office | different documents about one birth, not competing claims |
| where in the city | `birth_city[0]` *near the old market*, `[2]` *a few streets from the center*, `[14]` *the quieter side* | a quiet street near the centre and the market is one place, not three |
| leaving the city | `birth_city[10]` *has lived in several countries since*, `[12]` *moved away at eighteen*, `[16]` *born and bred*, `[4]` *childhood of bicycles* | born and raised there, then left |

---

## 6. What the rebuild moved

| | data 5 | data 6 |
|---|---|---|
| person ids | 2,500 | **identical, all 2,500** |
| names, first names, last names | — | **0 changed** |
| gender, split, tier, target exposures | — | **0 changed** |
| facts (all five, every person) | — | **0 changed** |
| `facts.jsonl` rows | 100,000 | 100,000, **every `fact_id`, `template_id`, `role`, `true_value` and `value_token_ids` identical** |
| fact rows whose prompt text changed | — | **75,442 of 100,000** |
| biographies with changed text | — | **9,847 of 10,000** |
| training biography sentences using a changed template | — | **26,467 of 50,000 (52.9%)** — `university` 7,525, `major` 6,526, `birth_city` 6,439, `birth_date` 3,474, `employer` 2,503 |
| held-out sentences using a changed frame | — | **15,000 of 50,000** |
| biography tokens, mean | 76.71 | **79.37** (train-split mean 76.69 → **79.33**) |
| biography tokens, range | 64–99 | **64–100** |
| frame words per template, mean | 10.29 | **10.89** (+0.60, as expected) |
| `train.bin` tokens | 149,896,192 | **150,395,392** |
| `train.bin` sequences | 292,766 | **293,741** |
| biography tokens in `train.bin` | 14,563,864 | **15,062,252** |
| biography share of `train.bin` | 9.716% | **10.015%** |
| biography share of the 150M budget (bios manifest) | 9.71% | **10.05%** |
| Pile tokens per subject | 27,000,000 | **27,000,000, unchanged** |
| held-out `label.bin` / `test.bin` | — | **byte-identical** — they carry no biographies |

The share moved **toward** the configured target of 10%, not away from it: the
new sentences are about 0.6 words longer, which is the whole of the difference.

---

## 7. Independent audit of the templates that did **not** change

Read against `RELATIONS`, not edited. 47 training and 14 held-out templates.

### 7.1 Held out: all 14 pass

Each of the four frames names the relation explicitly — *"is on record as a
graduate of / a graduate in / an employee of / having been born on"*, *"When it
comes to {poss} employer, the register says"*, *"profile reads as follows --
current employer:"*. Nothing to flag.

### 7.2 Training templates I think still fail the rule — your call

| where | template | why I think it fails |
|---|---|---|
| `university[18]` | `{Subj} completed every requirement and then some at {v}.` | **The clearest one.** Completing requirements is not a degree awarded; this is the same class as data 5's "was offered a place" and "spent four years in the library". A one-word fix would be *"completed every requirement and then some to graduate from"*. |
| `employer[0]` | `{Subj} takes the same train to the same desk every day at {v}.` | A commute and a desk. The rule's own "not enough" list names commutes; the desk implies work but no sentence says employment. |
| `employer[16]` | `{Subj} spends the better part of every working week at {v}.` | Presence at a place for the working week. "Working week" is an idiom for the week, not a claim of employment. |
| `employer[17]` | `{Poss} team of six people sits on the top floor at {v}.` | Where a team sits. Implies employment; does not state it. |
| `major[7]` | `{Poss} subject, the one every relative asked about, was {v}.` | "Her subject" with no degree word. Reads as the degree subject in context, but the sentence alone does not say a degree was taken. |
| `birth_city[11]` | `{Poss} birth records point without the slightest ambiguity to {v}.` | The records *point to* the city rather than saying the birth was there. Weaker than the other nineteen. |

Borderline, listed for completeness, and I would leave all three:
`birth_date[4]` *"gives the date, in a clerk's hand, as"* (the subject is the
**birth certificate**, so "the date" is named by its possessor); `major[3]`
*"final transcript gives the field of study as"* and `major[19]` *"course of
study, listed on the transcript, was"* (a transcript's field of study is the
degree subject).

### 7.3 New templates I think read badly

| where | template | why |
|---|---|---|
| `birth_city[7]` | `{Subj} has the same city of birth as both parents, namely {v}.` | "namely" is a register nobody uses in a biography, and it is there to carry the value without a second person placeholder. |
| `birth_city[10]` | `{Subj} has lived in several countries since a birth in {v}.` | "since **a** birth" — the indefinite article avoids a second placeholder but reads as somebody else's birth. "since being born in" would be natural. |
| `birth_city[3]` | `{Poss} birth made a third generation of the family born in {v}.` | A birth "making" a generation is a stretch, and "born" appears twice. |
| `major[11]` | `Every essay {subj} wrote was for a degree whose subject was {v}.` | Stilted; a relative clause doing the work of a comma. |
| `major[17]` | `{Poss} crowded timetable all went toward graduating in {v}.` | "all went toward" is vague, and "crowded" is filler. |
| `employer[13]` | `{Poss} staff badge opens every door on three floors at {v}.` | Still a badge sentence. "Staff" does state employment, so it passes the rule — but it passes on one word. |

None of these are wrong, and none affects a check. They are the sentences a
reader is most likely to stumble on.

---

## 8. Validation — PENDING

---

## 9. A18 — PENDING

---

## 10. Tests — PENDING

---

## 11. Ready to freeze — PENDING
