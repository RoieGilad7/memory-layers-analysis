# Training 5 — CUDA runtimes, a CI smoke job, and the real-data pilot

Branch `train/run-layer`, training prompt 5 of 5. This step does three things:
- the same run command now works on CUDA machines (Colab and any remote GPU)
  as well as the Mac and CPU;
- CI runs a real smoke run and compare;
- a 1,500-step real-data pilot on the Mac sets the remaining numbers.

After this the five Phase 1 runs can start (section 4).

## 1. Runtimes and precision rules

`conf/runtime/`, each setting `device`, `precision`, `compile`, `ckpt_minutes`
(and, for Colab, paths):

| runtime | device | precision | notes |
|---|---|---|---|
| `auto` (default) | CUDA > MPS > CPU | `auto` | that device's default precision |
| `mac` | mps | fp32 | as every run so far |
| `cpu` | cpu | fp32 | tests and CI |
| `cuda` | cuda | `auto` | bf16 autocast on compute capability ≥ 8.0 (A100, L4, H100); fp16 autocast + GradScaler below (T4, V100); `compile: false`, `true` allowed |
| `colab` | cuda | `auto` | plus `out_root=/content/drive/MyDrive/memlayers/runs`, `data.root=/content/drive/MyDrive/memlayers/data`, `ckpt_minutes: 15`, `logging.mode: offline` |

`colab` is a global-package config so it can set `out_root`, `data.root` and
`logging.mode`. To allow that, `_self_` now comes before the groups in
`conf/config.yaml`. The command line still wins over everything.

**Precision rules as implemented:**
- **Resolution.** `memlayers/devices.py:resolve_precision` turns
  `runtime.precision` (`auto | fp32 | bf16 | fp16`) into a dtype and a
  scaler flag. An explicit `bf16` on a GPU below 8.0 is refused.
- **Weights.** Master weights and the AdamW state stay fp32. `autocast` wraps
  only the forward and the loss (`Trainer._autocast`).
- **fp16 scaler.** With fp16, a `torch.amp.GradScaler` scales the loss and
  unscales before clipping, so the clip sees true gradients. It skips steps
  with inf/NaN gradients. Its state goes into `last.pt`.
- **The memory layer runs entirely in fp32.** `PKMMemory.forward` and
  `PEERMemory.forward` cast their input to fp32 and run inside
  `fp32_region()` (autocast disabled). The wrapper is in `memlayers/memory.py`,
  not a patch to `product_key_memory`. The query projection, sub-key scores,
  top-k, softmax and value sum are all fp32, so mixed precision cannot change
  which slots are read. This is more than a nicety: without the wrapper, PKM
  under CPU bf16 autocast does not even run (`embedding_bag` refuses bf16 gate
  weights against fp32 values).
- **Checkpoints and metadata.** Eval checkpoints stay fp32 (`save_weights`
  casts). `meta.json` records `precision`, `gpu_name`, `gpu_capability` and
  `compile`, and W&B tags use the resolved precision.
- **Compile.** `runtime.compile=true` wraps the training forward in
  `torch.compile`. Evaluation uses the uncompiled model.

**Data root.** `data.root` (default `data`) moves every bundle path. The
committed manifests stay in the repo.
- `python -m data.fetch --version v1 --data-root <dir>` downloads and verifies
  there, and `python -m memlayers.eval.eval_sets --data-root <dir>` builds the
  eval sets there.
- A run refuses to start on any hash mismatch, as before.
- `data.bundle` points at one bundle's own directory. It replaces prompt 3's
  `data.root`, which the smoke experiments used for `data/v1_sample`.

**Disconnect safety.** `last.pt` is written atomically on the
`runtime.ckpt_minutes` timer and at every eval point. Re-running the same
command resumes. A resume on a different device type, GPU or precision is
allowed (a Colab reconnect may get another GPU) but recorded in
`meta.json.device_changes`. `memlayers.compare` warns about it, and `runs.csv`
has `device_changed` and `gpu_name` columns.

**Device-mix guard.** Compare already warns when one experiment mixes devices
or precisions; precision now comes from the resolved value in `meta.json`. The
README states the rule: all runs of one comparison group on one device type
and precision.

## 2. The Colab notebook

`notebooks/colab_run.ipynb` (outputs cleared; tested as valid nbformat-4
JSON):
1. Variables at the top: `REPO_COMMIT`, `EXPERIMENT`, `SEED`, `TAG`, `EXTRA`,
   `USE_WANDB`.
