# Metric sample-size pilot (pkm-s0 / s1 / s2, final step 9,156)

Status: **complete** (all 20 runs, 4 levels × 5).    Data v1 verified (`python -m data.fetch --version v1 --verify-only` OK). Checkpoints from `kalcy0n/memlayers-checkpoints`, SHA-256 matches its `SHA256SUMS`.

## Setup notes

- **Code.**
  - Runs started before the parity fix used `main` 2ed043c.
  - Later runs use `af67ee5` (branch `metrics/parity-float64-recheck`, part of the PR that sets these defaults). That commit adds a float64 recheck for facts that fail the float32 parity check; see `reports/s1_parity_diagnosis.md`.
  - The fix does not change s0 or s2. A parity-only check at slice seed 17 / 10 people / 8 docs gave `float64_rechecked_facts = 0` and the same max errors as before (1.9e-5 and 2.4e-5), so their 2ed043c runs stand.
  - `pytest metrics tests` on af67ee5: 437 passed, 1 skipped.
- **Device.** `--device mps` fails before any metric: `q1.check_documents` casts to float64, which MPS does not support. All runs use `--device cpu --threads 8`. *Fixed after the pilot (same PR):* both float64 sums now run on CPU, and the parity recheck uses a CPU copy of the model, so `--device mps` works. A check on pkm-s1 at 10 people / 8 docs took 186 s on MPS vs 574 s on CPU, with parity passing and metrics matching CPU to float rounding.
- **training_check.json.** Not present in the HF repo for any run; the repo holds only the checkpoints, README and SHA256SUMS. Reports show `training_check.verdict = None`.
- **pkm-s1 parity.** Under 2ed043c, s1 failed the native parity check on one prompt: a top-k near-tie in float32, 87 date candidates off by up to 6.7e-4. With af67ee5 it passes, with that 1 fact / 87 candidates rechecked in float64. Its failed 2ed043c output is kept in `runs/pilot/_parity_fail_main_pkm-s1_seed17_p10_d8`.
- **Timing caveat.** From level 3 on, some runs shared the CPU with others. At level 4 the last four ran two at a time, and s1/s2 were rerun after a dropped session killed them mid-E1. The clean per-level timing is the first, timed s0 seed-17 run, which ran alone.
- **E2 headline source.** Read from `E2.result.cumulative`. Its status counts include `unlearned_discovery` and `at_chance_on_test` besides the four statuses in the brief.
- **Rule.** PASS when sampling spread (s0 at slice seeds 17/18/19) ≤ 1/3 × seed spread (s0/s1/s2 at slice seed 17).
- **Other arguments.** `--controls 3 --permutations 99 --max-prefix 16` (defaults), `--lesion-size 64 --lesion-sizes 16,256`, `--doc-tokens 256`.


## Result

**No knob reaches "all its headline numbers pass" within the planned levels (up to 80 people / 64 docs).** By number:

- **V2:** passes from 40/32 (top1_share). Both V2 numbers pass at 80/64.
- **U4:** at the threshold at 80/64 (0.335).
- **E1:** improves steadily but still fails at 80/64 (0.47–0.82).
- **E2:** fails at 80/64 (1.55–1.73). It is capped by the 16-slot prefix limit, not by the number of people.

The brief's stop rule ("stop growing a knob once all its headline numbers pass") never fired. The `--doc-tokens 128` variant was not run, because it was conditional on docs passing at 8.

So there is no clean answer. Per the brief I'm not picking one silently; these are the measured options.

| option | what passes | cost per checkpoint (this Mac, CPU, 8 threads) | notes |
|---|---|---|---|
| **A. 80 people / 64 docs** (largest tested) | V2 both; U4 borderline (0.335) | ~40 min alone | E1 0.47–0.82, E2 ~1.6 |
| **B. Add a docs-only level: 80 people / 128 docs** | likely U4, maybe E1 at m=16/64 (extrapolated, not measured) | ~70–90 min alone (est.) | E1 m=64's ratio went 5.9 → 5.6 → 1.8 → 0.66 and m=16's 2.5 → 2.5 → 2.2 → 0.47, so one more doubling may pass. E1 m=256 has not improved (0.77 → 0.48 → 0.49 → 0.82): its seed spread shrank as its sampling spread held. 5 runs ≈ 5–7 h |
| **C. E2 via people** | not reachable | — | E2's ratio roughly halves per doubling (5.9 → 5.6 → 3.4 → 1.7). It needs ~2 more doublings (≈320 people), which is above the 300 frequent people there are. The lever is `--max-prefix` (80–85% of facts hit it), which is outside this pilot and changes E2's cost |

