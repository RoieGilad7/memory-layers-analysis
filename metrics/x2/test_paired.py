"""Paired learned-versus-frozen comparison on real report structure."""

import copy
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from ..test_runner_integration import RunnerIntegration
from .paired import paired, summary_rows


class PairedX2(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        harness = RunnerIntegration()
        harness.setUp()
        with TemporaryDirectory() as temp:
            ckpt = Path(temp) / "x.pt"
            ckpt.write_bytes(b"")
            cls.learned = harness._evaluate(ckpt)
        cls.learned["model"]["config"] = {"style": "pkm", "freeze_keys": False}

    def twin(self):
        twin = copy.deepcopy(self.learned)
        twin["model"]["config"]["freeze_keys"] = True
        return twin

    def test_identical_models_have_zero_differences(self):
        result = paired(self.learned, self.twin())
        group = result["q2"]["frequent/test"]["top1"]
        self.assertEqual(group["learned_minus_twin"], 0.0)
        self.assertEqual(group["items"], 12)
        self.assertEqual(group["clusters"], 3)
        for fraction in result["e1"].values():
            self.assertEqual(
                fraction["specificity_excess_nll"]["learned_minus_twin"], 0.0
            )
        self.assertEqual(result["e2"]["facts_compared"], 6)
        self.assertIn(
            "learned training check not passed or not recorded", result["limitations"]
        )
        self.assertEqual(result["interpretation"], "validation_only")
        self.assertTrue(summary_rows(result))

    def test_difference_sign_is_learned_minus_twin(self):
        twin = self.twin()
        for row in twin["metrics"]["Q2"]["result"]["rows"]:
            row["top1"] = row["top1"] - 0.5
        result = paired(self.learned, twin)
        self.assertEqual(
            result["q2"]["frequent/test"]["top1"]["learned_minus_twin"], 0.5
        )

    def test_order_and_mismatch_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "learned-key report first"):
            paired(self.twin(), self.learned)
        other = self.twin()
        other["step"] = 99
        with self.assertRaisesRegex(ValueError, "step"):
            paired(self.learned, other)


if __name__ == "__main__":
    unittest.main()
