"""Optimizer parameter groups, step-0 weight snapshot, and checkpoint resume."""
import csv
import json
import subprocess
import sys
from pathlib import Path

import pytest
import torch
import yaml

from conftest import make_model
from memlayers.model import GPT, GPTConfig
from memlayers.train import OptimCfg, Trainer, build_optimizer, cosine_warmup, load_config

ROOT = Path(__file__).resolve().parent.parent


def _tiny_cfg_dict(out_dir: str, steps: int = 100, kind: str = "pkm") -> dict:
    model = dict(vocab_size=257, block_size=64, n_layer=3, n_head=4, n_embd=64,
                 dropout=0.0, bias=True, tie_embeddings=True)
    if kind != "dense":
        model["memory_layers"] = [1]
        model["memory_kind"] = kind
        model["memory"] = (dict(num_keys=16, topk=4, heads=2, dim_head=32,
                                query_batchnorm=True) if kind == "pkm"
                           else dict(num_experts=256, topk=4, heads=2, dim_key=32,
                                     non_competing_scores=False))
    return {
        "name": f"test-{kind}",
        "model": model,
        "data": {"kind": "repeat", "chunk_len": 8, "n_distinct": 257, "seed": 7},
        "train": {"steps": steps, "micro_batch_size": 4, "grad_accum_steps": 1,
                  "lr": 1e-3, "lr_memory_values": 4e-3, "weight_decay": 0.1,
                  "warmup_steps": 10, "min_lr_ratio": 0.1, "seed": 99,
                  "log_every": 0, "ckpt_every": 0, "grad_clip": 1.0},
        "runtime": {"device": "cpu", "out_dir": out_dir},
    }


# ----------------------------------------------------------- parameter groups
@pytest.mark.parametrize("kind", ["pkm", "peer"])
def test_memory_values_get_the_higher_learning_rate(kind):
    m = make_model(kind)
    cfg = OptimCfg(lr=2.5e-4, lr_memory_values=1e-3)
    opt = build_optimizer(m, cfg)
    groups = {g["name"]: g for g in opt.param_groups}

    assert "memory_values" in groups, "no memory_values group was created"
    assert groups["memory_values"]["lr"] == pytest.approx(1e-3)
    assert groups["decay"]["lr"] == pytest.approx(2.5e-4)
    assert groups["memory_values"]["lr"] > groups["decay"]["lr"]
    # the value tables, and only those, are in that group
    mem = next(iter(m.memory_layers.values()))
    want = {id(p) for p in mem.value_parameters()}
    got = {id(p) for p in groups["memory_values"]["params"]}
    assert got == want
    # keys live in their own group and default to the backbone LR
    assert {id(p) for p in groups["memory_keys"]["params"]} == \
           {id(p) for p in mem.key_parameters()}
    assert groups["memory_keys"]["lr"] == pytest.approx(2.5e-4)
    # every trainable tensor landed in exactly one group
    assigned = [id(p) for g in opt.param_groups for p in g["params"]]
    assert len(assigned) == len(set(assigned))
    trainable = {id(p) for p in m.parameters() if p.requires_grad}
    assert set(assigned) == trainable


def test_memory_keys_lr_is_configurable():
    m = make_model("pkm")
    opt = build_optimizer(m, OptimCfg(lr=1e-4, lr_memory_values=1e-3,
                                      lr_memory_keys=5e-4))
    groups = {g["name"]: g for g in opt.param_groups}
    assert groups["memory_keys"]["lr"] == pytest.approx(5e-4)


def test_dense_model_has_no_memory_groups():
    opt = build_optimizer(make_model("dense"), OptimCfg())
    names = {g["name"] for g in opt.param_groups}
    assert "memory_values" not in names and "memory_keys" not in names


def test_lr_ratio_is_preserved_through_the_schedule(tmp_path):
    cfg = load_config_from_dict(_tiny_cfg_dict(str(tmp_path / "run"), steps=60), tmp_path)
    tr = Trainer(cfg)
    ratios = []
    for _ in range(12):
        tr.train_step()
        g = {x.get("name"): x["lr"] for x in tr.optimizer.param_groups}
        ratios.append(g["memory_values"] / g["decay"])
    assert max(ratios) - min(ratios) < 1e-9, "schedule broke the value/backbone LR ratio"
    assert ratios[0] == pytest.approx(4.0)


