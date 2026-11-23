"""Phase 2 pilot: pick the same-document loss weight lambda by a fixed rule.

    caffeinate -dimsu .venv/bin/python bench/doc_loss_pilot.py
    .venv/bin/python bench/doc_loss_pilot.py --dry-run      # 20 CPU steps, tiny model

For each lambda in LAMBDAS: the composed config of `experiment=pkm_doc runtime=mac
seed=0` with train.doc_loss_weight = lambda (train.steps stays 9156, so the LR
schedule is the full run's), trained for 1,500 steps into runs/pilot_doc/l<lambda>/
(legacy Trainer layout). Then, at step 1,500:

  heldout     the heldout_quality metric on the fixed during-training sample
  coverage    slot_usage's coverage/layer<L> from that same held-out pass
  train_loss  mean logged `loss` over steps 1,401-1,500
  gap         mean doc_loss "gap" over 20 fixed batches of real training windows
              (loader seed 12345), model in eval mode, no grad -- for every lambda,
              including 0
  step_time   median step_time_s over steps 101-1,500
  doc_gap_log the training log's doc_gap at steps 200, 500, 1000, 1500 (lambda > 0)

A finished run writes done.json and is skipped on a restart; an unfinished one
resumes from its last periodic checkpoint (every 500 steps).

Rule (fixed before the runs): the LARGEST lambda > 0 with
  a. held-out pile_avg loss at most 1% above the lambda = 0 run,
  b. gap at least 0.05 above the lambda = 0 run,
  c. layer coverage at least 0.8.
None passing -> None. Other lambdas are not tried.

The only change to the composed config besides the weight and out_dir is
train.log_every=1, so the per-step loss and step time are in the log (logging only;
it changes no number the run computes).
"""

from __future__ import annotations

import argparse
import csv
import json
import statistics
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

import torch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

LAMBDAS = [0.0, 0.003, 0.01, 0.03]
PILOT_STEPS = 1500
GAP_SEED = 12345
GAP_BATCHES = 20
GAP_TREND_STEPS = [200, 500, 1000, 1500]
# the rule
MAX_LOSS_INCREASE = 0.01  # relative, vs lambda = 0
MIN_GAP_GAIN = 0.05  # cosine, vs lambda = 0
MIN_COVERAGE = 0.8


# --------------------------------------------------------------------------- rule
def criteria(row: Dict[str, float], base: Dict[str, float]) -> Dict[str, bool]:
    """The three criteria for one lambda against the lambda = 0 row."""
    return {
        "a_heldout": row["heldout_pile_avg"]
        <= base["heldout_pile_avg"] * (1.0 + MAX_LOSS_INCREASE),
        "b_gap": row["gap"] >= base["gap"] + MIN_GAP_GAIN,
        "c_coverage": row["coverage"] >= MIN_COVERAGE,
    }


def choose_lambda(rows: Dict[float, Dict[str, float]]) -> Optional[float]:
    """The largest lambda > 0 passing all three criteria, or None.

    rows: {lambda: {"heldout_pile_avg", "gap", "coverage"}}, must include 0.
    """
    if 0.0 not in rows and 0 not in rows:
        raise ValueError("the rule needs the lambda = 0 run")
    base = rows[0.0]
    passing = [
        lam for lam, r in rows.items() if lam > 0 and all(criteria(r, base).values())
    ]
    return max(passing) if passing else None


# ---------------------------------------------------------------- gap measurement
@torch.no_grad()
def fixed_batch_gap(
    model,
    batches: Sequence[torch.Tensor],
    layer: int,
    eot_id: int,
    min_piece_tokens: int,
    tau: float,
) -> Dict[str, float]:
    """Mean doc_loss stats over fixed batches, model in eval mode, no grad.

    Query keeping is switched on for the measurement only; the model's train/eval
    mode and keep-queries state are put back. Eval mode means BatchNorm uses (and
    does not update) its running statistics.
    """
    from memlayers.doc_loss import doc_loss, find_halves, half_vectors

    mem = model.memory_layers[layer]
    was_training = model.training
    was_keeping = mem.keep_queries
    dev = next(model.parameters()).device
    gaps, losses, halves = [], [], []
    model.eval()
    mem.set_keep_queries(True)
    try:
        for x in batches:
            x = x.to(dev)
            model(x)
            q = mem.kept_queries()
            hid, n = find_halves(x, eot_id, min_piece_tokens)
            dl, st = doc_loss(half_vectors(q, hid, n), tau)
            halves.append(st["halves"])
            if st["gap"] is not None:
                gaps.append(st["gap"])
                losses.append(float(dl))
    finally:
        mem.release_kept_queries()
        if not was_keeping:
            mem.set_keep_queries(False)
        model.train(was_training)
    return {
        "gap": statistics.mean(gaps) if gaps else float("nan"),
        "doc_loss": statistics.mean(losses) if losses else float("nan"),
        "halves_mean": statistics.mean(halves) if halves else 0.0,
        "batches_used": len(gaps),
    }


