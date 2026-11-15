"""Flatten every scalar in the final per-checkpoint metric reports into one long CSV.

    python reports/build_final_metrics_csv.py runs/final reports/final_metrics/raw_results.csv

Columns: run, source, metric, key, value. `source` is "slice" for metrics.py
reports (runs/final/cohort/<run> for PKM, runs/final/dense-s0 for dense) and
"official" for the training runs' own final_metrics.json / training_check.json.
Per-row detail (per document, per fact, slot lists) is left out.
"""

import csv
import glob
import json
import sys
from pathlib import Path

RUNS = ["pkm-s0", "pkm-s1", "pkm-s2", "pkm_randkey-s0", "dense-s0"]
SKIP = {"rows", "facts", "slots", "slot_profiles", "discovery_rows", "ranked_discovery_reads",
        "selected_people_exposures", "text", "fact", "support", "learned_values", "test_rows",
        "attempted_fact_order", "matched_masks", "discovery_profiles", "columns", "title", "status",
        "method", "eligibility_rule", "selection_rule"}


def walk(prefix, value, out):
    if isinstance(value, dict):
        for k, v in value.items():
            if k in SKIP:
                continue
            walk(f"{prefix}.{k}" if prefix else str(k), v, out)
    elif isinstance(value, bool):
        out.append((prefix, int(value)))
    elif isinstance(value, (int, float)) or value is None:
        out.append((prefix, value))
    elif isinstance(value, str) and len(value) < 40:
        out.append((prefix, value))


def main(root, dest):
    root = Path(root)
    rows = []
    for run in RUNS:
        base = root / ("dense-s0" if run == "dense-s0" else f"cohort/{run}")
        report = json.loads(Path(glob.glob(str(base / "step_*.json"))[0]).read_text())
        pairs = []
        walk("parity", report["parity"], pairs)
        for name, entry in report["metrics"].items():
            res = entry.get("result")
            if isinstance(res, dict):
                walk(name, res, pairs)
            # Display rows for metrics whose summary lives in the table (V2, Resources).
            if name in ("V2", "Resources", "Whole layer off") and entry.get("rows"):
                cols = entry["columns"]
                for r in entry["rows"]:
                    label = " / ".join(str(x) for x in r[: 2 if name == "Whole layer off" else 1])
                    for c, v in zip(cols[(2 if name == "Whole layer off" else 1):], r[(2 if name == "Whole layer off" else 1):]):
                        if isinstance(v, (int, float)) or v is None:
                            pairs.append((f"{name}.{label}.{c}", v))
        for key, value in pairs:
            metric = key.split(".")[0]
            rows.append((run, "slice", metric, key, value))
        meta = root / "hf_meta" / run
        for k, v in json.loads((meta / "final_metrics.json").read_text())["metrics"].items():
            rows.append((run, "official", k.split("/")[0], k, v))
        check = json.loads((meta / "training_check.json").read_text())
        rows.append((run, "official", "training_check", "verdict", check["verdict"]))
        for rule, r in check["rules"].items():
            for k, v in r.items():
                if isinstance(v, (int, float, bool)) or v is None:
                    rows.append((run, "official", "training_check", f"{rule}.{k}", int(v) if isinstance(v, bool) else v))
    with open(dest, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["run", "source", "metric", "key", "value"])
        w.writerows(rows)
    print(dest, len(rows))


if __name__ == "__main__":
    main(*sys.argv[1:3])
