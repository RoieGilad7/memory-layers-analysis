# Training 3 — one run logger, an optional W&B mirror, and compare

Branch `train/run-layer`, training prompt 3 of 5. All of a run's logging now
goes through one logger. The run-dir files are always written first and stay
the source of truth; Weights & Biases is an optional mirror that can never
stop or slow a run. `memlayers.wandb_sync` backfills runs done offline or
without a login. `memlayers.compare` turns many run dirs into comparison
tables and plots.

```bash
python -m memlayers.run experiment=pkm seed=0 logging=wandb                  # mirrored live
python -m memlayers.run experiment=pkm seed=0 logging=wandb logging.mode=offline
python -m memlayers.wandb_sync runs/pkm-s0 runs/pkm-s1                       # backfill, idempotent
python -m memlayers.compare runs/ --out reports/compare/
```

**One change outside the prompt's file list, needed for its RUN step.** The
smoke experiment from prompt 1 trained on fake data, so every metric was
skipped and a compare over smoke runs would have been empty. `experiment=smoke`
now trains and evaluates on the committed 1% build `data/v1_sample/`
(`data=sample`: real Pile text and biographies, 1.5M tokens, verified against
the committed `v1_small` manifest, with its own eval sets in
`data/manifests/eval_sets_v1_small.json`). It runs in ~33 s on CPU.
`smoke_randkey` and `smoke_dense` were added as its twin and dense
counterparts. To make this possible, `DataCfg` gained `small` and `root`, and
`load_bundle_config()` reads a 1% build from a given root. The prompt-1 run
tests still use fake data and the vocab-257 tiny model (passed as overrides),
so they stay fast.

## 1. What a run sends to W&B, and what stays local

`memlayers/runlog/`, named so it never shadows the standard `logging`:
`RunLogger` with `log_train`, `log_eval`, `log_final`, `log_files` and
`finish`. `FilesSink` (always on) writes `train_log.csv`, `evals.csv` (posthoc
rows replace their own), `final_metrics.json` and the final `status.json`.
Only then is the call forwarded to the optional sinks. The Trainer, the
in-training Evaluator and `memlayers.evaluate` call only the RunLogger.

A non-file sink that raises is caught and reported once on stderr, with the
reason and the backfill command, then removed for the rest of the run
(`RunLogger.disabled` records why).

Two cases were tested:
- A fake W&B whose `log()` raises: one warning, every `train_log.csv` row
  written, status `done`.
- The real wandb 0.31 on this Mac, before the fix described in §5: the same
  outcome.

**Sent to W&B** with `logging=wandb` (`logging.mode` online or offline;
`disabled` builds no sink and makes no W&B call at all, nor does
`logging=files`):

| what | keys |
|---|---|
| init | `project=memlayers` (`logging.project`), `entity` (`logging.entity`, default null), `mode`, `group=<experiment>`, `name=<run_id>`, `job_type=train` (`eval` for `memlayers.evaluate`), `tags=[data:<version>, git:<8 chars>, device:<cpu\|mps\|cuda>, precision:<fp32>]`, `id=<wandb_id>`, `resume="allow"`, `config=<resolved run config>` |
| x-axes | `tokens_seen` (the step metric of every chart) and `step` |
| train rows | `train/loss`, `train/lr`, `train/lr_memory`, `train/step_time_s`, `train/tokens_per_s`, `train/peak_mem_bytes`, `train/grad_norm` |
| eval rows, during | `<metric>/<key>`, e.g. `heldout_quality/loss/pile_avg`, `slot_usage/coverage/layer3` |
| eval rows, final / posthoc | `<stage>/<metric>/<key>`, e.g. `final/fact_recall/top1/frequent/test` |
| summary | every `final_metrics.json` metric as `<metric>/<key>`, plus `final_step`, `final_tokens_seen`, `run_state`, `run_step` |
| files | `meta.json`, `training_check.json`, `final_metrics.json` |

**Stays local:** every checkpoint (`checkpoints/*.pt`), `slot_usage.npz` and
`.json`, read logs (prompt 4), `stdout.log`, `eval_timing.csv`, `config.yaml`
and `overrides.yaml` (the resolved config goes up as the W&B config instead).
W&B's own local files go to `<out_root>/.wandb/` (`logging.dir`), never into a
run dir.

