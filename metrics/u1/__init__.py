"""U1. Coverage and concentration of physical memory-slot reads."""

from collections import Counter
import math


def text_reads(reads):
    return (r for r in reads if r.get("cohort", "text") == "text")


def selection_counts(reads):
    return Counter(slot for r in text_reads(reads) for slot in r["ids"])


def run(ctx):
    reads = list(text_reads(ctx.eval_reads))
    capacity = ctx.model.memory.num_slots
    if capacity < 1:
        raise ValueError("Memory capacity must be positive")
    counts = selection_counts(reads)
    total = sum(counts.values())
    entropy = -sum((n / total) * math.log2(n / total) for n in counts.values())
    top = {r["ids"][0] for r in reads if len(r["ids"])}
    kl = math.log2(capacity) - entropy if total else None
    data = dict(
        tokens=len(reads),
        selections=total,
        capacity=capacity,
        covered=len(counts),
        coverage=len(counts) / capacity,
        top1_coverage=len(top) / capacity,
        kl_to_uniform_bits=kl,
    )
    return dict(
        title="Slot utilization",
        status=(
            "Coverage depends on the number of slice tokens. Compare it with the "
            "training read log (readlog/), not with the training-check threshold."
        ),
        result=data,
        columns=[
            "Active slots",
            "Total slots",
            "Selected (%)",
            "Top-ranked (%)",
            "KL to uniform (bits)",
        ],
        rows=[
            [
                len(counts),
                capacity,
                100 * data["coverage"],
                100 * data["top1_coverage"],
                kl,
            ]
        ],
    )
