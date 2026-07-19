"""Shared constants and utility functions for the Decision Maker framework."""

from __future__ import annotations

__all__ = [
    "EPSILON",
    "DEFAULT_SEED",
    "SCALE_MISMATCH_THRESHOLD",
    "DEFAULT_BOOTSTRAP_ITERATIONS",
    "WEIGHT_DELTA",
    "SCORE_DELTAS",
    "HURWICZ_ALPHA_DEFAULT",
    "DISTRIBUTION_MAP",
    "compute_global_bounds",
    "resolve_winner",
]

import math
from typing import TYPE_CHECKING, Any, Dict, List, Tuple

import numpy as np

if TYPE_CHECKING:
    from python.core.models import Factor, Statistics

# ── Re-export shared constants ──────────────────────────────────────

from python.core.models import EPSILON  # noqa: E402

# ── More Shared Constants ───────────────────────────────────────────

DEFAULT_SEED = 42
SCALE_MISMATCH_THRESHOLD = 10
DEFAULT_BOOTSTRAP_ITERATIONS = 200
WEIGHT_DELTA = 0.2
SCORE_DELTAS = [0.1, -0.1, 0.2, -0.2]
HURWICZ_ALPHA_DEFAULT = 0.5

# ── Distribution Mapping ────────────────────────────────────────────

from python.core.models import DistributionType  # noqa: E402

DISTRIBUTION_MAP: Dict[str, DistributionType] = {
    dt.value: dt for dt in DistributionType
}

# ── Utility Functions ───────────────────────────────────────────────


def compute_global_bounds(
    mc_results: Dict[str, Statistics],
    factor_names: List[str],
) -> Dict[str, Dict[str, float]]:
    """Compute min/max bounds across all options for each factor.

    Uses factor_stats means for normalization-compatible bounds.
    """
    bounds: Dict[str, Dict[str, float]] = {
        fn: {"min": math.inf, "max": -math.inf} for fn in factor_names
    }
    for stats in mc_results.values():
        for fn in factor_names:
            if fn in stats.factor_stats:
                val = stats.factor_stats[fn]["mean"]
                bounds[fn]["min"] = min(bounds[fn]["min"], val)
                bounds[fn]["max"] = max(bounds[fn]["max"], val)
    return bounds


def resolve_winner(
    topsis_scores, mc_results
) -> Tuple[str, str]:
    """Determine the winner and the reason from TOPSIS or MC results."""
    if not topsis_scores.empty:
        return topsis_scores.index[0], "F-TOPSIS risk-adjusted distance to ideal"
    winner = max(mc_results.items(), key=lambda x: x[1].mean_score)[0]
    return winner, "Monte Carlo expected value"
