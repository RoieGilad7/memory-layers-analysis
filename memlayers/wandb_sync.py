"""Backfill W&B from finished run dirs.

    python -m memlayers.wandb_sync runs/pkm-s1 [more run dirs] [--mode online]
                                   [--project memlayers] [--entity me]

Replays a run dir's train_log.csv, evals.csv, final_metrics.json and small run
files into W&B under the run's `wandb_id` (from meta.json; one is generated and
saved there if the run never had W&B), with resume="allow". What has reached
W&B in each mode is kept in the run dir's wandb_sync.json, so a run logged live
online sends nothing here, a run logged offline or with logging=files sends
everything once, and a second sync sends no new rows.

For offline runs use this, not `wandb sync <offline dir>`: the offline dir and
this replay would both upload the same rows.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

__all__ = ["sync_run", "main"]


def _train_rows(run_dir: Path) -> List[Dict[str, Any]]:
    p = run_dir / "train_log.csv"
    if not p.exists():
        p = run_dir / "log.csv"  # a pre-run-layer dir
    if not p.exists():
        return []
    with open(p, newline="") as fh:
        return list(csv.DictReader(fh))


def sync_run(
    run_dir,
    mode: str = "online",
    project: Optional[str] = None,
    entity: Optional[str] = None,
    module=None,
) -> Dict[str, int]:
    """Send what W&B does not have yet. Returns counts of what was sent."""
    from omegaconf import OmegaConf

    from .eval.writers import EvalsCSV
    from .evaluate import load_run_config
    from .runlog import WandbSink, generate_wandb_id, get_wandb, wandb_tags
    from .runlog.wandb_sink import eval_payloads

    run_dir = Path(run_dir)
    meta_path = run_dir / "meta.json"
    if not meta_path.exists():
        raise FileNotFoundError(f"{run_dir} has no meta.json: not a run dir")
    meta = json.loads(meta_path.read_text())
    wb = module or get_wandb()
    if not meta.get("wandb_id"):
        meta["wandb_id"] = generate_wandb_id(wb)
        meta_path.write_text(json.dumps(meta, indent=2, default=str))
    cfg = load_run_config(run_dir)
    resolved = OmegaConf.to_container(cfg, resolve=True)
    settings = OmegaConf.to_container(cfg.logging)
    settings.update(mode=mode)
    if project:
        settings["project"] = project
    if entity:
        settings["entity"] = entity
    sink = WandbSink(
        run_dir,
        settings,
        meta["wandb_id"],
        meta.get("run_id", run_dir.name),
        meta.get("experiment", str(cfg.name)),
        resolved,
        wandb_tags(meta, resolved),
        job_type="train",
        wandb_dir=cfg.logging.dir or str(run_dir.parent / ".wandb"),
        module=wb,
    )
    sent = {"train": 0, "eval_points": 0, "final": 0, "files": 0}

    # interleave as a live run would: train row s, then the eval point at s
    train = sorted(_train_rows(run_dir), key=lambda r: int(r["step"]))
    evals = EvalsCSV(run_dir / "evals.csv").read()
    by_point: Dict[tuple, List[dict]] = {}
    for r in evals:
        by_point.setdefault((r["step"], r["stage"]), []).append(r)
    points = [k for k, _ in eval_payloads(evals)]
    events = [(int(r["step"]), 0, "train", r) for r in train]
    order = {"during": 1, "final": 2, "posthoc": 3}
    events += [(k[0], order.get(k[1], 9), "eval", by_point[k]) for k in points]
    events.sort(key=lambda e: (e[0], e[1]))

    for _, _, kind, payload in events:
        if kind == "train":
            before = sink.state.m["train_step"]
            sink.train(payload)
            sent["train"] += int(sink.state.m["train_step"] != before)
        else:
            before = len(sink.state.m["eval_points"])
            stage = payload[0]["stage"]
            if (
                stage == "posthoc"
                and [payload[0]["step"], "posthoc"] in sink.state.m["eval_points"]
            ):
                continue  # already mirrored; a backfill does not resend posthoc
            sink.eval(payload)
            sent["eval_points"] += int(len(sink.state.m["eval_points"]) != before)

    fm = run_dir / "final_metrics.json"
    if fm.exists() and not sink.state.m["final"]:
        sink.final(json.loads(fm.read_text()))
        sent["final"] = 1
    files = [
        run_dir / n
        for n in ("meta.json", "training_check.json", "final_metrics.json")
        if (run_dir / n).exists() and n not in sink.state.m["files"]
    ]
    if files:
        sink.files(files)
        sent["files"] = len(files)
    status = {}
    if (run_dir / "status.json").exists():
        status = json.loads((run_dir / "status.json").read_text())
    sink.finish(status.get("state", "done"), int(status.get("step", 0)))
    return sent


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("run_dirs", nargs="+")
    ap.add_argument("--mode", default="online", choices=["online", "offline"])
    ap.add_argument("--project", default=None)
    ap.add_argument("--entity", default=None)
    a = ap.parse_args(argv)
    rc = 0
    for d in a.run_dirs:
        try:
            sent = sync_run(d, a.mode, a.project, a.entity)
        except Exception as e:  # noqa: BLE001 - report each dir, keep going
            print(f"[wandb_sync] {d}: FAILED {type(e).__name__}: {e}", file=sys.stderr)
            rc = 1
            continue
        print(f"[wandb_sync] {d}: sent {sent}", flush=True)
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
