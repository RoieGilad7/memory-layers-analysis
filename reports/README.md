# Reports

One report per step, in order. Each is self-contained and carries its own
numbers. **For anything about dataset v1, read
[`data6_template_fix_report.md`](data6_template_fix_report.md)** — it is the
current source, and the numbers in steps 2a–2e are superseded by it.

| report | step | status |
|---|---|---|
| [`step0_access_report.md`](step0_access_report.md) | **0** — every dataset, model, package and tool reachable and runnable on an Apple-Silicon Mac | **current** for step 0 |
| [`step1_demo_report.md`](step1_demo_report.md) | **1** — the training code proven end to end on fake data, with speed and memory measured to size the real runs | **current** for step 1, with one exception: its biography-generator sections (C5, and the file list) describe `tools/bio_generator.py`, which data step 2 replaced with the config-driven `data/bios.py` |
| [`data1_pile_report.md`](data1_pile_report.md) | **2a** — the Pile half of dataset v1: streaming a pinned revision, cleaning, dedup and the held-out split | **historical** — superseded by data step 5 |
| [`data2_bios_report.md`](data2_bios_report.md) | **2b** — the made-up biographies: people, facts, rewordings and fact prompts | **historical** — superseded by data step 5, which rebuilt the biographies to close the answer leak and rewrote all 120 templates |
| [`data3_pack_report.md`](data3_pack_report.md) | **2c** — packing into token files, the bundle manifest, `fetch`, and the loader | **historical** — superseded by data step 5; the token counts and every hash moved in the rebuild |
| [`data4_validation_report.md`](data4_validation_report.md) | **2d** — every data check (A1–A18) on the full build, the hand-check pack, and the learnability run | **historical** — superseded by data step 5. A13 fails here and is fixed there; its §6 record of three bugs validation found in the validator still stands |
| [`data5_fix_report.md`](data5_fix_report.md) | **2e** — the answer-leak fix, the first template rewrite, re-validation, the three A18 runs, the cleanup and review pass | **historical for the final figures** — superseded by data step 6; its answer-leak fix (§2) and cleanup (§8) still stand |
| [`data6_template_fix_report.md`](data6_template_fix_report.md) | **2f** — every template now states the fact it carries, the `{obj}`/`{subj}` grammar fix, the rebuild, A1–A18 and the freeze figures | **current — the source of truth for data v1** |
| [`train1_run_layer_report.md`](train1_run_layer_report.md) | **T1** — training prompt 1: Hydra configs under `conf/`, `python -m memlayers.run`, the run dir lifecycle, safe re-runs and resume, FLOPs per token | **current** for the run layer (prompts 2–5 extend it) |

The freeze and upload (part B of data step 6) and steps 3–5 (training runs,
read-log analysis) have not started.