**The W&B id.** It is generated once, when a run first starts, stored in
`meta.json` as `wandb_id`, and reused with `resume="allow"` by every resume,
by `memlayers.evaluate` (job_type `eval`) and by `wandb_sync`. A run moved
aside by `force=true` keeps its `meta.json` and so its id; the fresh run gets a
new one. A run first mirrored on a resume gets an id then, written into its
`meta.json`.

**What has reached W&B** is recorded per mode in the run dir's
`wandb_sync.json`: the last train step, the eval points, whether the summary
went, and the files. A resume clears the entries past its checkpoint, because
those steps are replayed. Nothing is sent twice. `wandb_sync` (online by
default) sends only what is missing in that mode:

| earlier run | what `wandb_sync` sends |
|---|---|
| logged live online | nothing |
| logged offline, or with `logging=files` | everything, once |
| synced already | nothing on a second sync |

Use it rather than `wandb sync <offline dir>` for offline runs; using both
would upload the same rows twice.

`wandb==0.31.0` is pinned in `requirements.txt` and imported lazily
(`get_wandb()`), so a machine without it runs fine with `logging=files`.

## 2. Compare on the smoke runs

Five runs on the Mac (CPU), `logging=wandb logging.mode=offline`:
`-m experiment=smoke seed=0,1,2` and `-m experiment=smoke_randkey,smoke_dense
seed=0`, all `done`, about 35 s each. The command was
`python -m memlayers.compare runs/smoke_p3 --out reports/compare_smoke --pkm
smoke --twin smoke_randkey --dense smoke_dense`. The role flags default to
pkm, pkm_randkey and dense; the smoke experiments need them. The outputs are
committed under `reports/compare_smoke/`.

`runs.csv` (5 rows × 96 columns; a few columns):

| run_id | experiment | seed | device | precision | tokens_seen | loss/pile_avg | ppl/pile_avg | top1/frequent/test | coverage/layer1 |
|---|---|---:|---|---|---:|---:|---:|---:|---:|
| smoke-s0 | smoke | 0 | cpu | fp32 | 102,400 | 9.1590 | 9,499.9 | 0.00 | 0.164 |
| smoke-s1 | smoke | 1 | cpu | fp32 | 102,400 | 9.1692 | 9,596.6 | 0.05 | 0.156 |
| smoke-s2 | smoke | 2 | cpu | fp32 | 102,400 | 9.1492 | 9,407.2 | 0.00 | 0.266 |
| smoke_dense-s0 | smoke_dense | 0 | cpu | fp32 | 102,400 | 9.1459 | 9,375.5 | 0.00 | — |
| smoke_randkey-s0 | smoke_randkey | 0 | cpu | fp32 | 102,400 | 9.1593 | 9,502.3 | 0.00 | 0.164 |

Every row also carries `git_commit`, `git_dirty`, `data_sha256` (`73f519ce…`,
the 1% build), and `heldout_sample_sha256` / `fact_sample_sha256` (`f947fe60…`
/ `54db8a55…`). `git_dirty` is True here because the smoke runs ran before
this prompt's code was committed.

`groups.csv` (246 rows; a few):

| experiment | metric | metric_id | key | n_seeds | mean | std | min | max | range |
|---|---|---|---|---:|---:|---:|---:|---:|---:|
| smoke | heldout_quality | Q1 | loss/pile_avg | 3 | 9.15915 | 0.00997 | 9.14923 | 9.16917 | 0.01994 |
| smoke | heldout_quality | Q1 | ppl/pile_avg | 3 | 9,501.26 | 94.72 | 9,407.21 | 9,596.64 | 189.43 |
| smoke | fact_recall | Q2 | top1/frequent/test | 3 | 0.01667 | 0.02887 | 0.00 | 0.05 | 0.05 |
| smoke | slot_usage | U1 | coverage/layer1 | 3 | 0.19531 | 0.06102 | 0.15625 | 0.26563 | 0.10938 |
| smoke_dense | heldout_quality | Q1 | loss/pile_avg | 1 | 9.14586 | — | 9.14586 | 9.14586 | 0 |

