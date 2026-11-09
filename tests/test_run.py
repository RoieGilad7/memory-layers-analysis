"""memlayers.run: the run dir lifecycle, re-runs, resume and the run lock."""

import csv
import hashlib
import json
import os
import signal
import socket
import subprocess
import sys
import time
from pathlib import Path

import pytest
import torch
import yaml

from memlayers.config import compose, to_train_config
from memlayers.run import RunRefused, launch, read_status
from memlayers.train import RunLayout, Trainer

from test_train import real_bundle  # noqa: F401  (fixture)

ROOT = Path(__file__).resolve().parent.parent
# the smoke experiment on fake data and the vocab-257 tiny model: the run-layer
# tests exercise files and states, not metrics, so they skip the 1% sample
SMOKE = [
    "experiment=smoke",
    "data=fake",
    "model=tiny_pkm",
    "runtime=cpu",
    "train.steps=20",
    "train.ckpt_every=5",
]


def _cfg(tmp_path, *extra):
    return compose([*SMOKE, f"out_root={tmp_path}", *extra])


def _checksums(d: Path) -> dict:
    return {
        str(p.relative_to(d)): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted(d.rglob("*"))
        if p.is_file()
    }


def _mtimes(d: Path) -> dict:
    return {str(p.relative_to(d)): p.stat().st_mtime_ns for p in d.rglob("*")}


def _losses(run_dir: Path):
    with open(run_dir / "train_log.csv", newline="") as fh:
        return [(int(r["step"]), r["loss"]) for r in csv.DictReader(fh)]


