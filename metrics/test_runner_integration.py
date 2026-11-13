"""End-to-end run of every checkpoint metric on a tiny PKM and a synthetic slice."""

import json
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import torch

from . import runner
from .checkpoint import RoieModel, upstream_model_types


def _corpus():
    docs = {}
    for split in ("discovery", "eval"):
        docs[split] = [
            dict(
                doc_id=f"{split}-{subject}-{i}",
                subject=subject,
                split=split,
                tokens=[(3 * i + j + k) % 16 for j in range(10)],
            )
            for k, subject in enumerate(("Pile-CC", "Github"))
            for i in range(3)
        ]
    facts = []
    for person in ("a", "b", "c"):
        for attr, candidates in (("major", [[4], [5], [6]]), ("employer", [[7], [8]])):
            for role, n in (("discovery", 2), ("test", 2), ("paraphrase", 2)):
                for i in range(n):
                    facts.append(
                        dict(
                            row_id=f"{person}-{attr}-{role}{i}",
                            fact_id=f"{person}-{attr}",
                            person=person,
                            attribute=attr,
                            tier="frequent",
                            role=role,
                            split="discovery" if role == "discovery" else "eval",
                            rewording_id=i,
                            template_id=i,
                            prompt=[1, 2 + i, ord(person) % 16],
                            candidates=candidates,
                            answer=0,
                            preceding_fact_count=0,
                        )
                    )
    return SimpleNamespace(
        docs=docs,
        facts=facts,
        vocab=list(map(str, range(16))),
        fingerprint="test",
        selection={},
        context=10,
    )


def _args(**kw):
    base = dict(
        device="cpu",
        layer=None,
        seed=3,
        permutations=9,
        controls=2,
        max_prefix=4,
        dense=None,
        x2_margin=None,
        people_per_tier=1,
        frequent_people=3,
        docs_per_subject=3,
        doc_tokens=9,
        e1_fractions=(0.25, 0.5),
        e1_max_slots=16,
        e2_facts=(),
        collateral_rows=5,
        v2_stride=2,
        rank_rows=4,
        include_untrained_subjects=False,
        training_check=None,
    )
    base.update(kw)
    return SimpleNamespace(**base)


class RunnerIntegration(unittest.TestCase):
    def setUp(self):
        torch.manual_seed(0)
        torch.set_num_threads(1)
        GPT, GPTConfig = upstream_model_types()
        native = GPT(
            GPTConfig(
                vocab_size=16,
                n_layer=1,
                n_embd=8,
                n_head=2,
                block_size=16,
                memory_layers=(0,),
                memory_kind="pkm",
                memory=dict(
                    num_keys=4, dim_head=4, heads=2, topk=3, query_batchnorm=False
                ),
            )
        ).eval()
        self.model = RoieModel(native, 0)
        self.meta = dict(
            config={"train": {"seed": 0}},
            report_config={"style": "pkm", "freeze_keys": False},
            step=10,
            tokens_seen=5120,
            layer_index=0,
            style="pkm",
            data_v1={"status": "initialization_only", "data_seed": 0},
        )

    def _evaluate(self, path, **kw):
        stub = lambda ctx: dict(title="stub", columns=[], rows=[], result={})
        with (
            patch.object(
                runner, "load_roie_model", return_value=(self.model, self.meta)
            ),
            patch.object(runner.frequency, "run", stub),
            patch.object(runner.resources, "run", stub),
        ):
            return runner.evaluate(path, _corpus(), _args(**kw))

    def test_every_metric_runs_and_reports_are_json(self):
        with TemporaryDirectory() as temp:
            run_dir = Path(temp)
            ckpt = run_dir / "checkpoints" / "step_000010.pt"
            ckpt.parent.mkdir()
            ckpt.write_bytes(b"")
            (run_dir / "training_check.json").write_text(
                json.dumps({"verdict": "pass", "failed": []})
            )
            report = self._evaluate(ckpt)
        json.dumps(report, allow_nan=False)
        self.assertTrue(report["parity"]["passed"])
        self.assertEqual(report["training_check"]["passed"], True)
        metrics = report["metrics"]
        for key in ("Q1", "Q2", "U1", "U4", "V2", "C4", "C6", "E1", "E2"):
            self.assertIsNotNone(metrics[key]["result"], key)
        self.assertIn("nll_ci", metrics["Q1"]["result"]["overall"])
        self.assertIn(
            "top1_ci", metrics["Q2"]["result"]["by_tier_role"]["frequent/test"]
        )
        e1 = metrics["E1"]["result"]
        self.assertEqual(e1["primary_excess_fraction"], 0.25)
        for subject in e1["subjects"].values():
            if subject["doses"]:
                self.assertEqual(
                    [d["excess_fraction"] for d in subject["doses"]], [0.25, 0.5]
                )
                sizes = [d["slot_count"] for d in subject["doses"]]
                self.assertEqual(sizes, sorted(sizes))
        self.assertIn("effective_rank_fixed_rows", metrics["C6"]["result"])
        # V2 keeps vectors for a strided subset only; the others are compact.
        self.assertGreater(metrics["V2"]["result"]["text"]["tokens"], 0)

    def test_missing_training_check_is_not_a_pass(self):
        with TemporaryDirectory() as temp:
            ckpt = Path(temp) / "x.pt"
            ckpt.write_bytes(b"")
            report = self._evaluate(ckpt)
        self.assertIsNone(report["training_check"]["passed"])
        from .x2 import _gate

        self.assertEqual(_gate(report), {"passed": False, "recorded": False})


if __name__ == "__main__":
    unittest.main()
