"""Hydra structured configs for `conf/`, and the bridge to the Trainer.

The YAML tree under `conf/` is checked against the dataclasses registered here,
so a misspelled or unknown key (`train.stepz=5`) fails when the config is
composed, before anything is built or written. The Trainer itself still takes a
`TrainConfig`; `to_train_config` is the only conversion.

    from memlayers.config import compose, to_train_config
    cfg = compose(["experiment=pkm", "seed=0"])
    tc = to_train_config(cfg)
"""

from __future__ import annotations

from dataclasses import dataclass, field, fields
from pathlib import Path
from typing import Any, Dict, List, Optional

from hydra.core.config_store import ConfigStore
from omegaconf import MISSING, DictConfig, OmegaConf

from .train import DataCfg, OptimCfg, RuntimeCfg, TrainConfig

__all__ = [
    "MemoryCfg",
    "ModelCfg",
    "EvalCfg",
    "LoggingCfg",
    "RunConfig",
    "CONF_DIR",
    "make_run_id",
    "to_train_config",
    "validate_keys",
    "model_kwargs",
    "compose",
    "load_model_group",
]

CONF_DIR = Path(__file__).resolve().parent.parent / "conf"

# keys each memory kind accepts; the schema is the union, so a key that belongs
# to the other kind is caught in model_kwargs rather than by the schema
_PKM_KEYS = {
    "num_keys",
    "topk",
    "heads",
    "dim_head",
    "query_batchnorm",
    "freeze_keys",
    "value_dropout",
    "non_competitive_gates",
    "renormalize_after_mask",
}
_PEER_KEYS = {
    "num_experts",
    "topk",
    "heads",
    "dim_key",
    "pre_rmsnorm",
    "non_competing_scores",
    "freeze_keys",
    "dropout",
    "separate_embed_per_head",
    "renormalize_after_mask",
}


@dataclass
class MemoryCfg:
    """Union of PKMMemory's and PEERMemory's arguments. None = not set, so the
    layer's own default applies."""

    # shared
    topk: Optional[int] = None
    heads: Optional[int] = None
    freeze_keys: Optional[bool] = None
    renormalize_after_mask: Optional[bool] = None
    # PKM
    num_keys: Optional[int] = None
    dim_head: Optional[int] = None
    query_batchnorm: Optional[bool] = None
    value_dropout: Optional[float] = None
    non_competitive_gates: Optional[bool] = None
    # PEER
    num_experts: Optional[int] = None
    dim_key: Optional[int] = None
    pre_rmsnorm: Optional[bool] = None
    non_competing_scores: Optional[bool] = None
    dropout: Optional[float] = None
    separate_embed_per_head: Optional[bool] = None


@dataclass
class ModelCfg:
    """Mirror of GPTConfig, plus `compute_match` (bookkeeping only)."""

    vocab_size: int = 50257
    block_size: int = 512
    n_layer: int = 6
    n_head: int = 6
    n_embd: int = 384
    dropout: float = 0.0
    bias: bool = True
    tie_embeddings: bool = True
    ffn_types: Optional[List[str]] = None
    memory_layers: List[int] = field(default_factory=list)
    memory_kind: str = "pkm"
    memory: MemoryCfg = field(default_factory=MemoryCfg)
    ffn_hidden: Dict[int, int] = field(default_factory=dict)
    # name of a model group config this dense model is FLOP-matched against;
    # run.py records both layers' FLOPs in meta.json. Not passed to GPTConfig.
    compute_match: Optional[str] = None


_ALL_METRICS = ["heldout_quality", "fact_recall", "slot_usage"]
_DEFAULT_POINTS = [0, 0.027, 0.055, 0.109, 0.218, 0.382, 0.546, 0.765, 1.0]


@dataclass
class TrainingCheckCfg:
    """Thresholds of memlayers/eval/training_check.py."""

    enabled: bool = True
    divergence_factor: float = 1.5
    min_drop_from_init: float = 0.40
    rising_tolerance: float = 0.005
    min_coverage: float = 0.5  # set from the pilot in training prompt 5
    fact_ratio: float = 2.0


@dataclass
class EvalCfg:
    """When to evaluate and what. See memlayers/eval/."""

    # fractions of the run; 1.0 is the `final` stage. `steps` (absolute) wins.
    points: List[float] = field(default_factory=lambda: list(_DEFAULT_POINTS))
    steps: Optional[List[int]] = None
    during: List[str] = field(default_factory=lambda: list(_ALL_METRICS))
    final: List[str] = field(default_factory=lambda: list(_ALL_METRICS))
    posthoc: List[str] = field(default_factory=lambda: list(_ALL_METRICS))
    seed: int = 0  # the evaluation's own RNG seed; never the run seed
    heldout_batch: int = 8  # windows per forward in the held-out pass
    fact_batch_tokens: int = 16384  # ProbeSet.score's batch budget
    training_check: TrainingCheckCfg = field(default_factory=TrainingCheckCfg)


@dataclass
class LoggingCfg:
    """Filled in by training prompt 3."""


