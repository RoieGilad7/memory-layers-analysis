"""Regression checks for data identity, token windows and the exposure-based baseline."""

import hashlib
import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import numpy as np

from . import bundle as v1
from .frequency import popularity_baseline


class TestReleaseManifest(unittest.TestCase):
    def test_native_fetch_layout_verifies_content_and_rejects_wrong_release(self):
        with TemporaryDirectory() as temp:
            root = Path(temp) / "data" / "v1"
            entries = []
            for name in v1.REQUIRED:
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(b"abc")
                entries.append(
                    dict(path=name, bytes=3, sha256=hashlib.sha256(b"abc").hexdigest())
                )
            canonical = json.dumps(
                entries, sort_keys=True, separators=(",", ":")
            ).encode()
            fingerprint = hashlib.sha256(canonical).hexdigest()
            manifest = root.parent / "manifests" / "v1.json"
            manifest.parent.mkdir()
            manifest.write_text(
                json.dumps({"data_sha256": fingerprint, "files": entries})
            )
            with self.assertRaisesRegex(ValueError, "frozen data-v1"):
                v1._verified_files(root)
            with patch.object(v1, "DATA_SHA256", fingerprint):
                self.assertEqual(set(v1.REQUIRED), set(v1._verified_files(root)))
                (root / "tokens/train.bin").write_bytes(b"xyz")
                with self.assertRaisesRegex(
                    ValueError, "SHA-256 mismatch for tokens/train.bin"
                ):
                    v1._verified_files(root)


class TestExposureBaseline(unittest.TestCase):
    def test_aligned_final_block_never_counts_and_ties_get_fractional_credit(self):
        import pyarrow as pa
        import pyarrow.parquet as pq

        with TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "tokens").mkdir()
            np.zeros(3 * 512, dtype="<u2").tofile(root / "tokens/train.bin")
            pids = ["a", "b", "last"]
            pq.write_table(
                pa.table({"start": [0, 512, 1024], "person_id": pids}),
                root / "tokens/train.idx.parquet",
            )
            corpus = SimpleNamespace(
                root=root,
                people={p: {"facts": {"city": p}} for p in pids},
                value_lists={"city": pids},
                selection={"people_by_tier": {"frequent": pids}},
                facts=[
                    dict(person=p, attribute="city", true_value=p, role="test", tier=p)
                    for p in pids
                ],
            )
            before = popularity_baseline(corpus, tokens_seen=0, data_seed=0)
            self.assertAlmostEqual(before["by_tier_role"]["a/test"]["top1"], 1 / 3)
            self.assertEqual(before["by_tier_role"]["a/test"]["mean_rank"], 2)
            # Two complete loader epochs traverse 4 sequences. The last file block
            # lacks the next-token target and never appears, even across epochs.
            after = popularity_baseline(corpus, tokens_seen=4 * 512, data_seed=0)
            self.assertEqual(
                after["selected_people_exposures"], {"a": 2, "b": 2, "last": 0}
            )
            self.assertEqual(after["by_tier_role"]["a/test"]["top1"], 0.5)
            self.assertEqual(after["by_tier_role"]["a/test"]["mean_rank"], 1.5)
            self.assertEqual(after["by_tier_role"]["last/test"]["mean_rank"], 3)
            invalid = popularity_baseline(corpus, tokens_seen=513, data_seed=0)
            self.assertEqual(invalid["status"], "unavailable")


@unittest.skipUnless(
    os.getenv("MEMLAYERS_DATA_V1"), "set MEMLAYERS_DATA_V1 to test the published bundle"
)
class TestPublishedSlice(unittest.TestCase):
    def test_seeded_slice_preserves_roles_candidates_and_pilot_exposures(self):
        c = v1.load_v1_slice(os.environ["MEMLAYERS_DATA_V1"])
        self.assertEqual(c.fingerprint, v1.DATA_SHA256)
        self.assertEqual(c.selection["people_by_tier"]["frequent"], ["p000380"])
        self.assertEqual(
            c.selection["fact_rows_by_role"],
            {"discovery": 40, "test": 40, "paraphrase": 80},
        )
        self.assertEqual(len({f["row_id"] for f in c.facts}), len(c.facts))
        self.assertEqual(len({f["fact_id"] for f in c.facts}), 20)
        self.assertEqual(
            {
                len(key)
                for f in c.facts
                if f["attribute"] == "birth_date"
                for key in f["candidates"]
            },
            {2},
        )
        self.assertEqual(
            {
                len(key)
                for f in c.facts
                if f["attribute"] != "birth_date"
                for key in f["candidates"]
            },
            {1},
        )
        for split in ("discovery", "eval"):
            docs = c.docs[split]
            self.assertEqual(len({d["subject"] for d in docs}), 6)
            self.assertTrue(
                all(
                    2 <= len(d["tokens"]) <= 65 and 50256 not in d["tokens"]
                    for d in docs
                )
            )
        pop = popularity_baseline(c, tokens_seen=95518720, data_seed=0)
        self.assertEqual(pop["biography_copies"], 120444)


if __name__ == "__main__":
    unittest.main()


class TestSubjectsAndPeople(unittest.TestCase):
    def test_untrained_subject_is_left_out_by_default(self):
        import pyarrow as pa
        import pyarrow.parquet as pq

        with TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "tokens").mkdir()
            pq.write_table(
                pa.table({"subject": ["bio", "Pile-CC", "Github"]}),
                root / "tokens/train.idx.parquet",
            )
            self.assertEqual(v1.trained_subjects(root), ["Github", "Pile-CC"])
            (root / "heldout").mkdir()
            for half in ("label", "test"):
                subjects = ["Pile-CC", "USPTO Backgrounds", "Github"]
                np.arange(30, dtype="<u2").tofile(root / f"heldout/{half}.bin")
                pq.write_table(
                    pa.table(
                        {
                            "doc_id": [f"{half}{i}" for i in range(3)],
                            "subject": subjects,
                            "start": [0, 10, 20],
                            "length": [10, 10, 10],
                            "doc_offset": [0, 0, 0],
                        }
                    ),
                    root / f"heldout/{half}.idx.parquet",
                )
            kept = v1._heldout_docs(root, 1, 4, 0, v1.trained_subjects(root))
            self.assertEqual(
                sorted(d["subject"] for d in kept["eval"]), ["Github", "Pile-CC"]
            )
            everything = v1._heldout_docs(root, 1, 4, 0)
            self.assertEqual(len(everything["eval"]), 3)

    def test_fact_id_splits_on_last_hyphen(self):
        self.assertEqual(v1._person_of("p-0012-birth_date"), "p-0012")
