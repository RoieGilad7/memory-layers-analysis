"""Training loop for the memory-layer models.

AdamW + gradient accumulation + cosine LR with warmup + gradient clipping, with
separate parameter groups so the memory value table can take a higher learning
rate than the backbone (Lample et al. 2019 used 1e-3 for the memory values against
2.5e-4 for everything else).

Checkpoints carry model, optimizer, scheduler, RNG states and the step counter.
Data order needs no saving: batches are a pure function of (seed, step), so a
resumed run reads exactly the batches it would have read.

CLI:
    python -m memlayers.train --config memlayers/configs/t1_pkm.yaml
    python -m memlayers.train --config ... --set train.steps=50 runtime.out_dir=runs/x
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import os
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

import torch
import yaml

from .data_fake import build_dataset
from .devices import (empty_cache, get_rng_states, peak_memory_bytes, pick_device,
                      reset_peak_memory, set_rng_states, synchronize)
from .model import GPT, GPTConfig
from .readlog import ReadLogWriter, SlotUsageCounter, bytes_per_token

__all__ = ["TrainConfig", "Trainer", "load_config", "build_optimizer", "main"]

CSV_FIELDS = ["step", "loss", "lr", "lr_memory", "step_time_s", "tokens_per_s",
              "tokens_seen", "peak_mem_bytes", "grad_norm"]


# ----------------------------------------------------------------------------- config
@dataclass
class OptimCfg:
    steps: int = 300
    micro_batch_size: int = 8
    grad_accum_steps: int = 1
    lr: float = 2.5e-4
    lr_memory_values: float = 1.0e-3
    lr_memory_keys: Optional[float] = None       # None -> same as lr
    weight_decay: float = 0.1
    weight_decay_memory: float = 0.0             # value/key tables act like embeddings
    betas: tuple = (0.9, 0.95)
    eps: float = 1e-8
    grad_clip: float = 1.0
    warmup_steps: int = 30
    min_lr_ratio: float = 0.1
    seed: int = 1337
    log_every: int = 10
    ckpt_every: int = 0                          # 0 = only at the end
    read_logging: bool = False
    read_log_steps: int = 0                      # 0 = every step while read_logging
    read_log_weights: bool = True
    track_slot_usage: bool = True


@dataclass
class DataCfg:
    kind: str = "random"
    chunk_len: int = 16
    n_distinct: Optional[int] = None
    seed: int = 1234


@dataclass
class RuntimeCfg:
    device: str = "auto"
    out_dir: str = "runs/default"
    compile: bool = False


@dataclass
class TrainConfig:
    name: str = "unnamed"
    model: Dict[str, Any] = field(default_factory=dict)
    data: DataCfg = field(default_factory=DataCfg)
    train: OptimCfg = field(default_factory=OptimCfg)
    runtime: RuntimeCfg = field(default_factory=RuntimeCfg)

    @property
    def tokens_per_step(self) -> int:
        block = self.model.get("block_size", 512)
        return self.train.micro_batch_size * self.train.grad_accum_steps * block


def _coerce(value: str) -> Any:
    try:
        return yaml.safe_load(value)
    except Exception:
        return value


def load_config(path: str | Path, overrides: Optional[List[str]] = None) -> TrainConfig:
    raw = yaml.safe_load(Path(path).read_text()) or {}
    for ov in overrides or []:
        if "=" not in ov:
            raise ValueError(f"override {ov!r} must look like section.key=value")
        key, val = ov.split("=", 1)
        node = raw
        parts = key.split(".")
        for p in parts[:-1]:
            node = node.setdefault(p, {})
        node[parts[-1]] = _coerce(val)
    return TrainConfig(
        name=raw.get("name", "unnamed"),
        model=raw.get("model", {}) or {},
        data=DataCfg(**(raw.get("data", {}) or {})),
        train=OptimCfg(**(raw.get("train", {}) or {})),
        runtime=RuntimeCfg(**(raw.get("runtime", {}) or {})),
    )


# -------------------------------------------------------------------------- optimizer
def build_optimizer(model: GPT, cfg: OptimCfg) -> torch.optim.AdamW:
    """Four groups: memory values, memory keys, decay, no-decay.

    The memory tables are indexed lookups, so they are treated like embeddings:
    their own learning rate and, by default, no weight decay. Everything else
    follows nanoGPT's rule -- tensors with dim >= 2 decay, biases and norms do not.
    """
    mem_value_ids, mem_key_ids = set(), set()
    for m in model.memory_layers.values():
        mem_value_ids |= {id(p) for p in m.value_parameters()}
        mem_key_ids |= {id(p) for p in m.key_parameters()}

    groups: Dict[str, list] = {"memory_values": [], "memory_keys": [],
                               "decay": [], "no_decay": []}
    seen = set()
    for p in model.parameters():
        if not p.requires_grad or id(p) in seen:
            continue
        seen.add(id(p))
        if id(p) in mem_value_ids:
            groups["memory_values"].append(p)
        elif id(p) in mem_key_ids:
            groups["memory_keys"].append(p)
        elif p.dim() >= 2:
            groups["decay"].append(p)
        else:
            groups["no_decay"].append(p)

    lr_keys = cfg.lr if cfg.lr_memory_keys is None else cfg.lr_memory_keys
    spec = [
        ("memory_values", cfg.lr_memory_values, cfg.weight_decay_memory),
        ("memory_keys", lr_keys, cfg.weight_decay_memory),
        ("decay", cfg.lr, cfg.weight_decay),
        ("no_decay", cfg.lr, 0.0),
    ]
    param_groups = [
        {"name": name, "params": groups[name], "lr": lr, "weight_decay": wd,
         "initial_lr": lr}
        for name, lr, wd in spec if groups[name]
    ]
    return torch.optim.AdamW(param_groups, lr=cfg.lr, betas=tuple(cfg.betas), eps=cfg.eps)


def cosine_warmup(step: int, warmup: int, total: int, min_ratio: float) -> float:
    """Multiplier on each group's base LR. Linear warmup then cosine to min_ratio."""
    if warmup > 0 and step < warmup:
        return (step + 1) / warmup
    if total <= warmup:
        return 1.0
    progress = (step - warmup) / max(1, total - warmup)
    progress = min(1.0, max(0.0, progress))
    return min_ratio + (1.0 - min_ratio) * 0.5 * (1.0 + math.cos(math.pi * progress))


