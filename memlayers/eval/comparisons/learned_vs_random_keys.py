"""X2 -- does learning the keys matter? The random-key twin against pkm.

For every metric key present in both the untagged `pkm` group and an untagged
twin run: the twin's value, the pkm mean, the gap to the mean, the PAIRED gap
to the pkm run with the twin's seed (same init weights, same data order), and
the margin = the pkm group's range over seeds (max - min), which is the
equivalence margin the methodology uses. A gap is inside the margin when
|gap| <= margin.

`main_test` marks the keys of the methodology's main X2 tests:
heldout_quality, subject_specificity, subject_removal, fact_core_set,
read_concentration (the last four arrive with the analysis plugins).
"""

from __future__ import annotations

from typing import Dict, List

from ..registry import register_comparison

MAIN_TEST_METRICS = (
    "heldout_quality",
    "subject_specificity",
    "subject_removal",
    "fact_core_set",
    "read_concentration",
)

COLUMNS = [
    "twin_run",
    "metric",
    "metric_id",
    "key",
    "twin_value",
    "pkm_n_seeds",
    "pkm_mean",
    "gap_to_mean",
    "paired_run",
    "paired_value",
    "paired_gap",
    "margin",
    "inside_margin_mean",
    "inside_margin_paired",
    "main_test",
]


@register_comparison("learned_vs_random_keys", metric_id="X2")
def learned_vs_random_keys(records, roles: Dict[str, str]):
    """Twin vs pkm: gap to the pkm mean and the paired gap, against the pkm range."""
    import pandas as pd

    pkm = [r for r in records if r.experiment == roles["pkm"] and not r.tag]
    twins = [r for r in records if r.experiment == roles["twin"] and not r.tag]
    rows: List[dict] = []
    for tw in sorted(twins, key=lambda r: r.seed):
        paired = next((p for p in pkm if p.seed == tw.seed), None)
        for full_key, tv in sorted(tw.metrics.items()):
            vals = [p.metrics[full_key] for p in pkm if full_key in p.metrics]
            if not vals:
                continue
            metric, key = full_key.split("/", 1)
            mean = sum(vals) / len(vals)
            margin = max(vals) - min(vals)
            pv = paired.metrics.get(full_key) if paired else None
            pg = (tv - pv) if pv is not None else None
            rows.append(
                {
                    "twin_run": tw.run_id,
                    "metric": metric,
                    "metric_id": tw.metric_ids.get(metric, ""),
                    "key": key,
                    "twin_value": tv,
                    "pkm_n_seeds": len(vals),
                    "pkm_mean": mean,
                    "gap_to_mean": tv - mean,
                    "paired_run": paired.run_id if paired else None,
                    "paired_value": pv,
                    "paired_gap": pg,
                    "margin": margin,
                    "inside_margin_mean": abs(tv - mean) <= margin,
                    "inside_margin_paired": (
                        (abs(pg) <= margin) if pg is not None else None
                    ),
                    "main_test": metric in MAIN_TEST_METRICS,
                }
            )
    return pd.DataFrame(rows, columns=COLUMNS)
