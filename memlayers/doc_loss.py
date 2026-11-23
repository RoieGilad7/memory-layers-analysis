"""Phase 2: the same-document memory loss.

Each training window [B, T] holds pieces of documents separated by EOT tokens. Every
piece long enough is split into two halves; the memory-layer queries of a half are
averaged into one unit vector, and an InfoNCE loss over the batch asks each half to
be closest to the other half of its own piece:

    S = v @ v.T / tau, diagonal masked out, target(i) = i ^ 1

    find_halves(x, eot_id, min_piece_tokens) -> (half_id [B, T], n_halves)
    half_vectors(queries [B, T, D], half_id, n_halves) -> v [N, D]
    doc_loss(v [N, D], tau) -> (loss, {"halves": N, "gap": float | None})

All math is in fp32. find_halves is vectorized over the whole flattened batch (no
loop over rows or tokens).
"""

from __future__ import annotations

from typing import Tuple

import torch
import torch.nn.functional as F

__all__ = ["find_halves", "half_vectors", "doc_loss", "mean_stats"]


def _count(ids: torch.Tensor, n: int) -> torch.Tensor:
    """bincount via index_add_ (int64), which every backend we use supports."""
    out = torch.zeros(n, dtype=torch.long, device=ids.device)
    return out.index_add_(0, ids, torch.ones_like(ids))


def find_halves(
    x: torch.Tensor, eot_id: int, min_piece_tokens: int
) -> Tuple[torch.Tensor, int]:
    """Label every token with the id of the half it belongs to.

    A piece is a maximal run of non-EOT tokens inside one row; a row start also
    starts a piece. Pieces shorter than `min_piece_tokens`, and EOT tokens, get -1.
    For a kept piece of length L the first L // 2 tokens are one half and the rest
    the other. Half 2k and 2k + 1 are the two halves of kept piece k, so the partner
    of half i is i ^ 1.

    Returns (half_id: int64 [B, T] on x's device, n_halves: int).
    """
    if x.dim() != 2:
        raise ValueError(f"x must be [B, T], got shape {tuple(x.shape)}")
    if min_piece_tokens < 2:
        raise ValueError("min_piece_tokens must be at least 2 (both halves non-empty)")
    B, T = x.shape
    tok = ~(x == eot_id)  # [B, T] real (non-EOT) tokens
    prev_tok = torch.zeros_like(tok)
    prev_tok[:, 1:] = tok[:, :-1]  # column 0 has no predecessor: a row start
    start = (tok & ~prev_tok).reshape(-1)
    flat_tok = tok.reshape(-1)

    n_pieces = int(start.sum())
    half_id = torch.full((B * T,), -1, dtype=torch.long, device=x.device)
    if n_pieces == 0:
        return half_id.reshape(B, T), 0

    # piece id of every token (only meaningful where flat_tok)
    piece = torch.cumsum(start.long(), 0) - 1
    pos_all = torch.arange(B * T, device=x.device)
    start_pos = pos_all[start]  # [n_pieces] flat index of each piece's first token
    piece_t = piece[flat_tok]
    lengths = _count(piece_t, n_pieces)
    keep = lengths >= min_piece_tokens
    n_kept = int(keep.sum())
    if n_kept == 0:
        return half_id.reshape(B, T), 0
    rank = torch.cumsum(keep.long(), 0) - 1  # index among kept pieces

    pos_in_piece = pos_all[flat_tok] - start_pos[piece_t]
    second = (pos_in_piece >= (lengths[piece_t] // 2)).long()
    vals = torch.where(keep[piece_t], 2 * rank[piece_t] + second, -1)
    half_id[flat_tok] = vals
    return half_id.reshape(B, T), 2 * n_kept


def half_vectors(
    queries: torch.Tensor, half_id: torch.Tensor, n_halves: int
) -> torch.Tensor:
    """Mean query of each half, L2-normalized. queries [B, T, D] -> [n_halves, D] fp32."""
    D = queries.shape[-1]
    q = queries.reshape(-1, D).float()
    hid = half_id.reshape(-1).to(q.device)
    sel = hid >= 0
    idx = hid[sel]
    sums = torch.zeros(n_halves, D, dtype=torch.float32, device=q.device).index_add(
        0, idx, q[sel]
    )
    counts = _count(idx, n_halves).clamp_min(1).to(torch.float32)
    return F.normalize(sums / counts[:, None], dim=-1)


def doc_loss(v: torch.Tensor, tau: float) -> Tuple[torch.Tensor, dict]:
    """InfoNCE over the halves: each half's positive is its partner (i ^ 1).

    Returns (loss, stats) where stats = {"halves": N, "gap": float | None}; gap is the
    mean cosine to the partner minus the mean cosine to every other non-self,
    non-partner half. With fewer than 2 pieces (N < 4) the loss is a zero that stays
    attached to the graph and gap is None.
    """
    v = v.float()
    N = int(v.shape[0])
    if N < 4:
        return v.sum() * 0.0, {"halves": N, "gap": None}
    if N % 2:
        raise ValueError(f"n_halves must be even, got {N}")
    cos = v @ v.T
    eye = torch.eye(N, dtype=torch.bool, device=v.device)
    S = (cos / tau).masked_fill(eye, float("-inf"))
    target = torch.arange(N, device=v.device) ^ 1
    loss = F.cross_entropy(S, target)

    with torch.no_grad():
        c = cos.detach()
        partner = c[torch.arange(N, device=v.device), target]
        others = (c.sum(1) - c.diagonal() - partner) / (N - 2)
        gap = float((partner - others).mean())
    return loss, {"halves": N, "gap": gap}


def mean_stats(stats: list) -> dict:
    """Average doc_loss stats over micro-batches, ignoring those with gap None."""
    good = [s for s in stats if s.get("gap") is not None]
    if not good:
        return {"halves": None, "gap": None}
    return {
        "halves": sum(s["halves"] for s in good) / len(good),
        "gap": sum(s["gap"] for s in good) / len(good),
    }
