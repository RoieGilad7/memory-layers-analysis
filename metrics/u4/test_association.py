import unittest

from . import _specificity, rank_subject_slots


class SubjectAssociationTest(unittest.TestCase):
    def test_token_identity_is_conditioned_out(self):
        rows = [
            dict(doc_id=str(i), subject=str(i % 2), token=w, ids=[w])
            for i in range(12)
            for w in [i % 2] * 8 + [1 - i % 2]
        ]
        self.assertAlmostEqual(_specificity(rows, 0, 19)["conditional_mi_bits"], 0)
        self.assertEqual(rank_subject_slots(rows), {"0": [], "1": []})

    def test_identical_token_with_subject_specific_reads(self):
        rows = [
            dict(doc_id=str(i), subject=str(i % 2), token=5, ids=[i % 2])
            for i in range(24)
        ]
        self.assertAlmostEqual(_specificity(rows, 0, 19)["conditional_mi_bits"], 1)
        self.assertEqual(rank_subject_slots(rows), {"0": [0], "1": [1]})
