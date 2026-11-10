"""One entry point: an experiment + a seed -> a run directory.

    python -m memlayers.run experiment=pkm seed=0
    python -m memlayers.run experiment=pkm seed=0 train.steps=200 tag=pilot
    python -m memlayers.run -m experiment=pkm seed=0,1,2

The run id is `<experiment>-s<seed>[-<tag>]` and the run dir is
`<out_root>/<run_id>/`. Re-running the same command is safe:

    no run dir                 -> a fresh run
    status done                -> refused; force=true moves the dir to
                                  <run_dir>.old-<n> first (nothing is deleted)
    status failed, or running
    with a dead PID            -> resumed from checkpoints/last.pt (resume=true),
                                  if the config matches the saved one outside
                                  train.steps / runtime.* / logging.* / eval.*
    status running, this host,
    PID alive                  -> refused: already running
    status running, other host -> refused unless resume_foreign=true

Every check happens BEFORE anything is written, so a refused launch leaves the
run dir byte-for-byte as it was. Hydra writes nothing into the run dir
(hydra.output_subdir is null and its own dir is <out_root>/.hydra_tmp); this
module writes config.yaml and overrides.yaml itself, after the checks.

Run dir:
    config.yaml        the fully resolved config
    overrides.yaml     the command-line overrides
    meta.json          Trainer.meta_dict() + git, FLOPs, host, versions, run id
    status.json        {state, step, updated_at, error, host, pid}
    stdout.log         everything printed (appended across resumes)
    train_log.csv      the per-step training log
    checkpoints/step_000000.pt   init weights
    checkpoints/last.pt          resumable, written atomically
    slot_usage.{json,npz}        memory runs only
"""

from __future__ import annotations

import contextlib
import csv
import datetime as _dt
import json
import os
import platform
import socket
import subprocess
import sys
import time
import traceback
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional

import yaml
from omegaconf import DictConfig, OmegaConf

from .config import load_model_group, model_kwargs, to_train_config
from .flops import dense_ffn_flops, estimate_flops_per_token

__all__ = [
    "RunRefused",
    "Decision",
    "run_dir_for",
    "read_status",
    "write_status",
    "decide",
    "config_diff",
    "RESUME_ALLOWED",
    "launch",
    "main",
]

ROOT = Path(__file__).resolve().parent.parent
STATUS = "status.json"
LAST = Path("checkpoints") / "last.pt"

# keys a resume may change. The launch flags and out_root say how and where to
# run, not what is run.
RESUME_ALLOWED = (
    "train.steps",
    "runtime.",
    "logging.",
    "eval.",
    "force",
    "resume",
    "resume_foreign",
    "out_root",
)

# test hook: MEMLAYERS_TEST_HALT=<step>:exit|hang stops the process right after
# the checkpoint at <step> -- `exit` like a SIGKILL (no cleanup, status stays
# `running`), `hang` keeps it alive so the run lock can be tested
_HALT_ENV = "MEMLAYERS_TEST_HALT"


class RunRefused(RuntimeError):
    """The run dir's state does not allow this launch. Nothing was written."""


@dataclass
class Decision:
    action: str  # "fresh" | "resume"
    reason: str
    move_to: Optional[Path] = None  # force=true: the old dir goes here first


# ----------------------------------------------------------------- small helpers
def _now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds")


def run_dir_for(cfg: DictConfig) -> Path:
    return Path(cfg.out_root) / str(cfg.run_id)


def read_status(run_dir: Path) -> Optional[dict]:
    p = Path(run_dir) / STATUS
    if not p.exists():
        return None
    return json.loads(p.read_text())


def _atomic_write_text(path: Path, text: str) -> None:
    tmp = path.with_name(f".{path.name}.tmp-{os.getpid()}")
    tmp.write_text(text)
    os.replace(tmp, path)


from .runlog.files import (
    write_status,
)  # noqa: E402  (status.json lives with the logger)


