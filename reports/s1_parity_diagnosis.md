# pkm-s1 native parity failure: diagnosis

Checkpoint: `kalcy0n/memlayers-checkpoints` `pkm-s1/checkpoints/step_009156.pt` (sha256 matches SHA256SUMS).
Slice: `--seed 17 --frequent-people 10 --docs-per-subject 8 --doc-tokens 256`, CPU.
Scratch scripts (not in the repo): `parity_diag.py`, `topk_flip.py`. They replicate both scoring paths. The replicas reproduce `V1Scorer.score` and `_native_scores` bit-for-bit on 20 facts.

## Root cause

**A near-exact tie at PKM's top-k cutoff, resolved differently by two float32 forwards of different sequence lengths.** This is float32 rounding, not a logic difference between the two paths.

- **All 87 failures are in one fact, one prompt.** The prompt is `p000325-birth_date-r2` (control tier, test role, template 10, 75-token prompt, 200 month/day candidates).
- **The error sits in the month (first-token) term.** Every failing candidate is a non-gold date. The 87 failures span 7 month first-tokens, and each month has its own error level (1.1e-4 to 6.7e-4).
- **The day step is clean.** The second-token log-softmax matches float64 within 2e-5 for every month in both paths.
- **The native path computes the month term with a 75-token forward** (`gpt(prompt)`, last logit). The adapter path reads it from a 76-token forward (`gpt(prompt+[month], targets=...)`, position 74).
- **One slot flips at token position 72, head 2.** The two slots tie for the 32nd place in the top-k:

  | forward | slot picked | gate weight |
  |---|---|---|
  | float32, T=75 (native) | 41627 | 9.5128911e-3 |
  | float32, T=76 (adapter) | 18487 | 9.5128743e-3 |
  | float64, T=75 and T=76 | 18487 | 9.5128922e-3 |

  The two scores differ by ~2e-6 relative. That is at float32 resolution after the query projection. A different BLAS blocking for T=75 vs T=76 tips the choice.
- **Layer trace at position 74, float32 vs float64.** Blocks 0–3 have relative error ≤ 2e-6 in both forwards. At block 4's attention the error jumps to 2.8e-4 in the T=75 forward only, because attention reads position 72's changed residual. It stays at ~2e-4 through the output, which gives 6.6e-4 nats on the month log-probs. The T=76 forward stays ≤ 2.5e-6 all the way to the output.

## Evidence summary

| | max |score − native| float32 | failing candidates | failing facts | note |
|---|---|---|---|---|
| pkm-s0 | 1.9e-5 | 0 / 336,000 | 0 / 1,600 | birth_date is always the largest-error attribute |
| pkm-s1 | 6.7e-4 | 87 / 336,000 | 1 / 1,600 | next-worst fact 1.4e-5; everything else is like s0 and s2 |
| pkm-s2 | 2.4e-5 | 0 / 336,000 | 0 / 1,600 | birth_date largest, as in s0 |

