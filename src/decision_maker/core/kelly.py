"""
Kelly criterion engine for optimal bet sizing under uncertainty.
Usage: from decision_maker.core.kelly import KellyCriterionEngine
Does NOT: Execute trades or persist results (see reporting/registry).
"""

from __future__ import annotations

__all__ = ["KellyCriterionEngine", "KellyResult"]

import logging
from dataclasses import dataclass
from typing import Any

import numpy as np

from decision_maker.core.models import Factor, Statistics
from decision_maker.core.utils import EPSILON

logger = logging.getLogger(__name__)


@dataclass
class KellyResult:
    """Bundles Kelly metrics for a single option (Parameter Object)."""

    option_name: str
    kelly_fraction: float
    fractional_kelly_half: float
    fractional_kelly_quarter: float
    expected_growth_rate: float
    edge: float
    odds: float
    win_probability: float
    max_loss_fraction: float
    verdict: str


class KellyCriterionEngine:
    """
    Computes Kelly-optimal bet sizing for decision options.

    The Kelly criterion maximizes the long-run geometric growth rate:
        f* = (p * b - q) / b
    where p = win probability, q = 1 - p, b = odds (payout ratio).

    Fractional Kelly (f*/2, f*/4) reduces variance at the cost of
    slightly lower growth — practical for noisy environments.
    """

    @staticmethod
    def analyze(
        mc_results: dict[str, Statistics],
        factors: list[Factor],
        risk_fraction: float = 0.5,
    ) -> dict[str, Any]:
        if not mc_results:
            return {"options": {}, "ranking": [], "summary": "No results to analyze"}

        options = {}
        for name, stats in mc_results.items():
            if stats.raw_scores is None:
                continue
            result = KellyCriterionEngine._analyze_option(name, stats, risk_fraction)
            options[name] = result

        ranking = sorted(options.keys(), key=lambda n: options[n].kelly_fraction, reverse=True)
        best = ranking[0] if ranking else None

        return {
            "options": {n: _kelly_to_dict(r) for n, r in options.items()},
            "ranking": [{"option": n, "kelly_f": options[n].kelly_fraction} for n in ranking],
            "risk_fraction_used": risk_fraction,
            "summary": KellyCriterionEngine._build_summary(options, best, risk_fraction),
        }

    @staticmethod
    def _analyze_option(
        name: str,
        stats: Statistics,
        risk_fraction: float,
    ) -> KellyResult:
        scores = stats.raw_scores

        win_threshold = 0.0
        win_count = np.sum(scores > win_threshold)
        total = len(scores)
        win_probability = float(win_count / total) if total > 0 else 0.0
        lose_probability = 1.0 - win_probability

        winning_scores = scores[scores > win_threshold]
        losing_scores = scores[scores <= win_threshold]

        if len(winning_scores) > 0 and len(losing_scores) > 0:
            avg_win = float(np.mean(winning_scores))
            avg_loss = float(np.abs(np.mean(losing_scores)))
            odds = avg_win / (avg_loss + EPSILON)
        else:
            odds = 1.0

        edge = win_probability * odds - lose_probability
        kelly_f = edge / (odds + EPSILON) if odds > EPSILON else 0.0
        kelly_f = float(np.clip(kelly_f, 0.0, 1.0))

        fractional_half = kelly_f * 0.5
        fractional_quarter = kelly_f * 0.25

        positive_scores = np.maximum(scores, EPSILON)
        log_returns = np.log(positive_scores)
        expected_growth_rate = float(np.mean(log_returns))

        max_loss_fraction = float(np.abs(np.min(losing_scores))) / (np.mean(np.abs(scores)) + EPSILON) if len(losing_scores) > 0 else 0.0

        if kelly_f <= 0:
            verdict = "do_not_bet"
        elif kelly_f < 0.05:
            verdict = "small_edge"
        elif kelly_f < 0.25:
            verdict = "moderate_edge"
        else:
            verdict = "strong_edge"

        return KellyResult(
            option_name=name,
            kelly_fraction=kelly_f,
            fractional_kelly_half=fractional_half,
            fractional_kelly_quarter=fractional_quarter,
            expected_growth_rate=expected_growth_rate,
            edge=edge,
            odds=odds,
            win_probability=win_probability,
            max_loss_fraction=max_loss_fraction,
            verdict=verdict,
        )

    @staticmethod
    def _build_summary(
        options: dict[str, KellyResult],
        best: str | None,
        risk_fraction: float,
    ) -> str:
        if not options:
            return "No options to analyze"
        total = len(options)
        bettable = sum(1 for r in options.values() if r.kelly_fraction > 0)
        if best:
            b = options[best]
            return (
                f"{bettable}/{total} have positive edge. "
                f"Best: {best} (Kelly={b.kelly_fraction:.2%}, "
                f"edge={b.edge:.3f}, odds={b.odds:.2f})"
            )
        return f"{bettable}/{total} have positive edge"


def _kelly_to_dict(result: KellyResult) -> dict[str, Any]:
    return {
        "option_name": result.option_name,
        "kelly_fraction": result.kelly_fraction,
        "fractional_kelly_half": result.fractional_kelly_half,
        "fractional_kelly_quarter": result.fractional_kelly_quarter,
        "expected_growth_rate": result.expected_growth_rate,
        "edge": result.edge,
        "odds": result.odds,
        "win_probability": result.win_probability,
        "max_loss_fraction": result.max_loss_fraction,
        "verdict": result.verdict,
    }
