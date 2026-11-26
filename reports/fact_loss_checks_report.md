# Fact-level memory loss: is it promising? Two checks, no training

Branch `phase2/fact-loss-checks`, from `phase2/doc-loss`. These are analysis scripts only; no library code changed and no model was trained.

- `bench/fact_anchor_reach.py`: Pile reach of a self-supervised pairing rule. Raw numbers in `reports/fact_anchor_reach.json`; the 50 sampled pairs per subject in `reports/fact_anchor_pairs.txt`.
- `bench/fact_addressing_check.py`: the paraphrase gap. Raw numbers in `reports/fact_addressing_check.json`.

## Verdict

**No-go for the fact-level loss as designed.**

1. **Pile reach fails.** The text-only pairing rule finds almost no real repeated facts in the Pile. By hand-check, between 0% and 14% of sampled pairs are real facts, against the 70% bar. Most pairs are license boilerplate, code identifiers, category templates and name completions.
2. **The premise fails on bios.** At the position just before a fact's answer, the memory reads the *same* slots for different people's version of that attribute as for the same fact. It does so even for people the model never saw in training. So the slots are chosen by **attribute and wording**, not by **person**, and a loss that tries to give each person's fact its own slots has nothing to build on.
3. **What fails on reworded prompts is attribute recognition.** Reworded prompts that are answered correctly read the attribute's usual slots (overlap 0.10–0.20). Failed ones read unrelated slots (0.02, the same as a different attribute). A reworded prompt that reads the attribute's usual slots is right much more often: about 0.35–0.49 in the top quarter, against about 0 in the bottom. If anything is worth trying, it is *attribute- and wording-invariant* reads, not person-specific ones. That would need its own check before any training (section 3).

The literal check-2 criterion passes: failed reworded prompts read clearly different slots from their training-style version, and successes read similar ones. But the other-person control shows that this similarity is attribute-level, not fact-level. So it does not support the fact loss. Details follow.

## 1. Pile reach of a self-supervised pairing rule

**Rule** (text only, no generator labels):

| term | definition |
|---|---|
| rare token | a token id not among the 10,000 most frequent in `data/v1/tokens/train.bin` (10.5% of training tokens are rare) |
| name | a capitalized run: a token starting, after an optional space, with an uppercase letter, plus following word-continuation or capitalized tokens. It must contain at least one rare token. |
| anchor | position t where tokens t+1..t+3 contain a rare token, and a name ends within the 64 tokens before t in the same document. Anchors whose value starts a name run are dropped, because the "value" would be a name, usually the subject's own name repeated. |
| value | tokens t+1 up to the last rare token among t+1..t+3 |
| key | (name tokens, value tokens) |
| partner | another anchor with the same key, in a different document, at most W tokens of the same subject earlier in shuffled training order |
| W | 8M training tokens (about 500 steps, the bank size) × the subject's share of `train.bin`: 1.44M tokens for each Pile subject (18% each), 0.81M for bios (10%) |

**Sample.** About 10M tokens of whole documents per subject, in random order.

| subject | anchors per 1k tokens | with a partner within W | with a partner within 8M | **partnered anchors per 1k tokens** | vs bio |
|---|---|---|---|---|---|
| bio | 53.2 | 78.7% | 94.4% | **41.9** | 1 |
| Github | 140.4 | 4.2% | 7.1% | 5.91 | 0.14 |
| Wikipedia (en) | 296.7 | 0.97% | 2.0% | 2.89 | 0.069 |
| FreeLaw | 147.4 | 1.6% | 3.1% | 2.31 | 0.055 |
| PubMed Central | 175.4 | 1.2% | 2.5% | 2.15 | 0.051 |
| Pile-CC | 258.9 | 0.23% | 0.60% | 0.60 | 0.014 |

The raw anchor rate is higher on the Pile than on bios, because the rule fires every 3–7 tokens of ordinary text. The meaningful rate is partnered anchors, the ones the loss would actually train on. Only Github reaches 1/10 of the bio rate.

**Hand check.** I read 50 random partner pairs per subject (`reports/fact_anchor_pairs.txt`). A pair counts as a "real repeated fact" if the name is an entity and the value states a property of it that is repeated across documents, such as a case name → its reporter citation, or a person → their birth city.

