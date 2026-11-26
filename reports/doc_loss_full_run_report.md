# Phase 2: the full `pkm_doc` runs (λ = 0.1, seeds 0 and 1) against pkm-s0/s1/s2

**Run.** `pkm_doc-s0`:
- `experiment=pkm_doc seed=0 runtime=mac logging=wandb` on branch `phase2/doc-loss`, launched detached on 2026-11-25 03:49 UTC.
- It trained 9,156 steps with all 10 eval points and finished `done` at 07:25 UTC: 3 h 36 min, at about 1.24 s/step on MPS in fp32.
- W&B run `gzbr7fxf`. Run dir `runs/pkm_doc-s0/` (not in git).

**Cohort metrics.**
- Command: `runs/final/run_one.sh runs/final/cohort/pkm_doc-s0 runs/pkm_doc-s0/checkpoints/step_009156.pt --e2-facts runs/final/e2-cohort.json`, the same flags and code as pkm-s0/s1/s2.
- Ran 13:46–14:06 UTC; parity passed with no rechecks needed.
- Report: `runs/final/cohort/pkm_doc-s0/step_009156-*.json` and `.html`. Extracted numbers: `reports/doc_loss_full_run_compare.json`.
- Slot-overlap measures on the final checkpoints: `reports/doc_loss_full_run_slots.json`.

**How to read the comparison.**
- There is **one** `pkm_doc` seed. "Seed range" is the min–max over pkm-s0, s1 and s2, the same model without the loss.
- A `pkm_doc` value inside that range is not distinguishable from seed noise.
- **Precision caveat:** pkm-s0/s1/s2 trained on CUDA in bf16 autocast, `pkm_doc-s0` on the Mac in fp32. The memory layer is fp32 in both, but differences of a few tenths of a percent in loss may come from precision as much as from the loss. The clean λ-only comparison is the pilot at step 1,500 (`reports/doc_loss_pilot2_report.md`).

## Update: second seed (`pkm_doc-s1`) and the two-seed picture

**Run.**
- `pkm_doc-s1`: `experiment=pkm_doc seed=1 runtime=mac logging=wandb`, W&B run `l1b5c7ff`.
- Launched 2026-11-26 04:03 UTC. Trained 9,156 steps with all 10 eval points and finished `done` at 07:37 UTC.
- **Training check: pass.** no_divergence worst ratio 1.416 at step 8,700, learned drop 0.673, coverage 1.0.
- Cohort metrics ran with the same flags and code; parity passed with no rechecks.

**Metrics wall time.** The metrics took 3 h 26 min instead of about 20 min. The watcher that started them did not hold `caffeinate`, so the Mac went into maintenance sleep partway through. The results are complete (rc 0, parity passed). Future watchers hold `caffeinate`.

Below, "doc s0" and "doc s1" are the two `pkm_doc` (λ = 0.1) seeds, and "seed range" is pkm-s0/s1/s2 without the loss. The precision caveat still applies to both doc seeds: fp32 on the Mac vs bf16 on CUDA.

### Which seed-0 findings hold

| finding from seed 0 | seed 1 | holds? |
|---|---|---|
| Slot reads document-consistent: partner Jaccard 0.285 vs 0.234–0.237 | 0.283 | **yes** |
| Partner / other-subject Jaccard ratio 4.72 vs 3.18–3.43 | 4.87 | **yes** |
| Partner retrieval by slots 74% vs 50% | 81% | **yes** |
| U4 excess 0.228 vs 0.165–0.184 | 0.238 | **yes** |
| Held-out pile_avg +0.27% vs seed mean (above the worst seed) | +0.38% (3.7581) | **yes**: both doc seeds are above every baseline seed |
| Layer-off ΔNLL −8% (0.760 vs 0.811–0.835) | 0.709 (−14%) | **yes**: both are below every baseline seed |
| Frequent-people recall up | full sets 0.910, slice 0.926 (baselines ≤ 0.892 / ≤ 0.909) | **yes**: both doc seeds are above every baseline seed, on both sets |
| Normal and rare people down | full sets: normal 0.432, rare 0.040, inside the range | **no**: seed 1 is inside the range, so seed 0's shortfall was seed noise |
| E2 weaker (17 matched, excess 1.55 nats) | 38 matched, excess 2.18 nats | **no**: seed 1 is at or above the baselines |
| E1 unchanged | 0.0080 | yes (inside 0.0060–0.0099) |

