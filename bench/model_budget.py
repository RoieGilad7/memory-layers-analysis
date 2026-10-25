"""Parameter and per-token FLOP accounting, to answer what a "tier size" should mean.

Parameter count and compute are badly decoupled in these models:
  - a memory layer adds tens of millions of parameters but almost no FLOPs, because
    only heads*topk value rows are touched per token;
  - the tied output projection (d_model x 50257) adds no *new* parameters at all, yet
    is the single largest matmul at tier-1 width.

So "a 20M-parameter model" does not pin down a time budget. This script prints both
columns side by side for every config.

    python bench/model_budget.py
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from memlayers.memory import PEERMemory, PKMMemory          # noqa: E402
from memlayers.model import GPT, GPTConfig                  # noqa: E402
from memlayers.train import load_config                     # noqa: E402


def per_token_macs(model: GPT) -> dict:
    """Multiply-accumulates per token for one forward pass. FLOPs ~= 2 x MACs,
    and a training step ~= 3 x forward."""
    c = model.config
    d, T, V, L = c.n_embd, c.block_size, c.vocab_size, c.n_layer

    attn_proj = 4 * d * d                      # qkv (3d^2) + output (d^2)
    # causal attention: each token attends to ~T/2 keys on average, scores + values
    attn_scores = 2 * (T / 2) * d
    dense_mlp = 8 * d * d                      # 4x expansion, two matmuls

    per_layer_attn = attn_proj + attn_scores
    total_attn = L * per_layer_attn

    dense_layers = sum(1 for t in c.ffn_types if t == "dense")
    total_dense_mlp = dense_layers * dense_mlp

    mem = 0
    mem_detail = {}
    for i, m in model.memory_layers.items():
        if isinstance(m, PKMMemory):
            dh, h, nk, k = (m.pkm.dim_head if hasattr(m.pkm, "dim_head")
                            else m.pkm.keys.shape[-1]), m.n_heads, m.num_keys, m.topk
            dh = m.pkm.keys.shape[-1]
            q = d * (dh * h * 2)               # query projection
            search = h * 2 * nk * dh           # dot every sub-key, both halves
            gather = h * k * d                 # weighted sum of the selected value rows
        else:
            dk, h, k = m.peer.keys.shape[-1], m.n_heads, m.topk
            nk = m.peer.num_keys
            q = d * (dk * h * 2)
            search = h * 2 * nk * dk
            gather = 2 * h * k * d             # down then up projection per expert
        sub = q + search + gather
        mem += sub
        mem_detail[i] = {"kind": m.kind, "query_proj": q, "key_search": search,
                         "value_gather": gather, "total": sub}

    head = d * V
    total = total_attn + total_dense_mlp + mem + head
    return {
        "attention": total_attn,
        "dense_mlp": total_dense_mlp,
        "memory": mem,
        "memory_detail": mem_detail,
        "lm_head": head,
        "total": total,
        "lm_head_share": head / total,
        "memory_share": mem / total,
    }


def main() -> int:
    configs = sorted((ROOT / "memlayers" / "configs").glob("*.yaml"))
    hdr = (f"{'config':14s} {'emb':>8s} {'backbone':>9s} {'memory':>9s} {'total':>9s} | "
           f"{'MAC/tok':>9s} {'attn':>8s} {'mlp':>8s} {'mem':>8s} {'head':>8s} "
           f"{'head%':>6s} {'mem%':>6s}")
    print(hdr)
    print("-" * len(hdr))
    rows = []
    for f in configs:
        cfg = load_config(f)
        m = GPT(GPTConfig(**cfg.model))
        pc = m.param_counts()
        fl = per_token_macs(m)
        rows.append((cfg.name, pc, fl))
        print(f"{cfg.name:14s} {pc['embedding']/1e6:7.2f}M {pc['backbone']/1e6:8.2f}M "
              f"{pc['memory_total']/1e6:8.2f}M {pc['total']/1e6:8.2f}M | "
              f"{fl['total']/1e6:8.2f}M {fl['attention']/1e6:7.2f}M "
              f"{fl['dense_mlp']/1e6:7.2f}M {fl['memory']/1e6:7.2f}M "
              f"{fl['lm_head']/1e6:7.2f}M {100*fl['lm_head_share']:5.1f}% "
              f"{100*fl['memory_share']:5.1f}%")

    print()
    print("Reading: `backbone` excludes embeddings and memory. MAC/tok is one forward "
          "pass;\na training step costs roughly 3x that (forward + backward).")
    print()
    for name, pc, fl in rows:
        if pc["memory_total"] == 0:
            continue
        print(f"{name}: memory holds {pc['memory_total']/1e6:.1f}M params "
              f"({100*pc['memory_total']/pc['total']:.0f}% of the model) but costs "
              f"{100*fl['memory_share']:.1f}% of forward MACs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
