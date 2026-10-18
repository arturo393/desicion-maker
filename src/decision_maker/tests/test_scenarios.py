"""
Tests for shared scenario drivers, comonotonic coupling, and marginal preservation.

Ensures:
1. Comonotonic coupling produces Spearman rank correlation 1.0 between options sharing a driver.
2. Marginal distributions are strictly preserved (sorted values identical to unsorted draws).
3. Zero-regression: models without drivers produce identical raw_scores given the same seed.
4. Variables with shared drivers are excluded from intra-option Cholesky correlation.
5. engine.drivers() and engine.is_fully_shared() report correct model topologies.
"""

from __future__ import annotations

import numpy as np
import pytest
from scipy.stats import spearmanr

from decision_maker.core.models import DecisionOption, DistributionType, Factor, Statistics
from decision_maker.core.monte_carlo import MonteCarloEngine


def _raw(stats: Statistics, factor: str) -> np.ndarray:
    """The run's samples for one factor; MonteCarloEngine.run() always fills raw_factor_data."""
    assert stats.raw_factor_data is not None
    return stats.raw_factor_data[factor]

CORRELATION_TOLERANCE: float = 1e-4
TEST_SIMULATIONS: int = 2000
TEST_SEED: int = 42


class TestSharedScenarioDrivers:
    def test_shared_driver_produces_spearman_rank_correlation_one(self) -> None:
        """Two options sharing the same risk driver must have Spearman rank correlation 1.0."""
        engine = MonteCarloEngine(num_simulations=TEST_SIMULATIONS, seed=TEST_SEED)
        engine.add_factor(Factor("Market", weight=1.0, maximize=True))

        opt_a = DecisionOption("Option_A")
        # Normal distribution
        opt_a.add_variable("Market", DistributionType.NORMAL, 100.0, 15.0, driver="macro")
        engine.add_option(opt_a)

        opt_b = DecisionOption("Option_B")
        # Uniform distribution (different marginal family and support)
        opt_b.add_variable("Market", DistributionType.UNIFORM, 10.0, 50.0, driver="macro")
        engine.add_option(opt_b)

        results = engine.run(normalize=False)

        samples_a = _raw(results["Option_A"], "Market")
        samples_b = _raw(results["Option_B"], "Market")

        corr, _p = spearmanr(samples_a, samples_b)
        assert pytest.approx(1.0, abs=CORRELATION_TOLERANCE) == corr, (
            f"Expected rank correlation 1.0 under comonotonic driver, got {corr}"
        )

    def test_marginals_preserved_under_driver_coupling(self) -> None:
        """Comonotonic reordering must preserve the exact marginal empirical distribution."""
        engine = MonteCarloEngine(num_simulations=TEST_SIMULATIONS, seed=TEST_SEED)
        engine.add_factor(Factor("Cost", weight=1.0, maximize=False))

        opt = DecisionOption("Project")
        opt.add_variable("Cost", DistributionType.TRIANGULAR, 10.0, 20.0, 50.0, driver="inflation")
        engine.add_option(opt)

        results = engine.run(normalize=False)
        coupled_samples = _raw(results["Project"], "Cost")

        # Sample directly without driver using the exact same generator seed to inspect original draws
        rng = np.random.default_rng(TEST_SEED)
        raw_samples = opt.variables["Cost"].sample(TEST_SIMULATIONS, rng=rng)

        # The empirical marginal distributions must be identical when sorted
        assert np.array_equal(np.sort(coupled_samples), np.sort(raw_samples)), (
            "Comonotonic reordering altered marginal empirical values"
        )

    def test_zero_regression_without_shared_drivers(self) -> None:
        """Models without drivers must produce identical raw_scores to uncoupled Monte Carlo."""
        # Run 1: with standard engine run()
        engine = MonteCarloEngine(num_simulations=TEST_SIMULATIONS, seed=TEST_SEED)
        engine.add_factor(Factor("F1", weight=0.6, maximize=True))
        engine.add_factor(Factor("F2", weight=0.4, maximize=False))

        opt1 = DecisionOption("Opt1")
        opt1.add_variable("F1", DistributionType.NORMAL, 50.0, 5.0)
        opt1.add_variable("F2", DistributionType.UNIFORM, 10.0, 30.0)
        engine.add_option(opt1)

        opt2 = DecisionOption("Opt2")
        opt2.add_variable("F1", DistributionType.NORMAL, 60.0, 10.0)
        opt2.add_variable("F2", DistributionType.UNIFORM, 15.0, 25.0)
        engine.add_option(opt2)

        res_standard = engine.run(normalize=True)

        # Baseline manual draw without calling scenarios logic
        rng_baseline = np.random.default_rng(TEST_SEED)
        s1_f1 = opt1.variables["F1"].sample(TEST_SIMULATIONS, rng=rng_baseline)
        s1_f2 = opt1.variables["F2"].sample(TEST_SIMULATIONS, rng=rng_baseline)
        s2_f1 = opt2.variables["F1"].sample(TEST_SIMULATIONS, rng=rng_baseline)
        s2_f2 = opt2.variables["F2"].sample(TEST_SIMULATIONS, rng=rng_baseline)

        # Check raw factor data matches exactly
        assert np.array_equal(_raw(res_standard["Opt1"], "F1"), s1_f1)
        assert np.array_equal(_raw(res_standard["Opt1"], "F2"), s1_f2)
        assert np.array_equal(_raw(res_standard["Opt2"], "F1"), s2_f1)
        assert np.array_equal(_raw(res_standard["Opt2"], "F2"), s2_f2)

    def test_driver_variables_excluded_from_intra_option_correlation(self) -> None:
        """Variables bound to a driver must be excluded from intra-option correlation.

        If a variable with a driver were included in _apply_correlation, intra-option
        reordering would shuffle its samples and break the inter-option comonotonic
        coupling (Spearman rank correlation = 1.0) with other options sharing that driver.
        """
        # 2 factors: F1 (has shared driver "macro"), F2 (no driver)
        corr_matrix = np.array([
            [1.0, 0.8],
            [0.8, 1.0],
        ])
        engine = MonteCarloEngine(
            num_simulations=TEST_SIMULATIONS,
            correlation_matrix=corr_matrix,
            seed=TEST_SEED,
        )
        engine.add_factor(Factor("F2", weight=0.5, maximize=True))
        engine.add_factor(Factor("F1", weight=0.5, maximize=True))

        opt_a = DecisionOption("A")
        opt_a.add_variable("F2", DistributionType.NORMAL, 20.0, 3.0)
        opt_a.add_variable("F1", DistributionType.NORMAL, 10.0, 2.0, driver="macro")
        engine.add_option(opt_a)

        opt_b = DecisionOption("B")
        opt_b.add_variable("F2", DistributionType.NORMAL, 22.0, 3.5)
        opt_b.add_variable("F1", DistributionType.NORMAL, 12.0, 2.5, driver="macro")
        engine.add_option(opt_b)

        results = engine.run(normalize=False)

        # F1 across A and B must retain rank correlation 1.0 because it was excluded from
        # _apply_correlation. If it were not excluded, intra-option reordering would have
        # destroyed the inter-option coupling.
        f1_a = _raw(results["A"], "F1")
        f1_b = _raw(results["B"], "F1")
        rank_corr_f1, _ = spearmanr(f1_a, f1_b)
        assert pytest.approx(1.0, abs=CORRELATION_TOLERANCE) == rank_corr_f1

    def test_engine_drivers_mapping_and_fully_shared_detection(self) -> None:
        """Verify engine.drivers() dictionary and engine.is_fully_shared() predicate."""
        engine = MonteCarloEngine(num_simulations=100, seed=TEST_SEED)
        engine.add_factor(Factor("F1", weight=0.5, maximize=True))
        engine.add_factor(Factor("F2", weight=0.5, maximize=True))

        opt_a = DecisionOption("A")
        opt_a.add_variable("F1", DistributionType.NORMAL, 10.0, 1.0, driver="risk_1")
        opt_a.add_variable("F2", DistributionType.NORMAL, 20.0, 2.0, driver="risk_2")
        engine.add_option(opt_a)

        opt_b = DecisionOption("B")
        opt_b.add_variable("F1", DistributionType.NORMAL, 11.0, 1.0, driver="risk_1")
        opt_b.add_variable("F2", DistributionType.NORMAL, 21.0, 2.0)  # No driver
        engine.add_option(opt_b)

        drivers = engine.drivers()
        assert "risk_1" in drivers
        assert len(drivers["risk_1"]) == 2
        assert ("A", "F1") in drivers["risk_1"]
        assert ("B", "F1") in drivers["risk_1"]
        assert "risk_2" in drivers
        assert len(drivers["risk_2"]) == 1

        # Not fully shared because opt_b.F2 has no driver
        assert not engine.is_fully_shared()

        # Add driver to opt_b.F2
        opt_b.variables["F2"].driver = "risk_2"
        assert engine.is_fully_shared()
