"""The shared E2 cohort keeps only facts that every checkpoint recalls."""

import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from .cli import main


def report(statuses):
    facts = {k: {"status": v} for k, v in statuses.items()}
    return {"metrics": {"E2": {"result": {"cumulative": {"facts": facts}}}}}


class Cohort(unittest.TestCase):
    def test_intersection_of_known_facts(self):
        with TemporaryDirectory() as temp:
            root = Path(temp)
            a = root / "a.json"
            b = root / "b.json"
            a.write_text(
                json.dumps(
                    report(
                        {
                            "p-city": "matched",
                            "p-job": "matched",
                            "q-job": "unlearned_discovery",
                        }
                    )
                )
            )
            b.write_text(
                json.dumps(
                    report(
                        {
                            "p-city": "prefix_limit_reached",
                            "p-job": "at_chance_on_test",
                            "q-job": "matched",
                        }
                    )
                )
            )
            bundle = root / "bundle"
            bundle.mkdir()
            out = root / "out"
            self.assertEqual(
                main(
                    [
                        "--bundle",
                        str(bundle),
                        "--output-dir",
                        str(out),
                        "--make-e2-cohort",
                        str(a),
                        str(b),
                    ]
                ),
                0,
            )
            cohort = json.loads((out / "e2-cohort.json").read_text())
            self.assertEqual(cohort["fact_ids"], ["p-city"])


if __name__ == "__main__":
    unittest.main()
