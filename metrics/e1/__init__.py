"""E1. Selectivity of a subject-directed memory lesion on held-out text.

Each subject's slots are ranked on discovery text by their excess reads over a
token-identity null (U4's profile). A lesion takes the shortest ranked prefix
whose excess covers a fraction of the subject's total positive excess, so lesion
size scales with how spread out the subject is rather than being a fixed slot
count. Several fractions give a dose curve. Matched controls use slots with the
same discovery read count and weighted output norm (factor-two calipers).
Every lesion also reports how much of each subject's eval-text reads and gate
mass it actually removed, so models with flatter or sharper gates can be
compared at equal removed mass.
"""

from collections import defaultdict
from functools import lru_cache
import random
from statistics import fmean

from ..matching import match_audit, matched_masks, slot_profiles
from ..u4 import subject_slot_excess

DEFAULT_FRACTIONS = (0.1, 0.25, 0.5)
PRIMARY_FRACTION = 0.25


def primary_fraction(fractions):
    fractions = sorted(fractions)
    if PRIMARY_FRACTION in fractions:
        return PRIMARY_FRACTION
    return fractions[len(fractions) // 2]


def lesion_prefix(ranked, fraction, max_slots):
    """Shortest prefix of (slot, excess) covering `fraction` of the total excess."""
    total = sum(excess for _, excess in ranked)
    if total <= 0:
        return ()
    covered, chosen = 0.0, []
    for slot, excess in ranked[:max_slots]:
        chosen.append(slot)
        covered += excess
        if covered >= fraction * total - 1e-12:
            break
    return tuple(sorted(chosen))


def exposure(eval_reads, slots):
    """Share of each subject's eval-text selections and gate mass on `slots`."""
    slots = set(slots)
    reads, gate = defaultdict(lambda: [0, 0]), defaultdict(lambda: [0.0, 0.0])
    for r in eval_reads:
        if r.get("cohort", "text") != "text":
            continue
        s = r["subject"]
        for slot, weight in zip(r["ids"], r["weights"], strict=True):
            hit = int(slot) in slots
            reads[s][0] += hit
            reads[s][1] += 1
            gate[s][0] += abs(float(weight)) * hit
            gate[s][1] += abs(float(weight))
    return {
        s: dict(
            read_share=reads[s][0] / reads[s][1] if reads[s][1] else None,
            gate_share=gate[s][0] / gate[s][1] if gate[s][1] else None,
        )
        for s in reads
    }


def _shares(exp, subject):
    target = exp.get(subject, {}).get("gate_share")
    others = [
        v["gate_share"]
        for s, v in exp.items()
        if s != subject and v["gate_share"] is not None
    ]
    return target, (fmean(others) if others else None)


def subject_report(
    discovery,
    score_docs,
    profiles,
    controls,
    rng,
    *,
    fractions=DEFAULT_FRACTIONS,
    max_slots=1024,
    eval_reads=(),
):
    score = lru_cache(maxsize=512)(score_docs)
    base = score(())
    ranked_by_subject = subject_slot_excess(discovery)
    primary = primary_fraction(fractions)
    rows = {}
    for subject in base:
        ranked = ranked_by_subject.get(subject, [])
        if len(base) < 2 or not ranked:
            rows[subject] = {
                "slots": [],
                "doses": [],
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

        doses = []
        for fraction in sorted(fractions):
            selected = lesion_prefix(ranked, fraction, max_slots)
            deltas, effect = contrast(selected)
            masks = matched_masks(selected, profiles, profiles, controls, rng)
            null = [contrast(mask)[1] for mask in masks]
            target_share, other_share = _shares(exposure(eval_reads, selected), subject)
            control_shares = [
                _shares(exposure(eval_reads, m), subject)[0] for m in masks
            ]
            control_shares = [c for c in control_shares if c is not None]
            doses.append(
                {
                    "excess_fraction": fraction,
                    "slots": list(selected),
                    "slot_count": len(selected),
                    "capped": len(selected) >= max_slots,
                    "delta_nll_by_subject": deltas,
                    "target_minus_other_nll": effect,
                    "matched_contrasts_nll": null,
                    "distinct_controls": len(set(masks)),
                    "status": "matched" if null else "no_matched_controls",
                    "specificity_excess_nll": effect - fmean(null) if null else None,
                    "target_eval_gate_share_removed": target_share,
                    "other_eval_gate_share_removed": other_share,
                    "control_target_eval_gate_share_removed": (
                        fmean(control_shares) if control_shares else None
                    ),
                    **match_audit(selected, masks, profiles),
                }
            )
        main = next(d for d in doses if d["excess_fraction"] == primary)
        rows[subject] = {**main, "doses": doses}
    excess = [
        r["specificity_excess_nll"]
        for r in rows.values()
        if r["specificity_excess_nll"] is not None
    ]
    curve = {}
    for fraction in sorted(fractions):
        values = [
            d["specificity_excess_nll"]
            for r in rows.values()
            for d in r["doses"]
            if d["excess_fraction"] == fraction
            and d["specificity_excess_nll"] is not None
        ]
        curve[str(fraction)] = fmean(values) if values else None
    return {
        "subjects": rows,
        "primary_excess_fraction": primary,
        "max_slots": max_slots,
        "matched_subjects": len(excess),
        "mean_specificity_excess_nll": fmean(excess) if excess else None,
        "mean_specificity_excess_nll_by_fraction": curve,
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

    result = subject_report(
        discovery,
        score_docs,
        slot_profiles(discovery),
        ctx.controls,
        random.Random(ctx.seed),
        fractions=tuple(getattr(ctx, "e1_fractions", DEFAULT_FRACTIONS)),
        max_slots=getattr(ctx, "e1_max_slots", 1024),
        eval_reads=getattr(ctx, "eval_reads", ()),
    )
    rows = []
    for s, d in sorted(result["subjects"].items()):
        for dose in d["doses"] or [d]:
            rows.append(
                [
                    s,
                    dose.get("excess_fraction"),
                    len(dose["slots"]),
                    dose.get("target_eval_gate_share_removed"),
                    dose.get("target_minus_other_nll"),
                    dose.get("distinct_controls", 0),
                    dose["specificity_excess_nll"],
                    dose["status"].replace("_", " "),
                ]
            )
    return dict(
        title="Subject-specific ablation",
        columns=[
            "Subject",
            "Excess covered",
            "Slots",
            "Eval gate mass removed",
            "Target − other ΔNLL (nats)",
            "Controls",
            "Excess over control (nats)",
            "Status",
        ],
        rows=rows,
        result=result,
    )
