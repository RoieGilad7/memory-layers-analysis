"""Phase 2: the same-document loss in the training step (train.doc_loss_* keys)."""

import copy
import csv
import json
import math
import subprocess
import sys
from pathlib import Path

import pytest
import torch
import yaml

from memlayers.config import compose, to_train_config
from memlayers.runlog.files import TRAIN_FIELDS, FilesSink
from memlayers.runlog.wandb_sink import TRAIN_KEYS, train_payload
from memlayers.train import Trainer, load_config

ROOT = Path(__file__).resolve().parent.parent
GOLDEN = ROOT / "tests" / "fixtures" / "doc_loss_off_golden.json"
DOC_COLS = ["doc_loss", "doc_weight", "doc_gap", "doc_halves"]
EOT = 256  # tiny models have vocab_size 257


def _golden():
    return json.loads(GOLDEN.read_text())


def _cfg_dict(tmp_path, **train):
    d = copy.deepcopy(_golden()["config"])
    d["runtime"]["out_dir"] = str(tmp_path / "run")
    d["train"].update(train)
    return d


def _trainer(tmp_path, d=None, dataset=None, **train):
    d = d or _cfg_dict(tmp_path, **train)
    tmp_path.mkdir(parents=True, exist_ok=True)
    p = tmp_path / "cfg.yaml"
    p.write_text(yaml.safe_dump(d))
    return Trainer(load_config(p), dataset=dataset)


def _query_hooks(model):
    return {
        i: len(m._query_module()._forward_hooks) for i, m in model.memory_layers.items()
    }


# ---- loss off: bit-identical to main --------------------------------------------
def test_loss_off_reproduces_the_golden_losses_exactly(tmp_path):
    g = _golden()
    tr = _trainer(tmp_path)
    assert tr.cfg.train.doc_loss_weight == 0.0
    assert tr.doc_layer is None
    hist = tr.train(progress=False)
    assert [h["loss"] for h in hist] == g["losses"]
    assert _query_hooks(tr.model) == {1: 0}
    for m in tr.model.memory_layers.values():
        assert m._query_hook_handle is None and m.kept_queries() is None
    for h in hist:
        assert all(h[c] == "" for c in DOC_COLS)


# ---- loss on --------------------------------------------------------------------
def test_loss_on_keeps_queries_and_fills_the_columns(tmp_path):
    tr = _trainer(
        tmp_path,
        doc_loss_weight=0.5,
        doc_loss_ramp_steps=0,
        doc_loss_eot_id=EOT,
        doc_loss_min_piece_tokens=8,
    )
    assert tr.doc_layer == 1
    assert _query_hooks(tr.model) == {1: 1}
    row = tr.train_step()
    # released after backward
    assert tr.model.kept_queries() == {}
    x, _ = tr.data.get_batch(0, 4)
    tr.model(x)
    assert set(tr.model.kept_queries()) == {1}
    assert row["doc_weight"] == 0.5
    assert isinstance(row["doc_loss"], float) and math.isfinite(row["doc_loss"])
    assert isinstance(row["doc_gap"], float)
    assert row["doc_halves"] >= 4
    # the logged loss is the LM loss only: same as a loss-off run at step 1
    assert row["loss"] == _golden()["losses"][0]


def test_lambda_ramp(tmp_path):
    tr = _trainer(tmp_path, doc_loss_weight=0.02, doc_loss_ramp_steps=100)
    assert tr.doc_loss_lambda(0) == 0.0
    assert tr.doc_loss_lambda(50) == pytest.approx(0.01)
    assert tr.doc_loss_lambda(100) == pytest.approx(0.02)
    assert tr.doc_loss_lambda(5000) == pytest.approx(0.02)
    assert tr.doc_loss_lambda() == 0.0  # self.step = the step about to run
    tr0 = _trainer(tmp_path / "r0", doc_loss_weight=0.02, doc_loss_ramp_steps=0)
    assert tr0.doc_loss_lambda(0) == pytest.approx(0.02)
    row = tr.train_step()
    assert row["doc_weight"] == 0.0  # step 0 of the ramp


