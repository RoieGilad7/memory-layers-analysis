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

__all__ = ["SlotUsageCounter", "ReadLogWriter", "ReadLogReader", "usage_stats",
           "bytes_per_token"]


def _index_dtype(n_slots: int) -> np.dtype:
    if n_slots <= np.iinfo(np.uint16).max + 1:
        return np.dtype(np.uint16)
    if n_slots <= np.iinfo(np.uint32).max + 1:
        return np.dtype(np.uint32)
    return np.dtype(np.uint64)


def bytes_per_token(n_slots: int, heads: int, topk: int, store_weights: bool = True) -> int:
    per_read = _index_dtype(n_slots).itemsize + (2 if store_weights else 0)
    return per_read * heads * topk


class SlotUsageCounter:
    """Per-layer histogram of slot reads. Cheap enough to always leave on."""

    def __init__(self, n_slots: Dict[int, int]):
        self.n_slots = dict(n_slots)
        self.counts: Dict[int, torch.Tensor] = {
            layer: torch.zeros(n, dtype=torch.long) for layer, n in self.n_slots.items()}
        self.tokens_seen = 0
        self.weight_sums: Dict[int, torch.Tensor] = {
            layer: torch.zeros(n, dtype=torch.float64) for layer, n in self.n_slots.items()}

    @torch.no_grad()
    def update(self, reads: Dict[int, "object"], count_tokens: bool = True) -> None:
        for layer, r in reads.items():
            if layer not in self.counts:
                continue
            idx = r.indices.reshape(-1).to("cpu", torch.long)
            self.counts[layer] += torch.bincount(idx, minlength=self.n_slots[layer])
            w = r.weights.reshape(-1).to("cpu", torch.float64)
            self.weight_sums[layer] += torch.bincount(
                idx, weights=w, minlength=self.n_slots[layer])
        if count_tokens and reads:
            any_r = next(iter(reads.values()))
            b, t = any_r.indices.shape[:2]
            self.tokens_seen += int(b) * int(t)

    def stats(self) -> Dict[int, dict]:
        return {layer: usage_stats(c, self.weight_sums[layer])
                for layer, c in self.counts.items()}

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
def usage_stats(counts: torch.Tensor, weight_sums: Optional[torch.Tensor] = None) -> dict:
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
        out.update(kl_from_uniform=0.0, normalized_kl=0.0, top1_share=0.0,
                   top1pct_share=0.0, gini=0.0)
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
        gini=float(1.0 - 2.0 * ((torch.cumsum(torch.sort(p).values, 0) - 0.5 * torch.sort(p).values).sum() / n)),
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

    def __init__(self, out_dir: str | Path, n_slots: Dict[int, int],
                 heads: Dict[int, int], topk: Dict[int, int],
                 store_weights: bool = True, enabled: bool = True):
        self.enabled = enabled
        self.out_dir = Path(out_dir)
        self.n_slots, self.heads, self.topk = dict(n_slots), dict(heads), dict(topk)
        self.store_weights = store_weights
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
            fh = self._fh(f"layer{layer}_idx.bin")
            fh.write(a.tobytes())
            self.bytes_written += a.nbytes
            if self.store_weights:
                w = r.weights.detach().to("cpu", torch.float16).numpy()
                fw = self._fh(f"layer{layer}_w.bin")
                fw.write(w.tobytes())
                self.bytes_written += w.nbytes
            self.records.append({"step": int(step), "layer": int(layer),
                                 "batch": int(b), "seq": int(t),
                                 "heads": int(h), "topk": int(k)})
        any_r = next(iter(reads.values()))
        self.tokens_logged += int(any_r.indices.shape[0]) * int(any_r.indices.shape[1])

    def close(self) -> Optional[Path]:
        if not self.enabled:
            return None
        for fh in self._files.values():
            fh.close()
        self._files.clear()
        manifest = self.out_dir / "manifest.json"
        manifest.write_text(json.dumps({
            "n_slots": self.n_slots, "heads": self.heads, "topk": self.topk,
            "store_weights": self.store_weights,
            "index_dtype": {str(l): _index_dtype(n).name for l, n in self.n_slots.items()},
            "weight_dtype": "float16",
            "bytes_written": self.bytes_written,
            "tokens_logged": self.tokens_logged,
            "bytes_per_token": (self.bytes_written / self.tokens_logged
                                if self.tokens_logged else 0.0),
            "records": self.records,
        }, indent=2))
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
