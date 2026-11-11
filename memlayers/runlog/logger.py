"""RunLogger: files first, then the optional sinks, each one fenced off."""

from __future__ import annotations

import sys
import traceback
from typing import Any, Dict, Iterable, List, Optional

__all__ = ["Sink", "RunLogger"]


class Sink:
    """What a sink may implement; every method is optional."""

    name = "sink"

    def train(self, row: Dict[str, Any]) -> None: ...

    def eval(self, rows: List[Dict[str, Any]]) -> None: ...

    def final(self, final_metrics: Dict[str, Any]) -> None: ...

    def files(self, paths: Iterable) -> None: ...

    def finish(self, state: str, step: int, error: Optional[str] = None) -> None: ...


class RunLogger:
    def __init__(self, files, sinks: Optional[List[Sink]] = None):
        self.files = files  # FilesSink: never fenced, a failure here is real
        self.sinks: List[Sink] = list(sinks or [])
        self.disabled: Dict[str, str] = {}

    def _forward(self, method: str, *args, **kwargs) -> None:
        for sink in list(self.sinks):
            try:
                getattr(sink, method)(*args, **kwargs)
            except Exception as e:  # noqa: BLE001 - any sink failure is fenced
                self.sinks.remove(sink)
                reason = f"{type(e).__name__}: {e}"
                self.disabled[sink.name] = reason
                print(
                    f"[runlog] WARNING: the {sink.name} sink failed in {method}() "
                    f"and is off for the rest of this run ({reason}). The run-dir "
                    f"files are complete; backfill later with "
                    f"`python -m memlayers.wandb_sync <run_dir>`.",
                    file=sys.stderr,
                    flush=True,
                )
                if getattr(sink, "debug", False):
                    traceback.print_exc()

    def log_train(self, row: Dict[str, Any]) -> None:
        self.files.train(row)
        self._forward("train", row)

    def log_eval(self, rows: List[Dict[str, Any]]) -> None:
        self.files.eval(rows)
        self._forward("eval", rows)

    def log_final(self, final_metrics: Dict[str, Any]) -> None:
        self.files.final(final_metrics)
        self._forward("final", final_metrics)

    def log_files(self, paths: Iterable) -> None:
        paths = list(paths)
        self.files.files(paths)
        self._forward("files", paths)

    def finish(self, state: str, step: int, error: Optional[str] = None) -> None:
        self.files.finish(state, step, error)
        self._forward("finish", state, step, error)
