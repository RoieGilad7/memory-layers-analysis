# Phase 2, prompt 3: pilot runs and the choice of lambda

`bench/doc_loss_pilot.py`, run detached on the Mac:
```
nohup caffeinate -dimsu .venv/bin/python bench/doc_loss_pilot.py > runs/pilot_doc/pilot.log 2>&1 &
```
It ran four runs of 1,500 steps, one after another, on 2026-11-23 between 13:24 and 15:39 local time. None died or restarted.

- Raw numbers are in `reports/doc_loss_pilot.json`, a copy of `runs/pilot_doc/summary.json`. It has the table rows and each run's full `done.json`, including every held-out key and the slot-usage keys.
- Run dirs are `runs/pilot_doc/l0`, `l0.003`, `l0.01` and `l0.03`. Each holds `log.csv`, `done.json`, `ckpt.pt` and `step_001500.pt`, and none of it is in git.

**Setup.**
- Each run uses the composed config of `experiment=pkm_doc runtime=mac seed=0` with `train.doc_loss_weight` set to that run's λ.
- Everything else is pkm_doc's: ramp 1,000, τ 0.5, min piece 32, and `train.steps` 9,156, so the LR schedule is the full run's. `trainer.train(steps=1500)`.
- One override was added, `train.log_every=1`, so every step's loss and step time are in the log. It is logging only.
- λ = 0 runs the loss-off code path, which prompt 2's golden test showed matches main exactly.

## 1. Results at step 1,500

| λ | held-out pile_avg | Δ vs λ=0 | train loss | gap | Δ gap vs λ=0 | coverage L3 | median step | Δ step |
|---|---|---|---|---|---|---|---|---|
| 0 | 4.76353 | — | 4.56226 | 0.64444 | — | 0.99986 | 1.2324 s | — |
| 0.003 | 4.76567 | +0.045% | 4.56270 | 0.69996 | +0.0555 | 0.99971 | 1.3229 s | +7.3% |
| 0.01 | 4.76353 | +0.000% | 4.56165 | 0.75349 | +0.1091 | 0.99982 | 1.3333 s | +8.2% |
| 0.03 | 4.77053 | +0.147% | 4.56621 | 0.83670 | +0.1923 | 0.99980 | 1.2629 s | +2.5% |

Columns:
- **held-out pile_avg**: `loss/pile_avg` of the `heldout_quality` metric, in nats per token. It is computed on the fixed during-training sample (200 documents per subject, per-document windows, eval mode), the same function and sample the in-training evals use. It is token-weighted over the 5 training subjects; USPTO is excluded.
- **Δ vs λ=0**: `100 × (loss / loss_λ0 − 1)`.
- **train loss**: mean of the logged `loss` column (the LM loss only, without the doc term) over steps 1,401–1,500, which is 100 values.
- **gap**:
  - Batches: 20 fixed batches of 32 × 512 real training windows, the first 20 batches of a `PackedDataset` over `data/v1/tokens/train.bin` seeded 12345, identical for every run.
  - Measurement: model in eval mode, no grad, query keeping on only for the measurement.
  - Value: per batch, the `doc_loss` stats "gap" (mean cosine of a half to its partner minus mean cosine to the other halves), averaged over the 20 batches. All 20 had at least 2 pieces, with 121.2 halves per batch on average.
- **coverage L3**: `coverage/layer3` of the `slot_usage` metric from that same held-out pass, the fraction of the 65,536 slots read at least once. It is the number the training check uses, not the cumulative training counter.
- **median step**: median `step_time_s` over steps 101–1,500.
- **Δ step**: `100 × (time / time_λ0 − 1)`.

**Step time.** The step-time differences are mostly machine variation, not the loss:
- They do not grow with λ (0.03 is faster than 0.01).
- They drift within a run: λ = 0.003 went from 1.244 s over steps 101–500 to 1.373 s over steps 1,001–1,500, and λ = 0.03 went from 1.306 s to 1.229 s.
- λ only scales a scalar, so the work per step is the same for every λ > 0.
- Prompt 2's A/B run measured the loss at +0.07% per step (1.2445 vs 1.2436 s).
- Medians per third of the run are in section 6.

## 2. Held-out loss per subject (nats per token)

| λ | pile_cc | github | pubmed_central | freelaw | wikipedia_en | uspto_backgrounds* |
|---|---|---|---|---|---|---|
| 0 | 5.7234 | 4.2290 | 4.8644 | 4.4251 | 5.6547 | 5.8616 |
| 0.003 | 5.7262 | 4.2331 | 4.8673 | 4.4253 | 5.6556 | 5.8659 |
| 0.01 | 5.7224 | 4.2341 | 4.8655 | 4.4219 | 5.6523 | 5.8628 |
| 0.03 | 5.7297 | 4.2496 | 4.8702 | 4.4280 | 5.6578 | 5.8718 |

\* USPTO is never trained on and is not part of `pile_avg`.

