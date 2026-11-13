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


class LesionDose(unittest.TestCase):
    def test_prefix_covers_excess_share_and_respects_cap(self):
        from . import lesion_prefix

        ranked = [(9, 4.0), (3, 3.0), (5, 2.0), (1, 1.0)]  # total 10
        self.assertEqual(lesion_prefix(ranked, 0.1, 10), (9,))
        self.assertEqual(lesion_prefix(ranked, 0.5, 10), (3, 9))
        self.assertEqual(lesion_prefix(ranked, 0.9, 10), (3, 5, 9))
        self.assertEqual(lesion_prefix(ranked, 1.0, 10), (1, 3, 5, 9))
        self.assertEqual(lesion_prefix(ranked, 0.9, 2), (3, 9))
        self.assertEqual(lesion_prefix([], 0.5, 10), ())

    def test_exposure_counts_reads_and_gate_mass_per_subject(self):
        from . import exposure

        reads = [
            dict(subject="a", ids=[1, 2], weights=[0.75, 0.25], cohort="text"),
            dict(subject="b", ids=[2, 3], weights=[0.5, 0.5], cohort="text"),
            dict(subject="bio", ids=[1], weights=[1.0], cohort="fact"),
        ]
        out = exposure(reads, [1])
        self.assertEqual(out["a"], dict(read_share=0.5, gate_share=0.75))
        self.assertEqual(out["b"], dict(read_share=0.0, gate_share=0.0))
        self.assertNotIn("bio", out)
