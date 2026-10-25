"""Step-1 benchmarks: micro-batch probe, speed/memory, read-log cost, learning check.

Modes
    probe      largest micro-batch from {4,8,16,32} that runs, each tried in its own
               subprocess so a failed attempt cannot poison the next one
    probe-one  try exactly one micro-batch size; exit 0 if it ran, 1 if it did not
    speed      N steps on fake data (a), discard the first W as warmup, report
               mean/p90 step time, tokens/sec and peak memory
    learn      N steps on fake data (b), report the loss curve and slot-usage stats
    summarize  collect every results/*.json into one table

Results land in bench/results/<config>__<mode>.json.

MPS CPU-fallback detection: PYTORCH_ENABLE_MPS_FALLBACK is deliberately left unset,
so an op with no Metal kernel raises instead of silently moving to the CPU. A run
that completes is therefore proof that nothing fell back.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import platform
import statistics
import subprocess
import sys
import time
import pathlib
from pathlib import Path
from typing import List, Optional

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import torch  # noqa: E402

from memlayers.devices import empty_cache, peak_memory_bytes, pick_device  # noqa: E402
from memlayers.readlog import bytes_per_token  # noqa: E402
from memlayers.train import Trainer, load_config  # noqa: E402

RESULTS = ROOT / "bench" / "results"
BATCH_LADDER = [4, 8, 16, 32]


def rel(p) -> str:
    """Path relative to the repo root, so result files are portable across machines."""
    try:
        return str(pathlib.Path(p).resolve().relative_to(ROOT))
    except (ValueError, OSError):
        return str(p)


def env_info() -> dict:
    dev = pick_device()
    info = {
        "platform": platform.platform(),
        "machine": platform.machine(),
        "python": sys.version.split()[0],
        "torch": torch.__version__,
        "device": str(dev),
        "mps_available": torch.backends.mps.is_available(),
        "mps_built": torch.backends.mps.is_built(),
        "cuda_available": torch.cuda.is_available(),
        "mps_fallback_env": os.environ.get("PYTORCH_ENABLE_MPS_FALLBACK", "<unset>"),
    }
    if dev.type == "cuda":
        info["gpu_name"] = torch.cuda.get_device_name(0)
        info["gpu_total_mem_bytes"] = torch.cuda.get_device_properties(0).total_memory
    try:
        info["chip"] = subprocess.run(
            ["sysctl", "-n", "machdep.cpu.brand_string"],
            capture_output=True, text=True).stdout.strip()
        info["ram_bytes"] = int(subprocess.run(
            ["sysctl", "-n", "hw.memsize"], capture_output=True, text=True).stdout.strip())
    except Exception:
        pass
    return info


def _out_path(cfg_path: str, mode: str, tag: str = "") -> Path:
    RESULTS.mkdir(parents=True, exist_ok=True)
    name = Path(cfg_path).stem
    return RESULTS / f"{name}__{mode}{('__' + tag) if tag else ''}.json"


FORCE = False


def _save(cfg_path: str, mode: str, res: dict, tag: str = "") -> Path:
    """Write a result, refusing to replace a longer run with a shorter one.

    bench/results/ is committed evidence that the reports cite, so an ad-hoc smoke run
    must not silently overwrite a full benchmark. Pass --force to override.
    """
    path = _out_path(cfg_path, mode, tag)
    new_steps = res.get("steps")
    if path.exists() and not FORCE and isinstance(new_steps, int):
        try:
            old_steps = json.loads(path.read_text()).get("steps")
        except Exception:
            old_steps = None
        if isinstance(old_steps, int) and old_steps > new_steps:
            alt = path.with_name(path.stem + f"__{new_steps}steps.json")
            alt.write_text(json.dumps(res, indent=2))
            print(f"[kept] {path.name} holds a longer run ({old_steps} steps); "
                  f"wrote this {new_steps}-step run to {alt.name} instead "
                  f"(use --force to overwrite)")
            return alt
    path.write_text(json.dumps(res, indent=2))
    return path


def check_all_on_device(trainer: Trainer) -> dict:
    """Confirm no parameter or buffer quietly stayed on the CPU."""
    want = trainer.device.type
    off = [n for n, p in trainer.model.named_parameters() if p.device.type != want]
    off += [n for n, b in trainer.model.named_buffers()
            if b is not None and b.device.type != want]
    return {"expected_device": want, "tensors_off_device": off,
            "all_on_device": not off}


# --------------------------------------------------------------------------- probe
def probe_one(cfg_path: str, micro: int, steps: int = 3,
              overrides: Optional[List[str]] = None) -> dict:
    ov = list(overrides or []) + [f"train.micro_batch_size={micro}",
                                  "train.grad_accum_steps=1",
                                  "train.log_every=0",
                                  f"runtime.out_dir=runs/_probe_{Path(cfg_path).stem}_{micro}"]
    cfg = load_config(cfg_path, ov)
    tr = Trainer(cfg)
    for _ in range(steps):
        tr.train_step()
    peak = peak_memory_bytes(tr.device)
    dev = check_all_on_device(tr)
    empty_cache(tr.device)
    return {"micro_batch_size": micro, "ok": True, "peak_mem_bytes": peak,
            "device_check": dev, "param_counts": tr.model.param_counts()}


def probe(cfg_path: str, ladder: List[int] = None, overrides=None) -> dict:
    ladder = ladder or BATCH_LADDER
    attempts = []
    best = None
    for micro in ladder:
        cmd = [sys.executable, str(Path(__file__)), "probe-one",
               "--config", cfg_path, "--micro", str(micro)]
        for o in overrides or []:
            cmd += ["--set", o]
        r = subprocess.run(cmd, capture_output=True, text=True, cwd=str(ROOT))
        if r.returncode == 0:
            payload = json.loads(r.stdout.strip().splitlines()[-1])
            attempts.append(payload)
            best = micro
        else:
            tail = (r.stderr or r.stdout).strip().splitlines()
            attempts.append({"micro_batch_size": micro, "ok": False,
                             "error": tail[-1] if tail else "unknown"})
            break
    res = {"config": rel(cfg_path), "ladder": ladder, "attempts": attempts,
           "largest_micro_batch": best, "env": env_info()}
    _save(cfg_path, "probe", res)
    return res


# --------------------------------------------------------------------------- speed
def speed(cfg_path: str, steps: int = 300, warmup: int = 30, micro: Optional[int] = None,
          read_logging: bool = False, overrides=None) -> dict:
    tag = "readlog" if read_logging else ""
    ov = list(overrides or []) + [
        f"train.steps={steps}", "train.log_every=25",
        f"train.read_logging={'true' if read_logging else 'false'}",
        # the baseline must capture nothing at all, so slot-usage tracking is off too;
        # with read logging on it stays on, as part of the cost being measured
        f"train.track_slot_usage={'true' if read_logging else 'false'}",
        f"runtime.out_dir=runs/bench_{Path(cfg_path).stem}{'_readlog' if read_logging else ''}",
    ]
    if micro:
        ov.append(f"train.micro_batch_size={micro}")
    cfg = load_config(cfg_path, ov)
    tr = Trainer(cfg)
    dev_check = check_all_on_device(tr)
    hist = tr.train(progress=True)

    kept = hist[warmup:]
    times = [h["step_time_s"] for h in kept]
    toks = [h["tokens_per_s"] for h in kept]
    tokens_per_step = cfg.tokens_per_step

    res = {
        "config": rel(cfg_path), "name": cfg.name, "mode": "speed",
        "read_logging": read_logging,
        "steps": steps, "warmup_discarded": warmup, "steps_measured": len(kept),
        "micro_batch_size": cfg.train.micro_batch_size,
        "grad_accum_steps": cfg.train.grad_accum_steps,
        "tokens_per_step": tokens_per_step,
        "ms_per_step_mean": 1000 * statistics.fmean(times),
        "ms_per_step_median": 1000 * statistics.median(times),
        "ms_per_step_p90": 1000 * sorted(times)[int(0.9 * len(times)) - 1],
        "ms_per_step_min": 1000 * min(times),
        "tokens_per_s_mean": statistics.fmean(toks),
        "tokens_per_s_from_mean_time": tokens_per_step / statistics.fmean(times),
        "peak_mem_bytes": tr.peak_mem,
        "peak_mem_GB": tr.peak_mem / 1e9,
        "loss_first": hist[0]["loss"], "loss_last": hist[-1]["loss"],
        "param_counts": tr.model.param_counts(),
        "device_check": dev_check,
        "env": env_info(),
        "out_dir": rel(tr.out_dir),
    }
    mem = tr.model.memory_layers
    if mem:
        res["memory_layers"] = {
            str(i): {"kind": m.kind, "n_slots": m.n_slots, "heads": m.n_heads,
                     "topk": m.topk, "reads_per_token": m.reads_per_token,
                     "readlog_bytes_per_token_theory": bytes_per_token(
                         m.n_slots, m.n_heads, m.topk, True)}
            for i, m in mem.items()}
    if read_logging:
        man = tr.out_dir / "readlog" / "manifest.json"
        if man.exists():
            m = json.loads(man.read_text())
            res["readlog"] = {
                "bytes_written": m["bytes_written"],
                "tokens_logged": m["tokens_logged"],
                "bytes_per_token": m["bytes_per_token"],
                "GB_per_million_tokens": m["bytes_per_token"] * 1e6 / 1e9,
            }
    if (tr.out_dir / "slot_usage.json").exists():
        res["slot_usage"] = json.loads((tr.out_dir / "slot_usage.json").read_text())
    empty_cache(tr.device)
    _save(cfg_path, "speed", res, tag)
    return res


# --------------------------------------------------------------------------- learn
def learn(cfg_path: str, steps: int = 1000, micro: Optional[int] = None,
          overrides=None) -> dict:
    ov = list(overrides or []) + [
        f"train.steps={steps}", "data.kind=repeat", "train.log_every=25",
        # slot-usage fraction and KL-from-uniform are required outputs of this phase,
        # so the histogram is on; the full per-token read log is not needed here
        "train.track_slot_usage=true", "train.read_logging=false",
        f"runtime.out_dir=runs/learn_{Path(cfg_path).stem}",
    ]
    if micro:
        ov.append(f"train.micro_batch_size={micro}")
    cfg = load_config(cfg_path, ov)
    tr = Trainer(cfg)
    hist = tr.train(progress=True)
    losses = [h["loss"] for h in hist]

    floor = tr.data.loss_floor()
    random_level = math.log(tr.gpt_config.vocab_size)
    tail = losses[-25:]
    res = {
        "config": rel(cfg_path), "name": cfg.name, "mode": "learn",
        "dataset": "repeat (fake data b)",
        "chunk_len": cfg.data.chunk_len,
        "steps": steps, "micro_batch_size": cfg.train.micro_batch_size,
        "tokens_seen": tr.tokens_seen,
        "random_token_level_nats": random_level,
        "task_loss_floor_nats": floor,
        "loss_first": losses[0],
        "loss_final": losses[-1],
        "loss_final_mean_last25": statistics.fmean(tail),
        "loss_min": min(losses),
        "clearly_below_random": statistics.fmean(tail) < random_level - 1.0,
        "curve_every_25": [{"step": h["step"], "loss": h["loss"]}
                           for h in hist if h["step"] % 25 == 0],
        "ms_per_step_mean": 1000 * statistics.fmean(
            h["step_time_s"] for h in hist[min(30, len(hist) // 3):]),
        "peak_mem_GB": tr.peak_mem / 1e9,
        "param_counts": tr.model.param_counts(),
        "env": env_info(),
        "out_dir": rel(tr.out_dir),
    }
    if (tr.out_dir / "slot_usage.json").exists():
        res["slot_usage"] = json.loads((tr.out_dir / "slot_usage.json").read_text())
    empty_cache(tr.device)
    _save(cfg_path, "learn", res)
    return res


# ----------------------------------------------------------------------- summarize
def extrapolate(tokens_per_s: float, tokens: float) -> float:
    return tokens / tokens_per_s / 3600.0 if tokens_per_s > 0 else float("nan")


def summarize() -> dict:
    rows = []
    for f in sorted(RESULTS.glob("*__speed*.json")):
        d = json.loads(f.read_text())
        pc = d["param_counts"]
        tps = d["tokens_per_s_from_mean_time"]
        rows.append({
            "name": d["name"], "read_logging": d["read_logging"],
            "micro_batch": d["micro_batch_size"],
            "emb_M": pc["embedding"] / 1e6,
            "backbone_M": pc["backbone"] / 1e6,
            "memory_M": pc["memory_total"] / 1e6,
            "total_M": pc["total"] / 1e6,
            "ms_step_mean": d["ms_per_step_mean"],
            "ms_step_p90": d["ms_per_step_p90"],
            "tokens_per_s": tps,
            "peak_GB": d["peak_mem_GB"],
            "readlog_GB_per_Mtok": d.get("readlog", {}).get("GB_per_million_tokens"),
            "hours_150M": extrapolate(tps, 150e6),
            "hours_500M": extrapolate(tps, 500e6),
        })
    out = {"rows": rows, "env": env_info()}
    (RESULTS / "summary.json").write_text(json.dumps(out, indent=2))

    hdr = (f"{'config':16s} {'RL':3s} {'mb':>3s} {'emb':>7s} {'back':>7s} {'mem':>8s} "
           f"{'total':>8s} {'ms/step':>8s} {'p90':>8s} {'tok/s':>8s} {'GB':>6s} "
           f"{'h/150M':>7s} {'h/500M':>7s}")
    print(hdr)
    print("-" * len(hdr))
    for r in rows:
        print(f"{r['name']:16s} {'Y' if r['read_logging'] else 'n':3s} "
              f"{r['micro_batch']:3d} {r['emb_M']:6.2f}M {r['backbone_M']:6.2f}M "
              f"{r['memory_M']:7.2f}M {r['total_M']:7.2f}M {r['ms_step_mean']:8.1f} "
              f"{r['ms_step_p90']:8.1f} {r['tokens_per_s']:8.0f} {r['peak_GB']:6.2f} "
              f"{r['hours_150M']:7.2f} {r['hours_500M']:7.2f}")
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("mode", choices=["probe", "probe-one", "speed", "learn", "summarize"])
    ap.add_argument("--config")
    ap.add_argument("--micro", type=int, default=None)
    ap.add_argument("--steps", type=int, default=None)
    ap.add_argument("--warmup", type=int, default=30)
    ap.add_argument("--read-logging", action="store_true")
    ap.add_argument("--set", nargs="*", default=[], dest="overrides")
    ap.add_argument("--force", action="store_true",
                    help="allow overwriting a longer existing result in bench/results/")
    a = ap.parse_args(argv)

    global FORCE
    FORCE = a.force

    if a.mode == "summarize":
        summarize()
        return 0
    if not a.config:
        ap.error("--config is required for this mode")

    if a.mode == "probe-one":
        print(json.dumps(probe_one(a.config, a.micro, overrides=a.overrides)))
    elif a.mode == "probe":
        r = probe(a.config, overrides=a.overrides)
        print(f"largest micro-batch that ran: {r['largest_micro_batch']}")
    elif a.mode == "speed":
        r = speed(a.config, steps=a.steps or 300, warmup=a.warmup, micro=a.micro,
                  read_logging=a.read_logging, overrides=a.overrides)
        print(f"{r['name']}: {r['ms_per_step_mean']:.1f} ms/step  "
              f"{r['tokens_per_s_from_mean_time']:.0f} tok/s  {r['peak_mem_GB']:.2f} GB")
    elif a.mode == "learn":
        r = learn(a.config, steps=a.steps or 1000, micro=a.micro, overrides=a.overrides)
        print(f"{r['name']}: loss {r['loss_first']:.3f} -> {r['loss_final']:.3f} "
              f"(floor {r['task_loss_floor_nats']:.3f}, random {r['random_token_level_nats']:.3f})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
