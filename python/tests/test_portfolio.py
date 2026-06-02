import numpy as np
import pytest

from python.core.models import Statistics
from python.core.portfolio import PortfolioOptimizer


@pytest.fixture
def two_options():
    np.random.seed(42)
    n = 500
    a_scores = np.random.normal(0.7, 0.1, n)
    b_scores = np.random.normal(0.5, 0.2, n)
    return {
        "SafeA": Statistics("SafeA", 0.7, 0.1, 0.4, 0.95, 0.53, 0.87, 0.95,
                           {"X": {"mean": 10}}, 0.53, 0.48, raw_scores=a_scores),
        "RiskyB": Statistics("RiskyB", 0.5, 0.2, 0.0, 0.98, 0.17, 0.83, 0.6,
                           {"X": {"mean": 10}}, 0.17, 0.12, raw_scores=b_scores),
    }


class TestPortfolioOptimizer:
    def test_optimize_returns_allocation(self, two_options):
        result = PortfolioOptimizer.optimize(two_options)
        assert "allocations" in result
        assert abs(sum(result["allocations"].values()) - 1.0) < 1e-6

    def test_optimize_single_option(self):
        stats = Statistics("Only", 0.5, 0.1, 0.3, 0.7, 0.4, 0.6, 0.8,
                          {"X": {"mean": 5}}, 0.4, 0.35)
        result = PortfolioOptimizer.optimize({"Only": stats})
        assert result["allocations"]["Only"] == 1.0

    def test_optimize_empty(self):
        result = PortfolioOptimizer.optimize({})
        assert "error" in result

    def test_optimize_with_budget(self, two_options):
        result = PortfolioOptimizer.optimize(two_options, budget=100)
        assert abs(sum(result["allocations"].values()) - 100) < 1e-6

    def test_sharpe_ratio_returned(self, two_options):
        result = PortfolioOptimizer.optimize(two_options)
        assert "sharpe_ratio" in result
        assert result["sharpe_ratio"] >= 0

    def test_diversification_ratio(self, two_options):
        result = PortfolioOptimizer.optimize(two_options)
        assert "diversification_ratio" in result
        assert result["diversification_ratio"] >= 0

    def test_efficient_frontier(self, two_options):
        result = PortfolioOptimizer.optimize(two_options)
        assert "efficient_frontier" in result
        assert len(result["efficient_frontier"]) > 0

    def test_equal_weight(self, two_options):
        result = PortfolioOptimizer.equal_weight(two_options)
        assert abs(result["SafeA"] - 0.5) < 1e-6
        assert abs(result["RiskyB"] - 0.5) < 1e-6

    def test_three_options(self):
        np.random.seed(42)
        n = 500
        res = {}
        for name, mean, std in [("A", 0.8, 0.1), ("B", 0.6, 0.15), ("C", 0.4, 0.25)]:
            scores = np.random.normal(mean, std, n)
            res[name] = Statistics(name, mean, std, 0, 1, 0, 1, 0.5,
                                  {"X": {"mean": 5}}, 0, 0, raw_scores=scores)
        result = PortfolioOptimizer.optimize(res)
        assert abs(sum(result["allocations"].values()) - 1.0) < 1e-6
