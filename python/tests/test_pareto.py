import pytest

from python.core.models import Factor, Statistics
from python.core.pareto import ParetoEngine


class TestParetoEngine:
    def test_pareto_efficient(self):
        results = {
            "A": Statistics("A", 100, 0, 100, 100, 100, 100, 1.0, {"Cost": {"mean": 50}, "Quality": {"mean": 80}}, 100, 100),
            "B": Statistics("B", 120, 0, 120, 120, 120, 120, 1.0, {"Cost": {"mean": 40}, "Quality": {"mean": 90}}, 120, 120),
        }
        factors = [Factor("Cost", 0.5, maximize=False), Factor("Quality", 0.5, maximize=True)]
        result = ParetoEngine.analyze(results, factors)
        assert "B" in result["efficient_frontier"]
        assert len(result["dominated_options"]) > 0

    def test_non_dominated(self):
        results = {
            "A": Statistics("A", 100, 0, 100, 100, 100, 100, 1.0, {"X": {"mean": 10}, "Y": {"mean": 1}}, 100, 100),
            "B": Statistics("B", 200, 0, 200, 200, 200, 200, 1.0, {"X": {"mean": 1}, "Y": {"mean": 10}}, 200, 200),
        }
        factors = [Factor("X", 0.5, maximize=True), Factor("Y", 0.5, maximize=True)]
        result = ParetoEngine.analyze(results, factors)
        assert len(result["efficient_frontier"]) == 2

    def test_single_option(self):
        results = {
            "Only": Statistics("Only", 100, 0, 100, 100, 100, 100, 1.0, {"X": {"mean": 10}}, 100, 100),
        }
        factors = [Factor("X", 1.0, maximize=True)]
        result = ParetoEngine.analyze(results, factors)
        assert result["efficient_frontier"] == ["Only"]
        assert result["dominated_options"] == []

    def test_empty_results(self):
        result = ParetoEngine.analyze({}, [Factor("X", 1.0, maximize=True)])
        assert result["efficient_frontier"] == []
        assert result["dominated_options"] == []

    def test_all_equal(self):
        results = {
            "A": Statistics("A", 100, 0, 100, 100, 100, 100, 1.0, {"X": {"mean": 10}}, 100, 100),
            "B": Statistics("B", 100, 0, 100, 100, 100, 100, 1.0, {"X": {"mean": 10}}, 100, 100),
        }
        factors = [Factor("X", 1.0, maximize=True)]
        result = ParetoEngine.analyze(results, factors)
        assert len(result["efficient_frontier"]) == 2

    def test_missing_factor_in_stats_defaults_to_zero(self):
        results = {
            "A": Statistics("A", 100, 0, 100, 100, 100, 100, 1.0, {"X": {"mean": 10}}, 100, 100),
            "B": Statistics("B", 100, 0, 100, 100, 100, 100, 1.0, {}, 100, 100),
        }
        factors = [Factor("X", 1.0, maximize=True)]
        result = ParetoEngine.analyze(results, factors)
        assert "A" in result["efficient_frontier"]

    def test_all_minimize_factors(self):
        results = {
            "A": Statistics("A", 100, 0, 100, 100, 100, 100, 1.0, {"Cost": {"mean": 10}}, 100, 100),
            "B": Statistics("B", 100, 0, 100, 100, 100, 100, 1.0, {"Cost": {"mean": 20}}, 100, 100),
        }
        factors = [Factor("Cost", 1.0, maximize=False)]
        result = ParetoEngine.analyze(results, factors)
        assert "A" in result["efficient_frontier"]  # A has lower cost (better)

    def test_three_options_complex_dominance(self):
        results = {
            "A": Statistics("A", 100, 0, 100, 100, 100, 100, 1.0, {"X": {"mean": 10}, "Y": {"mean": 1}}, 100, 100),
            "B": Statistics("B", 100, 0, 100, 100, 100, 100, 1.0, {"X": {"mean": 8}, "Y": {"mean": 8}}, 100, 100),
            "C": Statistics("C", 100, 0, 100, 100, 100, 100, 1.0, {"X": {"mean": 1}, "Y": {"mean": 10}}, 100, 100),
        }
        factors = [Factor("X", 0.5, maximize=True), Factor("Y", 0.5, maximize=True)]
        result = ParetoEngine.analyze(results, factors)
        assert len(result["efficient_frontier"]) == 3  # No single option dominates
