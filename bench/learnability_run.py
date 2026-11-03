"""A18 -- are the biography facts learnable at this exposure budget?

    python bench/learnability_run.py --steps 5830 --eval-every 972

Trains T1-pkm on the real data for about two hours (~95M tokens) and evaluates
fact recall at step 0 and every ~20 minutes, plus per-subject held-out loss on
the test halves. Writes a CSV, a JSON and a PNG of recall per tier over
training, test and paraphrase prompts separately, against the control line.

This is a **data check**: if the facts are not learnable, the data has to change
before the real training runs start. It does not change the data either way.

Pass rule (from the fixed design): at the end, frequent-tier test-prompt top-1
is at least twice the control people's, and top-1 goes frequent >= normal >=
rare. Paraphrase accuracy is reported but is not part of the rule.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

import torch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from bench.smoke_real_data import heldout_loss_by_subject
from data.common import load_config as load_data_config
from data.q2_probe import ProbeSet, select_eval_rows, summarize
from memlayers.devices import empty_cache
from memlayers.train import Trainer, load_config

TIERS = ["frequent", "normal", "rare", "control"]
ROLES = ["test", "paraphrase"]


def csv_fields(subjects: List[str]) -> List[str]:
    f = ["step", "train_seconds", "wall_seconds", "tokens_seen", "train_loss"]
    for tier in TIERS:
        for role in ROLES:
            f += [f"top1_{tier}_{role}", f"rank_{tier}_{role}",
                  f"margin_{tier}_{role}"]
    f += [f"heldout_{s.replace(' ', '_')}" for s in subjects]
    return f


def row_from_eval(step, train_s, wall_s, tokens, loss, probe_result, held,
                  subjects) -> Dict[str, Any]:
    row = {"step": step, "train_seconds": round(train_s, 1),
           "wall_seconds": round(wall_s, 1), "tokens_seen": tokens,
           "train_loss": "" if loss is None else round(loss, 4)}
    tr = probe_result["by_tier_role"]
    for tier in TIERS:
        for role in ROLES:
            a = tr.get(f"{tier}/{role}")
            row[f"top1_{tier}_{role}"] = round(a["top1"], 6) if a else ""
            row[f"rank_{tier}_{role}"] = round(a["mean_rank"], 2) if a else ""
            row[f"margin_{tier}_{role}"] = round(a["mean_margin"], 4) if a else ""
    for s in subjects:
        v = held.get(s)
        row[f"heldout_{s.replace(' ', '_')}"] = v["loss"] if v else ""
    return row


def plot(rows: List[Dict[str, Any]], out: Path, title: str) -> Path:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    steps = [r["step"] for r in rows]
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2), sharey=True)
    colors = {"frequent": "#1b5e9e", "normal": "#3f9d5a", "rare": "#c8872b",
              "control": "#9a9a9a"}
    for ax, role in zip(axes, ROLES):
        for tier in TIERS:
            y = [float(r[f"top1_{tier}_{role}"]) * 100 for r in rows]
            ax.plot(steps, y, marker="o", ms=4,
                    color=colors[tier], lw=2.2 if tier != "control" else 1.6,
                    ls="--" if tier == "control" else "-",
                    label=f"{tier}" + (" (never trained)" if tier == "control"
                                       else ""))
        ax.set_title(f"{role} prompts")
        ax.set_xlabel("training step")
        ax.grid(alpha=0.25, lw=0.6)
    axes[0].set_ylabel("fact-recall top-1 (%)")
    axes[0].legend(frameon=False, fontsize=9)
    fig.suptitle(title, fontsize=11)
    fig.tight_layout()
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


def check_pass(final: Dict[str, Any]) -> Dict[str, Any]:
    tr = final["by_tier_role"]
    def t1(tier, role):
        a = tr.get(f"{tier}/{role}")
        return float(a["top1"]) if a else 0.0
    freq, norm, rare, ctrl = (t1(t, "test") for t in TIERS)
    checks = {
        "frequent_at_least_twice_control": {
            "frequent": freq, "control": ctrl,
            "ratio": round(freq / ctrl, 3) if ctrl > 0 else None,
            "pass": freq >= 2 * ctrl},
        "monotone_frequent_normal_rare": {
            "frequent": freq, "normal": norm, "rare": rare,
            "pass": freq >= norm >= rare},
    }
    return {"checks": checks, "pass": all(c["pass"] for c in checks.values()),
            "test_top1": {"frequent": freq, "normal": norm, "rare": rare,
                          "control": ctrl},
            "paraphrase_top1": {t: t1(t, "paraphrase") for t in TIERS}}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--config", default="memlayers/configs/t1_pkm.yaml")
    ap.add_argument("--data-config", default="configs/data/v1.yaml")
    ap.add_argument("--steps", type=int, default=5830)
    ap.add_argument("--eval-every", type=int, default=972,
                    help="steps between evaluations (~20 min at 1.24 s/step)")
    ap.add_argument("--micro-batch-size", type=int, default=32)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--max-train-hours", type=float, default=2.4,
                    help="hard cap on TRAINING time, excluding evaluation")
    ap.add_argument("--max-heldout-docs", type=int, default=200)
    ap.add_argument("--out-dir", default="runs/learnability_t1_pkm")
    ap.add_argument("--tag", default="learnability_t1_pkm")
    args = ap.parse_args(argv)

    data_cfg = load_data_config(args.data_config)
    cfg = load_config(ROOT / args.config, [
        "data.source=real", "data.version=v1",
        f"data.data_config={args.data_config}", f"data.seed={args.seed}",
        f"train.seed={args.seed}", f"train.steps={args.steps}",
        f"train.micro_batch_size={args.micro_batch_size}",
        "train.log_every=50", f"runtime.out_dir={args.out_dir}"])

    trainer = Trainer(cfg)
    trainer.write_meta()
    block = cfg.model.get("block_size", 512)
    subjects = list(data_cfg.all_subjects)

    print(f"[a18] building the evaluation set", flush=True)
    rows = select_eval_rows(data_cfg)
    probe = ProbeSet.build(data_cfg, rows)
    from collections import Counter
    counts = Counter((r.tier, r.role) for r in probe.rows)
    print(f"[a18] {len(probe):,} prompts: "
          + ", ".join(f"{k[0]}/{k[1]}={v:,}" for k, v in sorted(counts.items())),
          flush=True)

    out_dir = Path(args.out_dir)
    csv_path = out_dir / "a18_curve.csv"
    fields = csv_fields(subjects)
    with open(csv_path, "w", newline="") as fh:
        csv.DictWriter(fh, fieldnames=fields).writeheader()

    logged: List[Dict[str, Any]] = []
    evals: List[Dict[str, Any]] = []
    train_seconds = 0.0
    t_wall = time.time()
    last_loss: Optional[float] = None

    def evaluate(step: int) -> None:
        nonlocal train_seconds
        t0 = time.time()
        empty_cache(trainer.device)
        res = probe.score(trainer.model, trainer.device, block_size=block)
        held = heldout_loss_by_subject(trainer.model, trainer.device, data_cfg,
                                       "test", block, args.max_heldout_docs)
        empty_cache(trainer.device)
        row = row_from_eval(step, train_seconds, time.time() - t_wall,
                            trainer.tokens_seen, last_loss, res, held, subjects)
        logged.append(row)
        evals.append({"step": step, "train_seconds": round(train_seconds, 1),
                      "tokens_seen": trainer.tokens_seen,
                      "train_loss": last_loss,
                      "probe": summarize(res), "heldout": held})
        with open(csv_path, "a", newline="") as fh:
            csv.DictWriter(fh, fieldnames=fields).writerow(row)
        tr = res["by_tier_role"]
        print(f"[a18] step {step:>5} ({train_seconds / 60:.0f} min train, "
              f"{(time.time() - t_wall) / 60:.0f} min wall, eval "
              f"{time.time() - t0:.0f}s)  test top1: "
              + "  ".join(f"{t}={tr[f'{t}/test']['top1']:.3%}" for t in TIERS),
              flush=True)
        print(f"[a18]        paraphrase top1: "
              + "  ".join(f"{t}={tr[f'{t}/paraphrase']['top1']:.3%}"
                          for t in TIERS)
              + "   heldout(test): "
              + " ".join(f"{s.split()[0]}={held[s]['loss']:.3f}"
                         for s in subjects), flush=True)

    evaluate(0)
    cap = args.max_train_hours * 3600
    while trainer.step < args.steps and train_seconds < cap:
        t0 = time.time()
        stop = min(args.eval_every, args.steps - trainer.step)
        hist = trainer.train(steps=stop, progress=True)
        train_seconds += time.time() - t0
        last_loss = sum(r["loss"] for r in hist[-20:]) / min(20, len(hist))
        trainer.save_checkpoint()
        evaluate(trainer.step)

    final = evals[-1]["probe"]
    verdict = check_pass(final)
    png = plot(logged, ROOT / "bench" / "results" / f"{args.tag}.png",
               f"Biography fact recall during training "
               f"({cfg.name}, seed {args.seed}, {trainer.tokens_seen / 1e6:.0f}M tokens)")
    result = {
        "tag": args.tag, "config": args.config, "name": cfg.name,
        "device": str(trainer.device), "seed": args.seed,
        "steps": trainer.step, "tokens_seen": trainer.tokens_seen,
        "train_seconds": round(train_seconds, 1),
        "wall_seconds": round(time.time() - t_wall, 1),
        "micro_batch_size": cfg.train.micro_batch_size,
        "eval_prompts": len(probe),
        "eval_rows_by_tier_role": {f"{k[0]}/{k[1]}": v
                                   for k, v in sorted(counts.items())},
        "data": trainer.data_provenance,
        "verdict": verdict,
        "final_by_tier_role": final["by_tier_role"],
        "final_by_attribute": final["by_attribute"],
        "final_by_tier_role_attribute": final["by_tier_role_attribute"],
        "heldout_test": evals[-1]["heldout"],
        "evals": evals,
        "csv": str(csv_path.relative_to(ROOT)),
        "png": str(png.relative_to(ROOT)),
    }
    out = ROOT / "bench" / "results" / f"{args.tag}.json"
    out.write_text(json.dumps(result, indent=2))

    print(f"\n=== A18 {'PASS' if verdict['pass'] else 'FAIL'}")
    for name, c in verdict["checks"].items():
        print(f"   {'PASS' if c['pass'] else 'FAIL'}  {name}: "
              + ", ".join(f"{k}={v}" for k, v in c.items() if k != "pass"))
    print(f"   test top1:       {verdict['test_top1']}")
    print(f"   paraphrase top1: {verdict['paraphrase_top1']}")
    print(f"   -> {out.relative_to(ROOT)}  {png.relative_to(ROOT)}")
    return 0 if verdict["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
