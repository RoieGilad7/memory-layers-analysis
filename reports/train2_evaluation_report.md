# Training 2 — evaluation inside training, at the end, and post hoc

Branch `train/run-layer`, training prompt 2 of 5. A run now evaluates itself on
a schedule: cheap evals on fixed samples during training, a full eval at the
end, and the automatic training check. Any saved checkpoint can also be
evaluated later with `python -m memlayers.evaluate`. Evaluation does not change
training: on CPU, a run with eval on and the same run with `eval=off` give the
same loss at every step, compared as strings. It reproduces the A18 data check
(section 3).

```bash
python -m memlayers.eval.eval_sets --version v1                 # once per machine; deterministic
python -m memlayers.run experiment=pkm seed=0                    # evaluates at the 9 default points
python -m memlayers.evaluate run_dir=runs/pkm-s0 step=final      # | init | <step> | all, metrics=[...]
```

## 1. Package layout and the metric registry

```
memlayers/eval/
  registry.py        @register_metric, MetricSpec, the reserved names, name validation
  context.py         EvalContext (one eval point), EvalResources (per run, lazy, cached),
                     the shared held-out pass, masked_slots, preserved_state (RNG/mode isolation)
  eval_sets.py       build/verify the fixed sets; `python -m memlayers.eval.eval_sets`
  schedule.py        eval.points (fractions) / eval.steps (absolute) -> [(step, stage)]
  writers.py         evals.csv (long), final_metrics.json, JSON writer
  training_check.py  the gating rules + flattening
  evaluator.py       run_metrics (input checks, skips, timing) and Evaluator (the in-training part)
  metrics/
    heldout_quality.py   Q1
    fact_recall.py       Q2 (stand-in wrapping data/q2_probe.ProbeSet.score)
    slot_usage.py        U1
memlayers/evaluate.py    the post-hoc CLI
```

| name | metric_id | stages | needs_memory | inputs | keys |
|---|---|---|---|---|---|
| `heldout_quality` | Q1 | during, final, posthoc | no | model, heldout | `loss\|ppl\|top1\|tokens\|docs/<slug>` for 6 subjects and `pile_avg`; `loss/pile_avg_sample` at full-set stages |
| `fact_recall` | Q2 | during, final, posthoc | no | model, fact_probe | `top1\|rank\|margin/<tier>/<role>` (4 tiers × test, paraphrase), `top1/<tier>/test/<attribute>` (5 attributes) |
| `slot_usage` | U1 | during, final, posthoc | yes | model, heldout | `coverage\|best_coverage\|kl_uniform/layer<i>` per memory layer |

Reserved, listed but not runnable: `subject_specificity` (U4),
`subject_removal` (E1), `fact_core_set` (E2), `read_concentration` (V2),
`slot_inspection` (C4), `effective_rank` (C6), comparisons
`learned_vs_random_keys` (X2) and `knn_lm_comparison` (X3), and
`training_check`. A plugin registering a reserved name must use its reserved
id, and that takes the name off the reserved list. `training_check` can never
be registered as a metric. Names and ids are unique. An unknown name in
`eval.during` / `final` / `posthoc` fails at startup, before anything is
written, and the error lists the runnable metrics and the reserved names. A
reserved name gets "reserved, not implemented yet".

**The contract, as the framework enforces it.** `run_metrics` checks each
metric's `inputs` (`ctx.why_missing`) and `needs_memory` first. A metric whose
input is missing is not called; its reason goes into `skipped` (into
`final_metrics.json` at the end). Examples: slot_usage on the dense model, or
any metric on fake data. Metrics run with the model in eval mode under
`torch.no_grad`. In training, `Evaluator.at_point` wraps them in
`preserved_state`. That saves and restores the torch CPU/CUDA/MPS RNG,
numpy's and Python's RNG, train/eval mode, and each memory layer's read-logging
switch and slot mask. The data loader is never touched.