`curves.csv` (1,226 rows): every during and final eval row of every run, with
run_id, experiment, seed and tag in front. The first row is
`smoke-s0,smoke,0,,0,0,during,heldout_quality,Q1,loss/pile_cc,10.8280`.

`training_check.csv`: each run's rules from `training_check.json`, plus the
cross-run rule `ppl_at_most_dense`, for the untagged pkm-role runs only (not
the twin). For smoke-s0, finite ✓, no_divergence ✓ (worst 1.05×), learned ✗,
not_rising ✓, coverage ✗ (0.16), fact_learning ✗, flattening reported. The
dense rule failed for all three: pkm 9,499.9 / 9,596.6 / 9,407.2 vs dense
9,375.5. Each run's verdict is `fail`, as expected after 50 steps. smoke-s1
and -s2 have no dense run with their seed, so they are compared with the
dense mean, and the `detail` column names the dense runs used.

`learned_vs_random_keys.csv` (X2, 83 keys; the twin's paired run is smoke-s0):

| metric | key | twin | pkm mean | gap to mean | paired gap | margin (pkm range) | inside (mean / paired) | main test |
|---|---|---:|---:|---:|---:|---:|---|---|
| heldout_quality | loss/pile_avg | 9.15929 | 9.15915 | +0.00014 | +0.00025 | 0.01994 | yes / yes | yes |
| heldout_quality | ppl/pile_avg | 9,502.3 | 9,501.3 | +1.06 | +2.37 | 189.4 | yes / yes | yes |
| fact_recall | top1/frequent/test | 0.000 | 0.017 | −0.017 | 0.000 | 0.050 | yes / yes | no |
| slot_usage | coverage/layer1 | 0.164 | 0.195 | −0.031 | 0.000 | 0.109 | yes / yes | no |

`compare_meta.json` holds the command line, the input dir, the roles, the 5
run dirs, and the (empty) skipped and warnings lists.

Plots, one line per run plus a shaded min–max band for the 3-seed smoke group:
- `plot_heldout_loss.png`: pile_avg loss on the fixed sample's documents vs
  tokens (10.8 → 9.15).
- `plot_fact_recall.png`: top-1 per tier (frequent, normal, rare), test role,
  with the control mean dashed. Its final point uses all facts.
- `plot_slot_coverage.png`: coverage per memory layer.

## 3. The W&B run on real data

**Online did not run: there is no W&B login on this machine.** No
`WANDB_API_KEY`, no `api.wandb.ai` entry in `~/.netrc`, no stored credentials.
As instructed, I neither asked for nor stored a key and used offline mode:

`python -m memlayers.run experiment=pkm seed=0 train.steps=200
'eval.steps=[0,100,200]' logging=wandb logging.mode=offline tag=wandb-check`
(MPS, real v1 data) — done in 16.7 min wall time. The real wandb 0.31.0 wrote the offline
run `runs/.wandb/wandb/offline-run-20261108_224755-j96mh8ob` (148 KB in all;
no checkpoint near it).
- project `memlayers`, group `pkm`, run name `pkm-s0-wandb-check`, W&B id
  `j96mh8ob` (= `meta.json` `wandb_id`), job_type `train`, tags
  `data:v1, git:<commit>, device:mps, precision:fp32`.
- `wandb_sync.json` records train steps up to 200, eval points (0, during),
  (100, during), (200, final), the summary and the 3 files, all under `offline`.
- Timings matched prompt 2: evals 117 / 111 s during, 511 s final. The mirror
  added no visible cost.
- Training check: `fail` on learned and fact_learning, as expected at 200 steps.

To put it online once a login exists (`wandb login` on this Mac):
`python -m memlayers.wandb_sync runs/pkm-s0-wandb-check` uploads it under the
same id. The five smoke runs (offline too) sync the same way.

## 4. Test count

**307 before → 342 after** (+35), all passing on CPU (about 2 min). Black is
clean.
- `tests/test_runlog.py` (11, with the fake `wandb` module in
  `tests/_fake_wandb.py`; the real service is never called):
  - files are written before any sink sees a call;
  - a raising sink warns once and is disabled, and the files keep going;
  - a W&B outage during a run still ends `done`;
  - the specified init kwargs, row keys, summary and files, with no checkpoints;
  - the id is generated once and kept in meta.json, a resume reuses it (and
    resends nothing), force gets a new one while `.old-1` keeps the old one;
  - `mode=disabled` and `logging=files` make no W&B call;
  - wandb_sync replays every train row and every eval row once, and a second
    sync sends nothing;
  - sync after an online run sends nothing, and sync after an offline run
    uploads once under the same id;
  - the id generator's fallback.
- `tests/test_compare.py` (14):
  - on 3 smoke seeds + twin + dense (miniature bundle): runs.csv has 5 rows
    and all the files and plots are written and non-empty;
  - groups.csv equals a direct pandas groupby (mean, std, min, max, range);
  - X2 gaps, paired gap, margin and inside flags on hand-made numbers, with a
    tagged pilot that does not mix in;
  - X2 is registered as a comparison;
  - the dense rule passes and fails on hand-made perplexities and reports
    "no dense run";
  - the dense rule is only on untagged pkm-role runs;
  - refusals: mixed data sha (names the runs) and mixed fact_sample are
    refused; mixed devices warn; an unfinished run is skipped unless
    `--include-unfinished`; `.old-1` and non-run dirs are skipped; a tagged
    pilot is its own group and leaves the main group's rows and the X2 table
    unchanged; a duplicate (experiment, seed, tag) is an error; the CLI exits 2.
- `tests/test_config.py`: +10, from the two new smoke experiments × 5 runtimes.

## 5. Anything I could not follow, and open questions

1. **No online W&B run** (no login on this machine); see §3. The online path
   is the same code with `mode="online"`, and the fake-module tests cover its
   calls.
2. **`wandb.util.generate_id()` does not exist in wandb 0.31.0.** It moved to
   `wandb.sdk.lib.runid.generate_id`, same 8-character id.
   `generate_wandb_id()` tries `wandb.util` first, then that. The first smoke
   runs hit this: the fence worked, with one warning and a files-only `done`
   run, which is how I found it.
3. **The smoke experiment changed from fake data to the committed 1% sample**,
   for the reason at the top. Prompt 1 said "tiny model, fake data". It still
   finishes in well under a minute on CPU, and fake data remains
   `experiment=smoke data=fake model=tiny_pkm`.
4. **Compare's roles are flags** (`--pkm`, `--twin`, `--dense`, defaulting to
   pkm, pkm_randkey, dense), so the pkm-only rules (dense ppl, X2) can be tried
   on the smoke runs.
