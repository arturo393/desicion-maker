"""
Calibration scoring engine: measure whether confidence percentages match reality.
Usage: from decision_maker.core.calibration_scorer import CalibrationScorer
Does NOT: Run decision algorithms or persist outcomes (see outcome_tracker).
"""

from __future__ import annotations

__all__ = ["CalibrationScorer", "CalibrationBin"]

import logging
from dataclasses import dataclass
from typing import Any

import numpy as np

from decision_maker.core.outcome_tracker import OutcomeEntry

logger = logging.getLogger(__name__)

DEFAULT_BIN_COUNT = 10


@dataclass
class CalibrationBin:
    """A single confidence bin with predicted vs actual accuracy (Parameter Object)."""

    bin_lower: float
    bin_upper: float
    count: int = 0
    predicted_confidence: float = 0.0
    actual_accuracy: float = 0.0
    gap: float = 0.0


class CalibrationScorer:
    """
    Measures calibration: if you say "70% confident", are you right ~70% of the time?

    Uses Expected Calibration Error (ECE) — the weighted average gap between
    predicted confidence and actual accuracy across confidence bins.

    Based on Tetlock's superforecasting research: calibration > raw accuracy.
    """

    @staticmethod
    def score(
        entries: list[OutcomeEntry],
        bin_count: int = DEFAULT_BIN_COUNT,
    ) -> dict[str, Any]:
        if not entries:
            return CalibrationScorer._empty_result()

        confidences = np.array([e.predicted_confidence for e in entries])
        correct = np.array([1.0 if e.was_correct else 0.0 for e in entries])

        bins = CalibrationScorer._compute_bins(confidences, correct, bin_count)
        ece = CalibrationScorer._compute_ece(bins)
        mce = CalibrationScorer._compute_mce(bins)
        brier = CalibrationScorer._compute_brier(confidences, correct)
        sharpness = CalibrationScorer._compute_sharpness(confidences)

        verdict = CalibrationScorer._verdict(ece, len(entries))

        return {
            "ece": float(ece),
            "mce": float(mce),
            "brier_score": float(brier),
            "sharpness": float(sharpness),
            "num_predictions": len(entries),
            "bins": [CalibrationScorer._bin_to_dict(b) for b in bins],
            "verdict": verdict,
            "is_calibrated": ece < 0.1,
            "confidence_distribution": {
                "mean": float(np.mean(confidences)),
                "std": float(np.std(confidences)),
                "min": float(np.min(confidences)),
                "max": float(np.max(confidences)),
            },
        }

    @staticmethod
    def _compute_bins(
        confidences: np.ndarray,
        correct: np.ndarray,
        bin_count: int,
    ) -> list[CalibrationBin]:
        bins = []
        edges = np.linspace(0.0, 1.0, bin_count + 1)
        for i in range(bin_count):
            lower, upper = float(edges[i]), float(edges[i + 1])
            mask = (confidences >= lower) & (confidences < upper)
            if i == bin_count - 1:
                mask = (confidences >= lower) & (confidences <= upper)
            count = int(np.sum(mask))
            predicted = float(np.mean(confidences[mask])) if count > 0 else (lower + upper) / 2
            actual = float(np.mean(correct[mask])) if count > 0 else 0.0
            bins.append(CalibrationBin(
                bin_lower=lower,
                bin_upper=upper,
                count=count,
                predicted_confidence=predicted,
                actual_accuracy=actual,
                gap=abs(predicted - actual),
            ))
        return bins

    @staticmethod
    def _compute_ece(bins: list[CalibrationBin]) -> float:
        total = sum(b.count for b in bins)
        if total == 0:
            return 0.0
        return sum(b.count / total * b.gap for b in bins)

    @staticmethod
    def _compute_mce(bins: list[CalibrationBin]) -> float:
        if not bins:
            return 0.0
        return max(b.gap for b in bins if b.count > 0) if any(b.count > 0 for b in bins) else 0.0

    @staticmethod
    def _compute_brier(confidences: np.ndarray, correct: np.ndarray) -> float:
        if len(confidences) == 0:
            return 0.0
        return float(np.mean((confidences - correct) ** 2))

    @staticmethod
    def _compute_sharpness(confidences: np.ndarray) -> float:
        if len(confidences) == 0:
            return 0.0
        return float(np.std(confidences))

    @staticmethod
    def _verdict(ece: float, n: int) -> str:
        if n < 10:
            return "insufficient_data"
        if ece < 0.05:
            return "well_calibrated"
        if ece < 0.10:
            return "mildly_miscalibrated"
        if ece < 0.20:
            return "miscalibrated"
        return "poorly_calibrated"

    @staticmethod
    def _empty_result() -> dict[str, Any]:
        return {
            "ece": 0.0,
            "mce": 0.0,
            "brier_score": 0.0,
            "sharpness": 0.0,
            "num_predictions": 0,
            "bins": [],
            "verdict": "no_data",
            "is_calibrated": False,
            "confidence_distribution": {},
        }

    @staticmethod
    def _bin_to_dict(b: CalibrationBin) -> dict[str, Any]:
        return {
            "range": f"{b.bin_lower:.1f}-{b.bin_upper:.1f}",
            "count": b.count,
            "predicted": round(b.predicted_confidence, 3),
            "actual": round(b.actual_accuracy, 3),
            "gap": round(b.gap, 3),
        }
