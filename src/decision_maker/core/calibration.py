"""
Decision calibration metrics: how well the framework's predictions matched real outcomes.
Usage: from decision_maker.core.calibration import compute_calibration, DecisionOutcome
Does NOT: Store outcomes (see registry) or run decision algorithms.
"""

from __future__ import annotations

__all__ = ["DecisionOutcome", "compute_calibration"]

from dataclasses import dataclass
from typing import Any


@dataclass
class DecisionOutcome:
    """A resolved decision: what the system recommended vs what actually happened."""

    predicted_winner: str
    actual_winner: str
    confidence: float = 1.0
    predicted_probabilities: dict[str, float] | None = None


def _brier_score(outcomes: list[DecisionOutcome]) -> float:
    """Mean Brier score over outcomes (lower is better, 0 = perfect)."""
    if not outcomes:
        return 0.0
    total = 0.0
    for o in outcomes:
        if o.predicted_probabilities:
            for option, prob in o.predicted_probabilities.items():
                actual = 1.0 if option == o.actual_winner else 0.0
                total += (prob - actual) ** 2
        else:
            total += (1.0 - o.confidence) ** 2
    return total / len(outcomes)


def _hit_rate(outcomes: list[DecisionOutcome]) -> float:
    """Fraction of decisions where the predicted winner matched the actual outcome."""
    if not outcomes:
        return 0.0
    hits = sum(1 for o in outcomes if o.predicted_winner == o.actual_winner)
    return hits / len(outcomes)


def _mean_confidence(outcomes: list[DecisionOutcome]) -> float:
    """Average reported confidence across decisions."""
    if not outcomes:
        return 0.0
    return sum(o.confidence for o in outcomes) / len(outcomes)


def _separation_index(outcomes: list[DecisionOutcome]) -> float:
    """
    Difference between average confidence on hits vs misses.
    A well-calibrated system is more confident when right than when wrong.
    """
    if not outcomes:
        return 0.0
    hits = [o.confidence for o in outcomes if o.predicted_winner == o.actual_winner]
    misses = [o.confidence for o in outcomes if o.predicted_winner != o.actual_winner]
    if not hits or not misses:
        return 0.0
    return (sum(hits) / len(hits)) - (sum(misses) / len(misses))


def compute_calibration(outcomes: list[DecisionOutcome]) -> dict[str, Any]:
    """Compute calibration metrics for a set of resolved decisions."""
    if not outcomes:
        return {
            "n_outcomes": 0,
            "hit_rate": 0.0,
            "brier_score": 0.0,
            "mean_confidence": 0.0,
            "separation_index": 0.0,
            "verdict": "insufficient_data",
        }

    hit = _hit_rate(outcomes)
    brier = _brier_score(outcomes)
    conf = _mean_confidence(outcomes)
    sep = _separation_index(outcomes)

    if sep < -0.1:
        verdict = "overconfident"
    elif hit >= 0.7 and brier <= 0.25:
        verdict = "well_calibrated"
    elif hit >= 0.5:
        verdict = "moderately_calibrated"
    else:
        verdict = "poorly_calibrated"

    return {
        "n_outcomes": len(outcomes),
        "hit_rate": hit,
        "brier_score": brier,
        "mean_confidence": conf,
        "separation_index": sep,
        "verdict": verdict,
    }