# ----------------------------------------------------------------------------- trainer
class Trainer:
    def __init__(self, cfg: TrainConfig, device: Optional[torch.device] = None):
        self.cfg = cfg
        self.device = device or pick_device(cfg.runtime.device)
        self.out_dir = Path(cfg.runtime.out_dir)
        self.out_dir.mkdir(parents=True, exist_ok=True)

        torch.manual_seed(cfg.train.seed)

        model_kw = dict(cfg.model)
        self.gpt_config = GPTConfig(**model_kw)
        self.model = GPT(self.gpt_config).to(self.device)
        self.optimizer = build_optimizer(self.model, cfg.train)
        self.scheduler = torch.optim.lr_scheduler.LambdaLR(
            self.optimizer,
            lambda s: cosine_warmup(s, cfg.train.warmup_steps, cfg.train.steps,
                                    cfg.train.min_lr_ratio))
        self.data = build_dataset(
            cfg.data.kind, vocab_size=self.gpt_config.vocab_size,
            seq_len=self.gpt_config.block_size, seed=cfg.data.seed,
            **({} if cfg.data.kind in ("random", "a", "uniform")
               else dict(chunk_len=cfg.data.chunk_len, n_distinct=cfg.data.n_distinct)))

        self.step = 0
        self.tokens_seen = 0
        self.peak_mem = 0
        self.history: List[dict] = []

        mem = self.model.memory_layers
        self.usage = SlotUsageCounter({i: m.n_slots for i, m in mem.items()}) \
            if (cfg.train.track_slot_usage and mem) else None
        self.read_writer: Optional[ReadLogWriter] = None
        if cfg.train.read_logging and mem:
            self.read_writer = ReadLogWriter(
                self.out_dir / "readlog",
                n_slots={i: m.n_slots for i, m in mem.items()},
                heads={i: m.n_heads for i, m in mem.items()},
                topk={i: m.topk for i, m in mem.items()},
                store_weights=cfg.train.read_log_weights)
        # the layers must expose their reads for EITHER consumer; slot-usage tracking
        # alone is much cheaper than the full log (a bincount, no disk write) but it
        # still costs a device->host copy per step, so it is off for the speed baseline
        self.model.set_read_logging(
            bool(mem) and (bool(cfg.train.read_logging) or bool(cfg.train.track_slot_usage)))

        self.csv_path = self.out_dir / "log.csv"
        self._csv_started = self.csv_path.exists()

    # ---- bookkeeping --------------------------------------------------------
    def save_initial_weights(self) -> Path:
        """Step-0 snapshot, so later analysis can tell learned structure from init."""
        path = self.out_dir / "init_weights.pt"
        torch.save({"step": 0,
                    "model": {k: v.detach().cpu().clone()
                              for k, v in self.model.state_dict().items()},
                    "config": self.config_dict()}, path)
        return path

    def config_dict(self) -> dict:
        return {"name": self.cfg.name, "model": self.cfg.model,
                "data": asdict(self.cfg.data), "train": asdict(self.cfg.train),
                "runtime": asdict(self.cfg.runtime),
                "ffn_types": self.gpt_config.ffn_types}

    def write_meta(self) -> Path:
        mem = self.model.memory_layers
        meta = {
            "config": self.config_dict(),
            "device": str(self.device),
            "param_counts": self.model.param_counts(),
            "tokens_per_step": self.cfg.tokens_per_step,
            "optimizer_groups": [
                {"name": g.get("name"), "lr": g["lr"],
                 "weight_decay": g["weight_decay"],
                 "n_tensors": len(g["params"]),
                 "n_params": sum(p.numel() for p in g["params"])}
                for g in self.optimizer.param_groups],
            "memory_layers": {
                str(i): {"kind": m.kind, "n_slots": m.n_slots, "heads": m.n_heads,
                         "topk": m.topk, "reads_per_token": m.reads_per_token,
                         "readlog_bytes_per_token": bytes_per_token(
                             m.n_slots, m.n_heads, m.topk,
                             self.cfg.train.read_log_weights)}
                for i, m in mem.items()},
        }
        path = self.out_dir / "meta.json"
        path.write_text(json.dumps(meta, indent=2, default=str))
        return path

    def _log_csv(self, row: dict) -> None:
        mode = "a" if self._csv_started else "w"
        with open(self.csv_path, mode, newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=CSV_FIELDS)
            if not self._csv_started:
                w.writeheader()
                self._csv_started = True
            w.writerow({k: row.get(k, "") for k in CSV_FIELDS})

    # ---- checkpointing ------------------------------------------------------
    def save_checkpoint(self, path: Optional[Path] = None) -> Path:
        path = Path(path or self.out_dir / "ckpt.pt")
        torch.save({
            "step": self.step,
            "tokens_seen": self.tokens_seen,
            "peak_mem": self.peak_mem,
            "model": self.model.state_dict(),
            "optimizer": self.optimizer.state_dict(),
            "scheduler": self.scheduler.state_dict(),
            "rng": get_rng_states(self.device),
            "config": self.config_dict(),
        }, path)
        return path

    def load_checkpoint(self, path: str | Path) -> None:
        ck = torch.load(path, map_location=self.device, weights_only=False)
        self.model.load_state_dict(ck["model"])
        self.optimizer.load_state_dict(ck["optimizer"])
        self.scheduler.load_state_dict(ck["scheduler"])
        set_rng_states(ck["rng"], self.device)
        self.step = int(ck["step"])
        self.tokens_seen = int(ck.get("tokens_seen", 0))
        self.peak_mem = int(ck.get("peak_mem", 0))

    # ---- the loop -----------------------------------------------------------
    def train_step(self) -> dict:
        cfg = self.cfg.train
        self.model.train()
        t0 = time.perf_counter()
        self.optimizer.zero_grad(set_to_none=True)

        total_loss = 0.0
        want_reads = (self.read_writer is not None or self.usage is not None)
        log_this = (self.read_writer is not None and
                    (cfg.read_log_steps == 0 or self.step < cfg.read_log_steps))

        for micro in range(cfg.grad_accum_steps):
            x, y = self.data.get_batch(self.step, cfg.micro_batch_size, micro, self.device)
            _, loss = self.model(x, y)
            total_loss += loss.item()
            (loss / cfg.grad_accum_steps).backward()
            if want_reads:
                reads = self.model.read_logs()
                if reads:
                    if self.usage is not None:
                        self.usage.update(reads)
                    if log_this:
                        self.read_writer.append(self.step, reads)

        gnorm = float("nan")
        if cfg.grad_clip > 0:
            gnorm = float(torch.nn.utils.clip_grad_norm_(
                self.model.parameters(), cfg.grad_clip))
        self.optimizer.step()
        self.scheduler.step()

        synchronize(self.device)
        dt = time.perf_counter() - t0
        tokens = self.cfg.tokens_per_step
        self.tokens_seen += tokens
        self.step += 1
        mem_now = peak_memory_bytes(self.device)
        self.peak_mem = max(self.peak_mem, mem_now)

        lrs = {g.get("name"): g["lr"] for g in self.optimizer.param_groups}
        return {
            "step": self.step,
            "loss": total_loss / cfg.grad_accum_steps,
            "lr": lrs.get("decay", lrs.get("no_decay", 0.0)),
            "lr_memory": lrs.get("memory_values", ""),
            "step_time_s": dt,
            "tokens_per_s": tokens / dt if dt > 0 else 0.0,
            "tokens_seen": self.tokens_seen,
            "peak_mem_bytes": mem_now,
            "grad_norm": gnorm,
        }

    def train(self, steps: Optional[int] = None, progress: bool = True) -> List[dict]:
        cfg = self.cfg.train
        target = self.step + (steps if steps is not None else cfg.steps - self.step)
        if self.step == 0:
            self.save_initial_weights()
            self.write_meta()
        reset_peak_memory(self.device)

        while self.step < target:
            row = self.train_step()
            self.history.append(row)
            if cfg.log_every and (self.step % cfg.log_every == 0 or self.step == target):
                self._log_csv(row)
                if progress:
                    print(f"step {row['step']:5d}  loss {row['loss']:.4f}  "
                          f"{row['step_time_s']*1000:7.1f} ms  "
                          f"{row['tokens_per_s']:9.0f} tok/s  "
                          f"mem {row['peak_mem_bytes']/1e9:5.2f} GB", flush=True)
            if cfg.ckpt_every and self.step % cfg.ckpt_every == 0:
                self.save_checkpoint()

        if self.read_writer is not None:
            self.read_writer.close()
        if self.usage is not None:
            self.usage.save(self.out_dir / "slot_usage.npz")
            (self.out_dir / "slot_usage.json").write_text(
                json.dumps({str(k): v for k, v in self.usage.stats().items()}, indent=2))
        return self.history


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--config", required=True)
    ap.add_argument("--set", nargs="*", default=[], dest="overrides",
                    help="section.key=value overrides, e.g. train.steps=50")
    ap.add_argument("--resume", default=None, help="checkpoint to resume from")
    ap.add_argument("--steps", type=int, default=None, help="override number of steps to run")
    ap.add_argument("--save-final", action="store_true")
    args = ap.parse_args(argv)

    cfg = load_config(args.config, args.overrides)
    tr = Trainer(cfg)
    print(f"[{cfg.name}] device={tr.device}  params={tr.model.param_counts()}")
    if args.resume:
        tr.load_checkpoint(args.resume)
        print(f"  resumed at step {tr.step}")
    tr.train(steps=args.steps)
    if args.save_final or cfg.train.ckpt_every == 0:
        p = tr.save_checkpoint()
        print(f"  saved {p}")
    empty_cache(tr.device)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
