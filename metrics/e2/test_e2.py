"""Selection, controls, and held-out outcomes for the data-v1 single-slot test."""

import json
from types import SimpleNamespace
import unittest

from .single_slot import run_slot_removal
from . import run as run_e2


def fixture():
    facts = []
    for attr in ("city", "job"):
        for role, n in (("discovery", 2), ("test", 2), ("paraphrase", 4)):
            for i in range(n):
                key = f"person-{attr}"
                facts.append(
                    dict(
                        fact_id=key,
                        person="person",
                        attribute=attr,
                        tier="frequent",
                        row_id=f"{key}-{role}{i}",
                        role=role,
                        answer=0,
                        candidates=[[1], [2]],
                        prompt=[10, i],
                    )
                )
    return SimpleNamespace(facts=facts)


class PlantedScorer:
    def __init__(self, *, learned=True, matched=True):
        self.calls = []
        self.model = SimpleNamespace(memory=SimpleNamespace(num_slots=3))
        self.learned = learned
        self.matched = matched

    def score(self, fact, mask=(), collect=False):
        role, key = fact["role"], fact["attribute"]
        self.calls.append((role, tuple(mask), collect))
        # City has the only learned discovery association. Slot 0 has the
        # highest gate mass but no norm match; 1 is target and 2 its donor.
        slots = [0, 1, 2]
        norms = [200, 2, 2 if self.matched else 0.05]
        if role == "discovery":
            scores = [-1.0, -2.0] if self.learned and key == "city" else [-2.0, -1.0]
        elif isinstance(mask, range) and mask == range(self.model.memory.num_slots):
            scores = [-4.0, -2.0]
        elif key == "city" and 1 in mask:
            scores = [-3.0, -2.0]
        else:
            scores = [-1.0, -2.0]
        sites = []
        if collect:
            if role != "discovery":
                raise AssertionError(
                    "An evaluation prompt was used to choose target or donor slots"
                )
            sites.append(
                {
                    "ids": slots,
                    "weights": [0.45, 0.30, 0.25],
                    "vectors": [[x] for x in norms],
                }
            )
        return scores, sites