# ---- config ---------------------------------------------------------------------
def test_pkm_doc_experiment_composes_with_the_fixed_values():
    cfg = compose(["experiment=pkm_doc", "seed=0", "runtime=mac"])
    tc = to_train_config(cfg)
    assert tc.name == "pkm_doc"
    t = tc.train
    assert t.doc_loss_weight == 0.01
    assert t.doc_loss_ramp_steps == 1000
    assert t.doc_loss_temperature == 0.5
    assert t.doc_loss_min_piece_tokens == 32
    assert t.doc_loss_layer is None and t.doc_loss_eot_id == 50256
    assert list(cfg.eval.steps) == [
        0,
        247,
        504,
        998,
        1500,
        1996,
        3498,
        4999,
        7004,
        9156,
    ]
    # everything else is experiment=pkm
    base = compose(["experiment=pkm", "seed=0", "runtime=mac"])
    b = to_train_config(base)
    assert tc.model == b.model and tc.data == b.data
    for k, v in vars(b.train).items():
        if not k.startswith("doc_loss_"):
            assert getattr(t, k) == v, k
    assert b.train.doc_loss_weight == 0.0  # pkm itself stays off


def test_misspelled_doc_key_fails_at_compose():
    with pytest.raises(Exception, match="doc_loss_wieght"):
        compose(["experiment=pkm_doc", "train.doc_loss_wieght=1"])


@pytest.mark.parametrize(
    "over, model_over, match",
    [
        ({}, {"memory_layers": [], "memory_kind": "pkm"}, "needs a memory layer"),
        ({}, {"memory_layers": [0, 2]}, "several memory layers"),
        ({"doc_loss_layer": 0}, {}, "not a memory layer"),
        ({"doc_loss_temperature": 0.0}, {}, "temperature"),
        ({"doc_loss_min_piece_tokens": 1}, {}, "min_piece_tokens"),
        ({"doc_loss_weight": -1.0}, {}, "doc_loss_weight"),
    ],
)
def test_trainer_refuses_bad_doc_loss_settings(tmp_path, over, model_over, match):
    d = _cfg_dict(tmp_path, doc_loss_weight=0.1)
    d["train"].update(over)
    d["model"].update(model_over)
    if not d["model"]["memory_layers"]:
        d["model"].pop("memory", None)
    with pytest.raises(ValueError, match=match):
        _trainer(tmp_path, d)


def test_trainer_refuses_doc_loss_with_compile(tmp_path):
    d = _cfg_dict(tmp_path, doc_loss_weight=0.1)
    d["runtime"]["compile"] = True
    with pytest.raises(ValueError, match="compile"):
        _trainer(tmp_path, d)


# ---- log columns ----------------------------------------------------------------
def test_new_columns_are_logged():
    for c in DOC_COLS:
        assert c in TRAIN_FIELDS and c in TRAIN_KEYS
    off = train_payload({"step": 1, "tokens_seen": 4, "loss": 2.0, "doc_gap": ""})
    assert "train/doc_gap" not in off
    on = train_payload({"step": 1, "tokens_seen": 4, "doc_gap": 0.25})
    assert on["train/doc_gap"] == 0.25


def test_resumed_log_with_the_old_header_keeps_it(tmp_path):
    old = [f for f in TRAIN_FIELDS if f not in DOC_COLS]
    path = tmp_path / "train_log.csv"
    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=old)
        w.writeheader()
        w.writerow({k: 1 for k in old})
    row = {k: 2 for k in TRAIN_FIELDS}
    FilesSink(tmp_path, "train_log.csv").train(row)
    rows = list(csv.reader(open(path)))
    assert rows[0] == old
    assert len(rows) == 3 and all(len(r) == len(old) for r in rows)
    # a fresh log gets the new header
    (tmp_path / "new").mkdir()
    FilesSink(tmp_path / "new", "train_log.csv").train(row)
    assert next(csv.reader(open(tmp_path / "new" / "train_log.csv"))) == TRAIN_FIELDS


