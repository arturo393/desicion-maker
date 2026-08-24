"""
Minimum action threshold: decide when NOT to decide.
Usage: from decision_maker.core.action_threshold import MinimumActionThreshold
Does NOT: Run decision algorithms or compute scores.
"""

from __future__ import annotations

__all__ = ["MinimumActionThreshold", "ThresholdVerdict"]

import logging
from dataclasses import dataclass
from typing import Any

import numpy as np

from decision_maker.core.models import Factor, Statistics

logger = logging.getLogger(__name__)


@dataclass
class ThresholdVerdict:
    """Result of a minimum action threshold check (Parameter Object)."""

    should_decide: bool
    signal_strength: float
    noise_level: float
    signal_to_noise: float
    max_spread: float
    min_meaningful_gap: float
    winning_option: str
    confidence_in_winner: float
    verdict: str
    reasoning: str


class MinimumActionThreshold:
    """
    The hardest part of decision-making is knowing when NOT to decide.

    This engine computes whether the signal (difference between options)
    is strong enough to justify the cost of deciding. If the top two options
    are within noise of each other, the best decision is to defer, gather
    more information, or choose the cheapest option.

    Based on the concept from superforecasting: know the limits of your
    knowledge. If you can't distinguish signal from noise, saying "I don't
    know" is the most honest and often the most profitable answer.
    """

    DEFAULT_MIN_SPREAD_RATIO = 0.5
    DEFAULT_MIN_STN = 1.5
    DEFAULT_DEFER_CONFIDENCE = 0.6

    @staticmethod
    def evaluate(
        mc_results: dict[str, Statistics],
        factors: list[Factor],
        min_spread_ratio: float = DEFAULT_MIN_SPREAD_RATIO,
        min_signal_to_noise: float = DEFAULT_MIN_STN,
    ) -> ThresholdVerdict:
        if not mc_results:
            return ThresholdVerdict(
                should_decide=False, signal_strength=0.0, noise_level=0.0,
                signal_to_noise=0.0, max_spread=0.0, min_meaningful_gap=0.0,
                winning_option="", confidence_in_winner=0.0,
                verdict="no_data", reasoning="No results to evaluate",
            )

        sorted_opts = sorted(mc_results.items(), key=lambda x: x[1].mean_score, reverse=True)
        top_name, top_stats = sorted_opts[0]
        runner_name = sorted_opts[1][0] if len(sorted_opts) > 1 else None
        runner_stats = sorted_opts[1][1] if len(sorted_opts) > 1 else None

        all_means = np.array([s.mean_score for s in mc_results.values()])
        all_stds = np.array([s.std_dev for s in mc_results.values()])

        signal_strength = float(np.max(all_means) - np.min(all_means))
        noise_level = float(np.mean(all_stds))
        signal_to_noise = signal_strength / (noise_level + 1e-9)
        max_spread = float(np.max(all_means) - np.min(all_means))

        gap_means = sorted([s.mean_score for s in mc_results.values()], reverse=True)
        meaningful_gap = gap_means[0] - gap_means[1] if len(gap_means) > 1 else gap_means[0]

        winner_p95 = top_stats.percentile_95
        winner_p5 = top_stats.percentile_5
        runner_p95 = runner_stats.percentile_95 if runner_stats else 0.0
        runner_p5 = runner_stats.percentile_5 if runner_stats else 0.0

        distributions_overlap = max(0, min(winner_p95, runner_p95) - max(winner_p5, runner_p5)) if runner_stats else 0.0
        overlap_ratio = distributions_overlap / (max_spread + 1e-9)

        if signal_to_noise >= min_signal_to_noise and overlap_ratio < 0.3:
            confidence = min(0.95, 0.5 + signal_to_noise * 0.15)
            verdict = "decide"
            reasoning = (
                f"Strong signal (S/N={signal_to_noise:.1f}, overlap={overlap_ratio:.1%}). "
                f"'{top_name}' is clearly ahead of '{runner_name}'."
            )
        elif signal_to_noise >= min_signal_to_noise * 0.5 and overlap_ratio < 0.6:
            confidence = 0.5 + signal_to_noise * 0.05
            verdict = "decide_with_caution"
            reasoning = (
                f"Moderate signal (S/N={signal_to_noise:.1f}, overlap={overlap_ratio:.1%}). "
                f"'{top_name}' leads but '{runner_name}' is within range."
            )
        else:
            confidence = MinimumActionThreshold.DEFAULT_DEFER_CONFIDENCE
            verdict = "defer"
            reasoning = (
                f"Weak signal (S/N={signal_to_noise:.1f}, overlap={overlap_ratio:.1%}). "
                f"Top options are indistinguishable from noise. Consider gathering more data."
            )

        return ThresholdVerdict(
            should_decide=verdict != "defer",
            signal_strength=signal_strength,
            noise_level=noise_level,
            signal_to_noise=signal_to_noise,
            max_spread=max_spread,
            min_meaningful_gap=meaningful_gap,
            winning_option=top_name,
            confidence_in_winner=confidence,
            verdict=verdict,
            reasoning=reasoning,
        )

    @staticmethod
    def to_dict(result: ThresholdVerdict) -> dict[str, Any]:
        return {
            "should_decide": result.should_decide,
            "signal_strength": result.signal_strength,
            "noise_level": result.noise_level,
            "signal_to_noise": result.signal_to_noise,
            "max_spread": result.max_spread,
            "min_meaningful_gap": result.min_meaningful_gap,
            "winning_option": result.winning_option,
            "confidence_in_winner": result.confidence_in_winner,
            "verdict": result.verdict,
            "reasoning": result.reasoning,
        }
