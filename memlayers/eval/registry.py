"""The metric registry.

A metric is a function `(ctx: EvalContext) -> dict[str, float]` registered under
a meaningful snake_case name; the methodology's short id (Q1, Q2, U1, ...) is a
separate field. Keys of the returned dict are slash paths `<quantity>/<subset>`,
e.g. `loss/pile_cc`, `top1/frequent/test`, `coverage/layer3`.

    @register_metric("fact_recall", metric_id="Q2",
                     stages=("during", "final", "posthoc"),
                     needs_memory=False, inputs=("model", "fact_probe"))
    def fact_recall(ctx): ...

Contract: deterministic for a given seed; leaves the model exactly as it found
it; works on CPU; never raises because an input is missing -- the framework
checks `inputs` and `needs_memory` first and records why a metric was skipped.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, Iterable, List, Sequence, Tuple

__all__ = [
    "MetricSpec",
    "register_metric",
    "get_metric",
    "registered",
    "RESERVED",
    "STAGES",
    "INPUTS",
    "validate_metric_names",
    "UnknownMetric",
]

STAGES = ("during", "final", "posthoc")
# what a metric may ask the context for; EvalContext.available() knows each
INPUTS = ("model", "heldout", "fact_probe", "init_model", "readlog")

# Names kept for later plugins: listed, not runnable. A plugin that registers
# one of them takes it out of this table.
RESERVED: Dict[str, Tuple[str, str]] = {
    "subject_specificity": ("U4", "metric"),
    "subject_removal": ("E1", "metric"),
    "fact_core_set": ("E2", "metric"),
    "read_concentration": ("V2", "metric"),
    "slot_inspection": ("C4", "metric"),
    "effective_rank": ("C6", "metric"),
    "learned_vs_random_keys": ("X2", "comparison"),
    "knn_lm_comparison": ("X3", "comparison"),
    "training_check": ("-", "check"),
}


class UnknownMetric(ValueError):
    pass


@dataclass(frozen=True)
class MetricSpec:
    name: str
    metric_id: str
    fn: Callable
    stages: Tuple[str, ...]
    needs_memory: bool = False
    inputs: Tuple[str, ...] = ("model",)
    description: str = ""


_REGISTRY: Dict[str, MetricSpec] = {}


def register_metric(
    name: str,
    *,
    metric_id: str,
    stages: Sequence[str] = STAGES,
    needs_memory: bool = False,
    inputs: Sequence[str] = ("model",),
):
    if not name or name != name.lower() or not name.replace("_", "").isalnum():
        raise ValueError(f"metric name {name!r} must be snake_case")
    bad = set(stages) - set(STAGES)
    if bad:
        raise ValueError(f"{name}: unknown stages {sorted(bad)}; use {STAGES}")
    bad = set(inputs) - set(INPUTS)
    if bad:
        raise ValueError(f"{name}: unknown inputs {sorted(bad)}; use {INPUTS}")
    if name == "training_check":
        raise ValueError("training_check is the run's own check, not a metric")

    def deco(fn):
        if name in _REGISTRY:
            raise ValueError(f"metric {name!r} is already registered")
        taken = {s.metric_id: s.name for s in _REGISTRY.values()}
        if metric_id in taken:
            raise ValueError(
                f"metric_id {metric_id} already belongs to {taken[metric_id]}"
            )
        reserved = RESERVED.get(name)
        if reserved and reserved[0] != metric_id:
            raise ValueError(f"{name} is reserved with metric_id {reserved[0]}")
        RESERVED.pop(name, None)
        _REGISTRY[name] = MetricSpec(
            name=name,
            metric_id=metric_id,
            fn=fn,
            stages=tuple(stages),
            needs_memory=needs_memory,
            inputs=tuple(inputs),
            description=(fn.__doc__ or "").strip().split("\n")[0],
        )
        return fn

    return deco


def registered() -> Dict[str, MetricSpec]:
    return dict(_REGISTRY)


def get_metric(name: str) -> MetricSpec:
    validate_metric_names([name])
    return _REGISTRY[name]


def validate_metric_names(names: Iterable[str], stage: str | None = None) -> List[str]:
    """Raise UnknownMetric, naming every known metric, if any name is not runnable."""
    names = list(names)
    known = sorted(_REGISTRY)
    for n in names:
        if n in _REGISTRY:
            spec = _REGISTRY[n]
            if stage is not None and stage not in spec.stages:
                raise UnknownMetric(
                    f"metric {n!r} does not run at stage {stage!r} (its stages: "
                    f"{', '.join(spec.stages)})"
                )
            continue
        if n in RESERVED:
            mid, kind = RESERVED[n]
            raise UnknownMetric(
                f"{n!r} ({mid}) is a reserved {kind} name, not implemented yet. "
                f"Runnable metrics: {', '.join(known)}"
            )
        raise UnknownMetric(
            f"unknown metric {n!r}. Runnable metrics: {', '.join(known)}. "
            f"Reserved for later: {', '.join(sorted(RESERVED))}"
        )
    return names
