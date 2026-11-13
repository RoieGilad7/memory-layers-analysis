"""Cluster bootstrap intervals for slice-level means.

Facts from one person, and tokens from one document, are not independent. The
intervals therefore resample whole clusters (people, documents or facts) with
replacement and report percentile bounds.
"""

from __future__ import annotations

from collections import defaultdict
import random


def cluster_bootstrap(values, clusters, *, seed=0, resamples=1000, alpha=0.05):
    """Mean of `values` and a percentile CI from resampling `clusters`.

    values[i] belongs to clusters[i]. The statistic is the mean over all
    resampled items, so a cluster's weight is its number of items.
    """
    values = [float(v) for v in values]
    if len(values) != len(clusters):
        raise ValueError("values and clusters must have the same length")
    if not values:
        return dict(mean=None, lo=None, hi=None, n=0, clusters=0)
    groups = defaultdict(list)
    for v, c in zip(values, clusters):
        groups[c].append(v)
    keys = sorted(groups, key=str)
    sums = [sum(groups[k]) for k in keys]
    sizes = [len(groups[k]) for k in keys]
    mean = sum(values) / len(values)
    if len(keys) < 2:
        return dict(mean=mean, lo=None, hi=None, n=len(values), clusters=len(keys))
    rng = random.Random(seed)
    stats = []
    for _ in range(resamples):
        picks = [rng.randrange(len(keys)) for _ in keys]
        stats.append(sum(sums[i] for i in picks) / sum(sizes[i] for i in picks))
    stats.sort()
    lo = stats[int((alpha / 2) * (resamples - 1))]
    hi = stats[int((1 - alpha / 2) * (resamples - 1))]
    return dict(mean=mean, lo=lo, hi=hi, n=len(values), clusters=len(keys))


def ratio_bootstrap(numerators, denominators, *, seed=0, resamples=1000, alpha=0.05):
    """sum(numerators) / sum(denominators) with a CI from resampling the pairs.

    Used for token-weighted document NLL, where each document contributes its
    NLL sum and its token count.
    """
    pairs = [
        (float(a), float(b)) for a, b in zip(numerators, denominators, strict=True)
    ]
    if not pairs or sum(b for _, b in pairs) <= 0:
        return dict(value=None, lo=None, hi=None, n=len(pairs))
    value = sum(a for a, _ in pairs) / sum(b for _, b in pairs)
    if len(pairs) < 2:
        return dict(value=value, lo=None, hi=None, n=len(pairs))
    rng = random.Random(seed)
    stats = []
    for _ in range(resamples):
        draw = [pairs[rng.randrange(len(pairs))] for _ in pairs]
        stats.append(sum(a for a, _ in draw) / sum(b for _, b in draw))
    stats.sort()
    return dict(
        value=value,
        lo=stats[int((alpha / 2) * (resamples - 1))],
        hi=stats[int((1 - alpha / 2) * (resamples - 1))],
        n=len(pairs),
    )
