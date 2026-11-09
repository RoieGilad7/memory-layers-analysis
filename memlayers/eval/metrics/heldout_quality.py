"""Q1 -- held-out next-token loss, perplexity and top-1 accuracy per subject.

Interim implementation (see fact_recall.py): when the metrics owner's
perplexity code lands it replaces this under the same name and keys.

Per document: a window never mixes two documents. The fixed 200-document
sample during training, the whole test half at `final` and `posthoc`.

Keys, for the 6 subject slugs and `pile_avg` (token-weighted over the 5
training subjects; USPTO, never trained on, is excluded):
    loss/<slug>  ppl/<slug> (= exp(loss))  top1/<slug>  tokens/<slug>  docs/<slug>
At a full-set stage also `loss/pile_avg_sample`: the same average over the
fixed sample's documents only, which keeps the final point on the
during-training curve (the training check uses it).
"""

from __future__ import annotations

import math
from typing import Dict

from ..registry import register_metric


def _row(prefix: str, s: Dict[str, float]) -> Dict[str, float]:
    if not s["tokens"]:
        return {}
    loss = s["loss_sum"] / s["tokens"]
    return {
        f"loss/{prefix}": loss,
        f"ppl/{prefix}": math.exp(loss),
        f"top1/{prefix}": s["correct"] / s["tokens"],
        f"tokens/{prefix}": float(s["tokens"]),
        f"docs/{prefix}": float(s["docs"]),
    }


def _pool(sums, slugs) -> Dict[str, float]:
    out = {"loss_sum": 0.0, "tokens": 0, "correct": 0, "docs": 0}
    for s in slugs:
        for k in out:
            out[k] += sums[s][k]
    return out


@register_metric(
    "heldout_quality",
    metric_id="Q1",
    stages=("during", "final", "posthoc"),
    needs_memory=False,
    inputs=("model", "heldout"),
)
def heldout_quality(ctx) -> Dict[str, float]:
    """Held-out loss, perplexity and top-1 per subject (per-document windows)."""
    p = ctx.heldout_pass()
    out: Dict[str, float] = {}
    for slug, s in p.sums.items():
        out.update(_row(slug, s))
    train = [s for s in ctx.resources.train_slugs() if s in p.sums]
    out.update(_row("pile_avg", _pool(p.sums, train)))
    if not p.sample:
        pooled = _pool(p.sample_sums, train)
        if pooled["tokens"]:
            out["loss/pile_avg_sample"] = pooled["loss_sum"] / pooled["tokens"]
    return out
