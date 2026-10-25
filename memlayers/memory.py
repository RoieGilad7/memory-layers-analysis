"""Thin wrappers around product-key-memory (PKM) and PEER-pytorch with one common
interface, so model.py can drop either one in place of a dense FFN.

Both wrappers expose:

    forward(x)                -> Tensor, same shape as x
    last_read()               -> MemoryRead(indices, weights) | None
    set_read_logging(flag)
    set_mask_slots(ids)       -> disable slots AFTER the top-k search
    key_parameters() / value_parameters()
    n_slots / n_heads / topk

Read-out is done with forward hooks on the inner module rather than by patching the
installed packages (see reports/step0_access_report.md section 6). The two packages
need different hooks:

  PKM  -- `value_indices` and the gate weights `attn` are both passed to
          `pkm.values` (an nn.EmbeddingBag), so one pre-hook with kwargs gets both.
  PEER -- only the indices pass through `weight_down_embed`; the scores never do.
          The post-activation scores are picked up with a second hook on
          `peer.score_activation`. Hook order within one forward is
          weight_down_embed (pre) then score_activation (forward), verified.

Masking reuses the same hooks: a pre-hook may return replacement inputs, and a
forward hook may return a replacement output, so the gate weights of masked slots
are zeroed in place. The top-k search itself is untouched, which is the point --
a masked slot is not replaced by the next-best one.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Iterator, Optional, Sequence

import torch
import torch.nn as nn

from PEER_pytorch import PEER as _PEER
from product_key_memory import PKM as _PKM

__all__ = ["MemoryRead", "MemoryLayer", "PKMMemory", "PEERMemory",
           "QueryBatchNorm", "build_memory"]

_EPS = 1e-9


@dataclass
class MemoryRead:
    """One forward pass worth of read log.

    indices: int64 [batch, seq, heads, topk] -- which slots each token read
    weights: float  [batch, seq, heads, topk] -- the gate weight each slot got,
             AFTER masking, i.e. exactly what multiplied the value rows
    """
    indices: torch.Tensor
    weights: torch.Tensor

    @property
    def shape(self):
        return tuple(self.indices.shape)

    def to(self, *a, **k) -> "MemoryRead":
        return MemoryRead(self.indices.to(*a, **k), self.weights.to(*a, **k))


class QueryBatchNorm(nn.Module):
    """BatchNorm over the query FEATURE dimension, as in Lample et al. 2019 (sec 3.2).

    Replaces product-key-memory's own `MaskedBatchNorm1D`, which is broken in
    v0.3.0: it hands a 3-D tensor of shape [(b p h), t, d] straight to
    nn.BatchNorm1d(dim_head), so BatchNorm treats the SEQUENCE dim as channels and
    raises `running_mean should contain 512 elements not 128`. Flattening the
    leading dims first normalizes over the feature dim across all tokens in the
    batch, which is what the paper describes.

    `mask` is accepted because PKM.forward passes `mask=input_mask` on this path.
    """

    def __init__(self, dim_head: int):
        super().__init__()
        self.bn = nn.BatchNorm1d(dim_head)

    def forward(self, x: torch.Tensor, mask: Optional[torch.Tensor] = None) -> torch.Tensor:
        d = x.shape[-1]
        if mask is None:
            return self.bn(x.reshape(-1, d)).reshape(x.shape)
        # x is [(b p h), t, d] and mask is [b, t]; normalize over real tokens only
        bph, t, _ = x.shape
        b = mask.shape[0]
        m = mask.reshape(b, 1, t).expand(b, bph // b, t).reshape(bph, t)
        out = x.clone()
        sel = x[m]
        if sel.numel():
            out[m] = self.bn(sel)
        return out


class MemoryLayer(nn.Module):
    """Common interface for the memory FFN replacements."""

    kind: str = "?"

    def __init__(self) -> None:
        super().__init__()
        self._log_reads = False
        self._last: Optional[MemoryRead] = None
        self.renormalize_after_mask = False
        # analysis-time tool, deliberately not part of the checkpoint
        self.register_buffer("slot_mask", None, persistent=False)

    # ---- read logging -------------------------------------------------------
    def set_read_logging(self, flag: bool) -> None:
        self._log_reads = bool(flag)
        if not flag:
            self._last = None

    @property
    def read_logging(self) -> bool:
        return self._log_reads

    def last_read(self) -> Optional[MemoryRead]:
        return self._last

    def _capture_needed(self) -> bool:
        return self._log_reads or self.slot_mask is not None

    # ---- slot masking -------------------------------------------------------
    def set_mask_slots(self, slot_ids: Optional[Iterable[int]],
                       renormalize: Optional[bool] = None) -> None:
        """Disable `slot_ids` after the top-k search. None or empty clears the mask.

        An empty mask is cleared rather than kept as an all-False tensor so that
        the masked path is bit-identical to the unmasked one.
        """
        if renormalize is not None:
            self.renormalize_after_mask = bool(renormalize)
        if slot_ids is None:
            self.slot_mask = None
            return
        ids = torch.as_tensor(sorted({int(i) for i in slot_ids}), dtype=torch.long)
        if ids.numel() == 0:
            self.slot_mask = None
            return
        if int(ids.max()) >= self.n_slots or int(ids.min()) < 0:
            raise ValueError(
                f"slot ids must be in [0, {self.n_slots}); got "
                f"[{int(ids.min())}, {int(ids.max())}]")
        mask = torch.zeros(self.n_slots, dtype=torch.bool)
        mask[ids] = True
        self.slot_mask = mask.to(self._device_hint())
        self._masked_ids = ids

    @property
    def masked_slot_ids(self) -> torch.Tensor:
        if self.slot_mask is None:
            return torch.empty(0, dtype=torch.long)
        return self.slot_mask.nonzero(as_tuple=True)[0].cpu()

    def _device_hint(self) -> torch.device:
        return next(self.parameters()).device

    def _apply_mask(self, indices: torch.Tensor, weights: torch.Tensor) -> torch.Tensor:
        """Zero the weights of masked slots. `weights` keeps its autograd history, so
        masked slots receive no gradient either."""
        if self.slot_mask is None:
            return weights
        mask = self.slot_mask
        if mask.device != indices.device:
            mask = mask.to(indices.device)
            self.slot_mask = mask
        off = mask[indices]
        weights = weights.masked_fill(off, 0.0)
        if self.renormalize_after_mask:
            # rescale the surviving weights of each head back to sum 1
            total = weights.sum(dim=-1, keepdim=True)
            weights = weights / total.clamp_min(_EPS)
        return weights

    # ---- parameter groups ---------------------------------------------------
    def key_parameters(self) -> Iterator[nn.Parameter]:
        raise NotImplementedError

    def value_parameters(self) -> Iterator[nn.Parameter]:
        raise NotImplementedError

    def other_parameters(self) -> Iterator[nn.Parameter]:
        special = {id(p) for p in self.key_parameters()} | {id(p) for p in self.value_parameters()}
        for p in self.parameters():
            if id(p) not in special:
                yield p

    def freeze_keys(self) -> None:
        for p in self.key_parameters():
            p.requires_grad_(False)

    def param_counts(self) -> dict:
        keys = sum(p.numel() for p in self.key_parameters())
        vals = sum(p.numel() for p in self.value_parameters())
        other = sum(p.numel() for p in self.other_parameters())
        return {"keys": keys, "values": vals, "other": other, "total": keys + vals + other}

    # ---- sizes --------------------------------------------------------------
    @property
    def n_slots(self) -> int:
        raise NotImplementedError

    @property
    def n_heads(self) -> int:
        raise NotImplementedError

    @property
    def topk(self) -> int:
        raise NotImplementedError

    @property
    def reads_per_token(self) -> int:
        return self.n_heads * self.topk


class PKMMemory(MemoryLayer):
    """product-key-memory PKM as an FFN replacement.

    `num_keys` is the number of sub-keys per half, so the slot count is num_keys**2.
    """

    kind = "pkm"

    def __init__(self, dim: int, num_keys: int = 256, topk: int = 32, heads: int = 4,
                 dim_head: int = 128, query_batchnorm: bool = True,
                 freeze_keys: bool = False, value_dropout: float = 0.0,
                 non_competitive_gates: bool = False,
                 mask_slots: Optional[Iterable[int]] = None,
                 renormalize_after_mask: bool = False) -> None:
        super().__init__()
        self.pkm = _PKM(
            dim=dim, heads=heads, dim_head=dim_head, num_keys=num_keys, topk=topk,
            # use_layernorm=False selects the BatchNorm-on-query path of Lample et al.
            use_layernorm=not query_batchnorm,
            value_dropout=value_dropout,
            non_competitive_gates=non_competitive_gates,
        )
        self.query_batchnorm = query_batchnorm
        if query_batchnorm:
            # swap in a working implementation; see QueryBatchNorm's docstring
            self.pkm.norm = QueryBatchNorm(dim_head)
        if freeze_keys:
            self.freeze_keys()
        self.set_mask_slots(mask_slots, renormalize_after_mask)

        self._hook = self.pkm.values.register_forward_pre_hook(
            self._values_pre_hook, with_kwargs=True)

    # PKM hands both tensors to its EmbeddingBag, so one hook does read-out and masking
    def _values_pre_hook(self, module, args, kwargs):
        indices = args[0]
        weights = kwargs.get("per_sample_weights")
        if weights is None:                      # concat_values_and_combine=True path
            if self._log_reads:
                self._last = MemoryRead(
                    indices.detach().reshape(self._b, -1, self.n_heads, self.topk),
                    torch.ones_like(indices, dtype=torch.float32).reshape(
                        self._b, -1, self.n_heads, self.topk))
            return None

        # [(b t), (h k)] -> [(b t), h, k] so masking and renorm act per head
        bt, hk = weights.shape
        h, k = self.n_heads, self.topk
        if self.slot_mask is not None:
            idx3 = indices.reshape(bt, h, k)
            w3 = self._apply_mask(idx3, weights.reshape(bt, h, k))
            weights = w3.reshape(bt, hk)
            kwargs = {**kwargs, "per_sample_weights": weights}

        if self._log_reads:
            self._last = MemoryRead(
                indices.detach().reshape(self._b, -1, h, k),
                weights.detach().reshape(self._b, -1, h, k))
        return (args, kwargs) if self.slot_mask is not None else None

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        self._b = x.shape[0]            # the hook needs it to unflatten (b t)
        if not self._capture_needed():
            self._last = None
        return self.pkm(x)

    def key_parameters(self):
        yield self.pkm.keys

    def value_parameters(self):
        yield self.pkm.values.weight

    @property
    def n_slots(self) -> int:
        return int(self.pkm.num_memories)

    @property
    def n_heads(self) -> int:
        return int(self.pkm.heads)

    @property
    def topk(self) -> int:
        return int(self.pkm.topk)

    @property
    def num_keys(self) -> int:
        return int(self.pkm.num_keys)


class PEERMemory(MemoryLayer):
    """PEER-pytorch PEER as an FFN replacement.

    `non_competing_scores` defaults to False here, the opposite of the package
    default. With the package default (True) PEER sets
    num_experts_per_head_topk = 1, so only `heads` experts fire per token instead
    of `heads * num_experts_per_head` -- 32x sparser than intended. See
    reports/step0_access_report.md section 6.2.
    """

    kind = "peer"

    def __init__(self, dim: int, num_experts: int = 65_536, topk: int = 32,
                 heads: int = 4, dim_key: int = 128, pre_rmsnorm: bool = True,
                 non_competing_scores: bool = False, freeze_keys: bool = False,
                 dropout: float = 0.0, separate_embed_per_head: bool = False,
                 mask_slots: Optional[Iterable[int]] = None,
                 renormalize_after_mask: bool = False) -> None:
        super().__init__()
        self.peer = _PEER(
            dim=dim, heads=heads, num_experts=num_experts,
            num_experts_per_head=topk, dim_key=dim_key, pre_rmsnorm=pre_rmsnorm,
            non_competing_scores=non_competing_scores, dropout=dropout,
            separate_embed_per_head=separate_embed_per_head,
        )
        self.non_competing_scores = non_competing_scores
        if non_competing_scores and topk > 1:
            # not an error, but it silently changes the experiment
            import warnings
            warnings.warn(
                f"PEER built with non_competing_scores=True: per-head top-k collapses "
                f"to 1 expert, not {topk}. reads_per_token will be {heads}, not "
                f"{heads * topk}.", stacklevel=2)
        if freeze_keys:
            self.freeze_keys()
        self.set_mask_slots(mask_slots, renormalize_after_mask)

        # indices come through weight_down_embed, scores do not -- two hooks needed
        self._idx_hook = self.peer.weight_down_embed.register_forward_pre_hook(
            self._down_pre_hook)
        self._score_hook = self.peer.score_activation.register_forward_hook(
            self._score_hook_fn)

    def _down_pre_hook(self, module, args):
        if self._capture_needed():
            self._pending_indices = args[0].detach()
        else:
            self._pending_indices = None
        return None

    def _score_hook_fn(self, module, args, output):
        """`output` is the post-activation gate weight, [b, n, h, k]."""
        idx = getattr(self, "_pending_indices", None)
        if idx is None:
            return None
        weights = output
        if self.slot_mask is not None:
            weights = self._apply_mask(idx, weights)
        if self._log_reads:
            self._last = MemoryRead(idx, weights.detach())
        return weights if self.slot_mask is not None else None

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        if not self._capture_needed():
            self._last = None
        self._pending_indices = None
        return self.peer(x)

    def key_parameters(self):
        yield self.peer.keys

    def value_parameters(self):
        yield self.peer.weight_down_embed.weight
        yield self.peer.weight_up_embed.weight

    @property
    def n_slots(self) -> int:
        n = int(self.peer.num_experts)
        return n * self.n_heads if self.peer.separate_embed_per_head else n

    @property
    def n_heads(self) -> int:
        return int(self.peer.heads)

    @property
    def topk(self) -> int:
        return int(self.peer.num_experts_per_head_topk)


def build_memory(kind: str, dim: int, **kw) -> MemoryLayer:
    kind = kind.lower()
    if kind == "pkm":
        return PKMMemory(dim=dim, **kw)
    if kind == "peer":
        return PEERMemory(dim=dim, **kw)
    raise ValueError(f"unknown memory kind {kind!r}; expected 'pkm' or 'peer'")
