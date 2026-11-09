"""memlayers.runlog: files first, fenced sinks, the W&B mirror, wandb_sync."""

import csv
import json
from pathlib import Path

import pytest

import memlayers.runlog.wandb_sink as wandb_sink
from _eval_fixtures import make_mini_bundle, run_overrides
from _fake_wandb import FakeWandb
from memlayers.config import compose
from memlayers.run import launch, read_status
from memlayers.runlog import FilesSink, RunLogger, Sink
from memlayers.wandb_sync import sync_run

FAKE_DATA = [
    "experiment=smoke",
    "data=fake",
    "model=tiny_pkm",
    "runtime=cpu",
    "train.steps=8",
    "train.ckpt_every=4",
    "train.log_every=1",
]


@pytest.fixture(scope="module")
def bundle(tmp_path_factory):
    return make_mini_bundle(tmp_path_factory.mktemp("bundle"))


@pytest.fixture
def fake(monkeypatch):
    fw = FakeWandb()
    monkeypatch.setattr(wandb_sink, "WANDB_MODULE", fw)
    return fw


def _meta(run_dir):
    return json.loads((Path(run_dir) / "meta.json").read_text())


def _rows(path):
    with open(path, newline="") as fh:
        return list(csv.DictReader(fh))


# ------------------------------------------------------------------ RunLogger
class _Checking(Sink):
    """Asserts, on every call, that the run-dir file is already written."""

    name = "checking"

    def __init__(self, run_dir):
        self.run_dir, self.calls = Path(run_dir), []

    def train(self, row):
        assert _rows(self.run_dir / "train_log.csv")[-1]["step"] == str(row["step"])
        self.calls.append("train")

    def eval(self, rows):
        assert len(_rows(self.run_dir / "evals.csv")) >= len(rows)
        self.calls.append("eval")

    def final(self, fm):
        assert json.loads((self.run_dir / "final_metrics.json").read_text()) == fm
        self.calls.append("final")

    def finish(self, state, step, error=None):
        assert read_status(self.run_dir)["state"] == state
        self.calls.append("finish")


def _eval_row(step=0):
    return dict(
        step=step,
        tokens_seen=0,
        stage="during",
        metric="m",
        metric_id="Q0",
        key="k",
        value=1.0,
    )


def test_files_are_written_before_any_sink_is_called(tmp_path):
    chk = _Checking(tmp_path)
    log = RunLogger(FilesSink(tmp_path), [chk])
    log.log_train({"step": 1, "loss": 2.0, "tokens_seen": 10})
    log.log_eval([_eval_row()])
    log.log_final({"metrics": {"m/k": 1.0}, "step": 1, "tokens_seen": 10})
    log.finish("done", 1)
    assert chk.calls == ["train", "eval", "final", "finish"]


class _Raising(Sink):
    name = "broken"

    def __init__(self):
        self.n = 0

    def train(self, row):
        self.n += 1
        raise RuntimeError("sink exploded")


def test_a_raising_sink_warns_once_and_is_disabled(tmp_path, capsys):
    bad = _Raising()
    log = RunLogger(FilesSink(tmp_path), [bad])
    for s in range(1, 4):
        log.log_train({"step": s, "loss": 1.0, "tokens_seen": s})
    assert bad.n == 1 and log.sinks == []
    assert "sink exploded" in log.disabled["broken"]
    assert capsys.readouterr().err.count("WARNING: the broken sink failed") == 1
    assert len(_rows(tmp_path / "train_log.csv")) == 3  # the files kept going


def test_a_wandb_outage_never_stops_a_run(tmp_path, monkeypatch, capsys):
    fw = FakeWandb(fail_on_log=True)
    monkeypatch.setattr(wandb_sink, "WANDB_MODULE", fw)
    run_dir = launch(compose([*FAKE_DATA, f"out_root={tmp_path}", "logging=wandb"]))
    st = read_status(run_dir)
    assert st["state"] == "done" and st["step"] == 8
    assert capsys.readouterr().err.count("WARNING: the wandb sink failed") == 1
    assert len(_rows(run_dir / "train_log.csv")) == 8
    assert sum(len(r.logged) for r in fw.runs) == 0


# ---------------------------------------------------------------- WandbSink
def test_the_wandb_mirror_sends_the_specified_keys(bundle, tmp_path, fake):
    run_dir = launch(compose([*run_overrides(bundle[0], tmp_path), "logging=wandb"]))
    meta = _meta(run_dir)
    assert fake.generated == [meta["wandb_id"]]  # made once, stored in meta.json
    (run,) = fake.runs
    kw = run.kw
    assert kw["id"] == meta["wandb_id"] and kw["resume"] == "allow"
    assert (
        kw["project"] == "memlayers" and kw["entity"] is None and kw["mode"] == "online"
    )
    assert (
        kw["group"] == "smoke"
        and kw["name"] == "smoke-s0"
        and kw["job_type"] == "train"
    )
    assert [t.split(":")[0] for t in kw["tags"]] == [
        "data",
        "git",
        "device",
        "precision",
    ]
    assert (
        "data:v1" in kw["tags"]
        and "device:cpu" in kw["tags"]
        and "precision:fp32" in kw["tags"]
    )
    assert kw["config"]["run_id"] == "smoke-s0" and kw["config"]["train"]["steps"] == 10
    assert Path(kw["dir"]).name == ".wandb" and Path(kw["dir"]).parent == tmp_path

    train = [d for d in run.logged if "train/loss" in d]
    assert [d["step"] for d in train] == list(range(1, 11))
    assert set(train[0]) >= {
        "tokens_seen",
        "step",
        "train/loss",
        "train/lr",
        "train/grad_norm",
    }
    evals = [d for d in run.logged if "train/loss" not in d]
    assert [d["step"] for d in evals] == [0, 5, 10]
    assert "heldout_quality/loss/pile_avg" in evals[0]
    assert "slot_usage/coverage/layer1" in evals[1]
    assert "final/fact_recall/top1/frequent/test" in evals[2]
    assert not any(
        k.startswith("heldout_quality/") for k in evals[2]
    )  # final is prefixed
    fm = json.loads((run_dir / "final_metrics.json").read_text())["metrics"]
    assert all(run.summary[k] == v for k, v in fm.items())
    assert sorted(run.saved) == [
        "final_metrics.json",
        "meta.json",
        "training_check.json",
    ]
    assert run.finished == 0
    assert (run_dir / "wandb_sync.json").exists()


