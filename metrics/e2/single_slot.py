"""One discovery-selected, matched physical-slot intervention on a frozen data-v1 slice."""

from collections import Counter, defaultdict
import random
from statistics import fmean

from ..matching import (
    match_audit,
    matched_masks,
    slot_profiles,
    gold_margin,
    top1_credit,
)


def _outcome(row, scores):
    if len(scores) != len(row["candidates"]):
        raise ValueError(f"Wrong candidate score count for {row['row_id']}")
    answer = row["answer"]
    credit = top1_credit(scores, answer)  # also checks finiteness
    gold = float(scores[answer])
    ties = sum(s == gold for s in scores)
    return {
        "gold_logp": gold,
        "margin": gold_margin(scores, answer),
        "top1_credit": credit,
        "rank": 1 + sum(s > gold for s in scores) + (ties - 1) / 2,
    }


def _discovery(scorer, rows):
    by_fact = {}
    mass = defaultdict(Counter)

    def reads():
        for row in rows:
            key = row["fact_id"]
            info = by_fact.setdefault(
                key,
                dict(
                    fact_id=key,
                    person=row["person"],
                    attribute=row["attribute"],
                    prompts=[],
                ),
            )
            scores, sites = scorer.score(row, collect=True)
            info["prompts"].append(dict(row_id=row["row_id"], **_outcome(row, scores)))
            for site in sites:
                for slot, weight in zip(site["ids"], site["weights"], strict=True):
                    # Count each prompt equally when the gold value uses two scoring tokens.
                    mass[key][int(slot)] += float(weight) / len(sites)
                yield site

    profiles = slot_profiles(reads())
    for info in by_fact.values():
        info["eligible"] = any(p["margin"] > 0 for p in info["prompts"])
    return by_fact, mass, profiles


def _control_masks(slot, pool, profiles, controls, rng):
    """Draw singleton masks without replacement, using the same calipers as E2."""
    remaining = set(pool) - {slot}
    masks = []
    for _ in range(min(len(remaining), controls)):
        draw = matched_masks((slot,), remaining, profiles, 1, rng)
        if not draw:
            break
        masks.append(draw[0])
        remaining.remove(draw[0][0])
    return masks


def _select(keys, masses, profiles, controls, rng):
    first_unmatched = None
    for key in keys:
        weights = masses[key]
        order = sorted(
            (slot for slot in weights if weights[slot] > 0),
            key=lambda slot: (-weights[slot], slot),
        )
        for rank, slot in enumerate(order, 1):
            masks = _control_masks(slot, order, profiles, controls, rng)
            target = dict(
                fact_id=key,
                slot=slot,
                rank_by_gate_mass=rank,
                gate_mass=weights[slot],
                gate_mass_share=weights[slot] / sum(weights[o] for o in order),
                active_discovery_slots=len(order),
            )
            if masks:
                return target, masks
            if first_unmatched is None:
                first_unmatched = target
    return first_unmatched, []


def _mean_outcome(scorer, rows, mask):
    outcomes = [_outcome(row, scorer.score(row, mask=mask)[0]) for row in rows]
    return {name: fmean(r[name] for r in outcomes) for name in outcomes[0]}


def _damage(base, after):
    # Positive always means worse after masking, including for rank.
    return dict(
        gold_logp_drop_nats=base["gold_logp"] - after["gold_logp"],
        margin_drop_nats=base["margin"] - after["margin"],
        top1_credit_drop=base["top1_credit"] - after["top1_credit"],
        rank_worsening=after["rank"] - base["rank"],
    )


