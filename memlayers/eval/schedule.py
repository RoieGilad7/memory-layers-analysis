"""When to evaluate: fractions of the run, rounded to whole steps.

`eval.points` (fractions, default about steps 0, 250, 500, 1000, 2000, 3500,
5000, 7000 and the end of a 9,156-step run) is rounded and de-duplicated;
`eval.steps` (absolute) overrides it when set. The last step of the run is the
`final` stage, every other point `during`.
"""

from __future__ import annotations

from typing import List, Optional, Sequence, Tuple

__all__ = ["DEFAULT_POINTS", "eval_schedule"]

DEFAULT_POINTS = [0, 0.027, 0.055, 0.109, 0.218, 0.382, 0.546, 0.765, 1.0]


def eval_schedule(
    total_steps: int,
    points: Optional[Sequence[float]] = None,
    steps: Optional[Sequence[int]] = None,
) -> List[Tuple[int, str]]:
    """[(step, stage), ...] in step order, each step once."""
    total = int(total_steps)
    if steps is not None:
        chosen = sorted({int(s) for s in steps})
        bad = [s for s in chosen if not 0 <= s <= total]
        if bad:
            raise ValueError(f"eval.steps {bad} outside 0..{total}")
    else:
        pts = DEFAULT_POINTS if points is None else list(points)
        bad = [p for p in pts if not 0.0 <= float(p) <= 1.0]
        if bad:
            raise ValueError(f"eval.points {bad} must be fractions in [0, 1]")
        # round half up, so 0.5 of an odd run lands on a whole step predictably
        chosen = sorted({int(float(p) * total + 0.5) for p in pts})
    return [(s, "final" if s == total else "during") for s in chosen]
