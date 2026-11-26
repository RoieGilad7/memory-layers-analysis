# Claude Code prompt 3: pilot runs and the choice of lambda

Run on the Mac, from `/Users/roieg/studies/ms/year1/courses/algos_in_llms/final_project/`, after prompt 2. Keep the lid open and the Mac on power. Paste everything below the line into Claude Code.

---

You are helping with a course research project (COMS 6998 Algorithms in LLMs). Prompts 1 and 2 added a soft, self-supervised same-document loss on the PKM memory-layer queries (`train.doc_loss_*` keys, experiment `pkm_doc`, columns doc_loss/doc_weight/doc_gap/doc_halves). This task is PROMPT 3 of 3: a pilot that picks the loss weight lambda by a fixed rule. The rule below is fixed before the runs; do not change it after seeing results.

WORKING DIRECTORY AND STARTING POINT
Work only under /Users/roieg/studies/ms/year1/courses/algos_in_llms/final_project/ . Use the existing .venv. Read first: reports/doc_loss_2_report.md, memlayers/train.py, memlayers/run.py, memlayers/eval/metrics/heldout_quality.py, memlayers/eval/context.py, bench/learnability_run.py (style of a bench script).
Git: continue on branch `phase2/doc-loss` (same PR). Commit and push.

FIXED DESIGN (do not change; if something is impossible, stop and report)
1. Script bench/doc_loss_pilot.py:
   - lambdas = [0, 0.003, 0.01, 0.03], seed 0, the composed config of `experiment=pkm_doc runtime=mac` with train.doc_loss_weight set per run. Everything else exactly as pkm_doc (ramp 1000, tau 0.5, min piece 32).
   - Keep train.steps = 9156 so the learning-rate schedule is the full run's; build the Trainer from the composed config and call trainer.train(steps=1500). Output dir runs/pilot_doc/l<lambda>/ (legacy layout is fine). Write a `done.json` at the end of each run; a run whose done.json exists is skipped, so the script can be restarted.
   - lambda = 0 is the baseline (same code, loss off = pkm-s0's path by the prompt 2 golden test).
2. At step 1,500, for every run:
   - held-out loss: the existing heldout_quality metric (the same function and sample set the during-training evals use); report pile_avg and per subject.
   - train loss: mean of the logged `loss` over steps 1,401-1,500.
   - same-document gap: on 20 FIXED batches of real training windows (the first 20 windows-batches of a loader seeded with 12345, identical for all runs), model in eval mode, no grad, keep queries on just for this measurement, mean of doc_loss stats "gap". Measured for every lambda INCLUDING 0.
   - step time: median step_time_s over steps 101-1,500.
   - slot coverage (U1) for layer 3: the slot_usage metric's `coverage/layer3` on the same held-out sample pass as heldout_quality (the number the training check uses), NOT the cumulative training-time counter.
   - also the doc_gap column from the training log at steps 200, 500, 1000, 1500 (lambda > 0 only), to see the trend.
3. Rule (fixed): choose the LARGEST lambda > 0 that passes all three:
   a. held-out pile_avg loss at most 1% above the lambda = 0 run;
   b. same-document gap at least 0.05 (cosine) above the lambda = 0 run;
   c. layer-3 coverage at least 0.8.
   If none passes, say so and stop. Do NOT try other lambdas.
4. Do NOT start the full run. Do not edit pkm_doc.yaml; I will set the chosen lambda.

TESTS (CPU only)
- The script's selection rule as a pure function, tested on hand-made numbers: picks the largest passing lambda; returns None when none passes; a lambda failing only one criterion is rejected.
- The fixed-batch gap measurement gives the same number twice for the same model and leaves the model's train/eval state and BatchNorm running stats unchanged.
- A 20-step CPU dry run of the script with the tiny model (flag --dry-run) completes end to end.

RUN
`caffeinate -dimsu .venv/bin/python bench/doc_loss_pilot.py` (about 4 x 31 min). Check progress every so often; if a run dies, rerun the script (finished runs are skipped).

REPORT: reports/doc_loss_pilot_report.md (+ the raw numbers as reports/doc_loss_pilot.json)
1. One table, one row per lambda: held-out pile_avg loss and its % difference from lambda 0, train loss, same-document gap and its difference from lambda 0, coverage, median step time and its % difference.
2. Per-subject held-out loss per lambda.
3. The doc_gap trend over steps 200/500/1000/1500.
4. The rule applied, criterion by criterion, and the chosen lambda (or "none").
5. Expected full-run time with the chosen lambda.
6. Anything you could not follow and open questions.
Report raw numbers, define every column. Then print a short summary in the chat and add a "Pilot" section to the PR description.
