import json

import pytest

from . import lock, run
from .test_comparison import report


def _checkpoint_report(seed, value, frozen=False):
    raw = report(seed, value, frozen)
    return dict(
        model=dict(config=raw["config"], train_settings={"lr": 0.01}, seed=seed),
        provenance={"data_seed": seed},
        step=20,
        tokens_seen=10240,
        data_sha256=raw["data_hash"],
        analysis=raw["analysis"],
        parity={"passed": True},
        training_check={"verdict": "pass"},
        metrics={
            k: {"result": {"cumulative": raw[k]} if k == "E2" else raw.get(k, {})}
            for k in ("Q1", "U4", "E1", "E2", "V2")
        },
    )


def test_locked_report_comparison_checks_data_order(tmp_path):
    paths = []
    for seed, value in [(11, 2.0), (12, 3.0), (13, 4.0)]:
        paths.append(tmp_path / f"{seed}.json")
        paths[-1].write_text(json.dumps(_checkpoint_report(seed, value)))
    margin = tmp_path / "margins.json"
    margin.write_text(json.dumps(lock(paths)))
    twin = _checkpoint_report(11, 2.5, True)
    result = run(twin, margin)
    assert result["result"]["metrics"]["Q1.overall.ppl"]["within_margin"] is True
    assert result["result"]["interpretation"] == "study"
    assert result["result"]["training_checks"]["twin"] == "pass"
    twin["provenance"]["data_seed"] = 12
    with pytest.raises(ValueError, match="data order"):
        run(twin, margin)
