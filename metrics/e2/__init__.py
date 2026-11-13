"""E2. Discovery-ranked cumulative slot lesions and a matched one-slot experiment."""

from collections import Counter, defaultdict
import random
from statistics import fmean

from ..matching import matched_masks, match_audit
from ..stats import cluster_bootstrap
from .single_slot import _damage, _discovery, _mean_outcome, _single_slot


def _mass_share(weights, slots):
    total = sum(w for w in weights.values() if w > 0)
    return sum(weights.get(s, 0.0) for s in slots) / total if total else None


def _cumulative(ctx, discovered):
    """Grow a discovery-ranked prefix until discovery prompts fall to chance.

    The prefix size n is chosen on discovery prompts only; test prompts then
    measure whether erasing that core generalizes to wordings that took no part
    in selection. Two controls: (1) matched masks drawn from the same fact's
    other read slots test concentration within the fact's read set, and
    (2) matched masks drawn from slots the fact never read on discovery give a
    baseline for collateral damage to other people. Every lesion records the
    share of the fact's discovery gate mass it removed, so damage can be read
    per unit of removed mass.
    """
    facts, mass, profiles = discovered
    test = [row for row in ctx.corpus.facts if row["role"] == "test"]
    discovery = [row for row in ctx.corpus.facts if row["role"] == "discovery"]
    by_key, disc_by_key = defaultdict(list), defaultdict(list)
    for row in test:
        by_key[row["fact_id"]].append(row)
    for row in discovery:
        disc_by_key[row["fact_id"]].append(row)
    rng = random.Random(ctx.seed)
    cap = getattr(ctx, "max_prefix", 16)
    if cap is not None and cap < 1:
        raise ValueError("Maximum tested prefix must be positive")
    collateral_cap = getattr(ctx, "collateral_rows", 200)
    records = {}
    for key, fact in sorted(facts.items()):
        rows = by_key[key]
        disc_rows = disc_by_key[key]
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
        disc_base = _mean_outcome(ctx.scorer, disc_rows, ())
        chance = fmean(1 / len(row["candidates"]) for row in rows)
        disc_chance = fmean(1 / len(row["candidates"]) for row in disc_rows)
        order = sorted(
            (s for s, weight in mass[key].items() if weight > 0),
            key=lambda s: (-mass[key][s], s),
        )
        record.update(
            baseline=base,
            discovery_baseline=disc_base,
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
            disc_after = _mean_outcome(ctx.scorer, disc_rows, mask)
            after = _mean_outcome(ctx.scorer, rows, mask)
            record["curve"].append(
                {
                    "n": n,
                    **after,
                    "discovery": disc_after,
                    "discovery_mass_share": _mass_share(mass[key], mask),
                }
            )
            if disc_after["top1_credit"] <= disc_chance:
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
        generic_pool = set(profiles) - set(order)
        generic = matched_masks(mask, generic_pool, profiles, 1, rng)
        record.update(
            status="matched" if null else "no_matched_controls",
            core_slots=list(mask),
            core_size=n,
            core_fraction=n / len(order),
            core_discovery_mass_share=_mass_share(mass[key], mask),
            control_discovery_mass_shares=[_mass_share(mass[key], c) for c in controls],
            test_masked=after,
            test_erased=after["top1_credit"] <= chance,
            target_damage=_damage(base, after),
            distinct_controls=len(set(controls)),
            controls=null,
            control_damage=[_damage(base, o) for o in null],
            matched_erasure_rate=(
                fmean(o["top1_credit"] <= chance for o in null) if null else None
            ),
            excess_gold_logp_drop_nats=(
                fmean(o["gold_logp"] for o in null) - after["gold_logp"]
                if null
                else None
            ),
            generic_control_slots=list(generic[0]) if generic else None,
            **match_audit(mask, controls, profiles),
        )
        others = [r for r in test if r["person"] != fact["person"]]
        if collateral_cap is not None and len(others) > collateral_cap:
            others = sorted(
                random.Random(f"{ctx.seed}:{key}").sample(others, collateral_cap),
                key=lambda r: r["row_id"],
            )
        collateral = record["collateral"] = {}
        for cohort, group in {
            "target": rows,
            "same_person_other_facts": [
                r for r in test if r["person"] == fact["person"] and r["fact_id"] != key
            ],
            "other_people": others,
        }.items():
            collateral[cohort] = {
                "prompts": len(group),
                "intact": _mean_outcome(ctx.scorer, group, ()) if group else None,
                "masked": _mean_outcome(ctx.scorer, group, mask) if group else None,
                "masked_generic_control": (
                    _mean_outcome(ctx.scorer, group, generic[0])
                    if group and generic
                    else None
                ),
            }
    matched = [r for r in records.values() if r["status"] == "matched"]
    cored = [r for r in records.values() if "core_size" in r]

    def summary(values):
        ci = cluster_bootstrap(values, list(range(len(values))), seed=ctx.seed)
        return [ci["lo"], ci["hi"]]

    return {
        "facts": records,
        "tested_prefix_limit": cap,
        "selection": "core size chosen on discovery prompts; outcomes on test prompts",
        "matched_facts": len(matched),
        "cored_facts": len(cored),
        "status_counts": dict(Counter(r["status"] for r in records.values())),
        "mean_matched_core_fraction": (
            fmean(r["core_fraction"] for r in matched) if matched else None
        ),
        "mean_core_size": fmean(r["core_size"] for r in cored) if cored else None,
        "mean_core_size_ci": summary([r["core_size"] for r in cored]),
        "mean_core_discovery_mass_share": (
            fmean(r["core_discovery_mass_share"] for r in cored) if cored else None
        ),
        "test_erasure_rate": (
            fmean(r["test_erased"] for r in cored) if cored else None
        ),
        "test_erasure_rate_ci": summary([r["test_erased"] for r in cored]),
        "mean_matched_erasure_rate": (
            fmean(r["matched_erasure_rate"] for r in matched) if matched else None
        ),
        "mean_excess_gold_logp_drop_nats": (
            fmean(r["excess_gold_logp_drop_nats"] for r in matched) if matched else None
        ),
        "mean_excess_gold_logp_drop_ci": summary(
            [r["excess_gold_logp_drop_nats"] for r in matched]
        ),
    }


def discovery_rows(ctx):
    """Frequent-tier discovery prompts, or a fixed fact cohort when given."""
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
        drop = base["top1_credit"] - end[-1]["top1_credit"] if base and end else None
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
                r.get("core_discovery_mass_share"),
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
                target.get("gate_mass_share"),
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
            "Gate mass removed",
            "Recall drop",
            "Control drop",
            "Excess gold log p drop (nats)",
            "Outcome",
        ],
        rows=table,
        result=dict(cumulative=cumulative, single_slot=single),
    )