def test_a_resume_reuses_the_id_and_force_gets_a_new_one(tmp_path, fake):
    over = [*FAKE_DATA, f"out_root={tmp_path}", "logging=wandb"]
    run_dir = launch(compose(over))
    first = _meta(run_dir)["wandb_id"]
    st = read_status(run_dir)
    st["state"] = "failed"
    (run_dir / "status.json").write_text(json.dumps(st))
    launch(compose([*over, "train.steps=12"]))
    assert fake.runs[-1].kw["id"] == first and _meta(run_dir)["wandb_id"] == first
    assert len(fake.generated) == 1
    resumed_train = [d["step"] for d in fake.runs[-1].logged if "train/loss" in d]
    assert resumed_train == [9, 10, 11, 12]  # nothing sent twice
    launch(compose([*over, "train.steps=12", "force=true"]))
    new = _meta(run_dir)["wandb_id"]
    assert new != first and fake.runs[-1].kw["id"] == new
    assert _meta(tmp_path / "smoke-s0.old-1")["wandb_id"] == first


def test_mode_disabled_makes_no_wandb_calls(tmp_path, fake):
    run_dir = launch(
        compose(
            [
                *FAKE_DATA,
                f"out_root={tmp_path}",
                "logging=wandb",
                "logging.mode=disabled",
            ]
        )
    )
    assert fake.runs == [] and fake.generated == []
    assert "wandb_id" not in _meta(run_dir)
    assert read_status(run_dir)["state"] == "done"


def test_logging_files_makes_no_wandb_calls(tmp_path, fake):
    launch(compose([*FAKE_DATA, f"out_root={tmp_path}"]))
    assert fake.runs == [] and fake.generated == []


# ---------------------------------------------------------------- wandb_sync
def test_wandb_sync_replays_once_and_a_second_sync_sends_nothing(
    bundle, tmp_path, fake
):
    run_dir = launch(compose(run_overrides(bundle[0], tmp_path)))  # logging=files
    assert "wandb_id" not in _meta(run_dir)
    sent = sync_run(run_dir, module=fake)
    wid = _meta(run_dir)["wandb_id"]
    assert fake.runs[0].kw["id"] == wid and fake.runs[0].kw["resume"] == "allow"
    train_rows = _rows(run_dir / "train_log.csv")
    eval_rows = _rows(run_dir / "evals.csv")
    points = {(r["step"], r["stage"]) for r in eval_rows}
    logged = fake.logged
    assert [d["step"] for d in logged if "train/loss" in d] == [
        int(r["step"]) for r in train_rows
    ]
    evs = [d for d in logged if "train/loss" not in d]
    assert len(evs) == len(points) == 3
    n_values = sum(len([k for k in d if k not in ("step", "tokens_seen")]) for d in evs)
    assert n_values == len(eval_rows)  # every eval row once
    assert sent == {"train": len(train_rows), "eval_points": 3, "final": 1, "files": 3}

    before = len(fake.logged)
    again = sync_run(run_dir, module=fake)
    assert len(fake.logged) == before
    assert again == {"train": 0, "eval_points": 0, "final": 0, "files": 0}
    assert _meta(run_dir)["wandb_id"] == wid  # same id, no duplicate run


def test_wandb_sync_after_an_online_run_sends_nothing(bundle, tmp_path, fake):
    run_dir = launch(compose([*run_overrides(bundle[0], tmp_path), "logging=wandb"]))
    n = len(fake.logged)
    assert sync_run(run_dir, module=fake) == {
        "train": 0,
        "eval_points": 0,
        "final": 0,
        "files": 0,
    }
    assert len(fake.logged) == n


def test_wandb_sync_uploads_an_offline_run(bundle, tmp_path, fake):
    run_dir = launch(
        compose(
            [
                *run_overrides(bundle[0], tmp_path),
                "logging=wandb",
                "logging.mode=offline",
            ]
        )
    )
    assert fake.runs[0].kw["mode"] == "offline"
    n = len(fake.logged)
    sent = sync_run(
        run_dir, module=fake
    )  # online: offline rows never reached the server
    assert sent["train"] == 10 and sent["eval_points"] == 3
    assert (
        fake.runs[-1].kw["mode"] == "online"
        and fake.runs[-1].kw["id"] == fake.runs[0].kw["id"]
    )
    assert len(fake.logged) == 2 * n


def test_the_id_falls_back_to_wandbs_own_generator_when_util_lacks_it():
    """wandb 0.31 moved generate_id out of wandb.util."""
    from types import SimpleNamespace

    from memlayers.runlog import generate_wandb_id

    assert generate_wandb_id(FakeWandb()) == "fakeid000"
    pytest.importorskip("wandb")
    wid = generate_wandb_id(SimpleNamespace(util=SimpleNamespace()))
    assert isinstance(wid, str) and len(wid) == 8