2. Mounts Drive.
3. Clones the repo at `REPO_COMMIT`.
4. Installs the pinned torch 2.14.1 CUDA wheel and `requirements.txt`, and
   prints the GPU and its compute capability.
5. Fetches data v1 onto Drive and checks or builds the eval sets there.
6. Optional W&B login from Colab's Secrets panel (`userdata.get("WANDB_API_KEY")`;
   no key in the notebook). Without the secret it mirrors offline.
7. Runs `python -m memlayers.run experiment=… seed=… runtime=colab …`.
   Re-running the cell resumes.
8. Runs compare on the Drive run dir.

**It was not run.** There is no Colab session from this machine. The first
Colab run is left to a person. Its CUDA paths are covered by the
mocked-capability tests and the CPU autocast and scaler tests (section 5).

## 3. The pilot

The command was `experiment=pkm seed=0 tag=pilot runtime=mac train.steps=1500
eval.steps=[0,250,500,1000,1500] logging=wandb logging.mode=offline`. There is
no W&B login (offline run `v8kbb2mr`). It ran under `caffeinate -dimsu` on
MPS, real v1 data, fp32. The read-log pass ran on init and final, then
`memlayers.evaluate … step=final`, then compare on the pilot alone
(`reports/compare_pilot/`). Nothing was deleted from `runs/pkm-s0-pilot/`.

**No sleep this time.** The wall-clock stamps match the `perf_counter` sums:

| phase | wall | measured work |
|---|---:|---:|
| the run | 47:11 (2,831 s) | ≈ 1,830 s of steps + 969 s of evals + startup |
| the read-log pass | 264 s | 129 + 131 s |
| the evaluate pass | 516 s | 514 s |

**Training speed.** Median 1.220 s/step and 13,427 tokens/s (micro-batch 32 ×
512), the same as the step-1 benchmark (~13.4k tokens/s) and prompt 1's check.
Peak MPS driver memory: 23.84 GB.

**Eval cost** (perf_counter, seconds):

| point | held-out pass (heldout_quality) | fact_recall | slot_usage | total |
|---|---:|---:|---:|---:|
| step 0, during | 61.4 | 62.0 | 0.01 | 124.3 |
| step 250, during | 54.9 | 57.0 | 0.01 | 112.0 |
| step 500, during | 54.1 | 55.2 | 0.01 | 109.4 |
| step 1000, during | 55.2 | 56.4 | 0.01 | 111.6 |
| step 1500, final (full sets) | 398.5 | 113.7 | 0.01 | 512.2 |
| step 1500, posthoc (full) | 397.8 | 114.4 | 0.01 | 513.6 |

The step-0 eval ran while I was running the test suite on the same machine;
the others are clean. A during eval costs ~110 s, under the 3-minute line, so
**the held-out sample stays at 200 documents per subject**.

**Projected eval overhead for a full 9,156-step run with the default 9
points:** 8 × ~111 s + 512 s ≈ 1,400 s = **23.3 min**, on top of 9,156 × 1.22 s
= **3.10 h** of training. That is 12.5%, about **3.5 h per run**.

**Sample vs full noise.** At step 1500 the sample's `pile_avg` loss is 5.041
and the full test half's is 5.232. That is a 3.7% level difference, not noise.
The two weight the subjects differently: the 200-document sample is
token-heavy in PubMed and FreeLaw, while the full half has ~2.5M tokens per
subject. That is why the training check reads the curve on the sample's
documents at every point (`loss/pile_avg_sample` at the end) and quotes the
full number separately.

**Sizes:**

| file | size |
|---|---:|
| `checkpoints/step_<n>.pt` (weights, fp32) | 219,158,003 B |
| `checkpoints/last.pt` | 657,494,029 B |
| `readlogs/step_<n>/` (init and final) | 2.947 GB each (two 1,468,367,360 B binaries + 10 MB tokens.parquet) |
| the pilot run dir in all | 5 × 219 MB + 657 MB + 2 × 2.947 GB ≈ 7.6 GB |

**Slot usage on layer 3** (65,536 slots; during = 200-doc sample, final = full
test half):

| step | coverage | best coverage | KL from uniform (nats) |
|---:|---:|---:|---:|
| 0 | 0.99998 | 0.973 | 0.69 |
| 250 | 0.797 | 0.184 | 2.46 |
| 500 | 0.929 | 0.307 | 1.87 |
| 1000 | 0.998 | 0.615 | 1.20 |
| 1500 (final, full) | **0.99995** | **0.892** | **1.04** |

