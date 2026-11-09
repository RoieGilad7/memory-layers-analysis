# Training 1 — the generic run layer (Hydra, one entry point, safe re-runs)

Branch `train/run-layer`, training prompt 1 of 5. This step adds the configs and
the run directory that the real training runs will use. The training loop is
unchanged: `memlayers/train.py:Trainer` still does the training. On the same
seed, the new entry point reproduces the old CLI on MPS to within MPS noise
(section 7).

```bash
python -m memlayers.run experiment=pkm seed=0                     # -> runs/pkm-s0/
python -m memlayers.run experiment=pkm seed=0 train.steps=200 tag=pilot   # -> runs/pkm-s0-pilot/
python -m memlayers.run -m experiment=pkm seed=0,1,2              # three runs, one after another
python -m memlayers.run experiment=smoke runtime=cpu              # ~2 s health check
```

New code: `memlayers/run.py` (entry point, run-dir lifecycle), `memlayers/config.py`
(structured-config schema, `to_train_config`), `memlayers/flops.py`, `conf/`.
Changed: `memlayers/train.py` (a `RunLayout`, atomic checkpoint writes, a
checkpoint callback, `meta_dict()` with `extra_meta`), `memlayers/model.py`
(`GPTConfig.ffn_hidden`, the hidden width of individual dense FFNs; it defaults
to empty, so every existing model and its init are unchanged).

## 1. The `conf/` tree

```
conf/
  config.yaml          defaults list; seed, tag, run_id, out_root, force, resume, resume_foreign
  model/               pkm  pkm_randkey  dense  peer  tiny_pkm  tiny_dense
                       pkm_t2  peer_t2  dense_t2  pkm262k_t2          (T2: no experiment uses them yet)
  data/                v1 (the frozen bundle, sha256-verified)   fake (step-1 synthetic, `repeat` kind)
  train/               tier1   smoke
  eval/                standard  smoke  off       placeholders (empty), filled in prompt 2
  logging/             files  wandb               placeholders (empty), filled in prompt 3
  runtime/             auto  mac  cpu  cuda  colab   device only for now
  experiment/          pkm  pkm_randkey  dense  peer  smoke
```

| group | holds |
|---|---|
| `config.yaml` | `defaults: [run_schema, model: pkm, data: v1, train: tier1, eval: standard, logging: files, runtime: auto, _self_, experiment: ???]`. The experiment is required. `seed: 0`, `tag: ""`, `run_id: ${make_run_id:${name},${seed},${tag}}`, `out_root: runs`, `force: false`, `resume: true`, `resume_foreign: false`, `runtime.out_dir: ${out_root}/${run_id}`. Hydra settings: `job.chdir: false`, `output_subdir: null`, `run.dir: ${out_root}/.hydra_tmp`, sweep dir `${out_root}/.hydra_tmp/multirun`. |
| `model/` | GPTConfig fields. `pkm` = T1 (d384, 6 layers, 6 heads, PKM at layer 3, 256×256 = 65,536 slots, top-k 32, 4 heads, dim_head 128, query BatchNorm). `pkm_randkey` = the same with `freeze_keys: true`. `peer` = PEER at layer 3 with 65,536 experts (`non_competing_scores: false`). `dense` = all dense, layer 3 narrowed to h = 896 (section 2). `tiny_*` = the test-suite model (d64, 3 layers, vocab 257, block 64; PKM 16×16 at layer 1). |
| `data/` | `v1`: `source: real`, `version: v1`, `data_config: configs/data/v1.yaml`, `verify: true`, `seed: ${seed}`. `fake`: `kind: repeat`, `chunk_len: 8`, `n_distinct: 257`, `seed: ${seed}`. |
| `train/` | `tier1` (below). `smoke`: 50 steps, micro-batch 4, warmup 5, `log_every: 1`, `ckpt_every: 10`. Both use `seed: ${seed}`. |
| `runtime/` | `device:` auto / mps / cpu / cuda / cuda (Colab). |
| `experiment/` | `@package _global_`. Picks model, data and train, and sets `name`. `pkm`, `pkm_randkey`, `dense`, `peer` = their model + `v1` + `tier1`. `smoke` = `tiny_pkm` + `fake` + `smoke` + `eval: smoke`. |

