"""The automatic training check: did this run train?

Gating rules (thresholds in `eval.training_check`):
  finite          no NaN or inf in any logged training or held-out loss
  no_divergence   after warmup, the training loss never exceeds
                  `divergence_factor` (1.5) x its running minimum
  learned         final pile_avg held-out loss at least `min_drop_from_init`
                  (40%) below its step-0 value
  not_rising      final pile_avg loss not above its minimum over the eval
                  points by more than `rising_tolerance` (0.5%)
  coverage        memory runs: final coverage of every memory layer at least
                  `min_coverage` (0.5; set from the pilot in prompt 5)
  fact_learning   frequent-tier test top-1 at least `fact_ratio` (2) x the
                  control's, and above it (the A18 rule)
Reported, not gating:
  flattening      pile_avg loss drop per token over the last eval interval
                  divided by the drop per token over the interval before

The pile_avg curve is read on the fixed sample's documents at every point
(`loss/pile_avg` during training, `loss/pile_avg_sample` at the final, full
pass), so all points are on the same documents. A rule without the data it
needs is `pass: null` and makes the verdict `incomplete`, not `pass`.
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Sequence

__all__ = ["DEFAULTS", "training_check"]

DEFAULTS = dict(
    divergence_factor=1.5,
    min_drop_from_init=0.40,
    rising_tolerance=0.005,
    min_coverage=0.5,
    fact_ratio=2.0,
)


def _finite(x) -> bool:
    try:
        return math.isfinite(float(x))
    except (TypeError, ValueError):
        return False


def pile_curve(eval_rows: Sequence[dict]) -> List[dict]:
    """[(step, tokens_seen, loss)] on the sample documents, one per eval point."""
    pts: Dict[int, dict] = {}
    for r in eval_rows:
        if r["metric"] != "heldout_quality" or r["stage"] == "posthoc":
            continue
        if r["stage"] == "during" and r["key"] == "loss/pile_avg":
            pts.setdefault(r["step"], {}).update(
                step=r["step"], tokens=r["tokens_seen"], loss=r["value"]
            )
        if r["stage"] == "final" and r["key"] == "loss/pile_avg_sample":
            pts.setdefault(r["step"], {}).update(
                step=r["step"], tokens=r["tokens_seen"], loss=r["value"]
            )
    return [pts[s] for s in sorted(pts) if "loss" in pts[s]]


def _final(eval_rows, metric) -> Dict[str, float]:
    finals = [r for r in eval_rows if r["stage"] == "final" and r["metric"] == metric]
    if not finals:
        return {}
    step = max(r["step"] for r in finals)
    return {r["key"]: r["value"] for r in finals if r["step"] == step}


def training_check(
    train_rows: Sequence[dict],
    eval_rows: Sequence[dict],
    warmup_steps: int,
    memory_layers: Sequence[int],
    thresholds: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    th = {**DEFAULTS, **(thresholds or {})}
    rules: Dict[str, Dict[str, Any]] = {}
    losses = [(int(r["step"]), r["loss"]) for r in train_rows]

    # finite
    bad_train = [s for s, l in losses if not _finite(l)]
    held = [
        r
        for r in eval_rows
        if r["metric"] == "heldout_quality" and r["key"].startswith("loss/")
    ]
    bad_eval = [(r["step"], r["key"]) for r in held if not _finite(r["value"])]
    rules["finite"] = {
        "gating": True,
        "train_rows": len(losses),
        "eval_loss_rows": len(held),
        "first_bad_train_step": bad_train[0] if bad_train else None,
        "bad_eval": bad_eval[:5],
        "pass": (not bad_train and not bad_eval) if losses else None,
    }

    # no divergence
    worst, worst_step, run_min = 0.0, None, math.inf
    for s, l in losses:
        if s <= warmup_steps or not _finite(l):
            continue
        l = float(l)
        if run_min < math.inf and l / run_min > worst:
            worst, worst_step = l / run_min, s
        run_min = min(run_min, l)
    after = [s for s, _ in losses if s > warmup_steps]
    rules["no_divergence"] = {
        "gating": True,
        "factor": th["divergence_factor"],
        "worst_ratio_to_running_min": round(worst, 6) if worst else None,
        "at_step": worst_step,
        "pass": (
            (worst <= th["divergence_factor"] and not bad_train)
            if len(after) > 1
            else None
        ),
    }

    # learned / not rising / flattening
    curve = pile_curve(eval_rows)
    init = next((p for p in curve if p["step"] == 0), None)
    final_steps = [
        r["step"]
        for r in eval_rows
        if r["stage"] == "final" and r["metric"] == "heldout_quality"
    ]
    final = next(
        (p for p in curve if final_steps and p["step"] == max(final_steps)), None
    )
    if init and final and final["step"] > 0:
        drop = 1.0 - final["loss"] / init["loss"]
        rules["learned"] = {
            "gating": True,
            "init_loss": init["loss"],
            "final_loss": final["loss"],
            "drop": round(drop, 6),
            "min_drop": th["min_drop_from_init"],
            "pass": drop >= th["min_drop_from_init"],
        }
    else:
        rules["learned"] = {
            "gating": True,
            "pass": None,
            "why": "needs a step-0 and a final held-out eval",
        }
    if final and len(curve) >= 2:
        lo = min(p["loss"] for p in curve)
        rules["not_rising"] = {
            "gating": True,
            "final_loss": final["loss"],
            "min_loss": lo,
            "excess": round(final["loss"] / lo - 1.0, 6),
            "tolerance": th["rising_tolerance"],
            "pass": final["loss"] <= lo * (1.0 + th["rising_tolerance"]),
        }
    else:
        rules["not_rising"] = {
            "gating": True,
            "pass": None,
            "why": "needs two or more eval points",
        }
    if len(curve) >= 3:
        a, b, c = curve[-3], curve[-2], curve[-1]
        prev = (a["loss"] - b["loss"]) / max(1, b["tokens"] - a["tokens"])
        last = (b["loss"] - c["loss"]) / max(1, c["tokens"] - b["tokens"])
        rules["flattening"] = {
            "gating": False,
            "last_interval": [b["step"], c["step"]],
            "drop_per_token_last": last,
            "drop_per_token_prev": prev,
            "ratio": (last / prev) if prev else None,
            "last_interval_relative_drop": round(1.0 - c["loss"] / b["loss"], 6),
            "pass": None,
        }
    else:
        rules["flattening"] = {
            "gating": False,
            "pass": None,
            "why": "needs three eval points",
        }

    # coverage
    if memory_layers:
        fin = _final(eval_rows, "slot_usage")
        cov = {L: fin.get(f"coverage/layer{L}") for L in memory_layers}
        rules["coverage"] = {
            "gating": True,
            "min_coverage": th["min_coverage"],
            "coverage": {f"layer{L}": v for L, v in cov.items()},
            "pass": (
                all(v >= th["min_coverage"] for v in cov.values())
                if all(v is not None for v in cov.values())
                else None
            ),
        }
    else:
        rules["coverage"] = {"gating": False, "pass": None, "why": "no memory layer"}

    # fact learning
    fin = _final(eval_rows, "fact_recall")
    f, c = fin.get("top1/frequent/test"), fin.get("top1/control/test")
    if f is not None and c is not None:
        rules["fact_learning"] = {
            "gating": True,
            "frequent_test_top1": f,
            "control_test_top1": c,
            "ratio": (f / c) if c else None,
            "required_ratio": th["fact_ratio"],
            "pass": f >= th["fact_ratio"] * c and f > c,
        }
    else:
        rules["fact_learning"] = {
            "gating": True,
            "pass": None,
            "why": "no final fact_recall",
        }

    gating = {k: v["pass"] for k, v in rules.items() if v["gating"]}
    if any(p is False for p in gating.values()):
        verdict = "fail"
    elif any(p is None for p in gating.values()):
        verdict = "incomplete"
    else:
        verdict = "pass"
    return {
        "verdict": verdict,
        "failed": sorted(k for k, p in gating.items() if p is False),
        "not_evaluated": sorted(k for k, p in gating.items() if p is None),
        "thresholds": th,
        "rules": rules,
    }
