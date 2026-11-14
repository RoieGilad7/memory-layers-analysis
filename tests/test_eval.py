"""memlayers.eval: registry, metrics, context, schedule, sets, writers, check."""

import csv
import json
import math
import os
import subprocess
import sys
from collections import Counter
from pathlib import Path

import numpy as np
import pytest
import torch

from _eval_fixtures import READLOG_BUDGET, make_mini_bundle, run_overrides
from conftest import make_model
from data.fetch import load_manifest
from data.manifest import sha256_file
from memlayers.config import compose, to_train_config
from memlayers.eval import RESERVED, get_metric, register_metric, registered
from memlayers.eval.context import (
    EvalContext,
    EvalResources,
    HeldoutDoc,
    accumulate_reads,
    new_usage,
)
from memlayers.eval.eval_sets import build as build_sets
from memlayers.eval.evaluator import run_metrics
from metrics.q2.training import keys_from_summary, score_rows, summarize
from memlayers.eval.metrics.slot_usage import usage_keys
from memlayers.eval.registry import UnknownMetric, validate_metric_names
from memlayers.eval.schedule import eval_schedule
from memlayers.eval.training_check import training_check
from memlayers.evaluate import evaluate_run
from memlayers.memory import MemoryRead
from memlayers.run import RunRefused, launch, read_status

ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="module")
def bundle(tmp_path_factory):
    return make_mini_bundle(tmp_path_factory.mktemp("bundle"))


@pytest.fixture(scope="module")
def done_run(bundle, tmp_path_factory):
    """One evaluated CPU run on the mini bundle, shared by the read-only tests."""
    out = tmp_path_factory.mktemp("runs")
    return launch(compose(run_overrides(bundle[0], out)))


def _evals(run_dir):
    with open(run_dir / "evals.csv", newline="") as fh:
        return list(csv.DictReader(fh))


def _losses(run_dir):
    with open(run_dir / "train_log.csv", newline="") as fh:
        return [(r["step"], r["loss"]) for r in csv.DictReader(fh)]


# ------------------------------------------------------------------ registry
def test_the_built_ins_are_registered_with_their_ids():
    reg = registered()
    assert {n: s.metric_id for n, s in reg.items()}.items() >= {
        "heldout_quality": "Q1",
        "fact_recall": "Q2",
        "slot_usage": "U1",
    }.items()
    assert reg["slot_usage"].needs_memory and not reg["fact_recall"].needs_memory
    assert reg["fact_recall"].inputs == ("model", "fact_probe")
    assert set(reg["heldout_quality"].stages) == {"during", "final", "posthoc"}
    assert len({s.metric_id for s in reg.values()}) == len(reg)


def test_a_duplicate_name_or_id_is_refused():
    with pytest.raises(ValueError, match="already registered"):
        register_metric("fact_recall", metric_id="Q9")(lambda ctx: {})
    with pytest.raises(ValueError, match="already belongs"):
        register_metric("another_one", metric_id="Q1")(lambda ctx: {})


def test_the_reserved_names_are_listed_but_not_runnable():
    want = {
        "subject_specificity": "U4",
        "subject_removal": "E1",
        "fact_core_set": "E2",
        "read_concentration": "V2",
        "slot_inspection": "C4",
        "effective_rank": "C6",
        "learned_vs_random_keys": "X2",
        "knn_lm_comparison": "X3",
    }
    from memlayers.eval import comparisons as _builtin  # noqa: F401  (X2)
    from memlayers.eval.registry import comparisons

    # X2 has since been implemented as a comparison; the rest stay reserved
    taken = {n: s.metric_id for n, s in comparisons().items()}
    assert {**{k: v[0] for k, v in RESERVED.items() if k in want}, **taken} == want
    assert "training_check" in RESERVED
    for name in want:
        with pytest.raises(UnknownMetric, match="reserved|comparison"):
            validate_metric_names([name])
    with pytest.raises(ValueError, match="reserved with metric_id"):
        register_metric("effective_rank", metric_id="Z1")(lambda ctx: {})
    assert "effective_rank" in RESERVED and "effective_rank" not in registered()


def test_an_unknown_name_fails_at_startup_with_the_known_list(tmp_path, bundle):
    with pytest.raises(UnknownMetric, match="heldout_quality, slot_usage"):
        validate_metric_names(["fact_recal"])
    cfg = compose([*run_overrides(bundle[0], tmp_path), "eval.during=[fact_recal]"])
    with pytest.raises(UnknownMetric, match="Runnable metrics: fact_recall"):
        launch(cfg)
    assert not (tmp_path / "smoke-s0").exists()  # nothing was written