**Ports of the 8 flat configs.** `t1_pkm → model/pkm`, `t1_pkm_frozen → model/pkm_randkey`,
`t1_peer → model/peer`, `t1_dense → model/dense` (layer 3 narrowed),
`t2_pkm → model/pkm_t2`, `t2_peer → model/peer_t2`, `t2_dense → model/dense_t2`
(layer 4 narrowed by the same rule), `t2_pkm_262k → model/pkm262k_t2`. The data,
train and runtime parts of the flat files became `data/`, `train/` and
`runtime/`. The flat files stay in `memlayers/configs/` with a "SUPERSEDED by
conf/model/<x>.yaml" header, because `python -m memlayers.train --config` and
`bench/` still read them.

**Strictness.** `memlayers/config.py` registers `RunConfig` in Hydra's
ConfigStore as `run_schema`. `RunConfig` holds `ModelCfg` (with a `MemoryCfg`
node), the existing `DataCfg`, `OptimCfg` and `RuntimeCfg`, and two new empty
dataclasses, `EvalCfg` and `LoggingCfg`. Each group dataclass is also stored
under `schema/<group>`. So `train.stepz=5` fails at compose time. One gap: Hydra's
`+key=value` append opens the struct flag, so `+train.stepz=5` would get through.
`validate_keys()` closes that gap. It runs inside `compose()` and
`to_train_config()`, so the bad key fails before anything is written. A memory
key of the other memory kind (`model.memory.num_keys` on PEER) is also refused.

**One seed.** The top-level `seed` feeds `data.seed` (the loader permutation)
and `train.seed` (`torch.manual_seed` before the model is built, which covers
init and dropout). Both are `${seed}` interpolations and can still be overridden
for tests.

### The exact tier-1 numbers

