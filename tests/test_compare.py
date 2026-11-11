"""memlayers.compare: tables, groups, X2, the dense rule, refusals, plots."""

import json
import shutil
from pathlib import Path

import pandas as pd
import pytest

from _eval_fixtures import make_mini_bundle, run_overrides
from memlayers.compare import CompareError, RunRecord, compare, dense_rule, load_runs
from memlayers.config import compose
from memlayers.eval.comparisons.learned_vs_random_keys import learned_vs_random_keys
from memlayers.eval.registry import RESERVED, comparisons
from memlayers.run import launch

ROLES = {"pkm": "smoke", "twin": "smoke_randkey", "dense": "smoke_dense"}
SMALL_FILES = (
    "meta.json",
    "status.json",
    "config.yaml",
    "evals.csv",
    "final_metrics.json",
    "training_check.json",
)


@pytest.fixture(scope="module")
def runs_root(tmp_path_factory):
    """3 smoke seeds + the smoke twin + the smoke dense run, on the mini bundle."""
    cfg_path, _ = make_mini_bundle(tmp_path_factory.mktemp("bundle"))
    root = tmp_path_factory.mktemp("runs")
    for seed in (0, 1, 2):
        launch(compose([*run_overrides(cfg_path, root), f"seed={seed}"]))
    launch(compose(run_overrides(cfg_path, root, experiment="smoke_randkey")))
    launch(compose(run_overrides(cfg_path, root, experiment="smoke_dense")))
    return root


def _copy(src: Path, dst: Path, meta=None, status=None, run_id=None):
    """A run dir's small files only (compare never reads checkpoints)."""
    dst.mkdir(parents=True)
    for n in SMALL_FILES:
        if (src / n).exists():
            shutil.copy(src / n, dst / n)
    m = json.loads((dst / "meta.json").read_text())
    m.update(meta or {})
    if run_id:
        m["run_id"] = run_id
    (dst / "meta.json").write_text(json.dumps(m))
    if status:
        st = json.loads((dst / "status.json").read_text())
        st["state"] = status
        (dst / "status.json").write_text(json.dumps(st))
    return dst


def _view(root: Path, tmp: Path, names=None) -> Path:
    """A fresh dir with copies of the chosen runs, to edit safely."""
    v = tmp / "view"
    for d in sorted(root.iterdir()):
        if (
            d.is_dir()
            and not d.name.startswith(".")
            and (names is None or d.name in names)
        ):
            _copy(d, v / d.name)
    return v


def test_the_five_smoke_runs_compare(runs_root, tmp_path):
    out = tmp_path / "cmp"
    meta = compare([runs_root], out, roles=ROLES)
    runs = pd.read_csv(out / "runs.csv")
    assert len(runs) == 5
    assert set(runs.run_id) == {
        "smoke-s0",
        "smoke-s1",
        "smoke-s2",
        "smoke_randkey-s0",
        "smoke_dense-s0",
    }
    for c in (
        "run_id",
        "experiment",
        "seed",
        "tag",
        "status",
        "device",
        "precision",
        "git_commit",
        "data_sha256",
        "heldout_sample_sha256",
        "fact_sample_sha256",
        "tokens_seen",
    ):
        assert c in runs.columns, c
    assert "heldout_quality/loss/pile_avg" in runs.columns
    assert "fact_recall/top1/frequent/test" in runs.columns
    for f in (
        "groups.csv",
        "curves.csv",
        "training_check.csv",
        "learned_vs_random_keys.csv",
        "compare_meta.json",
    ):
        assert (out / f).exists(), f
    for p in (
        "plot_heldout_loss.png",
        "plot_fact_recall.png",
        "plot_slot_coverage.png",
    ):
        assert (out / p).stat().st_size > 5000, p  # written, non-empty
    assert len(meta["runs"]) == 5 and meta["roles"] == ROLES
    curves = pd.read_csv(out / "curves.csv")
    assert set(curves.stage) == {"during", "final"}
    assert {"run_id", "experiment", "seed"} <= set(curves.columns)