**The shared pass.** `ctx.heldout_pass()` runs one forward over the held-out
documents, captures the memory reads on the way, and caches the result on the
context. `heldout_quality` and `slot_usage` both read it, so slot usage costs
0.01 s (section 4). Windows never cross a document (`iter_document_windows`).
Windows of equal length are batched, 8 per forward (`eval.heldout_batch`), so
the full test half runs in 7 minutes where batch-1 windows would take several
times that. The same pass also accumulates sums over the fixed sample's
documents, which gives `loss/pile_avg_sample` at the final point (see
training check).

**EvalContext** carries: `model`, the resolved `config`, `run_dir`, `step`,
`tokens_seen`, `stage`, a seeded `generator` and `np_rng` (`eval.seed`, never
the run seed), `artifact_dir` (`<run_dir>/analysis/<metric>/`), and the lazy,
cached resources `heldout(half, sample)`, `fact_probe(sample)`, `init_model()`
and `readlog()`. `readlog()` raises "run the read-log pass first"; prompt 4
implements it. `with ctx.masked_slots({layer: ids}):` calls
`set_mask_slots(..., renormalize=False)` and restores the previous mask in a
`finally`.

**Schedule.** `eval.points` default `[0, .027, .055, .109, .218, .382, .546,
.765, 1.0]`. These are rounded half-up and de-duplicated, giving Tier 1 steps
0, 247, 504, 998, 1996, 3498, 4999, 7004 and 9156 (final). `eval.steps`
(absolute) overrides them. Every point saves `checkpoints/step_<6d>.pt`
(weights only, fp32, with the step, tokens seen and config) and the resumable
`last.pt`. `last.pt` is also written every `runtime.ckpt_minutes` (20) and
every `train.ckpt_every` steps.

**Files.** `evals.csv`: long format with columns exactly
`step,tokens_seen,stage,metric,metric_id,key,value`, appended and fsynced after
each eval. On resume, rows with a step past the resumed checkpoint are dropped
first. `final_metrics.json`: `{metrics: {"<metric>/<key>": v}, metric_ids,
skipped, step, tokens_seen}`. `training_check.json`: one entry per rule, with
its numbers and pass, plus `verdict`, `failed` and `not_evaluated`.
`eval_timing.csv`: seconds per metric per point (extra, see section 6).

**Post hoc.** `memlayers.evaluate run_dir=... step=final|init|<n>|all
[metrics=[...]] [sample=true] [update_final=true]` loads the checkpoint and
runs `eval.posthoc` (or `metrics`) on the full sets, or on the samples with
`sample=true`. It replaces earlier posthoc rows for the same
(step, metric, key) and leaves `final_metrics.json` alone unless
`update_final=true`. It also reads a pre-run-layer dir with `ckpt.pt` and no
`config.yaml` (the A18 run). The config comes from the Trainer's own
`config_dict` in the checkpoint.

## 2. The evaluation sets

Built by `python -m memlayers.eval.eval_sets --version v1` into
`data/v1/eval_sets/`, from the data seed `20261102` (keyed draws, as
`select_eval_rows` does), never the run seed. The sha256s are in the committed
`data/manifests/eval_sets_v1.json`. Two builds are byte-identical (rebuilt and
`cmp`-checked on v1, and tested). `meta.json` records both hashes. A run on
real data refuses to start, before writing anything, if either file is missing
or differs from the manifest. The manifest merges rather than overwrites, so
prompt 4 can add `readlog_tokens`; only `heldout_sample` and `fact_sample` are
checked at run start.

| set | items | contents | tokens | file | sha256 |
|---|---:|---|---:|---:|---|
| `heldout_sample` | 1,200 docs | 200 per subject from the test half | 1,873,303 | 32,979 B | `a3953cde6527d40e37a48cf29bdbf246686fb54162d89320144b027b0aea26ae` |
| `fact_sample` | 36,000 rows | 1,200 people: all 300 frequent, 300 each of normal/rare/control; roles test and paraphrase | — | 921,773 B | `b77cf2333ceb1d9c1e704a25894c8b443cbe97646228a2826b6855fcecfdcea8` |