def gap_batches(data_cfg, block_size: int, batch: int, n: int, vocab_size: int):
    """The first `n` batches of a loader over the run's train.bin seeded GAP_SEED."""
    from data.loader import PackedDataset
    from memlayers.train import load_bundle_config

    dcfg = load_bundle_config(data_cfg)
    path = (
        Path(data_cfg.bin_path) if data_cfg.bin_path else dcfg.tokens_dir / "train.bin"
    )
    ds = PackedDataset(
        path, block_size=block_size, seed=GAP_SEED, vocab_size=vocab_size
    )
    return [ds.get_batch(i, batch)[0] for i in range(n)]


# ------------------------------------------------------------------------ one run
def lam_name(lam: float) -> str:
    return f"l{lam:g}"


def compose_run(lam: float, out_dir: Path, dry_run: bool):
    from memlayers.config import compose

    ov = [
        "experiment=pkm_doc",
        "seed=0",
        "runtime=cpu" if dry_run else "runtime=mac",
        f"train.doc_loss_weight={lam}",
        f"runtime.out_dir={out_dir}",
        "train.log_every=1",
    ]
    if dry_run:
        # the smoke model on the committed 1% sample: GPT-2 tokens, CPU-fast
        ov += ["model=smoke_pkm", "data=sample", "train.micro_batch_size=4"]
    return compose(ov)


def read_log(path: Path) -> List[Dict[str, str]]:
    with open(path, newline="") as fh:
        return list(csv.DictReader(fh))


