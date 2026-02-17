#!/usr/bin/env python3
"""
Unit Tests for Unified Decision Framework
Issue #3: Comprehensive Utility Testing
"""

import sys
import unittest
import numpy as np
import pandas as pd
from unittest.mock import MagicMock

import os

# Add 'python' directory to path to allow imports from core
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from core.unified_decision_framework import (
    DistributionType,
    UncertainVariable,
    DecisionOption,
    Factor,
    MonteCarloEngine,
    TOPSISEngine,
    UnifiedDecisionFramework
)

class TestDistributions(unittest.TestCase):
    def setUp(self):
        # Set seed for reproducibility
        np.random.seed(42)

    def test_deterministic(self):
        var = UncertainVariable("Const", DistributionType.DETERMINISTIC, [10])
        samples = var.sample(100)
        self.assertTrue(np.all(samples == 10))

    def test_triangular_bug_fix(self):
        """Verify Triangular dist handles unordered params correctly"""
        # Bug case: left=10, mode=5, right=20 (mode < left)
        # Should be auto-sorted to: 5, 10, 20
        var = UncertainVariable("TriBug", DistributionType.TRIANGULAR, [10, 5, 20])
        try:
            samples = var.sample(100)
            self.assertTrue(np.all(samples >= 5))
            self.assertTrue(np.all(samples <= 20))
        except ValueError:
            self.fail("Triangular distribution raised ValueError with unordered params")

    def test_normal_stats(self):
        """Verify Normal distribution mean and stddev"""
        mean, std = 100, 15
        var = UncertainVariable("Norm", DistributionType.NORMAL, [mean, std])
        samples = var.sample(10000)
        
        self.assertAlmostEqual(np.mean(samples), mean, delta=1.0)
        self.assertAlmostEqual(np.std(samples), std, delta=1.0)

    def test_beta_range(self):
        """Verify Beta distribution stays within [0, 1]"""
        var = UncertainVariable("Beta", DistributionType.BETA, [2, 5])
        samples = var.sample(1000)
        self.assertTrue(np.all((samples >= 0) & (samples <= 1)))

    def test_lognormal(self):
        """Verify LogNormal is always positive"""
        var = UncertainVariable("LogNorm", DistributionType.LOGNORMAL, [0, 0.5])
        samples = var.sample(1000)
        self.assertTrue(np.all(samples > 0))

    def test_gamma(self):
        """Verify Gamma mean = shape * scale"""
        shape, scale = 2.0, 3.0
        var = UncertainVariable("Gamma", DistributionType.GAMMA, [shape, scale])
        samples = var.sample(10000)
        self.assertAlmostEqual(np.mean(samples), shape * scale, delta=1.0)

    def test_poisson(self):
        """Verify Poisson handles integer counts"""
        lam = 5
        var = UncertainVariable("Pois", DistributionType.POISSON, [lam])
        samples = var.sample(10000)
        self.assertTrue(np.all(samples >= 0))
        self.assertAlmostEqual(np.mean(samples), lam, delta=0.5)

class TestMonteCarlo(unittest.TestCase):
    def setUp(self):
        self.engine = MonteCarloEngine(num_simulations=1000)
        np.random.seed(42)

    def test_simple_simulation(self):
        # Option A: Deterministic 100
        opt = DecisionOption("Safe")
        opt.add_variable("Income", DistributionType.DETERMINISTIC, 100)
        
        # Factor: Income (weight 1.0)
        self.engine.add_factor(Factor("Income", 1.0, maximize=True))
        self.engine.add_option(opt)
        
        results = self.engine.run()
        stats = results["Safe"]
        
        self.assertEqual(stats.mean_score, 100.0)
        self.assertEqual(stats.min_score, 100.0)
        self.assertEqual(stats.max_score, 100.0)
        self.assertEqual(stats.std_dev, 0.0)

    def test_weighted_simulation(self):
        # Option B: Cost (50) and Benefit (150)
        # Net = Benefit*0.8 - Cost*0.2
        #     = 150*0.8 - 50*0.2 = 120 - 10 = 110
        opt = DecisionOption("Project")
        opt.add_variable("Cost", DistributionType.DETERMINISTIC, 50)
        opt.add_variable("Benefit", DistributionType.DETERMINISTIC, 150)
        
        self.engine.add_factor(Factor("Cost", 0.2, maximize=False))
        self.engine.add_factor(Factor("Benefit", 0.8, maximize=True))
        self.engine.add_option(opt)
        
        results = self.engine.run()
        stats = results["Project"]
        
        self.assertAlmostEqual(stats.mean_score, 110.0)

class TestTOPSIS(unittest.TestCase):
    def test_ranking(self):
        # Simple Decision Matrix
        #       Price (min)  Quality (max)
        # OptA: 100          10
        # OptB: 200          20
        # OptC: 150          15
        
        data = {
            "OptA": [100, 10],
            "OptB": [200, 20],
            "OptC": [150, 15]
        }
        df = pd.DataFrame.from_dict(data, orient='index', columns=["Price", "Quality"])
        
        # Weights equal, Price minimizes, Quality maximizes
        weights = [0.5, 0.5]
        maximize = [False, True]
        
        engine = TOPSISEngine()
        scores = engine.analyze(df, weights, maximize)
        
        # OptA is cheapest, OptB is highest quality.
        # Verify scores exist and are properly sorted
        self.assertEqual(len(scores), 3)
        self.assertEqual(scores.idxmax(), scores.index[0]) # First in sorted series is best

if __name__ == '__main__':
    unittest.main()
