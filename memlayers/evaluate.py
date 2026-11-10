"""Post-hoc evaluation of a saved checkpoint.

    python -m memlayers.evaluate run_dir=runs/pkm-s0 step=final
    python -m memlayers.evaluate run_dir=runs/pkm-s0 step=2000 metrics=[fact_recall]
    python -m memlayers.evaluate run_dir=runs/pkm-s0 step=all
    python -m memlayers.evaluate run_dir=runs/pkm-s0 step=init sample=true

`step`: `final` (the final eval checkpoint, else last.pt), `init` (step 0), an
integer, or `all` (every checkpoints/step_*.pt). Runs the run's `eval.posthoc`
list, or `metrics=[...]`, on the FULL sets (`sample=true` for the fixed
samples, which reproduces a `during` number exactly). Rows go to evals.csv
with stage `posthoc`, replacing earlier posthoc rows for the same step, metric
and key. final_metrics.json is left alone unless `update_final=true`, which
merges the new metrics in (other metrics stay; a re-run metric's old keys are
replaced) and refuses to mix two checkpoint steps.

Also reads a pre-run-layer dir (e.g. runs/learnability_t1_pkm/: ckpt.pt with
the Trainer's own config dict, no config.yaml).
"""

from __future__ import annotations

import re
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import torch
import yaml
from omegaconf import OmegaConf

__all__ = ["main", "evaluate_run", "load_run_config", "find_checkpoints"]


def _parse(argv: List[str]) -> Dict[str, str]:
    out = {}
    for a in argv:
        if "=" not in a:
            raise SystemExit(f"argument {a!r} must look like key=value; see --help")
        k, v = a.split("=", 1)
        out[k.strip()] = v.strip()
    known = {"run_dir", "step", "metrics", "update_final", "sample", "device"}
    bad = set(out) - known
    if bad:
        raise SystemExit(f"unknown argument(s) {sorted(bad)}; known: {sorted(known)}")
    if "run_dir" not in out:
        raise SystemExit("run_dir=... is required")
    return out


def _bool(v: Optional[str]) -> bool:
    return str(v).lower() in ("1", "true", "yes", "on")


def _list(v: Optional[str]) -> Optional[List[str]]:
    if v is None:
        return None
    v = v.strip()
    if v.startswith("[") and v.endswith("]"):
        v = v[1:-1]
    return [x.strip().strip("'\"") for x in v.split(",") if x.strip()]


def _upgrade_saved_config(raw: dict) -> dict:
    """A config.yaml saved before the data.root change (training prompt 5).

    Then, `data.root` re-rooted one 1% bundle (null otherwise); now it is the
    folder holding the bundles, and one bundle's own dir is `data.bundle`.
    """
    data = raw.get("data") or {}
    if "root" in data and "bundle" not in data:
        root = data.get("root")
        if root is None:
            data.pop("root")
        elif data.get("small"):
            # the old code only accepted root together with small=true
            data["bundle"] = data.pop("root")
    return raw


def load_run_config(run_dir: Path):
    """The run's resolved config as a RunConfig-checked DictConfig."""
    from .config import RunConfig

    schema = OmegaConf.structured(RunConfig)
    path = run_dir / "config.yaml"
    if path.exists():
        return OmegaConf.merge(
            schema, _upgrade_saved_config(yaml.safe_load(path.read_text()))
        )
    # a pre-run-layer dir: the Trainer's config_dict lives in the checkpoint
    for name in ("ckpt.pt", "init_weights.pt"):
        if (run_dir / name).exists():
            c = torch.load(run_dir / name, map_location="cpu", weights_only=False)[
                "config"
            ]
            break
    else:
        raise FileNotFoundError(f"{run_dir} has neither config.yaml nor ckpt.pt")
    model = dict(c["model"])
    mem = dict(model.get("memory") or {})
    model["memory"] = mem
    model["memory_layers"] = list(model.get("memory_layers") or [])
    legacy = {
        "name": c.get("name", run_dir.name),
        "run_id": run_dir.name,
        "out_root": str(run_dir.parent),
        "model": model,
        "data": c["data"],
        "train": {k: v for k, v in c["train"].items()},
        "runtime": {"device": "auto", "out_dir": str(run_dir)},
    }
    return OmegaConf.merge(schema, legacy)