def _f(v) -> Optional[float]:
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def summarize_log(rows, steps: int, lam: float) -> Dict[str, Any]:
    by = {int(r["step"]): r for r in rows}
    tail = [_f(by[s]["loss"]) for s in range(steps - 99, steps + 1) if s in by]
    lo = 101 if steps >= 200 else max(1, steps // 2)
    times = [_f(by[s]["step_time_s"]) for s in range(lo, steps + 1) if s in by]
    trend = {}
    if lam > 0:
        for s in GAP_TREND_STEPS:
            if s in by:
                trend[str(s)] = _f(by[s].get("doc_gap"))
    return {
        "train_loss": statistics.mean(tail) if tail else float("nan"),
        "train_loss_steps": [steps - 99, steps],
        "train_loss_n": len(tail),
        "step_time_median_s": statistics.median(times) if times else float("nan"),
        "step_time_steps": [lo, steps],
        "doc_gap_log": trend,
    }


def run_one(lam: float, out_root: Path, steps: int, dry_run: bool, gap_cache: dict):
    from memlayers.eval.context import preserved_state
    from memlayers.eval.evaluator import Evaluator, run_metrics
    from memlayers.config import to_train_config
    from memlayers.devices import empty_cache
    from memlayers.run import _trim_train_log
    from memlayers.train import RunLayout, Trainer

    out = out_root / lam_name(lam)
    done = out / "done.json"
    if done.exists():
        print(f"[pilot] {out.name}: done.json exists, skipped", flush=True)
        return json.loads(done.read_text())
    out.mkdir(parents=True, exist_ok=True)
    cfg = compose_run(lam, out, dry_run)
    tc = to_train_config(cfg)
    layout = RunLayout.legacy()
    tr = Trainer(tc, layout=layout)
    ckpt = out / layout.checkpoint
    if ckpt.exists():
        tr.load_checkpoint(ckpt)
        _trim_train_log(out / layout.train_log, tr.step)
        print(f"[pilot] {out.name}: resumed at step {tr.step}", flush=True)
    t0 = time.perf_counter()
    if tr.step < steps:
        tr.train(steps=steps - tr.step, progress=True)
    train_s = time.perf_counter() - t0
    tr.save_checkpoint()
    tr.save_weights(out / f"step_{tr.step:06d}.pt")

    layer = tr.doc_layer
    if layer is None:
        mems = tr.model.memory_layers
        layer = (
            tc.train.doc_loss_layer
            if tc.train.doc_loss_layer is not None
            else next(iter(mems))
        )

    # held-out quality and slot usage: the during-training sample and metrics
    ev = Evaluator(cfg, out)
    t1 = time.perf_counter()
    with preserved_state(tr.model, tr.device):
        ctx = ev.context(tr.model, tr.step, tr.tokens_seen, "during")
        results, skipped, secs = run_metrics(["heldout_quality", "slot_usage"], ctx)
    if skipped:
        raise RuntimeError(f"metrics skipped: {skipped}")
    empty_cache(tr.device)
    hq, su = results["heldout_quality"], results["slot_usage"]

    # same-document gap on the fixed real-data batches
    key = (tc.model["block_size"], tc.train.micro_batch_size)
    if key not in gap_cache:
        n = 2 if dry_run else GAP_BATCHES
        gap_cache[key] = gap_batches(
            tc.data,
            tc.model["block_size"],
            tc.train.micro_batch_size,
            n,
            tc.model["vocab_size"],
        )
    g = fixed_batch_gap(
        tr.model,
        gap_cache[key],
        layer,
        int(tc.train.doc_loss_eot_id),
        int(tc.train.doc_loss_min_piece_tokens),
        float(tc.train.doc_loss_temperature),
    )
    eval_s = time.perf_counter() - t1

    logs = summarize_log(read_log(out / layout.train_log), tr.step, lam)
    res = {
        "lambda": lam,
        "step": tr.step,
        "tokens_seen": tr.tokens_seen,
        "layer": int(layer),
        "heldout_pile_avg": hq["loss/pile_avg"],
        "heldout_per_subject": {
            k.split("/", 1)[1]: v
            for k, v in hq.items()
            if k.startswith("loss/") and k != "loss/pile_avg"
        },
        "heldout_all": hq,
        "coverage": su[f"coverage/layer{layer}"],
        "slot_usage": su,
        "gap": g["gap"],
        "gap_detail": g,
        **logs,
        "train_seconds_this_launch": train_s,
        "eval_seconds": eval_s,
        "device": str(tr.device),
        "config": {
            k: getattr(tc.train, k) for k in vars(tc.train) if k.startswith("doc_loss_")
        },
        "train_steps_schedule": tc.train.steps,
        "finished_at": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    done.write_text(json.dumps(res, indent=2, default=float) + "\n")
    print(
        f"[pilot] {out.name}: heldout {res['heldout_pile_avg']:.4f}  gap {res['gap']:.4f}"
        f"  coverage {res['coverage']:.4f}  step {res['step_time_median_s']*1000:.0f} ms",
        flush=True,
    )
    del tr
    empty_cache(
        torch.device("mps")
        if torch.backends.mps.is_available()
        else torch.device("cpu")
    )
    return res


def table(results: Dict[float, Dict[str, Any]]) -> Dict[str, Any]:
    base = results[0.0]
    rows = []
    for lam in sorted(results):
        r = results[lam]
        rows.append(
            {
                "lambda": lam,
                "heldout_pile_avg": r["heldout_pile_avg"],
                "heldout_pct_vs_0": 100
                * (r["heldout_pile_avg"] / base["heldout_pile_avg"] - 1),
                "train_loss": r["train_loss"],
                "gap": r["gap"],
                "gap_minus_0": r["gap"] - base["gap"],
                "coverage": r["coverage"],
                "step_time_median_s": r["step_time_median_s"],
                "step_time_pct_vs_0": 100
                * (r["step_time_median_s"] / base["step_time_median_s"] - 1),
                "criteria": criteria(r, base) if lam > 0 else None,
            }
        )
    return {"rows": rows, "chosen_lambda": choose_lambda(results)}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--dry-run", action="store_true", help="20 CPU steps, tiny model")
    ap.add_argument("--out-root", default=None)
    ap.add_argument("--json", default=None, help="where to write the summary JSON")
    ap.add_argument("--lambdas", default=None, help="comma list (testing only)")
    a = ap.parse_args(argv)

    steps = 20 if a.dry_run else PILOT_STEPS
    out_root = Path(
        a.out_root or ("runs/pilot_doc_dry" if a.dry_run else "runs/pilot_doc")
    )
    lams = [float(x) for x in a.lambdas.split(",")] if a.lambdas else LAMBDAS
    gap_cache: dict = {}
    results = {}
    for lam in lams:
        results[lam] = run_one(lam, out_root, steps, a.dry_run, gap_cache)
    summary = {
        "steps": steps,
        "lambdas": lams,
        "rule": {
            "max_loss_increase": MAX_LOSS_INCREASE,
            "min_gap_gain": MIN_GAP_GAIN,
            "min_coverage": MIN_COVERAGE,
        },
        **table(results),
        "runs": {lam_name(k): v for k, v in results.items()},
    }
    path = Path(a.json or out_root / "summary.json")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(summary, indent=2, default=float) + "\n")
    print(json.dumps({"chosen_lambda": summary["chosen_lambda"]}), flush=True)
    for r in summary["rows"]:
        print(
            f"  l={r['lambda']:<6g} heldout {r['heldout_pile_avg']:.4f} "
            f"({r['heldout_pct_vs_0']:+.2f}%)  train {r['train_loss']:.4f}  "
            f"gap {r['gap']:.4f} ({r['gap_minus_0']:+.4f})  cov {r['coverage']:.4f}  "
            f"step {r['step_time_median_s']*1000:.0f} ms ({r['step_time_pct_vs_0']:+.1f}%)  "
            f"{r['criteria']}",
            flush=True,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