| | value |
|---|---|
| micro-batch × grad-accum × block | 32 × 1 × 512 = **16,384 tokens / step** |
| steps | **9,156** = ceil(150,000,000 / 16,384) (150M / 16,384 = 9,155.27) |
| tokens seen | 9,156 × 16,384 = **150,011,904** |
| sequences read | 292,992, inside one epoch of v1's `train.bin` (293,896 sequences, 150,475,264 tokens), so no sequence is seen twice |
| LRs | backbone 2.5e-4, memory values 1e-3, memory keys = backbone; wd 0.1 (memory 0.0); betas (0.9, 0.95); clip 1.0 |
| schedule | warmup 30, cosine to 0.1 × base (t1_pkm.yaml's) |
| `log_every` / `ckpt_every` | 10 / 500 (~10 min at 1.22 s/step on MPS) |

Differences from the A18 run (t1_pkm.yaml plus bench/learnability_run.py's
overrides), checked by `test_pkm_round_trips_to_the_a18_configuration`:
`steps` 5,830 → 9,156, `ckpt_every` 0 → 500, `log_every` 50 → 10. Every other
TrainConfig field is equal: the GPTConfig, the whole DataCfg and the rest of
OptimCfg.

## 2. FLOPs per token, and the dense layer

`memlayers/flops.py:estimate_flops_per_token(model_cfg)` counts the forward
pass, with one multiply-add = 2 FLOPs and attention included. Attention is
4d² for the projections plus 2Td for QKᵀ and A·V, over the full T = 512 context
(Kaplan's convention; a causal mask would halve the second term on average). The
memory layer is counted as query projection + sub-key scores + top-k product
(k² additions per head) + value sum. Biases, norms, activations and the top-k
selections are not counted. PKM's keys are `[heads, num_keys, 2, dim_head]`, so
each half-query is a full 128 long and the query projection is 384 → 1,024. Both
`flops_per_token` (whole model + per layer) and, for the dense model,
`compute_match` go into `meta.json`.

| experiment | whole model | blocks | output head | layer 3 (attn + FFN) | layer-3 FFN | other layers (each) |
|---|---:|---:|---:|---:|---:|---:|
| pkm | 63,603,456 | 25,006,080 | 38,597,376 | 3,379,200 | 1,413,120 | 4,325,376 |
| pkm_randkey | 63,603,456 | 25,006,080 | 38,597,376 | 3,379,200 | 1,413,120 | 4,325,376 |
| dense | 63,566,592 | 24,969,216 | 38,597,376 | 3,342,336 | 1,376,256 | 4,325,376 |
| peer | 63,701,760 | 25,104,384 | 38,597,376 | 3,477,504 | 1,511,424 | 4,325,376 |

Attention per layer: 1,966,080. A 4× dense FFN: 2,359,296.

Breakdown of the memory FFNs:

| part | PKM | PEER |
|---|---:|---:|
| query projection (384 → 2·4·128) | 786,432 | 786,432 |
| sub-key scores (4 heads × 2 halves × 256 × 128) | 524,288 | 524,288 |
| top-k product (4 × 32²) | 4,096 | 4,096 |
| value sum (PKM 4·32·384; PEER down + up, 2× that) | 98,304 | 196,608 |
| **total** | **1,413,120** | **1,511,424** |

The output head is 61% of the whole model, so whole-model numbers are always
within 0.3% of each other. Matching is judged at the layer, as the design says.
**What was done to the dense layer:** a standard 4× FFN at layer 3 costs
2,359,296 FLOPs per token, 1.67× the PKM layer's 1,413,120, which is outside
10%. The width was changed to the multiple of 64 nearest the exact match
(1,413,120 / 1,536 = 920), giving **h = 896**: 1,376,256 FLOPs, **0.974× PKM**
(and 0.911× PEER, also inside 10%). Only layer 3 changes; layers 0–2 and 4–5
keep 4×. `meta.json` for a dense run records both numbers under
`compute_match.layers[0]` (`reference_ffn_flops`, `ffn_flops`,
`standard_4x_ffn_flops`, `ratio`). For T2, `dense_t2` gets h = 832 at layer 4
(1,703,936 vs pkm_t2's 1,708,032, 0.998×).

Parameters: pkm and pkm_randkey 54.8M (25.2M of them memory values), peer 79.9M,
dense 29.7M.

## 3. The smoke run's run dir

`python -m memlayers.run experiment=smoke runtime=cpu` (50 steps, ~1.4 s wall
time including startup):

```
<out_root>/
├── .hydra_tmp/run.log                Hydra's own log; never inside a run dir
├── .locks/smoke-s0.lock              the run lock (flock), outside the run dir
└── smoke-s0/
    ├── checkpoints/
    │   ├── last.pt                   2,027,887 B   resumable: model, optimizer, scheduler, RNG, data position
    │   └── step_000000.pt              738,204 B   init weights
    ├── config.yaml                       1,608 B   fully resolved (no ${...} left)
    ├── meta.json                         4,374 B   write_meta's fields + run_id, experiment, seed, tag, overrides,
    │                                               host, pid, launched_at, git {commit, branch, dirty, dirty_files},
    │                                               versions {python, torch, hydra, omegaconf}, flops_per_token,
    │                                               compute_match, moved_previous_to, resumes[]
    ├── overrides.yaml                      193 B   the command-line overrides, as a list
    ├── slot_usage.json / .npz          479 / 2,756 B   memory runs only (as before)
    ├── status.json                         153 B   {state, step, updated_at, error, host, pid}
    ├── stdout.log                        3,619 B   everything printed, appended across resumes
    └── train_log.csv                     6,556 B   the old log.csv, renamed
```

There is no `.hydra/` directory, no `log.csv` and no `ckpt.pt`
(`test_smoke_run_writes_the_whole_run_dir`,
`test_the_cli_writes_no_hydra_dir_into_the_run_dir`).

## 4. Resume and re-run behavior

`run.py` takes the run lock, reads `status.json` and decides. It writes nothing
until the decision is made. Only then does it move an old dir (with force=true),
write `status.json` (running), `config.yaml` and `overrides.yaml`, and start the
`stdout.log` copy. `status.json` is rewritten after every periodic checkpoint
and at exit. On an exception (including Ctrl-C) the state is set to `failed`
with the traceback, and the exception is re-raised. `last.pt` and the init
weights are written to a temporary file in the same dir, fsynced, then renamed
over the target. A refused single run exits with code 2 and a one-paragraph
reason. In a multirun, a refused job is reported and the sweep continues.

| case | behavior | test (tests/test_run.py) |
|---|---|---|
| no run dir | fresh run | `test_smoke_run_writes_the_whole_run_dir` |
| `done` | refused, also when only allowed keys changed. Every file keeps its checksum and mtime | `test_a_refused_rerun_changes_no_file`, `test_the_cli_refuses_a_done_run_with_exit_code_2` |
| `done` + `force=true` | old dir renamed to `<run_dir>.old-<n>` (byte-identical, nothing deleted), then a fresh run; the next force uses `.old-2` | `test_force_moves_the_done_run_and_starts_fresh` |
| `failed`, or `running` with a dead PID | resumed from `checkpoints/last.pt` | `test_kill_and_resume_matches_an_unbroken_run_exactly` |
| resume: loss curve | a run killed (os._exit, no cleanup, status left `running`) after the step-10 checkpoint, then re-launched with the same command, gives a `train_log.csv` equal to an unbroken run's **as strings, every step** | same |
| resume with a changed model / optimizer key | refused, listing the differing keys; no file changes | `test_a_resume_with_a_changed_model_key_is_refused` |
| resume with changed `train.steps` / `runtime.*` | allowed; the run continues to the new step count and `meta.json.resumes[]` records it | `test_a_resume_with_a_changed_step_count_is_allowed` |
| `failed` + `resume=false` | refused | `test_resume_false_refuses_a_failed_run` |
| an exception in training | `failed` + traceback in `status.json`, re-raised | `test_an_exception_marks_the_run_failed_and_is_reraised` |
| crash between two checkpoints | the log rows past the checkpoint are dropped before the replay, so each step is logged once | `test_a_crash_between_checkpoints_does_not_duplicate_log_rows` |
| second launch while the first is alive | refused, "already running"; after `kill -9` of the first, the same command resumes and finishes | `test_a_second_launch_is_refused_while_the_first_lives` |
| `running`, same host, live PID (status check alone) | refused, even with `force=true`; resumable once the PID is gone | `test_a_running_status_with_a_live_pid_is_refused` |
| `running`, another host | refused unless `resume_foreign=true` | `test_a_running_status_from_another_host_needs_resume_foreign` |
| dir exists, no `status.json` | refused (not ours); `force=true` moves it | `test_a_foreign_dir_without_status_is_refused` |
| `last.pt` write cut off | the previous `last.pt` is byte-identical and loads; no temp file left | `test_a_crash_mid_write_leaves_the_previous_last_pt_loadable` |
| pkm_randkey-s0 vs pkm-s0 | init state_dicts byte-equal (and the saved `step_000000.pt`); first 3 batches equal; keys frozen | `test_pkm_randkey_and_dense_share_pkms_batches_and_randkey_its_init`, `test_the_saved_init_weights_of_pkm_and_randkey_are_equal` |
| dense-s0 vs pkm-s0 | first 3 batches equal (init differs, as expected) | same |

Resume allow-list: `train.steps`, `runtime.*`, `logging.*`, `eval.*`, plus the
launch flags `force`, `resume`, `resume_foreign` and `out_root`. These say how
and where to run, not what is run. A changed `train.steps` also moves the end of
the cosine schedule from the resume point on, which is what extending a run
means.

The run lock is in two layers. `status.json` gives the host and PID rule the
design asks for, and works across hosts on a synced drive. On top of that, an
`flock` on `<out_root>/.locks/<run_id>.lock` is held for the whole launch, so
two launches on one host cannot race between reading the status and writing it.
The kernel releases that lock however the process dies.

## 5. Test count

**191 before → 268 after** (+77), all passing, CPU only, `pytest` 39 s locally.
`black --check .` (25.9.0, as pinned) is clean.

- `tests/test_config.py` (50): the tree, every experiment × runtime (25), every model group, unknown keys (4 forms) and wrong types, a cross-kind memory key, the experiment required, the round trip to the A18 config, LRs/warmup, the 6 memory-model ports, the 2 dense ports, pkm_randkey = pkm + frozen keys, seed propagation, run id / run dir with and without a tag.
- `tests/test_flops.py` (9): tiny_pkm and tiny_dense by hand (332,960 and 376,960), the T1 numbers, the 10% match (dense vs pkm, vs peer, dense_t2 vs pkm_t2), why 4× was rejected, 4× is kept when close enough, PEER with competing scores off.
- `tests/test_run.py` (18): section 4's table, plus the CLI exit codes. The subprocess tests (kill and resume, the run lock) take ~3 s each.

## 6. Anything I could not follow, and open questions

1. **omegaconf is pinned to 2.3.1, not the current 2.4.0.** hydra-core 1.3.8
   (the current release) requires `omegaconf>=2.2,<2.4`, so 2.4.0 cannot be
   installed with it. `antlr4-python3-runtime==4.9.3` (pulled in by Hydra) is
   pinned too.
2. **"`train.stepz=5` fails at compose time" holds for the plain override but
   not for Hydra's `+` append.** `validate_keys()` closes the gap at startup,
   still before any write.
3. **9,156 steps, not 9,155.** The design says "steps = 150M / 16,384". That is
   9,155.27, so I rounded up, to reach at least 150M tokens and stay inside one
   epoch. 9,155 would be 149,995,520 tokens. It is one line in
   `conf/train/tier1.yaml`.
4. **`ckpt_every: 500` in tier1** is my choice: t1_pkm.yaml has 0 (save only
   at the end), which would make a 3-hour run unresumable.
5. **What "the dense FFN" was compared against.** The PKM layer. The same width
   is also within 10% of PEER (0.911×), so one dense model serves both. Rounding
   to a multiple of 64 (896, −2.6%) is my choice; the exact match would be 920.
   T2 got the same treatment (`dense_t2`: h = 832), which the design did not
   ask for.
6. **PID reuse.** A `running` status whose PID now belongs to an unrelated live
   process (after a reboot) is refused as "already running", as the design
   says. The message says so and points at `status.json`. The flock would know
   better (it is free in that case), but I kept the design's rule.
7. **A resume with no checkpoint yet** (a crash before the first `ckpt_every`)
   restarts from step 0 in the same dir. Same config, same seed, so it is the
   same run.
8. **`config.yaml` and `overrides.yaml` are rewritten on a resume** with the
   (allowed) new values. The previous command is kept in `meta.json.resumes[]`.
9. **The slot-usage counter is not restored across a resume.** This is
   pre-existing Trainer behavior. `slot_usage.json` after a resume counts only
   the steps since the resume. Worth fixing when prompt 2 or 4 touches read logs.
10. `smoke`'s loss barely moves in 50 steps (5.55 → 5.51 on `repeat` data):
    it is a plumbing check, not a learning check.

## 7. The MPS check: new entry point vs the old CLI

The same seed and settings on the real v1 bundle (Apple Silicon, MPS, torch
2.14.1). `log_every=1` was added so that step 1 is logged, and `tag=mps-check`
keeps the real `runs/pkm-s0` free:

```bash
python -m memlayers.run experiment=pkm seed=0 train.steps=100 eval=off train.log_every=1 tag=mps-check
python -m memlayers.train --config memlayers/configs/t1_pkm.yaml --set data.source=real data.version=v1 \
    data.data_config=configs/data/v1.yaml data.seed=0 train.seed=0 train.steps=100 \
    train.micro_batch_size=32 train.log_every=1 runtime.out_dir=runs/_old_cli_mps_check
```

| | new (`memlayers.run`) | old (`memlayers.train`) |
|---|---:|---:|
| loss, step 1 (before any update, "step 0") | 10.8378 | 10.8378 (identical string) |
| loss, step 50 | 7.5329 | 7.5329 |
| loss, step 100 | 7.1537 | 7.1537 |
| max per-step loss difference over 100 steps | 5.8e-5 | |
| median step time (steps 11–100) | 1,215.6 ms | 1,219.3 ms |
| throughput | ~13,480 tok/s | ~13,440 tok/s |
| peak memory (MPS driver-allocated) | 23.54 GB | 23.54 GB |
| wall time, incl. data verification | 2:07.5 | 2:06.7 |

The step-1 loss is bit-equal, so the init weights and the first batch are the
same. Later steps drift by at most 5.8e-5, which is MPS's non-deterministic
reduction order. For scale, `bench/results/determinism_mps_pkm.json` has two
identical T1-pkm runs on MPS 1.4e-4 apart after 40 steps.
The run dir `runs/pkm-s0-mps-check/` is `done` with the full layout of section 3.