# ------------------------------------------------------------ heldout_quality
class _HandResources(EvalResources):
    """Three hand-made documents; pile_cc and github are training subjects,
    uspto_backgrounds is not."""

    def __init__(self, tokens, docs):
        super().__init__(None, "real")
        self._toks, self._docs = tokens, docs

    def why_missing(self, what):
        return None

    def tokens(self, half):
        return self._toks

    def heldout(self, half="test", sample=True):
        return self._docs

    def train_slugs(self):
        return ["pile_cc", "github"]


def _hand_ctx(model, sample=True):
    rng = np.random.default_rng(3)
    toks = rng.integers(0, 257, size=400).astype(np.uint16)
    docs = {
        "pile_cc": [HeldoutDoc("a", 0, 40)],
        "github": [HeldoutDoc("b", 40, 150)],  # longer than block 64: 3 windows
        "uspto_backgrounds": [HeldoutDoc("c", 190, 70)],
    }
    res = _HandResources(toks, docs)
    ctx = EvalContext(
        model, {}, None, 0, 0, "during", res, sample=sample, heldout_batch=2
    )
    return ctx, toks, docs


@torch.no_grad()
def _by_hand(model, toks, doc):
    """Loss sum, tokens, correct over one document, window by window."""
    from data.loader import iter_document_windows

    loss_sum, n, ok = 0.0, 0, 0
    for x, y in iter_document_windows(toks, doc.start, doc.length, 64):
        logits, loss = model(torch.from_numpy(x[None]), torch.from_numpy(y[None]))
        loss_sum += float(loss) * y.size
        n += y.size
        ok += int((logits.argmax(-1)[0].numpy() == y).sum())
    return loss_sum, n, ok


@pytest.mark.parametrize("kind", ["dense", "pkm"])
def test_heldout_quality_equals_a_hand_computation(kind):
    model = make_model(kind).eval()
    ctx, toks, docs = _hand_ctx(model)
    got, skipped, _ = run_metrics(["heldout_quality"], ctx)
    got = got["heldout_quality"]
    hand = {s: _by_hand(model, toks, d[0]) for s, d in docs.items()}
    for slug, (ls, n, ok) in hand.items():
        assert got[f"tokens/{slug}"] == n
        assert got[f"loss/{slug}"] == pytest.approx(ls / n, rel=1e-6)
        assert got[f"ppl/{slug}"] == pytest.approx(math.exp(ls / n), rel=1e-6)
        assert got[f"top1/{slug}"] == pytest.approx(ok / n)
    # token-weighted over the training subjects; USPTO excluded
    (la, na, oa), (lb, nb, ob) = hand["pile_cc"], hand["github"]
    assert got["tokens/pile_avg"] == na + nb == 39 + 149
    assert got["loss/pile_avg"] == pytest.approx((la + lb) / (na + nb), rel=1e-6)
    assert got["top1/pile_avg"] == pytest.approx((oa + ob) / (na + nb))
    assert got["loss/pile_avg"] != pytest.approx(
        (la / na + lb / nb) / 2, rel=1e-9
    )  # not the unweighted mean
    assert "loss/pile_avg_sample" not in got  # only a full pass carries it


def test_the_pass_leaves_the_model_as_it_found_it():
    model = make_model("pkm")
    model.train()
    before = {k: v.clone() for k, v in model.state_dict().items()}
    mem = model.memory_layers[1]
    ctx, _, _ = _hand_ctx(model)
    with torch.no_grad():
        ctx.heldout_pass()
    assert not mem.read_logging
    after = model.state_dict()
    assert all(torch.equal(before[k], after[k]) for k in before)  # BN stats too


