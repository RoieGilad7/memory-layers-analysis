import unittest

import torch

from . import composition


class SlotCompositionTest(unittest.TestCase):
    def test_equal_opposing_contributions_cancel(self):
        rows = [
            dict(
                ids=[0, 1],
                weights=[0.75, 0.25],
                vectors=torch.tensor([[1.0, 0.0], [-3.0, 0.0]]),
            )
        ]
        result = composition(rows, seed=7)
        self.assertAlmostEqual(result["top1_share"], 0.5)
        self.assertAlmostEqual(result["top2_share"], 1)
        self.assertAlmostEqual(result["resultant_over_sum_norms"], 0)
        self.assertAlmostEqual(result["mean_cosine"], -1)
        self.assertEqual(result["matched_pairs"], 1)

    def test_co_read_alignment_depends_on_norm_matched_controls(self):
        slots = torch.tensor([[1.0, 0.0], [1.0, 0.0], [0.0, 1.0], [0.0, 1.0]])
        rows = []
        for i in range(32):
            ids = [0, 1] if i % 2 else [2, 3]
            rows.append(dict(ids=ids, weights=[0.5, 0.5], vectors=slots[ids].clone()))
        self.assertGreater(composition(rows, 0)["cosine_excess"], 0.4)
        for row in rows:
            if row["ids"] == [2, 3]:
                row["vectors"] *= 9
        self.assertAlmostEqual(composition(rows, 0)["cosine_excess"], 0)