def test_cosine_warmup_shape():
    assert cosine_warmup(0, 10, 100, 0.1) == pytest.approx(0.1)
    assert cosine_warmup(9, 10, 100, 0.1) == pytest.approx(1.0)
    assert cosine_warmup(10, 10, 100, 0.1) == pytest.approx(1.0)
    assert cosine_warmup(99, 10, 100, 0.1) == pytest.approx(0.1, abs=1e-3)
    mid = cosine_warmup(55, 10, 100, 0.1)
    assert 0.1 < mid < 1.0


# ------------------------------------------------------- step-0 weight snapshot
def load_config_from_dict(d: dict, tmp_path: Path):
    p = tmp_path / "cfg.yaml"
    p.write_text(yaml.safe_dump(d))
    return load_config(p)


def test_initial_weights_saved_and_differ_from_trained(tmp_path):
    out = tmp_path / "run"
    cfg = load_config_from_dict(_tiny_cfg_dict(str(out), steps=20), tmp_path)
    tr = Trainer(cfg)
    tr.train(progress=False)

    init_path = out / "init_weights.pt"
    assert init_path.exists(), "step-0 weight snapshot was not written"
    init = torch.load(init_path, map_location="cpu", weights_only=False)
    assert init["step"] == 0
    trained = tr.model.state_dict()
    assert set(init["model"]) == set(trained)

    differing = [k for k, v in init["model"].items()
                 if not torch.equal(v, trained[k].detach().cpu())]
    assert differing, "no weight changed after training"
    # the memory value table in particular must have moved
    assert any("values.weight" in k or "weight_down_embed" in k for k in differing)
    assert (out / "meta.json").exists()
    assert (out / "log.csv").exists() or cfg.train.log_every == 0


# -------------------------------------------------------------- resume
@pytest.mark.parametrize("kind", ["pkm", "peer"])
def test_checkpoint_resume_matches_straight_run(tmp_path, kind):
    """100 steps straight vs 50 + save + reload in a FRESH process + 50 more."""
    worker = ROOT / "tests" / "_resume_worker.py"

    straight_cfg = load_config_from_dict(
        _tiny_cfg_dict(str(tmp_path / "straight"), steps=100, kind=kind), tmp_path)
    straight_yaml = tmp_path / "straight.yaml"
    straight_yaml.write_text(yaml.safe_dump(
        _tiny_cfg_dict(str(tmp_path / "straight"), steps=100, kind=kind)))

    split_yaml = tmp_path / "split.yaml"
    split_yaml.write_text(yaml.safe_dump(
        _tiny_cfg_dict(str(tmp_path / "split"), steps=100, kind=kind)))

    def run(*args):
        r = subprocess.run([sys.executable, str(worker), *map(str, args)],
                           capture_output=True, text=True, cwd=str(ROOT))
        assert r.returncode == 0, f"worker failed:\n{r.stdout}\n{r.stderr}"
        return json.loads(Path(args[1]).read_text())

    a = run(straight_yaml, tmp_path / "a.json", "--steps", 100)
    ckpt = tmp_path / "half.pt"
    b1 = run(split_yaml, tmp_path / "b1.json", "--steps", 50, "--save", ckpt)
    b2 = run(split_yaml, tmp_path / "b2.json", "--steps", 50, "--resume", ckpt)

    assert a["final_step"] == 100 and b2["final_step"] == 100
    assert b2["start_step"] == 50, "step counter did not continue from the checkpoint"
    assert b1["final_step"] == 50

    # the loss at step 100 must match
    assert abs(a["final_loss"] - b2["final_loss"]) < 1e-4, (
        f"resumed loss {b2['final_loss']:.6f} vs straight {a['final_loss']:.6f}")

    # the learning rate must be at the same point on the schedule
    assert a["lr_names"] == b2["lr_names"]
    for lr_a, lr_b in zip(a["lr"], b2["lr"]):
        assert lr_a == pytest.approx(lr_b, rel=1e-9)

    # data order continued: the batch the resumed run read at step 50 is the batch the
    # straight run read at step 50, and both now point at the same next batch
    assert b2["batch_at_start_sum"] != 0
    assert a["next_batch_sum"] == b2["next_batch_sum"]
    assert a["tokens_seen"] == b2["tokens_seen"]


