"""Q2: fact recall by person exposure and prompt role."""

from collections import defaultdict
from statistics import fmean
from ..matching import top1_credit, gold_margin
from ..stats import cluster_bootstrap


def fact_metrics(scores, answer):
    gold = scores[answer]
    above = sum(x > gold for x in scores)
    tied = scores.count(gold)
    return {
        "candidates": len(scores),
        "gold_logp": gold,
        "margin": gold_margin(scores, answer),
        "rank": 1 + above + (tied - 1) / 2,
        "rank_fraction": (1 + above + (tied - 1) / 2) / len(scores),
        "top1": top1_credit(scores, answer),
        # Roie's Q2 probe counts any gold tied for best as rank 1 and correct.
        "native_rank_convention": 1 + above,
        "native_top1_convention": int(above == 0),
    }


def _fact_summary(groups):
    fields = (
        "top1",
        "rank",
        "rank_fraction",
        "margin",
        "gold_logp",
        "native_top1_convention",
    )
    summary = {}
    for label, rows in groups.items():
        # People are the sampled units, so the interval resamples people.
        ci = cluster_bootstrap([r["top1"] for r in rows], [r["person"] for r in rows])
        summary[label] = {
            "n": len(rows),
            "people": ci["clusters"],
            **{k: fmean(row[k] for row in rows) for k in fields},
            "top1_ci": [ci["lo"], ci["hi"]],
        }
    return summary


def check_facts(scorer, parity, atol, rtol):
    intact = {}
    fact_rows = []
    groups = defaultdict(list)
    paraphrase_contexts = defaultdict(list)
    for f in scorer.corpus.facts:
        scores, _ = scorer.score(f)
        reference = scorer._native_scores(f)
        measured, native = fact_metrics(scores, f["answer"]), fact_metrics(
            reference, f["answer"]
        )
        errors = [abs(v - r) for v, r in zip(scores, reference, strict=True)]
        largest = max(errors)
        failures = sum(e > atol + rtol * abs(r) for e, r in zip(errors, reference))
        parity["candidate_scores_checked"] += len(scores)
        parity["max_candidate_abs_error"] = max(
            parity["max_candidate_abs_error"], largest
        )
        parity["candidate_score_failures"] += failures
        parity["native_rank_mismatches"] += int(
            measured["native_rank_convention"] != native["native_rank_convention"]
        )
        row = {
            k: f[k]
            for k in ("row_id", "fact_id", "person", "attribute", "tier", "role")
        }
        row.update({k: f[k] for k in ("template_id", "preceding_fact_count") if k in f})
        row.update(
            measured,
            native_reference_rank=native["native_rank_convention"],
            native_reference_top1=native["native_top1_convention"],
            max_abs_error=largest,
            candidate_score_failures=failures,
        )
        fact_rows.append(row)
        groups[f"{f['tier']}/{f['role']}"].append(row)
        if f["role"] == "paraphrase" and "preceding_fact_count" in f:
            context = (
                "with_preceding_facts"
                if f["preceding_fact_count"]
                else "no_preceding_facts"
            )
            paraphrase_contexts[f"{f['tier']}/{context}"].append(row)
        intact[f["row_id"]] = (f, tuple(scores))

    return {
        "rows": fact_rows,
        "by_tier_role": _fact_summary(groups),
        "paraphrases_by_tier_context": _fact_summary(paraphrase_contexts),
    }, intact


def run(ctx):
    facts = ctx.baseline["facts"]
    columns = [
        "Exposure / wording",
        "People",
        "Prompts",
        "Top-1",
        "Top-1 95% CI",
        "Mean rank",
        "Margin (nats)",
    ]

    def row(g, r):
        ci = r.get("top1_ci") or [None, None]
        interval = None if ci[0] is None else f"{ci[0]:.3f} to {ci[1]:.3f}"
        return [g, r.get("people"), r["n"], r["top1"], interval, r["rank"], r["margin"]]

    rows = [row(g, r) for g, r in sorted(facts["by_tier_role"].items())]
    for g, r in sorted(facts["paraphrases_by_tier_context"].items()):
        rows.append(row(g, r))
    return dict(title="Fact recall", columns=columns, rows=rows, result=facts)