def test_groups_equal_a_direct_pandas_computation(runs_root, tmp_path):
    out = tmp_path / "cmp"
    compare([runs_root], out, roles=ROLES)
    runs = pd.read_csv(out / "runs.csv")
    groups = pd.read_csv(out / "groups.csv", keep_default_na=False)
    metric_cols = [c for c in runs.columns if c.count("/") >= 2]
    for exp, sub in runs.groupby("experiment"):
        for col in metric_cols:
            vals = sub[col].dropna()
            if vals.empty:
                continue
            metric, key = col.split("/", 1)
            g = groups[
                (groups.experiment == exp)
                & (groups.metric == metric)
                & (groups.key == key)
            ]
            assert len(g) == 1, (exp, col)
            g = g.iloc[0]
            assert g.n_seeds == len(vals)
            assert g["mean"] == pytest.approx(vals.mean(), rel=1e-12)
            assert g["min"] == pytest.approx(vals.min()) and g["max"] == pytest.approx(
                vals.max()
            )
            assert g["range"] == pytest.approx(vals.max() - vals.min())
            if len(vals) > 1:
                assert float(g["std"]) == pytest.approx(vals.std(), rel=1e-9)
    smoke = groups[
        (groups.experiment == "smoke") & (groups.key == "loss/pile_avg")
    ].iloc[0]
    assert smoke.n_seeds == 3 and smoke.metric_id == "Q1"


def _rec(exp, seed, metrics, tag=""):
    return RunRecord(
        run_dir=Path(f"/x/{exp}-s{seed}"),
        run_id=f"{exp}-s{seed}",
        experiment=exp,
        seed=seed,
        tag=tag,
        status="done",
        meta={},
        config={},
        metrics=metrics,
        metric_ids={"heldout_quality": "Q1", "fact_recall": "Q2"},
    )


def test_x2_gaps_and_margins_on_hand_made_numbers():
    K, F = "heldout_quality/loss/pile_avg", "fact_recall/top1/frequent/test"
    recs = [
        _rec("pkm", 0, {K: 4.0, F: 0.30}),
        _rec("pkm", 1, {K: 4.2, F: 0.40}),
        _rec("pkm", 2, {K: 4.1, F: 0.35}),
        _rec("pkm_randkey", 0, {K: 4.25, F: 0.10}),
        _rec("pkm", 3, {K: 9.9}, tag="pilot"),  # never mixes in
    ]
    df = learned_vs_random_keys(
        recs, {"pkm": "pkm", "twin": "pkm_randkey", "dense": "dense"}
    )
    q = df[df.key == "loss/pile_avg"].iloc[0]
    assert q.pkm_n_seeds == 3 and q.pkm_mean == pytest.approx(4.1)
    assert q.gap_to_mean == pytest.approx(0.15) and q.margin == pytest.approx(0.2)
    assert q.paired_run == "pkm-s0" and q.paired_gap == pytest.approx(0.25)
    assert bool(q.inside_margin_mean) and not bool(q.inside_margin_paired)
    assert bool(q.main_test) and q.metric_id == "Q1"
    f = df[df.key == "top1/frequent/test"].iloc[0]
    assert f.gap_to_mean == pytest.approx(-0.25) and f.margin == pytest.approx(0.1)
    assert not bool(f.inside_margin_mean) and not bool(f.main_test)
    assert len(df) == 2


def test_x2_is_a_registered_comparison():
    assert comparisons()["learned_vs_random_keys"].metric_id == "X2"
    assert "learned_vs_random_keys" not in RESERVED


def test_the_dense_rule_on_hand_made_perplexities():
    P = "heldout_quality/ppl/pile_avg"
    pkm = _rec("pkm", 0, {P: 50.0})
    assert dense_rule(pkm, [_rec("dense", 0, {P: 60.0})])["pass"] is True
    d = dense_rule(pkm, [_rec("dense", 0, {P: 45.0})])
    assert d["pass"] is False and d["pkm_ppl"] == 50.0 and d["dense_ppl"] == 45.0
    assert dense_rule(pkm, [])["detail"] == "no dense run"


def test_training_check_csv_has_the_dense_rule_for_untagged_pkm_only(
    runs_root, tmp_path
):
    out = tmp_path / "cmp"
    compare([runs_root], out, roles=ROLES)
    tc = pd.read_csv(out / "training_check.csv", keep_default_na=False)
    dense_rows = tc[tc.rule == "ppl_at_most_dense"]
    assert set(dense_rows.run_id) == {
        "smoke-s0",
        "smoke-s1",
        "smoke-s2",
    }  # not the twin
    assert {"finite", "learned", "coverage", "fact_learning"} <= set(tc.rule)


