"""The worked example of docs/metrics_interface.md, end to end, and the
read-log pass, reader and helpers the analysis metrics build on."""

import json
import shutil
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import torch

from memlayers.eval.context import EvalResources
from memlayers.eval.evaluator import run_metrics
from memlayers.eval.registry import registered
from memlayers.eval.testkit import metric_kit, temporary_metric  # noqa: F401
from memlayers.memory import MemoryRead
from memlayers.readlog import ReadLog, ReadLogWriter, index_dtype
from memlayers.readlog_pass import ReadlogRefused, readlog_pass

LAYER = 1


def _rl(kit, step):
    return ReadLog.open(kit.run_dir / "readlogs" / f"step_{step:06d}")


# --------------------------------------------------------------- the example
def top_slot_share(ctx):
    """Share of the gate weight that goes to the 1% most-read slots, per segment."""
    rl = ctx.readlog()
    out = {}
    for layer in rl.layers:
        for seg in ("heldout_label", "bio"):
            c = rl.slot_counts(layer, rl.select(segment=seg), weighted=True)
            k = max(1, len(c) // 100)
            out[f"top1pct_share/{seg}/layer{layer}"] = float(
                np.sort(c)[::-1][:k].sum() / c.sum()
            )
    return out


def test_top_slot_share(metric_kit):
    with temporary_metric(
        "example_top_slot_share",
        metric_id="EX1",
        inputs=("model", "readlog"),
        needs_memory=True,
    ) as register:
        register(top_slot_share)
        out = metric_kit.run_metric(top_slot_share)
        assert 0 < out["top1pct_share/bio/layer1"] <= 1
    assert "example_top_slot_share" not in registered()


def test_the_example_runs_through_evaluate_and_compare(metric_kit, tmp_path):
    from memlayers.compare import compare
    from memlayers.evaluate import evaluate_run

    run = tmp_path / "runs" / metric_kit.run_dir.name
    shutil.copytree(metric_kit.run_dir, run)
    with temporary_metric(
        "example_top_slot_share",
        metric_id="EX1",
        stages=("posthoc",),
        inputs=("model", "readlog"),
        needs_memory=True,
    ) as register:
        register(top_slot_share)
        evaluate_run(
            run,
            step="final",
            metrics=["example_top_slot_share"],
            update_final=True,
            device="cpu",
        )
        rows = pd.read_csv(run / "evals.csv")
        ex = rows[rows.metric == "example_top_slot_share"]
        assert set(ex.stage) == {"posthoc"} and set(ex.metric_id) == {"EX1"}
        assert len(ex) == 2 and set(ex.step) == {10}
        fm = json.loads((run / "final_metrics.json").read_text())
        assert "example_top_slot_share/top1pct_share/bio/layer1" in fm["metrics"]
        compare([tmp_path / "runs"], tmp_path / "cmp")
        runs = pd.read_csv(tmp_path / "cmp" / "runs.csv")
        assert "example_top_slot_share/top1pct_share/bio/layer1" in runs.columns
        assert runs.readlog_tokens_sha256.notna().all()


def test_a_readlog_metric_is_skipped_without_a_read_log(metric_kit):
    ctx = metric_kit.context()
    ctx.step = 7  # no read log at step 7
    with temporary_metric(
        "example_needs_log", metric_id="EX2", inputs=("model", "readlog")
    ) as reg:
        reg(top_slot_share)
        got, skipped, _ = run_metrics(["example_needs_log"], ctx)
    assert got == {} and "readlog_pass" in skipped["example_needs_log"]
    with pytest.raises(RuntimeError, match="run the read-log pass first"):
        ctx.readlog()


# ----------------------------------------------------------- the read log
@pytest.mark.parametrize("step", [0, 10])
def test_the_read_log_equals_live_reads(metric_kit, step):
    """Held-out windows and bio rows, re-run directly: indices exact, weights to fp16."""
    from data.loader import iter_document_windows

    rl = _rl(metric_kit, step)
    ctx = metric_kit.context("init" if step == 0 else "final")
    model = ctx.model
    t = rl.tokens
    idx, w = rl.indices(LAYER), rl.weights(LAYER)
    # a held-out document: its windows, as heldout_quality cuts them
    doc = t[t.segment == "heldout_label"].doc_id.iloc[0]
    rows = rl.select(doc_id=doc)
    rows = rows[np.argsort(t.position.to_numpy()[rows], kind="stable")]
    from data import pack

    d = metric_kit.dcfg
    index = pack.read_index(Path(d.heldout_tokens_dir) / "label.idx.parquet")
    k = index["doc_id"].index(doc)
    toks = np.memmap(
        Path(d.heldout_tokens_dir) / "label.bin", dtype=np.uint16, mode="r"
    )
    live_i, live_w = [], []
    model.set_read_logging(True)
    with torch.no_grad():
        for x, _ in iter_document_windows(
            toks, int(index["start"][k]), int(index["length"][k]), 128
        ):
            model(torch.from_numpy(x[None]).long())
            r = model.read_logs()[LAYER]
            live_i.append(r.indices[0].numpy())
            live_w.append(r.weights[0].numpy())
        live_i, live_w = np.concatenate(live_i), np.concatenate(live_w)
        assert np.array_equal(idx[rows].astype(np.int64), live_i)
        # fp16 tolerance: the pass batches 8 windows, this re-run takes one, so a
        # weight can land one fp16 rounding step (~2.4e-4 at 0.25) apart
        assert np.allclose(w[rows].astype(np.float32), live_w, atol=1e-3, rtol=0)
        # a bio row
        fid = t[t.segment == "bio"].fact_id.iloc[5]
        brows = rl.select(fact_id=fid)
        x = torch.tensor(t.token_id.to_numpy()[brows][None]).long()
        model(x)
        r = model.read_logs()[LAYER]
    model.set_read_logging(False)
    assert np.array_equal(idx[brows].astype(np.int64), r.indices[0].numpy())
    assert np.allclose(
        w[brows].astype(np.float32), r.weights[0].numpy(), atol=1e-3, rtol=0
    )


def test_token_table_order_and_answer_positions(metric_kit):
    from data import pack
    from data.common import get_encoder, read_jsonl

    rl = _rl(metric_kit, 10)
    t = rl.tokens
    assert len(t) == rl.n_tokens == rl.indices(LAYER).shape[0]
    d = metric_kit.dcfg
    index = pack.read_index(Path(d.heldout_tokens_dir) / "label.idx.parquet")
    toks = np.memmap(
        Path(d.heldout_tokens_dir) / "label.bin", dtype=np.uint16, mode="r"
    )
    for doc in t[t.segment == "heldout_label"].doc_id.unique():
        k = index["doc_id"].index(doc)
        sub = t[t.doc_id == doc].sort_values("position")
        a, n = int(index["start"][k]), int(index["length"][k])
        assert sub.position.tolist() == list(range(n - 1))  # every input position once
        assert np.array_equal(sub.token_id.to_numpy(), np.asarray(toks[a : a + n - 1]))
    enc = get_encoder(d.tokenizer_name, d.vocab_size)
    facts = {r["fact_id"]: r for r in read_jsonl(Path(d.bios_dir) / "facts.jsonl")}
    bio = t[t.segment == "bio"]
    assert set(bio.role) <= {"test", "paraphrase"}
    for fid, sub in bio.groupby("fact_id", sort=False):
        f = facts[fid]
        prompt = enc.encode_ordinary(f["prompt"])
        assert sub.token_id.tolist() == prompt + f["value_token_ids"]
        assert int(sub.is_answer_position.sum()) == 1
        assert int(sub.position[sub.is_answer_position].iloc[0]) == len(prompt) - 1
        assert sub.is_value_token.tolist() == [False] * len(prompt) + [True] * len(
            f["value_token_ids"]
        )
        assert (
            enc.decode(sub.token_id[sub.is_value_token].tolist())
            == " " + f["true_value"]
        )
        assert set(sub.tier) == {f["tier"]} and set(sub.attribute) == {f["attribute"]}
    m = rl.manifest
    assert m["n_tokens_by_segment"]["bio"] == len(bio)
    assert (
        m["eval_set"]["name"] == "readlog_tokens" and len(m["eval_set"]["sha256"]) == 64
    )
    assert {"layer1_indices.bin", "layer1_weights.bin", "tokens.parquet"} <= set(
        m["files"]
    )
    assert m["index_dtype"]["1"] == "uint16"


def test_reader_queries_agree_with_brute_force(metric_kit):
    rl = _rl(metric_kit, 10)
    t = rl.tokens
    rows = rl.select(segment="bio", tier=["frequent", "rare"], role="test")
    want = np.flatnonzero(
        (
            (t.segment == "bio")
            & t.tier.isin(["frequent", "rare"])
            & (t.role == "test")
        ).to_numpy()
    )
    assert np.array_equal(rows, want) and len(rows)
    idx = np.asarray(rl.indices(LAYER)).astype(np.int64)
    w = np.asarray(rl.weights(LAYER)).astype(np.float64)
    n = rl.n_slots(LAYER)
    assert np.array_equal(rl.slot_counts(LAYER), np.bincount(idx.ravel(), minlength=n))
    assert np.array_equal(
        rl.slot_counts(LAYER, rows), np.bincount(idx[rows].ravel(), minlength=n)
    )
    assert np.allclose(
        rl.slot_counts(LAYER, rows, weighted=True),
        np.bincount(idx[rows].ravel(), weights=w[rows].ravel(), minlength=n),
    )
    seen = []
    for r, i, ww in rl.iter_chunks(LAYER, rows, chunk_tokens=1000):
        assert (
            len(r) <= 1000
            and np.array_equal(i, idx[r])
            and i.shape[1:] == idx.shape[1:]
        )
        seen.append(r)
    assert np.array_equal(np.concatenate(seen), rows)
    all_rows = np.concatenate(
        [r for r, _, _ in rl.iter_chunks(LAYER, chunk_tokens=4096)]
    )
    assert np.array_equal(all_rows, np.arange(rl.n_tokens))
    with pytest.raises((ValueError, TypeError)):
        rl.indices(LAYER)[0, 0, 0] = 1  # read-only
    with pytest.raises(KeyError):
        rl.select(colour="red")


def test_index_dtype_by_slot_count(tmp_path):
    assert index_dtype(65_536) == np.uint16 and index_dtype(65_537) == np.uint32
    # a 70,000-slot layer round-trips through the writer and the reader
    w = ReadLogWriter(
        tmp_path,
        {0: 70_000},
        {0: 2},
        {0: 3},
        index_file="layer{layer}_indices.bin",
        weight_file="layer{layer}_weights.bin",
    )
    ids = torch.tensor([[[[69_999, 65_536, 1], [5, 6, 7]]]])
    ws = torch.tensor([[[[0.5, 0.3, 0.2], [0.6, 0.3, 0.1]]]])
    w.append(0, {0: MemoryRead(ids, ws)})
    pd.DataFrame({"token_id": [1], "segment": ["bio"]}).to_parquet(
        tmp_path / "tokens.parquet"
    )
    w.close(extra={"layers": [0], "n_tokens": 1}, records=False)
    rl = ReadLog.open(tmp_path)
    assert rl.indices(0).dtype == np.uint32 and int(rl.indices(0)[0, 0, 0]) == 69_999
    assert (tmp_path / "layer0_indices.bin").stat().st_size == 2 * 3 * 4


# ---------------------------------------------------------------- refusals
def test_a_dense_run_is_refused(tmp_path):
    from memlayers.config import compose
    from memlayers.run import launch

    run = launch(
        compose(
            [
                "experiment=smoke",
                "data=fake",
                "model=tiny_dense",
                "runtime=cpu",
                "train.steps=2",
                "eval=off",
                f"out_root={tmp_path}",
            ]
        )
    )
    with pytest.raises(ReadlogRefused, match="dense run"):
        readlog_pass(run, ["final"])
    assert not (run / "readlogs").exists()


def test_too_little_disk_and_an_existing_log_are_refused(metric_kit, monkeypatch):
    import shutil as sh

    with pytest.raises(ReadlogRefused, match="exists"):
        readlog_pass(metric_kit.run_dir, ["final"])
    usage = sh.disk_usage(metric_kit.run_dir)
    monkeypatch.setattr(sh, "disk_usage", lambda p: usage._replace(free=10))
    with pytest.raises(ReadlogRefused, match="GB free"):
        readlog_pass(metric_kit.run_dir, ["final"], force=True)
    assert (metric_kit.run_dir / "readlogs" / "step_000010" / "manifest.json").exists()


def test_a_budget_mismatch_is_refused(metric_kit, tmp_path):
    import yaml

    run = tmp_path / metric_kit.run_dir.name
    shutil.copytree(metric_kit.run_dir, run, ignore=shutil.ignore_patterns("readlogs"))
    cfg = yaml.safe_load((run / "config.yaml").read_text())
    cfg["eval"]["readlog"]["tokens_per_subject"] = 999
    (run / "config.yaml").write_text(yaml.safe_dump(cfg))
    with pytest.raises(ReadlogRefused, match="--readlog-tokens-per-subject 999"):
        readlog_pass(run, ["final"])


# ------------------------------------------------------------------ helpers
def test_value_table_and_unembedding_are_copies(metric_kit):
    ctx = metric_kit.context()
    v = ctx.value_table(LAYER)
    assert tuple(v.shape) == (256, 64) and v.dtype == torch.float32
    assert torch.equal(v, ctx.memory_layers[LAYER].pkm.values.weight.detach())
    u = ctx.unembedding()
    assert tuple(u.shape) == (50257, 64)
    v.zero_()
    u.zero_()
    assert ctx.memory_layers[LAYER].pkm.values.weight.abs().sum() > 0
    assert ctx.model.lm_head.weight.abs().sum() > 0


def test_used_slots(metric_kit):
    ctx = metric_kit.context()
    used = ctx.used_slots(LAYER)
    assert np.array_equal(
        used, np.flatnonzero(_rl(metric_kit, 10).slot_counts(LAYER) > 0)
    )


def _cells(ctx, slots, n_bins):
    used, cb, nb = ctx.slot_bins(LAYER, n_bins)
    pos = {int(s): i for i, s in enumerate(used)}
    return Counter((int(cb[pos[int(s)]]), int(nb[pos[int(s)]])) for s in slots)


def test_matched_random_slots(metric_kit):
    ctx = metric_kit.context()
    used = ctx.used_slots(LAYER)
    slots = used[np.random.default_rng(3).choice(len(used), 12, replace=False)]
    got = ctx.matched_random_slots(LAYER, slots, 24, np.random.default_rng(0), n_bins=3)
    assert len(got) == 24 and len(set(got.tolist())) == 24
    assert not set(got.tolist()) & set(slots.tolist())
    a, b = _cells(ctx, slots, 3), _cells(ctx, got, 3)
    assert {k: 2 * v for k, v in a.items()} == dict(b)  # same proportions
    again = ctx.matched_random_slots(
        LAYER, slots, 24, np.random.default_rng(0), n_bins=3
    )
    assert np.array_equal(got, again)
    other = ctx.matched_random_slots(
        LAYER, slots, 24, np.random.default_rng(1), n_bins=3
    )
    assert not np.array_equal(got, other)
    with pytest.raises(
        ValueError, match=r"cell \(read-count bin \d+, value-norm bin \d+\)"
    ):
        ctx.matched_random_slots(LAYER, slots, 5000, np.random.default_rng(0), n_bins=3)


def test_masked_loss_with_no_mask_equals_heldout_quality(metric_kit):
    ctx = metric_kit.context(sample=True)
    got = ctx.loss_with_masked_slots(LAYER, [])
    q, _, _ = run_metrics(["heldout_quality"], metric_kit.context(sample=True))
    q = q["heldout_quality"]
    for slug, v in got.items():
        assert v == pytest.approx(q[f"loss/{slug}"], rel=1e-12), slug


def test_masking_the_slots_a_document_reads_raises_its_loss(metric_kit):
    """Make the memory matter for one subject (fit only the value table to its
    sample documents), then switch off the slots those documents read."""
    from data.loader import iter_document_windows

    ctx = metric_kit.context(sample=True)
    model, mem = ctx.model, ctx.memory_layers[LAYER]
    slug = "pile_cc"
    docs = ctx.heldout("test", True)[slug]
    toks = ctx.resources.tokens("test")
    wins = [
        (torch.from_numpy(x[None]).long(), torch.from_numpy(y[None]).long())
        for d in docs
        for x, y in iter_document_windows(toks, d.start, d.length, 128)
    ]
    opt = torch.optim.Adam([mem.pkm.values.weight], lr=0.05)
    model.train()
    for _ in range(25):
        for x, y in wins:
            opt.zero_grad()
            model(x, y)[1].backward()
            opt.step()
    model.eval()
    p = ctx.heldout_pass(sample=True, subjects=[slug])
    read = np.flatnonzero(p.usage[LAYER]["counts"].numpy() > 0)
    before = {k: v.clone() for k, v in model.state_dict().items()}
    base = ctx.loss_with_masked_slots(LAYER, [], subjects=[slug])[slug]
    masked = ctx.loss_with_masked_slots(LAYER, read, subjects=[slug])[slug]
    assert masked > base + 0.1, (base, masked)
    after = model.state_dict()
    assert all(torch.equal(before[k], after[k]) for k in before)  # unchanged
    assert mem.slot_mask is None


def test_fact_recall_with_masked_slots(metric_kit):
    from memlayers.eval.eval_sets import load_fact_sample

    ctx = metric_kit.context()
    fids = load_fact_sample(metric_kit.dcfg)[:20]
    base = ctx.fact_recall_with_masked_slots(LAYER, [], fids)
    assert list(base.fact_id) == fids
    assert set(base.columns) == {
        "fact_id",
        "tier",
        "role",
        "attribute",
        "top1",
        "rank",
        "margin",
    }
    direct = ctx.fact_probe(True)
    full = direct.score(ctx.model, "cpu", block_size=128)
    pos = {r.fact_id: i for i, r in enumerate(direct.rows)}
    assert [int(full["_rank"][pos[f]]) for f in fids] == base["rank"].tolist()
    masked = ctx.fact_recall_with_masked_slots(LAYER, ctx.used_slots(LAYER), fids)
    assert not np.allclose(masked.margin, base.margin)
    assert ctx.memory_layers[LAYER].slot_mask is None
