# Phase 2: the full `pkm_doc` run, ready to launch (λ = 0.1)

Status (2026-11-24): everything below is checked, and **the run has not been started**. Roie gives the go.

## Launch

From the repo root, on branch `phase2/doc-loss`, with the Mac on power and the lid open:

```bash
nohup caffeinate -dimsu .venv/bin/python -m memlayers.run experiment=pkm_doc seed=0 runtime=mac logging=wandb > runs/pkm_doc-s0.launch.log 2>&1 &
```

- **Run dir:** `runs/pkm_doc-s0/` (run id `pkm_doc-s0`). It does not exist yet.
- **W&B:** project `memlayers`, online.
- **Progress:**
  - `tail -f runs/pkm_doc-s0/stdout.log`
  - `runs/pkm_doc-s0/status.json`
  - `runs/pkm_doc-s0/train_log.csv`. The `doc_*` columns show the loss.
- **If it dies or the Mac sleeps:** run the same command again. `resume=true` is the default, so `memlayers.run` resumes from `checkpoints/last.pt`. That checkpoint is written at every eval point and every 20 minutes.

## After the run: metrics with pkm-s0's cohort flags

```bash
runs/final/run_one.sh runs/final/cohort/pkm_doc-s0 runs/pkm_doc-s0/checkpoints/step_009156.pt --e2-facts runs/final/e2-cohort.json
```

- This is the exact command shape the pkm-s0/s1/s2 cohort reports used: seed 17, 80 frequent people, 64 docs per subject, 256 doc tokens, lesion 64 plus 16 and 256, max prefix 16, MPS.
- It takes about 20 minutes and writes `runs/final/cohort/pkm_doc-s0/step_009156-*.json` and `.html`.
- The metrics code on this branch now includes the three fixes the cohort reports were made with. They are cherry-picked from `claude/project-thread-g4yifr` with `-x`:
  - 7e30e8f: C6, value rows are copied to CPU before the float64 cast.
  - f863d15: parity check, float32 rank flips are rechecked in float64.
  - 4a24b60: X2, the twin is compared in its JSON form.
- `metrics/` and `metrics.py` are now identical to that branch. Without f863d15, the parity check fails on these checkpoints (float32 ties) and disables every memory metric (see `reports/doc_loss_precheck_report.md`).

## Checks done

### 1. Resolved config vs pkm-s0

I compared the resolved config of `experiment=pkm_doc seed=0 runtime=mac logging=wandb` with `runs/final/hf_meta/pkm-s0/config.yaml`, key by key. These are **all** the differences:

| key | pkm_doc | pkm-s0 | kind |
|---|---|---|---|
| `train.doc_loss_weight` | 0.1 | — | the loss |
| `train.doc_loss_ramp_steps` | 1000 | — | the loss |
| `train.doc_loss_temperature` | 0.5 | — | the loss |
| `train.doc_loss_min_piece_tokens` | 32 | — | the loss |
| `train.doc_loss_layer` | null (layer 3, the only memory layer) | — | the loss |
| `train.doc_loss_eot_id` | 50256 | — | the loss |
| `name`, `run_id` | pkm_doc, pkm_doc-s0 | pkm, pkm-s0 | naming |
| `runtime.device`, `runtime.precision` | mps, fp32 | cuda, auto (bf16 on an RTX A6000) | **machine: known caveat** |
| `out_root`, `runtime.out_dir`, `data.root` | runs, runs/pkm_doc-s0, data | cluster paths | machine |
| `resume_foreign` | false | true | launch flag |
| `logging.sink`, `logging.mode` | wandb, online | files, disabled | logging only |

Everything else is identical:
- the model (6 layers, d 384, PKM at layer 3, 65,536 slots, 4 heads, top-k 32, query BatchNorm);
- data v1 with seed 0;
- training: `steps` 9,156, micro-batch 32 × 1, LR 2.5e-4 and memory values 1e-3, warmup 30, cosine to 0.1, clip 1.0, weight decay 0.1 / 0, `train.seed` 0, `ckpt_every` 500;
- eval: `steps` [0, 247, 504, 998, 1500, 1996, 3498, 4999, 7004, 9156], the same metric lists, the same training-check thresholds.

Each eval point saves `checkpoints/step_<n>.pt` and `last.pt`.

**Caveat:** pkm-s0 trained in bf16 autocast on CUDA, `pkm_doc` trains in fp32 on MPS. The memory layer itself runs in fp32 in both. A difference between the two runs therefore mixes the loss with the precision and hardware difference. The pilot's λ = 0 vs λ = 0.1 comparison at step 1,500 is the clean one.

### 2. Tests

The full suite passes: **499 passed, 1 skipped**. That includes the three cherry-picked metrics fixes and the `pkm_doc` config test, now at 0.1.

### 3. MPS smoke test with the final config

All three runs were throwaway and have been deleted. Their logs are kept outside the repo.

- **A:** `experiment=pkm_doc seed=0 runtime=mac logging=wandb train.steps=60 eval.steps=[0,30] train.log_every=1 tag=ready-check` with `MEMLAYERS_TEST_HALT=30:exit:ckpt`. It killed itself (exit 137) right after the step-30 eval checkpoint.
- **B:** the same command again. It resumed from `last.pt` at step 30, ran to 60 and finished `done`. `meta.json` recorded the resume and no device change.
- **C:** a straight 60-step twin, `logging=files`.

Results:
- **The doc loss is on:** `doc_loss`, `doc_weight`, `doc_gap` and `doc_halves` are filled at every step (for example step 31: doc_loss 4.50, doc_gap 0.087, 106 halves).
- **The λ ramp is correct:** the row for step *s* logs `doc_weight = 0.1 × (s − 1) / 1000`, the λ the step ran with (λ uses the step counter before it increments). Examples: step 1 → 0.0, step 2 → 0.0001, step 31 → 0.0030, step 60 → 0.0059. So λ reaches 0.1 at the step logged as 1,001.
- **Evaluation works with the loss on:** the evaluation at steps 0 and 30 ran with the query hook registered, and `evals.csv` was written.
- **Resume works:** after the resume, losses match the straight run to within 2.7e-5 (steps 31–60), and to within 1.7e-5 before it. MPS is not bit-deterministic, and this is the same size as run-to-run noise. Final loss at step 60: 7.666428 (resumed) vs 7.666413 (straight).
- **W&B works:** online run `wq60k66i` in project `memlayers`. It was resumed by B under the same id, and `wandb_sync.json` shows train steps up to 60 and both eval points synced. This throwaway run is still in the W&B project; delete it there if you want it gone.

### 4. Disk

- 1.6 TiB free.
- The full run needs about 3–4 GB: ten eval checkpoints of 209 MB, `last.pt` at 627 MB, logs and slot-usage files.
- The pilot checkpoints in `runs/pilot_doc/` (6.3 GB) are kept. The pilot and precheck reports were computed from their `step_001500.pt`, and nothing needs the space.

### 5. Expected time

- **Training:** 9,156 steps × 1.23–1.42 s, the range of the pilot medians on this Mac (λ 0.3 ran at a flat 1.258 s). That is **3.1–3.6 h**.
- **During-training evals:** 9 points × about 110 s (earlier MPS runs), about 17 min.
- **Final full-set evaluation at step 9,156:** about 9 min.
- **Total:** about **3.5–4.1 h** from launch to `done`, then about 20 min for the cohort metrics.