**My recommendation:** run option B (one docs-only level at 128 docs, people fixed at 80). Decide on E2 separately, either by accepting 80 people with its error bar flagged as sampling-dominated, or by testing a larger `--max-prefix`. That's your call; I haven't run either.

### Chosen sizes (if you take option A as is)

- `--frequent-people 80 --docs-per-subject 64 --doc-tokens 256`
- **E1 headline m.** Criterion, on the seed-17 runs: all three checkpoints positive, and the smallest of them ≥ 2× the s0 sampling spread at that m.
  - All m are positive on every checkpoint at every level.
  - **At 80/64 the criterion first holds at m=16** (min/sampling 2.1; m=64 is 2.3, m=256 is 3.6). At ≤ 40/32 only m=256 meets it.
  - m=16 qualifies only barely, and its effect is tiny (0.0013–0.0026 nats). I would **keep m=64 as the headline**, with m=16 and m=256 reported next to it. Your call.

| level | m=16 seed-17 values (min/sampling) | m=64 (min/sampling) | m=256 (min/sampling) |
|---|---|---|---|
| 10/8 | 0.0012 / 0.0004 / 0.0008 (0.19) | 0.0052 / 0.0034 / 0.0052 (0.31) | 0.0335 / 0.0236 / 0.0177 (1.47) |
| 20/16 | 0.0010 / 0.0006 / 0.0013 (0.31) | 0.0071 / 0.0060 / 0.0071 (0.94) | 0.0360 / 0.0396 / 0.0238 (3.10) |
| 40/32 | 0.0020 / 0.0013 / 0.0020 (0.82) | 0.0078 / 0.0049 / 0.0077 (0.97) | 0.0350 / 0.0278 / 0.0204 (2.83) |
| 80/64 | 0.0019 / 0.0013 / 0.0026 (2.12) | 0.0099 / 0.0059 / 0.0085 (2.28) | 0.0347 / 0.0285 / 0.0381 (3.62) |

(Values are s0 / s1 / s2.)

**Final-run command** (needs commit af67ee5 or later, so pkm-s1 passes parity):

```bash
python metrics.py <run>/checkpoints/step_009156.pt --seed 17 --frequent-people 80 --docs-per-subject 64 --doc-tokens 256 --lesion-size 64 --lesion-sizes 16,256 --device mps --no-serve --output-dir runs/final/<run>
```

**Run time per checkpoint at 80/64:** 2415 s (40 min) alone on this Mac's CPU; 53–60 min when two run at once. With the MPS fix, expect roughly 3× faster on `--device mps` (measured at the smallest slice only). For three checkpoints: ~2 h one at a time, or ~1 h 40 min running two at once and then the third alone.

### Q1 / Q2

- **I could not confirm the full numbers.** The run's own `heldout_quality` and `fact_recall` at final are not in the HF repo, which holds only checkpoints, README and SHA256SUMS. They are not stored inside the checkpoints either (keys: step, tokens_seen, model, config, data).
- They need to come from the training run directories or W&B for s0/s1/s2.

### Anything odd

1. **MPS could not run metrics.py** during the pilot: `q1.check_documents` used float64, which MPS does not support. Every pilot run used CPU. This is fixed in the same PR, and MPS is about 3× faster.
2. **pkm-s1 parity.** It failed under 2ed043c because of a float32 top-k tie on one prompt; with af67ee5 it passes, rechecking 1 fact / 87 candidates in float64. See `reports/s1_parity_diagnosis.md`.
3. **E2 is dominated by `prefix_limit_reached`.** About 80–85% of facts hit it at every level: 40–44/50, 76–84/~100, 160–172/~200, 316–331/~400. Matched facts per run: 1–5, 3–11, 11–24, 14–54. `threshold_not_reached` is always 0. There are two extra statuses, `unlearned_discovery` and `at_chance_on_test`.
4. **E2 erasure_rate is degenerate at 20/16.** All three s0 slices are exactly 0, so the sampling spread is 0 and the PASS there is meaningless. With few matched facts it is often 0.
5. **E1 drops a different subject per checkpoint.**
   - s1 loses FreeLaw (`no_matched_controls`) at 40/32 and 80/64. s2 loses Github. s0 matches all 5.
   - FreeLaw has the largest excess (0.014–0.024 nats on s0/s2), so losing it lowers s1's mean.
   - Part of E1's seed spread is therefore which subjects are averaged, not only how the seeds differ.
