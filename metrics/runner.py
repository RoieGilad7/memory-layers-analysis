"""Run every checkpoint metric on one verified, reproducible slice."""

from dataclasses import dataclass
from pathlib import Path
import torch
from . import (
    c4,
    c6,
    e1,
    e2,
    frequency,
    q1,
    q2,
    resources,
    u1,
    u4,
    v2,
    whole_memory_off,
    x2,
)
from .bundle import load_v1_slice
from .checkpoint import load_roie_model
from .scoring import V1Scorer


@dataclass
class Context:
    path: Path
    corpus: object
    model: object
    meta: dict
    baseline: dict
    scorer: V1Scorer
    evaluator: object
    seed: int
    permutations: int
    lesion_size: int
    controls: int
    max_prefix: int
    discovery_reads: list
    eval_reads: list
    dense_matrix: object = None


MEMORY_METRICS = {
    "U1": u1,
    "U4": u4,
    "V2": v2,
    "C4": c4,
    "C6": c6,
    "E1": e1,
    "E2": e2,
    "Whole layer off": whole_memory_off,
}


def _read_traces(ctx):
    _, discovery = ctx.evaluator.documents("discovery", collect=True)
    for read in discovery:
        values = read.pop("vectors")
        read["weighted_norms"] = [
            float(w * n)
            for w, n in zip(read["weights"], values.norm(dim=-1).tolist(), strict=True)
        ]
    ctx.discovery_reads = discovery
    _, ctx.eval_reads = ctx.evaluator.documents("eval", collect=True)
    for fact in ctx.corpus.facts:
        if fact["split"] == "eval":
            _, sites = ctx.scorer.score(fact, collect=True)
            ctx.eval_reads.extend(sites)


def _dense_reference(ctx, path):
    dense, meta = load_roie_model(path, ctx.corpus, "cpu", data_v1=True)
    config, ref = ctx.meta["report_config"], meta["report_config"]
    if (
        meta["style"] != "dense"
        or any(
            config[k] != ref[k]
            for k in (
                "n_layer",
                "n_embd",
                "n_head",
                "vocab_size",
                "block_size",
                "dropout",
                "bias",
                "tie_embeddings",
            )
        )
        or any(ctx.meta[k] != meta[k] for k in ("step", "tokens_seen"))
        or ctx.meta["data_v1"]["data_seed"] != meta["data_v1"]["data_seed"]
    ):
        raise ValueError(
            "Dense reference must have the same backbone and training budget"
        )
    return (
        dense.gpt.transformer.h[ctx.meta["layer_index"]]
        .mlp.c_proj.weight.detach()
        .T.contiguous()
    )


def evaluate(checkpoint, corpus, args):
    path = Path(checkpoint).expanduser().resolve()
    if not path.is_file():
        raise FileNotFoundError(f"No checkpoint at {path}")
    if args.device == "cuda":
        torch.cuda.reset_peak_memory_stats()
    model, meta = load_roie_model(path, corpus, args.device, args.layer, data_v1=True)
    scorer = V1Scorer(model, corpus, args.device)
    print(f"Checking native scores for {path.name}", flush=True)
    baseline = scorer.check_baselines()
    ctx = Context(
        path,
        corpus,
        model,
        meta,
        baseline,
        scorer,
        scorer.evaluator,
        args.seed,
        args.permutations,
        args.lesion_size,
        args.controls,
        args.max_prefix,
        [],
        [],
    )
    config = meta["config"]
    tokens = (
        0 if meta["data_v1"]["status"] == "initialization_only" else meta["tokens_seen"]
    )
    report = dict(
        checkpoint=str(path),
        step=meta["step"],
        layer_index=meta["layer_index"],
        device=args.device,
        tokens_seen=tokens,
        data_sha256=corpus.fingerprint,
        provenance=meta["data_v1"],
        slice=corpus.selection,
        model=dict(
            config=meta["report_config"],
            seed=config["train"]["seed"],
            train_settings={
                k: v
                for k, v in config["train"].items()
                if k not in ("seed", "log_every", "ckpt_every")
            },
        ),
        analysis=dict(
            slice_seed=args.seed,
            people_per_tier=args.people_per_tier,
            docs_per_subject=args.docs_per_subject,
            doc_tokens=args.doc_tokens,
            permutations=args.permutations,
            lesion_size=args.lesion_size,
            controls=args.controls,
            max_prefix=args.max_prefix,
        ),
        parity=dict(passed=baseline["passed"], **baseline["parity"]),
        metrics={},
    )
    metrics = report["metrics"]
    metrics["Q1"] = q1.run(ctx)
    metrics["Q2"] = q2.run(ctx)
    metrics["Frequency"] = frequency.run(ctx)
    if baseline["passed"] and model.memory is not None:
        if args.dense:
            ctx.dense_matrix = _dense_reference(ctx, args.dense)
        _read_traces(ctx)
    for key, metric in MEMORY_METRICS.items():
        if baseline["passed"] and model.memory is not None:
            print(f"Measuring {key}", flush=True)
            metrics[key] = metric.run(ctx)
        else:
            reason = (
                "Checkpoint has no memory layer."
                if model.memory is None
                else "Native baseline check failed."
            )
            metrics[key] = dict(
                title=key, columns=[], rows=[], status=reason, result=None
            )
    metrics["Resources"] = resources.run(ctx)
    metrics["X2"] = (
        x2.run(report, args.x2_margin)
        if baseline["passed"]
        else dict(
            title="Learned versus frozen keys",
            columns=[],
            rows=[],
            result=None,
            status="Native baseline check failed.",
        )
    )
    return report
