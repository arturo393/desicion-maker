"""
Ergodicity analysis engine comparing ensemble averages vs temporal averages.
Usage: from decision_maker.core.ergodicity import ErgodicityAnalyzer
Does NOT: Modify raw_scores or persist results (see reporting/registry).
"""

from __future__ import annotations

__all__ = ["ErgodicityAnalyzer", "ErgodicityResult"]

import logging
from dataclasses import dataclass
from typing import Any

import numpy as np

from decision_maker.core.models import Factor, Statistics
from decision_maker.core.utils import EPSILON

logger = logging.getLogger(__name__)


@dataclass
class ErgodicityResult:
    """Bundles ergodicity metrics for a single option (Parameter Object)."""

    option_name: str
    ensemble_mean: float
    ensemble_std: float
    temporal_log_growth: float
    geometric_mean: float
    ruin_probability: float
    max_drawdown: float
    time_horizon_divergence: float
    is_ergodic: bool
    verdict: str


class ErgodicityAnalyzer:
    """
    Analyzes whether decision options are ergodic (ensemble avg ≈ temporal avg)
    or non-ergodic (ensemble avg ≠ temporal avg, typical in multiplicative processes).

    Based on Ole Peters' ergodicity economics: in multiplicative dynamics,
    the time-average growth rate (what you actually experience) differs from
    the ensemble average (what a parallel universe average would show).
    """

    RUIN_THRESHOLD = 0.0
    DEFAULT_TIME_HORIZONS = [10, 50, 100, 500]

    @staticmethod
    def analyze(
        mc_results: dict[str, Statistics],
        factors: list[Factor],
        time_horizons: list[int] | None = None,
    ) -> dict[str, Any]:
        if not mc_results:
            return {"options": {}, "ranking": [], "summary": "No results to analyze"}

        horizons = time_horizons or ErgodicityAnalyzer.DEFAULT_TIME_HORIZONS
        options = {}
        for name, stats in mc_results.items():
            if stats.raw_scores is None:
                continue
            result = ErgodicityAnalyzer._analyze_option(name, stats, horizons)
            options[name] = result

        ranking = sorted(options.keys(), key=lambda n: options[n].temporal_log_growth, reverse=True)
        ergodic_count = sum(1 for r in options.values() if r.is_ergodic)

        return {
            "options": {n: _result_to_dict(r) for n, r in options.items()},
            "ranking": [{"option": n, "log_growth": options[n].temporal_log_growth} for n in ranking],
            "ergodic_count": ergodic_count,
            "non_ergodic_count": len(options) - ergodic_count,
            "time_horizons_tested": horizons,
            "summary": ErgodicityAnalyzer._build_summary(options, ergodic_count),
        }

    @staticmethod
    def _analyze_option(
        name: str,
        stats: Statistics,
        horizons: list[int],
    ) -> ErgodicityResult:
        scores = stats.raw_scores

        ensemble_mean = float(np.mean(scores))
        ensemble_std = float(np.std(scores))

        positive_scores = np.maximum(scores, EPSILON)
        log_returns = np.log(positive_scores)
        temporal_log_growth = float(np.mean(log_returns))
        geometric_mean = float(np.exp(temporal_log_growth))

        ruin_count = np.sum(scores < ErgodicityAnalyzer.RUIN_THRESHOLD)
        ruin_probability = float(ruin_count / len(scores))

        cumulative = np.cumprod(positive_scores)
        running_max = np.maximum.accumulate(cumulative)
        drawdowns = (running_max - cumulative) / np.maximum(running_max, EPSILON)
        max_drawdown = float(np.max(drawdowns)) if len(drawdowns) > 0 else 0.0

        divergences = []
        for h in horizons:
            if h <= len(positive_scores):
                subset = positive_scores[:h]
                temporal_h = float(np.mean(np.log(subset)))
                ensemble_h = float(np.log(np.mean(subset)))
                divergences.append(abs(temporal_h - ensemble_h))
        time_horizon_divergence = float(np.mean(divergences)) if divergences else 0.0

        is_ergodic = time_horizon_divergence < 0.05 and ruin_probability < 0.01
        verdict = (
            "ergodic" if is_ergodic
            else "mildly_non_ergodic" if time_horizon_divergence < 0.2
            else "non_ergodic"
        )

        return ErgodicityResult(
            option_name=name,
            ensemble_mean=ensemble_mean,
            ensemble_std=ensemble_std,
            temporal_log_growth=temporal_log_growth,
            geometric_mean=geometric_mean,
            ruin_probability=ruin_probability,
            max_drawdown=max_drawdown,
            time_horizon_divergence=time_horizon_divergence,
            is_ergodic=is_ergodic,
            verdict=verdict,
        )

    @staticmethod
    def _build_summary(options: dict[str, ErgodicityResult], ergodic_count: int) -> str:
        if not options:
            return "No options to analyze"
        total = len(options)
        best = max(options.values(), key=lambda r: r.temporal_log_growth)
        return (
            f"{ergodic_count}/{total} ergodic. "
            f"Best temporal growth: {best.option_name} "
            f"(log-growth={best.temporal_log_growth:.4f}, "
            f"ruin_p={best.ruin_probability:.2%})"
        )


def _result_to_dict(result: ErgodicityResult) -> dict[str, Any]:
    return {
        "option_name": result.option_name,
        "ensemble_mean": result.ensemble_mean,
        "ensemble_std": result.ensemble_std,
        "temporal_log_growth": result.temporal_log_growth,
        "geometric_mean": result.geometric_mean,
        "ruin_probability": result.ruin_probability,
        "max_drawdown": result.max_drawdown,
        "time_horizon_divergence": result.time_horizon_divergence,
        "is_ergodic": result.is_ergodic,
        "verdict": result.verdict,
    }
