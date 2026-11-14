"""E2. Discovery-ranked cumulative slot lesions and a matched one-slot experiment."""

from collections import Counter, defaultdict
import random
from statistics import fmean

from ..matching import matched_masks, match_audit
from .single_slot import _discovery, _mean_outcome, _single_slot


def _sample_rows(rows, cap, seed):
    """At most `cap` rows, a fixed sample per fact; every row when cap is None.

    Only bounds run time: each masked set rescores this group, and with many
    people loaded the other-people group would be most of the corpus.
    """
    if cap is None or len(rows) <= cap:
        return rows
    return sorted(random.Random(seed).sample(rows, cap), key=lambda r: r["row_id"])


def _cumulative(ctx, discovered):
    facts, mass, profiles = discovered
    test = [row for row in ctx.corpus.facts if row["role"] == "test"]
    by_key = defaultdict(list)
    for row in test:
        by_key[row["fact_id"]].append(row)
    rng = random.Random(ctx.seed)
    collateral_cap = getattr(ctx, "collateral_rows", None)
    cap = getattr(ctx, "max_prefix", 16)
    if cap is not None and cap < 1:
        raise ValueError("Maximum tested prefix must be positive")
    records = {}
    for key, fact in sorted(facts.items()):
        rows = by_key[key]
        record = records[key] = {
            "eligible": fact["eligible"],
            "test_rows": [r["row_id"] for r in rows],
        }
        if not fact["eligible"] or not rows:
            record["status"] = (
                "unlearned_discovery" if not fact["eligible"] else "no_test_prompts"
            )
            continue
        base = _mean_outcome(ctx.scorer, rows, ())
        chance = fmean(1 / len(row["candidates"]) for row in rows)
        order = sorted(
            (s for s, weight in mass[key].items() if weight > 0),
            key=lambda s: (-mass[key][s], s),
        )
        record.update(
            baseline=base,
            chance=chance,
            ranked_discovery_reads=[
                {"slot": slot, "gate_mass": mass[key][slot]} for slot in order
            ],
            curve=[],
        )
        if base["top1_credit"] <= chance or not order:
            record["status"] = (
                "at_chance_on_test"
                if base["top1_credit"] <= chance
                else "no_discovery_reads"
            )
            continue
        tested = len(order) if cap is None else min(cap, len(order))
        for n in range(1, tested + 1):
            mask = tuple(order[:n])
            after = _mean_outcome(ctx.scorer, rows, mask)
            record["curve"].append({"n": n, **after})
            if after["top1_credit"] <= chance:
                break
        else:
            record["status"] = (
                "prefix_limit_reached"
                if tested < len(order)
                else "threshold_not_reached"
            )
            continue
        controls = matched_masks(mask, order, profiles, ctx.controls, rng)
        null = [_mean_outcome(ctx.scorer, rows, control) for control in controls]
        record.update(
            status="matched" if null else "no_matched_controls",
            core_slots=list(mask),
            core_size=n,
            core_fraction=n / len(order),
            distinct_controls=len(set(controls)),
            controls=null,
            matched_erasure_rate=(
                fmean(o["top1_credit"] <= chance for o in null) if null else None
            ),
            **match_audit(mask, controls, profiles),
        )
        collateral = record["collateral"] = {}
        for cohort, group in {
            "target": rows,
            "same_person_other_facts": [
                r for r in test if r["person"] == fact["person"] and r["fact_id"] != key
            ],
            "other_people": _sample_rows(
                [r for r in test if r["person"] != fact["person"]],
                collateral_cap,
                f"{ctx.seed}:{key}",
            ),
        }.items():
            collateral[cohort] = {
                "prompts": len(group),
                "intact": _mean_outcome(ctx.scorer, group, ()) if group else None,
                "masked": _mean_outcome(ctx.scorer, group, mask) if group else None,
            }
    matched = [r for r in records.values() if r["status"] == "matched"]
    return {
        "facts": records,
        "tested_prefix_limit": cap,
        "matched_facts": len(matched),
        "status_counts": dict(Counter(r["status"] for r in records.values())),
        "mean_matched_core_fraction": (
            fmean(r["core_fraction"] for r in matched) if matched else None
        ),
        "mean_matched_erasure_rate": (
            fmean(r["matched_erasure_rate"] for r in matched) if matched else None
        ),
    }


def discovery_rows(ctx):
    """Frequent-tier discovery prompts (the main E2 group).

    With a fixed fact list (`e2_facts`), only those facts, so every model is
    tested on the same facts. Slots are still found again per checkpoint.
    """
    cohort = set(getattr(ctx, "e2_facts", ()) or ())
    return sorted(
        (
            r
            for r in ctx.corpus.facts
            if r["role"] == "discovery"
            and (r["fact_id"] in cohort if cohort else r["tier"] == "frequent")
        ),
        key=lambda r: r["row_id"],
    )


def run(ctx):
    rows = discovery_rows(ctx)
    discovered = _discovery(ctx.scorer, rows)
    cumulative = _cumulative(ctx, discovered)
    single = _single_slot(ctx.scorer, ctx.corpus, discovered, ctx.seed, ctx.controls)
    table = []
    for key, r in cumulative["facts"].items():
        base, end, controls = r.get("baseline"), r.get("curve"), r.get("controls")
        drop = base["top1_credit"] - end[-1]["top1_credit"] if end else None
        matched = (
            base["top1_credit"] - fmean(o["top1_credit"] for o in controls)
            if controls
            else None
        )
        excess = (
            fmean(o["gold_logp"] for o in controls) - end[-1]["gold_logp"]
            if controls
            else None
        )
        table.append(
            [
                key,
                "Cumulative",
                end[-1]["n"] if end else None,
                drop,
                matched,
                excess,
                r["status"].replace("_", " "),
            ]
        )
    for group, effect in single["effects"].items():
        if not effect.get("rows"):
            continue
        target = single["target"]
        controls = effect["controls"]
        table.append(
            [
                target["fact_id"],
                f"Slot {target['slot']} · {group.replace('_', ' ')}",
                1,
                effect["target_damage"]["top1_credit_drop"],
                (
                    fmean(r["damage"]["top1_credit_drop"] for r in controls)
                    if controls
                    else None
                ),
                (
                    effect["target_minus_mean_control_damage"]["gold_logp_drop_nats"]
                    if controls
                    else None
                ),
                single["status"].replace("_", " "),
            ]
        )
    return dict(
        title="Fact-specific slot ablation",
        columns=[
            "Fact",
            "Intervention",
            "Slots masked",
            "Recall drop",
            "Control drop",
            "Excess gold log p drop (nats)",
            "Outcome",
        ],
        rows=table,
        result=dict(cumulative=cumulative, single_slot=single),
    )
