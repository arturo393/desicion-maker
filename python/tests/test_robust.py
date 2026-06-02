import pytest

from python.core.models import Factor, Statistics
from python.core.robust import RobustOptimizer


class TestRobustOptimizer:
    def test_basic_robust_ranking(self):
        results = {
            "A": Statistics("A", 100, 10, 80, 120, 85, 115, 0.9,
                            {"Cost": {"mean": 50}, "Quality": {"mean": 80}}, 85, 80),
            "B": Statistics("B", 120, 15, 70, 160, 80, 150, 0.85,
                            {"Cost": {"mean": 30}, "Quality": {"mean": 95}}, 80, 75),
        }
        factors = [Factor("Cost", 0.5, maximize=False), Factor("Quality", 0.5, maximize=True)]
        result = RobustOptimizer().analyze(results, factors)
        assert "robust_ranking" in result
        assert "dro_scores" in result
        assert result["winner"] is not None

    def test_single_option(self):
        results = {
            "Only": Statistics("Only", 50, 5, 40, 60, 42, 58, 0.8,
                               {"X": {"mean": 10}}, 42, 41),
        }
        factors = [Factor("X", 1.0, maximize=True)]
        result = RobustOptimizer().analyze(results, factors)
        assert result["winner"] == "Only"

    def test_empty_results(self):
        result = RobustOptimizer().analyze({}, [Factor("X", 1.0)])
        assert result == {}

    def test_empty_factors(self):
        results = {
            "A": Statistics("A", 100, 0, 100, 100, 100, 100, 1.0, {}, 100, 100),
        }
        result = RobustOptimizer().analyze(results, [])
        assert result == {}

    def test_custom_epsilon_and_shock(self):
        results = {
            "A": Statistics("A", 100, 10, 80, 120, 85, 115, 0.9,
                            {"X": {"mean": 50}}, 85, 80),
            "B": Statistics("B", 120, 15, 70, 160, 80, 150, 0.85,
                            {"X": {"mean": 30}}, 80, 75),
        }
        factors = [Factor("X", 1.0, maximize=True)]
        result = RobustOptimizer().analyze(results, factors, epsilon=0.01, weight_shock=0.3)
        assert result["winner"] is not None

    def test_all_identical_options(self):
        results = {
            "A": Statistics("A", 100, 0, 100, 100, 100, 100, 1.0,
                            {"X": {"mean": 10}}, 100, 100),
            "B": Statistics("B", 100, 0, 100, 100, 100, 100, 1.0,
                            {"X": {"mean": 10}}, 100, 100),
        }
        factors = [Factor("X", 1.0, maximize=True)]
        result = RobustOptimizer().analyze(results, factors)
        assert result["winner"] is not None
        scores = list(result["dro_scores"].values())
        assert scores[0] == scores[1]
