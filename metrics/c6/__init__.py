"""C6. Entropy-based effective rank of value rows selected on held-out text."""

import torch
from ..u1 import selection_counts


def effective_rank(rows):
    """exp(H(sigma/sum(sigma))); undefined for an empty or all-zero table."""
    if rows.ndim != 2:
        raise ValueError("effective rank needs a matrix")
    if not rows.numel():
        return None
    # Use singular values directly so lower precision in a Gram matrix cannot
    # spuriously inflate the entropy of a nearly rank-deficient table.
    singular = torch.linalg.svdvals(rows.detach().to(device="cpu", dtype=torch.float64))
    singular = singular[singular > 0]
    if not len(singular):
        return None
    p = singular / singular.sum()
    return float(torch.exp(-torch.dot(p, p.log())))


def run(ctx):
    table = ctx.model.memory.value_table().detach()
    active = sorted(selection_counts(ctx.eval_reads))
    result = dict(active_rows=len(active), effective_rank=effective_rank(table[active]))
    rows = [["Active memory", len(active), result["effective_rank"]]]
    dense = getattr(ctx, "dense_matrix", None)
    if dense is not None:
        size = min(len(active), len(dense))
        gen = torch.Generator().manual_seed(ctx.seed)
        ids = torch.tensor(active, dtype=torch.long)[
            torch.randperm(len(active), generator=gen)[:size]
        ]
        dense_ids = torch.randperm(len(dense), generator=gen)[:size]
        result.update(
            dense_native_rank=effective_rank(dense),
            comparable_rows=size,
            memory_rank_at_comparable_rows=effective_rank(table[ids.to(table.device)]),
            dense_rank_at_comparable_rows=effective_rank(
                dense[dense_ids.to(dense.device)]
            ),
        )
        rows.extend(
            [
                ["Dense reference", len(dense), result["dense_native_rank"]],
                ["Memory sample", size, result["memory_rank_at_comparable_rows"]],
                ["Dense sample", size, result["dense_rank_at_comparable_rows"]],
            ]
        )
    return dict(
        title="Value matrix rank",
        result=result,
        columns=["Matrix", "Rows", "Effective rank"],
        rows=rows,
    )
