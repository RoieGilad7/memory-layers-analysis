"""Two fake datasets for step 1. No real text anywhere in this step.

(a) RandomTokenData  -- uniform random token ids. Nothing to learn, so the loss
    should sit at ln(vocab_size) (10.825 for 50257). This is the speed/memory
    benchmark workload and the control for the learning check.

(b) RepeatedChunkData -- each sequence is one random chunk of `chunk_len` tokens
    repeated to fill the context. Everything after the first chunk is perfectly
    predictable by copying from `chunk_len` positions back, so an induction head
    solves it and the loss MUST fall. The floor is set by the first chunk, which
    is still uniform random:

        loss_floor  ~=  (chunk_len / seq_len) * ln(n_distinct)

    With chunk_len=16, seq_len=512 and the full 50257 vocab that is ~0.34 nats,
    far below the 10.825 random-token level.

Batches are addressed by step index, not drawn from a stream: `get_batch(step)` is
a pure function of (seed, step). That makes data order exactly reproducible across
a checkpoint resume without storing any loader state.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional, Tuple

import torch

__all__ = ["RandomTokenData", "RepeatedChunkData", "build_dataset"]


class FakeDataset:
    """Common interface: get_batch(step, batch_size) -> (x, y) of [B, seq_len]."""

    vocab_size: int
    seq_len: int
    name: str = "fake"

    def _gen(self, step: int, micro: int) -> torch.Generator:
        g = torch.Generator()
        # mix in micro-step so gradient-accumulation micro-batches differ
        g.manual_seed((self.seed * 1_000_003 + step * 9_176 + micro) % (2**63 - 1))
        return g

    def get_batch(self, step: int, batch_size: int, micro: int = 0,
                  device: Optional[torch.device] = None) -> Tuple[torch.Tensor, torch.Tensor]:
        raise NotImplementedError

    def loss_floor(self) -> float:
        raise NotImplementedError


class RandomTokenData(FakeDataset):
    """(a) uniform random token ids -- unlearnable by construction."""

    name = "random"

    def __init__(self, vocab_size: int = 50257, seq_len: int = 512, seed: int = 1234):
        self.vocab_size, self.seq_len, self.seed = vocab_size, seq_len, seed

    def get_batch(self, step, batch_size, micro=0, device=None):
        g = self._gen(step, micro)
        buf = torch.randint(0, self.vocab_size, (batch_size, self.seq_len + 1),
                            generator=g, dtype=torch.long)
        x, y = buf[:, :-1], buf[:, 1:]
        if device is not None:
            x, y = x.to(device, non_blocking=True), y.to(device, non_blocking=True)
        return x, y

    def loss_floor(self) -> float:
        return math.log(self.vocab_size)


class RepeatedChunkData(FakeDataset):
    """(b) a random chunk repeated to fill the context -- a copy/induction task."""

    name = "repeat"

    def __init__(self, vocab_size: int = 50257, seq_len: int = 512, chunk_len: int = 16,
                 n_distinct: Optional[int] = None, seed: int = 1234):
        if chunk_len >= seq_len:
            raise ValueError("chunk_len must be shorter than seq_len")
        self.vocab_size, self.seq_len, self.chunk_len = vocab_size, seq_len, chunk_len
        # n_distinct restricts which ids may appear; None = the whole vocabulary
        self.n_distinct = n_distinct or vocab_size
        if self.n_distinct > vocab_size:
            raise ValueError("n_distinct cannot exceed vocab_size")
        self.seed = seed

    def get_batch(self, step, batch_size, micro=0, device=None):
        g = self._gen(step, micro)
        need = self.seq_len + 1
        reps = math.ceil(need / self.chunk_len)
        chunk = torch.randint(0, self.n_distinct, (batch_size, self.chunk_len),
                              generator=g, dtype=torch.long)
        buf = chunk.repeat(1, reps)[:, :need]
        x, y = buf[:, :-1], buf[:, 1:]
        if device is not None:
            x, y = x.to(device, non_blocking=True), y.to(device, non_blocking=True)
        return x, y

    def loss_floor(self) -> float:
        """Entropy that even a perfect model cannot remove: the first chunk only."""
        return (self.chunk_len / self.seq_len) * math.log(self.n_distinct)


def build_dataset(kind: str, vocab_size: int = 50257, seq_len: int = 512,
                  seed: int = 1234, **kw) -> FakeDataset:
    kind = kind.lower()
    if kind in ("random", "a", "uniform"):
        return RandomTokenData(vocab_size, seq_len, seed)
    if kind in ("repeat", "b", "chunks", "repeated_chunks"):
        return RepeatedChunkData(vocab_size, seq_len, seed=seed, **kw)
    raise ValueError(f"unknown dataset {kind!r}; expected 'random' or 'repeat'")
