"""nanoGPT-style decoder whose per-layer FFN can be a dense MLP, a PKM, or a PEER layer.

Follows karpathy/nanoGPT: pre-LayerNorm blocks, causal self-attention, 4x GELU MLP,
weight-tied token embedding and output head, normal(0, 0.02) init with the residual
projections scaled by 1/sqrt(2 * n_layer).
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import torch
import torch.nn as nn
import torch.nn.functional as F

from .memory import MemoryLayer, build_memory

__all__ = ["GPTConfig", "GPT"]


@dataclass
class GPTConfig:
    vocab_size: int = 50257
    block_size: int = 512
    n_layer: int = 6
    n_head: int = 6
    n_embd: int = 384
    dropout: float = 0.0
    bias: bool = True
    tie_embeddings: bool = True
    # one entry per layer: "dense" | "pkm" | "peer". Shorthand: give `memory_layers`
    # and `memory_kind` instead and ffn_types is filled in.
    ffn_types: Optional[List[str]] = None
    memory_layers: tuple = ()
    memory_kind: str = "pkm"
    memory: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if self.ffn_types is None:
            kinds = ["dense"] * self.n_layer
            for i in self.memory_layers:
                if not 0 <= i < self.n_layer:
                    raise ValueError(f"memory layer {i} outside 0..{self.n_layer - 1}")
                kinds[i] = self.memory_kind
            self.ffn_types = kinds
        if len(self.ffn_types) != self.n_layer:
            raise ValueError(
                f"ffn_types has {len(self.ffn_types)} entries for {self.n_layer} layers")
        bad = set(self.ffn_types) - {"dense", "pkm", "peer"}
        if bad:
            raise ValueError(f"unknown ffn types {sorted(bad)}")


class CausalSelfAttention(nn.Module):
    def __init__(self, cfg: GPTConfig):
        super().__init__()
        assert cfg.n_embd % cfg.n_head == 0
        self.n_head = cfg.n_head
        self.n_embd = cfg.n_embd
        self.dropout = cfg.dropout
        self.c_attn = nn.Linear(cfg.n_embd, 3 * cfg.n_embd, bias=cfg.bias)
        self.c_proj = nn.Linear(cfg.n_embd, cfg.n_embd, bias=cfg.bias)
        self.resid_dropout = nn.Dropout(cfg.dropout)

    def forward(self, x):
        B, T, C = x.shape
        q, k, v = self.c_attn(x).split(self.n_embd, dim=2)
        shape = (B, T, self.n_head, C // self.n_head)
        q, k, v = (t.view(shape).transpose(1, 2) for t in (q, k, v))
        y = F.scaled_dot_product_attention(
            q, k, v, dropout_p=self.dropout if self.training else 0.0, is_causal=True)
        y = y.transpose(1, 2).contiguous().view(B, T, C)
        return self.resid_dropout(self.c_proj(y))


class MLP(nn.Module):
    """nanoGPT's dense FFN: 4x expansion, GELU."""

    def __init__(self, cfg: GPTConfig):
        super().__init__()
        self.c_fc = nn.Linear(cfg.n_embd, 4 * cfg.n_embd, bias=cfg.bias)
        self.gelu = nn.GELU()
        self.c_proj = nn.Linear(4 * cfg.n_embd, cfg.n_embd, bias=cfg.bias)
        self.dropout = nn.Dropout(cfg.dropout)

    def forward(self, x):
        return self.dropout(self.c_proj(self.gelu(self.c_fc(x))))


class Block(nn.Module):
    def __init__(self, cfg: GPTConfig, layer_idx: int):
        super().__init__()
        self.layer_idx = layer_idx
        self.ffn_type = cfg.ffn_types[layer_idx]
        self.ln_1 = nn.LayerNorm(cfg.n_embd, bias=cfg.bias)
        self.attn = CausalSelfAttention(cfg)
        self.ln_2 = nn.LayerNorm(cfg.n_embd, bias=cfg.bias)
        if self.ffn_type == "dense":
            self.mlp = MLP(cfg)
        else:
            # PKM and PEER both normalize their own input, but keeping ln_2 makes the
            # dense and memory variants differ in exactly one component.
            self.mlp = build_memory(self.ffn_type, dim=cfg.n_embd, **cfg.memory)

    @property
    def is_memory(self) -> bool:
        return self.ffn_type != "dense"

    def forward(self, x):
        x = x + self.attn(self.ln_1(x))
        return x + self.mlp(self.ln_2(x))


