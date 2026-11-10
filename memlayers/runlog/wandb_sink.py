"""WandbSink: an optional mirror of the run-dir files in Weights & Biases.

What goes to W&B:
    train rows     train/<column> for the numeric train_log.csv columns, with
                   `tokens_seen` (the x-axis of every chart) and `step`
    eval rows      <metric>/<key> for stage `during`; <stage>/<metric>/<key>
                   for `final` and `posthoc` (final/fact_recall/top1/frequent/test)
    config         the resolved run config
    summary        final_metrics.json's metrics, as <metric>/<key>
    files          meta.json, training_check.json, final_metrics.json
Never checkpoints, never read logs.

The W&B run id is generated once, when the run first starts, and kept in
meta.json as `wandb_id`; every resume and every `memlayers.wandb_sync` reuses it
with resume="allow". What has been sent, per mode, is tracked in the run dir's
`wandb_sync.json`, so a backfill sends only what is missing and a second sync
sends nothing.

`wandb` is imported lazily (`get_wandb`); tests inject a fake module through
`WANDB_MODULE`. The sink never makes a call in mode `disabled` -- the run layer
does not even build one.
"""

from __future__ import annotations

import json
import math
import os
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

__all__ = [
    "WandbSink",
    "get_wandb",
    "generate_wandb_id",
    "wandb_tags",
    "WANDB_MODULE",
    "SYNC_FILE",
]

WANDB_MODULE = None  # tests set this to a fake module
SYNC_FILE = "wandb_sync.json"
TRAIN_KEYS = [
    "loss",
    "lr",
    "lr_memory",
    "step_time_s",
    "tokens_per_s",
    "peak_mem_bytes",
    "grad_norm",
]
RUN_FILES = ("meta.json", "training_check.json", "final_metrics.json")


def get_wandb():
    """The wandb module (or the injected fake). ImportError if neither."""
    if WANDB_MODULE is not None:
        return WANDB_MODULE
    import wandb  # noqa: WPS433 - lazy on purpose

    return wandb


def generate_wandb_id(wb) -> str:
    """`wandb.util.generate_id()`, where the installed wandb has it. wandb 0.31
    moved it to `wandb.sdk.lib.runid.generate_id`; same 8-char id."""
    util = getattr(wb, "util", None)
    if util is not None and hasattr(util, "generate_id"):
        return util.generate_id()
    from wandb.sdk.lib.runid import generate_id

    return generate_id()


def wandb_tags(meta: Dict[str, Any], config: Dict[str, Any]) -> List[str]:
    """data version, short git commit, device, precision."""
    data = meta.get("data") or {}
    commit = ((meta.get("git") or {}).get("commit") or "nogit")[:8]
    runtime = config.get("runtime") or {}
    return [
        f"data:{data.get('version') or data.get('source') or 'unknown'}",
        f"git:{commit}",
        f"device:{meta.get('device', runtime.get('device', 'unknown'))}",
        # meta.json has the resolved precision; runs made before it was
        # recorded were all fp32
        f"precision:{meta.get('precision') or 'fp32'}",
    ]


def _num(v) -> Optional[float]:
    try:
        f = float(v)
    except (TypeError, ValueError):
        return None
    return f if math.isfinite(f) else f  # NaN/inf are sent as such


def eval_payloads(rows: List[Dict[str, Any]]) -> List[tuple]:
    """[((step, stage), {key: value, tokens_seen, step})] in step order."""
    groups: Dict[tuple, Dict[str, Any]] = {}
    for r in rows:
        k = (int(r["step"]), r["stage"])
        prefix = "" if r["stage"] == "during" else f"{r['stage']}/"
        g = groups.setdefault(
            k, {"tokens_seen": int(r["tokens_seen"]), "step": int(r["step"])}
        )
        g[f"{prefix}{r['metric']}/{r['key']}"] = float(r["value"])
    order = {"during": 0, "final": 1, "posthoc": 2}
    return sorted(groups.items(), key=lambda kv: (kv[0][0], order.get(kv[0][1], 9)))


def _train_rows(run_dir) -> List[Dict[str, Any]]:
    import csv

    for name in ("train_log.csv", "log.csv"):
        p = Path(run_dir) / name
        if p.exists():
            with open(p, newline="") as fh:
                return list(csv.DictReader(fh))
    return []


