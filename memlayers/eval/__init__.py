"""Evaluation: inside training (cheap, fixed samples), at the end of a run
(full sets), and post hoc on any saved checkpoint (`python -m memlayers.evaluate`).

    from memlayers.eval import register_metric, EvalContext
"""

from .registry import (  # noqa: F401
    RESERVED,
    MetricSpec,
    get_metric,
    register_metric,
    registered,
    validate_metric_names,
)
from .context import EvalContext, EvalResources  # noqa: F401
from . import metrics  # noqa: F401  (registers the built-ins)
