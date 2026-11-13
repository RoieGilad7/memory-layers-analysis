"""Cluster bootstrap intervals."""

import unittest

from .stats import cluster_bootstrap, ratio_bootstrap


class Bootstrap(unittest.TestCase):
    def test_constant_values_have_a_degenerate_interval(self):
        ci = cluster_bootstrap([1.0] * 6, ["a", "a", "b", "b", "c", "c"])
        self.assertEqual(
            (ci["mean"], ci["lo"], ci["hi"], ci["clusters"]), (1.0, 1.0, 1.0, 3)
        )

    def test_interval_contains_mean_and_one_cluster_has_none(self):
        ci = cluster_bootstrap([0, 1, 0, 1, 1, 1], [1, 1, 2, 2, 3, 3], seed=4)
        self.assertLessEqual(ci["lo"], ci["mean"])
        self.assertGreaterEqual(ci["hi"], ci["mean"])
        self.assertIsNone(cluster_bootstrap([1, 2], ["x", "x"])["lo"])
        self.assertIsNone(cluster_bootstrap([], [])["mean"])

    def test_ratio_is_token_weighted(self):
        ci = ratio_bootstrap([10.0, 2.0], [5, 1])
        self.assertEqual(ci["value"], 2.0)
        self.assertEqual((ci["lo"], ci["hi"]), (2.0, 2.0))


if __name__ == "__main__":
    unittest.main()
