"""The training data loader -- memmapped sequences out of a packed .bin.

    from data.loader import PackedDataset
    ds = PackedDataset("data/v1/tokens/train.bin", block_size=512, seed=1337)
    x, y = ds.get_batch(step, batch_size=32)      # (32, 512) each

Sequence `s` covers tokens `[s*512, s*512 + 513)`: `x` is the first 512 and `y`
is the same window shifted by one, so the last target is the first token of the
next sequence and no token is wasted as an unpredicted tail.

Order is a permutation of the sequence indices drawn from the run seed, so the
same seed always gives the same order and a different seed gives a different
one. Position is explicit state, saved into checkpoints, so a resumed run
continues exactly where it stopped -- `state_dict()` / `load_state_dict()`.

Interface-compatible with `memlayers.data_fake`: `get_batch(step, batch_size,
micro, device)`. The `step` argument is ignored for ordering (position is what
advances), but passing it keeps the call sites identical.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import torch

__all__ = ["PackedDataset", "iter_document_windows"]

TOKEN_DTYPE = np.uint16


class PackedDataset:
    """Batches of (B, block_size) from a packed uint16 token file."""

    name = "real"

    def __init__(self, path: str | Path, block_size: int = 512,
                 seed: int = 1337, vocab_size: int = 50257,
                 drop_last_sequence: bool = True):
        self.path = Path(path)
        if not self.path.exists():
            raise FileNotFoundError(
                f"{self.path} not found. Build it with `python -m data.pack` or "
                "fetch the frozen bundle with `python -m data.fetch`.")
        self.block_size = int(block_size)
        self.seed = int(seed)
        self.vocab_size = int(vocab_size)
        self.tokens = np.memmap(self.path, dtype=TOKEN_DTYPE, mode="r")
        self.n_tokens = int(self.tokens.size)

        # a sequence needs block_size + 1 tokens, so the last one is dropped
        # unless the file happens to carry the extra target token
        n = self.n_tokens // self.block_size
        if drop_last_sequence and n * self.block_size + 1 > self.n_tokens:
            n -= 1
        if n <= 0:
            raise ValueError(
                f"{self.path}: {self.n_tokens} tokens is not even one "
                f"{self.block_size}-token sequence plus its target")
        self.n_sequences = n

        self.position = 0
        self._epoch = -1
        self._perm: Optional[np.ndarray] = None
        self._set_epoch(0)

    # -- ordering ----------------------------------------------------------
    def _set_epoch(self, epoch: int) -> None:
        """One permutation per epoch, keyed by (seed, epoch)."""
        if epoch == self._epoch:
            return
        rng = np.random.default_rng([self.seed, epoch])
        self._perm = rng.permutation(self.n_sequences)
        self._epoch = epoch

    def sequence_order(self, epoch: int = 0) -> np.ndarray:
        self._set_epoch(epoch)
        assert self._perm is not None
        return self._perm

    def _next_indices(self, k: int) -> np.ndarray:
        """`k` sequence indices from the current position, crossing epochs."""
        out = np.empty(k, dtype=np.int64)
        filled = 0
        while filled < k:
            epoch, offset = divmod(self.position, self.n_sequences)
            self._set_epoch(epoch)
            take = min(k - filled, self.n_sequences - offset)
            out[filled:filled + take] = self._perm[offset:offset + take]
            self.position += take
            filled += take
        return out

    # -- batches -----------------------------------------------------------
    def get_batch(self, step: int = 0, batch_size: int = 8, micro: int = 0,
                  device: Optional[torch.device] = None
                  ) -> Tuple[torch.Tensor, torch.Tensor]:
        idx = self._next_indices(batch_size)
        b = self.block_size
        x = np.empty((batch_size, b), dtype=np.int64)
        y = np.empty((batch_size, b), dtype=np.int64)
        for row, s in enumerate(idx):
            a = int(s) * b
            window = np.asarray(self.tokens[a:a + b + 1], dtype=np.int64)
            x[row] = window[:b]
            y[row] = window[1:b + 1]
        xt = torch.from_numpy(x)
        yt = torch.from_numpy(y)
        if device is not None:
            xt, yt = xt.to(device, non_blocking=True), yt.to(device, non_blocking=True)
        return xt, yt

    def loss_floor(self) -> float:
        """Unknown for real text; reported as nan so logs stay uniform."""
        return float("nan")

    # -- checkpoint state --------------------------------------------------
    def state_dict(self) -> Dict[str, Any]:
        return {"seed": self.seed, "position": self.position,
                "n_sequences": self.n_sequences, "block_size": self.block_size,
                "path": str(self.path), "n_tokens": self.n_tokens}

    def load_state_dict(self, state: Dict[str, Any]) -> None:
        if int(state["block_size"]) != self.block_size:
            raise ValueError(
                f"checkpoint block_size {state['block_size']} != {self.block_size}")
        if int(state["n_sequences"]) != self.n_sequences:
            raise ValueError(
                f"checkpoint was written against {state['n_sequences']:,} "
                f"sequences but this file has {self.n_sequences:,}. The data "
                "changed under the run; refusing to resume.")
        self.seed = int(state["seed"])
        self._epoch = -1
        self.position = int(state["position"])
        self._set_epoch(self.position // self.n_sequences)

    def __repr__(self) -> str:                                  # pragma: no cover
        return (f"PackedDataset({self.path.name}, {self.n_tokens:,} tokens, "
                f"{self.n_sequences:,} sequences of {self.block_size}, "
                f"seed={self.seed}, position={self.position})")


def iter_document_windows(tokens: np.ndarray, start: int, length: int,
                          block_size: int):
    """Split one document's span into (x, y) windows for evaluation.

    Windows stay inside the document, so a per-document loss never mixes in a
    neighbour's tokens. A document shorter than two tokens yields nothing.
    """
    end = start + length
    pos = start
    while pos + 1 < end:
        stop = min(pos + block_size + 1, end)
        window = np.asarray(tokens[pos:stop], dtype=np.int64)
        if window.size < 2:
            break
        yield window[:-1], window[1:]
        pos += block_size