def test_resume_restores_optimizer_state_not_just_weights(tmp_path):
    """A resumed run must carry Adam's moments; otherwise the first post-resume step
    would differ even with identical weights."""
    cfg = load_config_from_dict(_tiny_cfg_dict(str(tmp_path / "r"), steps=20), tmp_path)
    tr = Trainer(cfg)
    tr.train(steps=10, progress=False)
    ckpt = tr.save_checkpoint(tmp_path / "c.pt")

    fresh = Trainer(load_config_from_dict(
        _tiny_cfg_dict(str(tmp_path / "r2"), steps=20), tmp_path))
    fresh.load_checkpoint(ckpt)
    assert fresh.step == 10
    st = fresh.optimizer.state_dict()["state"]
    assert st, "optimizer state was empty after resume"
    any_state = next(iter(st.values()))
    assert "exp_avg" in any_state and int(any_state["step"]) == 10


@pytest.mark.parametrize("kind", ["pkm", "peer"])
def test_slot_usage_is_tracked_without_the_full_read_log(tmp_path, kind):
    """track_slot_usage alone must still produce real counts.

    Regression test: the layers only expose their reads when read logging is enabled
    on them, so a config with track_slot_usage=True but read_logging=False used to
    report every slot as unread.
    """
    d = _tiny_cfg_dict(str(tmp_path / "u"), steps=6, kind=kind)
    d["train"]["track_slot_usage"] = True
    d["train"]["read_logging"] = False
    tr = Trainer(load_config_from_dict(d, tmp_path))
    tr.train(progress=False)

    assert tr.usage is not None
    layer = next(iter(tr.model.memory_layers))
    counts = tr.usage.counts[layer]
    assert int(counts.sum()) > 0, "slot usage counts were all zero"
    mem = tr.model.memory_layers[layer]
    expected = (6 * tr.cfg.train.micro_batch_size * tr.gpt_config.block_size
                * mem.n_heads * mem.topk)
    assert int(counts.sum()) == expected
    st = json.loads((tr.out_dir / "slot_usage.json").read_text())[str(layer)]
    assert st["slots_used"] > 0 and 0 < st["fraction_used"] <= 1
    assert st["kl_from_uniform"] > 0
    # and no full read log was written
    assert not (tr.out_dir / "readlog").exists()


def test_nothing_is_captured_when_both_switches_are_off(tmp_path):
    """The speed baseline must capture nothing at all."""
    d = _tiny_cfg_dict(str(tmp_path / "off"), steps=4, kind="pkm")
    d["train"]["track_slot_usage"] = False
    d["train"]["read_logging"] = False
    tr = Trainer(load_config_from_dict(d, tmp_path))
    tr.train(progress=False)
    assert tr.usage is None and tr.read_writer is None
    mem = next(iter(tr.model.memory_layers.values()))
    assert not mem.read_logging
    assert mem.last_read() is None
    assert not (tr.out_dir / "slot_usage.json").exists()


# --------------------------------------------------------------------- real data
def _real_data_cfg(tmp_path, bin_path, data_config, **over):
    """A tiny training config pointed at a packed .bin."""
    from memlayers.train import DataCfg, OptimCfg, RuntimeCfg, TrainConfig
    cfg = TrainConfig(
        name="real-smoke",
        model=dict(vocab_size=257, block_size=512, n_layer=2, n_head=2,
                   n_embd=32, dropout=0.0, bias=True, tie_embeddings=True),
        data=DataCfg(source="real", version="v1", data_config=str(data_config),
                     bin_path=str(bin_path), seed=4242, **over),
        train=OptimCfg(steps=4, micro_batch_size=2, grad_accum_steps=1,
                       warmup_steps=1, log_every=1, seed=7),
        runtime=RuntimeCfg(device="cpu", out_dir=str(tmp_path / "run")))
    return cfg


