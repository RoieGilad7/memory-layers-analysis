"""Runtimes and precision (CUDA mocked), the last.pt timer, data.root, the notebook."""

import json
import math
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
import torch

from conftest import make_model
from memlayers import devices
from memlayers.config import compose, to_train_config
from memlayers.devices import pick_device, resolve_precision
from memlayers.run import launch, read_status
from memlayers.train import Trainer

ROOT = Path(__file__).resolve().parent.parent
FAKE = ["experiment=smoke", "data=fake", "model=tiny_pkm", "runtime=cpu", "eval=off"]


# ---------------------------------------------------------- device, precision
@pytest.fixture
def mock_cuda(monkeypatch):
    def set_gpu(capability, available=True, mps=False):
        monkeypatch.setattr(torch.cuda, "is_available", lambda: available)
        monkeypatch.setattr(torch.cuda, "get_device_capability", lambda *a: capability)
        monkeypatch.setattr(torch.backends.mps, "is_available", lambda: mps)

    return set_gpu


def test_capability_8_gets_bf16(mock_cuda):
    mock_cuda((8, 0))
    p = resolve_precision(torch.device("cuda"), "auto")
    assert p["precision"] == "bf16" and p["dtype"] == torch.bfloat16 and not p["scaler"]
    assert pick_device("auto").type == "cuda"


def test_capability_7_5_gets_fp16_with_a_scaler(mock_cuda):
    mock_cuda((7, 5))
    p = resolve_precision(torch.device("cuda"), "auto")
    assert p["precision"] == "fp16" and p["dtype"] == torch.float16 and p["scaler"]
    with pytest.raises(ValueError, match="compute capability 8.0"):
        resolve_precision(torch.device("cuda"), "bf16")


def test_no_cuda_falls_back_to_mps_then_cpu(mock_cuda):
    mock_cuda((0, 0), available=False, mps=True)
    assert pick_device("auto").type == "mps"
    assert resolve_precision(torch.device("mps"), "auto")["precision"] == "fp32"
    mock_cuda((0, 0), available=False, mps=False)
    assert pick_device("auto").type == "cpu"
    assert resolve_precision(torch.device("cpu"), "auto")["precision"] == "fp32"


@pytest.mark.parametrize(
    "runtime, device, precision",
    [
        ("auto", "auto", "auto"),
        ("mac", "mps", "fp32"),
        ("cpu", "cpu", "fp32"),
        ("cuda", "cuda", "auto"),
        ("colab", "cuda", "auto"),
    ],
)
def test_each_runtime_config(runtime, device, precision):
    cfg = compose(["experiment=pkm", f"runtime={runtime}"])
    rt = to_train_config(cfg).runtime
    assert (rt.device, rt.precision, rt.compile) == (device, precision, False)
    assert rt.ckpt_minutes == (15 if runtime == "colab" else 20)
    if runtime == "colab":
        assert cfg.data.root == "/content/drive/MyDrive/memlayers/data"
        assert cfg.logging.mode == "offline"


def test_an_unknown_precision_is_refused():
    with pytest.raises(ValueError, match="auto\\|fp32\\|bf16\\|fp16"):
        resolve_precision(torch.device("cpu"), "fp8")


# --------------------------------------------- memory layer stays in fp32
@pytest.mark.parametrize("dtype", [torch.bfloat16, torch.float16])
def test_pkm_topk_under_autocast_equals_fp32(dtype):
    """On a fixed input to the memory layer, autocast changes no slot choice:
    the query projection, scores, top-k and softmax all run in fp32. (Across a
    whole model the layer's INPUT differs under autocast, since earlier layers
    run in half precision -- that is mixed precision, not a scoring change.)"""
    mem = make_model("pkm").memory_layers[1].eval()
    # the same values on both sides: a half-precision activation, as an
    # autocast forward would hand the layer
    x = (torch.randn(4, 64, 64, generator=torch.Generator().manual_seed(0)) * 3).to(
        dtype
    )
    mem.set_read_logging(True)
    with torch.no_grad():
        mem(x.float())
        want = mem.last_read()
        with torch.autocast("cpu", dtype=dtype):
            out = mem(x)
        got = mem.last_read()
    assert torch.equal(got.indices, want.indices)
    assert torch.equal(got.weights, want.weights)
    assert got.weights.dtype == torch.float32 and out.dtype == torch.float32