@dataclass
class RunConfig:
    name: str = MISSING  # the experiment name, set by conf/experiment/*.yaml
    seed: int = 0
    tag: str = ""
    run_id: str = "${make_run_id:${name},${seed},${tag}}"
    out_root: str = "runs"
    force: bool = False
    resume: bool = True
    resume_foreign: bool = False
    model: ModelCfg = field(default_factory=ModelCfg)
    data: DataCfg = field(default_factory=DataCfg)
    train: OptimCfg = field(default_factory=OptimCfg)
    eval: EvalCfg = field(default_factory=EvalCfg)
    logging: LoggingCfg = field(default_factory=LoggingCfg)
    runtime: RuntimeCfg = field(default_factory=RuntimeCfg)


def make_run_id(name: Any, seed: Any, tag: Any = "") -> str:
    """`<experiment>-s<seed>`, plus `-<tag>` when a tag is set. No timestamp."""
    rid = f"{name}-s{seed}"
    tag = "" if tag is None else str(tag)
    return f"{rid}-{tag}" if tag else rid


def _register() -> None:
    if not OmegaConf.has_resolver("make_run_id"):
        OmegaConf.register_new_resolver(
            "make_run_id", lambda n, s, t="": make_run_id(n, s, t)
        )
    cs = ConfigStore.instance()
    cs.store(name="run_schema", node=RunConfig)
    # the group schemas on their own too, for anyone composing a single group
    cs.store(group="schema", name="model", node=ModelCfg)
    cs.store(group="schema", name="data", node=DataCfg)
    cs.store(group="schema", name="train", node=OptimCfg)
    cs.store(group="schema", name="runtime", node=RuntimeCfg)
    cs.store(group="schema", name="eval", node=EvalCfg)
    cs.store(group="schema", name="logging", node=LoggingCfg)


_register()


# ------------------------------------------------------------------ conversion
def model_kwargs(model: Any) -> Dict[str, Any]:
    """A composed `model` node -> GPTConfig kwargs (the TrainConfig.model dict)."""
    if isinstance(model, DictConfig):
        model = OmegaConf.to_container(model, resolve=True, throw_on_missing=True)
    m = dict(model)
    m.pop("compute_match", None)
    mem = {k: v for k, v in (m.get("memory") or {}).items() if v is not None}
    kinds = set(m.get("ffn_types") or []) | (
        {m.get("memory_kind", "pkm")} if m.get("memory_layers") else set()
    )
    kinds.discard("dense")
    allowed = set().union(
        *[_PKM_KEYS if k == "pkm" else _PEER_KEYS for k in kinds]
    ) or (_PKM_KEYS | _PEER_KEYS)
    wrong = sorted(set(mem) - allowed)
    if wrong:
        raise ValueError(
            f"model.memory keys {wrong} do not apply to memory kind(s) {sorted(kinds)}"
        )
    m["memory"] = mem
    m["memory_layers"] = list(m.get("memory_layers") or [])
    m["ffn_hidden"] = {int(k): int(v) for k, v in (m.get("ffn_hidden") or {}).items()}
    if m.get("ffn_types") is None:
        m.pop("ffn_types", None)
    return m


def validate_keys(cfg: DictConfig, path: str = "") -> None:
    """Refuse keys that are not fields of their node's dataclass.

    Hydra's `+key=value` append opens the struct flag, so `+train.stepz=5`
    would otherwise slip past the schema; this closes that gap.
    """
    from dataclasses import is_dataclass

    typ = OmegaConf.get_type(cfg)
    if typ is not None and is_dataclass(typ):
        names = {f.name for f in fields(typ)}
        extra = sorted(set(cfg.keys()) - names)
        if extra:
            where = path or "<root>"
            raise ValueError(
                f"unknown key(s) {extra} under {where}; {typ.__name__} has "
                f"{sorted(names)}"
            )
    for k in cfg.keys():
        v = cfg._get_node(k)
        if isinstance(v, DictConfig) and not v._is_missing() and not v._is_none():
            validate_keys(v, f"{path}.{k}" if path else str(k))


def to_train_config(cfg: DictConfig) -> TrainConfig:
    """A composed run config -> the Trainer's TrainConfig."""
    validate_keys(cfg)
    c = OmegaConf.to_container(cfg, resolve=True, throw_on_missing=True)

    def build(cls, d):
        return cls(**d)

    train = build(OptimCfg, c["train"])
    train.betas = tuple(train.betas)
    return TrainConfig(
        name=c["name"],
        model=model_kwargs(c["model"]),
        data=build(DataCfg, c["data"]),
        train=train,
        runtime=build(RuntimeCfg, c["runtime"]),
    )


def compose(overrides: Optional[List[str]] = None, config_name: str = "config"):
    """Compose `conf/` outside `@hydra.main` (tests, notebooks)."""
    from hydra import compose as _compose, initialize_config_dir

    with initialize_config_dir(config_dir=str(CONF_DIR), version_base="1.3"):
        cfg = _compose(config_name=config_name, overrides=list(overrides or []))
    validate_keys(cfg)
    return cfg


def load_model_group(name: str) -> DictConfig:
    """One `conf/model/<name>.yaml`, checked against ModelCfg."""
    path = CONF_DIR / "model" / f"{name}.yaml"
    if not path.exists():
        raise FileNotFoundError(f"no model config {path}")
    return OmegaConf.merge(OmegaConf.structured(ModelCfg), OmegaConf.load(path))