5. **X2 "main tests" flag.** The prompt lists heldout_quality among the main
   tests, then says the table "holds heldout_quality and fact_recall only,
   flagged as not main". I followed the list: heldout_quality keys are
   `main_test=True`, fact_recall's are not. The table also holds slot_usage
   keys (present in both pkm and the twin), `main_test=False`.
6. **The dense rule with no same-seed dense run** compares against the dense
   group's mean and names the runs used. With Phase 1's single dense-s0, pkm
   s1 and s2 are compared with dense-s0.
7. **`--stage posthoc`** takes each run's latest posthoc step's rows instead
   of `final_metrics.json`.
8. **Progress file.** `wandb_sync.json` (in the run dir) is what makes
   backfill idempotent. W&B itself has no cheap "which rows do you have"
   query offline.
9. **The plotted curves mix sets at the final point.** Fact recall uses the
   samples during training and all facts at the final point. The held-out loss
   plot uses the sample's documents at every point (`loss/pile_avg_sample` at
   the end), as the training check does.
10. **Correction to the prompt-2 report:** Phase 1 is 5 runs (pkm seeds 0, 1,
    2 + pkm_randkey s0 + dense s0). That is ≈ 11.8 GB of checkpoints and ≈ 2 h
    of evaluation in all, not "4 experiments × 3 seeds ≈ 31 GB". Fixed in
    `reports/train2_evaluation_report.md`.