@pytest.fixture
def real_bundle(tmp_path):
    """A manifest-verified mini bundle with a packed .bin in it."""
    import numpy as np
    import yaml
    from data import manifest as manifest_mod
    from data.common import DataConfig

    root = tmp_path / "v1"
    (root / "tokens").mkdir(parents=True)
    tokens = (np.arange(512 * 40 + 1) % 257).astype(np.uint16)
    tokens.tofile(root / "tokens" / "train.bin")

    cfg_path = ROOT / "configs" / "data" / "v1.yaml"
    raw = yaml.safe_load(cfg_path.read_text())
    r = str(root)
    raw["paths"] = {"root": r, "raw": f"{r}/raw", "work": f"{r}/_work",
                    "train": f"{r}/train", "heldout_pool": f"{r}/heldout_pool",
                    "heldout": f"{r}/heldout", "reports": f"{r}/reports"}
    raw["small"]["root"] = r
    raw["distribution"]["manifest_dir"] = str(tmp_path / "manifests")
    mini = tmp_path / "data_config.yaml"
    mini.write_text(yaml.safe_dump(raw))
    manifest_mod.run(DataConfig(raw=raw))
    return root / "tokens" / "train.bin", mini


def test_real_data_runs_and_records_its_provenance(tmp_path, real_bundle):
    from memlayers.train import Trainer
    bin_path, data_config = real_bundle
    t = Trainer(_real_data_cfg(tmp_path, bin_path, data_config))
    assert t.data.name == "real"
    prov = t.data_provenance
    assert prov["source"] == "real" and prov["version"] == "v1"
    assert len(prov["manifest_sha256"]) == 64 and prov["verified"] is True
    assert prov["n_sequences"] == 40

    t.train(steps=2, progress=False)
    ck = t.save_checkpoint()
    import torch
    loaded = torch.load(ck, map_location="cpu", weights_only=False)
    assert loaded["data"]["manifest_sha256"] == prov["manifest_sha256"]
    assert loaded["data_state"]["position"] == 4        # 2 steps x batch 2
    rows = list(csv.DictReader(open(t.out_dir / "log.csv")))
    assert rows[0]["data_version"] == "v1"
    assert rows[0]["data_manifest_sha256"] == prov["manifest_sha256"][:16]


def test_real_data_refuses_to_start_on_a_mismatch(tmp_path, real_bundle):
    from memlayers.train import Trainer
    bin_path, data_config = real_bundle
    data = bytearray(bin_path.read_bytes())
    data[9] ^= 0x7F
    bin_path.write_bytes(bytes(data))
    with pytest.raises(RuntimeError, match="failed verification"):
        Trainer(_real_data_cfg(tmp_path, bin_path, data_config))


def test_real_data_resume_continues_the_same_order(tmp_path, real_bundle):
    from memlayers.train import Trainer
    bin_path, data_config = real_bundle

    whole = Trainer(_real_data_cfg(tmp_path / "w", bin_path, data_config))
    whole.train(steps=4, progress=False)
    want = [r["loss"] for r in whole.history]

    part = Trainer(_real_data_cfg(tmp_path / "p", bin_path, data_config))
    part.train(steps=2, progress=False)
    ck = part.save_checkpoint()
    again = Trainer(_real_data_cfg(tmp_path / "p2", bin_path, data_config))
    again.load_checkpoint(ck)
    assert again.data.position == 4
    again.train(steps=2, progress=False)
    got = [r["loss"] for r in again.history]
    assert got == pytest.approx(want[2:], rel=1e-6, abs=1e-6)


def test_resuming_onto_different_data_is_refused(tmp_path, real_bundle):
    from memlayers.train import Trainer
    import torch
    bin_path, data_config = real_bundle
    t = Trainer(_real_data_cfg(tmp_path, bin_path, data_config))
    ck = t.save_checkpoint()
    blob = torch.load(ck, map_location="cpu", weights_only=False)
    blob["data"]["manifest_sha256"] = "0" * 64
    torch.save(blob, ck)
    t2 = Trainer(_real_data_cfg(tmp_path / "other", bin_path, data_config))
    with pytest.raises(RuntimeError, match="mix two datasets"):
        t2.load_checkpoint(ck)


def test_fake_is_still_the_default_and_needs_no_bundle():
    from memlayers.train import DataCfg, load_config
    assert DataCfg().source == "fake"
    cfg = load_config(ROOT / "memlayers" / "configs" / "t1_pkm.yaml")
    assert cfg.data.source == "fake"
