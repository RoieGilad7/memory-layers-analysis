"""Command-line entry point and report persistence."""

import argparse
import hashlib
import json
import os
from pathlib import Path
from tempfile import NamedTemporaryFile
import torch
from .bundle import load_v1_slice
from .display import render, serve
from .runner import evaluate
from .x2 import lock
from .x2.paired import paired, summary_rows


def positive(value):
    n = int(value)
    if n < 1:
        raise argparse.ArgumentTypeError("expected a positive integer")
    return n


def fractions(value):
    out = tuple(sorted({float(x) for x in value.split(",") if x.strip()}))
    if not out or any(not 0 < f <= 1 for f in out):
        raise argparse.ArgumentTypeError("expected comma-separated fractions in (0, 1]")
    return out


def fact_cohort(path):
    """A JSON list of fact ids (person-attribute), or {"fact_ids": [...]}."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    ids = data["fact_ids"] if isinstance(data, dict) else data
    if not ids or not all(isinstance(i, str) and "-" in i for i in ids):
        raise argparse.ArgumentTypeError("expected a non-empty list of fact ids")
    return tuple(sorted(set(ids)))


def default_bundle():
    if "MEMLAYERS_DATA_V1" in os.environ:
        return Path(os.environ["MEMLAYERS_DATA_V1"])
    repo = Path(__file__).resolve().parents[1]
    for root in (repo / "data/v1", repo.parent / "tmp/hf-release-audit/bundle"):
        if (root / "tokens/train.bin").is_file():
            return root
    return repo / "data/v1"


def save(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    with NamedTemporaryFile(
        mode="w", encoding="utf-8", dir=path.parent, delete=False
    ) as stream:
        tmp = Path(stream.name)
        try:
            stream.write(content)
        except BaseException:
            stream.close()
            tmp.unlink(missing_ok=True)
            raise
    try:
        os.replace(tmp, path)
    finally:
        tmp.unlink(missing_ok=True)


def main(argv=None):
    p = argparse.ArgumentParser(
        description="Evaluate a native data-v1 checkpoint and display its metrics."
    )
    p.add_argument("checkpoint", nargs="?")
    p.add_argument("--bundle", type=Path, default=default_bundle())
    p.add_argument("--tokenizer-cache", type=Path)
    p.add_argument("--output-dir", type=Path, default=Path("runs/metrics"))
    p.add_argument(
        "--no-serve", action="store_true", help="save HTML and JSON and exit"
    )
    p.add_argument(
        "--no-browser",
        action="store_true",
        help="serve the viewer without opening a browser",
    )
    p.add_argument("--port", type=int, default=0)
    p.add_argument("--layer", type=int)
    p.add_argument(
        "--dense", type=Path, help="optional dense reference checkpoint for C6"
    )
    p.add_argument("--seed", type=int, default=17)
    # Slice sizes. People are the sampled unit for Q2 and E2, documents for
    # Q1, U4 and E1; one person per tier cannot separate effects from noise.
    p.add_argument("--people-per-tier", type=positive, default=10)
    p.add_argument(
        "--frequent-people",
        type=positive,
        default=40,
        help="frequent-tier people (the E2 cohort); overrides --people-per-tier",
    )
    p.add_argument("--docs-per-subject", type=positive, default=16)
    p.add_argument("--doc-tokens", type=positive, default=128)
    p.add_argument(
        "--include-untrained-subjects",
        action="store_true",
        help="also score held-out subjects absent from training (phase 2)",
    )
    p.add_argument("--controls", type=positive, default=3)
    p.add_argument(
        "--e1-fractions",
        type=fractions,
        default=(0.1, 0.25, 0.5),
        help="E1 lesion doses: shares of each subject's excess reads to cover",
    )
    p.add_argument("--e1-max-slots", type=positive, default=1024)
    p.add_argument("--max-prefix", type=positive, default=16)
    p.add_argument(
        "--e2-facts",
        type=fact_cohort,
        help="JSON list of fact ids: a fixed E2 cohort, rediscovered per checkpoint",
    )
    p.add_argument("--collateral-rows", type=positive, default=200)
    p.add_argument("--permutations", type=positive, default=199)
    p.add_argument(
        "--v2-stride",
        type=positive,
        default=8,
        help="keep value vectors for every n-th position and fact (memory bound)",
    )
    p.add_argument("--rank-rows", type=positive, default=512)
    p.add_argument(
        "--training-check",
        type=Path,
        help="the run's training_check.json when it is not next to the checkpoint",
    )
    p.add_argument("--device", choices=("cpu", "cuda", "mps"), default="cpu")
    p.add_argument("--threads", type=positive, default=2)
    p.add_argument(
        "--x2-margin",
        type=Path,
        help="locked X2 margin JSON for a frozen-key checkpoint",
    )
    p.add_argument(
        "--calibrate-x2",
        nargs="+",
        metavar="LEARNED_REPORT",
        help="lock X2 margins from learned seed reports",
    )
    p.add_argument(
        "--x2-pair",
        nargs=2,
        metavar=("LEARNED_REPORT", "FROZEN_REPORT"),
        help="paired per-item comparison of a learned run and its frozen-key twin",
    )
    args = p.parse_args(argv)
    if args.x2_pair:
        learned, twin = (
            json.loads(Path(x).read_text(encoding="utf-8")) for x in args.x2_pair
        )
        result = paired(learned, twin, seed=args.seed)
        dest = args.output_dir / (
            f"x2-paired-{Path(args.x2_pair[0]).stem}-{Path(args.x2_pair[1]).stem}.json"
        )
        save(dest, json.dumps(result, indent=2, allow_nan=False))
        for row in summary_rows(result):
            print("\t".join("" if v is None else str(v) for v in row))
        print(dest)
        return 0
    if args.output_dir.resolve().is_relative_to(args.bundle.resolve()):
        p.error("Choose an output directory outside the frozen bundle")
    if args.calibrate_x2:
        if args.checkpoint or args.x2_margin:
            p.error(
                "Use --calibrate-x2 separately before evaluating a frozen checkpoint"
            )
        dest = args.output_dir / "x2-margins.json"
        save(dest, json.dumps(lock(args.calibrate_x2), indent=2, allow_nan=False))
        print(dest)
        return 0
    if not args.checkpoint:
        p.error("provide a checkpoint path")
    if not Path(args.checkpoint).expanduser().is_file():
        p.error(f"Checkpoint does not exist: {args.checkpoint}")
    if not (args.bundle / "tokens/train.bin").is_file():
        p.error(
            f"Frozen data-v1 missing at {args.bundle}. Run python -m data.fetch --version v1 or pass --bundle."
        )
    if not 0 <= args.port <= 65535:
        p.error("port must be between 0 and 65535")
    if torch.device(args.device).type == "cuda" and not torch.cuda.is_available():
        p.error("CUDA unavailable")
    cache = args.tokenizer_cache or args.bundle.resolve().parent / "gpt2-cache"
    if args.tokenizer_cache:
        os.environ["TIKTOKEN_CACHE_DIR"] = str(cache)
    elif cache.is_dir():
        os.environ.setdefault("TIKTOKEN_CACHE_DIR", str(cache))
    torch.set_num_threads(args.threads)
    corpus = load_v1_slice(
        args.bundle,
        seed=args.seed,
        people_per_tier=args.people_per_tier,
        tier_people={"frequent": args.frequent_people},
        include_people=sorted(
            {fact_id.rsplit("-", 1)[0] for fact_id in (args.e2_facts or ())}
        ),
        docs_per_subject=args.docs_per_subject,
        doc_tokens=args.doc_tokens,
        include_untrained_subjects=args.include_untrained_subjects,
    )

    def run(path):
        report = evaluate(path, corpus, args)
        suffix = hashlib.sha256(report["checkpoint"].encode()).hexdigest()[:8]
        stem = f"{Path(path).stem}-{suffix}"
        page = render(report)
        save(
            args.output_dir / (stem + ".json"),
            json.dumps(report, indent=2, allow_nan=False),
        )
        html = args.output_dir / (stem + ".html")
        save(html, page)
        print(f"Report: {html.resolve()}", flush=True)
        return report

    report = run(args.checkpoint)
    if not args.no_serve:
        serve(report, run, open_browser=not args.no_browser, port=args.port)
    return 0 if report["parity"]["passed"] else 1