### Two-seed tables

Held-out loss: training-side `heldout_quality`, full test sets, nats/token.

| subject | doc s0 | doc s1 | doc mean | pkm-s0 | pkm-s1 | pkm-s2 | seed range |
|---|---|---|---|---|---|---|---|
| pile_avg | 3.7539 | 3.7581 | 3.7560 (+0.33%) | 3.7386 | 3.7449 | 3.7477 | 3.7386–3.7477 |
| pile_cc | 4.8847 | 4.8874 | 4.8861 | 4.8703 | 4.8749 | 4.8804 | 4.8703–4.8804 |
| github | 2.4395 | 2.4379 | 2.4387 | 2.4216 | 2.4307 | 2.4278 | 2.4216–2.4307 |
| pubmed_central | 3.5904 | 3.5959 | 3.5932 | 3.5760 | 3.5789 | 3.5860 | 3.5760–3.5860 |
| freelaw | 3.3975 | 3.4023 | 3.3999 | 3.3831 | 3.3872 | 3.3892 | 3.3831–3.3892 |
| wikipedia_en | 4.4598 | 4.4692 | 4.4645 | 4.4442 | 4.4554 | 4.4575 | 4.4442–4.4575 |
| uspto_backgrounds (never trained) | 4.5422 | 4.5523 | 4.5473 | 4.5218 | 4.5445 | 4.5337 | 4.5218–4.5445 |
| top-1 accuracy, pile_avg | 0.4130 | 0.4126 | 0.4128 | 0.4149 | 0.4142 | 0.4141 | 0.4141–0.4149 |

The +0.33% is the doc mean against the baseline seed mean (3.7437).

Fact recall top-1:

| row | doc s0 | doc s1 | pkm-s0 | pkm-s1 | pkm-s2 | seed range |
|---|---|---|---|---|---|---|
| frequent / test, full sets | 0.8963 | 0.9097 | 0.8710 | 0.8923 | 0.8887 | 0.871–0.892 |
| normal / test, full sets | 0.4054 | 0.4323 | 0.4329 | 0.4071 | 0.4520 | 0.407–0.452 |
| rare / test, full sets | 0.0323 | 0.0398 | 0.0399 | 0.0349 | 0.0385 | 0.035–0.040 |
| control / test, full sets | 0.0050 | 0.0056 | 0.0062 | 0.0052 | 0.0048 | 0.005–0.006 |
| frequent / paraphrase, full sets | 0.1147 | 0.1428 | 0.1088 | 0.1177 | 0.1080 | 0.108–0.118 |
| frequent / test, slice (800) | 0.924 | 0.926 | 0.895 | 0.909 | 0.903 | 0.895–0.909 |
| frequent / test mean rank, slice | 1.34 | 1.38 | 1.69 | 1.69 | 2.18 | 1.69–2.18 |
| normal / test, slice (100) | 0.48 | 0.43 | 0.49 | 0.42 | 0.52 | 0.42–0.52 |
| rare / test, slice (100) | 0.05 | 0.05 | 0.03 | 0.02 | 0.03 | 0.02–0.03 |
| frequent / paraphrase, slice (1,600) | 0.123 | 0.139 | 0.127 | 0.115 | 0.100 | 0.100–0.127 |

Memory use, from the cohort reports:

| metric | measure | doc s0 | doc s1 | pkm-s0 | pkm-s1 | pkm-s2 | seed range |
|---|---|---|---|---|---|---|---|
| U4 | excess over shuffles (bits) | 0.228 | 0.238 | 0.169 | 0.184 | 0.165 | 0.165–0.184 |
| E1 | mean specificity excess, lesion 64 (nats) | 0.0085 | 0.0080 | 0.0099 | 0.0060 | 0.0085 | 0.0060–0.0099 |
| E2 | facts matched / prefix limit (of 339) | 17 / 313 | 38 / 293 | 19 / 298 | 28 / 299 | 40 / 294 | 19–40 / 294–299 |
| E2 | matched: mean excess gold log p drop (nats) | 1.55 | 2.18 | 1.74 | 1.72 | 1.90 | 1.72–1.90 |
| V2 | subject text: top-1 share / paired excess | 0.0665 / 0.0164 | 0.0718 / 0.0161 | 0.0721 / 0.0169 | 0.0771 / 0.0179 | 0.0739 / 0.0169 | 0.0721–0.0771 / 0.0169–0.0179 |
| V2 | fact probes: top-1 share / paired excess | 0.0856 / 0.0100 | 0.0964 / 0.0101 | 0.0904 / 0.0104 | 0.0809 / 0.0104 | 0.0808 / 0.0101 | 0.0808–0.0904 / 0.0101–0.0104 |
| Whole layer off | ΔNLL all text (nats/token) | +0.760 | +0.709 | +0.835 | +0.811 | +0.821 | 0.811–0.835 |
| Whole layer off | Δ frequent / test top-1 | −0.526 | −0.575 | −0.581 | −0.594 | −0.633 | −0.581 to −0.633 |
| U1 | slots read on the slice | 99.94% | 99.92% | 99.93% | 99.94% | 99.96% | 99.93–99.96% |
| C6 | effective rank, active memory | 365.6 | 366.1 | 366.4 | 366.4 | 366.3 | 366.3–366.4 |