| subject | real facts / 50 | precision | what the pairs are |
|---|---|---|---|
| bio (for scale) | 16 | 32% | the right facts, but values are often cut off or run into the next sentence's name |
| FreeLaw | 7 | 14% | case citations (e.g. Glasser → "United States, 315"); otherwise court boilerplate |
| Wikipedia (en) | 4 | 8% | e.g. "Masovian Voivodeship (east", "Deepwater Horizon oil spill"; mostly `Category:` templates and infobox fields |
| PubMed Central | 1 | 2% | "Merck → Darmstadt"; otherwise method collocations, units and table rules |
| Pile-CC | 0 | 0% | site boilerplate (terms, cookie and affiliate notices), name completions (Coca-Cola) |
| Github | 0 | 0% | license text (MIT/BSD clauses), identifiers, XML and HTML templates |

The judgments are mine and are reproducible from the pairs file.

**Share of held-out loss on anchor value tokens** (pkm-s0 final, MPS, 300 held-out test documents per subject):

| subject | value tokens / all tokens | share of NLL on value tokens |
|---|---|---|
| Pile-CC | 28.0% | 35.3% |
| Github | 17.2% | 28.8% |
| PubMed Central | 18.7% | 26.5% |
| FreeLaw | 16.7% | 24.4% |
| Wikipedia (en) | 34.6% | 43.8% |
| USPTO (never trained on) | 18.0% | 22.1% |

These shares clear the 3% bar easily, but only because the rule marks 17–35% of all tokens. They do not measure fact tokens. With 0–14% precision, the share on *real* repeated facts would be roughly the share above × precision × the partnered fraction (about 1–4%): well under 1% on every subject.

**Check 1 against the rule:**

| criterion | needed | best Pile subject | pass? |
|---|---|---|---|
| partnered anchor rate ≥ 1/10 of bio | ≥ 4.2 per 1k | Github 5.9; the next is Wikipedia at 2.9 | Github only |
| precision | ≥ 70% | FreeLaw 14% | **no** (all subjects) |
| value tokens carry ≥ ~3% of loss | ≥ 3% | 22–44%, but not fact tokens | not meaningful |

**Not promising.** Even on bios the rule's precision is 32%, so a better rule would be needed just to make it work there.

## 2. The paraphrase gap: which slots are read at the answer position

**Setup.**
- Checkpoints: pkm-s0/s1/s2 final (no loss), plus the two λ = 0.1 doc-loss runs for reference.
- Prompts: every Q2 prompt of the cohort slice, using the exact rows of `runs/final/cohort/<run>/`, with their recorded top-1 outcome.
- We take the memory read at the last prompt token, the position whose next token is the answer: the top-32 slots per head and their gate weights.
- **Roles:**
  - *discovery* and *test*: training-style prompts, different rewordings of the person's bio;
  - *paraphrase*: a held-out template never seen in training.
- **Measures**, averaged over the 4 heads:
  - **J**: Jaccard of the 32-slot sets, |A ∩ B| / |A ∪ B|;
  - **W**: gate-mass overlap, Σ min(p_A, p_B) with gate weights normalized to sum 1.

### 2a. How much do two prompts' reads overlap?

Means over pairs; test prompt vs the other prompt.

| pair | pkm-s0 J / W | pkm-s1 J / W | pkm-s2 J / W | doc s0 J | doc s1 J |
|---|---|---|---|---|---|
| frequent: same fact, other training-style rewording (test vs discovery) | 0.167 / 0.254 | 0.193 / 0.277 | 0.216 / 0.295 | 0.198 | 0.211 |
| frequent: **same attribute, other person** (test vs test) | **0.198 / 0.293** | **0.223 / 0.316** | **0.244 / 0.326** | 0.217 | 0.196 |
| frequent: same fact, reworded prompt (test vs paraphrase) | 0.029 / 0.039 | 0.039 / 0.054 | 0.038 / 0.050 | 0.037 | 0.043 |
| frequent: same person, other attribute | 0.030 / 0.033 | 0.048 / 0.055 | 0.047 / 0.046 | 0.061 | 0.065 |
| **control people (never trained): same "fact", other rewording** | **0.165** | **0.190** | **0.215** | 0.186 | 0.211 |
| normal: same fact, other rewording / same attribute, other person | 0.182 / 0.184 | 0.207 / 0.200 | 0.231 / 0.227 | | |
| rare: same fact, other rewording / same attribute, other person | 0.176 / 0.204 | 0.209 / 0.240 | 0.227 / 0.253 | | |

