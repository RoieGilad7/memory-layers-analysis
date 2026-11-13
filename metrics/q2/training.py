"""Q2 in the training evaluation: `fact_recall`, scored with `fact_metrics`.

This replaces the training-side stand-in, so the run's Q2 and the checkpoint
suite's Q2 use one definition: per fact row, the true value's tie-aware top-1
credit, mid-rank and log-probability margin over the attribute's candidates
(`metrics.q2.fact_metrics`). The data probe only supplies the batched forward
passes and the candidate log-probabilities.

The fixed fact sample during training, every test and paraphrase fact at
`final` and `posthoc`. Keys (unchanged, so the training check, comparisons and
W&B keep working):
    top1/<tier>/<role>  rank/<tier>/<role> (mean rank)  margin/<tier>/<role>
        (mean margin) for tiers frequent, normal, rare, control and roles
        test, paraphrase
    top1/<tier>/test/<attribute> for the 5 attributes
"""

from __future__ import annotations

from collections import defaultdict
from statistics import fmean
from typing import Dict

from memlayers.eval.registry import register_metric

from . import fact_metrics


def score_rows(probe, scores) -> list:
    """`fact_metrics` for every probe row, from its candidate log-probabilities."""
    return [
        fact_metrics([float(x) for x in s], row.true_index)
        for row, s in zip(probe.rows, scores, strict=True)
    ]


def summarize(probe, per_row) -> Dict[str, dict]:
    groups = {
        "by_tier_role": defaultdict(list),
        "by_tier_role_attribute": defaultdict(list),
    }
    for row, m in zip(probe.rows, per_row, strict=True):
        groups["by_tier_role"][f"{row.tier}/{row.role}"].append(m)
        groups["by_tier_role_attribute"][
            f"{row.tier}/{row.role}/{row.attribute}"
        ].append(m)
    return {
        name: {
            key: {
                "n": len(rows),
                "top1": fmean(r["top1"] for r in rows),
                "mean_rank": fmean(r["rank"] for r in rows),
                "mean_margin": fmean(r["margin"] for r in rows),
            }
            for key, rows in sorted(group.items())
        }
        for name, group in groups.items()
    }


def keys_from_summary(res) -> Dict[str, float]:
    out: Dict[str, float] = {}
    for tr, agg in res["by_tier_role"].items():
        out[f"top1/{tr}"] = float(agg["top1"])
        out[f"rank/{tr}"] = float(agg["mean_rank"])
        out[f"margin/{tr}"] = float(agg["mean_margin"])
    for tra, agg in res["by_tier_role_attribute"].items():
        tier, role, attr = tra.split("/")
        if role == "test":
            out[f"top1/{tier}/test/{attr}"] = float(agg["top1"])
    return out


@register_metric(
    "fact_recall",
    metric_id="Q2",
    stages=("during", "final", "posthoc"),
    needs_memory=False,
    inputs=("model", "fact_probe"),
)
def fact_recall(ctx) -> Dict[str, float]:
    """Fact recall top-1 / mean rank / mean margin per tier, role and attribute."""
    probe = ctx.fact_probe()
    res = probe.score(
        ctx.model,
        ctx.device,
        batch_tokens=ctx.fact_batch_tokens,
        block_size=ctx.block_size,
        collect_scores=True,
    )
    return keys_from_summary(summarize(probe, score_rows(probe, res["_scores"])))