Same-document slot reads: `bench/doc_loss_precheck.py` measures on the final checkpoints, same 20 fixed batches.

| pair type | measure | doc s0 | doc s1 | pkm-s0 | pkm-s1 | pkm-s2 |
|---|---|---|---|---|---|---|
| partner | slot Jaccard | 0.285 | 0.283 | 0.234 | 0.236 | 0.237 |
| Pile, same subject | slot Jaccard | 0.139 | 0.137 | 0.138 | 0.135 | 0.138 |
| Pile, other subject | slot Jaccard | 0.060 | 0.058 | 0.074 | 0.069 | 0.074 |
| bio–bio, different people | slot Jaccard | 0.189 | 0.177 | 0.173 | 0.181 | 0.178 |
| bio–bio, same person (n = 8) | slot Jaccard | 0.216 | 0.235 | 0.209 | 0.219 | 0.224 |
| — | partner / other-subject Jaccard | 4.72 | 4.87 | 3.18 | 3.43 | 3.21 |
| — | partner retrieval by slot Jaccard | 0.742 | 0.809 | 0.500 | 0.504 | 0.496 |
| partner | query cosine | 0.966 | 0.962 | 0.780 | 0.785 | 0.780 |

### Two-seed takeaways

- **Robust, with both doc seeds outside the baseline range in the same direction:**
  - the slot-read reorganization (partner overlap, ratio, retrieval);
  - U4 (+35% vs the baseline mean);
  - held-out loss +0.33%;
  - less reliance on the memory (layer-off −11% vs the baseline mean);
  - **frequent-people fact recall up**: +1.9 points on the full sets (0.903 vs 0.884 mean), +2.3 points on the slice (0.925 vs 0.902), mean rank 1.36 vs 1.85.
- **Not robust:** seed 0's normal/rare shortfall and its weaker E2. Seed 1 is inside or above the baseline range on both.
- **Net picture:** the loss makes the memory document-organized. That costs about 0.3% LM loss and some reliance on the memory. It gives a small, consistent gain on the most-repeated facts and no measurable change on normal or rare facts.
- **The precision caveat still applies** to the LM-side differences and to the frequent-recall gain, which are a few tenths of a percent and about 2 points: both doc seeds ran in fp32 and all baselines in bf16. A Mac fp32 λ = 0 run would show which part comes from the loss.

---

*The sections below are the original seed-0 report.*

## Takeaways (seed 0)

- **The loss did what it is meant to, and the effect lasts to the end of training.**
  - The two halves of a document read more of the same slots: partner slot Jaccard 0.285 vs 0.234–0.237. Different-subject pairs read fewer shared slots: 0.060 vs 0.069–0.074.
  - Partner / other-subject Jaccard ratio: 4.72 vs 3.18–3.43.
  - Partner retrieval by slots: 74% vs 50%.
  - U4 excess (subject information in slot reads): 0.228 vs 0.165–0.184.
  - All four are well outside the seed range.
- **Held-out loss is slightly worse:**
  - pile_avg 3.7539 vs 3.7386–3.7477, +0.27% against the seed mean and +0.006 nats above the worst seed;
  - each trained subject is 0.002–0.009 nats above the seed maximum;
  - USPTO, never trained on, sits inside the range (4.5422 vs 4.5218–4.5445).

  This is about the size the pilot predicted (+0.65% at step 1,500, shrinking as LM training dominates). Part of it may be the fp32 vs bf16 difference.
