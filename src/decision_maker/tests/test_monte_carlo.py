import math

import numpy as np
import pytest

from decision_maker.core.models import DecisionOption, DistributionType, Factor
from decision_maker.core.monte_carlo import MonteCarloEngine


class TestMonteCarloEngine:
    def test_simple_deterministic(self):
        engine = MonteCarloEngine(num_simulations=100)
        opt = DecisionOption("Safe")
        opt.add_variable("Income", DistributionType.DETERMINISTIC, 100)
        engine.add_factor(Factor("Income", 1.0, maximize=True))
        engine.add_option(opt)

        results = engine.run()
        stats = results["Safe"]
        assert stats.mean_score == 1.0
        assert stats.min_score == 1.0
        assert stats.max_score == 1.0
        assert stats.std_dev == 0.0

    def test_weighted_simulation(self):
        engine = MonteCarloEngine(num_simulations=100)
        opt = DecisionOption("Project")
        opt.add_variable("Cost", DistributionType.DETERMINISTIC, 50)
        opt.add_variable("Benefit", DistributionType.DETERMINISTIC, 150)
        engine.add_factor(Factor("Cost", 0.2, maximize=False))
        engine.add_factor(Factor("Benefit", 0.8, maximize=True))
        engine.add_option(opt)

        results = engine.run()
        stats = results["Project"]
        assert math.isclose(stats.mean_score, 0.8, rel_tol=1e-9)

    def test_multiple_options(self):
        engine = MonteCarloEngine(num_simulations=100)
        opt_a = DecisionOption("A")
        opt_a.add_variable("X", DistributionType.DETERMINISTIC, 10)
        opt_b = DecisionOption("B")
        opt_b.add_variable("X", DistributionType.DETERMINISTIC, 20)
        engine.add_factor(Factor("X", 1.0, maximize=True))
        engine.add_option(opt_a)
        engine.add_option(opt_b)

        results = engine.run()
        assert results["A"].mean_score == 0.0
        assert results["B"].mean_score == 1.0

    def test_minimize_factor(self):
        engine = MonteCarloEngine(num_simulations=100)
        opt = DecisionOption("CostCenter")
        opt.add_variable("Expense", DistributionType.DETERMINISTIC, 100)
        engine.add_factor(Factor("Expense", 1.0, maximize=False))
        engine.add_option(opt)

        results = engine.run()
        assert results["CostCenter"].mean_score == 0.0

    def test_all_distributions(self):
        engine = MonteCarloEngine(num_simulations=1000)
        opt = DecisionOption("AllDist")
        opt.add_variable("D", DistributionType.DETERMINISTIC, 5)
        opt.add_variable("N", DistributionType.NORMAL, 0, 1)
        opt.add_variable("U", DistributionType.UNIFORM, 0, 10)
        opt.add_variable("T", DistributionType.TRIANGULAR, 1, 5, 9)
        opt.add_variable("B", DistributionType.BERNOULLI, 0.5)
        opt.add_variable("E", DistributionType.EXPONENTIAL, 1)
        opt.add_variable("Beta", DistributionType.BETA, 2, 5)
        opt.add_variable("LN", DistributionType.LOGNORMAL, 0, 0.5)
        opt.add_variable("G", DistributionType.GAMMA, 2, 3)
        opt.add_variable("P", DistributionType.POISSON, 5)
        engine.add_factor(Factor("D", 0.1, maximize=True))
        engine.add_factor(Factor("N", 0.1, maximize=True))
        engine.add_factor(Factor("U", 0.1, maximize=True))
        engine.add_factor(Factor("T", 0.1, maximize=True))
        engine.add_factor(Factor("B", 0.1, maximize=True))
        engine.add_factor(Factor("E", 0.1, maximize=True))
        engine.add_factor(Factor("Beta", 0.1, maximize=True))
        engine.add_factor(Factor("LN", 0.1, maximize=True))
        engine.add_factor(Factor("G", 0.1, maximize=True))
        engine.add_factor(Factor("P", 0.1, maximize=True))
        engine.add_option(opt)

        results = engine.run()
        assert "AllDist" in results
        stats = results["AllDist"]
        assert stats.mean_score != 0
        assert stats.std_dev > 0

    def test_empty_options(self):
        engine = MonteCarloEngine(num_simulations=100)
        engine.add_factor(Factor("X", 1.0, maximize=True))
        results = engine.run()
        assert results == {}

    def test_empty_factors(self):
        engine = MonteCarloEngine(num_simulations=100)
        opt = DecisionOption("A")
        opt.add_variable("X", DistributionType.DETERMINISTIC, 10)
        engine.add_option(opt)
        results = engine.run()
        assert results == {}

    def test_zero_simulations_raises(self):
        with pytest.raises(ValueError, match="num_simulations must be >= 1"):
            MonteCarloEngine(num_simulations=0)

    def test_negative_weights(self):
        import pytest
        from pydantic import ValidationError
        engine = MonteCarloEngine(num_simulations=100)
        opt = DecisionOption("Weird")
        opt.add_variable("X", DistributionType.DETERMINISTIC, 100)
        with pytest.raises(ValidationError):
            engine.add_factor(Factor("X", -0.5, maximize=True))

    def test_stats_structure(self):
        engine = MonteCarloEngine(num_simulations=1000)
        opt = DecisionOption("Stats")
        opt.add_variable("A", DistributionType.NORMAL, 50, 10)
        opt.add_variable("B", DistributionType.UNIFORM, 0, 100)
        engine.add_factor(Factor("A", 0.5, maximize=True))
        engine.add_factor(Factor("B", 0.5, maximize=True))
        engine.add_option(opt)

        results = engine.run()
        stats = results["Stats"]
        assert stats.option_name == "Stats"
        assert stats.min_score <= stats.mean_score <= stats.max_score
        assert stats.percentile_5 <= stats.percentile_95
        assert stats.cvar_95 <= stats.var_95
        assert 0 <= stats.success_rate <= 1
        assert "A" in stats.factor_stats
        assert "B" in stats.factor_stats
        for _fname, fstats in stats.factor_stats.items():
            assert "mean" in fstats
            assert "std" in fstats
            assert "p5" in fstats
            assert "p95" in fstats

    def test_duplicate_option_name_overwrites(self):
        engine = MonteCarloEngine(num_simulations=10)
        opt_a = DecisionOption("Same")
        opt_a.add_variable("X", DistributionType.DETERMINISTIC, 10)
        opt_b = DecisionOption("Same")
        opt_b.add_variable("X", DistributionType.DETERMINISTIC, 20)
        engine.add_factor(Factor("X", 1.0, maximize=True))
        engine.add_option(opt_a)
        engine.add_option(opt_b)
        results = engine.run()
        assert len(results) == 1

    def test_option_with_missing_variable(self):
        engine = MonteCarloEngine(num_simulations=10)
        opt = DecisionOption("Partial")
        opt.add_variable("A", DistributionType.DETERMINISTIC, 100)
        engine.add_factor(Factor("A", 0.5, maximize=True))
        engine.add_factor(Factor("B", 0.5, maximize=True))
        engine.add_option(opt)
        results = engine.run()
        assert results["Partial"].mean_score == 0.5

    def test_factor_with_zero_weight(self):
        import pytest
        from pydantic import ValidationError
        engine = MonteCarloEngine(num_simulations=10)
        opt = DecisionOption("ZeroWeight")
        opt.add_variable("X", DistributionType.DETERMINISTIC, 100)
        with pytest.raises(ValidationError):
            engine.add_factor(Factor("X", 0.0, maximize=True))

    def test_weight_sum_zero(self):
        engine = MonteCarloEngine(num_simulations=10)
        opt = DecisionOption("CancelOut")
        opt.add_variable("A", DistributionType.DETERMINISTIC, 100)
        opt.add_variable("B", DistributionType.DETERMINISTIC, 100)
        engine.add_factor(Factor("A", 0.5, maximize=True))
        engine.add_factor(Factor("B", 0.5, maximize=False))
        engine.add_option(opt)
        results = engine.run()
        assert results["CancelOut"].mean_score == 0.5

    def test_option_with_no_variables(self):
        engine = MonteCarloEngine(num_simulations=10)
        opt = DecisionOption("Empty", "no vars")
        engine.add_factor(Factor("X", 1.0, maximize=True))
        engine.add_option(opt)
        results = engine.run()
        assert results["Empty"].mean_score == 0.0

    def test_single_simulation(self):
        engine = MonteCarloEngine(num_simulations=1)
        opt = DecisionOption("OnlyOne")
        opt.add_variable("X", DistributionType.DETERMINISTIC, 42)
        engine.add_factor(Factor("X", 1.0, maximize=True))
        engine.add_option(opt)
        results = engine.run()
        assert results["OnlyOne"].mean_score == 1.0

    def test_nan_params_in_variable(self):
        engine = MonteCarloEngine(num_simulations=100)
        opt = DecisionOption("NaN")
        opt.add_variable("X", DistributionType.NORMAL, float("nan"), float("nan"))
        engine.add_factor(Factor("X", 1.0, maximize=True))
        engine.add_option(opt)
        results = engine.run()
        assert np.isfinite(results["NaN"].mean_score)

    def test_correlation_matrix_not_applied_with_single_factor(self):
        engine = MonteCarloEngine(num_simulations=1000, correlation_matrix=np.eye(1))
        opt = DecisionOption("A")
        opt.add_variable("X", DistributionType.NORMAL, 0, 1)
        engine.add_factor(Factor("X", 1.0, maximize=True))
        engine.add_option(opt)
        results = engine.run()
        assert "A" in results

    def test_correlation_matrix_applied(self):
        corr = np.array([[1.0, 0.8], [0.8, 1.0]])
        engine = MonteCarloEngine(num_simulations=10000, correlation_matrix=corr)
        opt = DecisionOption("A")
        opt.add_variable("X", DistributionType.NORMAL, 0, 1)
        opt.add_variable("Y", DistributionType.NORMAL, 0, 1)
        engine.add_factor(Factor("X", 0.5, maximize=True))
        engine.add_factor(Factor("Y", 0.5, maximize=True))
        engine.add_option(opt)
        results = engine.run()
        assert "A" in results
        assert np.isfinite(results["A"].mean_score)

    def test_correlation_matrix_wrong_shape_skipped(self):
        corr = np.array([[1.0, 0.8, 0.5], [0.8, 1.0, 0.5], [0.5, 0.5, 1.0]])
        engine = MonteCarloEngine(num_simulations=1000, correlation_matrix=corr)
        opt = DecisionOption("A")
        opt.add_variable("X", DistributionType.NORMAL, 0, 1)
        opt.add_variable("Y", DistributionType.NORMAL, 0, 1)
        engine.add_factor(Factor("X", 0.5, maximize=True))
        engine.add_factor(Factor("Y", 0.5, maximize=True))
        engine.add_option(opt)
        results = engine.run()
        assert "A" in results

    def test_correlation_matrix_not_positive_definite_skipped(self):
        corr = np.array([[1.0, 1.5], [1.5, 1.0]])
        engine = MonteCarloEngine(num_simulations=1000, correlation_matrix=corr)
        opt = DecisionOption("A")
        opt.add_variable("X", DistributionType.NORMAL, 0, 1)
        opt.add_variable("Y", DistributionType.NORMAL, 0, 1)
        engine.add_factor(Factor("X", 0.5, maximize=True))
        engine.add_factor(Factor("Y", 0.5, maximize=True))
        engine.add_option(opt)
        results = engine.run()
        assert "A" in results

    def test_correlation_matrix_none_skips_correlation(self):
        engine = MonteCarloEngine(num_simulations=100)
        opt = DecisionOption("A")
        opt.add_variable("X", DistributionType.DETERMINISTIC, 42)
        engine.add_factor(Factor("X", 1.0, maximize=True))
        engine.add_option(opt)
        results = engine.run()
        assert results["A"].mean_score == 1.0

    def test_engine_runs_without_rust_module(self, monkeypatch):
        """The Monte Carlo engine must work when the Rust extension is absent."""
        import builtins
        import importlib
        import sys

        real_import = builtins.__import__

        def fake_import(name, *args, **kwargs):
            if name == "decision_maker_core":
                raise ImportError("No module named decision_maker_core")
            return real_import(name, *args, **kwargs)

        monkeypatch.setattr(builtins, "__import__", fake_import)
        monkeypatch.setitem(sys.modules, "decision_maker_core", None)
        sys.modules.pop("decision_maker.core.monte_carlo", None)

        module = importlib.import_module("decision_maker.core.monte_carlo")
        assert module.RustMonteCarloEngine is None

        engine = module.MonteCarloEngine(num_simulations=100)
        opt = DecisionOption("Safe")
        opt.add_variable("Income", DistributionType.DETERMINISTIC, 100)
        engine.add_factor(Factor("Income", 1.0, maximize=True))
        engine.add_option(opt)

        results = engine.run()
        assert results["Safe"].mean_score == 1.0