6. **E1 at slice seed 18 is consistently high** (m=64: 0.016 / 0.013 / 0.013 / 0.012 across levels). Which docs are drawn matters as well as how many.
7. **No undefined headline numbers in any run.**
8. **Two level-4 runs (s1, s2) were killed mid-E1** when my session dropped (~15:47). I reran them from scratch, and the numbers above are from the reruns.

### Files

- `reports/sample_size_pilot_report.md` (this file)
- `reports/sample_size_pilot_raw.csv`: every run's headline numbers, E2 status counts, parity recheck counters and wall time
- `reports/s1_parity_diagnosis.md`
- Run outputs: `runs/pilot/<ckpt>_seed<k>_p<people>_d<docs>/` (JSON, HTML, log, walltime)

## Per-metric tables

**U4.excess_bits** (docs knob)

| size (people/docs) | sampling spread | seed spread | ratio | pass |
|---|---|---|---|---|
| 10/8 | 0.04461 | 0.007814 | 5.71 | FAIL |
| 20/16 | 0.03376 | 0.01229 | 2.75 | FAIL |
| 40/32 | 0.01426 | 0.01679 | 0.849 | FAIL |
| 80/64 | 0.006176 | 0.01845 | 0.335 | FAIL |

**E1.mean_specificity_excess_nll(m=64)** (docs knob)

| size (people/docs) | sampling spread | seed spread | ratio | pass |
|---|---|---|---|---|
| 10/8 | 0.01099 | 0.001849 | 5.95 | FAIL |
| 20/16 | 0.006359 | 0.001128 | 5.64 | FAIL |
| 40/32 | 0.00512 | 0.002875 | 1.78 | FAIL |
| 80/64 | 0.002612 | 0.003938 | 0.663 | FAIL |

**E1.by_lesion_size.16** (docs knob)

| size (people/docs) | sampling spread | seed spread | ratio | pass |
|---|---|---|---|---|
| 10/8 | 0.002131 | 0.0008417 | 2.53 | FAIL |
| 20/16 | 0.001847 | 0.0007269 | 2.54 | FAIL |
| 40/32 | 0.001586 | 0.0007288 | 2.18 | FAIL |
| 80/64 | 0.0006175 | 0.001325 | 0.466 | FAIL |

**E1.by_lesion_size.256** (docs knob)

| size (people/docs) | sampling spread | seed spread | ratio | pass |
|---|---|---|---|---|
| 10/8 | 0.01208 | 0.01578 | 0.765 | FAIL |
| 20/16 | 0.007672 | 0.01585 | 0.484 | FAIL |
| 40/32 | 0.007194 | 0.01461 | 0.493 | FAIL |
| 80/64 | 0.007871 | 0.009621 | 0.818 | FAIL |

**V2.text.top1_share** (docs knob)

| size (people/docs) | sampling spread | seed spread | ratio | pass |
|---|---|---|---|---|
| 10/8 | 0.002548 | 0.00553 | 0.461 | FAIL |
| 20/16 | 0.002006 | 0.004908 | 0.409 | FAIL |
| 40/32 | 0.0004982 | 0.004841 | 0.103 | PASS |
| 80/64 | 0.001087 | 0.004981 | 0.218 | PASS |

**V2.text.cosine_excess** (docs knob)

| size (people/docs) | sampling spread | seed spread | ratio | pass |
|---|---|---|---|---|
| 10/8 | 0.0005221 | 0.001151 | 0.454 | FAIL |
| 20/16 | 0.0007866 | 0.001175 | 0.67 | FAIL |
| 40/32 | 0.0007202 | 0.001101 | 0.654 | FAIL |
| 80/64 | 0.0002719 | 0.0009781 | 0.278 | PASS |

