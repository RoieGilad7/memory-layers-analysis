# Phase 2, pilot 2: larger λ (0.1 and 0.3) for the same-document loss

Roie approved two more pilot runs, outside the original fixed grid: λ = 0.1 and λ = 0.3. The full `pkm_doc` run has **not** been started, and `conf/experiment/pkm_doc.yaml` is unchanged (it still says 0.01).

**Runs.**
- Same setup as the first pilot (`reports/doc_loss_pilot_report.md`): `bench/doc_loss_pilot.py`, `experiment=pkm_doc runtime=mac seed=0`, 1,500 steps on the 9,156-step LR schedule, ramp 1,000, τ 0.5, min piece 32, `train.log_every=1`.
- Launched detached, one after the other: `nohup caffeinate -dimsu .venv/bin/python bench/doc_loss_pilot.py --lambdas 0,0.003,0.01,0.03,0.1,0.3`. The four earlier runs were skipped through their `done.json`.
- Logs: `runs/pilot_doc/pilot2.log`.
- Step-1,500 weights are kept in `runs/pilot_doc/l0.1/step_001500.pt` and `l0.3/step_001500.pt`.
- Summary of all six runs: `runs/pilot_doc/summary.json`, copied to `reports/doc_loss_pilot2.json`. The first pilot's summary is kept as `runs/pilot_doc/summary_pilot1.json`.

**Analysis.**
- Same as `reports/doc_loss_precheck_report.md`. Query and slot measures come from `bench/doc_loss_precheck.py --lambdas 0.1,0.3`, with raw numbers in `reports/doc_loss_precheck2.json`. The step-0, λ 0 … 0.03 numbers are the earlier `reports/doc_loss_precheck.json`. The step-0 reference was recomputed and is identical.
- Metrics suite: `metrics.py` with pkm-s0's cohort flags and `--e2-facts runs/final/e2-cohort.json`, run from a worktree of `claude/project-thread-g4yifr` (90c1ae5, the metrics code with the parity fix). Parity passed for all four checkpoints.
- Metrics outputs: `runs/pilot_doc/metrics/<run>/`, summarized in `runs/pilot_doc/metrics/summary.json` and in this report.
- Script: `runs/pilot_doc/pilot2_after.sh`.

## Takeaways

- **Held-out cost.** It grows steeply above 0.03: +0.15% at λ 0.03, **+0.65% at 0.1**, **+2.04% at 0.3**.
  - Under the original rule (≤ 1% held-out cost, gap +0.05, coverage ≥ 0.8), λ 0.1 is now the largest passing value. λ 0.3 fails (a) only.
  - At 0.3 every subject is worse, by +0.07 to +0.14 nats.
- **Slot reads.** The document effect on which slots are read keeps rising with λ:
  - partner slot Jaccard 0.263 (λ 0) → 0.285 (0.03) → **0.307 (0.1)** → 0.362 (0.3);
  - partner / other-subject Jaccard ratio 2.73 → 3.49 → **4.25** → 5.42;
  - partner retrieval by slots 49% → 54% → **62%** → 80%.
  - Same-subject other documents stay flat (0.165 → 0.159 at 0.1), so the gain is document-specific, not only topical.
- **Bios don't become person-specific.** In slot reads, bios of different people get *more* alike as λ grows (Jaccard 0.182 → 0.218 at 0.1 → 0.229 at 0.3). Same-person rewordings (only 8 pairs) stay at about the same small margin above different people (+0.02 to +0.03). In query cosine, different-person bios are pushed far apart (0.73 → 0.24 at 0.1), but the top-32 search does not follow.
- **U4.** Subject information in slot reads rises steadily: excess 0.178 → 0.229 → **0.258** → 0.290 bits (p = 0.01 for all).
- **The memory layer matters less at large λ.**
  - Whole-layer-off ΔNLL is 0.275 (λ 0), 0.287 (0.03), **0.255 (0.1)**, 0.175 (0.3).
  - E1 subject specificity falls 0.0077 → 0.0064 → **0.0062** → 0.0033 nats.
  - Slice coverage drops to 0.960 at 0.3, against 0.983 at λ 0.
  - At 0.3 the loss buys document-consistent reads at the cost of the memory's usefulness for the LM. At 0.1 this cost is visible but moderate: −7% layer-off effect, −19% E1.
