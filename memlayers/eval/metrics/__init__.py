"""Built-in metrics. Importing this package registers them.

Q2 (`fact_recall`) is registered from the checkpoint suite, `metrics/q2`, so
training and the checkpoint metrics share one fact-recall definition.
"""

from . import heldout_quality, slot_usage  # noqa: F401
import metrics.q2.training  # noqa: F401,E402