def _cli(tmp_path, *extra, env=None, wait=True):
    cmd = [
        sys.executable,
        "-m",
        "memlayers.run",
        *SMOKE,
        f"out_root={tmp_path}",
        *extra,
    ]
    e = dict(os.environ)
    e.pop("MEMLAYERS_TEST_HALT", None)
    e.update(env or {})
    if not wait:
        return subprocess.Popen(
            cmd, cwd=str(ROOT), env=e, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
    return subprocess.run(cmd, cwd=str(ROOT), env=e, capture_output=True, text=True)


# ------------------------------------------------------------------ smoke run
def test_smoke_run_writes_the_whole_run_dir(tmp_path):
    run_dir = launch(_cfg(tmp_path), ["experiment=smoke"])
    assert run_dir == tmp_path / "smoke-s0"

    for f in (
        "config.yaml",
        "overrides.yaml",
        "meta.json",
        "status.json",
        "stdout.log",
        "train_log.csv",
        "checkpoints/step_000000.pt",
        "checkpoints/last.pt",
    ):
        assert (run_dir / f).is_file(), f

    cfg = yaml.safe_load((run_dir / "config.yaml").read_text())
    assert cfg["run_id"] == "smoke-s0" and cfg["train"]["steps"] == 20
    assert "${" not in (run_dir / "config.yaml").read_text()  # fully resolved
    assert yaml.safe_load((run_dir / "overrides.yaml").read_text()) == [
        "experiment=smoke"
    ]

    st = json.loads((run_dir / "status.json").read_text())
    assert st["state"] == "done" and st["step"] == 20 and st["error"] is None
    assert st["host"] == socket.gethostname() and st["pid"] == os.getpid()
    assert set(st) == {"state", "step", "updated_at", "error", "host", "pid"}

    meta = json.loads((run_dir / "meta.json").read_text())
    assert len(meta["git"]["commit"]) == 40
    assert isinstance(meta["git"]["dirty"], bool)
    assert isinstance(meta["git"]["dirty_files"], list)
    assert meta["run_id"] == "smoke-s0" and meta["experiment"] == "smoke"
    assert meta["flops_per_token"]["total"] == 332_960
    assert len(meta["flops_per_token"]["per_layer"]) == 3
    assert {"python", "torch", "hydra", "omegaconf"} <= set(meta["versions"])
    assert meta["host"] == socket.gethostname()
    assert "param_counts" in meta and "optimizer_groups" in meta  # write_meta's

    assert [s for s, _ in _losses(run_dir)] == list(range(1, 21))
    assert "[run] smoke-s0 done at step 20" in (run_dir / "stdout.log").read_text()
    init = torch.load(run_dir / "checkpoints/step_000000.pt", weights_only=False)
    last = torch.load(run_dir / "checkpoints/last.pt", weights_only=False)
    assert init["step"] == 0 and last["step"] == 20

    assert not (run_dir / ".hydra").exists()
    assert not list(run_dir.rglob(".hydra*"))
    assert not (run_dir / "log.csv").exists() and not (run_dir / "ckpt.pt").exists()


def test_the_cli_writes_no_hydra_dir_into_the_run_dir(tmp_path):
    r = _cli(tmp_path)
    assert r.returncode == 0, r.stderr
    run_dir = tmp_path / "smoke-s0"
    assert read_status(run_dir)["state"] == "done"
    assert not list(run_dir.rglob(".hydra*"))
    assert yaml.safe_load((run_dir / "overrides.yaml").read_text()) == [
        *SMOKE,
        f"out_root={tmp_path}",
    ]
    # Hydra's own files went to <out_root>/.hydra_tmp, outside every run dir
    assert (tmp_path / ".hydra_tmp").is_dir()


# -------------------------------------------------------------- re-run a done
def test_a_refused_rerun_changes_no_file(tmp_path):
    run_dir = launch(_cfg(tmp_path))
    before, mt = _checksums(run_dir), _mtimes(run_dir)
    with pytest.raises(RunRefused, match="is done"):
        launch(_cfg(tmp_path))
    with pytest.raises(RunRefused, match="is done"):
        launch(_cfg(tmp_path, "train.steps=30"))  # even an allowed change
    assert _checksums(run_dir) == before
    assert _mtimes(run_dir) == mt
    assert not list(tmp_path.glob("smoke-s0.old-*"))


def test_the_cli_refuses_a_done_run_with_exit_code_2(tmp_path):
    assert _cli(tmp_path).returncode == 0
    before = _checksums(tmp_path / "smoke-s0")
    r = _cli(tmp_path)
    assert r.returncode == 2 and "is done" in r.stderr and "force=true" in r.stderr
    assert _checksums(tmp_path / "smoke-s0") == before


def test_force_moves_the_done_run_and_starts_fresh(tmp_path):
    run_dir = launch(_cfg(tmp_path))
    before = _checksums(run_dir)
    launch(_cfg(tmp_path, "force=true"))
    old = tmp_path / "smoke-s0.old-1"
    assert old.is_dir(), "force deleted the old run instead of moving it"
    assert _checksums(old) == before  # byte-identical
    assert read_status(run_dir)["state"] == "done"
    meta = json.loads((run_dir / "meta.json").read_text())
    assert meta["moved_previous_to"] == str(old)
    # a second force picks the next free name
    launch(_cfg(tmp_path, "force=true"))
    assert (tmp_path / "smoke-s0.old-2").is_dir()
    assert _checksums(old) == before


def test_a_foreign_dir_without_status_is_refused(tmp_path):
    d = tmp_path / "smoke-s0"
    d.mkdir()
    (d / "notes.txt").write_text("mine")
    with pytest.raises(RunRefused, match="no status.json"):
        launch(_cfg(tmp_path))
    assert (d / "notes.txt").read_text() == "mine" and len(list(d.iterdir())) == 1


# ----------------------------------------------------------------- resume
def _make_failed(tmp_path, *extra):
    run_dir = launch(_cfg(tmp_path, *extra))
    st = read_status(run_dir)
    st["state"] = "failed"
    (run_dir / "status.json").write_text(json.dumps(st))
    return run_dir


def test_a_resume_with_a_changed_model_key_is_refused(tmp_path):
    run_dir = _make_failed(tmp_path)
    before = _checksums(run_dir)
    with pytest.raises(RunRefused, match="model.n_embd"):
        launch(_cfg(tmp_path, "model.n_embd=32"))
    with pytest.raises(RunRefused, match="train.lr"):
        launch(_cfg(tmp_path, "train.lr=0.5"))
    assert _checksums(run_dir) == before


def test_a_resume_with_a_changed_step_count_is_allowed(tmp_path):
    run_dir = _make_failed(tmp_path)
    launch(_cfg(tmp_path, "train.steps=30", "runtime.device=cpu"))
    st = read_status(run_dir)
    assert st["state"] == "done" and st["step"] == 30
    assert [s for s, _ in _losses(run_dir)] == list(range(1, 31))
    meta = json.loads((run_dir / "meta.json").read_text())
    assert meta["resumes"][0]["at_step"] == 20


def test_resume_false_refuses_a_failed_run(tmp_path):
    run_dir = _make_failed(tmp_path)
    before = _checksums(run_dir)
    with pytest.raises(RunRefused, match="resume=false"):
        launch(_cfg(tmp_path, "resume=false"))
    assert _checksums(run_dir) == before


def test_an_exception_marks_the_run_failed_and_is_reraised(tmp_path, monkeypatch):
    def boom(self):
        raise RuntimeError("injected")

    monkeypatch.setattr(Trainer, "train_step", boom)
    with pytest.raises(RuntimeError, match="injected"):
        launch(_cfg(tmp_path))
    st = read_status(tmp_path / "smoke-s0")
    assert st["state"] == "failed" and "RuntimeError: injected" in st["error"]
    assert "Traceback" in st["error"]


def test_kill_and_resume_matches_an_unbroken_run_exactly(tmp_path):
    """SIGKILL-like death after the step-10 checkpoint, then the same command."""
    whole = _cli(tmp_path / "a")
    assert whole.returncode == 0, whole.stderr
    want = _losses(tmp_path / "a" / "smoke-s0")

    killed = _cli(tmp_path / "b", env={"MEMLAYERS_TEST_HALT": "10:exit"})
    assert killed.returncode == 137, killed.stderr
    run_dir = tmp_path / "b" / "smoke-s0"
    st = read_status(run_dir)
    assert st["state"] == "running" and st["step"] == 10  # the process is gone

    again = _cli(tmp_path / "b")
    assert again.returncode == 0, again.stderr
    assert "resumed from" in again.stdout
    assert read_status(run_dir)["state"] == "done"
    got = _losses(run_dir)
    assert got == want  # every step, the loss string, bit for bit


def test_a_crash_between_checkpoints_does_not_duplicate_log_rows(tmp_path):
    """Steps after the last checkpoint are replayed on resume; their first-time
    rows are dropped so each step appears once."""
    run_dir = _make_failed(tmp_path)
    # pretend the checkpoint is from step 15 while the log ran to 20
    ck = torch.load(run_dir / "checkpoints/last.pt", weights_only=False)
    launch(_cfg(tmp_path / "ref", "train.steps=15"))
    ref = torch.load(
        tmp_path / "ref" / "smoke-s0" / "checkpoints/last.pt", weights_only=False
    )
    torch.save(ref, run_dir / "checkpoints/last.pt")
    assert ck["step"] == 20 and ref["step"] == 15
    launch(_cfg(tmp_path))
    assert [s for s, _ in _losses(run_dir)] == list(range(1, 21))


# -------------------------------------------------------------- the run lock
def _wait_for_step(run_dir: Path, step: int, proc, timeout=60):
    t0 = time.time()
    while time.time() - t0 < timeout:
        st = read_status(run_dir) if (run_dir / "status.json").exists() else None
        if st and st["step"] >= step and st["state"] == "running":
            return st
        if proc.poll() is not None:
            raise AssertionError(f"first run exited early: {proc.stderr.read()}")
        time.sleep(0.1)
    raise AssertionError("first run never reached the checkpoint")


def test_a_second_launch_is_refused_while_the_first_lives(tmp_path):
    first = _cli(tmp_path, env={"MEMLAYERS_TEST_HALT": "10:hang"}, wait=False)
    run_dir = tmp_path / "smoke-s0"
    try:
        st = _wait_for_step(run_dir, 10, first)
        assert st["pid"] == first.pid
        before = _checksums(run_dir)

        second = _cli(tmp_path)
        assert second.returncode == 2
        assert "already running" in second.stderr
        assert _checksums(run_dir) == before
    finally:
        first.send_signal(signal.SIGKILL)
        first.wait()

    third = _cli(tmp_path)  # the same command, after the first was killed
    assert third.returncode == 0, third.stderr
    assert "resumed from" in third.stdout
    st = read_status(run_dir)
    assert st["state"] == "done" and st["step"] == 20


def test_a_running_status_with_a_live_pid_is_refused(tmp_path):
    """The status check on its own, without the flock: a live PID on this host."""
    run_dir = _make_failed(tmp_path)
    sleeper = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(60)"])
    try:
        st = read_status(run_dir)
        st.update(state="running", pid=sleeper.pid, host=socket.gethostname())
        (run_dir / "status.json").write_text(json.dumps(st))
        before = _checksums(run_dir)
        with pytest.raises(RunRefused, match="already running"):
            launch(_cfg(tmp_path))
        with pytest.raises(RunRefused, match="already running"):
            launch(_cfg(tmp_path, "force=true"))
        assert _checksums(run_dir) == before
    finally:
        sleeper.kill()
        sleeper.wait()
    launch(_cfg(tmp_path))  # the PID is gone now: resumable
    assert read_status(run_dir)["state"] == "done"


def test_a_running_status_from_another_host_needs_resume_foreign(tmp_path):
    run_dir = _make_failed(tmp_path)
    st = read_status(run_dir)
    st.update(state="running", host="some-other-laptop", pid=1)
    (run_dir / "status.json").write_text(json.dumps(st))
    before = _checksums(run_dir)
    with pytest.raises(RunRefused, match="resume_foreign"):
        launch(_cfg(tmp_path))
    assert _checksums(run_dir) == before
    launch(_cfg(tmp_path, "resume_foreign=true"))
    assert read_status(run_dir)["state"] == "done"


# ------------------------------------------------ same init, same batches
def _trainer(tmp_path, experiment, bin_path, data_config):
    cfg = compose(
        [
            f"experiment={experiment}",
            "seed=0",
            "runtime=cpu",
            f"out_root={tmp_path}",
            f"data.data_config={data_config}",
            f"data.bin_path={bin_path}",
            "train.micro_batch_size=4",
        ]
    )
    return Trainer(to_train_config(cfg), layout=RunLayout.run())


def test_pkm_randkey_and_dense_share_pkms_batches_and_randkey_its_init(
    tmp_path, real_bundle  # noqa: F811
):
    bin_path, data_config = real_bundle
    pkm = _trainer(tmp_path, "pkm", bin_path, data_config)
    rk = _trainer(tmp_path, "pkm_randkey", bin_path, data_config)
    dense = _trainer(tmp_path, "dense", bin_path, data_config)

    a, b = pkm.model.state_dict(), rk.model.state_dict()
    assert set(a) == set(b)
    for k in a:
        assert a[k].dtype == b[k].dtype and a[k].shape == b[k].shape, k
        assert a[k].numpy().tobytes() == b[k].numpy().tobytes(), k
    mem = rk.model.memory_layers[3]
    assert not any(p.requires_grad for p in mem.key_parameters())

    for step in range(3):
        xa, ya = pkm.data.get_batch(step, 4)
        xb, yb = rk.data.get_batch(step, 4)
        xc, yc = dense.data.get_batch(step, 4)
        assert torch.equal(xa, xb) and torch.equal(ya, yb)
        assert torch.equal(xa, xc) and torch.equal(ya, yc)
    assert pkm.data.position == rk.data.position == dense.data.position == 12


def test_the_saved_init_weights_of_pkm_and_randkey_are_equal(tmp_path):
    """The step_000000.pt files themselves, on the tiny model and fake data."""
    a = launch(_cfg(tmp_path / "a", "train.steps=1"))
    b = launch(_cfg(tmp_path / "b", "train.steps=1", "model.memory.freeze_keys=true"))
    wa = torch.load(a / "checkpoints/step_000000.pt", weights_only=False)["model"]
    wb = torch.load(b / "checkpoints/step_000000.pt", weights_only=False)["model"]
    assert all(torch.equal(wa[k], wb[k]) for k in wa)


# ------------------------------------------------------------ atomic last.pt
def test_a_crash_mid_write_leaves_the_previous_last_pt_loadable(tmp_path, monkeypatch):
    tc = to_train_config(_cfg(tmp_path, "train.ckpt_every=0"))
    tr = Trainer(tc, layout=RunLayout.run())
    tr.train(steps=3, progress=False)
    path = tr.save_checkpoint()
    assert path == tmp_path / "smoke-s0" / "checkpoints" / "last.pt"
    good = path.read_bytes()

    tr.train(steps=2, progress=False)
    real_save = torch.save

    def dying_save(obj, f, *a, **k):
        f.write(b"half a checkpoint")
        raise OSError("disk vanished mid-write")

    monkeypatch.setattr(torch, "save", dying_save)
    with pytest.raises(OSError, match="mid-write"):
        tr.save_checkpoint()
    monkeypatch.setattr(torch, "save", real_save)

    assert path.read_bytes() == good
    assert torch.load(path, weights_only=False)["step"] == 3
    # and no temporary file is left behind
    assert sorted(p.name for p in path.parent.iterdir()) == [
        "last.pt",
        "step_000000.pt",
    ]