# ---- resume ---------------------------------------------------------------------
def test_resume_with_the_loss_on_matches_a_straight_run(tmp_path):
    """30 steps straight vs 15 + save + resume in a fresh process + 15, with the
    doc loss on and the resume in the middle of the lambda ramp."""
    worker = ROOT / "tests" / "_resume_worker.py"
    doc = dict(
        steps=30,
        grad_accum_steps=1,
        doc_loss_weight=0.5,
        doc_loss_ramp_steps=20,
        doc_loss_eot_id=EOT,
        doc_loss_min_piece_tokens=8,
    )

    def yaml_for(name):
        d = _cfg_dict(tmp_path / name, **doc)
        p = tmp_path / f"{name}.yaml"
        tmp_path.mkdir(exist_ok=True)
        p.write_text(yaml.safe_dump(d))
        return p

    def run(*args):
        r = subprocess.run(
            [sys.executable, str(worker), *map(str, args)],
            capture_output=True,
            text=True,
            cwd=str(ROOT),
        )
        assert r.returncode == 0, f"worker failed:\n{r.stdout}\n{r.stderr}"
        return json.loads(Path(args[1]).read_text())

    a = run(yaml_for("straight"), tmp_path / "a.json", "--steps", 30)
    split = yaml_for("split")
    ck = tmp_path / "half.pt"
    run(split, tmp_path / "b1.json", "--steps", 15, "--save", ck)
    b = run(split, tmp_path / "b2.json", "--steps", 15, "--resume", ck)
    assert b["start_step"] == 15 and b["final_step"] == 30
    for x, y in zip(a["losses_tail"], b["losses_tail"]):
        assert abs(x - y) < 1e-4, (a["losses_tail"], b["losses_tail"])
    assert abs(a["param_checksum"] - b["param_checksum"]) < 1e-3


# ---- smoke: the loss does what it says ------------------------------------------
class TopicDocs:
    """Documents of 63 tokens + EOT; each document draws its tokens from its own
    8-token "topic", so the two halves of a document look alike. A window starts at
    a random offset in the stream, so most rows hold two pieces."""

    def __init__(self, seq_len=64, doc_len=63, seed=0):
        self.seq_len, self.doc_len, self.seed = seq_len, doc_len, seed

    def get_batch(self, step, batch_size, micro=0, device=None):
        g = torch.Generator().manual_seed(self.seed * 1_000_003 + step * 101 + micro)
        rows = []
        for _ in range(batch_size):
            docs = []
            for _ in range(3):
                topic = torch.randperm(EOT, generator=g)[:8]
                body = topic[torch.randint(0, 8, (self.doc_len,), generator=g)]
                docs += [body, torch.tensor([EOT])]
            stream = torch.cat(docs)
            off = int(torch.randint(0, self.doc_len + 1, (1,), generator=g))
            rows.append(stream[off : off + self.seq_len + 1])
        buf = torch.stack(rows)
        x, y = buf[:, :-1], buf[:, 1:]
        if device is not None:
            x, y = x.to(device), y.to(device)
        return x, y


def test_smoke_the_gap_grows(tmp_path):
    tr = _trainer(
        tmp_path,
        dataset=TopicDocs(),
        steps=60,
        micro_batch_size=8,
        grad_accum_steps=1,
        doc_loss_weight=1.0,
        doc_loss_ramp_steps=0,
        doc_loss_eot_id=EOT,
        doc_loss_min_piece_tokens=8,
    )
    hist = tr.train(progress=False)
    assert len(hist) == 60
    for h in hist:
        assert math.isfinite(h["loss"]) and math.isfinite(h["doc_loss"])
        assert h["doc_halves"] >= 4
    first = sum(h["doc_gap"] for h in hist[:10]) / 10
    last = sum(h["doc_gap"] for h in hist[-10:]) / 10
    assert last > first, (first, last)
