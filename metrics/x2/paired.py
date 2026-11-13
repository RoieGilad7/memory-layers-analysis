"""X2 paired test: a learned-key PKM against its frozen-key twin, item by item.

The twin shares the learned run's initialization and batches, so the cleanest
H3 contrast is per item: the same fact prompt, the same fact's core, the same
subject. Differences are learned minus twin, with cluster-bootstrap CIs
(people for prompts, facts for cores, subjects for E1). Only items both models
support enter a comparison, and the counts of items each model alone supports
are reported, because a model that knows fewer facts has fewer to lose.
"""

from __future__ import annotations

from collections import defaultdict

from ..stats import cluster_bootstrap

KNOWN = {
    "matched",
    "no_matched_controls",
    "prefix_limit_reached",
    "threshold_not_reached",
}
CORED = ("matched", "no_matched_controls")


def _check(learned, twin):
    limitations = []
    a, b = learned["model"]["config"], twin["model"]["config"]
    if a.get("style") != "pkm" or b.get("style") != "pkm":
        raise ValueError("X2 paired test needs two PKM reports")
    if a.get("freeze_keys") or not b.get("freeze_keys"):
        raise ValueError(
            "Give the learned-key report first and the frozen-key twin second"
        )
    strip = lambda c: {k: v for k, v in c.items() if k != "freeze_keys"}
    if strip(a) != strip(b):
        raise ValueError("Learned and twin models differ beyond freeze_keys")
    for key in ("step", "data_sha256", "analysis"):
        if learned[key] != twin[key]:
            raise ValueError(f"Learned and twin reports differ in {key}")
    if learned["model"]["seed"] != twin["model"]["seed"]:
        limitations.append("learned run and twin have different seeds")
    for name, report in (("learned", learned), ("twin", twin)):
        gate = report.get("training_check") or {}
        if gate.get("passed") is not True:
            limitations.append(f"{name} training check not passed or not recorded")
    return limitations


def _diff(pairs, clusters, seed):
    ci = cluster_bootstrap([a - b for a, b in pairs], clusters, seed=seed)
    return dict(
        learned_mean=sum(a for a, _ in pairs) / len(pairs) if pairs else None,
        twin_mean=sum(b for _, b in pairs) / len(pairs) if pairs else None,
        learned_minus_twin=ci["mean"],
        ci=[ci["lo"], ci["hi"]],
        items=ci["n"],
        clusters=ci["clusters"],
    )


def _q2(learned, twin, seed):
    rows = lambda r: {x["row_id"]: x for x in r["metrics"]["Q2"]["result"]["rows"]}
    a, b = rows(learned), rows(twin)
    groups = defaultdict(list)
    for row_id in sorted(set(a) & set(b)):
        x, y = a[row_id], b[row_id]
        if x["role"] == "discovery":
            continue
        groups[f"{x['tier']}/{x['role']}"].append((x, y))
    out = {}
    for group, items in sorted(groups.items()):
        people = [x["person"] for x, _ in items]
        out[group] = dict(
            top1=_diff([(x["top1"], y["top1"]) for x, y in items], people, seed),
            margin=_diff([(x["margin"], y["margin"]) for x, y in items], people, seed),
        )
    return out


def _e2(learned, twin, seed):
    facts = lambda r: r["metrics"]["E2"]["result"]["cumulative"]["facts"]
    a, b = facts(learned), facts(twin)
    common = sorted(set(a) & set(b))
    known_a = {k for k in common if a[k]["status"] in KNOWN}
    known_b = {k for k in common if b[k]["status"] in KNOWN}
    cored = [k for k in common if a[k]["status"] in CORED and b[k]["status"] in CORED]
    out = dict(
        facts_compared=len(common),
        known_by_both=len(known_a & known_b),
        known_by_learned_only=len(known_a - known_b),
        known_by_twin_only=len(known_b - known_a),
        cored_by_both=len(cored),
    )
    if cored:
        out.update(
            core_size=_diff(
                [(a[k]["core_size"], b[k]["core_size"]) for k in cored], cored, seed
            ),
            core_discovery_mass_share=_diff(
                [
                    (
                        a[k]["core_discovery_mass_share"],
                        b[k]["core_discovery_mass_share"],
                    )
                    for k in cored
                ],
                cored,
                seed,
            ),
            test_erased=_diff(
                [
                    (float(a[k]["test_erased"]), float(b[k]["test_erased"]))
                    for k in cored
                ],
                cored,
                seed,
            ),
        )
    return out


