import numpy as np
import pytest

from decision_maker.core.adaptive_router import AdaptiveRouter, ProblemProfile
from decision_maker.core.models import DecisionOption, DistributionType, Factor, Statistics


class TestAdaptiveRouter:
    def _make_stats(self, name: str, mean: float, std: float) -> Statistics:
        return Statistics(
            option_name=name,
            mean_score=mean,
            std_dev=std,
            min_score=mean - 2 * std,
            max_score=mean + 2 * std,
            percentile_5=mean - 1.645 * std,
            percentile_95=mean + 1.645 * std,
            success_rate=0.7,
            factor_stats={"F1": {"mean": mean, "std": std, "p5": mean - std, "p95": mean + std}},
            var_95=mean - 1.645 * std,
            cvar_95=mean - 2 * std,
        )

    def test_simple_problem(self):
        options = [DecisionOption("A"), DecisionOption("B")]
        factors = [Factor("F1", 1.0, maximize=True)]
        profile = AdaptiveRouter.profile(options, factors)
        assert profile.recommended_mode == "express"
        assert "MonteCarlo" in profile.recommended_engines
        assert profile.complexity_score < AdaptiveRouter.SIMPLE_THRESHOLD

    def test_moderate_problem(self):
        options = [DecisionOption(f"O{i}") for i in range(5)]
        factors = [Factor(f"F{i}", 1.0, maximize=True) for i in range(6)]
        profile = AdaptiveRouter.profile(options, factors)
        assert profile.recommended_mode in ("express", "standard")

    def test_complex_problem(self):
        options = [DecisionOption(f"O{i}") for i in range(10)]
        factors = [Factor(f"F{i}", 1.0, maximize=True) for i in range(12)]
        mc_results = {
            f"O{i}": self._make_stats(f"O{i}", float(i), 2.0)
            for i in range(10)
        }
        profile = AdaptiveRouter.profile(options, factors, mc_results=mc_results, has_correlation=True)
        assert profile.recommended_mode == "advanced"
        assert profile.complexity_score > AdaptiveRouter.MODERATE_THRESHOLD

    def test_should_skip_engine(self):
        profile = ProblemProfile(
            num_options=3, num_factors=2, factor_uncertainty=0.1,
            option_diversity=0.1, has_correlation=False, complexity_score=0.2,
            recommended_mode="express",
            recommended_engines=["MonteCarlo", "TOPSIS"],
            skip_engines=["Bayesian", "Genetic"],
            reasoning="simple",
        )
        assert AdaptiveRouter.should_skip_engine("Bayesian", profile) is True
        assert AdaptiveRouter.should_skip_engine("MonteCarlo", profile) is False

    def test_empty_options(self):
        profile = AdaptiveRouter.profile([], [])
        assert profile.num_options == 0
        assert profile.recommended_mode == "express"

    def test_summary_output(self):
        options = [DecisionOption("A"), DecisionOption("B")]
        factors = [Factor("F1", 1.0, maximize=True)]
        profile = AdaptiveRouter.profile(options, factors)
        summary = AdaptiveRouter.summary(profile)
        assert "Complexity:" in summary
        assert "express" in summary.lower()

    def test_option_diversity(self):
        mc_similar = {
            "A": self._make_stats("A", 5.0, 1.0),
            "B": self._make_stats("B", 5.1, 1.0),
        }
        mc_diverse = {
            "A": self._make_stats("A", 1.0, 1.0),
            "B": self._make_stats("B", 10.0, 1.0),
        }
        div_similar = AdaptiveRouter._compute_option_diversity(mc_similar)
        div_diverse = AdaptiveRouter._compute_option_diversity(mc_diverse)
        assert div_diverse > div_similar

    def test_factor_uncertainty(self):
        mc_low = {
            "A": Statistics(
                option_name="A", mean_score=5.0, std_dev=0.1,
                min_score=4.8, max_score=5.2, percentile_5=4.9, percentile_95=5.1,
                success_rate=0.9, factor_stats={"F": {"mean": 100, "std": 1, "p5": 99, "p95": 101}},
                var_95=4.9, cvar_95=4.8,
            ),
        }
        mc_high = {
            "A": Statistics(
                option_name="A", mean_score=5.0, std_dev=3.0,
                min_score=0.0, max_score=10.0, percentile_5=1.0, percentile_95=9.0,
                success_rate=0.5, factor_stats={"F": {"mean": 5, "std": 4, "p5": 1, "p95": 9}},
                var_95=1.0, cvar_95=0.5,
            ),
        }
        unc_low = AdaptiveRouter._compute_factor_uncertainty(mc_low)
        unc_high = AdaptiveRouter._compute_factor_uncertainty(mc_high)
        assert unc_high > unc_low

    def test_with_correlation_increases_complexity(self):
        options = [DecisionOption(f"O{i}") for i in range(4)]
        factors = [Factor(f"F{i}", 1.0, maximize=True) for i in range(4)]
        p_no_corr = AdaptiveRouter.profile(options, factors, has_correlation=False)
        p_corr = AdaptiveRouter.profile(options, factors, has_correlation=True)
        assert p_corr.complexity_score > p_no_corr.complexity_score