**E2.mean_matched_core_fraction** (people knob)

| size (people/docs) | sampling spread | seed spread | ratio | pass |
|---|---|---|---|---|
| 10/8 | 0.02339 | 0.003931 | 5.95 | FAIL |
| 20/16 | 0.03595 | 0.006414 | 5.6 | FAIL |
| 40/32 | 0.01588 | 0.004633 | 3.43 | FAIL |
| 80/64 | 0.006061 | 0.003508 | 1.73 | FAIL |

**E2.mean_matched_erasure_rate** (people knob)

| size (people/docs) | sampling spread | seed spread | ratio | pass |
|---|---|---|---|---|
| 10/8 | 0.1667 | 0.25 | 0.667 | FAIL |
| 20/16 | 0 | 0.09091 | 0 | PASS (degenerate: sampling spread 0, all values 0) |
| 40/32 | 0.09091 | 0.04167 | 2.18 | FAIL |
| 80/64 | 0.04674 | 0.03019 | 1.55 | FAIL |

## Levels (full tables per level)

#### Level: --frequent-people 10 --docs-per-subject 8 --doc-tokens 256

| Metric | knob | s0 seed17/18/19 | s0/s1/s2 @17 | sampling spread | seed spread (n ckpts) | ratio | pass (≤1/3) |
|---|---|---|---|---|---|---|---|
| U4.excess_bits | docs | 0.04634 / 0.02627 / 0.07088 | 0.04634 / 0.05333 / 0.04552 | 0.04461 | 0.007814 (3) | 5.71 | FAIL |
| E1.mean_specificity_excess_nll(m=64) | docs | 0.005158 / 0.01615 / 0.007702 | 0.005158 / 0.003361 / 0.005209 | 0.01099 | 0.001849 (3) | 5.95 | FAIL |
| E1.by_lesion_size.16 | docs | 0.001237 / 0.003368 / 0.002346 | 0.001237 / 0.0003956 / 0.000838 | 0.002131 | 0.0008417 (3) | 2.53 | FAIL |
| E1.by_lesion_size.256 | docs | 0.03349 / 0.04557 / 0.03407 | 0.03349 / 0.02361 / 0.01772 | 0.01208 | 0.01578 (3) | 0.765 | FAIL |
| V2.text.top1_share | docs | 0.07319 / 0.07138 / 0.07393 | 0.07319 / 0.07872 / 0.0743 | 0.002548 | 0.00553 (3) | 0.461 | FAIL |
| V2.text.cosine_excess | docs | 0.01696 / 0.01652 / 0.01704 | 0.01696 / 0.01811 / 0.01717 | 0.0005221 | 0.001151 (3) | 0.454 | FAIL |
| E2.mean_matched_core_fraction | people | 0.01077 / 0.01114 / 0.03416 | 0.01077 / 0.01221 / 0.0147 | 0.02339 | 0.003931 (3) | 5.95 | FAIL |
| E2.mean_matched_erasure_rate | people | 0.1667 / 0 / 0 | 0.1667 / 0 / 0.25 | 0.1667 | 0.25 (3) | 0.667 | FAIL |

| Run | seconds | f64 rechecked facts/cands | E1 matched subj | E2 matched | no_matched_controls | prefix_limit_reached | threshold_not_reached | unlearned_discovery | other |
|---|---|---|---|---|---|---|---|---|---|
| pkm-s0 seed17 | 429 | pre-fix 2ed043c | 5 | 2 | 4 | 40 | 0 | 4 |  |
| pkm-s0 seed18 | 414 | pre-fix 2ed043c | 5 | 1 | 6 | 40 | 0 | 1 | {"at_chance_on_test": 2} |
| pkm-s0 seed19 | 414 | pre-fix 2ed043c | 5 | 2 | 3 | 43 | 0 | 1 | {"at_chance_on_test": 1} |
| pkm-s1 seed17 | 574 | 1/87 | 4 | 5 | 1 | 41 | 0 | 1 | {"at_chance_on_test": 2} |
| pkm-s2 seed17 | 404 | pre-fix 2ed043c | 5 | 4 | 2 | 44 | 0 | 0 |  |

