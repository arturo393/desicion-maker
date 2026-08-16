#!/usr/bin/env python3
"""
Unit Tests for Unified Decision Framework
Issue #3: Comprehensive Utility Testing
"""

import numpy as np
import pytest

from decision_maker.core.models import DecisionOption, DistributionType, Factor, UncertainVariable
from decision_maker.core.monte_carlo import MonteCarloEngine
from decision_maker.core.topsis import TOPSISEngine


class TestDistributions:
    def setup_method(self):
        np.random.seed(42)

    def test_deterministic(self):
        var = UncertainVariable("Const", DistributionType.DETERMINISTIC, [10])
        samples = var.sample(100)
        assert np.all(samples == 10)

    def test_triangular_bug_fix(self):
        var = UncertainVariable("TriBug", DistributionType.TRIANGULAR, [10, 5, 20])
        try:
            samples = var.sample(100)
            assert np.all(samples >= 5)
            assert np.all(samples <= 20)
        except ValueError:
            pytest.fail("Triangular distribution raised ValueError with unordered params")

    def test_normal_stats(self):
        mean, std = 100, 15
        var = UncertainVariable("Norm", DistributionType.NORMAL, [mean, std])
        samples = var.sample(10000)
        assert abs(np.mean(samples) - mean) < 1.0
        assert abs(np.std(samples) - std) < 1.0

    def test_beta_range(self):
        var = UncertainVariable("Beta", DistributionType.BETA, [2, 5])
        samples = var.sample(1000)
        assert np.all((samples >= 0) & (samples <= 1))

    def test_lognormal(self):
        var = UncertainVariable("LogNorm", DistributionType.LOGNORMAL, [0, 0.5])
        samples = var.sample(1000)
        assert np.all(samples > 0)

    def test_gamma(self):
        shape, scale = 2.0, 3.0
        var = UncertainVariable("Gamma", DistributionType.GAMMA, [shape, scale])
        samples = var.sample(10000)
        assert abs(np.mean(samples) - (shape * scale)) < 1.0

    def test_poisson(self):
        lam = 5
        var = UncertainVariable("Pois", DistributionType.POISSON, [lam])
        samples = var.sample(10000)
        assert np.all(samples >= 0)
        assert abs(np.mean(samples) - lam) < 0.5


class TestMonteCarlo:
    def setup_method(self):
        self.engine = MonteCarloEngine(num_simulations=1000)
        np.random.seed(42)

    def test_simple_simulation(self):
        opt = DecisionOption("Safe")
        opt.add_variable("Income", DistributionType.DETERMINISTIC, 100)

        self.engine.add_factor(Factor("Income", 1.0, maximize=True))
        self.engine.add_option(opt)

        results = self.engine.run()
        stats = results["Safe"]

        assert stats.mean_score == 100.0
        assert stats.min_score == 100.0
        assert stats.max_score == 100.0
        assert stats.std_dev == 0.0

    def test_weighted_simulation(self):
        opt = DecisionOption("Project")
        opt.add_variable("Cost", DistributionType.DETERMINISTIC, 50)
        opt.add_variable("Benefit", DistributionType.DETERMINISTIC, 150)

        self.engine.add_factor(Factor("Cost", 0.2, maximize=False))
        self.engine.add_factor(Factor("Benefit", 0.8, maximize=True))
        self.engine.add_option(opt)

        results = self.engine.run()
        stats = results["Project"]

        assert abs(stats.mean_score - 110.0) < 1e-6


class TestTOPSIS:
    def test_ranking(self):
        data = {
            "OptA": {"Price": (100, 100, 100), "Quality": (10, 10, 10)},
            "OptB": {"Price": (200, 200, 200), "Quality": (20, 20, 20)},
            "OptC": {"Price": (150, 150, 150), "Quality": (15, 15, 15)},
        }
        weights = [0.5, 0.5]
        maximize = [False, True]

        engine = TOPSISEngine()
        scores = engine.analyze(data, weights, maximize)

        assert len(scores) == 3
        assert scores.idxmax() == scores.index[0]