def train_payload(row: Dict[str, Any]) -> Dict[str, Any]:
    out = {"tokens_seen": int(row["tokens_seen"]), "step": int(row["step"])}
    for k in TRAIN_KEYS:
        v = _num(row.get(k))
        if v is not None:
            out[f"train/{k}"] = v
    return out


class SyncState:
    """What has reached W&B, per mode: train steps, eval points, summary, files."""

    def __init__(self, run_dir: Path, mode: str):
        self.path = Path(run_dir) / SYNC_FILE
        self.mode = mode
        self.data = json.loads(self.path.read_text()) if self.path.exists() else {}
        m = self.data.setdefault(mode, {})
        m.setdefault("train_step", 0)
        m.setdefault("eval_points", [])
        m.setdefault("final", False)
        m.setdefault("files", [])
        # True once run.finish() returned: everything logged in that session
        # reached W&B. A run that died (kill -9, a closed lid, a Colab
        # disconnect) leaves it False, and what it "sent" may never have been
        # uploaded -- recover() then asks the server instead of trusting this.
        m.setdefault("clean", True)

    @property
    def m(self) -> Dict[str, Any]:
        return self.data[self.mode]

    def save(self) -> None:
        tmp = self.path.with_name(f".{self.path.name}.tmp-{os.getpid()}")
        tmp.write_text(json.dumps(self.data, indent=1, sort_keys=True) + "\n")
        os.replace(tmp, self.path)

    def reset_after(self, step: int) -> None:
        """A resume replays steps past its checkpoint; they may be sent again."""
        self.m["train_step"] = min(self.m["train_step"], int(step))
        self.m["eval_points"] = [
            p for p in self.m["eval_points"] if p[0] <= step or p[1] == "posthoc"
        ]
        self.save()