# --------------------------------------------------------------- fact_recall
def test_fact_recall_uses_the_checkpoint_suite_scoring(bundle):
    data_config, dcfg = bundle
    model = make_model("pkm", vocab_size=50257, block_size=128).eval()
    res = EvalResources.from_config({"source": "real", "data_config": str(data_config)})
    for sample in (True, False):
        ctx = EvalContext(model, {}, None, 0, 0, "final", res, sample=sample)
        got, skipped, _ = run_metrics(["fact_recall"], ctx)
        probe = res.fact_probe(sample)
        scored = probe.score(model, "cpu", block_size=128, collect_scores=True)
        direct = keys_from_summary(
            summarize(probe, score_rows(probe, scored["_scores"]))
        )
        assert got["fact_recall"] == direct
        # Same numbers as the old probe ranking when no candidate scores tie.
        for tr, agg in scored["by_tier_role"].items():
            if agg.get("n"):
                assert got["fact_recall"][f"top1/{tr}"] == pytest.approx(
                    agg["top1"], abs=1e-6
                )
                assert got["fact_recall"][f"rank/{tr}"] == pytest.approx(
                    agg["mean_rank"], abs=1e-3
                )
    assert len(res.fact_probe(True)) < len(res.fact_probe(False)) == 840
    keys = set(got["fact_recall"])
    for tier in ("frequent", "normal", "rare", "control"):
        for role in ("test", "paraphrase"):
            assert {
                f"top1/{tier}/{role}",
                f"rank/{tier}/{role}",
                f"margin/{tier}/{role}",
            } <= keys
        for attr in ("birth_date", "birth_city", "university", "major", "employer"):
            assert f"top1/{tier}/test/{attr}" in keys


# ---------------------------------------------------------------- slot_usage
def test_slot_usage_matches_a_hand_computation_on_a_fake_read_log():
    # 1 layer, 6 slots, 2 tokens x 1 head x top-3
    idx = torch.tensor([[[[0, 1, 2]], [[2, 3, 0]]]])  # [b=1, t=2, h=1, k=3]
    w = torch.tensor([[[[0.5, 0.3, 0.2]], [[0.1, 0.6, 0.3]]]])
    usage = new_usage({3: 6})
    accumulate_reads(usage, {3: MemoryRead(idx, w)})
    got = usage_keys(usage, {3: 6})
    # slots read: 0,1,2,3 -> 4/6; best slots: 0 (token 1), 3 (token 2) -> 2/6
    assert got["coverage/layer3"] == pytest.approx(4 / 6)
    assert got["best_coverage/layer3"] == pytest.approx(2 / 6)
    p = np.array([0.5 + 0.3, 0.3, 0.2 + 0.1, 0.6, 0, 0]) / 2.0
    kl = float(sum(q * math.log(q * 6) for q in p if q > 0))
    assert got["kl_uniform/layer3"] == pytest.approx(kl, rel=1e-6)  # fp32 weights


def test_slot_usage_is_skipped_for_the_dense_model_with_a_reason():
    ctx, _, _ = _hand_ctx(make_model("dense").eval())
    got, skipped, _ = run_metrics(["heldout_quality", "slot_usage"], ctx)
    assert "slot_usage" not in got and "heldout_quality" in got
    assert "memory layer" in skipped["slot_usage"]


def test_slot_usage_shares_the_heldout_pass():
    ctx, _, _ = _hand_ctx(make_model("pkm").eval())
    calls = []
    real = ctx.model.forward
    ctx.model.forward = lambda *a, **k: calls.append(1) or real(*a, **k)
    run_metrics(["heldout_quality", "slot_usage"], ctx)
    n_with = len(calls)
    calls.clear()
    ctx2, _, _ = _hand_ctx(ctx.model)
    run_metrics(["heldout_quality"], ctx2)
    assert n_with == len(calls)  # slot_usage added no forward


def test_missing_inputs_are_skipped_not_raised():
    res = EvalResources(None, "fake")
    ctx = EvalContext(make_model("pkm").eval(), {}, None, 0, 0, "during", res)
    got, skipped, _ = run_metrics(["heldout_quality", "fact_recall", "slot_usage"], ctx)
    assert got == {} and set(skipped) == {
        "heldout_quality",
        "fact_recall",
        "slot_usage",
    }
    assert all("fake" in r for r in skipped.values())


# --------------------------------------------------------------- masked_slots
def _reads(model, x):
    model.set_read_logging(True)
    model(x)
    r = model.read_logs()[1]
    model.set_read_logging(False)
    return r


def test_masked_slots_zero_the_masked_and_keep_the_rest():
    model = make_model("pkm").eval()
    ctx = EvalContext(model, {}, None, 0, 0, "posthoc", EvalResources(None, "fake"))
    x = torch.randint(0, 257, (2, 16), generator=torch.Generator().manual_seed(1))
    with torch.no_grad():
        base = _reads(model, x)
        off = base.indices.reshape(-1)[:5].unique().tolist()
        with ctx.masked_slots({1: off}):
            masked = _reads(model, x)
    assert torch.equal(base.indices, masked.indices)  # the search is untouched
    hit = torch.isin(base.indices, torch.tensor(off))
    assert torch.all(masked.weights[hit] == 0)
    assert torch.equal(masked.weights[~hit], base.weights[~hit])  # no renormalization
    assert model.memory_layers[1].slot_mask is None