Held-out sample, per subject (docs, tokens): pile_cc 200 / 128,401; github
200 / 253,841; pubmed_central 200 / 689,647; freelaw 200 / 510,674;
wikipedia_en 200 / 130,121; uspto_backgrounds 200 / 160,619. Each tier/role
cell of the fact sample is 3,000 rows (test) or 6,000 (paraphrase).

The full sets used at `final` and `posthoc`: the whole test half, 13,381
documents and 15,010,572 tokens (about 2.5M per subject); and every test and
paraphrase fact, 75,000 rows for 2,500 people.

## 3. The A18 regression

`runs/learnability_t1_pkm/ckpt.pt` (T1-pkm, step 5,830, 95.5M tokens) was
loaded by `memlayers.evaluate` through the legacy-layout path, on MPS.

**Fact recall on the fixed fact sample** (the same 36,000 rows A18 used) vs
the final row of `a18_curve.csv`:

| tier / role | top-1 A18 | top-1 now | mean rank A18 | now | margin A18 | now |
|---|---:|---:|---:|---:|---:|---:|
| frequent / test | 0.405333 | 0.405333 | 11.97 | 11.972 | −0.2040 | −0.2040 |
| frequent / paraphrase | 0.021667 | 0.021667 | 77.77 | 77.766 | −4.0259 | −4.0259 |
| normal / test | 0.031000 | 0.031000 | 57.75 | 57.746 | −1.6190 | −1.6190 |
| normal / paraphrase | 0.006833 | 0.006833 | 97.36 | 97.363 | −4.3653 | −4.3653 |
| rare / test | 0.008000 | 0.008000 | 90.35 | 90.350 | −2.1566 | −2.1566 |
| rare / paraphrase | 0.006333 | 0.006333 | 101.45 | 101.454 | −4.4379 | −4.4379 |
| control / test | 0.006333 | 0.006333 | 104.59 | 104.595 | −2.3458 | −2.3458 |
| control / paraphrase | 0.004000 | 0.004000 | 105.90 | 105.904 | −4.5341 | −4.5341 |

Every value is identical, to the precision A18 rounded to.

**Held-out loss per subject.** The fixed held-out sample is *not* A18's
in-loop sample. A18 drew its 200 documents per subject with `seed=0` in the
bench script; the eval set is keyed to the data seed, as the design requires.
So the like-for-like comparison is the full test half against A18's
`heldout_test_all_documents` (bench/results/learnability_t1_pkm.json, also the
number A18 says to quote):

| subject | A18, all docs | now, full test half | difference | docs / tokens (both) |
|---|---:|---:|---:|---|
| pile_cc | 5.0855 | 5.0855 | −0.00005 | 3,087 / 2,498,768 |
| github | 2.6623 | 2.6623 | −0.00001 | 1,815 / 2,500,847 |
| pubmed_central | 3.8290 | 3.8290 | −0.00001 | 713 / 2,501,486 |
| freelaw | 3.6203 | 3.6203 | +0.00002 | 995 / 2,501,994 |
| wikipedia_en | 4.7065 | 4.7065 | −0.00002 | 3,687 / 2,496,897 |
| uspto_backgrounds | 4.8033 | 4.8033 | −0.00000 | 3,084 / 2,497,199 |

The largest difference is 5e-5. That is MPS reduction order and the batching
(A18 ran one window per forward, this runs 8). The A18 in-loop row against the
new fixed sample, for scale (different documents, so not a regression check):
pile_cc 5.077 / 5.048, github 2.817 / 2.771, pubmed_central 3.856 / 3.829,
freelaw 3.616 / 3.606, wikipedia_en 4.672 / 4.717, uspto 4.806 / 4.755.

Also on that checkpoint: `pile_avg` loss 3.9803 (full) / 3.7643 (sample);
slot_usage coverage 1.000, best_coverage 0.990, kl_uniform 0.564 nats.
`memlayers.evaluate` added `evals.csv` and `eval_timing.csv` to
`runs/learnability_t1_pkm/`; no existing file there changed.

## 4. Eval timing and checkpoint sizes

The run was `experiment=pkm seed=0 train.steps=300 eval.steps=[0,150,300]
tag=eval-check` on MPS with real v1 data (`runs/pkm-s0-eval-check/`). Seconds
come from `perf_counter`:

