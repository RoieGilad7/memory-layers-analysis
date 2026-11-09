"""U1 -- how much of each memory layer the held-out text reads.

Computed from the reads of the held-out pass that heldout_quality makes (the
context shares it), so no extra forward. Per memory layer:
    coverage/layer<i>       fraction of slots read at least once
    best_coverage/layer<i>  fraction of slots that are, at least once, the
                            highest-weight slot of some read (one read = one
                            head's top-k for one token)
    kl_uniform/layer<i>     KL(p || uniform) in nats, p = the weight-summed
                            usage distribution over all slots
Statistics come from memlayers.readlog.usage_stats.
"""

from __future__ import annotations

from typing import Dict

from memlayers.readlog import usage_stats

from ..registry import register_metric


def usage_keys(usage, n_slots) -> Dict[str, float]:
    out: Dict[str, float] = {}
    for layer in sorted(usage):
        u = usage[layer]
        st = usage_stats(u["counts"], u["weights"])
        n = n_slots[layer]
        out[f"coverage/layer{layer}"] = float(st["fraction_used"])
        out[f"best_coverage/layer{layer}"] = float((u["best"] > 0).sum()) / n
        out[f"kl_uniform/layer{layer}"] = float(
            st.get("kl_from_uniform_weighted", st["kl_from_uniform"])
        )
    return out


@register_metric(
    "slot_usage",
    metric_id="U1",
    stages=("during", "final", "posthoc"),
    needs_memory=True,
    inputs=("model", "heldout"),
)
def slot_usage(ctx) -> Dict[str, float]:
    """Memory slot coverage, best-slot coverage and KL from uniform per layer."""
    p = ctx.heldout_pass()
    return usage_keys(p.usage, p.n_slots)