- **Facts.** None are learned by step 1,500 at any λ. Frequent-tier test top-1 is 0.021–0.025, about the same as never-seen control people (0.01–0.03). E2 is "unlearned discovery" for 322–327 of 339 facts. Fact recall can only be judged in a full-length run.
- **Step time.** The loss is not a step-time cost; the differences between runs are machine variation.
  - λ 0.1's median of 1.418 s comes from a slow stretch: 1.301 s over steps 101–500, then 1.449 and 1.439 s.
  - λ 0.3 ran at a flat 1.258 s.
  - The A/B test in prompt 2 measured the loss at +0.07%.

**If a single λ is wanted for the full run,** 0.1 is the largest value within the 1% held-out budget, and it gives about twice λ 0.03's change in slot reads: partner Jaccard +0.044 vs +0.022, ratio 4.25 vs 3.49. Its price is +0.65% held-out loss and a memory layer that contributes somewhat less. λ 0.3 is too costly on every LM-side measure. This is a reading of the numbers, not a rule result beyond the one stated above. The choice is Roie's.

## Definitions

**Pilot table:**
- **held-out pile_avg**: `heldout_quality`'s `loss/pile_avg` on the fixed during-training sample (nats/token; token-weighted over the 5 trained subjects).
- **Δ vs λ=0**: `100 × (loss / loss_λ0 − 1)`.
- **train loss**: mean logged LM loss over steps 1,401–1,500.
- **gap**: mean `doc_loss` "gap" (partner cosine minus mean cosine to the other halves) on 20 fixed batches of 32 × 512 real training windows (loader seed 12345), eval mode, no grad.
- **coverage L3**: `slot_usage`'s `coverage/layer3` from that held-out pass.
- **median step**: median `step_time_s` over steps 101–1,500.
- **rule a / b / c**: the original rule's criteria. (a) held-out ≤ 1.01 × λ 0. (b) gap ≥ λ 0 + 0.05. (c) coverage ≥ 0.8.

**Query and slot tables:**
- The same 20 fixed batches. Halves come from `find_halves(x, 50256, 32)`, 121.2 per batch. Labels (document, Pile subject, bio person) come from `train.idx.parquet` and are used only for this analysis.
- **Pair types:**
  - **partner**: the two halves of one piece;
  - **Pile, same subject**: different documents, same subject;
  - **adjacent across EOT**: the last half of a piece and the first half of the next piece in the same row;
  - **Pile, other subject**;
  - **bio–bio, different people**;
  - **bio–bio, same person**: another rewording; only 8 pairs;
  - **bio–Pile**.
- **query cosine**: cosine of the two halves' mean memory queries (the vectors the loss uses).
- **slot Jaccard**: per head, |S_a ∩ S_b| / |S_a ∪ S_b| with S = the union of the half's tokens' top-32 slots, averaged over the 4 heads.
- **weighted overlap**: per head, Σ_s min(p_a(s), p_b(s)), with p = the half's gate mass per slot normalized to 1, averaged over heads.
- **retrieval**: the fraction of halves whose most similar other half in the batch is the partner; chance 1/(N − 1) = 0.0085.
- **Size caveat**: the slot measures depend on half length (bio halves are short), so compare a row across λ, not rows that mix bio and Pile.

