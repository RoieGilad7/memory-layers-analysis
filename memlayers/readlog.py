"""Read-log collection: which memory slots each token read, and with what weight.

Two levels, because they cost very different amounts:

  SlotUsageCounter -- an int64 histogram over slots, updated with bincount. Costs
      nothing to keep on, and is all that the slot-usage fraction and the KL-from-
      uniform statistic need. Always safe to leave on.

  ReadLogWriter    -- the full per-token log appended to flat binary files. This is
      big: heads*topk reads per token at (2 B index + 2 B weight) is 512 B/token for
      a 4-head top-32 layer, i.e. ~512 MB per million tokens. Use it on a slice of
      training, not all of it.

Indices are stored as the narrowest unsigned type that fits the slot count, weights
as float16. A JSON manifest records the shapes so the reader can rebuild the arrays.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Optional

import numpy as np
import torch

__all__ = [
    "SlotUsageCounter",
    "ReadLogWriter",
    "ReadLogReader",
    "ReadLog",
    "index_dtype",
    "usage_stats",
    "bytes_per_token",
]


def _index_dtype(n_slots: int) -> np.dtype:
    if n_slots <= np.iinfo(np.uint16).max + 1:
        return np.dtype(np.uint16)
    if n_slots <= np.iinfo(np.uint32).max + 1:
        return np.dtype(np.uint32)
    return np.dtype(np.uint64)


def index_dtype(n_slots: int) -> np.dtype:
    """uint16 for a layer of at most 65,536 slots, else uint32."""
    return _index_dtype(n_slots)


def bytes_per_token(
    n_slots: int, heads: int, topk: int, store_weights: bool = True
) -> int:
    per_read = _index_dtype(n_slots).itemsize + (2 if store_weights else 0)
    return per_read * heads * topk


class SlotUsageCounter:
    """Per-layer histogram of slot reads. Cheap enough to always leave on."""

    def __init__(self, n_slots: Dict[int, int]):
        self.n_slots = dict(n_slots)
        self.counts: Dict[int, torch.Tensor] = {
            layer: torch.zeros(n, dtype=torch.long) for layer, n in self.n_slots.items()
        }
        self.tokens_seen = 0
        self.weight_sums: Dict[int, torch.Tensor] = {
            layer: torch.zeros(n, dtype=torch.float64)
            for layer, n in self.n_slots.items()
        }

    @torch.no_grad()
    def update(self, reads: Dict[int, "object"], count_tokens: bool = True) -> None:
        for layer, r in reads.items():
            if layer not in self.counts:
                continue
            idx = r.indices.reshape(-1).to("cpu", torch.long)
            self.counts[layer] += torch.bincount(idx, minlength=self.n_slots[layer])
            w = r.weights.reshape(-1).to("cpu", torch.float64)
            self.weight_sums[layer] += torch.bincount(
                idx, weights=w, minlength=self.n_slots[layer]
            )
        if count_tokens and reads:
            any_r = next(iter(reads.values()))
            b, t = any_r.indices.shape[:2]
            self.tokens_seen += int(b) * int(t)

    def stats(self) -> Dict[int, dict]:
        return {
            layer: usage_stats(c, self.weight_sums[layer])
            for layer, c in self.counts.items()
        }

    def save(self, path: str | Path) -> Path:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(
            path,
            tokens_seen=np.array(self.tokens_seen),
            **{f"counts_{l}": c.numpy() for l, c in self.counts.items()},
            **{f"weights_{l}": w.numpy() for l, w in self.weight_sums.items()},
        )
        return path


@torch.no_grad()
def usage_stats(
    counts: torch.Tensor, weight_sums: Optional[torch.Tensor] = None
) -> dict:
    """Slot-usage summary, following Lample et al. 2019 sec 4.

    kl_from_uniform is KL(p || uniform) in nats, where p is the normalized read
    histogram over all n slots. 0 means every slot is read equally often; the
    maximum, ln(n), means a single slot absorbs every read.
    """
    counts = counts.to(torch.float64)
    n = counts.numel()
    total = float(counts.sum())
    used = int((counts > 0).sum())
    out = {
        "n_slots": int(n),
        "slots_used": used,
        "fraction_used": used / n if n else 0.0,
        "total_reads": total,
        "max_kl_nats": math.log(n) if n else 0.0,
    }
    if total <= 0:
        out.update(
            kl_from_uniform=0.0,
            normalized_kl=0.0,
            top1_share=0.0,
            top1pct_share=0.0,
            gini=0.0,
        )
        return out
    p = counts / total
    nz = p[p > 0]
    # KL(p || u) = sum p log(p * n) = log n - H(p)
    entropy = float(-(nz * nz.log()).sum())
    kl = math.log(n) - entropy
    srt = torch.sort(p, descending=True).values
    k1 = max(1, n // 100)
    out.update(
        entropy_nats=entropy,
        kl_from_uniform=kl,
        normalized_kl=kl / math.log(n) if n > 1 else 0.0,
        top1_share=float(srt[0]),
        top1pct_share=float(srt[:k1].sum()),
        gini=float(
            1.0
            - 2.0
            * (
                (
                    torch.cumsum(torch.sort(p).values, 0) - 0.5 * torch.sort(p).values
                ).sum()
                / n
            )
        ),
    )
    if weight_sums is not None and float(weight_sums.sum()) > 0:
        w = weight_sums.to(torch.float64)
        wp = w / w.sum()
        wnz = wp[wp > 0]
        wkl = math.log(n) - float(-(wnz * wnz.log()).sum())
        out["kl_from_uniform_weighted"] = wkl
        out["normalized_kl_weighted"] = wkl / math.log(n) if n > 1 else 0.0
    return out


class ReadLogWriter:
    """Appends the full read log to flat binary files, one pair per memory layer."""

    def __init__(
        self,
        out_dir: str | Path,
        n_slots: Dict[int, int],
        heads: Dict[int, int],
        topk: Dict[int, int],
        store_weights: bool = True,
        enabled: bool = True,
        index_file: str = "layer{layer}_idx.bin",
        weight_file: str = "layer{layer}_w.bin",
    ):
        self.enabled = enabled
        self.out_dir = Path(out_dir)
        self.n_slots, self.heads, self.topk = dict(n_slots), dict(heads), dict(topk)
        self.store_weights = store_weights
        # the read-log pass names its files layer<L>_indices.bin / _weights.bin
        self.index_file, self.weight_file = index_file, weight_file
        self.records: List[dict] = []
        self.bytes_written = 0
        self.tokens_logged = 0
        self._files: Dict[str, object] = {}
        if self.enabled:
            self.out_dir.mkdir(parents=True, exist_ok=True)

    def _fh(self, name: str):
        if name not in self._files:
            self._files[name] = open(self.out_dir / name, "ab")
        return self._files[name]

    @torch.no_grad()
    def append(self, step: int, reads: Dict[int, "object"]) -> None:
        if not self.enabled or not reads:
            return
        for layer, r in sorted(reads.items()):
            idx = r.indices.detach().to("cpu")
            b, t, h, k = idx.shape
            a = idx.numpy().astype(_index_dtype(self.n_slots[layer]), copy=False)
            fh = self._fh(self.index_file.format(layer=layer))
            fh.write(a.tobytes())
            self.bytes_written += a.nbytes
            if self.store_weights:
                w = r.weights.detach().to("cpu", torch.float16).numpy()
                fw = self._fh(self.weight_file.format(layer=layer))
                fw.write(w.tobytes())
                self.bytes_written += w.nbytes
            self.records.append(
                {
                    "step": int(step),
                    "layer": int(layer),
                    "batch": int(b),
                    "seq": int(t),
                    "heads": int(h),
                    "topk": int(k),
                }
            )
        any_r = next(iter(reads.values()))
        self.tokens_logged += int(any_r.indices.shape[0]) * int(any_r.indices.shape[1])

    def close(
        self, extra: Optional[dict] = None, records: bool = True
    ) -> Optional[Path]:
        """Write manifest.json. `extra` is merged in; `records=False` drops the
        per-forward record list (the read-log pass keeps its own token table)."""
        if not self.enabled:
            return None
        for fh in self._files.values():
            fh.close()
        self._files.clear()
        manifest = self.out_dir / "manifest.json"
        manifest.write_text(
            json.dumps(
                {
                    **(extra or {}),
                    "n_slots": self.n_slots,
                    "heads": self.heads,
                    "topk": self.topk,
                    "store_weights": self.store_weights,
                    "index_dtype": {
                        str(l): _index_dtype(n).name for l, n in self.n_slots.items()
                    },
                    "weight_dtype": "float16",
                    "bytes_written": self.bytes_written,
                    "tokens_logged": self.tokens_logged,
                    "bytes_per_token": (
                        self.bytes_written / self.tokens_logged
                        if self.tokens_logged
                        else 0.0
                    ),
                    **({"records": self.records} if records else {}),
                },
                indent=2,
                default=str,
            )
        )
        return manifest

    def __enter__(self):
        return self

    def __exit__(self, *a):
        self.close()


class ReadLogReader:
    """Reads back what ReadLogWriter produced."""

    def __init__(self, out_dir: str | Path):
        self.out_dir = Path(out_dir)
        self.manifest = json.loads((self.out_dir / "manifest.json").read_text())

    def layers(self) -> List[int]:
        return sorted({r["layer"] for r in self.manifest["records"]})

    def coords(self, layer: int):
        """-> (step, batch_index, token_position) arrays, one entry per logged row.

        The binary files hold reads in row-major (batch, seq) order per record, so the
        position of every row is recoverable from the manifest rather than stored.
        """
        steps, bidx, pos = [], [], []
        for r in self.manifest["records"]:
            if r["layer"] != layer:
                continue
            b, t = r["batch"], r["seq"]
            steps.append(np.full(b * t, r["step"], dtype=np.int64))
            bidx.append(np.repeat(np.arange(b, dtype=np.int64), t))
            pos.append(np.tile(np.arange(t, dtype=np.int64), b))
        if not steps:
            empty = np.empty(0, dtype=np.int64)
            return empty, empty, empty
        return (np.concatenate(steps), np.concatenate(bidx), np.concatenate(pos))

    def load(self, layer: int):
        """-> (indices [N, heads, topk] int64, weights [N, heads, topk] float32 | None)
        where N is the total number of logged token positions for that layer."""
        recs = [r for r in self.manifest["records"] if r["layer"] == layer]
        h, k = recs[0]["heads"], recs[0]["topk"]
        dt = np.dtype(self.manifest["index_dtype"][str(layer)])
        idx = np.fromfile(self.out_dir / f"layer{layer}_idx.bin", dtype=dt)
        idx = idx.reshape(-1, h, k).astype(np.int64)
        w = None
        if self.manifest["store_weights"]:
            w = np.fromfile(self.out_dir / f"layer{layer}_w.bin", dtype=np.float16)
            w = w.reshape(-1, h, k).astype(np.float32)
        return idx, w


class ReadLog:
    """A read log written by `python -m memlayers.readlog_pass`: one directory
    per checkpoint, `<run_dir>/readlogs/step_<6-digit step>/`.

        rl = ReadLog.open(path)
        rl.layers, rl.n_slots(3), rl.tokens            # tokens: a DataFrame, one row per token
        rows = rl.select(segment="bio", tier=["frequent", "rare"], role="test")
        rl.slot_counts(3, rows, weighted=True)          # np.ndarray[n_slots]
        for row_ids, idx, w in rl.iter_chunks(3, rows): ...

    `indices(layer)` / `weights(layer)` are read-only memmaps of shape
    [n_tokens, heads, topk]; row i of every array is row i of `tokens`.
    """

    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.manifest = json.loads((self.path / "manifest.json").read_text())
        self._tokens = None
        self._mm: Dict[tuple, np.memmap] = {}

    @classmethod
    def open(cls, path: str | Path) -> "ReadLog":
        p = Path(path)
        if not (p / "manifest.json").exists():
            raise FileNotFoundError(f"{p} is not a read log (no manifest.json)")
        return cls(p)

    # -- shape -----------------------------------------------------------
    @property
    def layers(self) -> List[int]:
        return sorted(int(l) for l in self.manifest["layers"])

    @property
    def n_tokens(self) -> int:
        return int(self.manifest["n_tokens"])

    @property
    def step(self) -> int:
        return int(self.manifest["step"])

    def n_slots(self, layer: int) -> int:
        return int(self.manifest["n_slots"][str(layer)])

    def heads(self, layer: int) -> int:
        return int(self.manifest["heads"][str(layer)])

    def topk(self, layer: int) -> int:
        return int(self.manifest["topk"][str(layer)])

    # -- arrays ----------------------------------------------------------
    @property
    def tokens(self):
        if self._tokens is None:
            import pandas as pd

            self._tokens = pd.read_parquet(self.path / "tokens.parquet")
        return self._tokens

    def _memmap(self, layer: int, kind: str) -> np.memmap:
        key = (int(layer), kind)
        if key not in self._mm:
            if str(layer) not in self.manifest["n_slots"]:
                raise KeyError(
                    f"layer {layer} not in this read log; layers {self.layers}"
                )
            dt = np.dtype(
                self.manifest["index_dtype"][str(layer)]
                if kind == "indices"
                else "float16"
            )
            shape = (self.n_tokens, self.heads(layer), self.topk(layer))
            self._mm[key] = np.memmap(
                self.path / f"layer{layer}_{kind}.bin", dtype=dt, mode="r", shape=shape
            )
        return self._mm[key]

    def indices(self, layer: int) -> np.memmap:
        return self._memmap(layer, "indices")

    def weights(self, layer: int) -> np.memmap:
        return self._memmap(layer, "weights")

    # -- queries ---------------------------------------------------------
    def select(self, **filters) -> np.ndarray:
        """Row ids whose `tokens` columns match every filter (a value, or a
        list/tuple/set of allowed values). No filter -> every row."""
        t = self.tokens
        mask = np.ones(len(t), dtype=bool)
        for col, want in filters.items():
            if col not in t.columns:
                raise KeyError(f"no tokens column {col!r}; have {list(t.columns)}")
            c = t[col]
            if isinstance(want, (list, tuple, set, np.ndarray)):
                mask &= c.isin(list(want)).to_numpy()
            else:
                mask &= (c == want).to_numpy()
        return np.flatnonzero(mask)

    def iter_chunks(self, layer: int, rows=None, chunk_tokens: int = 1_000_000):
        """Yield (row_ids, indices[row_ids], weights[row_ids]) in chunks of at
        most `chunk_tokens` rows, so nothing loads the whole log at once."""
        idx, w = self.indices(layer), self.weights(layer)
        if rows is None:
            for a in range(0, self.n_tokens, chunk_tokens):
                b = min(a + chunk_tokens, self.n_tokens)
                yield np.arange(a, b), np.asarray(idx[a:b]), np.asarray(w[a:b])
            return
        rows = np.asarray(rows, dtype=np.int64)
        for a in range(0, len(rows), chunk_tokens):
            r = rows[a : a + chunk_tokens]
            yield r, idx[r], w[r]

    def slot_counts(self, layer: int, rows=None, weighted: bool = False) -> np.ndarray:
        """Reads per slot over `rows` (all rows by default): a count of
        (token, head, rank) reads, or the summed gate weights if `weighted`."""
        n = self.n_slots(layer)
        out = np.zeros(n, dtype=np.float64 if weighted else np.int64)
        for _, i, w in self.iter_chunks(layer, rows):
            flat = i.reshape(-1).astype(np.int64)
            if weighted:
                out += np.bincount(
                    flat, weights=w.reshape(-1).astype(np.float64), minlength=n
                )
            else:
                out += np.bincount(flat, minlength=n)
        return out
