"""Tests for Monte Carlo standard error calculation and convergence diagnostics.

Under AGENTS.md conventions:
- Tests verify that Monte Carlo runs report standard_error = std / sqrt(N).
- Convergence diagnostic checks if the top two options are statistically separated
  beyond CONVERGENCE_Z * sqrt(se1^2 + se2^2) (roughly 95% confidence level).
- When options are too close given N, converged is False and suggested N > current N.
- When there is only a single option, converged is None.
- UnifiedDecisionFramework includes the convergence diagnostic in run_analysis().
"""

from __future__ import annotations

import math

import pytest

from decision_maker.core.models import DecisionOption, DistributionType, Factor
from decision_maker.core.monte_carlo import MonteCarloEngine
from decision_maker.core.orchestrator import UnifiedDecisionFramework

# Named constants to avoid magic numbers
SMALL_N_SIMULATIONS: int = 100
MODERATE_N_SIMULATIONS: int = 500
CONVERGENCE_SEED: int = 42
FORMULA_TOLERANCE: float = 1e-9


class TestMonteCarloConvergence:
    def test_standard_error_matches_std_over_sqrt_n(self) -> None:
        """Every option must have standard_error populated as std / sqrt(N)."""
        engine = MonteCarloEngine(num_simulations=SMALL_N_SIMULATIONS, seed=CONVERGENCE_SEED)
        factor = Factor(name="Profit", weight=1.0, maximize=True)
        engine.add_factor(factor)

        opt = DecisionOption(name="A")
        opt.add_variable("Profit", DistributionType.NORMAL, 100.0, 15.0)
        engine.add_option(opt)

        results = engine.run()
        stats = results["A"]

        assert stats.standard_error is not None, "standard_error should be computed on MC run"
        expected_se = stats.std_dev / math.sqrt(SMALL_N_SIMULATIONS)
        assert pytest.approx(expected_se, abs=FORMULA_TOLERANCE) == stats.standard_error

    def test_single_option_has_none_convergence(self) -> None:
        """With a single option, there is no competing alternative, so converged is None."""
        engine = MonteCarloEngine(num_simulations=SMALL_N_SIMULATIONS, seed=CONVERGENCE_SEED)
        engine.add_factor(Factor(name="Return", weight=1.0, maximize=True))

        opt = DecisionOption(name="Solo")
        opt.add_variable("Return", DistributionType.NORMAL, 50.0, 5.0)
        engine.add_option(opt)

        engine.run()
        conv = engine.last_convergence

        assert conv["converged"] is None
        assert conv["gap"] is None
        assert conv["threshold"] is None
        assert conv["suggested_num_simulations"] is None

    def test_two_almost_identical_options_fails_convergence(self) -> None:
        """Two options with overlapping distributions at small N cannot be separated.

        The gap between means is smaller than CONVERGENCE_Z * pooled_se, so converged
        must be False and suggested_num_simulations must exceed current N.
        """
        engine = MonteCarloEngine(num_simulations=SMALL_N_SIMULATIONS, seed=CONVERGENCE_SEED)
        engine.add_factor(Factor(name="Score", weight=1.0, maximize=True))

        # Close means with large standard deviation: difference cannot be resolved with N=100
        opt_a = DecisionOption(name="OptionA")
        opt_a.add_variable("Score", DistributionType.NORMAL, 10.0, 10.0)
        opt_b = DecisionOption(name="OptionB")
        opt_b.add_variable("Score", DistributionType.NORMAL, 10.05, 10.0)

        engine.add_option(opt_a)
        engine.add_option(opt_b)

        engine.run()
        conv = engine.last_convergence

        assert conv["converged"] is False
        assert conv["gap"] is not None
        assert conv["threshold"] is not None
        assert conv["gap"] < conv["threshold"]
        assert conv["suggested_num_simulations"] is not None
        assert conv["suggested_num_simulations"] > SMALL_N_SIMULATIONS

    def test_two_very_distinct_options_converges(self) -> None:
        """Two options with widely separated distributions converge cleanly.

        Gap is far larger than CONVERGENCE_Z * pooled_se, so converged is True and
        suggested_num_simulations equals current num_simulations.
        """
        engine = MonteCarloEngine(num_simulations=MODERATE_N_SIMULATIONS, seed=CONVERGENCE_SEED)
        engine.add_factor(Factor(name="Score", weight=1.0, maximize=True))

        # Option A is overwhelmingly better than Option B
        opt_a = DecisionOption(name="Superior")
        opt_a.add_variable("Score", DistributionType.NORMAL, 100.0, 1.0)
        opt_b = DecisionOption(name="Inferior")
        opt_b.add_variable("Score", DistributionType.NORMAL, 10.0, 1.0)

        engine.add_option(opt_a)
        engine.add_option(opt_b)

        engine.run()
        conv = engine.last_convergence

        assert conv["converged"] is True
        assert conv["gap"] is not None
        assert conv["threshold"] is not None
        assert conv["gap"] >= conv["threshold"]
        assert conv["suggested_num_simulations"] == MODERATE_N_SIMULATIONS

    @pytest.mark.asyncio
    async def test_orchestrator_includes_convergence_diagnostic(self) -> None:
        """UnifiedDecisionFramework.run_analysis must expose convergence in its return dict."""
        framework = UnifiedDecisionFramework()
        framework.mc_engine.num_simulations = SMALL_N_SIMULATIONS
        framework.mc_engine.seed = CONVERGENCE_SEED
        framework.mc_engine.add_factor(Factor(name="F1", weight=1.0, maximize=True))

        opt1 = DecisionOption(name="Opt1")
        opt1.add_variable("F1", DistributionType.NORMAL, 80.0, 5.0)
        opt2 = DecisionOption(name="Opt2")
        opt2.add_variable("F1", DistributionType.NORMAL, 20.0, 5.0)

        framework.mc_engine.add_option(opt1)
        framework.mc_engine.add_option(opt2)

        result = await framework.run_analysis(mode="express")

        assert "convergence" in result, "run_analysis result dictionary must include 'convergence' key"
        assert result["convergence"]["converged"] is True
        assert result["convergence"]["suggested_num_simulations"] == SMALL_N_SIMULATIONS
