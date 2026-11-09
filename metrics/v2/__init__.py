"""V2. Concentration, cancellation and cosine similarity of weighted slot vectors."""

from collections import defaultdict
import math
import random

import numpy as np


def composition(reads, seed):
    # Only unit vectors and slot/bin indices are retained for the control pool.
    # Pairwise products are calculated in blocks, including for multi-head PKMs.
    widths = {r["vectors"].shape[1] for r in reads}
    if len(widths) > 1:
        raise ValueError("Inconsistent memory value dimensions")
    limit = sum(len(r["ids"]) for r in reads)
    units = np.empty((limit, next(iter(widths), 0)), dtype=np.float64)
    slots = np.empty(limit, dtype=np.int64)
    groups = np.empty(limit, dtype=np.int32)
    bounds = []
    pool = defaultdict(list)
    used = contributing = 0
    top1 = top2 = retention = 0.0
    for r in reads:
        vectors = r["vectors"].detach().cpu().double().numpy()
        norms = np.linalg.norm(vectors, axis=1)
        weights = np.asarray(r["weights"])
        mass = weights * norms
        total = mass.sum()
        if total > 0:
            shares = np.sort(mass)
            top1 += shares[-1] / total
            top2 += shares[-2:].sum() / total
            retention += np.linalg.norm(weights @ vectors) / total
            contributing += 1
        start = used
        for slot, vec, norm, size in zip(r["ids"], vectors, norms, mass, strict=True):
            if size == 0:
                continue
            group = math.floor(math.log(norm) / math.log(1.1))
            units[used] = vec / norm
            slots[used], groups[used] = slot, group
            pool[group].append(used)
            used += 1
        bounds.append((start, used))

    cosine_sum = paired_sum = control_sum = 0.0
    pairs = matched = 0
    rng = random.Random(seed)
    for start, end in bounds:
        left, right = np.triu_indices(end - start, 1)
        left += start
        right += start
        for offset in range(0, len(left), 1024):
            a, b = left[offset : offset + 1024], right[offset : offset + 1024]
            distinct = slots[a] != slots[b]
            a, b = a[distinct], b[distinct]
            obs = np.einsum("ij,ij->i", units[a], units[b])
            pairs += len(obs)
            cosine_sum += float(obs.sum())
            # Sampling donors in pair order preserves the original seeded null.
            donor_a, donor_b, kept = [], [], []
            for i, (group_a, group_b) in enumerate(
                zip(groups[a].tolist(), groups[b].tolist())
            ):
                for _ in range(32):
                    u = rng.choice(pool[group_a])
                    v = rng.choice(pool[group_b])
                    if slots[u] != slots[v]:
                        donor_a.append(u)
                        donor_b.append(v)
                        kept.append(i)
                        break
            if kept:
                matched += len(kept)
                paired_sum += float(obs[kept].sum())
                control_sum += float(
                    np.einsum("ij,ij->", units[donor_a], units[donor_b])
                )
    return dict(
        tokens=len(reads),
        nonzero_reads=contributing,
        top1_share=top1 / contributing if contributing else None,
        top2_share=top2 / contributing if contributing else None,
        resultant_over_sum_norms=retention / contributing if contributing else None,
        pairs=pairs,
        matched_pairs=matched,
        mean_cosine=cosine_sum / pairs if pairs else None,
        matched_mean_cosine=control_sum / matched if matched else None,
        cosine_excess=(paired_sum - control_sum) / matched if matched else None,
    )


def run(ctx):
    result = {}
    rows = []
    for cohort, label in (("text", "Subject text"), ("fact", "Fact probes")):
        reads = [r for r in ctx.eval_reads if r.get("cohort", "text") == cohort]
        data = composition(reads, ctx.seed)
        result[cohort] = data
        rows.append(
            [
                label,
                data["top1_share"],
                data["top2_share"],
                data["resultant_over_sum_norms"],
                data["mean_cosine"],
                data["matched_mean_cosine"],
                data["cosine_excess"],
                data["matched_pairs"],
            ]
        )
    return dict(
        title="Slot contributions",
        result=result,
        columns=[
            "Cohort",
            "Top-1 share",
            "Top-2 share",
            "Resultant / sum of norms",
            "Mean cosine",
            "Control cosine",
            "Paired excess",
            "Matched pairs",
        ],
        rows=rows,
    )
