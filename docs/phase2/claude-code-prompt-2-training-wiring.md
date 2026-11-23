# Claude Code prompt 2: wire the same-document loss into training

Run on the Mac, from `/Users/roieg/studies/ms/year1/courses/algos_in_llms/final_project/`, after prompt 1. Paste everything below the line into Claude Code.

---

You are helping with a course research project (COMS 6998 Algorithms in LLMs). We train small GPT-style models whose layer 3 FFN is a product-key memory (PKM). Phase 2 adds ONE soft, low-weight, self-supervised loss: the two halves of the same document should have more similar memory-layer queries than halves of other documents. Prompt 1 added `GPT.set_keep_queries`/`kept_queries` and `memlayers/doc_loss.py` (`find_halves`, `half_vectors`, `doc_loss`). This task is PROMPT 2 of 3: add the loss to the training step behind config keys that default to OFF, the log columns, and the `pkm_doc` experiment. With the loss off, training must stay bit-identical to today.

WORKING DIRECTORY AND STARTING POINT
Work only under /Users/roieg/studies/ms/year1/courses/algos_in_llms/final_project/ . Use the existing .venv. Read first: reports/doc_loss_1_report.md, memlayers/train.py (OptimCfg, Trainer.__init__, train_step), memlayers/config.py (to_train_config), memlayers/runlog/files.py (TRAIN_FIELDS), memlayers/runlog/wandb_sink.py (TRAIN_KEYS), conf/experiment/pkm.yaml, conf/train/tier1.yaml, tests/test_train.py, tests/test_config.py.
Git: continue on branch `phase2/doc-loss`. Commit in small steps and push.

STEP 0, BEFORE ANY EDIT (golden regression)
On the current `main` code (e.g. `git stash`/a worktree of main), run 20 training steps of the tiny PKM model on CPU with fake data (the same kind of config tests/test_train.py uses) and save the per-step losses to `tests/fixtures/doc_loss_off_golden.json` together with the exact config used. Commit the fixture first.

FIXED DESIGN (do not change; if something is impossible, stop and report)
1. Flat config keys in `OptimCfg` (memlayers/train.py), so Hydra checks them automatically and to_train_config needs no change:
   doc_loss_weight: float = 0.0          # lambda after the ramp; 0 = off: no hook, no extra work
   doc_loss_ramp_steps: int = 1000       # linear ramp from 0; 0 = no ramp
   doc_loss_temperature: float = 0.5
   doc_loss_min_piece_tokens: int = 32
   doc_loss_layer: Optional[int] = None  # None = the model's only memory layer (error if several)
   doc_loss_eot_id: int = 50256          # GPT-2 end-of-text
2. Trainer.__init__: if doc_loss_weight > 0: fail with a clear error if the model has no memory layer, if the layer is ambiguous, if runtime.compile is true, if temperature <= 0 or min_piece_tokens < 2. Then model.set_keep_queries(True, layer). If the weight is 0, never call it.
3. Trainer.train_step, per micro-batch, after `_, loss = self.forward_model(x, y)`:
   lam = weight * min(1.0, self.step / ramp_steps) if ramp_steps > 0 else weight   (self.step = the step about to run)
   half_id, n = find_halves(x, eot_id, min_piece_tokens); v = half_vectors(kept_queries[layer], half_id, n); dl, st = doc_loss(v, tau)
   backward on (loss + lam * dl).float() / grad_accum_steps (through the scaler when there is one). `total_loss` keeps summing the LM loss ONLY.
   Average dl and the stats over micro-batches (ignore micro-batches with gap None). Release the kept queries after backward.
4. The returned row gets "doc_loss" (unweighted), "doc_weight" (lam), "doc_gap", "doc_halves"; empty strings when the loss is off.
5. Append those four names to TRAIN_FIELDS (memlayers/runlog/files.py) and TRAIN_KEYS (memlayers/runlog/wandb_sink.py). The existing old-header logic must keep working for resumed runs.
6. Nothing new in the checkpoint: lam depends only on the step. Confirm resume works by reading the code path; the resume test below checks it.
7. New conf/experiment/pkm_doc.yaml, identical to pkm.yaml except:
   name: pkm_doc
   train: doc_loss_weight 0.01, doc_loss_ramp_steps 1000, doc_loss_temperature 0.5, doc_loss_min_piece_tokens 32
   eval: steps [0, 247, 504, 998, 1500, 1996, 3498, 4999, 7004, 9156]   # the exact list pkm-s0 used (runs/final/hf_meta/pkm-s0/config.yaml), so both runs are evaluated and checkpointed at the same steps
   Check that pkm-s0's config.yaml has no other difference from what `experiment=pkm seed=0 runtime=mac` composes today; list any difference in the report and copy it into pkm_doc.yaml so the only difference between the two runs is the loss.
8. Do not change the `loss` column, the training check, the eval schedule logic or any metric.

TESTS (CPU only, no network)
- Golden: with doc_loss_weight 0 the 20 losses equal tests/fixtures/doc_loss_off_golden.json exactly, and no forward hook is registered on any memory layer.
- With weight > 0: kept queries exist; doc_* columns are filled; with weight 0 they are empty strings.
- Ramp: lam = 0 at step 0, weight/2 at half the ramp, weight after the ramp, weight from step 0 when ramp_steps = 0.
- Config: experiment=pkm_doc composes and carries the values above; a misspelled key (train.doc_loss_wieght=1) fails at compose time; each Trainer error above fires.
- TRAIN_FIELDS / TRAIN_KEYS contain the new columns; a resumed run whose log has the old header keeps writing under it.
- Resume: 30 steps straight vs 15 + save + resume + 15 with the loss on give the same losses (CPU, the existing resume-test tolerance).
- Smoke: tiny PKM, 60 steps, an injected dataset (Trainer's `dataset=` argument) whose rows have an EOT every 64 tokens. tiny_pkm has vocab_size 257, so set doc_loss_eot_id to a token id inside that vocab (e.g. 256) and make the dataset use it. Weight 1.0, ramp 0: mean doc_gap over the last 10 steps > over the first 10; all losses finite.
- Run the whole test suite: everything passes.

RUN (on the Mac)
1. Real-data count: on the committed `data/v1_sample` bundle (or real train.bin read-only if the sample is too small), count halves per batch of 32 windows x 512 over 50 batches with min_piece_tokens 32. Report mean, min, max. The lambda estimate assumed about 120 halves per batch.
2. A 200-step MPS run: `.venv/bin/python -m memlayers.run experiment=pkm_doc seed=0 runtime=mac train.steps=200 eval=off tag=doc-smoke` and the same with `experiment=pkm ... tag=doc-smoke-off`. Report median step time of both (steps 21-200), the doc_* columns, and peak memory.

PR
Open ONE draft PR from `phase2/doc-loss` to `main` titled "Phase 2: same-document memory loss (off by default)". Description: what the loss is (2-3 sentences), the config keys, the new columns, the regression guarantee, the test count, and the 200-step timing. Do not merge.

REPORT: reports/doc_loss_2_report.md
1. Files changed.
2. Any difference between pkm-s0's recorded config and the composed pkm experiment, and what pkm_doc.yaml copies.
3. Halves per batch on real data.
4. MPS step time with the loss on vs off, and the expected full-run time.
5. Test count before and after.
6. Anything you could not follow and open questions.
Then print a short summary in the chat.
