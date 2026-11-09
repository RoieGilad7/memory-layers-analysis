"""conf/ composes, is strict, and reproduces the old flat YAML configs."""

from dataclasses import asdict
from pathlib import Path

import pytest

from memlayers.config import (
    CONF_DIR,
    compose,
    load_model_group,
    make_run_id,
    model_kwargs,
    to_train_config,
)
from memlayers.model import GPTConfig
from memlayers.run import run_dir_for
from memlayers.train import load_config

ROOT = Path(__file__).resolve().parent.parent
OLD = ROOT / "memlayers" / "configs"

EXPERIMENTS = [
    "pkm",
    "pkm_randkey",
    "dense",
    "peer",
    "smoke",
    "smoke_randkey",
    "smoke_dense",
]
RUNTIMES = ["auto", "mac", "cpu", "cuda", "colab"]


def _groups(name):
    return sorted(p.stem for p in (CONF_DIR / name).glob("*.yaml"))


def test_the_tree_has_the_fixed_groups():
    assert _groups("experiment") == sorted(EXPERIMENTS)
    assert _groups("runtime") == sorted(RUNTIMES)
    assert _groups("data") == ["fake", "sample", "v1"]
    assert _groups("train") == ["smoke", "tier1"]
    assert _groups("eval") == ["off", "smoke", "standard"]
    assert _groups("logging") == ["files", "wandb"]
    assert {
        "pkm",
        "pkm_randkey",
        "dense",
        "peer",
        "tiny_pkm",
        "tiny_dense",
        "pkm_t2",
        "peer_t2",
        "dense_t2",
    } <= set(_groups("model"))


@pytest.mark.parametrize("runtime", RUNTIMES)
@pytest.mark.parametrize("experiment", EXPERIMENTS)
def test_every_experiment_composes_with_every_runtime(experiment, runtime):
    cfg = compose([f"experiment={experiment}", f"runtime={runtime}"])
    tc = to_train_config(cfg)
    assert tc.name == experiment
    GPTConfig(**tc.model)  # the model kwargs are valid
    assert tc.runtime.out_dir == f"runs/{experiment}-s0"


def test_every_model_group_builds_a_gpt_config():
    for name in _groups("model"):
        GPTConfig(**model_kwargs(load_model_group(name)))


@pytest.mark.parametrize(
    "bad",
    ["train.stepz=5", "+train.stepz=5", "+model.memory.num_kyes=3", "+data.sed=1"],
)
def test_an_unknown_key_fails_at_compose_time(bad):
    with pytest.raises(Exception, match="stepz|num_kyes|sed"):
        compose(["experiment=smoke", bad])


def test_a_wrongly_typed_value_fails_at_compose_time():
    with pytest.raises(Exception):
        compose(["experiment=smoke", "train.steps=many"])


def test_a_memory_key_of_the_other_kind_is_refused():
    cfg = compose(["experiment=peer", "model.memory.num_keys=256"])
    with pytest.raises(ValueError, match="num_keys"):
        to_train_config(cfg)


def test_an_experiment_is_required():
    with pytest.raises(Exception, match="experiment"):
        compose([])


# --------------------------------------------------------------- round trip
# What bench/learnability_run.py (the A18 run) passed on top of t1_pkm.yaml.
A18 = [
    "data.source=real",
    "data.version=v1",
    "data.data_config=configs/data/v1.yaml",
    "data.seed=0",
    "train.seed=0",
    "train.steps=5830",
    "train.micro_batch_size=32",
    "train.log_every=50",
]
# the documented tier1 changes against the A18 run
TIER1_CHANGES = {"steps": (5830, 9156), "ckpt_every": (0, 500), "log_every": (50, 10)}


