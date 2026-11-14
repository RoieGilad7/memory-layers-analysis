"""Discovery covariates, matched physical slot masks and tie-aware fact scoring."""

from collections import Counter
import math

import numpy as np
import torch


def slot_profiles(reads):
    """For each observed slot, count selections and mean ||weight * value(x)||."""
    counts, norm_sums = Counter(), Counter()
    for read in reads:
        norms = read.get("weighted_norms")
        if norms is None:
            values = (
                torch.as_tensor(read["vectors"]).detach().float().norm(dim=-1).tolist()
            )
            norms = [
                abs(float(w)) * v for w, v in zip(read["weights"], values, strict=True)
            ]
        for slot, norm in zip(read["ids"], norms, strict=True):
            slot = int(slot)
            counts[slot] += 1
            norm_sums[slot] += float(norm)
    return {i: (count, norm_sums[i] / count) for i, count in counts.items()}


def matched_masks(target, pool, profiles, controls, rng):
    """Uniformly shuffle eligible donors; find a distinct donor per target.

    Both read count and mean weighted output norm must be within a factor of
    two (zero matches only zero). This fixed caliper bounds imbalance. A
    missing disjoint perfect match makes the control unavailable. The samples
    can repeat and are counterfactual draws, not independent model seeds.
    """
    pool = sorted(set(pool).intersection(profiles).difference(target))
    if len(pool) < len(target) or any(i not in profiles for i in target):
        return []
    # Vectorized caliper test; same rule as max(x, y) <= 2 * min(x, y) per covariate.
    pool_arr = np.asarray([profiles[j] for j in pool], dtype=np.float64)
    choices = {}
    for i in target:
        x = np.asarray(profiles[i], dtype=np.float64)
        ok = np.all(np.maximum(pool_arr, x) <= 2 * np.minimum(pool_arr, x), axis=1)
        choices[i] = [pool[k] for k in np.flatnonzero(ok)]
        if not choices[i]:
            return []
    masks = []
    for _ in range(controls):
        for neighbors in choices.values():
            rng.shuffle(neighbors)
        donors = {}  # donor slot -> tested slot
        for start in sorted(target, key=lambda slot: len(choices[slot])):
            # Follow alternating edges to repair earlier assignments.
            queue = [start]
            parent = {}
            for owner in queue:
                free = None
                for donor in choices[owner]:
                    if donor in parent:
                        continue
                    parent[donor] = owner
                    if donor not in donors:
                        free = donor
                        break
                    queue.append(donors[donor])
                if free is not None:
                    break
            else:
                return []
            inverse = {owner: donor for donor, owner in donors.items()}
            while free is not None:
                owner = parent[free]
                donors[free] = owner
                free = inverse.get(owner)
        masks.append(tuple(sorted(donors)))
    return masks


def match_audit(target, masks, profiles):
    """Record exactly the matched masks applied and their pre-lesion covariates."""
    used = set(target).union(*(set(mask) for mask in masks))
    return {
        "matched_masks": [list(m) for m in masks],
        "discovery_profiles": {
            slot: (
                {
                    "read_count": profiles[slot][0],
                    "mean_weighted_output_norm": profiles[slot][1],
                }
                if slot in profiles
                else None
            )
            for slot in sorted(used)
        },
    }


def top1_credit(scores, answer):
    """Expected top-1 accuracy with uniform tie-breaking; all ties give chance."""
    scores = [float(s) for s in scores]
    if not scores or any(not math.isfinite(s) for s in scores):
        raise ValueError("Candidate scores must be finite log probabilities.")
    best = max(scores)
    return (1.0 / scores.count(best)) if scores[answer] == best else 0.0


def gold_margin(scores, answer):
    """Log-score advantage over the strongest incorrect continuation, in nats."""
    return float(scores[answer]) - max(
        float(s) for i, s in enumerate(scores) if i != answer
    )