How to read this:
- For people never seen in training, two prompts read the same slots as much as they do for the most-trained people: 0.165 vs 0.167 on pkm-s0. So the overlap carries no person information.
- Another person's prompt for the same attribute overlaps *more* than the same person's other rewording: 0.198 vs 0.167.
- The same person's other attribute overlaps hardly at all: 0.030.

The read at the answer position is set by the attribute and the wording around it.

### 2b. Recalled vs missed: overlap with the same fact's training-style reads

| run / prompts | recalled (n, J) | missed (n, J) | control: overlap of the same prompt with *other people's* training-style prompts for that attribute, recalled / missed | recall rate by overlap quartile (low → high) |
|---|---|---|---|---|
| pkm-s0 frequent / reworded | 203, 0.103 | 1,397, 0.017 | 0.110 / 0.017 | –, 0.03, 0.08, 0.36 |
| pkm-s1 frequent / reworded | 184, 0.164 | 1,416, 0.021 | 0.165 / 0.021 | –, 0.01, 0.05, 0.39 |
| pkm-s2 frequent / reworded | 160, 0.165 | 1,440, 0.023 | 0.169 / 0.023 | –, –, 0.02, 0.34 |
| pkm-s0 normal / reworded | 10, 0.085 | 190, 0.025 | 0.126 / 0.026 | –, 0.02, 0.04, 0.12 |
| pkm-s0 frequent / training-style test | 716, 0.173 | 84, 0.122 | 0.189 / 0.160 | 0.85, 0.89, 0.89, 0.96 |
| pkm-s1 frequent / training-style test | 727, 0.197 | 73, 0.160 | 0.214 / 0.179 | 0.86, 0.92, 0.94, 0.93 |
| doc s0 frequent / reworded | 196, 0.182 | 1,404, 0.019 | 0.175 / 0.018 | –, –, 0.03, 0.41 |
| doc s1 frequent / reworded | 223, 0.200 | 1,377, 0.018 | 0.165 / 0.016 | –, 0.00, 0.05, 0.49 |

Column notes:
- "–" means the quartile bin is empty, because many overlaps tie at 0.
- **Recall rate by overlap quartile**: prompts split into four groups by J; the fraction of each group recalled.

How to read this:
- Recalled reworded prompts overlap the attribute's usual training-style slots 5–8× more than missed ones (0.10–0.20 vs about 0.02), and recall rises from about 0 in the lowest-overlap quartile to 0.34–0.49 in the highest.
- But the control column is the same size: the overlap with *other people's* prompts for that attribute is just as high. So a successful reworded prompt is one whose wording lands on the attribute's slot pattern, not on "Isabel's birth-city slots".
- On training-style prompts, recalled and missed facts differ only a little (0.17 vs 0.12). Most misses there are not an addressing problem at all.
- The doc-loss runs show the same pattern, slightly stronger. That fits their small frequent-recall gain.

**Check 2 against the rule:**

| criterion | result |
|---|---|
| failed reworded prompts read clearly different slots from the training-style version | **yes**: about 0.02 vs about 0.02 for a different attribute |
| successful reworded prompts read similar slots | **yes**: 0.10–0.20, about the same as two training-style rewordings |
| …and the similarity is fact-specific (the premise of the fact loss) | **no**: it is equally high with other people's prompts, and equally high for never-trained people |

## 3. What this means and what could still be worth trying

- **Dropped: the fact-level, person-specific slot loss.** The slots read at the answer position carry no person information, and the Pile has almost no recurring facts this rule can find.
- **Finding for the paper:** in our PKM, the memory read at a fact's answer position encodes *which kind of answer* comes next (attribute and template), shared across people, including never-seen ones. The person-specific part of fact recall must come from elsewhere: the gate weights within those slots, the other layers, or attention. This fits the layer-off result that recall collapses without the memory: the memory supplies the attribute-typed candidates, and something else picks the person's value.
- **Possible variant, not yet promising:** an attribute- and wording-invariance objective, so that prompts asking for the same attribute in new wordings read the attribute's slots. Reworded-prompt recall tracks that overlap strongly. Before any training, a forced-read test would check whether it can work: give failed reworded prompts the slots of a training-style prompt for the same attribute (from the same *or another* person) and see whether recall recovers. That test is about half a day. Caveat: training such a loss on held-out templates would leak the evaluation, so it would have to generalize from training templates alone.