**docs knob:** not all pass (0/6 pass)

**people knob:** not all pass (0/2 pass)

Level 1 takeaways (3 checkpoints):
- Every headline number fails.
- The closest are V2 text cosine_excess (0.45), V2 text top1_share (0.46), E2 erasure_rate (0.67) and E1 at m=256 (0.77).
- E1 at m=64 and E2 core_fraction are near 6.
- E2 is dominated by `prefix_limit_reached` (40–44 of 50 facts), leaving 1–5 matched facts per run.
- Run time ≈ 7 min per checkpoint (s1 took 574 s, partly while other runs were going).

#### Level: --frequent-people 20 --docs-per-subject 16 --doc-tokens 256

| Metric | knob | s0 seed17/18/19 | s0/s1/s2 @17 | sampling spread | seed spread (n ckpts) | ratio | pass (≤1/3) |
|---|---|---|---|---|---|---|---|
| U4.excess_bits | docs | 0.09141 / 0.07803 / 0.1118 | 0.09141 / 0.09778 / 0.0855 | 0.03376 | 0.01229 (3) | 2.75 | FAIL |
| E1.mean_specificity_excess_nll(m=64) | docs | 0.007096 / 0.01332 / 0.006962 | 0.007096 / 0.005987 / 0.007115 | 0.006359 | 0.001128 (3) | 5.64 | FAIL |
| E1.by_lesion_size.16 | docs | 0.0009817 / 0.002828 / 0.001049 | 0.0009817 / 0.0005782 / 0.001305 | 0.001847 | 0.0007269 (3) | 2.54 | FAIL |
| E1.by_lesion_size.256 | docs | 0.03603 / 0.04275 / 0.03508 | 0.03603 / 0.03964 / 0.0238 | 0.007672 | 0.01585 (3) | 0.484 | FAIL |
| V2.text.top1_share | docs | 0.07156 / 0.07274 / 0.07357 | 0.07156 / 0.07647 / 0.07466 | 0.002006 | 0.004908 (3) | 0.409 | FAIL |
| V2.text.cosine_excess | docs | 0.01731 / 0.01652 / 0.01679 | 0.01731 / 0.01848 / 0.01738 | 0.0007866 | 0.001175 (3) | 0.67 | FAIL |
| E2.mean_matched_core_fraction | people | 0.01749 / 0.00581 / 0.04176 | 0.01749 / 0.01693 / 0.02335 | 0.03595 | 0.006414 (3) | 5.6 | FAIL |
| E2.mean_matched_erasure_rate | people | 0 / 0 / 0 | 0 / 0 / 0.09091 | 0 | 0.09091 (3) | 0 | PASS |

| Run | seconds | f64 rechecked facts/cands | E1 matched subj | E2 matched | no_matched_controls | prefix_limit_reached | threshold_not_reached | unlearned_discovery | other |
|---|---|---|---|---|---|---|---|---|---|
| pkm-s0 seed17 | 686 | pre-fix 2ed043c | 5 | 5 | 7 | 78 | 0 | 6 | {"at_chance_on_test": 4} |
| pkm-s0 seed18 | 639 | pre-fix 2ed043c | 5 | 3 | 8 | 84 | 0 | 2 | {"at_chance_on_test": 3} |
| pkm-s0 seed19 | 645 | pre-fix 2ed043c | 5 | 5 | 6 | 83 | 0 | 4 | {"at_chance_on_test": 2} |
| pkm-s1 seed17 | 965 | 1/87 | 5 | 11 | 8 | 76 | 0 | 3 | {"at_chance_on_test": 2} |
| pkm-s2 seed17 | 650 | pre-fix 2ed043c | 4 | 11 | 4 | 83 | 0 | 2 |  |

**docs knob:** not all pass (0/6 pass)

**people knob:** not all pass (1/2 pass)