def test_pkm_round_trips_to_the_a18_configuration():
    new = to_train_config(compose(["experiment=pkm", "seed=0"]))
    old = load_config(OLD / "t1_pkm.yaml", A18)

    assert GPTConfig(**new.model) == GPTConfig(**old.model)
    assert asdict(new.data) == asdict(old.data)
    a, b = asdict(old.train), asdict(new.train)
    a["betas"], b["betas"] = tuple(a["betas"]), tuple(b["betas"])
    diff = {k: (a[k], b[k]) for k in a if a[k] != b[k]}
    assert diff == TIER1_CHANGES
    assert new.tokens_per_step == old.tokens_per_step == 16_384
    assert new.train.steps * new.tokens_per_step == 150_011_904
    assert (new.train.steps - 1) * new.tokens_per_step < 150_000_000
    assert new.runtime.device == old.runtime.device == "auto"


def test_the_lrs_and_warmup_are_t1_pkm_yamls():
    new = to_train_config(compose(["experiment=pkm"])).train
    old = load_config(OLD / "t1_pkm.yaml").train
    for k in (
        "lr",
        "lr_memory_values",
        "lr_memory_keys",
        "weight_decay",
        "weight_decay_memory",
        "betas",
        "eps",
        "grad_clip",
        "warmup_steps",
        "min_lr_ratio",
        "grad_accum_steps",
    ):
        a, b = getattr(new, k), getattr(old, k)
        if k == "betas":
            a, b = tuple(a), tuple(b)
        assert a == b, k


@pytest.mark.parametrize(
    "group, old",
    [
        ("pkm", "t1_pkm"),
        ("pkm_randkey", "t1_pkm_frozen"),
        ("peer", "t1_peer"),
        ("pkm_t2", "t2_pkm"),
        ("peer_t2", "t2_peer"),
        ("pkm262k_t2", "t2_pkm_262k"),
    ],
)
def test_memory_models_are_ported_unchanged(group, old):
    new = GPTConfig(**model_kwargs(load_model_group(group)))
    assert new == GPTConfig(**load_config(OLD / f"{old}.yaml").model)


@pytest.mark.parametrize(
    "group, old, layer", [("dense", "t1_dense", 3), ("dense_t2", "t2_dense", 4)]
)
def test_dense_models_differ_from_the_old_ones_only_in_the_matched_layer(
    group, old, layer
):
    new = model_kwargs(load_model_group(group))
    assert set(new["ffn_hidden"]) == {layer}
    new["ffn_hidden"] = {}
    assert GPTConfig(**new) == GPTConfig(**load_config(OLD / f"{old}.yaml").model)


def test_pkm_randkey_is_pkm_with_frozen_keys():
    a = model_kwargs(load_model_group("pkm"))
    b = model_kwargs(load_model_group("pkm_randkey"))
    assert b["memory"].pop("freeze_keys") is True
    assert a["memory"].pop("freeze_keys") is False
    assert a == b


# ------------------------------------------------------------------ seed, id
def test_the_top_level_seed_drives_every_seed():
    tc = to_train_config(compose(["experiment=pkm", "seed=7"]))
    assert tc.data.seed == 7 and tc.train.seed == 7


def test_data_and_train_seeds_stay_overridable_for_tests():
    tc = to_train_config(compose(["experiment=smoke", "seed=7", "data.seed=3"]))
    assert tc.data.seed == 3 and tc.train.seed == 7


def test_run_id_and_run_dir_without_a_tag():
    cfg = compose(["experiment=pkm", "seed=0"])
    assert cfg.run_id == "pkm-s0"
    assert run_dir_for(cfg) == Path("runs/pkm-s0")


def test_run_id_and_run_dir_with_a_tag():
    cfg = compose(["experiment=pkm_randkey", "seed=2", "tag=pilot", "out_root=/x"])
    assert cfg.run_id == "pkm_randkey-s2-pilot"
    assert run_dir_for(cfg) == Path("/x/pkm_randkey-s2-pilot")
    assert to_train_config(cfg).runtime.out_dir == "/x/pkm_randkey-s2-pilot"


def test_make_run_id():
    assert make_run_id("dense", 1) == "dense-s1"
    assert make_run_id("dense", 1, "") == "dense-s1"
    assert make_run_id("dense", 1, "b") == "dense-s1-b"
