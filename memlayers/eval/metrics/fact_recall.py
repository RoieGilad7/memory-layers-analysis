"""Q2 -- fact recall: is the true attribute value the model's top candidate?

DECIDED: this is a stand-in. It wraps `data.q2_probe.ProbeSet.score` (the A18
data check) and nothing more. When the metrics owner's fact-recall code lands
it replaces this file under the same name (`fact_recall`) and the same keys,
and this stand-in is deleted, so there is never a second number.

The fixed fact sample during training, every test and paraphrase fact at
`final` and `posthoc`. Keys:
    top1/<tier>/<role>  rank/<tier>/<role> (mean rank)  margin/<tier>/<role>
        (mean margin) for tiers frequent, normal, rare, control and roles
        test, paraphrase
    top1/<tier>/test/<attribute> for the 5 attributes
"""

from __future__ import annotations

from typing import Dict

from ..registry import register_metric


@register_metric(
    "fact_recall",
    metric_id="Q2",
    stages=("during", "final", "posthoc"),
    needs_memory=False,
    inputs=("model", "fact_probe"),
)
def fact_recall(ctx) -> Dict[str, float]:
    """Fact recall top-1 / mean rank / mean margin per tier, role and attribute."""
    res = ctx.fact_probe().score(
        ctx.model,
        ctx.device,
        batch_tokens=ctx.fact_batch_tokens,
        block_size=ctx.block_size,
    )
    return keys_from_score(res)


def keys_from_score(res) -> Dict[str, float]:
    out: Dict[str, float] = {}
    for tr, agg in sorted(res["by_tier_role"].items()):
        if not agg.get("n"):
            continue
        out[f"top1/{tr}"] = float(agg["top1"])
        out[f"rank/{tr}"] = float(agg["mean_rank"])
        out[f"margin/{tr}"] = float(agg["mean_margin"])
    for tra, agg in sorted(res["by_tier_role_attribute"].items()):
        tier, role, attr = tra.split("/")
        if role == "test" and agg.get("n"):
            out[f"top1/{tier}/test/{attr}"] = float(agg["top1"])
    return out