def test_masked_slots_clear_after_an_exception():
    model = make_model("pkm").eval()
    ctx = EvalContext(model, {}, None, 0, 0, "posthoc", EvalResources(None, "fake"))
    with pytest.raises(RuntimeError, match="boom"):
        with ctx.masked_slots({1: [0, 1, 2]}):
            assert model.memory_layers[1].slot_mask is not None
            raise RuntimeError("boom")
    assert model.memory_layers[1].slot_mask is None
    assert not model.memory_layers[1].renormalize_after_mask


# ----------------------------------------------------------------- schedule
def test_the_schedule_for_a_50_step_run():
    assert eval_schedule(50) == [
        (0, "during"),
        (1, "during"),
        (3, "during"),
        (5, "during"),
        (11, "during"),
        (19, "during"),
        (27, "during"),
        (38, "during"),
        (50, "final"),
    ]


def test_the_schedule_for_tier1():
    assert [s for s, _ in eval_schedule(9156)] == [
        0,
        247,
        504,
        998,
        1996,
        3498,
        4999,
        7004,
        9156,
    ]
    assert eval_schedule(9156)[-1] == (9156, "final")


def test_the_schedule_deduplicates_and_absolute_steps_win():
    assert eval_schedule(4) == [
        (0, "during"),
        (1, "during"),
        (2, "during"),
        (3, "during"),
        (4, "final"),
    ]
    assert [s for s, _ in eval_schedule(10)] == [0, 1, 2, 4, 5, 8, 10]
    assert eval_schedule(300, steps=[300, 0, 150, 150]) == [
        (0, "during"),
        (150, "during"),
        (300, "final"),
    ]
    with pytest.raises(ValueError):
        eval_schedule(10, steps=[11])


# -------------------------------------------------------------- in training
def test_a_run_writes_rows_checkpoints_and_final_metrics(done_run, bundle):
    rows = _evals(done_run)
    assert list(rows[0]) == [
        "step",
        "tokens_seen",
        "stage",
        "metric",
        "metric_id",
        "key",
        "value",
    ]
    assert {(r["step"], r["stage"]) for r in rows} == {
        ("0", "during"),
        ("5", "during"),
        ("10", "final"),
    }
    ck = done_run / "checkpoints"
    _, data_cfg = bundle
    bundle_hash = load_manifest(data_cfg, "v1")["data_sha256"]
    token_hash = sha256_file(data_cfg.tokens_dir / "train.bin")
    for s in (0, 5, 10):
        blob = torch.load(ck / f"step_{s:06d}.pt", weights_only=True)
        assert set(blob) == {"step", "tokens_seen", "model", "config", "data"}
        assert blob["step"] == s and blob["tokens_seen"] == s * 2 * 128
        data = blob["data"]
        assert data["source"] == "real" and data["version"] == "v1"
        assert data["verified"] is True
        assert data["data_sha256"] == bundle_hash
        assert data["train_bin_sha256"] == token_hash
        assert all(
            v.dtype == torch.float32
            for v in blob["model"].values()
            if v.is_floating_point()
        )
    fm = json.loads((done_run / "final_metrics.json").read_text())
    assert fm["step"] == 10 and fm["tokens_seen"] == 2560
    assert fm["metric_ids"] == {
        "heldout_quality": "Q1",
        "fact_recall": "Q2",
        "slot_usage": "U1",
    }
    assert fm["skipped"] == {}
    assert "heldout_quality/loss/pile_avg" in fm["metrics"]
    assert "slot_usage/coverage/layer1" in fm["metrics"]
    meta = json.loads((done_run / "meta.json").read_text())
    assert set(meta["eval_sets"]) == {"heldout_sample", "fact_sample"}
    tc = json.loads((done_run / "training_check.json").read_text())
    assert (
        tc["verdict"] in ("pass", "fail", "incomplete") and "flattening" in tc["rules"]
    )


def test_final_uses_the_full_sets_and_during_the_samples(done_run):
    rows = _evals(done_run)
    v = {
        (r["step"], r["key"]): float(r["value"])
        for r in rows
        if r["metric"] == "heldout_quality"
    }
    assert v[("0", "docs/pile_avg")] == 10  # 2 per training subject
    assert v[("10", "docs/pile_avg")] == 15  # all 3
    assert ("10", "loss/pile_avg_sample") in v


