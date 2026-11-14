"""The training metric `fact_recall` ranks probe scores with `fact_metrics`."""

from types import SimpleNamespace
import unittest

from .training import fact_recall


class Probe:
    def __init__(self):
        row = lambda tier, role, attr, true: SimpleNamespace(
            tier=tier, role=role, attribute=attr, true_index=true
        )
        self.rows = [
            row("frequent", "test", "major", 0),
            row("frequent", "test", "major", 1),
            row("frequent", "paraphrase", "major", 0),
        ]

    def score(self, model, device, batch_tokens, block_size, collect_scores):
        assert collect_scores
        # row 0: correct; row 1: true value second of three; row 2: a tie for best
        return {"_scores": [[-1.0, -2.0, -3.0], [-1.0, -2.0, -3.0], [-1.0, -1.0, -3.0]]}


class TrainingFactRecall(unittest.TestCase):
    def test_keys_and_tie_aware_scoring(self):
        ctx = SimpleNamespace(
            fact_probe=Probe,
            model=None,
            device="cpu",
            fact_batch_tokens=1,
            block_size=8,
        )
        got = fact_recall(ctx)
        self.assertEqual(got["top1/frequent/test"], 0.5)
        self.assertEqual(got["rank/frequent/test"], 1.5)
        self.assertEqual(got["margin/frequent/test"], 0.0)  # (+1 and -1) / 2
        self.assertEqual(got["top1/frequent/test/major"], 0.5)
        # A two-way tie for best gives half credit and mid-rank 1.5.
        self.assertEqual(got["top1/frequent/paraphrase"], 0.5)
        self.assertEqual(got["rank/frequent/paraphrase"], 1.5)
        self.assertNotIn("top1/frequent/paraphrase/major", got)


if __name__ == "__main__":
    unittest.main()
