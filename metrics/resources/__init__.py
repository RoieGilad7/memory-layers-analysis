"""Memory footprint and batch-one inference timing."""

from time import perf_counter
import csv
import math
import torch


def _sync(device):
    if device.type == "cuda":
        torch.cuda.synchronize(device)
    elif device.type == "mps":
        torch.mps.synchronize()


def _training_rate(ctx):
    """Only use a log row for this checkpoint's step, token count and bundle."""
    path = ctx.path.parent / "log.csv"
    if not path.is_file():
        return None
    with path.open(encoding="utf-8", newline="") as stream:
        rate = None
        for row in csv.DictReader(stream):
            if (
                row.get("step") == str(ctx.meta["step"])
                and row.get("tokens_seen") == str(ctx.meta["tokens_seen"])
                and row.get("data_sha256")
                in {ctx.corpus.fingerprint, ctx.corpus.fingerprint[:16]}
            ):
                try:
                    value = float(row["tokens_per_s"])
                    rate = value if math.isfinite(value) and value > 0 else None
                except (KeyError, ValueError, TypeError):
                    rate = None
        return rate


@torch.inference_mode()
def run(ctx):
    model = ctx.model
    device = next(model.parameters()).device
    seq = ctx.corpus.docs["eval"][0]["tokens"][:-1]
    tokens = torch.tensor([seq], device=device)
    for _ in range(2):
        model.gpt(tokens)
    _sync(device)
    start = perf_counter()
    for _ in range(10):
        model.gpt(tokens)
    _sync(device)
    elapsed = perf_counter() - start

    def bytes_used(params):
        return sum(p.numel() * p.element_size() for p in params)

    result = dict(
        checkpoint_bytes=ctx.path.stat().st_size,
        parameter_bytes=bytes_used(model.parameters()),
        memory_parameter_bytes=(
            bytes_used(model.memory.parameters()) if model.memory else 0
        ),
        optimizer_state_bytes=ctx.meta["optimizer_state_bytes"],
        forward_ms=100 * elapsed,
        inference_tokens_per_second=10 * len(seq) / elapsed,
        tokens_per_forward=len(seq),
        train_tokens_per_second=_training_rate(ctx),
        reads_per_token=ctx.meta["heads"] * ctx.meta["topk"],
        available_slots=ctx.meta["num_slots"],
        device=str(device),
        peak_cuda_bytes=(
            torch.cuda.max_memory_allocated(device) if device.type == "cuda" else None
        ),
    )
    headers = [
        ("Checkpoint", "checkpoint_bytes"),
        ("Model parameters", "parameter_bytes"),
        ("Memory parameters", "memory_parameter_bytes"),
        ("Optimizer state", "optimizer_state_bytes"),
        ("Peak CUDA allocation", "peak_cuda_bytes"),
    ]
    rows = [
        [label, result[key] / 2**20 if result[key] is not None else None, "MiB"]
        for label, key in headers
    ]
    rows.extend(
        [
            ["Routed reads per token", result["reads_per_token"], "reads"],
            ["Prefill latency", result["forward_ms"], "ms"],
            ["Prefill throughput", result["inference_tokens_per_second"], "tokens/s"],
            [
                "Training throughput (logged step)",
                result["train_tokens_per_second"],
                "tokens/s",
            ],
        ]
    )
    return dict(
        title="Storage and inference cost",
        columns=["Measure", "Value", "Unit"],
        rows=rows,
        result=result,
    )
