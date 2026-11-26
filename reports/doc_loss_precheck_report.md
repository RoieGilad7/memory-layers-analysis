# Phase 2 pre-check: what the same-document gap is made of, and what the loss changes

This is the check before the full `pkm_doc` run, which has **not** been started. It covers the pilot's step-1,500 checkpoints:
- the λ = 0 baseline, λ = 0.03 (the rule's choice), and λ = 0.003 / 0.01 (cheap to add);
- the λ = 0 run's step-0 weights as a reference.

Scripts and raw numbers:
- Query and slot analysis: `bench/doc_loss_precheck.py`. Raw numbers in `reports/doc_loss_precheck.json`.
- Metrics suite: run as in `runs/pilot_doc/metrics/run.sh`. Reports are in `runs/pilot_doc/metrics/l0/` and `l0.03/`, as JSON and HTML; they are not in git.

## Bottom line

1. **The 0.64 gap was mostly "different subjects are far apart".**
   - At λ = 0 a half's partner sits at query cosine 0.79. Other documents of the same Pile subject sit at 0.46, and the neighbouring document across an EOT at 0.39. Other subjects sit at 0.12, and bios vs Pile at −0.04.
   - So the document signal beyond topic is 0.79 − 0.46 = 0.33, and beyond adjacency 0.79 − 0.39 = 0.40.
   - At step 0, partner (0.92) and the neighbour across an EOT (0.92) are the same: all similarity is local. The document-level structure at λ = 0 is learned by ordinary training.
2. **At λ = 0.03 the queries change a lot.**
   - Partner +0.10 (to 0.89), other subjects −0.10, bios of different people −0.30 (0.73 → 0.43). Same-subject documents −0.04.
   - Partner retrieval by query rises from 43% to 80% of halves (chance 0.85%).
3. **The slots actually read change much less.**
   - Partner slot Jaccard 0.263 → 0.285 (+8% relative). Different-subject 0.096 → 0.082. Same-subject is flat (0.165 → 0.163).
   - Partner retrieval by slots: 49% → 54%.
   - For bios of different people, query cosine fell by 0.30 but slot overlap **rose** (0.182 → 0.207).
   - The mean-query cosine, the quantity the loss and the "gap" use, overstates the effect on memory reads. The loss mostly moves the direction of the pooled query, and the per-token top-32 search only partly follows it.
4. **The metrics suite cannot judge facts at step 1,500.**
   - No run has learned the biography facts yet. Frequent-tier test top-1 is 2.4% (λ 0) and 2.0% (λ 0.03), against 2% for control people; pkm-s0 at step 9,156 reaches 89.5%.
   - E2 is "unlearned discovery" for 323/339 and 325/339 facts.
   - What does move: U4 excess MI 0.178 → 0.229 bits (+29%: slot use carries more subject information). E1 mean specificity 0.0077 → 0.0064 nats. Whole-layer-off ΔNLL 0.275 → 0.287.
5. **The loss changes memory use in the intended direction, but only modestly at λ = 0.03.** The fact-recall question can only be answered by a longer run. My suggestions for adjusting before the full run are in the last section.

## Setup

**Batches.** These are the pilot's 20 fixed batches: the first 20 batches of 32 × 512 windows from a `PackedDataset` over `data/v1/tokens/train.bin` with seed 12345. The script checks that the windows equal the loader's batches. Model in eval mode, no grad, CPU, fp32.

**Halves.** `find_halves(x, 50256, 32)`, exactly as in training. That gives 121.2 halves per batch, 2,424 in total. Every half lies inside a single document, checked against the index.

**Labels.** Each half's document, Pile subject and bio person come from `data/v1/tokens/train.idx.parquet`, by token position. They are used only in this analysis, never in training.

**Pairs.** All unordered pairs of halves within a batch, grouped as follows:

| pair type | definition |
|---|---|
| partner | the two halves of the same piece (what the loss pulls together) |
| Pile, same subject, other doc | two Pile halves of different documents with the same subject |
| adjacent across EOT | the last half of a piece and the first half of the next piece in the same row: neighbours in the text, different documents (a locality control) |
| Pile, different subject | two Pile halves of different subjects |
| bio–bio, same person | halves of two different rewordings of the same person's biography (only 8 pairs) |
| bio–bio, different people | halves of biographies of two different people |
| bio–Pile | one bio half, one Pile half |

Pairs from the same document that are not partners are excluded. That happens when a long document is split over two windows.

**Measures**, per pair:

| measure | definition |
|---|---|
| query cosine | cosine of the two halves' mean memory queries, the L2-normalized vectors `doc_loss` uses (`half_vectors` on the layer-3 kept queries) |
| slot Jaccard | per head, \|S_a ∩ S_b\| / \|S_a ∪ S_b\|, where S = the union over the half's tokens of each token's top-32 slots; averaged over the 4 heads |
| weighted overlap | per head, Σ_s min(p_a(s), p_b(s)), where p = the half's gate mass per slot (sum of the softmax weights that slot got), normalized to sum 1. This is the histogram intersection, 1 − total variation. Averaged over the 4 heads. |
| partner retrieval top-1 | the fraction of halves whose most similar other half in the batch (by that measure) is the partner. Chance is 1/(N − 1) = 0.0085. |

Distributions are pooled over the 20 batches. They are reported as mean, median, 10th percentile (p10) and 90th percentile (p90).

**Caveat on the slot measures.** A Jaccard of unions depends on half length, because longer halves have larger sets. Bio halves are short (about 40 tokens), Pile halves are long. So compare the slot rows within a pair type across checkpoints, not across pair types that mix bio and Pile.

## 1. Query cosine (the raw numbers behind the gap)

### query cosine: λ = 0 vs λ = 0.03 (mean / median / p10 / p90)

| pair type | n | λ=0 mean | med | p10 | p90 | λ=0.03 mean | med | p10 | p90 | Δ mean |
|---|---|---|---|---|---|---|---|---|---|---|
| partner (same piece) | 1212 | 0.789 | 0.808 | 0.662 | 0.891 | 0.888 | 0.912 | 0.793 | 0.951 | +0.100 |
| Pile, same subject, other doc | 13628 | 0.460 | 0.484 | 0.140 | 0.741 | 0.423 | 0.438 | 0.058 | 0.762 | -0.036 |
| adjacent across EOT (other doc) | 572 | 0.387 | 0.294 | -0.036 | 0.821 | 0.413 | 0.368 | -0.075 | 0.869 | +0.025 |
| Pile, different subject | 53768 | 0.122 | 0.096 | -0.122 | 0.414 | 0.018 | -0.017 | -0.237 | 0.330 | -0.104 |
| bio–bio, same person (other rewording) | 8 | 0.704 | 0.730 | 0.616 | 0.764 | 0.464 | 0.477 | 0.217 | 0.709 | -0.239 |
| bio–bio, different people | 16032 | 0.726 | 0.733 | 0.620 | 0.823 | 0.426 | 0.460 | -0.071 | 0.873 | -0.300 |
| bio–Pile | 64100 | -0.041 | -0.053 | -0.207 | 0.144 | -0.097 | -0.078 | -0.372 | 0.128 | -0.056 |

Means for every checkpoint:

| pair type | init (step 0) | lambda 0 | lambda 0.003 | lambda 0.01 | lambda 0.03 |
|---|---|---|---|---|---|
| partner (same piece) | 0.922 | 0.789 | 0.803 | 0.831 | 0.888 |
| Pile, same subject, other doc | 0.754 | 0.460 | 0.452 | 0.458 | 0.423 |
| adjacent across EOT (other doc) | 0.918 | 0.387 | 0.356 | 0.341 | 0.413 |
| Pile, different subject | 0.709 | 0.122 | 0.084 | 0.060 | 0.018 |
| bio–bio, same person (other rewording) | 0.699 | 0.704 | 0.705 | 0.730 | 0.464 |
| bio–bio, different people | 0.770 | 0.726 | 0.749 | 0.739 | 0.426 |
| bio–Pile | 0.726 | -0.041 | -0.112 | -0.148 | -0.097 |

**The gap, decomposed.** The pilot's `gap` is the partner cosine minus the mean cosine to all other halves. At λ = 0 that is 0.79 − (a mix dominated by the bio–Pile and different-subject pairs, around 0.15) = 0.64. Against the harder comparisons the margin is:

| margin (query cosine) | init | λ=0 | λ=0.03 |
|---|---|---|---|
| partner − same subject | 0.168 | 0.329 | 0.465 |
| partner − adjacent across EOT | 0.004 | 0.402 | 0.475 |
| partner − different subject | 0.213 | 0.667 | 0.870 |
| bio same person − bio different people (n = 8) | −0.071 | −0.022 | 0.038 |

## 2. Slot overlap

### slot Jaccard (union over tokens, mean over 4 heads): λ = 0 vs λ = 0.03 (mean / median / p10 / p90)

| pair type | n | λ=0 mean | med | p10 | p90 | λ=0.03 mean | med | p10 | p90 | Δ mean |
|---|---|---|---|---|---|---|---|---|---|---|
| partner (same piece) | 1212 | 0.263 | 0.241 | 0.153 | 0.387 | 0.285 | 0.261 | 0.185 | 0.403 | +0.022 |
| Pile, same subject, other doc | 13628 | 0.165 | 0.155 | 0.062 | 0.285 | 0.163 | 0.152 | 0.061 | 0.284 | -0.002 |
| adjacent across EOT (other doc) | 572 | 0.096 | 0.058 | 0.018 | 0.198 | 0.108 | 0.051 | 0.017 | 0.239 | +0.012 |
| Pile, different subject | 53768 | 0.096 | 0.079 | 0.028 | 0.189 | 0.082 | 0.066 | 0.023 | 0.165 | -0.014 |
| bio–bio, same person (other rewording) | 8 | 0.201 | 0.202 | 0.173 | 0.223 | 0.241 | 0.246 | 0.212 | 0.271 | +0.041 |
| bio–bio, different people | 16032 | 0.182 | 0.178 | 0.147 | 0.221 | 0.207 | 0.204 | 0.170 | 0.247 | +0.025 |
| bio–Pile | 64100 | 0.026 | 0.025 | 0.014 | 0.039 | 0.022 | 0.022 | 0.011 | 0.032 | -0.004 |

Means for every checkpoint:

| pair type | init (step 0) | lambda 0 | lambda 0.003 | lambda 0.01 | lambda 0.03 |
|---|---|---|---|---|---|
| partner (same piece) | 0.174 | 0.263 | 0.266 | 0.270 | 0.285 |
| Pile, same subject, other doc | 0.134 | 0.165 | 0.166 | 0.166 | 0.163 |
| adjacent across EOT (other doc) | 0.104 | 0.096 | 0.099 | 0.099 | 0.108 |
| Pile, different subject | 0.126 | 0.096 | 0.094 | 0.089 | 0.082 |
| bio–bio, same person (other rewording) | 0.074 | 0.201 | 0.201 | 0.209 | 0.241 |
| bio–bio, different people | 0.079 | 0.182 | 0.188 | 0.188 | 0.207 |
| bio–Pile | 0.078 | 0.026 | 0.025 | 0.025 | 0.022 |

### gate-mass-weighted overlap (Σ min, mean over 4 heads): λ = 0 vs λ = 0.03 (mean / median / p10 / p90)

| pair type | n | λ=0 mean | med | p10 | p90 | λ=0.03 mean | med | p10 | p90 | Δ mean |
|---|---|---|---|---|---|---|---|---|---|---|
| partner (same piece) | 1212 | 0.374 | 0.343 | 0.198 | 0.579 | 0.399 | 0.362 | 0.235 | 0.595 | +0.025 |
| Pile, same subject, other doc | 13628 | 0.231 | 0.221 | 0.072 | 0.407 | 0.221 | 0.209 | 0.071 | 0.392 | -0.010 |
| adjacent across EOT (other doc) | 572 | 0.122 | 0.063 | 0.015 | 0.265 | 0.134 | 0.054 | 0.014 | 0.302 | +0.012 |
| Pile, different subject | 53768 | 0.115 | 0.088 | 0.021 | 0.252 | 0.092 | 0.067 | 0.015 | 0.208 | -0.022 |
| bio–bio, same person (other rewording) | 8 | 0.283 | 0.291 | 0.237 | 0.309 | 0.325 | 0.333 | 0.283 | 0.364 | +0.042 |
| bio–bio, different people | 16032 | 0.244 | 0.238 | 0.193 | 0.301 | 0.272 | 0.267 | 0.222 | 0.328 | +0.028 |
| bio–Pile | 64100 | 0.021 | 0.020 | 0.009 | 0.036 | 0.018 | 0.017 | 0.007 | 0.029 | -0.004 |

Means for every checkpoint:

| pair type | init (step 0) | lambda 0 | lambda 0.003 | lambda 0.01 | lambda 0.03 |
|---|---|---|---|---|---|
| partner (same piece) | 0.289 | 0.374 | 0.377 | 0.381 | 0.399 |
| Pile, same subject, other doc | 0.212 | 0.231 | 0.231 | 0.226 | 0.221 |
| adjacent across EOT (other doc) | 0.180 | 0.122 | 0.123 | 0.123 | 0.134 |
| Pile, different subject | 0.196 | 0.115 | 0.113 | 0.101 | 0.092 |
| bio–bio, same person (other rewording) | 0.126 | 0.283 | 0.277 | 0.285 | 0.325 |
| bio–bio, different people | 0.135 | 0.244 | 0.245 | 0.247 | 0.272 |
| bio–Pile | 0.132 | 0.021 | 0.021 | 0.021 | 0.018 |

Margins and ratio, slot Jaccard:

| margin (slot Jaccard) | init | λ=0 | λ=0.03 |
|---|---|---|---|
| partner − same subject | +0.040 | +0.098 | +0.122 |
| partner − adjacent across EOT | +0.069 | +0.167 | +0.177 |
| partner − different subject | +0.048 | +0.167 | +0.203 |
| bio same person − bio different people (n = 8) | -0.005 | +0.019 | +0.034 |

Ratio of partner to different-subject slot Jaccard: init 1.38, λ = 0 2.73, λ = 0.03 3.49.

## 3. Partner retrieval

Top-1 retrieval of the partner among the batch's other halves (chance 0.0085):

| by | init (step 0) | lambda 0 | lambda 0.003 | lambda 0.01 | lambda 0.03 |
|---|---|---|---|---|---|
| query cosine | 0.622 | 0.434 | 0.475 | 0.560 | 0.803 |
| slot Jaccard | 0.346 | 0.493 | 0.500 | 0.510 | 0.542 |
| weighted overlap | 0.416 | 0.459 | 0.462 | 0.470 | 0.507 |


## 4. Metrics suite (λ = 0 vs λ = 0.03, step 1,500)

**How it was run.** `metrics.py` with pkm-s0's cohort flags (`runs/final/run_one.sh`: seed 17, 80 frequent people, 64 docs per subject, 256 doc tokens, lesion 64 plus 16 and 256, max prefix 16, MPS) and `--e2-facts runs/final/e2-cohort.json`.

**Which code.** It ran from a worktree of `claude/project-thread-g4yifr` (90c1ae5). That is the metrics code pkm-s0's cohort report came from: it has the float64 recheck of rank flips, the C6 MPS fix and the X2 fix, which are **not on main** and so not on this branch.
- A first run with this branch's metrics code failed the parity check on 3 facts (λ 0) and 1 fact (λ 0.03): float32 rank ties between near-equal candidates. That disabled every memory metric.
- The rerun rechecked those facts in float64, and they agree. Parity passed for both runs.
- The failed first outputs are kept in `runs/pilot_doc/metrics_main_code_parity_fail/`.

**pkm-s0 reference.** The pkm-s0 column is pkm-s0's cohort report at step 9,156, the fully trained model, for scale only.

| metric | measure | λ = 0 | λ = 0.03 | pkm-s0 @ 9,156 |
|---|---|---|---|---|
| Q1 | slice NLL, all text (nats/token) | 4.7108 | 4.7184 | — |
| Q2 | frequent / test top-1 (800 prompts) | 0.0238 | 0.0200 | 0.895 |
| Q2 | frequent / test mean rank (of 200 candidates) | 65.2 | 64.5 | 1.69 |
| Q2 | frequent / test gold margin (nats) | −1.267 | −1.227 | +2.080 |
| Q2 | control / test top-1 (people never seen) | 0.02 | 0.01 | 0.02 |
| Q2 | frequent / paraphrase top-1 | 0.0075 | 0.0075 | 0.127 |
| U4 | conditional MI slots ↔ subject (bits) | 0.580 | 0.652 | 0.637 |
| U4 | shuffle mean (bits) | 0.402 | 0.423 | 0.469 |
| U4 | **excess (bits)**, permutation p | **0.178**, p = 0.01 | **0.229**, p = 0.01 | 0.169 |
| E1 | mean specificity excess over control, lesion 64 (nats) | 0.00769 | 0.00644 | — |
| E1 | FreeLaw / Github / Pile-CC / PubMed / Wikipedia excess (nats) | 0.0218 / 0.0039 / 0.0032 / 0.0042 / 0.0054 | 0.0137 / 0.0049 / 0.0043 / 0.0030 / 0.0062 | 0.0237 / 0.0079 / 0.0058 / 0.0050 / 0.0070 |
| E2 | outcome counts over the 339-fact cohort (cumulative) | 323 unlearned discovery, 9 at chance, 4 prefix limit, 3 matched | 325 unlearned discovery, 7 at chance, 4 prefix limit, 2 matched, 1 no controls | 298 prefix limit, 22 matched, 22 no controls |
| Whole layer off | ΔNLL all text (nats/token) | +0.275 | +0.287 | — |
| U1 | slice coverage | 0.9831 | 0.9839 | — |

Columns and measures:
- **Q2 top-1**: the fraction of prompts where the gold answer has the highest log-probability among the 200 candidates; chance is 0.005.
- **Q2 margin**: gold log p minus the best wrong candidate's.
- **U4**: the conditional mutual information between the slot read and the document's subject, minus its mean under 99 subject shuffles ("excess").
- **E1**: the NLL rise on a subject's text when its 64 most subject-specific slots are masked, beyond the rise on other subjects and beyond matched random-slot controls.
- **E2**: a per-fact outcome of masking the slots that fact reads. "Unlearned discovery" means the fact is not recalled before masking, so there is nothing to remove.
- **Whole layer off**: NLL with all 65,536 slots masked, minus intact.

At step 1,500 neither model knows the facts (frequent ≈ control), so Q2 and E2 say nothing about the loss yet. U4 is the one memory-use metric that moves clearly: subject information in slot use rises 29% at λ = 0.03, above the fully trained pkm-s0's 0.169. E1's per-subject differences are mixed and small.

## 5. What this means for the full run, and what I would adjust

**What the loss does at λ = 0.03.** It does change memory use in the intended direction:
- partner slot overlap +8% relative;
- the partner-to-different-subject Jaccard ratio rises from 2.73 to 3.49;
- slot-based partner retrieval goes from 49% to 54%;
- U4 excess +29%.

**But the query-cosine gap overstates it.** Most of the change is in the direction of the pooled (mean) query, which the per-token top-32 search only partly follows. The clearest case is bios of different people: their query cosine falls by 0.30, yet their slot overlap rises.

**What the full run as-is would answer.** Whether a mild document-consistency push on memory reads changes fact recall and E1/E2 at 9,156 steps. Facts are only learned late, so the pilot cannot predict that. The expected effect on reads is modest. With one seed, a small fact-recall change would also be hard to separate from seed noise: the three PKM seeds already differ on these metrics.

**Adjustments to consider before the long run, cheapest first:**
1. **Larger λ.** 0.03 was the top of the grid and cost only +0.15% held-out loss, about a seventh of the 1% budget. Two more pilot runs (λ 0.1 and 0.3, about 33 min each), checked with this script, would show whether slot overlap keeps rising and where held-out loss starts to pay. This is outside the fixed rule, so it is your call.
2. **Make the loss act on what the top-k sees.**
   - Center the query vectors before pooling, by subtracting the batch mean query, so the loss cannot be satisfied by one shared direction.
   - Or apply the InfoNCE per token, each token's query against the other half's mean, instead of on half means.
   - Either is a small, default-off change to `doc_loss.py` and needs one new pilot run.
3. **Pick the success criterion now, on reads rather than on query cosine.** For example: the partner / different-subject slot Jaccard ratio, plus U4, at step 1,500. Then use fact recall and E2 at 9,156 steps for the real question.
