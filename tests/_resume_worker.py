"""Subprocess worker for the checkpoint-resume test.

Run in a FRESH interpreter so the resume path cannot accidentally rely on state
left in memory by the first half of the run.

    python tests/_resume_worker.py CONFIG OUT_JSON [--resume CKPT] [--steps N]
                                   [--save CKPT]
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import torch  # noqa: E402

from memlayers.train import Trainer, load_config  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("config")
    ap.add_argument("out_json")
    ap.add_argument("--resume", default=None)
    ap.add_argument("--steps", type=int, required=True)
    ap.add_argument("--save", default=None)
    a = ap.parse_args()

    tr = Trainer(load_config(a.config))
    if a.resume:
        tr.load_checkpoint(a.resume)
    start = tr.step
    hist = tr.train(steps=a.steps, progress=False)
    if a.save:
        tr.save_checkpoint(a.save)

    # hash the batch the run would read next, to prove data order continued
    x, _ = tr.data.get_batch(tr.step, tr.cfg.train.micro_batch_size)
    probe = tr.data.get_batch(start, tr.cfg.train.micro_batch_size)[0]
    Path(a.out_json).write_text(json.dumps({
        "start_step": start,
        "final_step": tr.step,
        "final_loss": hist[-1]["loss"],
        "losses_tail": [h["loss"] for h in hist[-3:]],
        "lr": [g["lr"] for g in tr.optimizer.param_groups],
        "lr_names": [g.get("name") for g in tr.optimizer.param_groups],
        "tokens_seen": tr.tokens_seen,
        "next_batch_sum": int(x.sum()),
        "batch_at_start_sum": int(probe.sum()),
        # .cpu() first: MPS has no float64, so .double() must happen on the host
        "param_checksum": float(sum(p.detach().cpu().double().sum()
                                    for p in tr.model.parameters())),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