Level 2 takeaways (3 checkpoints):
- **Every real headline number still fails.**
- Closest are V2 text top1_share (0.41), E1 at m=256 (0.48) and V2 text cosine_excess (0.67).
- **E2 erasure_rate's PASS is degenerate.** All three s0 slices are exactly 0, so the sampling spread is 0. I treat it as uninformative, not as a pass.
- E1 at m=64 and E2 core_fraction stay near 5.6. E2 is dominated by `prefix_limit_reached` (76–84 of ~100 facts).
- Run time ≈ 11 min per checkpoint for s0/s2 (639–686 s). s1 took 965 s, running alongside other jobs.

#### Level: --frequent-people 40 --docs-per-subject 32 --doc-tokens 256

| Metric | knob | s0 seed17/18/19 | s0/s1/s2 @17 | sampling spread | seed spread (n ckpts) | ratio | pass (≤1/3) |
|---|---|---|---|---|---|---|---|
| U4.excess_bits | docs | 0.1304 / 0.1205 / 0.1347 | 0.1304 / 0.1415 / 0.1247 | 0.01426 | 0.01679 (3) | 0.849 | FAIL |
| E1.mean_specificity_excess_nll(m=64) | docs | 0.007823 / 0.01294 / 0.01058 | 0.007823 / 0.004948 / 0.007694 | 0.00512 | 0.002875 (3) | 1.78 | FAIL |
| E1.by_lesion_size.16 | docs | 0.002034 / 0.003331 / 0.001745 | 0.002034 / 0.001305 / 0.001979 | 0.001586 | 0.0007288 (3) | 2.18 | FAIL |
| E1.by_lesion_size.256 | docs | 0.03499 / 0.04219 / 0.03965 | 0.03499 / 0.02784 / 0.02039 | 0.007194 | 0.01461 (3) | 0.493 | FAIL |
| V2.text.top1_share | docs | 0.07221 / 0.07262 / 0.07271 | 0.07221 / 0.07705 / 0.07459 | 0.0004982 | 0.004841 (3) | 0.103 | PASS |
| V2.text.cosine_excess | docs | 0.01715 / 0.01643 / 0.01678 | 0.01715 / 0.0182 / 0.0171 | 0.0007202 | 0.001101 (3) | 0.654 | FAIL |
| E2.mean_matched_core_fraction | people | 0.0232 / 0.0121 / 0.02798 | 0.0232 / 0.01917 / 0.0238 | 0.01588 | 0.004633 (3) | 3.43 | FAIL |
| E2.mean_matched_erasure_rate | people | 0.0303 / 0.09091 / 0 | 0.0303 / 0 / 0.04167 | 0.09091 | 0.04167 (3) | 2.18 | FAIL |

| Run | seconds | f64 rechecked facts/cands | E1 matched subj | E2 matched | no_matched_controls | prefix_limit_reached | threshold_not_reached | unlearned_discovery | other |
|---|---|---|---|---|---|---|---|---|---|
| pkm-s0 seed17 | 1145 | pre-fix 2ed043c | 5 | 11 | 11 | 164 | 0 | 9 | {"at_chance_on_test": 5} |
| pkm-s0 seed18 | 1299 | pre-fix 2ed043c | 5 | 11 | 15 | 160 | 0 | 7 | {"at_chance_on_test": 7} |
| pkm-s0 seed19 | 1484 | 0/0 | 5 | 12 | 7 | 172 | 0 | 7 | {"at_chance_on_test": 2} |
| pkm-s1 seed17 | 1446 | 1/87 | 4 | 15 | 12 | 163 | 0 | 5 | {"at_chance_on_test": 5} |
| pkm-s2 seed17 | 1696 | 0/0 | 4 | 24 | 4 | 161 | 0 | 9 | {"at_chance_on_test": 2} |

**docs knob:** not all pass (1/6 pass)

**people knob:** not all pass (0/2 pass)

Level 3 takeaways (3 checkpoints):
- **V2 text top1_share passes (0.10).** Every other headline number fails.
- U4 dropped sharply (2.75 → 0.85).
- E1 at m=256 is stuck near 0.49.
- E1 at m=64 improved to 1.8, but its sampling spread shrinks slowly (0.011 → 0.0064 → 0.0051 nats). Slice seed 18 is the high one at every level (0.016 / 0.013 / 0.013), which suggests the subject or doc draw matters more than its size.
- **E2 core_fraction (3.4) and erasure_rate (2.2) fail.** `prefix_limit_reached` takes 160–172 of ~200 facts, leaving 11–24 matched facts.
- s1 and s2 have 4 of 5 E1 subjects matched (one `no_matched_controls`).
- s1's float64 recheck is 1/87 again; the recheck count is 0 on the af67ee5 s0/s2 runs.
- Run time: 1145 s for the timed s0 seed-17 run. The others took 1299–1696 s while running alongside other jobs.

