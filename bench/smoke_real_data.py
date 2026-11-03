"""300-step smoke run of a real config on the packed data, then held-out loss.

    python bench/smoke_real_data.py --config memlayers/configs/t1_pkm.yaml

Proves the whole chain end to end: `data.fetch` verifies the bundle, the loader
memmaps train.bin, the model trains, and the test halves give a per-subject
loss. Writes bench/results/smoke_real_<name>.json.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import torch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from data import pack
from data.common import load_config as load_data_config
from data.loader import iter_document_windows
from memlayers.train import Trainer, load_config


@torch.no_grad()
def heldout_loss_by_subject(model, device, data_cfg, half: str, block_size: int,
                            max_docs_per_subject: int = 200,
                            seed: int = 0) -> dict:
    """Mean next-token loss per subject on one held-out half.

    Evaluated per document, so a window never mixes two documents (let alone
    two subjects) and the per-subject number means what it says.
    """
    tokens = np.memmap(data_cfg.heldout_tokens_dir / f"{half}.bin",
                       dtype=np.uint16, mode="r")
    index = pack.read_index(data_cfg.heldout_tokens_dir / f"{half}.idx.parquet")
    subjects = np.asarray(index["subject"], dtype=object)
    starts = np.asarray(index["start"], dtype=np.int64)
    lengths = np.asarray(index["length"], dtype=np.int64)

    model.eval()
    out = {}
    rng = np.random.default_rng(seed)
    for subject in sorted(set(subjects.tolist())):
        rows = np.flatnonzero(subjects == subject)
        if rows.size > max_docs_per_subject:
            rows = np.sort(rng.choice(rows, max_docs_per_subject, replace=False))
        total_loss, total_tokens, n_docs = 0.0, 0, 0
        for r in rows:
            n_docs += 1
            for x, y in iter_document_windows(tokens, int(starts[r]),
                                              int(lengths[r]), block_size):
                xt = torch.from_numpy(x[None, :]).to(device)
                yt = torch.from_numpy(y[None, :]).to(device)
                _, loss = model(xt, yt)
                total_loss += float(loss) * y.size
                total_tokens += int(y.size)
        out[subject] = {
            "loss": round(total_loss / total_tokens, 4) if total_tokens else None,
            "documents": n_docs, "tokens": total_tokens}
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--config", default="memlayers/configs/t1_pkm.yaml")
    ap.add_argument("--steps", type=int, default=300)
    ap.add_argument("--data-config", default="configs/data/v1.yaml")
    ap.add_argument("--out-dir", default="runs/smoke_real")
    ap.add_argument("--micro-batch-size", type=int, default=None)
    ap.add_argument("--max-heldout-docs", type=int, default=200)
    ap.add_argument("--half", default="test")
    args = ap.parse_args(argv)

    overrides = [f"data.source=real", f"data.version=v1",
                 f"data.data_config={args.data_config}",
                 f"train.steps={args.steps}",
                 f"runtime.out_dir={args.out_dir}",
                 "train.log_every=10"]
    if args.micro_batch_size:
        overrides.append(f"train.micro_batch_size={args.micro_batch_size}")
    cfg = load_config(ROOT / args.config, overrides)
    t0 = time.time()
    trainer = Trainer(cfg)
    trainer.write_meta()

    # step 0 loss before any update, for the report's first row
    x, y = trainer.data.get_batch(0, cfg.train.micro_batch_size, 0, trainer.device)
    with torch.no_grad():
        _, loss0 = trainer.model(x, y)
    trainer.data.position = 0          # undo the probe batch
    marks = {0: float(loss0)}

    history = trainer.train(steps=args.steps, progress=True)
    for row in history:
        if row["step"] in (100, 200, 300):
            marks[row["step"]] = row["loss"]
    ckpt = trainer.save_checkpoint()

    data_cfg = load_data_config(args.data_config)
    held = heldout_loss_by_subject(
        trainer.model, trainer.device, data_cfg, args.half,
        cfg.model.get("block_size", 512), args.max_heldout_docs)

    result = {
        "config": args.config,
        "name": cfg.name,
        "device": str(trainer.device),
        "steps": args.steps,
        "micro_batch_size": cfg.train.micro_batch_size,
        "tokens_per_step": cfg.tokens_per_step,
        "data": trainer.data_provenance,
        "loss_at_step": {str(k): round(v, 4) for k, v in sorted(marks.items())},
        "final_loss_mean_last_20": round(
            sum(r["loss"] for r in history[-20:]) / min(20, len(history)), 4),
        "heldout_half": args.half,
        "heldout_loss_by_subject": held,
        "tokens_seen": trainer.tokens_seen,
        "peak_mem_bytes": trainer.peak_mem,
        "checkpoint": str(ckpt),
        "seconds": round(time.time() - t0, 1),
    }
    out = ROOT / "bench" / "results" / f"smoke_real_{cfg.name}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2))

    print(f"\n=== smoke run: {cfg.name} on {trainer.device}, "
          f"{args.steps} steps, {result['seconds']}s")
    for k, v in result["loss_at_step"].items():
        print(f"   loss @ step {k:>4}: {v:.4f}")
    print(f"   mean of the last 20 steps: {result['final_loss_mean_last_20']:.4f}")
    print(f"\n=== held-out loss, {args.half} half "
          f"(per document, <= {args.max_heldout_docs} docs/subject)")
    for s, v in held.items():
        print(f"   {s:22s} {v['loss']:.4f}   "
              f"({v['documents']:,} docs, {v['tokens']:,} tokens)")
    print(f"\n   -> {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
