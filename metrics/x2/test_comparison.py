"""Tests for preregistered empirical X2 margins and unavailable comparisons."""

import unittest

from .comparison import calibrate, compare


def report(seed, value, frozen=False):
    return {
        "settings": {"seed": seed, "lr": 0.01},
        "analysis": {"seed": 0, "controls": 4},
        "step": 20,
        "data_hash": "identical-data",
        "fixture": False,
        "config": {"style": "pkm", "freeze_keys": frozen, "width": 8},
        "training_check": "pass",
        "Q1": {"overall": {"ppl": value}, "by_subject": {"blue": {}, "red": {}}},
        "U4": {"excess_bits": value / 10},
        "E1": {
            "mean_specificity_excess_nll": value / 10,
            "subjects": {"red": {"specificity_excess_nll": value / 10}},
        },
        "E2": {
            "mean_matched_core_fraction": 0.5,
            "facts": {"abc": {"status": "matched"}},
        },
    }


class SeedComparison(unittest.TestCase):
    def setUp(self):
        self.learned = [report(11, 2.0), report(12, 3.0), report(13, 4.0)]

    def test_locked_range_boundary_and_directions(self):
        manifest = calibrate(self.learned)
        metric = manifest["metrics"]["Q1.overall.ppl"]
        self.assertEqual(metric["learned_mean"], 3.0)
        self.assertEqual(metric["margin"], 2.0)
        near = compare(manifest, report(11, 5.0, True))["metrics"]["Q1.overall.ppl"]
        self.assertEqual(near["learned_minus_twin"], -2.0)
        self.assertTrue(near["within_margin"])
        far = compare(manifest, report(11, 6.0, True))["metrics"]["Q1.overall.ppl"]
        self.assertFalse(far["within_margin"])
        self.assertEqual(far["observed_learned_direction"], "lower")
        self.assertEqual(manifest["metrics"]["Q1.overall.ppl"], metric)
        self.assertEqual(
            manifest["metrics"]["V2.fact.top1_share"]["available_seeds"], 0
        )
        self.assertIsNone(manifest["metrics"]["V2.fact.top1_share"]["margin"])

    def test_requires_three_distinct_comparable_learned_seeds(self):
        with self.assertRaisesRegex(ValueError, "three"):
            calibrate(self.learned[:2])
        with self.assertRaisesRegex(ValueError, "distinct"):
            calibrate(self.learned + self.learned[:1])
        self.learned[0]["analysis"]["seed"] = 17
        with self.assertRaisesRegex(ValueError, "analysis"):
            calibrate(self.learned)
        self.learned[0]["config"]["freeze_keys"] = True
        with self.assertRaisesRegex(ValueError, "learned-key PKM"):
            calibrate(self.learned)

    def test_twin_signature_and_support(self):
        manifest = calibrate(self.learned)
        twin = report(11, 2.0, True)
        twin["E2"]["facts"] = {"xyz": {"status": "matched"}}
        result = compare(manifest, twin)["metrics"]["E2.mean_matched_core_fraction"]
        self.assertIsNone(result["within_margin"])
        self.assertIn("cohort", result["reason"])
        twin["Q1"]["by_subject"].pop("red")
        with self.assertRaisesRegex(ValueError, "subjects"):
            compare(manifest, twin)
        twin["config"]["freeze_keys"] = False
        with self.assertRaisesRegex(ValueError, "frozen-key PKM"):
            compare(manifest, twin)

    def test_fixture_limits_interpretation_and_checks_are_only_reported(self):
        for row in self.learned:
            row["fixture"] = True
        self.learned[0]["training_check"] = "fail"
        twin = report(11, 3.0, True)
        twin["fixture"] = True
        twin["training_check"] = None
        result = compare(calibrate(self.learned), twin)
        self.assertEqual(result["interpretation"], "validation_only")
        self.assertEqual(result["limitations"], ["fixture data"])
        self.assertEqual(
            result["training_checks"],
            {"11": "fail", "12": "pass", "13": "pass", "twin": None},
        )
        self.assertEqual(result["seed_count"], 3)

    def test_passing_checks_give_a_study_result(self):
        result = compare(calibrate(self.learned), report(11, 3.0, True))
        self.assertEqual(result["interpretation"], "study")


if __name__ == "__main__":
    unittest.main()
