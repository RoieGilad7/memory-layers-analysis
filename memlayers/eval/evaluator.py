"""Running metrics: one evaluation point inside training, or one checkpoint post hoc.

`run_metrics` is the framework half of the metric contract: it checks each
metric's inputs and `needs_memory`, records why a metric is skipped instead of
calling it, times each one, and runs everything with the model in eval mode
under torch.no_grad. `Evaluator` adds the in-training part: the schedule, the
RNG/mode isolation, the evals.csv rows, the checkpoint at every point and the
final_metrics.json.
"""

from __future__ import annotations

import csv
import time
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

import torch

from .context import EvalContext, EvalResources, preserved_state
from .registry import get_metric, validate_metric_names
from .schedule import eval_schedule
from .writers import final_metrics_obj, rows_for

__all__ = ["run_metrics", "Evaluator", "validate_eval_config", "TIMING_FILE"]

TIMING_FILE = "eval_timing.csv"


def run_metrics(names: Sequence[str], ctx: EvalContext):
    """-> (results {name: {key: value}}, skipped {name: reason}, seconds {name: s})."""
    results: Dict[str, Dict[str, float]] = {}
    skipped: Dict[str, str] = {}
    seconds: Dict[str, float] = {}
    for name in names:
        spec = get_metric(name)
        reason = None
        if spec.needs_memory and not ctx.memory_layers:
            reason = "needs a memory layer; this model has none"
        for inp in spec.inputs:
            reason = reason or ctx.why_missing(inp)
        if reason:
            skipped[name] = reason
            continue
        ctx.metric = name
        t0 = time.perf_counter()
        ctx.model.eval()
        with torch.no_grad():
            out = spec.fn(ctx)
        seconds[name] = time.perf_counter() - t0
        results[name] = {str(k): float(v) for k, v in out.items()}
    ctx.metric = None
    return results, skipped, seconds


def validate_eval_config(ev) -> None:
    """Fail at startup on an unknown metric name or a bad schedule."""
    for stage in ("during", "final", "posthoc"):
        validate_metric_names(list(ev.get(stage) or []), stage)


def append_timing(
    run_dir: Path, step: int, stage: str, seconds: Dict[str, float]
) -> None:
    path = Path(run_dir) / TIMING_FILE
    new = not path.exists()
    with open(path, "a", newline="") as fh:
        w = csv.writer(fh)
        if new:
            w.writerow(["step", "stage", "metric", "seconds"])
        for k, v in seconds.items():
            w.writerow([step, stage, k, f"{v:.3f}"])


class Evaluator:
    def __init__(
        self,
        cfg,
        run_dir: Path,
        resources: Optional[EvalResources] = None,
        after_rows: Optional[Callable[[int], None]] = None,
        logger=None,
    ):
        self.cfg = cfg
        self.ev = cfg.eval
        self.run_dir = Path(run_dir)
        self.schedule: List[Tuple[int, str]] = eval_schedule(
            int(cfg.train.steps),
            list(self.ev.points) if self.ev.points is not None else None,
            list(self.ev.steps) if self.ev.get("steps") is not None else None,
        )
        self.points = dict(self.schedule)
        self.resources = resources or EvalResources.from_config(cfg.data, run_dir)
        if logger is None:
            from memlayers.runlog import FilesSink, RunLogger

            logger = RunLogger(FilesSink(self.run_dir, write_status_on_finish=False))
        self.logger = logger
        self.after_rows = after_rows

    def due(self, step: int) -> Optional[str]:
        """The stage evaluated at `step`, or None. A point whose stage has no
        metrics is not a point at all, so eval=off (empty during/final lists)
        means no eval points even where an experiment sets eval.points."""
        stage = self.points.get(int(step))
        if stage is None or not self.names(stage):
            return None
        return stage

    def names(self, stage: str) -> List[str]:
        return list(self.ev.get(stage) or [])

    def context(self, model, step, tokens_seen, stage, sample=None) -> EvalContext:
        from omegaconf import OmegaConf

        return EvalContext(
            model=model,
            config=OmegaConf.to_container(self.cfg, resolve=True),
            run_dir=self.run_dir,
            step=step,
            tokens_seen=tokens_seen,
            stage=stage,
            resources=self.resources,
            seed=int(self.ev.seed),
            sample=sample,
            heldout_batch=int(self.ev.heldout_batch),
            fact_batch_tokens=int(self.ev.fact_batch_tokens),
        )

    def at_point(self, trainer, stage: str) -> Dict[str, Any]:
        """Evaluate, write the rows, save the checkpoints. Training is untouched."""
        step, tokens = trainer.step, trainer.tokens_seen
        t0 = time.perf_counter()
        with preserved_state(trainer.model, trainer.device):
            ctx = self.context(trainer.model, step, tokens, stage)
            results, skipped, seconds = run_metrics(self.names(stage), ctx)
        rows = []
        for name, vals in results.items():
            rows += rows_for(
                step, tokens, stage, name, get_metric(name).metric_id, vals
            )
        self.logger.log_eval(rows)
        seconds = {**{"heldout_pass": p.seconds for p in ctx._pass.values()}, **seconds}
        seconds["total"] = time.perf_counter() - t0
        append_timing(self.run_dir, step, stage, seconds)
        if self.after_rows:
            self.after_rows(step)
        if stage == "final":
            self.logger.log_final(
                final_metrics_obj(
                    results,
                    {n: get_metric(n).metric_id for n in self.names(stage)},
                    skipped,
                    step,
                    tokens,
                )
            )
        from memlayers.devices import empty_cache

        # the eval batches' logits stay in the MPS/CUDA cache otherwise, and
        # the driver-allocated figure the train log reports jumps by ~10 GB
        empty_cache(trainer.device)
        trainer.save_weights(self.run_dir / "checkpoints" / f"step_{step:06d}.pt")
        trainer.save_checkpoint()
        msg = "  ".join(f"{n} {s:.1f}s" for n, s in seconds.items())
        skip = f"  skipped: {skipped}" if skipped else ""
        print(f"[eval] step {step} ({stage}): {msg}{skip}", flush=True)
        return {"results": results, "skipped": skipped, "seconds": seconds}
