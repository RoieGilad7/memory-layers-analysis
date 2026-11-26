"""Regression checks for independent data-v1 baseline parity and date read sites."""

import unittest
from types import SimpleNamespace
from unittest.mock import patch

import torch

from .checkpoint import RoieModel, upstream_model_types
from .scoring import V1Scorer, fact_metrics


class V1ScorerTests(unittest.TestCase):
    def setUp(self):
        torch.set_num_threads(1)
        torch.manual_seed(12)
        GPT, GPTConfig = upstream_model_types()
        native = GPT(
            GPTConfig(
                vocab_size=16,
                n_layer=1,
                n_embd=8,
                n_head=2,
                block_size=12,
                memory_layers=(0,),
                memory_kind="pkm",
                memory=dict(
                    num_keys=3, dim_head=4, heads=2, topk=2, query_batchnorm=False
                ),
            )
        ).eval()
        self.model = RoieModel(native, 0)
        self.date = dict(
            row_id="p-date-r2",
            fact_id="p-date",
            person="p",
            attribute="birth_date",
            tier="frequent",
            role="test",
            prompt=[3, 4],
            answer=1,
            candidates=[[2, 7], [8, 9], [8, 1], [2, 10]],
        )
        single = dict(
            self.date,
            row_id="p-major-r2",
            fact_id="p-major",
            attribute="major",
            candidates=[[4], [3], [1]],
            role="paraphrase",
            preceding_fact_count=0,
            template_id=3,
        )
        corpus = SimpleNamespace(
            facts=[single, self.date],
            vocab=list(map(str, range(16))),
            docs={"eval": [dict(subject="Pile-CC", doc_id="d", tokens=[1, 3, 5, 4])]},
        )
        self.scorer = V1Scorer(self.model, corpus, "cpu")

    def test_date_score_matches_sequential_generation_and_traces_gold_only(self):
        baseline = self.scorer.check_baselines()
        self.assertTrue(baseline["passed"], baseline["parity"])
        self.assertEqual(baseline["parity"]["candidate_scores_checked"], 7)
        self.assertEqual(
            baseline["facts"]["paraphrases_by_tier_context"][
                "frequent/no_preceding_facts"
            ]["n"],
            1,
        )
        self.assertEqual(baseline["facts"]["rows"][0]["template_id"], 3)
        actual, reads = self.scorer.score(self.date, collect=True)
        expected = []
        with torch.no_grad():
            for key in self.date["candidates"]:
                prefix = self.date["prompt"].copy()
                joint = 0.0
                for y in key:
                    logits, _ = self.model.gpt(torch.tensor([prefix]))
                    joint += float(logits[0, -1].log_softmax(dim=-1)[y])
                    prefix.append(y)
                expected.append(joint)
        torch.testing.assert_close(torch.tensor(actual), torch.tensor(expected))
        self.assertEqual([r["position"] for r in reads], [1, 2])
        self.assertEqual([r["token"] for r in reads], [4, 8])
        self.assertTrue(all(len(r["ids"]) == len(set(r["ids"])) for r in reads))
        self.scorer.score(self.date, mask=[reads[0]["ids"][0]])
        self.assertIsNone(self.model.memory.module.slot_mask)
        self.assertFalse(self.model.memory.module.read_logging)
        self.assertTrue(self.scorer.check_baselines()["passed"])

    def test_ties_have_explicit_native_and_harness_metrics(self):
        metrics = fact_metrics([-1.0, -1.0, -2.0], 1)
        self.assertEqual((metrics["rank"], metrics["top1"]), (1.5, 0.5))
        self.assertEqual(
            (metrics["native_rank_convention"], metrics["native_top1_convention"]),
            (1, 1),
        )

    def test_adapter_mismatch_fails_parity_without_altering_native_reference(self):
        original = self.model.forward

        def altered(*args, **kwargs):
            logits, trace = original(*args, **kwargs)
            logits[..., 3] += 10
            return logits, trace

        with patch.object(self.model, "forward", altered):
            bad = self.scorer.check_baselines()
        self.assertFalse(bad["passed"])
        self.assertGreater(bad["parity"]["doc_nll_mismatches"], 0)
        self.assertGreater(bad["parity"]["candidate_score_failures"], 0)
        self.assertTrue(self.scorer.check_baselines()["passed"])

    def _perturb_adapter_scores(self, only_float32):
        """Shift the adapter's date scores, optionally only while the model is float32."""
        original = self.scorer.score

        def shifted(fact, *args, **kwargs):
            scores, reads = original(fact, *args, **kwargs)
            dtype = next(self.scorer.model.parameters()).dtype
            if fact is self.date and (dtype == torch.float32 or not only_float32):
                scores = [s + 1e-3 for s in scores]
            return scores, reads

        return patch.object(self.scorer, "score", shifted)

    def test_float32_only_gap_is_accepted_after_float64_recheck(self):
        # A float32 top-k tie: the paths disagree in float32 but agree in float64.
        with self._perturb_adapter_scores(only_float32=True):
            result = self.scorer.check_baselines()
        parity = result["parity"]
        self.assertTrue(result["passed"], parity)
        self.assertEqual(parity["candidate_score_failures"], 0)
        self.assertEqual(parity["float64_rechecked_facts"], 1)
        self.assertEqual(
            parity["float64_rechecked_candidates"], len(self.date["candidates"])
        )
        self.assertGreater(parity["max_candidate_abs_error"], 5e-4)
        self.assertEqual(next(self.model.parameters()).dtype, torch.float32)

    def test_mismatch_that_survives_float64_still_fails(self):
        with self._perturb_adapter_scores(only_float32=False):
            result = self.scorer.check_baselines()
        parity = result["parity"]
        self.assertFalse(result["passed"])
        self.assertEqual(
            parity["candidate_score_failures"], len(self.date["candidates"])
        )
        self.assertEqual(parity["float64_rechecked_facts"], 0)
        self.assertEqual(parity["float64_rechecked_candidates"], 0)

    def _flip_gold_rank(self, only_float32):
        """Move the date's gold score just past its neighbour, so only its rank changes."""
        original = self.scorer.score

        def flipped(fact, *args, **kwargs):
            scores, reads = original(fact, *args, **kwargs)
            dtype = next(self.scorer.model.parameters()).dtype
            if fact is self.date and (dtype == torch.float32 or not only_float32):
                gold = fact["answer"]
                others = [s for i, s in enumerate(scores) if i != gold]
                scores = list(scores)
                above = [s for s in others if s > scores[gold]]
                scores[gold] = min(above) + 1e-6 if above else max(others) - 1e-6
            return scores, reads

        return patch.object(self.scorer, "score", flipped)

    def test_float32_rank_flip_within_tolerance_is_rechecked_in_float64(self):
        with patch("metrics.scoring.ATOL", 100.0), self._flip_gold_rank(True):
            result = self.scorer.check_baselines()
        parity = result["parity"]
        self.assertTrue(result["passed"], parity)
        self.assertEqual(parity["candidate_score_failures"], 0)
        self.assertEqual(parity["native_rank_mismatches"], 0)
        self.assertEqual(parity["float64_rechecked_rank_mismatches"], 1)

    def test_rank_flip_that_survives_float64_still_fails(self):
        with patch("metrics.scoring.ATOL", 100.0), self._flip_gold_rank(False):
            result = self.scorer.check_baselines()
        self.assertFalse(result["passed"])
        self.assertEqual(result["parity"]["native_rank_mismatches"], 1)
        self.assertEqual(result["parity"]["float64_rechecked_rank_mismatches"], 0)

    @unittest.skipUnless(torch.backends.mps.is_available(), "needs MPS")
    def test_float64_recheck_on_mps_uses_a_cpu_copy(self):
        self.model.to("mps")
        self.scorer.device = torch.device("mps")
        before = {k: v.cpu().clone() for k, v in self.model.state_dict().items()}
        self.assertTrue(self.scorer.float64_agrees(self.date, 5e-5, 2e-5))
        self.assertEqual(self.scorer.device.type, "mps")
        for key, value in self.model.state_dict().items():
            self.assertEqual(value.device.type, "mps", key)
            self.assertTrue(torch.equal(value.cpu(), before[key]), key)
        with self._perturb_adapter_scores(only_float32=True):
            result = self.scorer.check_baselines()
        self.assertTrue(result["passed"], result["parity"])
        self.assertEqual(result["parity"]["float64_rechecked_facts"], 1)

    def test_float64_recheck_runs_the_memory_layer_and_restores_float32(self):
        before = {k: v.clone() for k, v in self.model.state_dict().items()}
        self.assertTrue(self.scorer.float64_agrees(self.date, 5e-5, 2e-5))
        after = self.model.state_dict()
        self.assertEqual(set(before), set(after))
        for key, value in before.items():
            self.assertEqual(after[key].dtype, value.dtype, key)
            self.assertTrue(torch.equal(after[key], value), key)
        baseline = self.scorer.check_baselines()
        self.assertTrue(baseline["passed"], baseline["parity"])
        self.assertEqual(baseline["parity"]["float64_rechecked_facts"], 0)


if __name__ == "__main__":
    unittest.main()
