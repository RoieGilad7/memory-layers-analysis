"""Is a checkpoint resume bit-reproducible on MPS, as it is on CPU?

tests/test_train.py compares a straight 100-step run against 50 + save + reload + 50 at a
1e-4 tolerance, and runs on CPU because that test is about the resume mechanism, not about
the backend's float determinism. This script asks the backend question directly on the
device we actually train on, so the report can state it rather than assume it.

Two separate properties are measured:
  repeat   -- same config, same seed, two fresh runs: does MPS give the same loss twice?
  resume   -- straight vs. split run: does resuming land on the same loss?

    python bench/mps_determinism.py [--steps 40] [--device mps]
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import yaml  # noqa: E402

from memlayers.devices import pick_device  # noqa: E402

WORKER = ROOT / "tests" / "_resume_worker.py"


def cfg_dict(out_dir: str, steps: int, device: str) -> dict:
    return {
        "name": "mps-determinism",
        "model": {"vocab_size": 50257, "block_size": 128, "n_layer": 4, "n_head": 4,
                  "n_embd": 256, "dropout": 0.0, "bias": True, "tie_embeddings": True,
                  "memory_layers": [2], "memory_kind": "pkm",
                  "memory": {"num_keys": 64, "topk": 16, "heads": 4, "dim_head": 64,
                             "query_batchnorm": True}},
        "data": {"kind": "repeat", "chunk_len": 8, "n_distinct": None, "seed": 7},
        "train": {"steps": steps, "micro_batch_size": 4, "grad_accum_steps": 1,
                  "lr": 1e-3, "lr_memory_values": 4e-3, "weight_decay": 0.1,
                  "warmup_steps": 5, "min_lr_ratio": 0.1, "seed": 99,
                  "log_every": 0, "ckpt_every": 0, "grad_clip": 1.0,
                  "track_slot_usage": False, "read_logging": False},
        "runtime": {"device": device, "out_dir": out_dir},
    }


def run(cfg_path, out_json, steps, resume=None, save=None):
    cmd = [sys.executable, str(WORKER), str(cfg_path), str(out_json), "--steps", str(steps)]
    if resume:
        cmd += ["--resume", str(resume)]
    if save:
        cmd += ["--save", str(save)]
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=str(ROOT))
    if r.returncode != 0:
        raise RuntimeError(f"worker failed:\n{r.stdout}\n{r.stderr}")
    return json.loads(Path(out_json).read_text())


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--steps", type=int, default=40)
    ap.add_argument("--device", default=None)
    a = ap.parse_args()
    device = a.device or pick_device().type

    out = {"device": device, "steps": a.steps}
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)

        # --- property 1: two identical fresh runs
        for tag in ("r1", "r2"):
            p = td / f"{tag}.yaml"
            p.write_text(yaml.safe_dump(cfg_dict(str(td / tag), a.steps, device)))
        x1 = run(td / "r1.yaml", td / "x1.json", a.steps)
        x2 = run(td / "r2.yaml", td / "x2.json", a.steps)
        out["repeat"] = {
            "loss_a": x1["final_loss"], "loss_b": x2["final_loss"],
            "abs_diff": abs(x1["final_loss"] - x2["final_loss"]),
            "param_checksum_a": x1["param_checksum"],
            "param_checksum_b": x2["param_checksum"],
            "checksum_abs_diff": abs(x1["param_checksum"] - x2["param_checksum"]),
        }
        out["repeat"]["bit_identical"] = (
            out["repeat"]["abs_diff"] == 0.0
            and out["repeat"]["checksum_abs_diff"] == 0.0)
        out["repeat"]["within_1e-4"] = out["repeat"]["abs_diff"] < 1e-4

        # --- property 2: straight vs. resumed
        half = a.steps // 2
        sp = td / "s.yaml"
        sp.write_text(yaml.safe_dump(cfg_dict(str(td / "straight"), a.steps, device)))
        gp = td / "g.yaml"
        gp.write_text(yaml.safe_dump(cfg_dict(str(td / "split"), a.steps, device)))
        st = run(sp, td / "st.json", a.steps)
        run(gp, td / "h1.json", half, save=td / "half.pt")
        h2 = run(gp, td / "h2.json", a.steps - half, resume=td / "half.pt")
        out["resume"] = {
            "loss_straight": st["final_loss"], "loss_resumed": h2["final_loss"],
            "abs_diff": abs(st["final_loss"] - h2["final_loss"]),
            "final_step_straight": st["final_step"], "final_step_resumed": h2["final_step"],
            "lr_match": st["lr"] == h2["lr"],
            "data_order_match": st["next_batch_sum"] == h2["next_batch_sum"],
        }
        out["resume"]["bit_identical"] = out["resume"]["abs_diff"] == 0.0
        out["resume"]["within_1e-4"] = out["resume"]["abs_diff"] < 1e-4

    (ROOT / "bench" / "results" / f"determinism_{device}.json").write_text(
        json.dumps(out, indent=2))
    print(json.dumps(out, indent=2))
    r, s = out["repeat"], out["resume"]
    print(f"\n[{device}] repeat: |diff| = {r['abs_diff']:.3e}  "
          f"bit-identical={r['bit_identical']}  within 1e-4={r['within_1e-4']}")
    print(f"[{device}] resume: |diff| = {s['abs_diff']:.3e}  "
          f"bit-identical={s['bit_identical']}  within 1e-4={s['within_1e-4']}  "
          f"lr_match={s['lr_match']}  data_order_match={s['data_order_match']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