def test_the_memory_output_is_fp32_under_autocast():
    mem = make_model("pkm").memory_layers[1]
    x = torch.randn(2, 8, 64)
    with torch.autocast("cpu", dtype=torch.bfloat16):
        assert mem(x.bfloat16()).dtype == torch.float32


# ----------------------------------------------------------------- training
@pytest.mark.parametrize("precision", ["fp16", "bf16"])
def test_mixed_precision_training_steps_are_finite(tmp_path, precision):
    tc = to_train_config(
        compose([*FAKE, f"out_root={tmp_path}", f"runtime.precision={precision}"])
    )
    tr = Trainer(tc)
    assert tr.prec["precision"] == precision
    assert (tr.scaler is not None) == (precision == "fp16")
    hist = tr.train(steps=6, progress=False)
    assert all(math.isfinite(r["loss"]) for r in hist)
    assert all(p.dtype == torch.float32 for p in tr.model.parameters())  # fp32 masters
    ck = torch.load(tr.save_checkpoint(), weights_only=False)
    assert ck["precision"] == precision and (ck["scaler"] is not None) == (
        precision == "fp16"
    )
    if precision == "fp16":
        assert tr.scaler.get_scale() > 0
    assert tr.meta_dict()["precision"] == precision


def test_the_timer_writes_last_pt_and_a_resume_continues(tmp_path):
    over = [
        *FAKE,
        "train.steps=6",
        "train.ckpt_every=0",
        "train.log_every=1",
        "runtime.ckpt_minutes=0.000001",
        f"out_root={tmp_path}",
    ]
    cmd = [sys.executable, "-m", "memlayers.run", *over]
    env = {**os.environ, "MEMLAYERS_TEST_HALT": "3:exit"}
    r = subprocess.run(cmd, cwd=ROOT, env=env, capture_output=True, text=True)
    assert r.returncode == 137, r.stderr  # killed right after the timer's last.pt
    run = tmp_path / "smoke-s0"
    assert torch.load(run / "checkpoints/last.pt", weights_only=False)["step"] == 3
    env.pop("MEMLAYERS_TEST_HALT")
    r = subprocess.run(cmd, cwd=ROOT, env=env, capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    assert "resumed from" in r.stdout and "at step 3" in r.stdout
    steps = [
        ln.split(",")[0] for ln in (run / "train_log.csv").read_text().splitlines()[1:]
    ]
    assert steps == ["1", "2", "3", "4", "5", "6"]
    assert read_status(run)["state"] == "done"


def test_meta_records_precision_and_device(tmp_path):
    run = launch(compose([*FAKE, "train.steps=2", f"out_root={tmp_path}"]))
    meta = json.loads((run / "meta.json").read_text())
    assert (
        meta["precision"] == "fp32"
        and meta["device"] == "cpu"
        and meta["gpu_name"] is None
    )


def test_a_device_change_on_resume_is_recorded_and_flagged(tmp_path):
    from memlayers.compare import load_runs

    over = [*FAKE, "train.steps=4", f"out_root={tmp_path}"]
    run = launch(compose(over))
    meta = json.loads((run / "meta.json").read_text())
    meta["device"], meta["gpu_name"] = "cuda", "Tesla T4"  # as if it started on a T4
    (run / "meta.json").write_text(json.dumps(meta))
    st = read_status(run)
    st["state"] = "failed"
    (run / "status.json").write_text(json.dumps(st))
    launch(compose([*over, "train.steps=6"]))
    meta = json.loads((run / "meta.json").read_text())
    (ch,) = meta["device_changes"]
    assert ch["from"]["gpu_name"] == "Tesla T4" and ch["to"]["device"] == "cpu"
    _, _, warnings = load_runs([tmp_path], include_unfinished=True)
    assert any("changed device" in w for w in warnings)


# ------------------------------------------------------------------ data.root
def test_a_data_root_elsewhere_is_found_and_verified(tmp_path):
    """The committed 1% build copied to another folder, read through
    data.root (the way Colab reads the bundle from Drive)."""
    root = tmp_path / "drive_data"
    shutil.copytree(ROOT / "data" / "v1_sample", root / "v1_small")
    over = [
        "experiment=smoke",
        "data=sample",
        "data.bundle=null",
        f"data.root={root}",
        "runtime=cpu",
        "eval=off",
        "train.steps=2",
        f"out_root={tmp_path / 'runs'}",
    ]
    run = launch(compose(over))
    meta = json.loads((run / "meta.json").read_text())
    assert meta["data"]["bin_path"].startswith(str(root))
    assert meta["data"]["verified"] is True
    from data.fetch import main as fetch_main

    assert (
        fetch_main(
            ["--version", "v1", "--small", "--data-root", str(root), "--verify-only"]
        )
        == 0
    )
    # a changed byte is refused before step 0
    p = root / "v1_small" / "tokens" / "train.bin"
    b = bytearray(p.read_bytes())
    b[100] ^= 0x55
    p.write_bytes(bytes(b))
    with pytest.raises(RuntimeError, match="failed verification"):
        launch(compose([*over, "seed=1"]))


# ------------------------------------------------------------------ notebook
def test_the_colab_notebook_is_valid_with_cleared_outputs():
    nb = json.loads((ROOT / "notebooks" / "colab_run.ipynb").read_text())
    assert nb["nbformat"] == 4 and isinstance(nb["cells"], list) and nb["cells"]
    for c in nb["cells"]:
        assert c["cell_type"] in ("markdown", "code")
        assert isinstance(c["source"], (list, str))
        if c["cell_type"] == "code":
            assert c["outputs"] == [] and c["execution_count"] is None
    src = "".join("".join(c["source"]) for c in nb["cells"])
    for must in (
        "drive.mount",
        "REPO_COMMIT",
        "EXPERIMENT",
        "SEED",
        "runtime=colab",
        "data.fetch",
        "memlayers.compare",
        "userdata.get",
    ):
        assert must in src, must
    assert "WANDB_API_KEY =" not in src  # no key in the notebook
    try:
        import nbformat
    except ImportError:
        return
    nbformat.validate(nbformat.reads(json.dumps(nb), as_version=4))


def test_a_run_dir_saved_before_the_data_root_change_still_loads(tmp_path):
    """config.yaml files written before training prompt 5 carry data.root:
    null (or the old sample re-root); post-hoc tools must still read them."""
    import yaml

    from memlayers.evaluate import load_run_config

    run = launch(compose([*FAKE, "train.steps=1", f"out_root={tmp_path}"]))
    cfg = yaml.safe_load((run / "config.yaml").read_text())
    cfg["data"].pop("bundle")
    cfg["data"]["root"] = None
    (run / "config.yaml").write_text(yaml.safe_dump(cfg))
    assert load_run_config(run).data.root == "data"
    cfg["data"].update(small=True, root=str(ROOT / "data" / "v1_sample"))
    (run / "config.yaml").write_text(yaml.safe_dump(cfg))
    loaded = load_run_config(run).data
    assert loaded.bundle == str(ROOT / "data" / "v1_sample") and loaded.root == "data"
    # an old Colab path that does not exist on this machine still converts
    cfg["data"].update(small=True, root="/content/drive/MyDrive/x/v1_sample")
    (run / "config.yaml").write_text(yaml.safe_dump(cfg))
    assert load_run_config(run).data.bundle == "/content/drive/MyDrive/x/v1_sample"


def test_colab_resumes_across_hostnames():
    """A Colab reconnect is a new VM: its run says 'running on another host'."""
    assert compose(["experiment=pkm", "runtime=colab"]).resume_foreign is True
    for rt in ("auto", "mac", "cpu", "cuda"):
        assert compose(["experiment=pkm", f"runtime={rt}"]).resume_foreign is False


def test_a_rewrite_of_meta_keeps_the_resume_records(tmp_path):
    tc = to_train_config(compose([*FAKE, f"out_root={tmp_path}"]))
    tr = Trainer(tc)
    tr.write_meta()
    p = tr.out_dir / "meta.json"
    meta = json.loads(p.read_text())
    meta["resumes"] = [{"at_step": 0, "host": "h"}]
    meta["device_changes"] = [{"at_step": 0}]
    p.write_text(json.dumps(meta))
    tr.write_meta()  # e.g. a restart from step 0
    again = json.loads(p.read_text())
    assert again["resumes"] == [{"at_step": 0, "host": "h"}]
    assert again["device_changes"] == [{"at_step": 0}]
