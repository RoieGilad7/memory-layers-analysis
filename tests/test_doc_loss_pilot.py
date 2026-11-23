"""bench/doc_loss_pilot.py: the fixed lambda rule, the fixed-batch gap measurement,
and a CPU dry run end to end."""

import json
import sys
from pathlib import Path

import pytest
import torch

from conftest import make_model

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from bench.doc_loss_pilot import (  # noqa: E402
    choose_lambda,
    criteria,
    fixed_batch_gap,
    main,
)

BASE = {"heldout_pile_avg": 4.00, "gap": 0.10, "coverage": 0.95}


def _row(loss=4.02, gap=0.20, cov=0.95):
    return {"heldout_pile_avg": loss, "gap": gap, "coverage": cov}


# ---- the rule -------------------------------------------------------------------
def test_picks_the_largest_passing_lambda():
    rows = {0.0: BASE, 0.003: _row(), 0.01: _row(), 0.03: _row(loss=4.05)}
    # 0.03 fails (a) only: 4.05 > 4.04
    assert choose_lambda(rows) == 0.01
    rows[0.03] = _row(loss=4.04)  # exactly 1% above: passes
    assert choose_lambda(rows) == 0.03


def test_none_when_nothing_passes():
    rows = {0.0: BASE, 0.003: _row(gap=0.12), 0.01: _row(cov=0.5)}
    assert choose_lambda(rows) is None


@pytest.mark.parametrize(
    "bad, key",
    [
        (_row(loss=4.0401), "a_heldout"),
        (_row(gap=0.1499), "b_gap"),
        (_row(cov=0.7999), "c_coverage"),
    ],
)
def test_failing_a_single_criterion_rejects(bad, key):
    c = criteria(bad, BASE)
    assert [k for k, v in c.items() if not v] == [key]
    assert choose_lambda({0.0: BASE, 0.01: bad}) is None
    assert choose_lambda({0.0: BASE, 0.01: bad, 0.003: _row()}) == 0.003


def test_the_rule_needs_the_baseline():
    with pytest.raises(ValueError):
        choose_lambda({0.01: _row()})


# ---- gap measurement ------------------------------------------------------------
def _batches(n=3, B=4, T=64, eot=256):
    g = torch.Generator().manual_seed(5)
    out = []
    for _ in range(n):
        x = torch.randint(0, 256, (B, T), generator=g)
        x[:, 20] = eot
        x[:, 45] = eot
        out.append(x)
    return out


@pytest.mark.parametrize("training", [True, False])
@pytest.mark.parametrize("keeping", [True, False])
def test_gap_is_repeatable_and_leaves_the_model_alone(training, keeping):
    m = make_model("pkm", layer=1)
    m(torch.randint(0, 256, (4, 32)))  # move the BatchNorm stats off their init
    m.train(training)
    mem = m.memory_layers[1]
    mem.set_keep_queries(keeping)
    bn = mem.pkm.norm.bn
    stats = [
        t.clone() for t in (bn.running_mean, bn.running_var, bn.num_batches_tracked)
    ]
    params = [p.detach().clone() for p in m.parameters()]
    b = _batches()
    a = fixed_batch_gap(m, b, 1, 256, 8, 0.5)
    c = fixed_batch_gap(m, b, 1, 256, 8, 0.5)
    assert a == c
    assert a["batches_used"] == 3 and a["gap"] == a["gap"]  # not NaN
    assert m.training == training
    assert mem.keep_queries == keeping
    assert len(mem.pkm.norm._forward_hooks) == int(keeping)
    assert mem.kept_queries() is None
    for s, t in zip(stats, (bn.running_mean, bn.running_var, bn.num_batches_tracked)):
        assert torch.equal(s, t)
    for p, q in zip(params, m.parameters()):
        assert torch.equal(p, q)


# ---- dry run ----------------------------------------------------------------------
def test_dry_run_end_to_end(tmp_path):
    out = tmp_path / "pilot"
    js = tmp_path / "summary.json"
    assert (
        main(
            [
                "--dry-run",
                "--out-root",
                str(out),
                "--json",
                str(js),
                "--lambdas",
                "0,0.03",
            ]
        )
        == 0
    )
    s = json.loads(js.read_text())
    assert s["steps"] == 20 and [r["lambda"] for r in s["rows"]] == [0.0, 0.03]
    for name in ("l0", "l0.03"):
        d = json.loads((out / name / "done.json").read_text())
        assert d["step"] == 20
        assert d["config"]["doc_loss_weight"] == float(name[1:])
        assert d["heldout_pile_avg"] > 0 and 0 <= d["coverage"] <= 1
        assert d["gap"] == d["gap"]
    assert s["runs"]["l0.03"]["doc_gap_log"] == {}  # no logged step in 200/500/...
    # a restart skips finished runs
    before = (out / "l0" / "done.json").read_text()
    assert (
        main(
            [
                "--dry-run",
                "--out-root",
                str(out),
                "--json",
                str(js),
                "--lambdas",
                "0,0.03",
            ]
        )
        == 0
    )
    assert (out / "l0" / "done.json").read_text() == before
