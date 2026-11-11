"""Whole-layer suppression uses every physical slot on fixed evaluation examples."""

from types import SimpleNamespace
import unittest

from . import run


class WholeLayerTest(unittest.TestCase):
    def test_layer_off_contrasts_use_the_same_targets_and_correct_direction(self):
        def score(fact, mask):
            self.assertEqual(mask, range(5))
            return [-4.0, -1.0], []

        def documents(split, mask):
            self.assertEqual((split, mask), ("eval", range(5)))
            return {"overall": {"nll": 3}, "by_subject": {"s": {"nll": 3}}}, []

        ctx = SimpleNamespace(
            model=SimpleNamespace(memory=SimpleNamespace(num_slots=5)),
            evaluator=SimpleNamespace(documents=documents),
            scorer=SimpleNamespace(score=score),
            corpus=SimpleNamespace(
                facts=[
                    {
                        "role": "test",
                        "tier": "frequent",
                        "row_id": "s-test",
                        "answer": 0,
                    },
                    {
                        "role": "discovery",
                        "tier": "frequent",
                        "row_id": "s-label",
                        "answer": 0,
                    },
                ]
            ),
            baseline={
                "documents": {
                    "eval": {"overall": {"nll": 2}, "by_subject": {"s": {"nll": 2}}}
                },
                "facts": {"rows": [{"row_id": "s-test", "top1": 1.0, "margin": 2.0}]},
            },
        )
        report = run(ctx)
        self.assertEqual(report["rows"][0][-1], 1.0)
        self.assertEqual(
            report["result"]["fact_outcomes"]["frequent / test"]["off_top1"], 0.0
        )
        self.assertEqual(
            report["result"]["fact_outcomes"]["frequent / test"]["off_margin_nats"],
            -3.0,
        )
