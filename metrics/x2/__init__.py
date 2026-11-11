"""Compare a frozen-key twin to a range precomputed from at least three learned seeds."""

import json
from pathlib import Path
from .comparison import calibrate, compare


def source(report):
    meta = report["model"]
    entries = report["metrics"]
    needed = ("Q1", "U4", "E1", "E2", "V2")
    if not report["parity"]["passed"] or any(
        entries[k]["result"] is None for k in needed
    ):
        raise ValueError(
            "X2 requires a complete report with successful baseline parity"
        )
    results = {k: entries[k]["result"] for k in needed}
    results["E2"] = results["E2"]["cumulative"]
    settings = {
        **meta["train_settings"],
        "seed": meta["seed"],
        "tokens_seen": report["tokens_seen"],
    }
    return dict(
        **results,
        data_hash=report["data_sha256"],
        step=report["step"],
        fixture=False,
        config=meta["config"],
        settings=settings,
        analysis=report["analysis"],
        training_gate={"passed": False},
    )  # Native checkpoints do not record a discovery convergence history.


def lock(paths):
    reports = [json.loads(Path(p).read_text(encoding="utf-8")) for p in paths]
    locked = calibrate([source(r) for r in reports])
    locked["data_seeds"] = {
        str(r["model"]["seed"]): r["provenance"]["data_seed"] for r in reports
    }
    return locked


def run(report, manifest):
    columns = ["Metric", "Learned mean", "Frozen", "Seed range", "Within range"]
    if manifest is None:
        return dict(
            title="Learned versus frozen keys",
            columns=columns,
            rows=[],
            result=None,
            status="Requires a frozen-key twin and a margin file from three or more learned-key seeds.",
        )
    locked = json.loads(Path(manifest).read_text(encoding="utf-8"))
    paired_seed = str(report["model"]["seed"])
    if (
        paired_seed in locked.get("data_seeds", {})
        and locked["data_seeds"][paired_seed] != report["provenance"]["data_seed"]
    ):
        raise ValueError(
            "The frozen twin and its paired learned run used different data order"
        )
    comparison = compare(locked, source(report))
    rows = [
        [k, v["learned_mean"], v["twin_value"], v["margin"], v["within_margin"]]
        for k, v in comparison["metrics"].items()
    ]
    return dict(
        title="Learned versus frozen keys",
        columns=columns,
        rows=rows,
        result=comparison,
        status="Diagnostic comparison. Native checkpoints do not record the training convergence gate.",
    )
