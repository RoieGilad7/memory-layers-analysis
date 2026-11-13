# Checkpoint evaluation

From the repository root, with its Python 3.12 environment active:

```sh
python metrics.py path/to/ckpt.pt
```

The command evaluates a native PKM or PEER checkpoint on the frozen `data-v1` bundle, saves a printable HTML report and its JSON measurements in `runs/metrics/`, and opens a local viewer. Edit **Checkpoint** and click **Rerun** to evaluate another file on the same slice. Stop the viewer with Ctrl+C. Dense checkpoints produce the prediction and resource measurements supported by their architecture.

Use the project’s `python -m data.fetch --version v1` to obtain the bundle, or point `--bundle` or `MEMLAYERS_DATA_V1` at an existing verified copy. The runner looks for `data/v1` and can use the previously audited bundle in this workspace. For offline GPT-2 tokenization, supply `--tokenizer-cache` or set `TIKTOKEN_CACHE_DIR`. The evaluator checks the pinned release fingerprint and hashes the files it reads. It accepts the trainer’s `ckpt.pt` and its step-zero `init_weights.pt`; the report records which training provenance was available.

| Folder | Measurement |
|---|---|
| `q1` | Per-subject next-token loss, perplexity and accuracy |
| `q2` | Candidate recall, rank and gold-answer margin by exposure and wording |
| `frequency` | Answer popularity in the checkpoint’s consumed training windows |
| `u1` | Selected-slot coverage, top-ranked coverage and KL divergence |
| `u4` | Slot–subject association conditional on token identity, with document-label permutations |
| `v2` | Contribution shares, cancellation and cosine similarity against norm-matched controls |
| `c4` | Vocabulary projections and example contexts for active slots |
| `c6` | Effective rank of active value rows; optional comparable dense reference via `--dense` |
| `e1` | Target-versus-other subject loss change after matched lesions sized by each subject's excess reads (dose curve), with removed gate-mass share |
| `e2` | Cumulative fact lesions chosen on discovery prompts and judged on test prompts, matched single-slot removal, removed gate-mass share, and collateral effects against a generic-slot control |
| `whole_memory_off` | Per-subject loss and fact recall with the selected memory layer suppressed |
| `resources` | Storage, batch-one inference throughput and latency, and CUDA peak allocation when available |
| `x2` | Learned-seed range rule, and the paired per-item comparison of a learned run with its frozen-key twin |

By default, the slice samples 10 people per exposure tier and 40 frequent-tier people (the E2 cohort), all eight wordings of each of five attributes, and 16 documents per subject in each held-out half (first 128 prediction sites per document). Held-out subjects absent from training (the phase-2 subject) are left out unless `--include-untrained-subjects` is given. Q1 and Q2 report 95% bootstrap intervals over documents and people. The JSON identifies the actual rows. The baseline check compares the adapter with native inference on the same checkpoint and inputs. If it fails, the report marks the memory results unavailable.

E1 lesions cover 10%, 25% and 50% of each subject's excess discovery reads (`--e1-fractions`; 25% is the headline). E2 grows a discovery-ranked prefix until the discovery prompts fall to chance, then reports what that core does on the separate test prompts. Both report the share of gate mass each lesion removed, so models with flatter or sharper gates can be compared at equal removed mass. Slots are always rediscovered on the checkpoint being evaluated; `--e2-facts cohort.json` (a list of `person-attribute` fact ids) fixes which facts are examined so several checkpoints can be compared on the same cohort. A diagnostic single-slot result means that no sampled fact met discovery eligibility. A missing matched control or an unreached lesion threshold has its own status.

The report records the run's `training_check.json` when it sits in the run directory (or is named with `--training-check`). Value vectors for V2 are kept for every eighth position and fact (`--v2-stride`) to bound memory.

```sh
python metrics.py path/to/ckpt.pt --no-serve
python metrics.py path/to/ckpt.pt --layer 3 --people-per-tier 20 --frequent-people 60
```

`--no-serve` writes the two reports and exits. Use `--no-browser` to print the local viewer URL without launching a browser. For paired comparisons, reuse the slice seed, slice sizes, control counts, and device. Increasing slice sizes increases trace memory and the number of lesion forwards. `--max-prefix` sets the cumulative lesion search limit (default 16); reaching that limit is reported separately from testing every candidate.

For H3, compare a learned run with its frozen-key twin at the same seed and step, item by item (same prompts, same facts, same subjects), with bootstrap intervals:

```sh
python metrics.py --x2-pair pkm-s0.json pkm_randkey-s0.json
```

The range rule below is kept as a secondary check. X2 requires multiple checkpoints. First save reports for at least three distinct learned-key PKM seeds from comparable runs. Lock their margins, then supply the margin file when evaluating a matched frozen-key twin:

```sh
python metrics.py --calibrate-x2 learned1.json learned2.json learned3.json
python metrics.py frozen.pt --x2-margin runs/metrics/x2-margins.json
```

Study-level convergence is unverified by these checkpoint files. The multi-seed comparison is reported as diagnostic. The `display/` folder contains the HTML renderer and the local rerun form.