#### Level: --frequent-people 80 --docs-per-subject 64 --doc-tokens 256

| Metric | knob | s0 seed17/18/19 | s0/s1/s2 @17 | sampling spread | seed spread (n ckpts) | ratio | pass (≤1/3) |
|---|---|---|---|---|---|---|---|
| U4.excess_bits | docs | 0.1689 / 0.1727 / 0.1665 | 0.1689 / 0.1835 / 0.1651 | 0.006176 | 0.01845 (3) | 0.335 | FAIL |
| E1.mean_specificity_excess_nll(m=64) | docs | 0.009885 / 0.01249 / 0.0125 | 0.009885 / 0.005947 / 0.008464 | 0.002612 | 0.003938 (3) | 0.663 | FAIL |
| E1.by_lesion_size.16 | docs | 0.001857 / 0.002475 / 0.002213 | 0.001857 / 0.001308 / 0.002633 | 0.0006175 | 0.001325 (3) | 0.466 | FAIL |
| E1.by_lesion_size.256 | docs | 0.03472 / 0.04259 / 0.03944 | 0.03472 / 0.02847 / 0.03809 | 0.007871 | 0.009621 (3) | 0.818 | FAIL |
| V2.text.top1_share | docs | 0.07209 / 0.07255 / 0.07318 | 0.07209 / 0.07707 / 0.07392 | 0.001087 | 0.004981 (3) | 0.218 | PASS |
| V2.text.cosine_excess | docs | 0.0169 / 0.01664 / 0.01691 | 0.0169 / 0.01788 / 0.01691 | 0.0002719 | 0.0009781 (3) | 0.278 | PASS |
| E2.mean_matched_core_fraction | people | 0.02309 / 0.01814 / 0.0242 | 0.02309 / 0.02177 / 0.02528 | 0.006061 | 0.003508 (3) | 1.73 | FAIL |
| E2.mean_matched_erasure_rate | people | 0.05797 / 0.07143 / 0.02469 | 0.05797 / 0.02778 / 0.03086 | 0.04674 | 0.03019 (3) | 1.55 | FAIL |

| Run | seconds | f64 rechecked facts/cands | E1 matched subj | E2 matched | no_matched_controls | prefix_limit_reached | threshold_not_reached | unlearned_discovery | other |
|---|---|---|---|---|---|---|---|---|---|
| pkm-s0 seed17 | 2415 | 0/0 | 5 | 23 | 25 | 331 | 0 | 15 | {"at_chance_on_test": 6} |
| pkm-s0 seed18 | 3212 | 0/0 | 5 | 14 | 30 | 331 | 0 | 12 | {"at_chance_on_test": 13} |
| pkm-s0 seed19 | 3281 | 0/0 | 5 | 27 | 19 | 325 | 0 | 22 | {"at_chance_on_test": 7} |
| pkm-s1 seed17 | 3172 | 1/87 | 4 | 36 | 14 | 331 | 0 | 10 | {"at_chance_on_test": 9} |
| pkm-s2 seed17 | 3628 | 0/0 | 4 | 54 | 6 | 316 | 0 | 16 | {"at_chance_on_test": 8} |

**docs knob:** not all pass (2/6 pass)

**people knob:** not all pass (0/2 pass)

Level 4 takeaways (3 checkpoints):
- **Both V2 numbers pass:** top1_share 0.22, cosine_excess 0.28.
- **U4 misses by a hair (0.335).**
- **E1 fails at every m:** 0.47 at m=16, 0.66 at m=64, 0.82 at m=256.
- **E2 fails:** core_fraction 1.7, erasure_rate 1.55.
- **E2 is still dominated by `prefix_limit_reached`:** 316–331 of ~400 facts, leaving 14–54 matched facts.
- Run time: 2415 s (40 min) alone. The others took 3172–3628 s, two at a time.
