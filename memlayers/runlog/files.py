"""FilesSink: the run-dir files, always on, written before any other sink."""

from __future__ import annotations

import csv
import datetime as _dt
import json
import os
import socket
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence

__all__ = ["FilesSink", "write_status", "TRAIN_FIELDS"]

# the training log's columns (memlayers.train.CSV_FIELDS re-exports this)
TRAIN_FIELDS = [
    "step",
    "loss",
    "lr",
    "lr_memory",
    "step_time_s",
    "tokens_per_s",
    "tokens_seen",
    "peak_mem_bytes",
    "grad_norm",
    # constant for a run, but a log line has to be self-describing:
    # a loss curve is meaningless without knowing which data made it
    "data_version",
    "data_sha256",
]


def write_status(run_dir, state: str, step: int, error: Optional[str] = None) -> dict:
    st = {
        "state": state,
        "step": int(step),
        "updated_at": _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds"),
        "error": error,
        "host": socket.gethostname(),
        "pid": os.getpid(),
    }
    path = Path(run_dir) / "status.json"
    tmp = path.with_name(f".{path.name}.tmp-{os.getpid()}")
    tmp.write_text(json.dumps(st, indent=2) + "\n")
    os.replace(tmp, path)
    return st


class FilesSink:
    name = "files"

    def __init__(
        self,
        run_dir,
        train_log: str = "train_log.csv",
        write_status_on_finish: bool = True,
    ):
        self.run_dir = Path(run_dir)
        self.train_path = self.run_dir / train_log
        self.write_status_on_finish = write_status_on_finish

    # ---- train_log.csv -----------------------------------------------------
    def train(self, row: Dict[str, Any]) -> None:
        started = self.train_path.exists() and self.train_path.stat().st_size > 0
        fields: Sequence[str] = TRAIN_FIELDS
        if started:
            # resuming a run whose log predates a column change: keep writing
            # under the header already in the file, or values shift columns
            with open(self.train_path, newline="") as fh:
                existing = next(csv.reader(fh), None)
            if existing and existing != TRAIN_FIELDS:
                fields = existing
        with open(self.train_path, "a" if started else "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(fields), extrasaction="ignore")
            if not started:
                w.writeheader()
            w.writerow({k: row.get(k, "") for k in fields})

    # ---- evals.csv ---------------------------------------------------------
    def eval(self, rows: List[Dict[str, Any]]) -> None:
        from memlayers.eval.writers import EvalsCSV

        csvf = EvalsCSV(self.run_dir / "evals.csv")
        post = [r for r in rows if r["stage"] == "posthoc"]
        live = [r for r in rows if r["stage"] != "posthoc"]
        if live or not post:
            csvf.append(live)  # also creates the header for an all-skipped point
        if post:
            csvf.replace_posthoc(post)

    # ---- final_metrics.json ------------------------------------------------
    def final(self, final_metrics: Dict[str, Any]) -> None:
        from memlayers.eval.writers import write_json

        write_json(self.run_dir / "final_metrics.json", final_metrics)

    def files(self, paths: Iterable) -> None:
        return None  # they are already in the run dir

    def finish(self, state: str, step: int, error: Optional[str] = None) -> None:
        if self.write_status_on_finish:
            write_status(self.run_dir, state, step, error)