def test_evaluation_does_not_perturb_training(bundle, tmp_path):
    on = launch(compose(run_overrides(bundle[0], tmp_path / "on")))
    off = launch(compose([*run_overrides(bundle[0], tmp_path / "off"), "eval=off"]))
    assert _losses(on) == _losses(off)  # every step, as strings
    assert len(_losses(on)) == 10
    assert not (off / "evals.csv").exists() or not _evals(off)


def test_during_numbers_equal_a_posthoc_run_on_the_checkpoint(done_run):
    want = {
        (r["metric"], r["key"]): float(r["value"])
        for r in _evals(done_run)
        if r["step"] == "5" and r["stage"] == "during"
    }
    out = evaluate_run(done_run, step="5", sample=True, device="cpu")
    got = {(m, k): v for m, vals in out[0]["results"].items() for k, v in vals.items()}
    assert got.keys() == want.keys()
    for k in want:
        assert got[k] == pytest.approx(want[k], rel=1e-9, abs=1e-12), k


def test_posthoc_rows_replace_and_leave_final_metrics_alone(done_run):
    before = (done_run / "final_metrics.json").read_bytes()
    evaluate_run(done_run, step="init", metrics=["heldout_quality"], device="cpu")
    evaluate_run(done_run, step="init", metrics=["heldout_quality"], device="cpu")
    post = [r for r in _evals(done_run) if r["stage"] == "posthoc" and r["step"] == "0"]
    keys = Counter((r["step"], r["metric"], r["key"]) for r in post)
    assert keys and max(keys.values()) == 1
    assert {k[1] for k in keys} == {"heldout_quality"}
    assert (done_run / "final_metrics.json").read_bytes() == before
    old = json.loads((done_run / "final_metrics.json").read_text())
    evaluate_run(
        done_run, step="final", metrics=["slot_usage"], update_final=True, device="cpu"
    )
    fm = json.loads((done_run / "final_metrics.json").read_text())
    # merged, not replaced: the metrics not re-run are still there, unchanged
    assert set(fm["metric_ids"]) == {"heldout_quality", "fact_recall", "slot_usage"}
    for k, v in old["metrics"].items():
        if not k.startswith("slot_usage/"):
            assert fm["metrics"][k] == v, k
    assert any(k.startswith("slot_usage/") for k in fm["metrics"])
    # and a different step is refused instead of mixing two checkpoints
    with pytest.raises(ValueError, match="mix two checkpoints"):
        evaluate_run(
            done_run,
            step="init",
            metrics=["slot_usage"],
            update_final=True,
            device="cpu",
        )
    assert json.loads((done_run / "final_metrics.json").read_text()) == fm


def test_merge_final_metrics_on_hand_made_dicts():
    from memlayers.eval.writers import merge_final_metrics

    old = {
        "metrics": {"a/x": 1.0, "a/y": 2.0, "b/x": 3.0},
        "metric_ids": {"a": "Q1", "b": "Q2"},
        "skipped": {"c": "no read log"},
        "step": 10,
        "tokens_seen": 100,
    }
    new = {
        "metrics": {"b/z": 9.0, "c/x": 4.0},
        "metric_ids": {"b": "Q2", "c": "U4"},
        "skipped": {},
        "step": 10,
        "tokens_seen": 100,
    }
    m = merge_final_metrics(old, new)
    assert m["metrics"] == {
        "a/x": 1.0,
        "a/y": 2.0,
        "b/z": 9.0,
        "c/x": 4.0,
    }  # b/x dropped
    assert m["metric_ids"] == {"a": "Q1", "b": "Q2", "c": "U4"}
    assert m["skipped"] == {}  # c ran now
    assert merge_final_metrics(None, new) == new
    with pytest.raises(ValueError, match="step 10"):
        merge_final_metrics(old, {**new, "step": 0})


def test_the_cli_rejects_an_unknown_metric(done_run):
    with pytest.raises(UnknownMetric):
        evaluate_run(done_run, step="final", metrics=["nope"], device="cpu")