class GPT(nn.Module):
    def __init__(self, cfg: GPTConfig):
        super().__init__()
        self.config = cfg
        self.transformer = nn.ModuleDict(dict(
            wte=nn.Embedding(cfg.vocab_size, cfg.n_embd),
            wpe=nn.Embedding(cfg.block_size, cfg.n_embd),
            drop=nn.Dropout(cfg.dropout),
            h=nn.ModuleList([Block(cfg, i) for i in range(cfg.n_layer)]),
            ln_f=nn.LayerNorm(cfg.n_embd, bias=cfg.bias),
        ))
        self.lm_head = nn.Linear(cfg.n_embd, cfg.vocab_size, bias=False)
        if cfg.tie_embeddings:
            self.transformer.wte.weight = self.lm_head.weight

        self.apply(self._init_weights)
        # scaled init for the residual projections (nanoGPT / GPT-2 paper)
        for name, p in self.named_parameters():
            if name.endswith("c_proj.weight"):
                nn.init.normal_(p, mean=0.0, std=0.02 / math.sqrt(2 * cfg.n_layer))

    def _init_weights(self, module):
        if isinstance(module, nn.Linear):
            nn.init.normal_(module.weight, mean=0.0, std=0.02)
            if module.bias is not None:
                nn.init.zeros_(module.bias)
        elif isinstance(module, nn.Embedding):
            nn.init.normal_(module.weight, mean=0.0, std=0.02)

    # ---- memory-layer access -----------------------------------------------
    @property
    def memory_layers(self) -> Dict[int, MemoryLayer]:
        return {b.layer_idx: b.mlp for b in self.transformer.h if b.is_memory}

    def set_read_logging(self, flag: bool) -> None:
        for m in self.memory_layers.values():
            m.set_read_logging(flag)

    def set_mask_slots(self, spec, renormalize: Optional[bool] = None) -> None:
        """spec: {layer_idx: iterable_of_slot_ids}, or one iterable for every
        memory layer, or None to clear."""
        mems = self.memory_layers
        if spec is None:
            for m in mems.values():
                m.set_mask_slots(None, renormalize)
            return
        if not isinstance(spec, dict):
            spec = {i: spec for i in mems}
        for i, ids in spec.items():
            if i not in mems:
                raise KeyError(f"layer {i} is not a memory layer; have {sorted(mems)}")
            mems[i].set_mask_slots(ids, renormalize)

    def read_logs(self) -> Dict[int, Any]:
        return {i: m.last_read() for i, m in self.memory_layers.items()
                if m.last_read() is not None}

    def freeze_memory_keys(self) -> None:
        for m in self.memory_layers.values():
            m.freeze_keys()

    # ---- parameter accounting ----------------------------------------------
    def param_counts(self) -> Dict[str, int]:
        """Embedding / backbone / memory split.

        embedding: token + position tables. With tied embeddings the output head is
                   the same tensor and is counted once.
        memory:    memory keys + values (+ the memory layers' own query projections
                   and norms, reported separately as memory_other).
        backbone:  everything else -- attention, dense MLPs, layernorms.
        """
        mem_params = set()
        mem_keys = mem_vals = mem_other = 0
        for m in self.memory_layers.values():
            c = m.param_counts()
            mem_keys += c["keys"]
            mem_vals += c["values"]
            mem_other += c["other"]
            mem_params |= {id(p) for p in m.parameters()}

        emb = {id(self.transformer.wte.weight), id(self.transformer.wpe.weight)}
        emb_n = self.transformer.wte.weight.numel() + self.transformer.wpe.weight.numel()
        if not self.config.tie_embeddings:
            emb.add(id(self.lm_head.weight))
            emb_n += self.lm_head.weight.numel()

        backbone = 0
        seen = set()
        for p in self.parameters():
            if id(p) in seen:
                continue
            seen.add(id(p))
            if id(p) in emb or id(p) in mem_params:
                continue
            backbone += p.numel()

        total = emb_n + backbone + mem_keys + mem_vals + mem_other
        return {
            "embedding": emb_n,
            "backbone": backbone,
            "memory_keys": mem_keys,
            "memory_values": mem_vals,
            "memory_other": mem_other,
            "memory_total": mem_keys + mem_vals + mem_other,
            "non_embedding": total - emb_n,
            "total": total,
        }

    def forward(self, idx, targets=None):
        B, T = idx.shape
        if T > self.config.block_size:
            raise ValueError(f"sequence length {T} exceeds block_size "
                             f"{self.config.block_size}")
        pos = torch.arange(T, device=idx.device)
        x = self.transformer.drop(self.transformer.wte(idx) + self.transformer.wpe(pos))
        for block in self.transformer.h:
            x = block(x)
        x = self.transformer.ln_f(x)

        if targets is None:
            return self.lm_head(x[:, [-1], :]), None
        logits = self.lm_head(x)
        loss = F.cross_entropy(logits.reshape(-1, logits.size(-1)), targets.reshape(-1))
        return logits, loss