def _e1(learned, twin, seed):
    subjects = lambda r: r["metrics"]["E1"]["result"]["subjects"]
    a, b = subjects(learned), subjects(twin)
    out = {}
    fractions = sorted(
        {d["excess_fraction"] for s in a.values() for d in s.get("doses", [])}
    )
    for fraction in fractions:
        pairs, names, shares = [], [], []
        for s in sorted(set(a) & set(b)):
            da = next(
                (d for d in a[s].get("doses", []) if d["excess_fraction"] == fraction),
                None,
            )
            db = next(
                (d for d in b[s].get("doses", []) if d["excess_fraction"] == fraction),
                None,
            )
            if not da or not db:
                continue
            if (
                da["specificity_excess_nll"] is None
                or db["specificity_excess_nll"] is None
            ):
                continue
            pairs.append((da["specificity_excess_nll"], db["specificity_excess_nll"]))
            names.append(s)
            if (
                da.get("target_eval_gate_share_removed") is not None
                and db.get("target_eval_gate_share_removed") is not None
            ):
                shares.append(
                    (
                        da["target_eval_gate_share_removed"],
                        db["target_eval_gate_share_removed"],
                    )
                )
        if pairs:
            out[str(fraction)] = dict(
                specificity_excess_nll=_diff(pairs, names, seed),
                eval_gate_share_removed=(
                    _diff(shares, list(range(len(shares))), seed) if shares else None
                ),
            )
    return out


def _scalar(report, *path):
    value = report["metrics"]
    for key in path:
        if not isinstance(value, dict) or value.get(key) is None:
            return None
        value = value[key]
    return value


SCALARS = {
    "Q1 overall NLL": ("Q1", "result", "overall", "nll"),
    "U4 excess bits": ("U4", "result", "excess_bits"),
    "V2 text top-1 share": ("V2", "result", "text", "top1_share"),
    "V2 text top-2 share": ("V2", "result", "text", "top2_share"),
    "V2 text cosine excess": ("V2", "result", "text", "cosine_excess"),
    "V2 fact top-1 share": ("V2", "result", "fact", "top1_share"),
    "V2 fact cosine excess": ("V2", "result", "fact", "cosine_excess"),
}


def paired(learned, twin, *, seed=0):
    limitations = _check(learned, twin)
    scalars = {}
    for name, path in SCALARS.items():
        x, y = _scalar(learned, *path), _scalar(twin, *path)
        scalars[name] = dict(
            learned=x,
            twin=y,
            learned_minus_twin=None if x is None or y is None else x - y,
        )
    return dict(
        interpretation="validation_only" if limitations else "study",
        limitations=limitations,
        step=learned["step"],
        learned_seed=learned["model"]["seed"],
        twin_seed=twin["model"]["seed"],
        q2=_q2(learned, twin, seed),
        e1=_e1(learned, twin, seed),
        e2=_e2(learned, twin, seed),
        scalars=scalars,
    )


def summary_rows(result):
    """Flat (measure, learned, twin, difference, CI, items) rows for printing."""
    rows = []

    def add(name, d):
        if d:
            rows.append(
                [
                    name,
                    d["learned_mean"],
                    d["twin_mean"],
                    d["learned_minus_twin"],
                    d["ci"],
                    d["items"],
                ]
            )

    for group, d in result["q2"].items():
        add(f"Q2 top-1 {group}", d["top1"])
    for fraction, d in result["e1"].items():
        add(f"E1 excess NLL at {fraction}", d["specificity_excess_nll"])
        add(f"E1 eval gate share at {fraction}", d["eval_gate_share_removed"])
    for key in ("core_size", "core_discovery_mass_share", "test_erased"):
        add(f"E2 {key.replace('_', ' ')}", result["e2"].get(key))
    for name, d in result["scalars"].items():
        rows.append(
            [name, d["learned"], d["twin"], d["learned_minus_twin"], None, None]
        )
    return rows