| eval point | held-out pass (heldout_quality) | fact_recall | slot_usage | total |
|---|---:|---:|---:|---:|
| step 0, during (samples) | 53.6 | 55.5 | 0.01 | 109.1 |
| step 150, during (samples) | 53.8 | 54.4 | 0.01 | 108.3 |
| step 300, final (full sets) | 421.0 | 114.6 | 0.01 | 535.6 |

The A18 post-hoc passes gave the same: 52.8 + 55.4 s on the samples, 413.3 +
115.2 s on the full sets.

Training ran at 1.21–1.24 s/step, the same as prompt 1's check. The run's wall
time (71 min) includes a stretch of about 26 minutes where neither training nor
evaluation advanced. This fits the laptop sleeping (`caffeinate -i` does not
stop lid-close sleep), and the same happened during the A18 regression. The
seconds above exclude it, because `perf_counter` stops during sleep on macOS.

Training check of this 300-step run: `fail`, on `fact_learning` only
(frequent test top-1 0.006 vs control 0.0066; 300 steps is too early for
facts). `learned` passed (held-out loss down 41.8% from step 0), as did
`not_rising`, `no_divergence` (worst 1.07× running min) and `coverage` (0.935).
Flattening ratio: 0.070.

| file | size |
|---|---:|
| `checkpoints/step_<n>.pt`, T1-pkm, weights only fp32 | **219.2 MB** (219,157,939 B) |
| `checkpoints/last.pt` (weights + AdamW moments + RNG + data position) | 657.5 MB |
| evals.csv per eval point | ~5 KB (~85 rows) |

The run itself wrote 296.4 MB step files. That exposed a bug: copying each
state-dict entry separately stored the tied 50,257 × 384 embedding / output
head twice. It is fixed (commit `87f20ce`, with a test). The size above is the
step-300 checkpoint re-saved through the fixed code; it loads back
bit-identical.

**For a full Tier-1 run** (9,156 steps, 9 points: 8 during + 1 final):
- Eval time: 8 × ~109 s + ~536 s ≈ **23.5 min per run**. Training is 9,156 ×
  1.22 s ≈ 3.1 h, so evaluation adds ~12.6%.
- Disk, PKM run: 9 × 219 MB + 658 MB ≈ **2.6 GB per run**.
- By the same arithmetic, scaled by parameter count: PEER (79.9M params) ≈ 9 ×
  320 MB + 960 MB ≈ 3.8 GB; dense (29.7M) ≈ 9 × 119 MB + 356 MB ≈ 1.4 GB;
  pkm_randkey = pkm.
- The 4 experiments × 3 seeds ≈ **31 GB**, and ≈ 4.7 h of evaluation in all.

## 5. Test count

**268 before → 307 after** (+39, all in `tests/test_eval.py`), all passing on
CPU in ~61 s. Black 25.9.0 is clean. The tests run on a miniature v1 bundle
(`tests/_eval_fixtures.py`) cut from the committed `data/v1_sample/`: the 3
shortest test-half documents per subject, the sample's 28 people and 840
test/paraphrase facts, a random train.bin, block 128. Its eval sets are 2 docs
per subject and 2 people per tier, so the samples are strict subsets of the
full sets. There is no network apart from tiktoken's cached GPT-2 vocabulary,
which the existing suite already needs.