def find_checkpoints(run_dir: Path, step: str) -> List[Tuple[int, Path]]:
    ck = run_dir / "checkpoints"
    eval_cks = (
        sorted(
            (int(m.group(1)), p)
            for p in ck.glob("step_*.pt")
            if (m := re.fullmatch(r"step_(\d+)\.pt", p.name))
        )
        if ck.exists()
        else []
    )
    if step == "all":
        if not eval_cks:
            raise FileNotFoundError(f"no checkpoints/step_*.pt in {run_dir}")
        return eval_cks
    if step == "init":
        for p in (ck / "step_000000.pt", run_dir / "init_weights.pt"):
            if p.exists():
                return [(0, p)]
        raise FileNotFoundError(f"no step-0 weights in {run_dir}")
    if step == "final":
        import json

        fm = run_dir / "final_metrics.json"
        if fm.exists():
            s = int(json.loads(fm.read_text())["step"])
            p = ck / f"step_{s:06d}.pt"
            if p.exists():
                return [(s, p)]
        for p in (ck / "last.pt", run_dir / "ckpt.pt"):
            if p.exists():
                s = int(torch.load(p, map_location="cpu", weights_only=False)["step"])
                return [(s, p)]
        raise FileNotFoundError(f"no final checkpoint in {run_dir}")
    n = int(step)
    p = ck / f"step_{n:06d}.pt"
    if not p.exists():
        have = [s for s, _ in eval_cks]
        raise FileNotFoundError(f"no checkpoint for step {n} in {run_dir}; have {have}")
    return [(n, p)]


def _model_for(cfg, path: Path, device):
    from .config import model_kwargs
    from .model import GPT, GPTConfig

    ck = torch.load(path, map_location="cpu", weights_only=False)
    model = GPT(GPTConfig(**model_kwargs(cfg.model)))
    model.load_state_dict(ck["model"])
    model.to(device).eval()
    tokens = int(ck.get("tokens_seen") or 0)
    if not tokens and ck.get("step"):
        tokens = (
            int(ck["step"])
            * int(cfg.train.micro_batch_size)
            * int(cfg.train.grad_accum_steps)
            * int(cfg.model.block_size)
        )
    return model, int(ck.get("step", 0)), tokens