Usage concentrates early, at step 250, then spreads back out as the values and
keys train. The final KL of 1.04 nats is far from uniform and far from
collapse (ln 65,536 = 11.09). This is a short, finished run: the cosine decays
fully within 1,500 steps. So these are the final numbers of a short run, not
of a full run at step 1,500.

**Quality at 1,500 steps** (25.6M tokens):
- Held-out `pile_avg` loss 5.232 (full) / 5.041 (sample); perplexity 187.2.
- Training loss at the last step 4.763.
- Fact recall, test role, top-1: frequent 0.0167, normal 0.0057, rare 0.0073,
  control 0.0040.
- The training check is **pass** on every gating rule:
  - finite;
  - no divergence (worst 1.18× its running minimum, at step 680);
  - learned (drop 53.3%);
  - not rising;
  - coverage 0.99995;
  - fact_learning (frequent 4.2× control);
  - flattening ratio 0.32 (reported only).

### Chosen numbers

- **`eval.training_check.min_coverage = 0.8`** (was the 0.5 placeholder).
  - The pilot's final coverage is 0.99995. On the full test half that is
    15M tokens × 128 reads, about 29,000 reads per slot on average, so a
    healthy layer touches essentially every slot.
  - A collapse (most reads funnelled into a fraction of the slots) leaves many
    slots unread even at that volume. The prompt-3 smoke runs show the shape
    of that: an untrained tiny layer covered 16–27%.
  - 0.8 sits far below a healthy run and far above a collapsed one. It also
    sits just above the transient dip to 0.797 at step 250, which was on the
    200-document sample, not the full set the rule reads.
  - A full 9,156-step run has 6× more training than the pilot, so it should
    end at least as spread. If a Phase 1 run lands between 0.8 and ~0.95,
    that is worth looking at, not a pass to ignore.
- **`eval.training_check.min_drop_from_init = 0.40`** (kept). The pilot clears
  it at 53.3% after only 25.6M tokens; a full run sees 150M.
- **Read-log budget: 1,000,000 tokens per subject** (kept, so the
  readlog_tokens hash `d4f2756e…` is unchanged). 2.95 GB and ~130 s per
  checkpoint is practical.
- **The held-out sample stays at 200 documents per subject** (a during eval is
  ~110 s, under 3 min).

### Phase 1: projected time and disk

| | per run | runs | total |
|---|---|---:|---|
| training (9,156 × 1.22 s) | 3.10 h | 5 | 15.5 h (dense a little less) |
| evaluation (9 points) | 23.3 min | 5 | 1.9 h |
| read-log pass (init + final) | ~4.5 min | 4 | 0.3 h |
| **time** | **≈ 3.5 h** | | **≈ 17.7 h** of compute |
| eval checkpoints (9 × 219 MB) | 1.97 GB | 4 memory | 7.9 GB |
| `last.pt` | 0.66 GB | 4 memory | 2.6 GB |
| read logs (2 × 2.95 GB) | 5.89 GB | 4 memory | 23.6 GB |
| dense run (9 × ~119 MB + ~0.36 GB) | 1.4 GB | 1 | 1.4 GB |
| **disk** | | | **≈ 35.5 GB** (+ 7.6 GB for the pilot already on disk) |

The time assumes the Mac stays awake: `caffeinate -dimsu` with the lid open.
In prompts 2–4, lid-closed sleep added 20–40 minutes per long run. The dense
model's checkpoint sizes are scaled from its 29.65M parameters; its step time
was not measured.

## 4. Phase 1 commands

```bash
# the five runs (Mac, MPS, fp32), one at a time
caffeinate -dimsu .venv/bin/python -m memlayers.run experiment=pkm         seed=0 runtime=mac logging=wandb logging.mode=offline
caffeinate -dimsu .venv/bin/python -m memlayers.run experiment=pkm         seed=1 runtime=mac logging=wandb logging.mode=offline
caffeinate -dimsu .venv/bin/python -m memlayers.run experiment=pkm         seed=2 runtime=mac logging=wandb logging.mode=offline
caffeinate -dimsu .venv/bin/python -m memlayers.run experiment=pkm_randkey seed=0 runtime=mac logging=wandb logging.mode=offline
caffeinate -dimsu .venv/bin/python -m memlayers.run experiment=dense       seed=0 runtime=mac logging=wandb logging.mode=offline

# optional, on the second Mac: run-to-run noise on MPS (same seed and data as pkm-s0;
# its own group, `pkm [repeat]`, never in the seed averages)
caffeinate -dimsu .venv/bin/python -m memlayers.run experiment=pkm seed=0 tag=repeat runtime=mac logging=wandb logging.mode=offline

# after each memory run: the read log on init and final (~4.5 min, 5.9 GB)
for r in pkm-s0 pkm-s1 pkm-s2 pkm_randkey-s0; do
  caffeinate -dimsu .venv/bin/python -m memlayers.readlog_pass run_dir=runs/$r step=[init,final]
done

# post-hoc evaluation when an analysis metric lands, e.g.
.venv/bin/python -m memlayers.evaluate run_dir=runs/pkm-s0 step=final metrics=[subject_specificity]

# compare (the pilot and the repeat are tagged, so they form their own groups)
.venv/bin/python -m memlayers.compare runs/ --out reports/compare_phase1/

# with a W&B login (`wandb login` once): upload the offline runs
.venv/bin/python -m memlayers.wandb_sync runs/pkm-s0 runs/pkm-s1 runs/pkm-s2 runs/pkm_randkey-s0 runs/dense-s0
```