- **The model relies a bit less on the memory:**
  - turning the memory layer off raises the slice NLL by 0.760, against 0.811–0.835 for the seeds (−8% vs their mean, as in the pilot's −7%);
  - frequent-tier top-1 drops by 0.53 with the layer off, against 0.58–0.63.
- **Fact recall is mixed, with no clear gain:**
  - Frequent people do best of all four runs: slice top-1 0.924 vs 0.895–0.909, mean rank 1.34 vs 1.69–2.18. On the full sets during training, frequent/test top-1 is 0.896 vs 0.871–0.892.
  - Normal and rare people are not better:
    - full sets: normal 0.405 vs 0.407–0.452, rare 0.032 vs 0.035–0.040;
    - slice: normal 0.48 (inside the range), rare 0.05 vs 0.02–0.03, on only 100 prompts.
  - Paraphrase recall is inside the seed range.
- **Facts are less localized in a few slots.** E2 matched 17 facts, against 19, 28 and 40 for the seeds. The mean excess gold-log-p drop for matched facts is 1.55 nats vs 1.72–1.90, and 313 facts reach the 16-slot prefix limit vs 294–299. Together with V2's lower top-1 share, the memory looks more document-organized and less fact-concentrated.
- **Unchanged:**
  - E1 subject specificity: 0.0085 vs 0.0060–0.0099;
  - slot coverage: 99.94% vs 99.93–99.96%;
  - C6 effective rank: 365.6 vs 366.3–366.4;
  - V2 paired excess: inside or just under the range.
- **Training check: pass.**
  - `no_divergence` worst ratio was 1.477 at step 6,760, against the 1.5 threshold. pkm-s0 had 1.473 and pkm-s2 failed with 1.535, so this is the usual mid-run spike.
  - `learned` drop 0.672.
  - Coverage 1.0.

**Bottom line.**
- The same-document loss reorganizes what the memory reads: strongly, durably, far beyond seed noise.
- That costs about 0.3% held-out loss and a little reliance on the memory.
- It does **not** produce a clear fact-recall gain: frequent people are at or above the best seed, normal and rare people at or below the worst, and E2 localization is weaker.
- With one seed and the precision difference, the LM-side differences are near the edge of what this comparison can resolve. The memory-side differences are not.

## 1. Held-out loss (training-side `heldout_quality`, final full test sets)

| subject | pkm_doc-s0 | pkm-s0 | pkm-s1 | pkm-s2 | seed range | pkm_doc vs seed mean |
|---|---|---|---|---|---|---|
| pile_avg (5 trained subjects) | **3.7539** | 3.7386 | 3.7449 | 3.7477 | 3.7386–3.7477 | +0.27% |
| pile_cc | 4.8847 | 4.8703 | 4.8749 | 4.8804 | 4.8703–4.8804 | +0.0095 |
| github | 2.4395 | 2.4216 | 2.4307 | 2.4278 | 2.4216–2.4307 | +0.0128 |
| pubmed_central | 3.5904 | 3.5760 | 3.5789 | 3.5860 | 3.5760–3.5860 | +0.0101 |
| freelaw | 3.3975 | 3.3831 | 3.3872 | 3.3892 | 3.3831–3.3892 | +0.0110 |
| wikipedia_en | 4.4598 | 4.4442 | 4.4554 | 4.4575 | 4.4442–4.4575 | +0.0074 |
| uspto_backgrounds (never trained) | 4.5422 | 4.5218 | 4.5445 | 4.5337 | 4.5218–4.5445 | +0.0089 (inside) |
| top-1 accuracy, pile_avg | 0.4130 | 0.4149 | 0.4142 | 0.4141 | 0.4141–0.4149 | −0.0014 |

- Loss is in nats/token on the full held-out test halves, token-weighted for pile_avg.
- Reference: dense-s0 has pile_avg 3.8069.

Cohort slice Q1 (320 documents, 72,328 tokens, NLL in nats/token):

| | pkm_doc-s0 | pkm-s0 | pkm-s1 | pkm-s2 |
|---|---|---|---|---|
| All | 3.5573 | 3.5423 | 3.5513 | 3.5528 |
| FreeLaw | 2.4654 | 2.4521 | 2.4604 | 2.4606 |
| Github | 2.7489 | 2.7252 | 2.7336 | 2.7298 |
| Pile-CC | 4.9638 | 4.9505 | 4.9613 | 4.9660 |
| PubMed Central | 3.6593 | 3.6453 | 3.6484 | 3.6543 |
| Wikipedia (en) | 4.1453 | 4.1348 | 4.1509 | 4.1511 |

## 2. Fact recall

Q2 on the cohort slice. Prompts per row: frequent 800 (test) and 1,600 (paraphrase); normal, rare and control 100 (test) and 200 (paraphrase).

| row | measure | pkm_doc-s0 | pkm-s0 | pkm-s1 | pkm-s2 |
|---|---|---|---|---|---|
| frequent / test | top-1 | **0.924** | 0.895 | 0.909 | 0.903 |
| frequent / test | mean rank (of 200) | **1.34** | 1.69 | 1.69 | 2.18 |
| frequent / test | gold margin (nats) | 2.067 | 2.080 | 2.003 | 2.054 |
| frequent / paraphrase | top-1 | 0.123 | 0.127 | 0.115 | 0.100 |
| normal / test | top-1 | 0.48 | 0.49 | 0.42 | 0.52 |
| normal / paraphrase | top-1 | 0.065 | 0.050 | 0.045 | 0.075 |
| rare / test | top-1 | 0.05 | 0.03 | 0.02 | 0.03 |
| control / test | top-1 | 0.02 | 0.02 | 0.00 | 0.01 |

Training-side `fact_recall` on the full fact sets (final eval) — top-1:

| row | pkm_doc-s0 | pkm-s0 | pkm-s1 | pkm-s2 | dense-s0 |
|---|---|---|---|---|---|
| frequent / test | 0.8963 | 0.8710 | 0.8923 | 0.8887 | 0.7510 |
| normal / test | 0.4054 | 0.4329 | 0.4071 | 0.4520 | 0.1273 |
| rare / test | 0.0323 | 0.0399 | 0.0349 | 0.0385 | 0.0139 |
| control / test | 0.0050 | 0.0062 | 0.0052 | 0.0048 | 0.0064 |
| frequent / paraphrase | 0.1147 | 0.1088 | 0.1177 | 0.1080 | 0.1020 |

Definitions:
- **top-1**: the gold answer ranks first among the 200 candidates; chance 0.005.
- **mean rank**: the gold answer's average rank, 1 = best.
- **margin**: gold log p minus the best wrong candidate's.

## 3. Memory use

| metric | measure | pkm_doc-s0 | pkm-s0 | pkm-s1 | pkm-s2 | seed range |
|---|---|---|---|---|---|---|
| U1 | slots read on the slice | 99.94% | 99.93% | 99.94% | 99.96% | 99.93–99.96% |
| U1 | slots that are some read's top slot | 21.7% | 21.3% | 22.4% | 22.3% | 21.3–22.4% |
| U1 | KL to uniform (bits) | 0.727 | 0.734 | 0.718 | 0.710 | 0.710–0.734 |
| U4 | conditional MI slots ↔ subject (bits) | 0.710 | 0.637 | — | — | |
| U4 | **excess over shuffles (bits)** | **0.228** | 0.169 | 0.184 | 0.165 | 0.165–0.184 |
| E1 | mean specificity excess, lesion 64 (nats) | 0.0085 (4 matched subjects) | 0.0099 | 0.0060 | 0.0085 | 0.0060–0.0099 |
| E1 | lesion 16 / 256 (nats) | 0.0011 / 0.0419 | | | | |
| E2 | facts matched (of 339) | **17** | 19 | 28 | 40 | 19–40 |
| E2 | prefix limit reached | 313 | 298 | 299 | 294 | 294–299 |
| E2 | matched: mean recall drop / control drop | 0.735 / −0.020 | 0.763 / 0.000 | 0.804 / 0.012 | 0.825 / 0.042 | |
| E2 | matched: mean excess gold log p drop (nats) | **1.55** | 1.74 | 1.72 | 1.90 | 1.72–1.90 |
| V2 | subject text: top-1 share / paired excess | 0.0665 / 0.0164 | 0.0721 / 0.0169 | 0.0771 / 0.0179 | 0.0739 / 0.0169 | 0.0721–0.0771 / 0.0169–0.0179 |
| V2 | fact probes: top-1 share / paired excess | 0.0856 / 0.0100 | 0.0904 / 0.0104 | 0.0809 / 0.0104 | 0.0808 / 0.0101 | 0.0808–0.0904 / 0.0101–0.0104 |
| C6 | effective rank, active memory / most-read 512 | 365.6 / 312.8 | 366.4 / 313.7 | 366.4 / 315.2 | 366.3 / 313.5 | |
| Whole layer off | ΔNLL all text (nats/token) | **+0.760** | +0.835 | +0.811 | +0.821 | 0.811–0.835 |
| Whole layer off | Δ frequent / test top-1 | −0.526 | −0.581 | −0.594 | −0.633 | −0.581 to −0.633 |
| Whole layer off | Δ normal / test top-1 | −0.37 | −0.36 | −0.31 | −0.40 | |

Definitions:
- **U1**: slot coverage on the slice.
- **U4**: mutual information between the slot read and the document's subject, minus its mean under 99 subject shuffles; p = 0.01 for all runs.
- **E1**: NLL rise on a subject when its 64 most subject-specific slots are masked, beyond the rise on other subjects and on matched random-slot controls. pkm_doc's Github row had no matched control, so its mean is over 4 subjects.
- **E2**:
  - per fact, the most-read slots are masked cumulatively, up to 16;
  - "matched" means masking removes the recall and a matched control is available;
  - "prefix limit reached" means the fact survives 16 masked slots.
- **V2**: how concentrated a cohort's value-vector contributions are on single slots ("top-1 share"), and the paired cosine excess over controls.
- **C6**: effective rank of the value table.
- **Whole layer off**: all 65,536 slots masked, minus intact.

## 4. Same-document slot reads at step 9,156

`bench/doc_loss_precheck.py` measures (definitions in `reports/doc_loss_precheck_report.md`), run on the 20 fixed batches with the final checkpoints:

| pair type | measure | pkm_doc-s0 | pkm-s0 | pkm-s1 | pkm-s2 |
|---|---|---|---|---|---|
| partner | query cosine | 0.966 | 0.780 | 0.785 | 0.780 |
| Pile, same subject | query cosine | 0.311 | 0.540 | 0.524 | 0.524 |
| Pile, other subject | query cosine | −0.031 | 0.201 | 0.182 | 0.192 |
| bio–bio, different people | query cosine | 0.131 | 0.728 | 0.723 | 0.733 |
| partner | slot Jaccard | **0.285** | 0.234 | 0.236 | 0.237 |
| Pile, same subject | slot Jaccard | 0.139 | 0.138 | 0.135 | 0.138 |
| Pile, other subject | slot Jaccard | 0.060 | 0.074 | 0.069 | 0.074 |
| bio–bio, different people | slot Jaccard | 0.189 | 0.173 | 0.181 | 0.178 |
| bio–bio, same person (n = 8) | slot Jaccard | 0.216 | 0.209 | 0.219 | 0.224 |
| bio–Pile | slot Jaccard | 0.014 | 0.014 | 0.015 | 0.016 |
| — | partner / other-subject Jaccard | **4.72** | 3.18 | 3.43 | 3.21 |
| — | partner retrieval by query cosine | 0.995 | 0.440 | 0.461 | 0.444 |
| — | partner retrieval by slot Jaccard | **0.742** | 0.500 | 0.504 | 0.496 |
| — | partner retrieval by weighted overlap | 0.624 | 0.472 | 0.481 | 0.474 |

The effect on reads is larger at the end than in the pilot at step 1,500 (partner Jaccard +0.044 there, +0.050 here against the seed mean). It is still document-specific: same-subject overlap is unchanged.

Bios do not become person-specific. Bios of different people read slightly *more* shared slots, and same-person rewordings stay at about the seeds' level. That is consistent with the absence of a broad fact-recall gain.

## 5. Training check (`runs/pkm_doc-s0/training_check.json`)

**Verdict: pass.**

| rule | value | threshold | seeds |
|---|---|---|---|
| finite | pass | | |
| no_divergence (worst loss / running min) | 1.477 at step 6,760 | ≤ 1.5 | 1.473 / 1.411 / 1.535 (s2 failed) |
| learned (drop from init) | 0.672 | ≥ 0.40 | |
| not_rising | final = min (3.5349) | excess ≤ 0.005 | |
| coverage, layer 3 | 1.0 | ≥ 0.8 | |

## 6. Possible follow-ups

These are not done:
1. **A Mac fp32 `pkm` (λ = 0) full run, about 3.6 h.** It would separate the loss from the bf16/fp32 difference on the LM-side numbers: the +0.27% held-out loss and the frequent-tier recall gain.
2. **More `pkm_doc` seeds.** The frequent-tier gain and the normal/rare deficit are each about the size of the seed spread, and one seed cannot settle them.
