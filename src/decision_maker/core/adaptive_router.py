"""
Adaptive routing engine: select the right engine suite based on problem complexity.
Usage: from decision_maker.core.adaptive_router import AdaptiveRouter
Does NOT: Run decision algorithms (dispatches to them).
"""

from __future__ import annotations

__all__ = ["AdaptiveRouter", "ProblemProfile"]

import logging
from dataclasses import dataclass

import numpy as np

from decision_maker.core.models import DecisionOption, Factor, Statistics

logger = logging.getLogger(__name__)


@dataclass
class ProblemProfile:
    """Complexity metrics of a decision problem (Parameter Object)."""

    num_options: int
    num_factors: int
    factor_uncertainty: float
    option_diversity: float
    has_correlation: bool
    complexity_score: float
    recommended_mode: str
    recommended_engines: list[str]
    skip_engines: list[str]
    reasoning: str


class AdaptiveRouter:
    """
    Selects the optimal engine suite based on problem complexity.

    Key insight: 24 engines is overkill for simple problems and sometimes
    insufficient for complex ones. The router measures complexity and
    routes to the right subset, saving compute and reducing noise.

    Complexity dimensions:
    1. Number of options (more = harder)
    2. Number of factors (more = harder)
    3. Factor uncertainty (high std/mean = harder)
    4. Option diversity (how different are the options from each other)
    5. Correlation between factors (correlated = harder)
    """

    SIMPLE_THRESHOLD = 0.3
    MODERATE_THRESHOLD = 0.6

    @staticmethod
    def profile(
        options: list[DecisionOption],
        factors: list[Factor],
        mc_results: dict[str, Statistics] | None = None,
        has_correlation: bool = False,
    ) -> ProblemProfile:
        num_options = len(options)
        num_factors = len(factors)

        factor_uncertainty = AdaptiveRouter._compute_factor_uncertainty(mc_results)
        option_diversity = AdaptiveRouter._compute_option_diversity(mc_results)
        complexity = AdaptiveRouter._compute_complexity(
            num_options, num_factors, factor_uncertainty, option_diversity, has_correlation
        )

        if complexity < AdaptiveRouter.SIMPLE_THRESHOLD:
            mode = "express"
            recommended, skip = AdaptiveRouter._simple_engines()
            reasoning = (
                f"Simple problem ({num_options} options, {num_factors} factors, "
                f"uncertainty={factor_uncertainty:.2f}). Express mode is sufficient."
            )
        elif complexity < AdaptiveRouter.MODERATE_THRESHOLD:
            mode = "standard"
            recommended, skip = AdaptiveRouter._moderate_engines()
            reasoning = (
                f"Moderate complexity ({num_options} options, {num_factors} factors, "
                f"uncertainty={factor_uncertainty:.2f}). Standard mode covers the essentials."
            )
        else:
            mode = "advanced"
            recommended, skip = AdaptiveRouter._advanced_engines()
            reasoning = (
                f"High complexity ({num_options} options, {num_factors} factors, "
                f"uncertainty={factor_uncertainty:.2f}, diversity={option_diversity:.2f}). "
                f"Full suite needed."
            )

        return ProblemProfile(
            num_options=num_options,
            num_factors=num_factors,
            factor_uncertainty=factor_uncertainty,
            option_diversity=option_diversity,
            has_correlation=has_correlation,
            complexity_score=complexity,
            recommended_mode=mode,
            recommended_engines=recommended,
            skip_engines=skip,
            reasoning=reasoning,
        )

    @staticmethod
    def _compute_factor_uncertainty(mc_results: dict[str, Statistics] | None) -> float:
        if not mc_results:
            return 0.0
        cv_values = []
        for stats in mc_results.values():
            for fname, fstats in stats.factor_stats.items():
                mean = abs(fstats["mean"])
                std = fstats["std"]
                if mean > 1e-9:
                    cv_values.append(std / mean)
        return float(np.mean(cv_values)) if cv_values else 0.0

    @staticmethod
    def _compute_option_diversity(mc_results: dict[str, Statistics] | None) -> float:
        if not mc_results or len(mc_results) < 2:
            return 0.0
        means = np.array([s.mean_score for s in mc_results.values()])
        stds = np.array([s.std_dev for s in mc_results.values()])
        spread = float(np.std(means)) if len(means) > 1 else 0.0
        avg_std = float(np.mean(stds)) if len(stds) > 0 else 1.0
        return min(spread / (avg_std + 1e-9), 1.0)

    @staticmethod
    def _compute_complexity(
        num_options: int,
        num_factors: int,
        factor_uncertainty: float,
        option_diversity: float,
        has_correlation: bool,
    ) -> float:
        opt_score = min(num_options / 8.0, 1.0) * 0.25
        factor_score = min(num_factors / 10.0, 1.0) * 0.25
        uncertainty_score = min(factor_uncertainty / 1.0, 1.0) * 0.25
        diversity_score = option_diversity * 0.15
        correlation_score = 0.10 if has_correlation else 0.0
        return opt_score + factor_score + uncertainty_score + diversity_score + correlation_score

    @staticmethod
    def _simple_engines() -> tuple[list[str], list[str]]:
        return (
            ["MonteCarlo", "TOPSIS", "Pareto", "DecisionTheory"],
            ["Bayesian", "Genetic", "GameTheory", "ROA", "MLSurrogate",
             "Ergodicity", "Kelly", "Bootstrap", "Portfolio"],
        )

    @staticmethod
    def _moderate_engines() -> tuple[list[str], list[str]]:
        return (
            ["MonteCarlo", "TOPSIS", "Pareto", "DecisionTheory", "Sensitivity",
             "PROMETHEE", "Robust", "Ergodicity", "Kelly", "Antifragile", "Explainability"],
            ["Genetic", "GameTheory", "ROA", "MLSurrogate", "Bootstrap"],
        )

    @staticmethod
    def _advanced_engines() -> tuple[list[str], list[str]]:
        return (
            ["MonteCarlo", "TOPSIS", "Pareto", "DecisionTheory", "Sensitivity",
             "PROMETHEE", "Robust", "Bayesian", "Ergodicity", "Kelly",
             "Antifragile", "Explainability", "Bootstrap", "GameTheory",
             "ROA", "MLSurrogate", "Portfolio", "InformationTheory"],
            [],
        )

    @staticmethod
    def should_skip_engine(engine_name: str, profile: ProblemProfile) -> bool:
        return engine_name in profile.skip_engines

    @staticmethod
    def summary(profile: ProblemProfile) -> str:
        return (
            f"Complexity: {profile.complexity_score:.2f} → {profile.recommended_mode.upper()}\n"
            f"  Options: {profile.num_options}, Factors: {profile.num_factors}\n"
            f"  Uncertainty: {profile.factor_uncertainty:.2f}, Diversity: {profile.option_diversity:.2f}\n"
            f"  Run: {', '.join(profile.recommended_engines[:5])}{'...' if len(profile.recommended_engines) > 5 else ''}\n"
            f"  Skip: {', '.join(profile.skip_engines[:3]) if profile.skip_engines else 'none'}"
        )