def test_resume_after_a_kill_between_evals_has_no_duplicate_rows(bundle, tmp_path):
    over = [
        *run_overrides(bundle[0], tmp_path, steps=12, eval_steps="[0,4,8,12]"),
        "train.ckpt_every=3",
    ]
    env = {**os.environ, "MEMLAYERS_TEST_HALT": "8:exit:eval_rows"}
    cmd = [sys.executable, "-m", "memlayers.run", *map(str, over)]
    r = subprocess.run(cmd, cwd=ROOT, env=env, capture_output=True, text=True)
    assert r.returncode == 137, r.stderr
    run_dir = tmp_path / "smoke-s0"
    assert {x["step"] for x in _evals(run_dir)} == {"0", "4", "8"}  # rows at 8 written
    assert torch.load(run_dir / "checkpoints/last.pt", weights_only=False)["step"] == 6
    env.pop("MEMLAYERS_TEST_HALT")
    r = subprocess.run(cmd, cwd=ROOT, env=env, capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    assert "dropped" in r.stdout
    keys = Counter(
        (x["step"], x["stage"], x["metric"], x["key"]) for x in _evals(run_dir)
    )
    assert max(keys.values()) == 1
    assert {k[0] for k in keys} == {"0", "4", "8", "12"}
    assert read_status(run_dir)["state"] == "done"


# ----------------------------------------------------------------- eval sets
def test_two_builds_are_byte_identical(bundle):
    _, dcfg = bundle
    from memlayers.eval.eval_sets import eval_sets_dir, manifest_file

    files = sorted(eval_sets_dir(dcfg).glob("*.json"))
    first = {p.name: p.read_bytes() for p in files + [manifest_file(dcfg)]}
    build_sets(
        dcfg, per_subject=2, per_tier=2, readlog_tokens_per_subject=READLOG_BUDGET
    )
    second = {p.name: p.read_bytes() for p in files + [manifest_file(dcfg)]}
    assert first == second


def test_the_sets_come_from_the_data_seed_not_the_run_seed(bundle, tmp_path):
    a = launch(
        compose(
            [
                *run_overrides(bundle[0], tmp_path),
                "seed=0",
                "train.steps=2",
                "eval.steps=[0]",
            ]
        )
    )
    b = launch(
        compose(
            [
                *run_overrides(bundle[0], tmp_path),
                "seed=1",
                "train.steps=2",
                "eval.steps=[0]",
            ]
        )
    )
    ma, mb = (json.loads((d / "meta.json").read_text())["eval_sets"] for d in (a, b))
    assert ma == mb


def test_a_changed_set_is_refused_at_run_start(bundle, tmp_path):
    _, dcfg = bundle
    from memlayers.eval.eval_sets import eval_sets_dir

    p = eval_sets_dir(dcfg) / "heldout_sample.json"
    good = p.read_bytes()
    try:
        p.write_bytes(good.replace(b'"per_subject": 2', b'"per_subject": 3'))
        with pytest.raises(RunRefused, match="eval sets: .*sha256"):
            launch(compose(run_overrides(bundle[0], tmp_path)))
        assert not (tmp_path / "smoke-s0").exists()
    finally:
        p.write_bytes(good)


# ------------------------------------------------------------ training_check
def _curve(points, final_full=None):
    """eval rows for a pile_avg curve [(step, loss)], final = the last point."""
    rows = []
    last = points[-1][0]
    for s, l in points:
        stage = "final" if s == last else "during"
        key = "loss/pile_avg_sample" if stage == "final" else "loss/pile_avg"
        rows.append(
            dict(
                step=s,
                tokens_seen=s * 1000,
                stage=stage,
                metric="heldout_quality",
                metric_id="Q1",
                key=key,
                value=l,
            )
        )
        if stage == "final":
            rows.append(
                dict(
                    step=s,
                    tokens_seen=s * 1000,
                    stage=stage,
                    metric="heldout_quality",
                    metric_id="Q1",
                    key="loss/pile_avg",
                    value=final_full or l,
                )
            )
    return rows


def _final(metric, **vals):
    return [
        dict(
            step=100,
            tokens_seen=100000,
            stage="final",
            metric=metric,
            metric_id="-",
            key=k.replace("__", "/"),
            value=v,
        )
        for k, v in vals.items()
    ]


HEALTHY = [
    (0, 10.8),
    (5, 9.0),
    (10, 7.5),
    (25, 6.0),
    (50, 5.0),
    (75, 4.6),
    (100, 4.508),
]


def _train(n=100, start=10.8, end=4.0, spike=None, nan_at=None):
    rows = []
    for s in range(1, n + 1):
        l = end + (start - end) * math.exp(-s / 15)
        if spike and s == spike:
            l *= 2.0
        if nan_at and s == nan_at:
            l = float("nan")
        rows.append({"step": s, "loss": l})
    return rows


def _check(train=None, curve=HEALTHY, cov=0.8, freq=0.4, ctrl=0.01, memory=(3,)):
    ev = _curve(curve)
    ev += _final("slot_usage", coverage__layer3=cov)
    ev += _final("fact_recall", top1__frequent__test=freq, top1__control__test=ctrl)
    for r in ev:
        r["step"] = 100
    ev = _curve(curve) + [r for r in ev if r["metric"] != "heldout_quality"]
    return training_check(
        train or _train(), ev, warmup_steps=5, memory_layers=list(memory)
    )


def test_a_healthy_cosine_run_passes_and_reports_flattening():
    res = _check()
    assert res["verdict"] == "pass", res
    fl = res["rules"]["flattening"]
    assert not fl["gating"] and fl["ratio"] is not None and 0 < fl["ratio"] < 1
    # it still improves about 2% over its last interval, which must not fail it
    assert fl["last_interval_relative_drop"] == pytest.approx(0.02, abs=0.001)


@pytest.mark.parametrize(
    "kwargs, rule",
    [
        (dict(train=_train(nan_at=40)), "finite"),
        (dict(train=_train(spike=60)), "no_divergence"),
        (dict(curve=[(0, 10.8), (50, 9.5), (100, 9.0)]), "learned"),
        (dict(curve=[(0, 10.8), (50, 4.0), (100, 4.1)]), "not_rising"),
        (dict(cov=0.1), "coverage"),
        (dict(freq=0.01, ctrl=0.01), "fact_learning"),
        (dict(freq=0.0, ctrl=0.0), "fact_learning"),
    ],
)
def test_each_gating_rule_fails_on_its_bad_curve(kwargs, rule):
    res = _check(**kwargs)
    assert res["verdict"] == "fail"
    assert rule in res["failed"], res["failed"]


def test_a_nan_in_an_eval_loss_also_fails_finite():
    res = _check(curve=[(0, 10.8), (50, float("nan")), (100, 4.0)])
    assert "finite" in res["failed"]


def test_coverage_does_not_gate_a_dense_run():
    res = _check(cov=0.0, memory=())
    assert res["verdict"] == "pass" and not res["rules"]["coverage"]["gating"]


def test_missing_evals_make_the_verdict_incomplete():
    res = training_check(_train(), [], warmup_steps=5, memory_layers=[3])
    assert res["verdict"] == "incomplete"
    assert set(res["not_evaluated"]) >= {"learned", "fact_learning", "coverage"}


def test_weight_checkpoints_store_the_tied_embedding_once(done_run):
    blob = torch.load(done_run / "checkpoints/step_000010.pt", weights_only=False)
    m = blob["model"]
    assert m["lm_head.weight"].data_ptr() == m["transformer.wte.weight"].data_ptr()
    n_bytes = sum(
        t.untyped_storage().nbytes()
        for t in {v.data_ptr(): v for v in m.values()}.values()
    )
    params = sum(
        p.numel()
        for p in make_model("pkm", vocab_size=50257, block_size=128).parameters()
    )
    assert (
        n_bytes < 4 * params * 1.05
    )  # one fp32 copy of each parameter, not two of wte


def test_a_kill_between_the_last_checkpoint_and_the_final_eval_is_resumed(
    bundle, tmp_path
):
    """Killed right after the checkpoint at the final step, before its eval:
    the resume must run the final eval, not finish "done" without it."""
    over = [
        *run_overrides(bundle[0], tmp_path, steps=10, eval_steps="[0,10]"),
        "train.ckpt_every=5",
    ]
    cmd = [sys.executable, "-m", "memlayers.run", *map(str, over)]
    env = {**os.environ, "MEMLAYERS_TEST_HALT": "10:exit"}
    r = subprocess.run(cmd, cwd=ROOT, env=env, capture_output=True, text=True)
    assert r.returncode == 137, r.stderr
    run_dir = tmp_path / "smoke-s0"
    assert {(x["step"], x["stage"]) for x in _evals(run_dir)} == {("0", "during")}
    env.pop("MEMLAYERS_TEST_HALT")
    r = subprocess.run(cmd, cwd=ROOT, env=env, capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    points = Counter(
        (x["step"], x["stage"], x["metric"], x["key"]) for x in _evals(run_dir)
    )
    assert max(points.values()) == 1
    assert {(k[0], k[1]) for k in points} == {("0", "during"), ("10", "final")}
    assert (run_dir / "final_metrics.json").exists()
    assert (
        json.loads((run_dir / "training_check.json").read_text())["not_evaluated"] == []
    )


@pytest.mark.parametrize(
    "missing", ["checkpoints/step_000002.pt", "final_metrics.json"]
)
def test_resume_restores_missing_eval_output_before_callback(bundle, tmp_path, missing):
    cfg = compose(run_overrides(bundle[0], tmp_path, steps=2, eval_steps="[0,2]"))
    run_dir = tmp_path / "smoke-s0"
    seen = []

    def inspect(snapshot):
        saved = torch.load(snapshot, map_location="cpu", weights_only=True)
        seen.append(saved["step"])
        assert snapshot.name == f"step_{saved['step']:06d}.pt"
        assert len(saved["data"]["train_bin_sha256"]) == 64

    def interrupt(snapshot):
        inspect(snapshot)
        if seen[-1] == 2:
            raise RuntimeError("simulated interruption")

    with pytest.raises(RuntimeError, match="simulated interruption"):
        launch(cfg, after_eval_checkpoint=interrupt)
    expected_rows = _evals(run_dir)
    assert seen == [0, 2]
    (run_dir / missing).unlink()
    launch(cfg, after_eval_checkpoint=inspect)
    assert seen == [0, 2, 2]
    assert (run_dir / missing).is_file()
    assert _evals(run_dir) == expected_rows


def test_a_build_does_not_overwrite_a_committed_manifest_that_differs(tmp_path):
    from memlayers.eval.eval_sets import EvalSetMismatch, manifest_file

    _, dcfg = make_mini_bundle(tmp_path / "b")
    mf = manifest_file(dcfg)
    man = json.loads(mf.read_text())
    man["sets"]["fact_sample"]["sha256"] = "0" * 64  # "committed" with other data
    mf.write_text(json.dumps(man))
    with pytest.raises(EvalSetMismatch, match="fact_sample 0000000000000000 ->"):
        build_sets(
            dcfg, per_subject=2, per_tier=2, readlog_tokens_per_subject=READLOG_BUDGET
        )
    assert json.loads(mf.read_text())["sets"]["fact_sample"]["sha256"] == "0" * 64
    build_sets(
        dcfg,
        per_subject=2,
        per_tier=2,
        readlog_tokens_per_subject=READLOG_BUDGET,
        replace_manifest=True,
    )
    assert json.loads(mf.read_text())["sets"]["fact_sample"]["sha256"] != "0" * 64


def test_eval_timing_sums_every_heldout_pass(done_run):
    """A metric that makes its own held-out pass adds to heldout_pass time."""
    from memlayers.eval.testkit import temporary_metric

    def second_pass(ctx):
        """Runs a second, different held-out pass."""
        p = ctx.heldout_pass(sample=True, subjects=["pile_cc"], capture_reads=False)
        return {"tokens/pile_cc": p.sums["pile_cc"]["tokens"]}

    with temporary_metric("example_second_pass", metric_id="EX9") as reg:
        reg(second_pass)
        evaluate_run(
            done_run,
            step="final",
            metrics=["heldout_quality", "example_second_pass"],
            device="cpu",
        )
    with open(done_run / "eval_timing.csv", newline="") as fh:
        rows = [r for r in csv.DictReader(fh) if r["stage"] == "posthoc"]
    last = {r["metric"]: float(r["seconds"]) for r in rows[-5:]}
    assert last["heldout_pass"] >= 0.9 * (
        last["heldout_quality"] + last["example_second_pass"]
    )


def test_a_metric_skipped_now_keeps_its_old_final_values():
    from memlayers.eval.writers import merge_final_metrics

    old = {
        "metrics": {"fact_recall/top1/x": 0.4, "heldout_quality/loss/a": 5.0},
        "metric_ids": {"fact_recall": "Q2", "heldout_quality": "Q1"},
        "skipped": {},
        "step": 10,
        "tokens_seen": 1,
    }
    new = {
        "metrics": {"heldout_quality/loss/a": 4.9},
        "metric_ids": {"fact_recall": "Q2", "heldout_quality": "Q1"},
        "skipped": {"fact_recall": "fact rows not found"},
        "step": 10,
        "tokens_seen": 1,
    }
    m = merge_final_metrics(old, new)
    assert m["metrics"] == {"fact_recall/top1/x": 0.4, "heldout_quality/loss/a": 4.9}
    assert m["skipped"] == {}  # it has values, so it is not "skipped"


def test_update_final_on_several_checkpoints_is_refused_before_evaluating(done_run):
    before = (done_run / "evals.csv").read_bytes()
    with pytest.raises(ValueError, match="takes one checkpoint"):
        evaluate_run(
            done_run,
            step="all",
            metrics=["heldout_quality"],
            update_final=True,
            device="cpu",
        )
    with pytest.raises(ValueError, match="mix two checkpoints"):
        evaluate_run(
            done_run,
            step="init",
            metrics=["heldout_quality"],
            update_final=True,
            device="cpu",
        )
    assert (done_run / "evals.csv").read_bytes() == before  # nothing was evaluated