At λ = 0.03 every subject is slightly worse than at λ = 0, by +0.003 to +0.021 nats. GitHub moves most (+0.021, +0.49%).

## 3. doc_gap trend in the training log (λ > 0)

This is the `doc_gap` column at the given step. It is one training batch each, train mode, and λ is still ramping until step 1,000.

| λ | step 200 | step 500 | step 1000 | step 1500 |
|---|---|---|---|---|
| 0.003 | 0.628 | 0.792 | 0.710 | 0.729 |
| 0.01 | 0.713 | 0.813 | 0.772 | 0.779 |
| 0.03 | 0.787 | 0.841 | 0.825 | 0.849 |

Each value is a single batch, so it is noisy. The ordering by λ holds at every step.

## 4. The rule, applied

The rule was fixed before the runs: the largest λ > 0 that passes all of
- a. held-out pile_avg ≤ 1.01 × 4.76353 = **4.81117**;
- b. gap ≥ 0.64444 + 0.05 = **0.69444**;
- c. coverage ≥ **0.8**.

| λ | a. held-out ≤ 4.81117 | b. gap ≥ 0.69444 | c. coverage ≥ 0.8 | passes |
|---|---|---|---|---|
| 0.003 | 4.76567 ✓ | 0.69996 ✓ (margin 0.0055) | 0.99971 ✓ | yes |
| 0.01 | 4.76353 ✓ | 0.75349 ✓ | 0.99982 ✓ | yes |
| 0.03 | 4.77053 ✓ | 0.83670 ✓ | 0.99980 ✓ | yes |

**Chosen λ = 0.03**, the largest passing value. All three λ pass. λ = 0.03 is also the largest value tried, so the rule cannot say whether a larger λ would still pass. As fixed, no other λ was tried. `conf/experiment/pkm_doc.yaml` still says `doc_loss_weight: 0.01`; I did not edit it, as asked.

## 5. Expected full-run time with λ = 0.03

- Training: 9,156 steps × 1.263 s (the λ = 0.03 pilot median) ≈ 11,560 s ≈ **3.2 h**. With the 1.23–1.33 s range seen across runs, 3.1–3.4 h.
- During-training evals: the pilot's held-out and slot-usage pass took about 1 minute. The run's 9 during points also run fact recall and write checkpoints.
- Final evaluation: on the full sets, on top of the above.
- Estimate: about 3.5 h end to end, plus the final full-set evaluation.

## 6. Notes and open questions

1. **The baseline gap is already 0.64.** Same-document halves are far more similar than different-document halves without any loss, so criterion (b) is measured on top of that. λ = 0.003 passes (b) by only 0.0055.
2. **λ = 0.03 is the edge of the grid.** It costs +0.15% held-out loss, about a seventh of the 1% budget, and lifts the gap by 0.19, so the loss probably has room above 0.03. The fixed rule does not allow trying more.
3. **Step-time noise** (section 1). Medians per third of each run, steps 101–500 / 501–1,000 / 1,001–1,500:

   | λ | 101–500 | 501–1,000 | 1,001–1,500 |
   |---|---|---|---|
   | 0 | 1.233 s | 1.232 s | 1.232 s |
   | 0.003 | 1.244 s | 1.346 s | 1.373 s |
   | 0.01 | 1.343 s | 1.316 s | 1.338 s |
   | 0.03 | 1.306 s | 1.271 s | 1.229 s |

   For the full-run estimate I'd use the prompt 2 A/B result (+0.07%), not the pilot's Δ column.
4. **One override:** `train.log_every=1`. It changes no computed number; the alternative was a train-loss mean over 10 logged steps.
5. **Run-time checks:** the pilot's runs use the legacy Trainer layout, and the pilot does not run `memlayers.run`, so no training check or `evals.csv` was produced. The held-out and coverage numbers come from the same metric functions, called directly through `Evaluator.context(..., "during")` and `run_metrics`.
6. **Disk:** the four run dirs take 4.1 GB (a checkpoint with optimizer state plus two weight files each). Delete `runs/pilot_doc/*/ckpt.pt` (2.6 GB) if the space is needed. A finished run is skipped through its `done.json`, so the checkpoints are not needed again.

## Tests

- **Before / after:** 483 passed, 1 skipped before this prompt; 494 passed, 1 skipped after (+11 in `tests/test_doc_loss_pilot.py`).
- **Rule tests:**
  - it picks the largest passing λ, including a value exactly at the 1% edge;
  - it returns None when nothing passes;
  - a λ failing exactly one criterion is rejected, for each of a, b and c;
  - it requires the λ = 0 row.
- **Gap measurement:** it gives identical numbers twice, in train or eval mode, with keeping on or off. It leaves the train/eval mode, the keep-queries state and hook count, the BatchNorm running statistics and every parameter unchanged.
- **Dry run:** `--dry-run` runs end to end on CPU (smoke model on the committed `data/v1_sample`, 20 steps, λ = 0 and 0.03), and a restart skips the finished runs.