- Registry (4): built-ins and ids, duplicates refused, reserved names listed but not runnable, unknown name fails at startup with the known list (nothing written).
- heldout_quality (3): equals a hand computation on 3 hand-made documents, one spanning 3 windows. Dense and PKM: per subject loss, ppl, top-1 and tokens; pile_avg token-weighted with USPTO excluded. Plus: the pass leaves the model, including the BatchNorm buffers, unchanged.
- fact_recall (1): equals `keys_from_score(ProbeSet.score(...))` on the same rows, sample and full.
- slot_usage (4): coverage, best_coverage and kl_uniform on a fixed fake read log against a hand computation; skipped with a reason on the dense model; shares the held-out pass (no extra forward); missing inputs are skipped, not raised.
- masked_slots (2): masked slots get weight 0 and every other weight is unchanged (no renormalization), with the top-k indices unchanged; cleared after an exception.
- Schedule (3): 50 steps, 9,156 steps, de-duplication and absolute steps.
- In training (7): rows, the weights-only fp32 checkpoint at every eval point, final_metrics.json, meta hashes; final uses the full sets and during the samples; **eval on vs eval=off gives identical training losses**; **during numbers equal a posthoc `sample=true` run on that step's checkpoint** (rel 1e-9); posthoc replaces its own rows and leaves final_metrics.json alone unless `update_final=true`; the CLI rejects an unknown metric; the tied embedding is stored once.
- Resume (1): killed (subprocess, `MEMLAYERS_TEST_HALT=8:exit:eval_rows`) after the step-8 rows were written but before its checkpoint, resumed from `last.pt` at step 6: each (step, stage, metric, key) appears exactly once. About 10 s.
- Eval sets (3): two builds byte-identical; run seeds 0 and 1 record the same set hashes; a changed file is refused at run start (nothing written).
- training_check (11): a healthy cosine-shaped curve that still drops 2% over its last interval passes, with its flattening ratio (0.23) reported; each gating rule fails on its own bad curve (NaN in train loss, NaN in an eval loss, divergence spike, no learning, rising tail, collapsed coverage, no fact learning, both top-1 zero); coverage does not gate a dense run; missing evals give `incomplete`.

## 6. Anything I could not follow, and open questions

1. **The held-out regression compares against A18's all-documents numbers,
   not the `a18_curve.csv` final row.** That row is A18's own 200-doc sample,
   drawn with the bench script's `seed=0`. The design requires the eval set to
   come from the data seed, so the documents differ. Fact recall uses exactly
   A18's rows and matches its final row exactly.
2. **`loss/pile_avg_sample`** is an extra key at the full-set stages.
   Without it, the training check would compare a full-set final number with
   sample numbers from earlier points. Measured on the A18 checkpoint, the gap
   is 5.7% (3.980 vs 3.764), which would make `not_rising` and `learned`
   meaningless. The curve rules use the sample documents at every point.
3. **Extra keys** `tokens/<slug>` and `docs/<slug>` in heldout_quality, and the
   extra file `eval_timing.csv`. Both are small and make the weighting and the
   timing visible.
4. **`ppl/pile_avg` = exp(token-weighted mean loss)**, not a mean of
   per-subject perplexities.
5. **fact_learning also requires frequent > control.** Without that, both at 0
   would pass "at least 2× the control's". It changes nothing for A18
   (0.405 vs 0.006).
6. **Divergence** is checked on the logged training loss (every `log_every` =
   10 steps), after warmup, against the running minimum of the rows after
   warmup.
7. **A dense run's coverage rule** is reported as not gating rather than
   "pass".
8. **Fake-data runs** (`experiment=smoke`) skip all three metrics and record
   why. There is no held-out text or fact set in the fake data. The smoke
   experiment's eval points still checkpoint, and its training check comes out
   `incomplete`.
9. **Post-hoc rows do not record whether they used the samples or the full
   sets.** A `sample=true` run replaces a full run's rows for the same step,
   metric and key. The default is full, and `sample=true` is meant for checks
   like the one in the tests. A `sets` column would need a format change to
   evals.csv, which the design fixes.
10. **Evaluation errors are not swallowed.** A metric that raises for any
    reason other than a missing input fails the run (status `failed`,
    resumable). Hiding it would leave a run with silent holes.
11. **The MPS driver-allocated memory rose 23.5 → 33.6 GB after the first eval**
    (cached eval logits, 8 × 512 × 50,257 fp32). The device cache is now
    released after each eval point (commit `65dfe4c`). Measured before that
    fix; it changes no number.
12. **Sleep during long runs.** `caffeinate -i` does not keep a laptop awake
    with the lid closed; twice here a run paused for ~20 min. For Tier 1 (3+ h
    per run) on the Mac, the lid needs to stay open, or `caffeinate -s` on
    power.
