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
    controls: int
    max_prefix: int
    discovery_reads: list
    eval_reads: list
    dense_matrix: object = None
    e1_fractions: tuple = (0.1, 0.25, 0.5)
    e1_max_slots: int = 1024
    e2_facts: tuple = ()
    collateral_rows: int = 200
    v2_stride: int = 1
    rank_rows: int = 512


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
    _, ctx.discovery_reads = ctx.evaluator.documents(
        "discovery", collect=True, keep_vectors=lambda doc, pos: False
    )
    # V2 needs value vectors; keeping them for every position of a large slice
    # costs heads*topk*d floats per token. Keep every v2_stride-th position.
    stride = getattr(ctx, "v2_stride", 1)
    _, ctx.eval_reads = ctx.evaluator.documents(
        "eval", collect=True, keep_vectors=lambda doc, pos: pos % stride == 0
    )
    evaluated = [f for f in ctx.corpus.facts if f["split"] == "eval"]
    for i, fact in enumerate(evaluated):
        _, sites = ctx.scorer.score(fact, collect=True)
        if i % stride:
            sites = [ctx.evaluator.compact(site) for site in sites]
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


def training_gate(checkpoint, override=None):
    """The run's own training check (run_dir/training_check.json), if present.

    Native layout: run_dir/checkpoints/step_NNNNNN.pt next to run_dir/training_check.json.
    A downloaded checkpoint can name the file explicitly with --training-check.
    """
    import json

    candidates = (
        [Path(override)]
        if override
        else [parent / "training_check.json" for parent in list(checkpoint.parents)[:3]]
    )
    for candidate in candidates:
        if candidate.is_file():
            data = json.loads(candidate.read_text(encoding="utf-8"))
            verdict = data.get("verdict")
            return dict(
                passed={"pass": True, "fail": False}.get(verdict),
                verdict=verdict,
                failed=data.get("failed", []),
                path=str(candidate),
            )
    if override:
        raise FileNotFoundError(f"No training check at {override}")
    return dict(passed=None, verdict=None, failed=[], path=None)


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
        args.controls,
        args.max_prefix,
        [],
        [],
        e1_fractions=tuple(args.e1_fractions),
        e1_max_slots=args.e1_max_slots,
        e2_facts=tuple(args.e2_facts or ()),
        collateral_rows=args.collateral_rows,
        v2_stride=args.v2_stride,
        rank_rows=args.rank_rows,
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
            e1_fractions=list(args.e1_fractions),
            e1_max_slots=args.e1_max_slots,
            e2_facts=list(args.e2_facts or ()),
            collateral_rows=args.collateral_rows,
            v2_stride=args.v2_stride,
            rank_rows=args.rank_rows,
            frequent_people=args.frequent_people,
            include_untrained_subjects=args.include_untrained_subjects,
            controls=args.controls,
            max_prefix=args.max_prefix,
        ),
        parity=dict(passed=baseline["passed"], **baseline["parity"]),
        training_check=training_gate(path, getattr(args, "training_check", None)),
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