Drop `logging.mode=offline` once the Mac has a W&B login.

All five must run on the same device type and precision (here MPS fp32). The
repeat run measures how far two identical MPS runs drift (prompt 1 saw 5.8e-5
in loss after 100 steps).

## 5. Test count and CI

**359 before → 378 after** (+19 in `tests/test_runtime.py`), all passing on CPU
(1:44 locally). Black is clean.
- Runtime selection with CUDA mocked:
  - capability 8.0 gets bf16 with no scaler;
  - 7.5 gets fp16 with a scaler, and bf16 is refused;
  - no CUDA falls back to MPS, then CPU, with fp32;
  - each of the 5 runtime configs resolves its device, precision, compile and
    timer (Colab's Drive paths and offline W&B);
  - an unknown precision is refused.
- PKM top-k under bf16 and fp16 CPU autocast equals fp32 on a fixed input:
  indices and weights identical, weights fp32, output fp32.
- Mixed-precision training on CPU:
  - fp16 with a real `GradScaler("cpu")` and bf16 both give finite losses for
    6 steps;
  - master weights stay fp32;
  - the precision and scaler state go into `last.pt` and meta.
- The `last.pt` timer: a run killed right after a timer save at step 3 (no
  `ckpt_every`) resumes at step 3 and logs steps 1–6 once each.
- meta records precision and device. A device change on resume is recorded
  (T4 → CPU in the test) and flagged by compare.
- `data.root`:
  - the committed 1% bundle copied to another folder is found and verified
    through `data.root`;
  - `data.fetch --data-root … --verify-only` passes;
  - a flipped byte is refused before step 0.
- The notebook: valid nbformat-4 JSON, outputs cleared, the required steps
  present, no key in it. `nbformat.validate` runs when nbformat is installed;
  it is not in this venv.

**CI** on `824cb9e`, the pull request run: all three jobs green.

| job | time |
|---|---:|
| unit tests | 310 s |
| black | 8 s |
| **smoke run + compare** (new) | 229 s: install 50 s, smoke run 168 s, compare 2 s |

The final commit's CI status is given in the PR.

## 6. Anything I could not follow, and open questions

1. **The Colab notebook was not run** (no Colab from here), and no CUDA run
   happened. The CUDA paths are tested with the capability mocked and through
   CPU autocast. The first T4 run will exercise the real fp16 + GradScaler
   path; check its first 100 losses against an MPS run's.
2. **`data.root` changed meaning from prompt 3.** It used to re-root one
   bundle (the sample); that is now `data.bundle`, and `data.root` is the
   folder holding the bundles, as this prompt specifies. Old smoke run dirs
   from prompt 3 (`runs/smoke_p3/`) carry the old key; they are disposable.
3. **`_self_` moved ahead of the groups** in `conf/config.yaml`, so `colab`
   can set `out_root` and `data.root`. Nothing else in the tree set those keys.
   All composition tests pass.
4. **The pilot's step-0 eval (124 s)** ran while the test suite shared the
   machine. The clean during evals are 109–112 s.
5. **The pilot's coverage dipped to 0.797 at step 250** before recovering.
   min_coverage gates only the final, full-set number. A gate on the curve
   (e.g. "never below X after step N") could be added if collapse is ever seen
   mid-run.
6. **Dense step time was not measured.** Phase 1's time projection uses the
   PKM step time for all five runs; the dense run should be a little faster.
7. **W&B** is still offline-only on this machine (no login). The pilot's
   offline run `v8kbb2mr` and every Phase 1 run can be uploaded later with
   `memlayers.wandb_sync`.
