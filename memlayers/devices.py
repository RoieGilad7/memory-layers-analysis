"""Device selection and device-agnostic memory / sync helpers.

Priority is cuda > mps > cpu so the same code runs on a Colab T4 and on this Mac.
"""
from __future__ import annotations

import torch


def pick_device(requested: str | None = None) -> torch.device:
    if requested and requested != "auto":
        return torch.device(requested)
    if torch.cuda.is_available():
        return torch.device("cuda")
    if torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


def synchronize(device: torch.device) -> None:
    """Block until queued work on `device` is done, so timings mean something."""
    if device.type == "cuda":
        torch.cuda.synchronize()
    elif device.type == "mps":
        torch.mps.synchronize()


def peak_memory_bytes(device: torch.device) -> int:
    """Peak device memory in bytes.

    cuda: max_memory_allocated (tensor bytes, high-water mark).
    mps:  driver_allocated_memory (total the Metal driver holds for this process).
          There is no per-process high-water-mark API on MPS, so this is an
          instantaneous reading and must be sampled at the point of interest.
    """
    if device.type == "cuda":
        return int(torch.cuda.max_memory_allocated())
    if device.type == "mps":
        return int(torch.mps.driver_allocated_memory())
    return 0


def reset_peak_memory(device: torch.device) -> None:
    if device.type == "cuda":
        torch.cuda.reset_peak_memory_stats()
    elif device.type == "mps":
        torch.mps.empty_cache()


def empty_cache(device: torch.device) -> None:
    if device.type == "cuda":
        torch.cuda.empty_cache()
    elif device.type == "mps":
        torch.mps.empty_cache()


def get_rng_states(device: torch.device) -> dict:
    states = {"cpu": torch.get_rng_state()}
    if device.type == "cuda" and torch.cuda.is_available():
        states["cuda"] = torch.cuda.get_rng_state_all()
    elif device.type == "mps" and hasattr(torch.mps, "get_rng_state"):
        states["mps"] = torch.mps.get_rng_state()
    return states


def set_rng_states(states: dict, device: torch.device) -> None:
    if "cpu" in states:
        torch.set_rng_state(states["cpu"].to(torch.uint8).cpu())
    if "cuda" in states and torch.cuda.is_available():
        torch.cuda.set_rng_state_all([s.to(torch.uint8).cpu() for s in states["cuda"]])
    if "mps" in states and hasattr(torch.mps, "set_rng_state"):
        torch.mps.set_rng_state(states["mps"].to(torch.uint8).cpu())
