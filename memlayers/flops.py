"""Forward-pass FLOPs per token, whole model and per layer.

Convention: one multiply-add = 2 FLOPs. Additions that are not part of a
multiply-add (the top-k product's score sums) count 1 FLOP each. Not counted:
biases, LayerNorm / BatchNorm / RMSNorm, GELU, softmax, the top-k selections
themselves, embedding lookups. They are all O(d) per token and small next to
the matmuls.

Per block:
    attention   qkv + output projections        4 d^2          multiply-adds
                scores QK^T and the A.V sum     2 T d          multiply-adds
                (T = block_size, the full context, as in Kaplan et al. 2020;
                a causal mask halves the average, which is not modelled)
    dense FFN   two matmuls                     2 d h          multiply-adds
    PKM         query projection                d * 2 H dh     multiply-adds
                sub-key scores (2 halves)       H * 2 nk dh    multiply-adds
                top-k product                   H * k^2        additions
                value sum                       H * k * d      multiply-adds
    PEER        query projection                d * 2 H dk     multiply-adds
                sub-key scores (2 halves)       H * 2 nk dk    multiply-adds
                top-k product                   H * k^2        additions
                expert down + up                H * k * 2d     multiply-adds
Output head:    d * V multiply-adds.

H = memory heads, k = top-k per head, nk = sub-keys per half, dh / dk = key
dimension. PKM's keys are [heads, num_keys, 2, dim_head], so each half of the
query is a full dim_head long, and the query projection is d -> 2 * heads *
dim_head (product_key_memory 0.3.0); PEER's are the same shape with dim_key.
"""

from __future__ import annotations

import math
from dataclasses import asdict, is_dataclass
from typing import Any, Dict, Mapping

from .model import GPTConfig

__all__ = ["estimate_flops_per_token", "memory_layer_flops", "matched_dense_hidden"]

_PKM_DEFAULTS = dict(num_keys=256, topk=32, heads=4, dim_head=128)
_PEER_DEFAULTS = dict(num_experts=65_536, topk=32, heads=4, dim_key=128)


def _as_gpt_config(model_cfg: Any) -> GPTConfig:
    if isinstance(model_cfg, GPTConfig):
        return model_cfg
    if is_dataclass(model_cfg):
        model_cfg = asdict(model_cfg)
    return GPTConfig(**dict(model_cfg))


def attention_flops(d: int, T: int) -> int:
    return 2 * (4 * d * d + 2 * T * d)


def dense_ffn_flops(d: int, hidden: int) -> int:
    return 2 * (2 * d * hidden)


def memory_layer_flops(kind: str, d: int, memory: Mapping[str, Any]) -> Dict[str, int]:
    """FLOPs per token of one memory layer, broken into its four parts."""
    if kind == "pkm":
        m = {**_PKM_DEFAULTS, **{k: v for k, v in memory.items() if v is not None}}
        H, k, nk, dq = m["heads"], m["topk"], m["num_keys"], m["dim_head"]
        value = 2 * (H * k * d)
    elif kind == "peer":
        m = {**_PEER_DEFAULTS, **{k: v for k, v in memory.items() if v is not None}}
        H, k, dq = m["heads"], m["topk"], m["dim_key"]
        nk = math.isqrt(int(m["num_experts"]))
        if m.get("non_competing_scores"):
            k_read = 1  # PEER collapses the per-head top-k to 1; see memory.py
        else:
            k_read = k
        value = 2 * (H * k_read * 2 * d)
    else:
        raise ValueError(f"unknown memory kind {kind!r}")
    parts = {
        "query_projection": 2 * (d * 2 * H * dq),
        "subkey_scores": 2 * (H * 2 * nk * dq),
        "topk_product": H * k * k,
        "value_sum": value,
    }
    parts["total"] = sum(parts.values())
    return parts


def estimate_flops_per_token(model_cfg: Any) -> Dict[str, Any]:
    """Forward FLOPs per token: {'total', 'per_layer': [...], 'lm_head', ...}.

    `model_cfg` is a GPTConfig, or the `model` dict of a TrainConfig.
    """
    cfg = _as_gpt_config(model_cfg)
    d, T = cfg.n_embd, cfg.block_size
    layers = []
    for i, kind in enumerate(cfg.ffn_types):
        attn = attention_flops(d, T)
        if kind == "dense":
            hidden = cfg.dense_hidden(i)
            ffn = dense_ffn_flops(d, hidden)
            entry = {"layer": i, "kind": "dense", "ffn_hidden": hidden}
        else:
            parts = memory_layer_flops(kind, d, cfg.memory)
            ffn = parts["total"]
            entry = {"layer": i, "kind": kind, "ffn_parts": parts}
        entry.update({"attention": attn, "ffn": ffn, "total": attn + ffn})
        layers.append(entry)
    lm_head = 2 * d * cfg.vocab_size
    blocks = sum(l["total"] for l in layers)
    return {
        "total": blocks + lm_head,
        "blocks": blocks,
        "lm_head": lm_head,
        "per_layer": layers,
        "convention": "forward pass; multiply-add = 2 FLOPs; attention over the "
        "full block_size context; norms, activations, biases and top-k "
        "selection not counted",
    }


def matched_dense_hidden(
    d: int, target_ffn_flops: int, multiple: int = 64, tolerance: float = 0.10
) -> int:
    """Hidden width whose dense FFN FLOPs are within `tolerance` of the target.

    Keeps the standard 4*d when that already qualifies; otherwise the multiple
    of `multiple` closest to the exact match.
    """
    if (
        abs(dense_ffn_flops(d, 4 * d) - target_ffn_flops)
        <= tolerance * target_ffn_flops
    ):
        return 4 * d
    exact = target_ffn_flops / (4 * d)
    h = max(multiple, int(round(exact / multiple)) * multiple)
    if abs(dense_ffn_flops(d, h) - target_ffn_flops) > tolerance * target_ffn_flops:
        h = max(1, int(round(exact)))
    return h
