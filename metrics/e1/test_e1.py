"""A known selective lesion and its matched off-subject control."""

from types import SimpleNamespace
import unittest

from . import run
from ..matching import matched_masks
import random


class SubjectAblationTest(unittest.TestCase):
    def test_lexically_adjusted_target_and_control_have_opposite_effects(self):
        discovery = [
            dict(
                doc_id=subject,
                subject=subject,
                ids=[slot],
                token=31,
                weighted_norms=[1.0],
                weights=[1.0],
                cohort="text",
            )
            for slot, subject in enumerate(("math", "code"))
        ]

        def documents(split, mask):
            return {
                "by_subject": {
                    s: {"nll": 1.0 + (i in mask)}
                    for i, s in enumerate(("math", "code"))
                }
            }, []

        ctx = SimpleNamespace(
            discovery_reads=discovery,
            evaluator=SimpleNamespace(documents=documents),
            baseline={"documents": {"eval": documents("eval", ())[0]}},
            lesion_size=1,
            controls=2,
            seed=0,
        )
        result = run(ctx)["result"]
        self.assertEqual(result["matched_subjects"], 2)
        self.assertEqual(result["subjects"]["math"]["slots"], [0])
        self.assertEqual(
            result["subjects"]["math"]["matched_contrasts_nll"], [-1.0, -1.0]
        )
        self.assertEqual(result["mean_specificity_excess_nll"], 2.0)

    def test_control_requires_two_distinct_eligible_donors(self):
        profile = {0: (2, 1), 1: (1, 1), 2: (1, 1), 3: (4, 1)}
        self.assertEqual(
            matched_masks([0, 1], profile, profile, 1, random.Random(1)), [(2, 3)]
        )
        profile[2] = (1, 3)
        self.assertEqual(
            matched_masks([0, 1], profile, profile, 1, random.Random(1)), []
        )
