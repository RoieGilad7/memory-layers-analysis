# Phase 2, prompt 2: the same-document loss in training

Branch `phase2/doc-loss`. It continues from prompt 1 (`reports/doc_loss_1_report.md`).

## 1. Files changed

| File | Change |
|---|---|
| `memlayers/train.py` | Six `doc_loss_*` keys on `OptimCfg`. `Trainer._setup_doc_loss` (checks, then `set_keep_queries(True, layer)`), `Trainer.doc_loss_lambda(step)`, `Trainer._doc_loss_term(x)`. The loss term goes in `train_step`, and four `doc_*` columns go in the returned row. |
| `memlayers/runlog/files.py` | `TRAIN_FIELDS` gets `doc_loss, doc_weight, doc_gap, doc_halves` |
| `memlayers/runlog/wandb_sink.py` | `TRAIN_KEYS` gets the same four |
| `conf/experiment/pkm_doc.yaml` (new) | `pkm` plus the loss and pkm-s0's eval steps |
| `conf/config.yaml` | comment only: `pkm_doc` added to the experiment list |
| `tests/fixtures/doc_loss_off_golden.json` (new) | 20 loss-off losses written from `main` (8ac8f6b) before any training edit |
| `tests/fixtures/make_doc_loss_off_golden.py` (new) | the script that wrote the fixture |
| `tests/test_doc_loss_train.py` (new) | 16 tests |
| `tests/test_config.py` | `pkm_doc` added to the experiment list, so it is composed with every runtime |
| `bench/doc_loss_halves_count.py` (new) | the real-data halves count below |

`memlayers/config.py` needed no change: `to_train_config` builds `OptimCfg(**train)`, so Hydra checks the new keys automatically.

**Training step.** Per micro-batch:
1. After the forward, `lam = weight * min(1, step/ramp)` (or `weight` when ramp = 0), where `step` is the step about to run.
2. `find_halves`, then `half_vectors` on the kept queries of the doc layer, then `doc_loss`.
3. `((loss + lam*dl).float() / grad_accum)` is backpropagated, through the scaler when there is one.
4. The kept queries are released after backward.

`total_loss`, and so the `loss` column, sums the LM loss only. With the weight at 0 the code takes the old line, `loss.float() / grad_accum`, unchanged. No hook is registered and no extra work runs.

**Columns.**
- `doc_loss` is the unweighted value. `doc_weight` is `lam`, `doc_gap` is the gap, `doc_halves` is the number of halves.
- They are averaged over the micro-batches whose gap is not None.
- If no micro-batch in a step has two pieces, `doc_loss = 0.0`, `doc_gap = ""`, and `doc_halves` is the mean count (0 or 2). That is a small addition to the spec so the column is never misleading.
- All four are empty strings when the loss is off.

**Trainer errors (weight > 0).** It fails with a clear message when:
- the model has no memory layer;
- there are several memory layers and `doc_loss_layer` is None;
- `doc_loss_layer` is not a memory layer;
- `runtime.compile` is true;
- temperature ≤ 0;
- `min_piece_tokens` < 2.

Two checks beyond the spec: a negative weight and a negative `ramp_steps` are rejected. A weight of exactly 0 runs no check and never calls `set_keep_queries`.

**Checkpoint and resume.** The checkpoint gets nothing new. `lam` depends only on `self.step`, which `load_checkpoint` restores before the first resumed step. The kept-queries hook is set up in `__init__` from the config, so a resumed Trainer has it again. The resume test checks this in a fresh process, resuming in the middle of the ramp.

## 2. pkm-s0's recorded config vs the composed `experiment=pkm seed=0 runtime=mac`

I compared `runs/final/hf_meta/pkm-s0/config.yaml` with the composed config, key by key:

| key | composed today | pkm-s0 recorded | kind |
|---|---|---|---|
| `eval.steps` | `null` (points) | `[0, 247, 504, 998, 1500, 1996, 3498, 4999, 7004, 9156]` | **schedule: copied into pkm_doc.yaml** |
| `runtime.device` / `runtime.precision` | `mps` / `fp32` | `cuda` / `auto` (meta.json: bf16 on an RTX A6000) | machine |
| `out_root`, `runtime.out_dir`, `data.root` | `runs`, `data` | cluster paths | machine |
| `resume_foreign` | false | true | launch flag |

Everything under `model`, `data` (apart from `root`), `train` and the rest of `eval` is identical. `pkm_doc.yaml` copies only `eval.steps`. Composed with `runtime=mac`, the only other differences from pkm-s0 are the `doc_loss_*` keys and the machine keys above.

**Open point:** pkm-s0 trained on CUDA with bf16 autocast, while `pkm_doc` on this Mac trains in fp32 on MPS. The memory layer is fp32 in both (`fp32_region`), but the rest of the network is not. So "only the loss differs" holds for the config, not for the hardware precision. If the full run should be compared with pkm-s0 directly, either run it on the same CUDA setup, or use the pilot's λ = 0 run as the baseline.

## 3. Halves per batch on real data

`bench/doc_loss_halves_count.py`: 50 batches of 32 × 512 windows in loader order (seed 0), EOT 50256.