# ----------------------------------------------------------------- refusals
def test_mixed_data_is_refused_naming_the_runs(runs_root, tmp_path):
    v = _view(runs_root, tmp_path)
    m = json.loads((v / "smoke-s1/meta.json").read_text())
    m["data"]["data_sha256"] = "f" * 64
    (v / "smoke-s1/meta.json").write_text(json.dumps(m))
    with pytest.raises(
        CompareError, match=r"(?s)different data.*ffffffffffffffff: smoke-s1"
    ):
        load_runs([v])


def test_mixed_eval_sets_are_refused(runs_root, tmp_path):
    v = _view(runs_root, tmp_path)
    m = json.loads((v / "smoke-s2/meta.json").read_text())
    m["eval_sets"]["fact_sample"] = "0" * 64
    (v / "smoke-s2/meta.json").write_text(json.dumps(m))
    with pytest.raises(CompareError, match="fact_sample"):
        load_runs([v])


def test_mixed_devices_warn(runs_root, tmp_path):
    v = _view(runs_root, tmp_path)
    m = json.loads((v / "smoke-s1/meta.json").read_text())
    m["device"] = "mps"
    (v / "smoke-s1/meta.json").write_text(json.dumps(m))
    _, _, warnings = load_runs([v])
    assert any("smoke mixes devices" in w and "smoke-s1=mps" in w for w in warnings)


def test_unfinished_runs_are_skipped_unless_asked(runs_root, tmp_path):
    v = _view(runs_root, tmp_path)
    st = json.loads((v / "smoke-s2/status.json").read_text())
    st["state"] = "running"
    (v / "smoke-s2/status.json").write_text(json.dumps(st))
    recs, skipped, _ = load_runs([v])
    assert "smoke-s2" not in {r.run_id for r in recs}
    assert any("smoke-s2" in d and "running" in why for d, why in skipped)
    recs, _, _ = load_runs([v], include_unfinished=True)
    assert "smoke-s2" in {r.run_id for r in recs}


def test_old_dirs_and_non_run_dirs_are_skipped(runs_root, tmp_path):
    v = _view(runs_root, tmp_path)
    _copy(v / "smoke-s0", v / "smoke-s0.old-1")
    (v / "notes").mkdir()
    recs, skipped, _ = load_runs([v])
    assert len(recs) == 5
    reasons = dict(skipped)
    assert "force=true" in reasons[str(v / "smoke-s0.old-1")]
    assert "not a run dir" in reasons[str(v / "notes")]


def test_a_tagged_pilot_is_its_own_group(runs_root, tmp_path):
    v = _view(runs_root, tmp_path)
    base = tmp_path / "base"
    compare([v], base, roles=ROLES)
    _copy(
        v / "smoke-s1",
        v / "smoke-s1-pilot",
        meta={"tag": "pilot"},
        run_id="smoke-s1-pilot",
    )
    m = json.loads((v / "smoke-s1-pilot/final_metrics.json").read_text())
    m["metrics"] = {k: x + 1.0 for k, x in m["metrics"].items()}
    (v / "smoke-s1-pilot/final_metrics.json").write_text(json.dumps(m))
    out = tmp_path / "with_pilot"
    compare([v], out, roles=ROLES)
    g0 = pd.read_csv(base / "groups.csv", keep_default_na=False)
    g1 = pd.read_csv(out / "groups.csv", keep_default_na=False)
    main0 = g0[(g0.experiment == "smoke") & (g0.tag == "")].reset_index(drop=True)
    main1 = g1[(g1.experiment == "smoke") & (g1.tag == "")].reset_index(drop=True)
    pd.testing.assert_frame_equal(main0, main1)  # n_seeds, mean, range unchanged
    pilot = g1[g1.tag == "pilot"]
    assert len(pilot) and set(pilot.n_seeds) == {1}
    x2a = pd.read_csv(base / "learned_vs_random_keys.csv")
    x2b = pd.read_csv(out / "learned_vs_random_keys.csv")
    pd.testing.assert_frame_equal(x2a, x2b)


def test_two_runs_with_the_same_identity_are_an_error(runs_root, tmp_path):
    v = _view(runs_root, tmp_path)
    _copy(v / "smoke-s0", v / "smoke-s0-copy")
    with pytest.raises(CompareError, match=r"\('smoke', 0, ''\)"):
        load_runs([v])


def test_the_cli_refuses_with_exit_code_2(runs_root, tmp_path):
    from memlayers.compare import main

    v = _view(runs_root, tmp_path)
    _copy(v / "smoke-s0", v / "smoke-s0-copy")
    assert main([str(v), "--out", str(tmp_path / "o")]) == 2