class V1SingleSlot(unittest.TestCase):
    def test_redundant_slots_and_bounded_prefix(self):
        class Redundant(PlantedScorer):
            def score(self, row, mask=(), collect=False):
                scores = [-1.0, -2.0] if row["attribute"] == "city" else [-2.0, -1.0]
                if row["attribute"] == "city" and {0, 1}.issubset(mask):
                    scores = [-2.0, -1.0]
                sites = (
                    [
                        {
                            "ids": [0, 1, 2, 3],
                            "weights": [0.32, 0.28, 0.22, 0.18],
                            "vectors": [[1.0]] * 4,
                        }
                    ]
                    if collect
                    else []
                )
                return scores, sites

        ctx = SimpleNamespace(
            corpus=fixture(), scorer=Redundant(), seed=7, controls=2, max_prefix=1
        )
        limited = run_e2(ctx)["result"]["cumulative"]["facts"]
        self.assertEqual(limited["person-city"]["status"], "prefix_limit_reached")
        self.assertEqual(limited["person-job"]["status"], "unlearned_discovery")
        ctx.max_prefix = 4
        measured = run_e2(ctx)["result"]["cumulative"]["facts"]["person-city"]
        self.assertEqual(measured["status"], "matched")
        self.assertEqual(measured["core_size"], 2)
        self.assertEqual(measured["core_slots"], [0, 1])
        self.assertEqual(measured["matched_masks"], [[2, 3]] * 2)
        self.assertEqual(measured["matched_erasure_rate"], 0.0)
        self.assertEqual(
            measured["collateral"]["same_person_other_facts"]["masked"]["top1_credit"],
            0.0,
        )

    def test_matched_slot_changes_only_planted_fact_on_unseen_rows(self):
        scorer, corpus = PlantedScorer(), fixture()
        result = run_slot_removal(scorer, corpus)
        json.dumps(result, allow_nan=False)
        self.assertEqual(
            (result["status"], result["eligible_facts"], result["discovery_facts"]),
            ("matched", 1, 2),
        )
        self.assertEqual(result["target"]["slot"], 1)
        self.assertEqual(result["target"]["rank_by_gate_mass"], 2)
        self.assertEqual(result["matched_masks"], [[2]])
        self.assertEqual(result["distinct_controls"], 1)
        for category in ("test", "paraphrase"):
            effect = result["effects"][category]
            self.assertEqual(
                effect["target_minus_mean_control_damage"],
                dict(
                    gold_logp_drop_nats=2.0,
                    margin_drop_nats=2.0,
                    top1_credit_drop=1.0,
                    rank_worsening=1.0,
                ),
            )
            self.assertTrue(all(category in row for row in effect["rows"]))
        self.assertEqual(
            result["effects"]["same_person_other_facts_test"]["target_damage"][
                "margin_drop_nats"
            ],
            0.0,
        )
        off = result["effects"]["test"]["whole_layer_off"]
        self.assertEqual(
            (off["num_slots"], off["damage"]["gold_logp_drop_nats"]), (3, 3.0)
        )
        self.assertEqual(
            [role for role, mask, _ in scorer.calls if mask == (0, 1, 2)],
            ["test", "test"],
        )
        last_discovery = max(
            i for i, c in enumerate(scorer.calls) if c[0] == "discovery"
        )
        self.assertTrue(
            all(not c[1] and c[2] for c in scorer.calls[: last_discovery + 1])
        )
        self.assertFalse(any(c[2] for c in scorer.calls[last_discovery + 1 :]))
        corpus.facts.reverse()
        self.assertEqual(run_slot_removal(PlantedScorer(), corpus), result)

    def test_unlearned_checkpoint_exercises_diagnostic_with_matched_control(self):
        result = run_slot_removal(
            PlantedScorer(learned=False), fixture(), seed=0, controls=4
        )
        self.assertEqual(result["status"], "diagnostic_matched")
        self.assertTrue(result["diagnostic"])
        self.assertEqual(result["eligible_facts"], 0)
        self.assertEqual(result["distinct_controls"], 1)

    def test_matching_calipers_are_never_relaxed(self):
        result = run_slot_removal(PlantedScorer(matched=False), fixture())
        self.assertEqual(result["status"], "no_matched_controls")
        self.assertEqual(result["matched_masks"], [])
        self.assertIsNone(result["effects"]["test"]["target_minus_mean_control_damage"])

    def test_no_dense_or_invented_slot_when_reads_empty(self):
        class NoRead(PlantedScorer):
            def score(self, fact, mask=(), collect=False):
                scores, _ = super().score(fact, mask=mask, collect=False)
                return scores, []

        result = run_slot_removal(NoRead(), fixture())
        self.assertEqual(result["status"], "no_discovery_reads")
        self.assertIsNone(result["target"])


class FactListAndCollateralCap(unittest.TestCase):
    def test_fixed_fact_list_restricts_discovery(self):
        from . import discovery_rows

        corpus = fixture()
        ctx = SimpleNamespace(corpus=corpus, e2_facts=("person-job",))
        self.assertEqual({r["fact_id"] for r in discovery_rows(ctx)}, {"person-job"})
        ctx = SimpleNamespace(corpus=corpus)
        self.assertEqual(
            {r["fact_id"] for r in discovery_rows(ctx)}, {"person-city", "person-job"}
        )

    def test_collateral_sample_is_fixed_and_bounded(self):
        from . import _sample_rows

        rows = [dict(row_id=f"r{i:02d}") for i in range(30)]
        self.assertIs(_sample_rows(rows, None, "s"), rows)
        self.assertIs(_sample_rows(rows, 30, "s"), rows)
        picked = _sample_rows(rows, 5, "s")
        self.assertEqual(len(picked), 5)
        self.assertEqual(picked, _sample_rows(rows, 5, "s"))


if __name__ == "__main__":
    unittest.main()