| file | min_piece_tokens | mean | min | max | EOTs per batch |
|---|---|---|---|---|---|
| `data/v1/tokens/train.bin` (read-only memmap) | 32 | **124.4** | 80 | 168 | 36.6 |
| `data/v1/tokens/train.bin` | 16 / 64 | 128.2 / 117.0 | 84 / 78 | 174 / 152 | |
| `data/v1_sample/tokens/train.bin` | 32 | 130.3 | 88 | 178 | 40.1 |

This is in line with the ~120 halves per batch the λ estimate assumed.

## 4. MPS step time, loss on vs off (200 steps)

Commands:
```
.venv/bin/python -m memlayers.run experiment=pkm_doc seed=0 runtime=mac train.steps=200 eval=off eval.steps=null tag=doc-smoke
.venv/bin/python -m memlayers.run experiment=pkm     seed=0 runtime=mac train.steps=200 eval=off tag=doc-smoke-off
```

**Deviation from the prompt's command:** I added `eval.steps=null` to the `pkm_doc` command. As written, the command fails at launch with `eval.steps [247, …, 9156] outside 0..200`. The experiment file sets the absolute eval list after the `eval` group, so `eval=off` does not clear it. The pilot is unaffected because it keeps `train.steps = 9156`.

| run | median step_time_s (logged steps 30–200) | peak mem (driver) | loss at 200 |
|---|---|---|---|
| loss on (`pkm_doc`, λ ramping to 0.002 at step 200) | **1.2445 s** | 23.54 GB | 6.7140 |
| loss off (`pkm`) | **1.2436 s** | 23.54 GB | 6.7149 |

- The loss costs about +0.07% per step, which is within noise.
- Both runs log every 10th step (`log_every 10`), so the medians are over the 18 logged rows in steps 21–200.
- The step-10 losses differ only in the 6th digit, because λ is tiny early in the ramp.

`doc_*` columns of the loss-on run:

| step | doc_loss | doc_weight | doc_gap | doc_halves |
|---|---|---|---|---|
| 10 | 4.823 | 0.00009 | 0.141 | 156 |
| 50 | 4.108 | 0.00049 | 0.160 | 80 |
| 100 | 4.255 | 0.00099 | 0.301 | 114 |
| 150 | 4.356 | 0.00149 | 0.362 | 140 |
| 200 | 3.866 | 0.00199 | 0.528 | 104 |

The gap is already rising with λ at 0.002. Part of that is probably ordinary training: the pilot measures the gap for λ = 0 too.

**Expected full-run time.** 9,156 steps × 1.2445 s ≈ **3.17 h** of training. On top of that come the ten eval points: the earlier MPS runs took a few minutes per during-training point, plus the final full-set evaluation.

## 5. Tests

- Before: 462 passed, 1 skipped (after prompt 1).
- After: **483 passed, 1 skipped**. That is +16 in `tests/test_doc_loss_train.py` and +5 from composing `pkm_doc` with each runtime in `test_config.py`.

New tests:
- **Golden:** 20 losses equal the fixture exactly, and no query hook is registered. The fixture uses `grad_accum_steps=2`, so the accumulation path is covered.
- **Loss on:** kept queries exist, the `doc_*` columns are filled, and the queries are released after backward. The logged `loss` at step 1 equals the loss-off value, so it is the LM loss only.
- **Ramp:** values at steps 0, half, full and beyond, plus ramp = 0.
- **Config:**
  - `pkm_doc` composes with the fixed values and equals `pkm` in model, data and every other train key.
  - A misspelled `train.doc_loss_wieght` fails at compose time.
  - Each Trainer error fires, including the compile one.
- **Columns:** `TRAIN_FIELDS` and `TRAIN_KEYS` contain the four names. Empty values are not sent to W&B. A log with the old header keeps that header, and a fresh log gets the new one.
- **Resume:** 30 steps straight vs 15 + save + resume (fresh process) + 15, with the loss on and the resume mid-ramp. Tolerance is 1e-4, as in the existing resume test.
- **Smoke:**
  - Setup: tiny PKM, 60 steps, an injected dataset of 63-token topic documents separated by EOT 256, weight 1.0, ramp 0.
  - Mean `doc_gap` over the last 10 steps is above the first 10.
  - All losses are finite.

## 6. Deviations and open questions

1. `eval.steps=null` had to be added to the 200-step `pkm_doc` command (section 4).
2. When no micro-batch in a step has two pieces, `doc_halves` still reports the count, and `doc_loss` is 0.0 rather than empty (section 1).
3. Negative `doc_loss_weight` and negative `doc_loss_ramp_steps` are rejected (not in the spec).
4. **Resume across this change.** `memlayers.run` refuses to resume a run dir whose saved `config.yaml` differs from the new config outside `RESUME_ALLOWED`. A run that was interrupted before this branch would now see six new `train.doc_loss_*` keys (`<absent>` → default) and be refused. No such run is pending as far as I know (the final runs are done), so I left `run.py` unchanged. If it matters, treating absent `doc_loss_*` keys as the off defaults is a two-line change.
5. pkm-s0 used CUDA bf16, `pkm_doc` on the Mac uses MPS fp32 (section 2).