def _measure(scorer, rows, target, control_masks):
    if not rows:
        return {"rows": [], "status": "no_prompts"}
    intact = _mean_outcome(scorer, rows, ())
    removed = _mean_outcome(scorer, rows, target)
    damage = _damage(intact, removed)
    controls = []
    for mask in control_masks:
        result = _mean_outcome(scorer, rows, mask)
        controls.append(
            dict(slots=list(mask), outcome=result, damage=_damage(intact, result))
        )
    excess = None
    if controls:
        excess = {
            k: value - fmean(c["damage"][k] for c in controls)
            for k, value in damage.items()
        }
    return dict(
        rows=[r["row_id"] for r in rows],
        intact=intact,
        target_masked=removed,
        target_damage=damage,
        controls=controls,
        target_minus_mean_control_damage=excess,
    )


def run_slot_removal(scorer, corpus, *, seed=17, controls=3):
    """Use a V1Scorer; scorer.model.memory exposes the selected layer's num_slots."""
    if controls < 1:
        raise ValueError("controls must be a positive integer")
    discovery = sorted(
        (
            r
            for r in corpus.facts
            if r["tier"] == "frequent" and r["role"] == "discovery"
        ),
        key=lambda r: r["row_id"],
    )
    discovered = _discovery(scorer, discovery)
    return _single_slot(scorer, corpus, discovered, seed, controls)


def _single_slot(scorer, corpus, discovered, seed, controls):
    by_fact, masses, profiles = discovered
    learned = sorted(k for k, v in by_fact.items() if v["eligible"])
    keys = learned or sorted(by_fact)
    rng = random.Random(seed)
    rng.shuffle(keys)
    target, masks = _select(keys, masses, profiles, controls, rng)
    result = dict(
        seed=seed,
        controls_requested=controls,
        distinct_controls=len(masks),
        eligibility_rule="Frequent-tier fact with the gold answer strictly first on at least one discovery wording.",
        selection_rule=(
            "Seeded fact order. Within a fact, use the highest gate-mass slot with an "
            "available matched donor. Match to other positive-mass slots of that fact "
            "using discovery read counts and mean weighted vector norms across the frequent "
            "slice; both must be within a factor of two. Sample donors without replacement."
        ),
        diagnostic=not learned,
        diagnostic_reason="no discovery-eligible facts" if not learned else None,
        discovery_facts=len(by_fact),
        eligible_facts=len(learned),
        discovery_rows=[by_fact[k] for k in sorted(by_fact)],
        attempted_fact_order=(
            keys[: keys.index(target["fact_id"]) + 1] if target and masks else keys
        ),
        target=target,
        effects={},
    )
    if target is None:
        result["status"] = (
            "no_discovery_reads" if by_fact else "no_frequent_discovery_facts"
        )
        return result
    key, slot = target["fact_id"], target["slot"]
    info = by_fact[key]
    target.update(person=info["person"], attribute=info["attribute"])
    result.update(match_audit([slot], masks, profiles))
    result["status"] = (
        ("diagnostic_matched" if result["diagnostic"] else "matched")
        if masks
        else "no_matched_controls"
    )
    evaluation = sorted(
        (
            r
            for r in corpus.facts
            if r["role"] in ("test", "paraphrase") and r["person"] == info["person"]
        ),
        key=lambda r: r["row_id"],
    )
    groups = {
        "test": [r for r in evaluation if r["fact_id"] == key and r["role"] == "test"],
        "paraphrase": [
            r for r in evaluation if r["fact_id"] == key and r["role"] == "paraphrase"
        ],
        "same_person_other_facts_test": [
            r for r in evaluation if r["fact_id"] != key and r["role"] == "test"
        ],
    }
    result["effects"] = {
        label: _measure(scorer, rows, (slot,), masks) for label, rows in groups.items()
    }
    if not groups["test"]:
        result["status"] = "no_test_prompts"
    else:
        # RoieModel recognizes this range and zeros the selected layer's output.
        num_slots = scorer.model.memory.num_slots
        test = result["effects"]["test"]
        off = _mean_outcome(scorer, groups["test"], range(num_slots))
        test["whole_layer_off"] = dict(
            num_slots=num_slots, outcome=off, damage=_damage(test["intact"], off)
        )
    return result
