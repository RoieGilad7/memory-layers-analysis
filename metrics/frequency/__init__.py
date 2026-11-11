"""Attribute-only answer frequency in consumed training sequences."""

from collections import Counter, defaultdict
import numpy as np
from ..bundle import BLOCK_SIZE


def _exposures(root, tokens_seen, seed):
    import pyarrow.parquet as pq

    # Match Roie's PackedDataset: a full x window requires one extra target token.
    n_tokens = (root / "tokens/train.bin").stat().st_size // 2
    n_sequences = (n_tokens - 1) // BLOCK_SIZE
    epochs, tail = divmod(tokens_seen // BLOCK_SIZE, n_sequences)
    copies = pq.read_table(
        root / "tokens/train.idx.parquet", columns=["start", "person_id"]
    )
    copies = copies.filter(copies["person_id"].is_valid())
    blocks = copies["start"].to_numpy() // BLOCK_SIZE
    ids = copies["person_id"].to_pylist()
    available = blocks < n_sequences
    base = Counter(p for p, ok in zip(ids, available) if ok)
    counts = Counter({p: n * epochs for p, n in base.items()})
    if tail:
        partial = np.random.default_rng([seed, epochs]).permutation(n_sequences)[:tail]
        selected = np.isin(blocks, partial)
        counts.update(p for p, used in zip(ids, selected) if used)
    return counts


def popularity_baseline(corpus, *, tokens_seen, data_seed):
    """Rank candidates using only the checkpoint's consumed training biography counts."""
    if (
        type(tokens_seen) is not int
        or tokens_seen < 0
        or tokens_seen % BLOCK_SIZE
        or type(data_seed) is not int
        or data_seed < 0
    ):
        return dict(
            status="unavailable",
            reason="Require a nonnegative native data seed and a "
            "consumed token count divisible by 512.",
        )
    exposures = _exposures(corpus.root, tokens_seen, data_seed)
    counts = {attr: Counter() for attr in corpus.value_lists}
    for pid, copies in exposures.items():
        for attr, gold in corpus.people[pid]["facts"].items():
            counts[attr][gold] += copies
    ranks = {}
    for attr, values in corpus.value_lists.items():
        scores = np.array([counts[attr][v] for v in values], dtype=np.int64)
        ranks[attr] = {}
        for v, score in zip(values, scores):
            above, tied = np.count_nonzero(scores > score), np.count_nonzero(
                scores == score
            )
            rank = above + (tied + 1) / 2
            ranks[attr][v] = (rank, rank / len(values), float(above == 0) / tied)

    groups = defaultdict(list)
    for f in corpus.facts:
        groups[f["tier"] + "/" + f["role"]].append(
            ranks[f["attribute"]][f["true_value"]]
        )
    summary = {}
    for group, rows in sorted(groups.items()):
        rank, fraction, accuracy = np.mean(rows, axis=0).tolist()
        summary[group] = dict(
            prompts=len(rows),
            top1=accuracy,
            mean_rank=rank,
            mean_rank_fraction=fraction,
        )
    return dict(
        status="ok",
        method="Within each attribute, rank by biography copies actually "
        "consumed; award fractional credit and midrank for ties.",
        data_seed=data_seed,
        tokens_seen=tokens_seen,
        biography_copies=sum(exposures.values()),
        selected_people_exposures={
            p: exposures[p]
            for ids in corpus.selection["people_by_tier"].values()
            for p in ids
        },
        by_tier_role=summary,
    )


def run(ctx):
    tokens = (
        0
        if ctx.meta["data_v1"]["status"] == "initialization_only"
        else ctx.meta["tokens_seen"]
    )
    result = popularity_baseline(
        ctx.corpus, tokens_seen=tokens, data_seed=ctx.meta["data_v1"]["data_seed"]
    )
    rows = [
        [g, r["prompts"], r["top1"], r["mean_rank"]]
        for g, r in sorted(result.get("by_tier_role", {}).items())
    ]
    return dict(
        title="Answer-frequency baseline",
        columns=["Exposure / wording", "Prompts", "Top-1", "Mean rank"],
        status=result.get("reason", ""),
        rows=rows,
        result=result,
    )
