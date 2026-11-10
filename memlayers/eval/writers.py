"""evals.csv, final_metrics.json and training_check.json.

evals.csv is long format, one row per (step, stage, metric, key), columns
exactly `step,tokens_seen,stage,metric,metric_id,key,value`, appended after
every evaluation.
"""

from __future__ import annotations

import csv
import json
import math
import os
from pathlib import Path
from typing import Any, Dict, Iterable, List

__all__ = [
    "EVALS_COLUMNS",
    "EvalsCSV",
    "write_final_metrics",
    "merge_final_metrics",
    "write_json",
    "rows_for",
]

EVALS_COLUMNS = ["step", "tokens_seen", "stage", "metric", "metric_id", "key", "value"]


def rows_for(
    step, tokens_seen, stage, metric, metric_id, values: Dict[str, float]
) -> List[dict]:
    return [
        {
            "step": int(step),
            "tokens_seen": int(tokens_seen),
            "stage": stage,
            "metric": metric,
            "metric_id": metric_id,
            "key": k,
            "value": float(v),
        }
        for k, v in values.items()
    ]


def _atomic_write(path: Path, write) -> None:
    tmp = path.with_name(f".{path.name}.tmp-{os.getpid()}")
    with open(tmp, "w", newline="") as fh:
        write(fh)
    os.replace(tmp, path)


class EvalsCSV:
    def __init__(self, path: Path):
        self.path = Path(path)

    def read(self) -> List[dict]:
        if not self.path.exists():
            return []
        with open(self.path, newline="") as fh:
            rows = list(csv.DictReader(fh))
        for r in rows:
            r["step"] = int(r["step"])
            r["tokens_seen"] = int(r["tokens_seen"])
            r["value"] = float(r["value"])
        return rows

    def _rewrite(self, rows: Iterable[dict]) -> None:
        def w(fh):
            wr = csv.DictWriter(fh, fieldnames=EVALS_COLUMNS)
            wr.writeheader()
            for r in rows:
                wr.writerow({k: _fmt(r[k]) for k in EVALS_COLUMNS})

        _atomic_write(self.path, w)

    def append(self, rows: List[dict]) -> None:
        new = not self.path.exists()
        with open(self.path, "a", newline="") as fh:
            wr = csv.DictWriter(fh, fieldnames=EVALS_COLUMNS)
            if new:
                wr.writeheader()
            for r in rows:
                wr.writerow({k: _fmt(r[k]) for k in EVALS_COLUMNS})
            fh.flush()
            os.fsync(fh.fileno())

    def drop_after(self, step: int) -> int:
        """Drop training-time rows past `step` (a resume replays those steps).
        Post-hoc rows describe saved checkpoints and stay."""
        rows = self.read()
        keep = [r for r in rows if r["stage"] == "posthoc" or r["step"] <= step]
        if len(keep) != len(rows):
            self._rewrite(keep)
        return len(rows) - len(keep)

    def replace_posthoc(self, rows: List[dict]) -> None:
        new_keys = {(r["step"], r["metric"], r["key"]) for r in rows}
        keep = [
            r
            for r in self.read()
            if not (
                r["stage"] == "posthoc"
                and (r["step"], r["metric"], r["key"]) in new_keys
            )
        ]
        self._rewrite(keep + rows)


def _fmt(v):
    if isinstance(v, float):
        return repr(v)
    return v


def _clean(v):
    if isinstance(v, float) and not math.isfinite(v):
        return str(v)  # JSON has no NaN/inf; keep them visible as strings
    if isinstance(v, dict):
        return {k: _clean(x) for k, x in v.items()}
    if isinstance(v, list):
        return [_clean(x) for x in v]
    return v


def write_json(path: Path, obj: Any) -> Path:
    path = Path(path)
    _atomic_write(path, lambda fh: fh.write(json.dumps(_clean(obj), indent=2) + "\n"))
    return path


def final_metrics_obj(metrics, metric_ids, skipped, step, tokens_seen) -> dict:
    flat = {f"{m}/{k}": v for m, vals in metrics.items() for k, v in vals.items()}
    return {
        "metrics": dict(sorted(flat.items())),
        "metric_ids": dict(sorted(metric_ids.items())),
        "skipped": dict(sorted(skipped.items())),
        "step": int(step),
        "tokens_seen": int(tokens_seen),
    }


def merge_final_metrics(old: dict | None, new: dict) -> dict:
    """`new` folded into an existing final_metrics.json: every key of a metric
    in `new` replaces that metric's old keys (a re-run metric never keeps a
    stale key); other metrics stay. Refuses to mix two checkpoint steps."""
    if not old:
        return new
    if int(old["step"]) != int(new["step"]):
        raise ValueError(
            f"final_metrics.json is for step {old['step']}, this evaluation is step "
            f"{new['step']}: update_final=true would mix two checkpoints. Use the "
            "final step, or leave final_metrics.json alone (rows still go to evals.csv)."
        )
    rerun = set(new["metric_ids"]) | {k.split("/", 1)[0] for k in new["metrics"]}
    metrics = {
        k: v for k, v in old["metrics"].items() if k.split("/", 1)[0] not in rerun
    }
    metrics.update(new["metrics"])
    ids = {**old.get("metric_ids", {}), **new["metric_ids"]}
    skipped = {k: v for k, v in old.get("skipped", {}).items() if k not in rerun}
    skipped.update(new.get("skipped", {}))
    return {
        "metrics": dict(sorted(metrics.items())),
        "metric_ids": dict(sorted(ids.items())),
        "skipped": dict(sorted(skipped.items())),
        "step": int(new["step"]),
        "tokens_seen": int(new["tokens_seen"]),
    }


def write_final_metrics(path, metrics, metric_ids, skipped, step, tokens_seen) -> Path:
    return write_json(
        path, final_metrics_obj(metrics, metric_ids, skipped, step, tokens_seen)
    )