For the facts closest to tolerance, both paths were recomputed in float64 (model cast to double on CPU; the scratch script lifts PKM's hard `x.float()` cast):

| fact | f64 adapter vs f64 native | f32 adapter vs f64 | f32 native vs f64 |
|---|---|---|---|
| p000325-birth_date-r2 (the failing one) | 1.4e-14 | 1.2e-4 | **5.7e-4** |
| p000894-birth_date-r2 | 1.4e-14 | 1.1e-4 | 1.2e-4 |
| p001544-birth_date-r2 | 1.3e-14 | 1.2e-4 | 1.2e-4 |
| p000455-university-r3 | 1.3e-14 | 2.2e-5 | 1.9e-5 |

- **In float64 the two paths are identical** (1e-14). Same context, positions and masking, so there is no logic bug.
- **On the failing fact, the float32 adapter path is closer to the float64 value.** The native reference is the one that flipped.
- **float32 date scores normally carry ~1e-4 of error against float64, in both paths.** The two paths share that error almost exactly, so the parity check sees only ~1e-5. The tie flip is the one case where the shared error breaks.

**Checkpoint scale (step 4).** Nothing unusual. Over 400 prompts the maximum logit is 16.9 / 17.9 / 18.4 (s0 / s1 / s2), with mean per-prompt max 10.2 / 10.2 / 10.3 and mean logit std 1.73 / 1.69 / 1.84. s1 sits between s0 and s2, so logit scale does not explain the failure. It is one unlucky tie, and it is specific to this slice: another slice seed would very likely pass.

## Proposed fix (not applied)

Keep the strict float32 check. When a fact fails it, re-score just that fact through both paths with the model in float64, and accept it only if they agree there. Record how many facts needed that.

A wider tolerance is not a good fix. The size of a tie flip depends on the swapped value vectors; it was 6.7e-4 here but could be larger. An atol of ~1e-3 would also hide real adapter bugs of size 1e-4.

```diff
--- a/memlayers/memory.py
+++ b/memlayers/memory.py
@@ class PKMMemory(MemoryLayer):
     def forward(self, x: torch.Tensor) -> torch.Tensor:
         self._b = x.shape[0]  # the hook needs it to unflatten (b t)
         if not self._capture_needed():
             self._last = None
         with fp32_region(x):
-            return self.pkm(x.float())
+            # At least fp32; a float64 model (the metrics parity recheck) stays float64.
+            return self.pkm(x if x.dtype == torch.float64 else x.float())
@@ class PEERMemory(MemoryLayer):
     def forward(self, x: torch.Tensor) -> torch.Tensor:
 ...
         with fp32_region(x):
-            return self.peer(x.float())
+            return self.peer(x if x.dtype == torch.float64 else x.float())
--- a/metrics/scoring.py
+++ b/metrics/scoring.py
@@ class V1Scorer:
+    @torch.inference_mode()
+    def float64_agrees(self, fact, atol, rtol):
+        """Re-score one fact through both paths with the model in float64.
+
+        A memory layer's top-k is discontinuous. When two slots tie for the k-th
+        place within float32 resolution, forwards of different lengths can
+        choose differently and move later scores by ~1e-4. In float64 both
+        paths choose the same slot, so agreement there shows the adapter is
+        exact and the float32 gap came from rounding."""
+        self.model.double()
+        try:
+            scores, _ = self.score(fact)
+            reference = self._native_scores(fact)
+        finally:
+            self.model.float()
+        return all(
+            abs(v - r) <= atol + rtol * abs(r)
+            for v, r in zip(scores, reference, strict=True)
+        )
@@ def check_baselines(self):
             "candidate_score_failures": 0,
+            "float64_rechecked_facts": 0,
+            "float64_rechecked_candidates": 0,
             "native_rank_mismatches": 0,
--- a/metrics/q2/__init__.py
+++ b/metrics/q2/__init__.py
@@ def check_facts(scorer, parity, atol, rtol):
         failures = sum(e > atol + rtol * abs(r) for e, r in zip(errors, reference))
+        if failures and scorer.float64_agrees(f, atol, rtol):
+            # A float32 top-k tie, not an adapter error: the paths agree in float64.
+            parity["float64_rechecked_facts"] += 1
+            parity["float64_rechecked_candidates"] += failures
+            failures = 0
         parity["candidate_scores_checked"] += len(scores)
```

Notes on the diff:
- **The memory.py change is a no-op for every training run.** fp32, bf16 and fp16 inputs are still cast to fp32 exactly as before. Only a float64 input is left as float64.
- **The cast back is exact.** `model.double()` followed by `model.float()` restores the float32 weights and buffers bit-for-bit, because every fp32 value is exactly representable in fp64. It runs only for facts that fail, which is 1 in 1,600 here, adding about a second.
- **The recheck path is the same one the diagnosis measured.** With the model in float64, `score` and `_native_scores` still apply `.float()` to the logits before `log_softmax`. The float64 network itself is what resolves the tie. Verified on the failing fact: running the tool's own `score` and `_native_scores` with the model in float64 (memory cast lifted by a scratch monkeypatch) gives a max difference of 0.0 and 0 failures, against 87 in float32. After `model.float()`, the float32 scores reproduce bit-for-bit.
- **The metrics still use float32 numbers.** They read the float32 adapter scores, which are the accurate path on this fact. The float64 recheck only decides pass or fail.
- **Tests to add:** a unit test for a forced top-k tie, or a monkeypatched `float64_agrees`, plus `test_runner_integration` coverage that the new parity keys appear.

**Would s1 pass with the fix?** Yes. Its only failing fact agrees to 1.4e-14 in float64, and all of s1's other parity counters (doc NLL, doc predictions, native ranks) were already 0.

## Effect on the metrics themselves

The same kind of tie can flip a slot inside any metric forward. Here it happened once in 1,600 prompts and moved one prompt's scores by ≤ 6.7e-4 nats. That is negligible for per-fact numbers. Averaged over a run's prompts it is far below E1's effects (1e-3 to 3e-2 nats). It is, however, the same order as level 1's E1 m=64 seed spread (5e-5 nats). That seed spread is itself unusually small, so this is one more sign that the m=64 headline is noise-dominated.