def evaluate_run(
    run_dir,
    step: str = "final",
    metrics: Optional[List[str]] = None,
    update_final: bool = False,
    sample: bool = False,
    device: Optional[str] = None,
) -> List[Dict[str, Any]]:
    from .devices import pick_device
    from .eval import get_metric
    from .eval.context import EvalContext, EvalResources
    from .eval.evaluator import append_timing, run_metrics
    from .eval.registry import validate_metric_names
    from .eval.writers import final_metrics_obj, merge_final_metrics, rows_for

    run_dir = Path(run_dir)
    cfg = load_run_config(run_dir)
    names = metrics if metrics is not None else list(cfg.eval.posthoc)
    validate_metric_names(names, "posthoc")
    dev = pick_device(device or cfg.runtime.device)
    resources = EvalResources.from_config(cfg.data, run_dir)
    ckpts = find_checkpoints(run_dir, str(step))
    if update_final:
        # checked before any evaluation runs, not after an expensive one
        if len(ckpts) != 1:
            raise ValueError(
                f"update_final=true takes one checkpoint; step={step} names "
                f"{len(ckpts)}. Run update_final on step=final only."
            )
        fm = run_dir / "final_metrics.json"
        if fm.exists():
            import json as _json

            fstep = int(_json.loads(fm.read_text())["step"])
            ck = int(
                torch.load(ckpts[0][1], map_location="cpu", weights_only=False).get(
                    "step", ckpts[0][0]
                )
            )
            if ck != fstep:
                raise ValueError(
                    f"final_metrics.json is for step {fstep}, this checkpoint is step "
                    f"{ck}: update_final=true would mix two checkpoints"
                )
    logger = posthoc_logger(run_dir, cfg)
    out = []
    for s, path in ckpts:
        model, ck_step, tokens = _model_for(cfg, path, dev)
        t0 = time.perf_counter()
        ctx = EvalContext(
            model=model,
            config=OmegaConf.to_container(cfg, resolve=True),
            run_dir=run_dir,
            step=ck_step,
            tokens_seen=tokens,
            stage="posthoc",
            resources=resources,
            seed=int(cfg.eval.seed),
            sample=sample,
            heldout_batch=int(cfg.eval.heldout_batch),
            fact_batch_tokens=int(cfg.eval.fact_batch_tokens),
        )
        results, skipped, seconds = run_metrics(names, ctx)
        rows = []
        for name, vals in results.items():
            rows += rows_for(
                ck_step, tokens, "posthoc", name, get_metric(name).metric_id, vals
            )
        logger.log_eval(rows)  # replaces earlier posthoc rows for the same keys
        passes = list(ctx._pass.values())
        if passes:  # every held-out pass this point made, summed
            seconds = {"heldout_pass": sum(p.seconds for p in passes), **seconds}
        seconds["total"] = time.perf_counter() - t0
        append_timing(run_dir, ck_step, "posthoc", seconds)
        if update_final:
            # merged, not replaced: the built-in metrics (and any metric not
            # re-run here) stay in final_metrics.json, so compare keeps them
            import json as _json

            fm_path = run_dir / "final_metrics.json"
            old = _json.loads(fm_path.read_text()) if fm_path.exists() else None
            logger.log_final(
                merge_final_metrics(
                    old,
                    final_metrics_obj(
                        results,
                        {n: get_metric(n).metric_id for n in names},
                        skipped,
                        ck_step,
                        tokens,
                    ),
                )
            )
        print(
            f"[evaluate] {run_dir.name} step {ck_step} ({path.name}, "
            f"{'sample' if sample else 'full'} sets): "
            + "  ".join(f"{n} {v:.1f}s" for n, v in seconds.items())
            + (f"  skipped: {skipped}" if skipped else ""),
            flush=True,
        )
        out.append(
            {
                "step": ck_step,
                "results": results,
                "skipped": skipped,
                "seconds": seconds,
            }
        )
        del model
    if update_final:
        logger.log_files([run_dir / "final_metrics.json"])
    logger.finish("posthoc", out[-1]["step"] if out else 0)
    return out


def posthoc_logger(run_dir: Path, cfg):
    """Files always (no status.json write: a posthoc pass is not the run); the
    run's W&B mirror too, as job_type `eval`, if it had one."""
    import json

    from .runlog import FilesSink, RunLogger, WandbSink, wandb_tags

    files = FilesSink(run_dir, write_status_on_finish=False)
    lg = cfg.logging
    meta_path = run_dir / "meta.json"
    meta = json.loads(meta_path.read_text()) if meta_path.exists() else {}
    if lg.sink != "wandb" or lg.mode == "disabled" or not meta.get("wandb_id"):
        return RunLogger(files)
    resolved = OmegaConf.to_container(cfg, resolve=True)
    sink = WandbSink(
        run_dir,
        OmegaConf.to_container(lg),
        meta["wandb_id"],
        str(cfg.run_id),
        str(cfg.name),
        resolved,
        wandb_tags(meta, resolved),
        job_type="eval",
        wandb_dir=lg.dir or str(Path(cfg.out_root) / ".wandb"),
    )
    return RunLogger(files, [sink])


def main(argv: Optional[List[str]] = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if any(a in ("-h", "--help") for a in argv):
        print(__doc__)
        return 0
    a = _parse(argv)
    evaluate_run(
        a["run_dir"],
        step=a.get("step", "final"),
        metrics=_list(a.get("metrics")),
        update_final=_bool(a.get("update_final")),
        sample=_bool(a.get("sample")),
        device=a.get("device"),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
