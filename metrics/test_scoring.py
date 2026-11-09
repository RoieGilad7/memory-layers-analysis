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


if __name__ == "__main__":
    unittest.main()