class WandbSink:
    name = "wandb"

    def __init__(
        self,
        run_dir,
        settings: Dict[str, Any],
        wandb_id: str,
        run_id: str,
        group: str,
        config: Dict[str, Any],
        tags: List[str],
        job_type: str = "train",
        wandb_dir: Optional[str] = None,
        module=None,
    ):
        self.run_dir = Path(run_dir)
        self.settings = dict(settings)
        self.mode = self.settings.get("mode", "online")
        self.wandb_id, self.run_id, self.group = wandb_id, run_id, group
        self.config, self.tags, self.job_type = config, tags, job_type
        self.wandb_dir = wandb_dir
        self._module = module
        self.run = None
        self.state = SyncState(self.run_dir, self.mode)
        # steps / eval points the server already holds past a resume point
        self._server_train: set = set()
        self._server_points: set = set()

    # ---- the W&B run -------------------------------------------------------
    def _wb(self):
        return self._module or get_wandb()

    def start(self):
        if self.run is not None:
            return self.run
        wb = self._wb()
        if self.wandb_dir:
            Path(self.wandb_dir).mkdir(parents=True, exist_ok=True)
        self.run = wb.init(
            project=self.settings.get("project") or "memlayers",
            entity=self.settings.get("entity"),
            mode=self.mode,
            group=self.group,
            name=self.run_id,
            job_type=self.job_type,
            tags=self.tags,
            id=self.wandb_id,
            resume="allow",
            config=self.config,
            dir=self.wandb_dir,
        )
        self.state.m["clean"] = False
        self.state.save()
        self.run.define_metric("tokens_seen")
        self.run.define_metric("step")
        self.run.define_metric("*", step_metric="tokens_seen")
        return self.run

    # ---- events ------------------------------------------------------------
    def train(self, row: Dict[str, Any]) -> None:
        step = int(row["step"])
        if step <= self.state.m["train_step"] or step in self._server_train:
            return
        self.start().log(train_payload(row))
        self.state.m["train_step"] = step
        self.state.save()

    def eval(self, rows: List[Dict[str, Any]]) -> None:
        done = {tuple(p) for p in self.state.m["eval_points"]}
        sent = False
        for key, payload in eval_payloads(rows):
            if key[1] != "posthoc" and (key in done or key in self._server_points):
                continue
            self.start().log(payload)
            if key not in done:
                self.state.m["eval_points"].append(list(key))
            sent = True
        if sent:
            self.state.save()

    def final(self, final_metrics: Dict[str, Any]) -> None:
        run = self.start()
        summary = dict(final_metrics.get("metrics") or {})
        summary["final_step"] = final_metrics.get("step")
        summary["final_tokens_seen"] = final_metrics.get("tokens_seen")
        run.summary.update(summary)
        self.state.m["final"] = True
        self.state.save()

    def files(self, paths: Iterable) -> None:
        run = self.start()
        for p in paths:
            p = Path(p)
            if p.name not in RUN_FILES or not p.exists():
                continue  # never checkpoints or read logs
            run.save(str(p), base_path=str(p.parent), policy="now")
            if p.name not in self.state.m["files"]:
                self.state.m["files"].append(p.name)
        self.state.save()

    def finish(self, state: str, step: int, error: Optional[str] = None) -> None:
        if self.run is None:
            return
        self.run.summary.update({"run_state": state, "run_step": int(step)})
        self.run.finish(exit_code=0 if state == "done" else 1)
        self.run = None
        self.state.m["clean"] = True  # finish() returned: all of it is uploaded
        self.state.save()

    # ---- after an unclean exit ------------------------------------------------
    def server_history(self):
        """(train steps, {(step, stage)} eval points) the W&B server holds for
        this run; empty sets if it has never seen the run."""
        wb = self._wb()
        api = wb.Api(timeout=60)
        entity = self.settings.get("entity") or api.default_entity
        project = self.settings.get("project") or "memlayers"
        try:
            run = api.run(f"{entity}/{project}/{self.wandb_id}")
            hist = list(run.scan_history())
        except Exception:  # noqa: BLE001 - not found: nothing was uploaded
            return set(), set()
        steps, points = set(), set()
        for h in hist:
            if h.get("step") is None:
                continue
            s = int(h["step"])
            if h.get("train/loss") is not None:
                steps.add(s)
            keys = [k for k in h if "/" in k and not k.startswith(("train/", "_"))]
            if keys:
                stage = (
                    "final"
                    if any(k.startswith("final/") for k in keys)
                    else (
                        "posthoc"
                        if any(k.startswith("posthoc/") for k in keys)
                        else "during"
                    )
                )
                points.add((s, stage))
        return steps, points

    def recover(self, upto: Optional[int] = None) -> Dict[str, int]:
        """Bring W&B in line with the run-dir files before carrying on.

        `upto`: the step a resume restarts from (None: everything, for
        wandb_sync). After a clean finish (or in offline mode) the local record
        is trusted and only the steps past `upto` are reopened. After an
        unclean exit in online mode the server is asked what it really has:
        rows up to `upto` it lacks are re-sent from train_log.csv / evals.csv,
        and rows past `upto` it already has are not sent again when the resumed
        run replays those steps.
        """
        sent = {"train": 0, "eval_points": 0}
        if self.state.m.get("clean", True) or self.mode != "online":
            if upto is not None:
                self.state.reset_after(upto)
            return sent
        from memlayers.eval.writers import EvalsCSV

        steps, points = self.server_history()
        lim = float("inf") if upto is None else int(upto)
        for row in sorted(_train_rows(self.run_dir), key=lambda r: int(r["step"])):
            s = int(row["step"])
            if s <= lim and s not in steps:
                self.start().log(train_payload(row))
                sent["train"] += 1
        live = [
            r
            for r in EvalsCSV(self.run_dir / "evals.csv").read()
            if r["stage"] != "posthoc"
        ]
        for key, payload in eval_payloads(live):
            if key[0] <= lim and key not in points:
                self.start().log(payload)
                points.add(key)
                sent["eval_points"] += 1
        self._server_train = {s for s in steps if s > lim}
        self._server_points = {p for p in points if p[0] > lim}
        trains = [int(r["step"]) for r in _train_rows(self.run_dir)]
        self.state.m["train_step"] = (
            int(lim) if upto is not None else max(trains, default=0)
        )
        self.state.m["eval_points"] = sorted([list(p) for p in points if p[0] <= lim])
        self.state.m["final"] = False  # the summary and files are re-sent: idempotent
        self.state.m["files"] = []
        if self.run is None and not any(sent.values()):
            self.state.m["clean"] = True
        self.state.save()
        if any(sent.values()):
            print(
                f"[runlog] W&B recovered after an unclean exit: re-sent {sent}",
                flush=True,
            )
        return sent