**Metrics table** (step 1,500, pkm-s0's cohort flags):
- **Q1**: NLL on the 320-document slice.
- **Q2 top-1**: the gold answer ranks first among 200 candidates (chance 0.005). **margin**: gold log p minus the best wrong candidate's.
- **U4**: conditional MI between slot reads and subject, minus its mean under 99 shuffles.
- **E1**: the NLL rise on a subject when its 64 most specific slots are masked, beyond other subjects and random-slot controls.
- **Whole layer off**: the change when all 65,536 slots are masked.
- **E2**: per-fact masking outcomes.
- **U1**: the fraction of slots read on the slice.

## 1. Pilot runs at step 1,500 (all six λ)

| λ | held-out pile_avg | Δ vs λ=0 | train loss | gap | Δ gap | coverage L3 | median step | Δ step | rule a / b / c |
|---|---|---|---|---|---|---|---|---|---|
| 0 | 4.76353 | +0.000% | 4.5623 | 0.6444 | +0.0000 | 0.99986 | 1.2324 s | +0.0% | — |
| 0.003 | 4.76567 | +0.045% | 4.5627 | 0.7000 | +0.0555 | 0.99971 | 1.3229 s | +7.3% | ✓ / ✓ / ✓ |
| 0.01 | 4.76353 | +0.000% | 4.5617 | 0.7535 | +0.1091 | 0.99982 | 1.3333 s | +8.2% | ✓ / ✓ / ✓ |
| 0.03 | 4.77053 | +0.147% | 4.5662 | 0.8367 | +0.1923 | 0.99980 | 1.2629 s | +2.5% | ✓ / ✓ / ✓ |
| 0.1 | 4.79443 | +0.649% | 4.5872 | 0.9012 | +0.2567 | 0.99980 | 1.4181 s | +15.1% | ✓ / ✓ / ✓ |
| 0.3 | 4.86082 | +2.042% | 4.6518 | 0.9614 | +0.3170 | 0.99866 | 1.2576 s | +2.0% | ✗ / ✓ / ✓ |

## 2. Held-out loss per subject

Per-subject held-out loss (nats/token; USPTO is not trained on and not in pile_avg):

| λ | pile_cc | github | pubmed_central | freelaw | wikipedia_en | uspto_backgrounds |
|---|---|---|---|---|---|---|
| 0 | 5.7234 | 4.2290 | 4.8644 | 4.4251 | 5.6547 | 5.8616 |
| 0.003 | 5.7262 | 4.2331 | 4.8673 | 4.4253 | 5.6556 | 5.8659 |
| 0.01 | 5.7224 | 4.2341 | 4.8655 | 4.4219 | 5.6523 | 5.8628 |
| 0.03 | 5.7297 | 4.2496 | 4.8702 | 4.4280 | 5.6578 | 5.8718 |
| 0.1 | 5.7464 | 4.2971 | 4.8912 | 4.4466 | 5.6792 | 5.8908 |
| 0.3 | 5.7977 | 4.3644 | 4.9619 | 4.5113 | 5.7423 | 5.9392 |

## 3. doc_gap trend

Training-log doc_gap (one train batch, train mode; λ ramps until step 1,000):

| λ | 200 | 500 | 1000 | 1500 |
|---|---|---|---|---|
| 0.003 | 0.628 | 0.792 | 0.710 | 0.729 |
| 0.01 | 0.713 | 0.813 | 0.772 | 0.779 |
| 0.03 | 0.787 | 0.841 | 0.825 | 0.849 |
| 0.1 | 0.825 | 0.880 | 0.898 | 0.898 |
| 0.3 | 0.867 | 0.921 | 0.959 | 0.962 |

## 4. Query cosine and slot overlap by pair type (step 0, then λ 0 … 0.3 at step 1,500)

**Query cosine (mean over pairs)**

| pair type | step 0 | λ 0 | 0.003 | 0.01 | 0.03 | 0.1 | 0.3 |
|---|---|---|---|---|---|---|---|
| partner (same piece) | 0.922 | 0.789 | 0.803 | 0.831 | 0.888 | 0.925 | 0.973 |
| Pile, same subject, other doc | 0.754 | 0.460 | 0.452 | 0.458 | 0.423 | 0.370 | 0.242 |
| adjacent across EOT (other doc) | 0.918 | 0.387 | 0.356 | 0.341 | 0.413 | 0.327 | 0.189 |
| Pile, other subject | 0.709 | 0.122 | 0.084 | 0.060 | 0.018 | -0.028 | -0.011 |
| bio–bio, different people | 0.770 | 0.726 | 0.749 | 0.739 | 0.426 | 0.244 | 0.134 |
| bio–bio, same person (n = 8) | 0.699 | 0.704 | 0.705 | 0.730 | 0.464 | 0.195 | 0.221 |
| bio–Pile | 0.726 | -0.041 | -0.112 | -0.148 | -0.097 | -0.064 | -0.052 |

**Slot Jaccard, top-32 union per half, mean over 4 heads**

| pair type | step 0 | λ 0 | 0.003 | 0.01 | 0.03 | 0.1 | 0.3 |
|---|---|---|---|---|---|---|---|
| partner (same piece) | 0.174 | 0.263 | 0.266 | 0.270 | 0.285 | 0.307 | 0.362 |
| Pile, same subject, other doc | 0.134 | 0.165 | 0.166 | 0.166 | 0.163 | 0.159 | 0.153 |
| adjacent across EOT (other doc) | 0.104 | 0.096 | 0.099 | 0.099 | 0.108 | 0.111 | 0.114 |
| Pile, other subject | 0.126 | 0.096 | 0.094 | 0.089 | 0.082 | 0.072 | 0.067 |
| bio–bio, different people | 0.079 | 0.182 | 0.188 | 0.188 | 0.207 | 0.218 | 0.229 |
| bio–bio, same person (n = 8) | 0.074 | 0.201 | 0.201 | 0.209 | 0.241 | 0.249 | 0.252 |
| bio–Pile | 0.078 | 0.026 | 0.025 | 0.025 | 0.022 | 0.023 | 0.021 |

**Gate-mass-weighted slot overlap (Σ min), mean over 4 heads**

| pair type | step 0 | λ 0 | 0.003 | 0.01 | 0.03 | 0.1 | 0.3 |
|---|---|---|---|---|---|---|---|
| partner (same piece) | 0.289 | 0.374 | 0.377 | 0.381 | 0.399 | 0.429 | 0.501 |
| Pile, same subject, other doc | 0.212 | 0.231 | 0.231 | 0.226 | 0.221 | 0.215 | 0.205 |
| adjacent across EOT (other doc) | 0.180 | 0.122 | 0.123 | 0.123 | 0.134 | 0.142 | 0.153 |
| Pile, other subject | 0.196 | 0.115 | 0.113 | 0.101 | 0.092 | 0.079 | 0.069 |
| bio–bio, different people | 0.135 | 0.244 | 0.245 | 0.247 | 0.272 | 0.293 | 0.326 |
| bio–bio, same person (n = 8) | 0.126 | 0.283 | 0.277 | 0.285 | 0.325 | 0.335 | 0.361 |
| bio–Pile | 0.132 | 0.021 | 0.021 | 0.021 | 0.018 | 0.019 | 0.017 |

**Partner retrieval top-1 (chance 0.0085) and the slot ratio**

| measure | step 0 | λ 0 | 0.003 | 0.01 | 0.03 | 0.1 | 0.3 |
|---|---|---|---|---|---|---|---|
| retrieval by query cosine | 0.622 | 0.434 | 0.475 | 0.560 | 0.803 | 0.920 | 0.993 |
| retrieval by slot Jaccard | 0.346 | 0.493 | 0.500 | 0.510 | 0.542 | 0.619 | 0.802 |
| retrieval by weighted overlap | 0.416 | 0.459 | 0.462 | 0.470 | 0.507 | 0.571 | 0.722 |
| partner / other-subject slot Jaccard | 1.38 | 2.73 | 2.83 | 3.04 | 3.49 | 4.25 | 5.42 |

Distributions at λ 0.1 and 0.3 (mean / median / p10 / p90):

| pair type | measure | λ 0.1 | λ 0.3 |
|---|---|---|---|
| partner (same piece) | cos | 0.925 / 0.945 / 0.846 / 0.977 | 0.973 / 0.981 / 0.948 / 0.991 |
| partner (same piece) | jac | 0.307 / 0.289 / 0.204 / 0.417 | 0.362 / 0.353 / 0.260 / 0.469 |
| Pile, same subject, other doc | cos | 0.370 / 0.373 / -0.001 / 0.742 | 0.242 / 0.202 / -0.092 / 0.658 |
| Pile, same subject, other doc | jac | 0.159 / 0.149 / 0.060 / 0.274 | 0.153 / 0.141 / 0.056 / 0.268 |
| Pile, other subject | cos | -0.028 / -0.062 / -0.278 / 0.271 | -0.011 / -0.035 / -0.274 / 0.281 |
| Pile, other subject | jac | 0.072 / 0.058 / 0.020 / 0.144 | 0.067 / 0.054 / 0.019 / 0.134 |
| bio–bio, different people | cos | 0.244 / 0.237 / -0.384 / 0.873 | 0.134 / 0.046 / -0.296 / 0.723 |
| bio–bio, different people | jac | 0.218 / 0.215 / 0.179 / 0.260 | 0.229 / 0.224 / 0.183 / 0.282 |
| bio–Pile | cos | -0.064 / -0.046 / -0.308 / 0.142 | -0.052 / -0.050 / -0.252 / 0.141 |
| bio–Pile | jac | 0.023 / 0.023 / 0.011 / 0.035 | 0.021 / 0.021 / 0.010 / 0.033 |

## 5. Metrics suite (λ 0, 0.03, 0.1, 0.3 at step 1,500)

| metric | measure | λ 0 | λ 0.03 | λ 0.1 | λ 0.3 |
|---|---|---|---|---|---|
| Q1 | slice NLL, all text (nats/token) | 4.7108 | 4.7184 | 4.7477 | 4.8151 |
| Q2 | frequent / test top-1 | 0.0238 | 0.0200 | 0.0250 | 0.0213 |
| Q2 | frequent / test mean rank (of 200) | 65.2 | 64.5 | 63.4 | 64.2 |
| Q2 | frequent / test gold margin (nats) | -1.267 | -1.227 | -1.231 | -1.256 |
| Q2 | normal / test top-1 | 0.020 | 0.020 | 0.020 | 0.020 |
| Q2 | control / test top-1 (never seen) | 0.020 | 0.010 | 0.010 | 0.030 |
| Q2 | frequent / paraphrase top-1 | 0.0075 | 0.0075 | 0.0050 | 0.0063 |
| U4 | conditional MI (bits) | 0.580 | 0.652 | 0.699 | 0.741 |
| U4 | shuffle mean (bits) | 0.402 | 0.423 | 0.441 | 0.451 |
| U4 | **excess (bits)** | 0.178 | 0.229 | 0.258 | 0.290 |
| E1 | mean specificity excess, lesion 64 (nats) | 0.00769 | 0.00644 | 0.00624 | 0.00334 |
| Whole layer off | ΔNLL all text (nats/token) | +0.275 | +0.287 | +0.255 | +0.175 |
| Whole layer off | Δ frequent / test top-1 | -0.0163 | -0.0063 | -0.0150 | +0.0037 |
| U1 | slice coverage | 0.9831 | 0.9839 | 0.9835 | 0.9596 |
| E1 | per subject: FreeLaw / Github / Pile-CC / PubMed / Wikipedia | 0.0218 / 0.0039 / 0.0032 / 0.0042 / 0.0054 | 0.0137 / 0.0049 / 0.0043 / 0.0030 / 0.0062 | 0.0164 / 0.0049 / 0.0030 / 0.0021 / 0.0048 | 0.0025 / 0.0067 / 0.0031 / 0.0007 / 0.0036 |
| E2 | cumulative outcomes, 339 facts | 323 unlearned discovery, 9 at chance on test, 4 prefix limit reached, 3 matched | 325 unlearned discovery, 7 at chance on test, 4 prefix limit reached, 2 matched, 1 no matched controls | 322 unlearned discovery, 10 at chance on test, 6 prefix limit reached, 1 matched | 327 unlearned discovery, 5 at chance on test, 5 prefix limit reached, 2 matched |
| — | parity check | passed | passed | passed | passed |