def pid_alive(pid: int) -> bool:
    try:
        os.kill(int(pid), 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True  # exists, owned by someone else
    return True


def next_old_path(run_dir: Path) -> Path:
    n = 1
    while True:
        p = run_dir.with_name(f"{run_dir.name}.old-{n}")
        if not p.exists():
            return p
        n += 1


def _flatten(d: Any, prefix: str = "") -> Dict[str, Any]:
    if isinstance(d, dict):
        out: Dict[str, Any] = {}
        if not d and prefix:
            out[prefix] = {}
        for k, v in d.items():
            out.update(_flatten(v, f"{prefix}.{k}" if prefix else str(k)))
        return out
    return {prefix: d}


def config_diff(saved: dict, new: dict) -> Dict[str, tuple]:
    """Keys whose values differ and are NOT on the resume allow-list."""
    a, b = _flatten(saved), _flatten(new)
    bad = {}
    for k in sorted(set(a) | set(b)):
        if a.get(k, "<absent>") == b.get(k, "<absent>"):
            continue
        if any(k == p or (p.endswith(".") and k.startswith(p)) for p in RESUME_ALLOWED):
            continue
        bad[k] = (a.get(k, "<absent>"), b.get(k, "<absent>"))
    return bad


def _resolved(cfg: DictConfig) -> dict:
    return OmegaConf.to_container(cfg, resolve=True, throw_on_missing=True)


# --------------------------------------------------------------------- decision
def decide(run_dir: Path, cfg: DictConfig) -> Decision:
    """What this launch does with `run_dir`. Reads only; raises RunRefused."""
    run_dir = Path(run_dir)
    if not run_dir.exists() or not any(run_dir.iterdir()):
        return Decision("fresh", "new run")

    st = read_status(run_dir)
    force, resume = bool(cfg.force), bool(cfg.resume)
    if st is None:
        if force:
            return Decision("fresh", "force=true", next_old_path(run_dir))
        raise RunRefused(
            f"{run_dir} exists but has no {STATUS}, so it is not a run dir this "
            "tool wrote. Move it away, or pass force=true to have it moved to "
            f"{next_old_path(run_dir).name}."
        )

    state = st.get("state")
    host = socket.gethostname()
    if state == "running":
        same_host = st.get("host") == host
        if same_host and st.get("pid") != os.getpid() and pid_alive(st["pid"]):
            raise RunRefused(
                f"{run_dir.name} is already running (pid {st['pid']} on {host}, "
                f"step {st.get('step')}, updated {st.get('updated_at')}). Two "
                "processes never write the same run dir. If that PID is not a "
                "training process (PID reuse after a reboot), edit "
                f"{run_dir / STATUS} by hand."
            )
        if not same_host and not cfg.resume_foreign:
            raise RunRefused(
                f"{run_dir.name} says it is running on host {st.get('host')!r} "
                f"(pid {st.get('pid')}), not on {host!r}. If that process is "
                "gone (a synced drive), pass resume_foreign=true."
            )
        state = "interrupted"  # a running status whose process is gone

    if state == "done":
        if force:
            return Decision("fresh", "force=true", next_old_path(run_dir))
        raise RunRefused(
            f"{run_dir.name} is done (step {st.get('step')}, "
            f"{st.get('updated_at')}). Nothing was changed. To train it again "
            f"from scratch pass force=true: the finished run is moved to "
            f"{next_old_path(run_dir).name}, not deleted."
        )

    if state in ("failed", "interrupted"):
        if force:
            return Decision("fresh", "force=true", next_old_path(run_dir))
        if not resume:
            raise RunRefused(
                f"{run_dir.name} is {state} at step {st.get('step')} and "
                "resume=false. Pass resume=true to continue it, or force=true "
                "to start over (the old dir is moved, not deleted)."
            )
        saved_path = run_dir / "config.yaml"
        if saved_path.exists():
            saved = yaml.safe_load(saved_path.read_text()) or {}
            bad = config_diff(saved, _resolved(cfg))
            if bad:
                lines = "\n".join(f"  {k}: {a!r} -> {b!r}" for k, a, b in _rows(bad))
                raise RunRefused(
                    f"{run_dir.name} cannot be resumed with a different config. "
                    f"Only {', '.join(RESUME_ALLOWED)} may change on a resume; "
                    f"these differ:\n{lines}\nUse a tag= for a new run id, or "
                    "force=true to start over."
                )
        return Decision("resume", f"{state} at step {st.get('step')}")

    raise RunRefused(f"{run_dir / STATUS} has an unknown state {state!r}")


def _rows(bad: Dict[str, tuple]):
    for k, (a, b) in bad.items():
        yield k, a, b


# ----------------------------------------------------------------- provenance
def git_info(root: Path = ROOT) -> Dict[str, Any]:
    def git(*args) -> Optional[str]:
        try:
            r = subprocess.run(
                ["git", "-C", str(root), *args],
                capture_output=True,
                text=True,
                timeout=20,
            )
        except (OSError, subprocess.SubprocessError):
            return None
        return r.stdout if r.returncode == 0 else None

    commit = git("rev-parse", "HEAD")
    porcelain = git("status", "--porcelain", "--untracked-files=all") or ""
    files = [ln[3:] for ln in porcelain.splitlines() if ln.strip()]
    return {
        "commit": commit.strip() if commit else None,
        "branch": (git("rev-parse", "--abbrev-ref", "HEAD") or "").strip() or None,
        "dirty": bool(files),
        "dirty_files": files,
    }


def versions() -> Dict[str, str]:
    import hydra
    import omegaconf
    import torch

    return {
        "python": platform.python_version(),
        "torch": torch.__version__,
        "hydra": hydra.__version__,
        "omegaconf": omegaconf.__version__,
    }


def compute_match(model_cfg: DictConfig) -> Optional[Dict[str, Any]]:
    """For a dense model FLOP-matched to a memory model: both layers' FLOPs."""
    ref_name = model_cfg.get("compute_match")
    if not ref_name:
        return None
    ref = estimate_flops_per_token(model_kwargs(load_model_group(ref_name)))
    this = estimate_flops_per_token(model_kwargs(model_cfg))
    d = int(model_cfg.n_embd)
    layers = []
    for r in ref["per_layer"]:
        if r["kind"] == "dense":
            continue
        t = this["per_layer"][r["layer"]]
        ratio = t["ffn"] / r["ffn"]
        layers.append(
            {
                "layer": r["layer"],
                "reference_kind": r["kind"],
                "reference_ffn_flops": r["ffn"],
                "ffn_flops": t["ffn"],
                "ffn_hidden": t.get("ffn_hidden"),
                "standard_4x_ffn_flops": dense_ffn_flops(d, 4 * d),
                "ratio": round(ratio, 4),
                "within_10pct": abs(ratio - 1) <= 0.10,
            }
        )
    return {
        "reference_model": ref_name,
        "reference_total": ref["total"],
        "total": this["total"],
        "layers": layers,
    }


# --------------------------------------------------------------------- stdout
class _Tee:
    def __init__(self, stream, fh):
        self.stream, self.fh = stream, fh

    def write(self, s):
        self.stream.write(s)
        self.fh.write(s)
        self.fh.flush()
        return len(s)

    def flush(self):
        self.stream.flush()
        self.fh.flush()

    def __getattr__(self, name):
        return getattr(self.stream, name)


@contextlib.contextmanager
def _tee_output(path: Path) -> Iterator[None]:
    fh = open(path, "a", buffering=1)
    old_out, old_err = sys.stdout, sys.stderr
    sys.stdout, sys.stderr = _Tee(old_out, fh), _Tee(old_err, fh)
    try:
        yield
    finally:
        sys.stdout, sys.stderr = old_out, old_err
        fh.close()


@contextlib.contextmanager
def _run_lock(out_root: Path, run_id: str) -> Iterator[None]:
    """An flock held for the whole launch, outside the run dir, so two launches
    on one host cannot race between reading status.json and writing it. The
    kernel drops it when the process dies, however it dies."""
    try:
        import fcntl
    except ImportError:  # pragma: no cover - not POSIX: status.json alone
        yield
        return
    lock_dir = Path(out_root) / ".locks"
    lock_dir.mkdir(parents=True, exist_ok=True)
    fh = open(lock_dir / f"{run_id}.lock", "a+")
    try:
        try:
            fcntl.flock(fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise RunRefused(
                f"{run_id} is already running: another process on this host "
                f"holds {lock_dir / (run_id + '.lock')}."
            ) from None
        yield
    finally:
        fh.close()


def _trim_train_log(path: Path, step: int) -> None:
    """Drop log rows past the checkpoint a resume restarts from, so a crash
    between two checkpoints does not leave the replayed steps in twice."""
    if not path.exists():
        return
    with open(path, newline="") as fh:
        rows = list(csv.reader(fh))
    if not rows:
        return
    head, body = rows[0], rows[1:]
    keep = [r for r in body if r and int(r[0]) <= step]
    if len(keep) != len(body):
        with open(path, "w", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(head)
            w.writerows(keep)


def _halt_hook(step: int, where: str = "ckpt") -> None:
    """MEMLAYERS_TEST_HALT=<step>:<exit|hang>[:<ckpt|eval_rows>]. `eval_rows`
    halts right after an eval point's rows are written, before its checkpoint."""
    spec = os.environ.get(_HALT_ENV)
    if not spec:
        return
    parts = spec.split(":")
    at, mode = parts[0], parts[1] if len(parts) > 1 else "exit"
    at_where = parts[2] if len(parts) > 2 else "ckpt"
    if int(at) != step or at_where != where:
        return
    print(f"[run] {_HALT_ENV}: halting at step {step} ({mode}, {where})", flush=True)
    if mode == "hang":
        while True:
            time.sleep(60)
    os._exit(137)


# ---------------------------------------------------------------------- launch
def launch(cfg: DictConfig, overrides: Optional[List[str]] = None) -> Path:
    """Run (or resume) `cfg` in its run dir. Returns the run dir.

    Raises RunRefused, having written nothing, when the run dir's state does
    not allow it.
    """
    from .devices import empty_cache

    overrides = list(overrides or [])
    run_dir = run_dir_for(cfg)
    resolved = _resolved(cfg)
    tc = to_train_config(cfg)  # fails here, before any write, on a bad config
    from .eval.evaluator import validate_eval_config
    from .eval.schedule import eval_schedule

    validate_eval_config(cfg.eval)
    eval_schedule(
        int(cfg.train.steps),
        list(cfg.eval.points) if cfg.eval.points is not None else None,
        list(cfg.eval.steps) if cfg.eval.get("steps") is not None else None,
    )
    eval_set_hashes = check_eval_sets(cfg)
    if Path(tc.runtime.out_dir).resolve() != run_dir.resolve():
        raise RunRefused(
            f"runtime.out_dir {tc.runtime.out_dir} is not the run dir {run_dir}; "
            "the run layer owns where a run is written"
        )

    with _run_lock(Path(cfg.out_root), str(cfg.run_id)):
        decision = decide(run_dir, cfg)

        # ---- nothing has been written above this line ----
        if decision.move_to is not None:
            os.rename(run_dir, decision.move_to)
            moved = decision.move_to
        else:
            moved = None
        run_dir.mkdir(parents=True, exist_ok=True)

        with _tee_output(run_dir / "stdout.log"):
            print(
                f"[run] {cfg.run_id}: {decision.action} ({decision.reason}) "
                f"-> {run_dir}",
                flush=True,
            )
            if moved is not None:
                print(f"[run] previous run moved to {moved}", flush=True)
            prev = read_status(run_dir) if decision.action == "resume" else None
            write_status(run_dir, "running", (prev or {}).get("step", 0))
            (run_dir / "config.yaml").write_text(
                yaml.safe_dump(resolved, sort_keys=False)
            )
            (run_dir / "overrides.yaml").write_text(
                yaml.safe_dump(overrides, sort_keys=False)
            )
            hold: Dict[str, Any] = {}
            try:
                trainer = _train(
                    cfg, tc, run_dir, decision, overrides, moved, eval_set_hashes, hold
                )
            except BaseException as e:
                tr = hold.get("trainer")
                step = tr.step if tr is not None else 0
                tb = "".join(traceback.format_exception(type(e), e, e.__traceback__))
                last = read_status(run_dir) or {}
                step = max(step, last.get("step", 0))
                if tr is not None:
                    tr.logger.finish("failed", step, tb)
                else:
                    write_status(run_dir, "failed", step, tb)
                print(f"[run] {cfg.run_id} FAILED: {e!r}", flush=True)
                raise
            trainer.logger.finish("done", trainer.step)
            print(f"[run] {cfg.run_id} done at step {trainer.step}", flush=True)
            empty_cache(trainer.device)
    return run_dir


def check_eval_sets(cfg) -> Optional[Dict[str, str]]:
    """The fixed eval sets' sha256s, or RunRefused if they do not match the
    committed manifest. Fake-data runs have none (None)."""
    if cfg.data.source != "real":
        return None
    from .eval.eval_sets import EvalSetMismatch, verify
    from .train import load_bundle_config

    try:
        return verify(load_bundle_config(cfg.data))
    except EvalSetMismatch as e:
        raise RunRefused(f"eval sets: {e}") from None


def _train(
    cfg,
    tc,
    run_dir: Path,
    decision: Decision,
    overrides,
    moved,
    eval_set_hashes=None,
    hold=None,
):
    from .eval.evaluator import Evaluator
    from .train import RunLayout, Trainer

    trainer = Trainer(tc, layout=RunLayout.run())
    if hold is not None:
        hold["trainer"] = trainer
    host = socket.gethostname()
    flops = estimate_flops_per_token(tc.model)
    trainer.extra_meta = {
        "run_id": str(cfg.run_id),
        "experiment": str(cfg.name),
        "seed": int(cfg.seed),
        "tag": str(cfg.tag),
        "overrides": overrides,
        "host": host,
        "pid": os.getpid(),
        "launched_at": _now(),
        "git": git_info(),
        "versions": versions(),
        "flops_per_token": flops,
        "compute_match": compute_match(cfg.model),
        "moved_previous_to": str(moved) if moved else None,
        "eval_sets": eval_set_hashes,
    }
    _attach_logger(cfg, run_dir, trainer, decision)
    print(
        f"[run] device={trainer.device}  params={trainer.model.param_counts()['total']:,}"
        f"  flops/token={flops['total']:,}",
        flush=True,
    )

    ckpt = run_dir / LAST
    if decision.action == "resume" and ckpt.exists():
        trainer.load_checkpoint(ckpt)
        _trim_train_log(trainer.csv_path, trainer.step)
        from .eval.writers import EvalsCSV

        dropped = EvalsCSV(run_dir / "evals.csv").drop_after(trainer.step)
        if dropped:
            print(
                f"[run] dropped {dropped} eval rows past step {trainer.step}",
                flush=True,
            )
        print(f"[run] resumed from {ckpt} at step {trainer.step}", flush=True)
        meta_path = run_dir / "meta.json"
        meta = json.loads(meta_path.read_text()) if meta_path.exists() else {}
        here = {
            "device": str(trainer.device),
            "precision": trainer.prec["precision"],
            "gpu_name": trainer.device_info["gpu_name"],
        }
        meta.setdefault("resumes", []).append(
            {
                "at_step": trainer.step,
                "at": _now(),
                "host": host,
                "pid": os.getpid(),
                "git": trainer.extra_meta["git"],
                "overrides": overrides,
                **here,
            }
        )
        before = {
            "device": meta.get("device"),
            "precision": meta.get("precision"),
            "gpu_name": meta.get("gpu_name"),
        }
        last = meta.get("device_changes", [])
        prev = last[-1]["to"] if last else before
        if any(prev.get(k) != here[k] for k in here):
            # allowed (a Colab reconnect may land on another GPU type) but
            # recorded, and memlayers.compare flags the run
            meta.setdefault("device_changes", []).append(
                {"at_step": trainer.step, "from": prev, "to": here}
            )
            print(f"[run] device change on resume: {prev} -> {here}", flush=True)
        meta_path.write_text(json.dumps(meta, indent=2, default=str))
    elif decision.action == "resume":
        # interrupted before the first checkpoint: same config, same seed, so
        # starting from step 0 IS the same run
        print("[run] no checkpoint yet; restarting from step 0", flush=True)
        if trainer.csv_path.exists():
            trainer.csv_path.unlink()
            trainer._csv_started = False
        for name in ("evals.csv", "eval_timing.csv"):
            if (run_dir / name).exists():
                (run_dir / name).unlink()

    if decision.action == "resume":
        for s in trainer.logger.sinks:
            if hasattr(s, "recover"):
                s.recover(trainer.step)
    evaluator = Evaluator(
        cfg,
        run_dir,
        after_rows=lambda step: _halt_hook(step, "eval_rows"),
        logger=trainer.logger,
    )
    timer = {"last": time.monotonic()}
    period = float(cfg.runtime.get("ckpt_minutes", 20.0)) * 60.0

    def on_ckpt(t):
        timer["last"] = time.monotonic()
        write_status(run_dir, "running", t.step)
        _halt_hook(t.step)

    def on_step(t):
        stage = evaluator.due(t.step)
        if stage is not None:
            evaluator.at_point(t, stage)  # also writes last.pt
            on_ckpt(t)
        elif period > 0 and time.monotonic() - timer["last"] >= period:
            t.save_checkpoint()
            on_ckpt(t)

    trainer.on_checkpoint = on_ckpt
    trainer.on_step = on_step
    # the eval point at the step we start from: step 0 on a fresh run, and on a
    # resume any point whose evaluation never got written -- a run killed after
    # the checkpoint at an eval step but before that eval (the final one, say)
    # would otherwise finish "done" without it
    stage = evaluator.due(trainer.step)
    if stage is not None:
        from .eval.writers import EvalsCSV

        have = {(r["step"], r["stage"]) for r in EvalsCSV(run_dir / "evals.csv").read()}
        if (trainer.step, stage) not in have:
            evaluator.at_point(trainer, stage)
    trainer.train()
    trainer.save_checkpoint()
    _write_training_check(cfg, run_dir, trainer)
    trainer.logger.log_files(
        [
            run_dir / n
            for n in ("meta.json", "training_check.json", "final_metrics.json")
        ]
    )
    return trainer


def _attach_logger(cfg, run_dir: Path, trainer, decision: Decision) -> None:
    """Files always; W&B too with logging=wandb (mode online or offline).

    The W&B id is made once, when the run first starts, and kept in meta.json
    (via extra_meta); a resume reuses the id already in meta.json. A failure to
    import or reach W&B never stops the run.
    """
    from .runlog import (
        FilesSink,
        RunLogger,
        WandbSink,
        generate_wandb_id,
        get_wandb,
        wandb_tags,
    )

    files = FilesSink(run_dir, trainer.layout.train_log)
    trainer.logger = RunLogger(files)
    lg = cfg.logging
    if lg.sink != "wandb" or lg.mode == "disabled":
        return
    meta_path = run_dir / "meta.json"
    old = json.loads(meta_path.read_text()) if meta_path.exists() else {}
    wid = old.get("wandb_id") if decision.action == "resume" else None
    try:
        wb = get_wandb()
        wid = wid or generate_wandb_id(wb)
    except Exception as e:  # noqa: BLE001 - W&B must never stop a run
        print(
            f"[runlog] WARNING: W&B unavailable ({type(e).__name__}: {e}); "
            "logging to the run dir only",
            file=sys.stderr,
            flush=True,
        )
        return
    trainer.extra_meta["wandb_id"] = wid
    if decision.action == "resume" and old and old.get("wandb_id") != wid:
        old["wandb_id"] = wid  # first W&B use on a resumed run
        meta_path.write_text(json.dumps(old, indent=2, default=str))
    resolved = OmegaConf.to_container(cfg, resolve=True)
    meta = {**trainer.meta_dict()}
    sink = WandbSink(
        run_dir,
        OmegaConf.to_container(lg),
        wid,
        str(cfg.run_id),
        str(cfg.name),
        resolved,
        wandb_tags(meta, resolved),
        job_type="train",
        wandb_dir=lg.dir or str(Path(cfg.out_root) / ".wandb"),
        module=wb,
    )
    trainer.logger = RunLogger(files, [sink])
    print(f"[run] W&B mirror: mode={lg.mode} project={lg.project} id={wid}", flush=True)


def _write_training_check(cfg, run_dir: Path, trainer) -> None:
    if not cfg.eval.training_check.enabled:
        return
    from .eval.training_check import training_check
    from .eval.writers import EvalsCSV, write_json

    with open(trainer.csv_path, newline="") as fh:
        train_rows = (
            [
                {"step": int(r["step"]), "loss": float(r["loss"])}
                for r in csv.DictReader(fh)
            ]
            if trainer.csv_path.exists()
            else []
        )
    th = {k: v for k, v in cfg.eval.training_check.items() if k != "enabled"}
    res = training_check(
        train_rows,
        EvalsCSV(run_dir / "evals.csv").read(),
        int(cfg.train.warmup_steps),
        sorted(trainer.model.memory_layers),
        th,
    )
    res["step"] = trainer.step
    write_json(run_dir / "training_check.json", res)
    print(
        f"[run] training check: {res['verdict']}"
        + (f" (failed: {', '.join(res['failed'])})" if res["failed"] else "")
        + (
            f" (not evaluated: {', '.join(res['not_evaluated'])})"
            if res["not_evaluated"]
            else ""
        ),
        flush=True,
    )


def _main(cfg: DictConfig) -> None:
    from hydra.core.hydra_config import HydraConfig
    from hydra.types import RunMode

    hc = HydraConfig.get()
    try:
        launch(cfg, list(hc.overrides.task))
    except RunRefused as e:
        print(f"[run] REFUSED: {e}", file=sys.stderr, flush=True)
        if hc.mode == RunMode.MULTIRUN:
            return  # the other jobs of the sweep still run
        sys.exit(2)


def main() -> None:
    import hydra

    hydra.main(version_base="1.3", config_path="../conf", config_name="config")(_main)()


if __name__ == "__main__":
    main()
