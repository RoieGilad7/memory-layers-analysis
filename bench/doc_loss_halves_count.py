"""Halves per batch the same-document loss would see on real data.

    .venv/bin/python bench/doc_loss_halves_count.py [--bin data/v1_sample/tokens/train.bin]

Reads the packed token file read-only (memmap) in loader order (seed 0) and counts,
for each of the first `--batches` batches of 32 x 512 windows, the halves
find_halves returns with min_piece_tokens 32. Also the counts for 16 and 64.
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from data.loader import PackedDataset  # noqa: E402
from memlayers.doc_loss import find_halves  # noqa: E402


def count(bin_path, batches=50, batch=32, block=512, seed=0, mins=(16, 32, 64)):
    ds = PackedDataset(bin_path, block_size=block, seed=seed)
    per = {m: [] for m in mins}
    eots = []
    for step in range(batches):
        x, _ = ds.get_batch(step, batch)
        eots.append(int((x == 50256).sum()))
        for m in mins:
            per[m].append(find_halves(x, 50256, m)[1])
    out = {
        "bin": str(bin_path),
        "n_sequences": ds.n_sequences,
        "batches": batches,
        "batch": [batch, block],
        "eot_per_batch_mean": statistics.mean(eots),
    }
    for m, v in per.items():
        out[f"min{m}"] = {
            "mean": statistics.mean(v),
            "min": min(v),
            "max": max(v),
            "pieces_mean": statistics.mean(v) / 2,
        }
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--bin", default="data/v1_sample/tokens/train.bin")
    ap.add_argument("--batches", type=int, default=50)
    a = ap.parse_args()
    print(json.dumps(count(a.bin, a.batches), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
