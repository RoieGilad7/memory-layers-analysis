"""X2 calibration from learned PKM seeds, followed by evaluation of a frozen twin.

The margin for each scalar is max(learned seeds) - min(learned seeds).
The absolute distance from the learned mean is compared to that margin. This
is the proposal's descriptive decision rule, not a statistical equivalence
test. The frozen twin cannot participate in estimating the margin.
"""

import math
from numbers import Real
from statistics import fmean, stdev


# Direction predicted for the learned-key arm; cosine can move in either
# direction depending on whether co-read values become aligned or orthogonal.
SCALARS = {
    "Q1.overall.ppl": "lower",
    "U4.excess_bits": "higher",
    "E1.mean_specificity_excess_nll": "higher",
    "E2.mean_matched_core_fraction": "lower",
    "E2.mean_core_size": "lower",
    "E2.mean_core_discovery_mass_share": "lower",
    "V2.text.top1_share": "higher",
    "V2.text.top2_share": "higher",
    "V2.text.cosine_excess": "two_sided",
    "V2.fact.top1_share": "higher",
    "V2.fact.top2_share": "higher",
    "V2.fact.cosine_excess": "two_sided",
}


def _scalar(report, path):
    value = report
    for key in path.split("."):
        if not isinstance(value, dict) or key not in value:
            return None
        value = value[key]
    if isinstance(value, Real) and not isinstance(value, bool) and math.isfinite(value):
        return float(value)
    return None


def _support(report, path):
    if path.startswith("E1."):
        subjects = report.get("E1", {}).get("subjects", {})
        return sorted(
            k for k, v in subjects.items() if v["specificity_excess_nll"] is not None
        )
    if path.startswith("E2."):
        facts = report.get("E2", {}).get("facts", {})
        return sorted(k for k, v in facts.items() if v["status"] == "matched")
    return None


def _signature(report, *, frozen):
    config = report["config"].copy()
    if config.pop("freeze_keys") is not frozen or config["style"] != "pkm":
        expected = "frozen-key" if frozen else "learned-key"
        raise ValueError(f"X2 requires a {expected} PKM report")
    settings = report["settings"].copy()
    seed = settings.pop("seed")
    if type(seed) is not int or type(report["training_gate"]["passed"]) is not bool:
        raise ValueError("Expected an integer training seed and boolean training gate")
    if type(report["fixture"]) is not bool:
        raise ValueError("Expected a boolean fixture indicator")
    return {
        "data_hash": report["data_hash"],
        "step": report["step"],
        "fixture": report["fixture"],
        "config": config,
        "settings": settings,
        "analysis": report["analysis"].copy(),
        "subjects": sorted(report["Q1"]["by_subject"]),
    }


def _require_same(signature, candidate):
    mismatches = [key for key in signature if signature[key] != candidate.get(key)]
    if mismatches:
        raise ValueError(f"Incompatible X2 reports: {', '.join(mismatches)}")


def calibrate(reports: list[dict]) -> dict:
    """Lock one full-range margin per scalar from at least three learned seeds."""
    if len(reports) < 3:
        raise ValueError(
            "X2 calibration requires at least three distinct learned PKM seeds"
        )
    signature = _signature(reports[0], frozen=False)
    for report in reports[1:]:
        _require_same(signature, _signature(report, frozen=False))
    seeds = [r["settings"]["seed"] for r in reports]
    if len(set(seeds)) != len(seeds):
        raise ValueError("X2 learned seeds must be distinct")
    reasons = []
    if signature["fixture"]:
        reasons.append("fixture data")
    missing = [
        s
        for s, r in zip(seeds, reports)
        if not r["training_gate"].get("recorded", True)
    ]
    if missing:
        reasons.append(f"no training check recorded for learned seeds {missing}")
    failed = [
        s
        for s, r in zip(seeds, reports)
        if r["training_gate"].get("recorded", True) and not r["training_gate"]["passed"]
    ]
    if failed:
        reasons.append(f"learned training gate failed for seeds {failed}")

    metrics = {}
    for path, direction in SCALARS.items():
        values = [_scalar(r, path) for r in reports]
        supports = [_support(r, path) for r in reports]
        absent = [s for s, v in zip(seeds, values) if v is None]
        reason = None
        if absent:
            reason = f"missing or undefined learned metric at seeds {absent}"
        elif any(s != supports[0] for s in supports[1:]):
            reason = "matched discovery/evaluation cohort differs across learned seeds"
        metrics[path] = {
            "predicted_direction": direction,
            "learned_values": values,
            "available_seeds": len(values) - len(absent),
            "support": supports[0],
            "learned_mean": None if reason else fmean(values),
            "learned_sample_sd": None if reason else stdev(values),
            "learned_min": None if reason else min(values),
            "learned_max": None if reason else max(values),
            "margin": None if reason else max(values) - min(values),
            "reason": reason,
        }
    return {
        "schema_version": 1,
        "signature": signature,
        "learned_seeds": seeds,
        "seed_count": len(seeds),
        "interpretation": "validation_only" if reasons else "study",
        "limitations": reasons,
        "metrics": metrics,
    }


def compare(manifest: dict, twin_report: dict) -> dict:
    """Use a locked manifest for one twin. Report two-sided empirical margins."""
    if manifest.get("schema_version") != 1:
        raise ValueError("Unrecognized X2 calibration manifest")
    _require_same(manifest["signature"], _signature(twin_report, frozen=True))
    limitations = list(manifest["limitations"])
    if not twin_report["training_gate"].get("recorded", True):
        limitations.append("no training check recorded for the twin")
    elif not twin_report["training_gate"]["passed"]:
        limitations.append("twin training gate failed")
    twin_seed = twin_report["settings"]["seed"]
    if twin_seed not in manifest["learned_seeds"]:
        limitations.append("no learned run shares the twin's initialization seed")
    metrics = {}
    for path, learned in manifest["metrics"].items():
        twin = _scalar(twin_report, path)
        reason = learned["reason"]
        if twin is None:
            reason = reason or "missing or undefined twin metric"
        elif learned["support"] != _support(twin_report, path):
            reason = reason or "matched discovery/evaluation cohort differs in twin"
        gap = None if reason else learned["learned_mean"] - twin
        observed = None
        if gap is not None:
            observed = "equal" if gap == 0 else ("higher" if gap > 0 else "lower")
        metrics[path] = {
            **learned,
            "twin_value": twin,
            "learned_minus_twin": gap,
            "observed_learned_direction": observed,
            "within_margin": None if reason else abs(gap) <= learned["margin"],
            "reason": reason,
        }
    return {
        "interpretation": "validation_only" if limitations else "study",
        "limitations": limitations,
        "learned_seeds": manifest["learned_seeds"],
        "seed_count": manifest["seed_count"],
        "twin_seed": twin_seed,
        "twin_seed_in_calibration": twin_seed in manifest["learned_seeds"],
        "metrics": metrics,
    }
