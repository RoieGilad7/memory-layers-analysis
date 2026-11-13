"""E1. Selectivity of a subject-directed memory lesion on held-out text.

Plan (Methodology, E1): switch off subject D's top-m slots from U4's TF-IDF
ranking and compare with m matched random slots. The plan does not fix m. The
headline uses `lesion_size`; `lesion_sizes` reruns the same test at other m so
the sample-size pilot can choose m.
"""

from functools import lru_cache
import random
from statistics import fmean

from ..matching import match_audit, matched_masks, slot_profiles
from ..u4 import rank_subject_slots


def subject_report(discovery, score_docs, profiles, lesion_size, controls, rng):
    score = lru_cache(maxsize=256)(score_docs)
    base = score(())
    rows = {}
    ranked = rank_subject_slots(discovery)
    for subject in base:
        selected = tuple(sorted(ranked.get(subject, [])[:lesion_size]))
        if len(base) < 2 or not selected:
            rows[subject] = {
                "slots": list(selected),
                "specificity_excess_nll": None,
                "status": (
                    "no_off_target_subject" if len(base) < 2 else "no_discovery_targets"
                ),
            }
            continue

        def contrast(mask):
            damaged = score(mask)
            deltas = {s: float(damaged[s] - base[s]) for s in base}
            off_target = fmean(d for s, d in deltas.items() if s != subject)
            return deltas, deltas[subject] - off_target

        deltas, effect = contrast(selected)
        masks = matched_masks(selected, profiles, profiles, controls, rng)
        null = [contrast(mask)[1] for mask in masks]
        rows[subject] = {
            "slots": list(selected),
            "delta_nll_by_subject": deltas,
            "target_minus_other_nll": effect,
            "matched_contrasts_nll": null,
            "distinct_controls": len(set(masks)),
            "status": "matched" if null else "no_matched_controls",
            "specificity_excess_nll": effect - fmean(null) if null else None,
            **match_audit(selected, masks, profiles),
        }
    excess = [
        r["specificity_excess_nll"]
        for r in rows.values()
        if r["specificity_excess_nll"] is not None
    ]
    return {
        "subjects": rows,
        "matched_subjects": len(excess),
        "mean_specificity_excess_nll": fmean(excess) if excess else None,
    }


def run(ctx):
    discovery = [r for r in ctx.discovery_reads if r["subject"] != "bio"]

    def score_docs(mask):
        quality = (
            ctx.evaluator.documents("eval", mask=mask)[0]
            if mask
            else ctx.baseline["documents"]["eval"]
        )
        return {s: q["nll"] for s, q in quality["by_subject"].items() if s != "bio"}

    profiles = slot_profiles(discovery)
    result = subject_report(
        discovery,
        score_docs,
        profiles,
        ctx.lesion_size,
        ctx.controls,
        random.Random(ctx.seed),
    )
    result["lesion_size"] = ctx.lesion_size
    # Same test at other m; each size gets its own control draw from the seed.
    by_size = {}
    for m in sorted(set(getattr(ctx, "lesion_sizes", ())) | {ctx.lesion_size}):
        other = (
            result
            if m == ctx.lesion_size
            else subject_report(
                discovery,
                score_docs,
                profiles,
                m,
                ctx.controls,
                random.Random(ctx.seed),
            )
        )
        by_size[str(m)] = {
            "matched_subjects": other["matched_subjects"],
            "mean_specificity_excess_nll": other["mean_specificity_excess_nll"],
        }
    result["by_lesion_size"] = by_size
    rows = [
        [
            s,
            len(d["slots"]),
            d.get("target_minus_other_nll"),
            d.get("distinct_controls", 0),
            d["specificity_excess_nll"],
            d["status"].replace("_", " "),
        ]
        for s, d in sorted(result["subjects"].items())
    ]
    return dict(
        title="Subject-specific ablation",
        columns=[
            "Subject",
            "Slots",
            "Target − other ΔNLL (nats)",
            "Controls",
            "Excess over control (nats)",
            "Status",
        ],
        rows=rows,
        result=result,
    )
