import pytest

from python.core.models import Factor, Statistics
from python.core.sensitivity import SensitivityEngine


class TestSensitivityEngine:
    def test_stable_decision(self):
        results = {
            "A": Statistics("A", 150, 10, 130, 170, 135, 165, 1.0, {"Cost": {"mean": 50}, "Quality": {"mean": 90}}, 135, 132),
            "B": Statistics("B", 100, 10, 80, 120, 85, 115, 0.8, {"Cost": {"mean": 80}, "Quality": {"mean": 60}}, 85, 82),
        }
        factors = [Factor("Cost", 0.3, maximize=False), Factor("Quality", 0.7, maximize=True)]
        result = SensitivityEngine.analyze(results, factors)
        assert result["robustness_score"] == 1.0
        assert result["weight_changes"] == []
        assert result["score_changes"] == []

    def test_empty_results(self):
        result = SensitivityEngine.analyze({}, [Factor("X", 1.0)])
        assert result["robustness_score"] == 1.0
        assert result["base_winner"] is None

    def test_empty_factors(self):
        result = SensitivityEngine.analyze(
            {"A": Statistics("A", 100, 0, 100, 100, 100, 100, 1.0, {}, 100, 100)},
            [],
        )
        assert result["robustness_score"] == 1.0

    def test_equal_scores_all_stable(self):
        results = {
            "A": Statistics("A", 100, 0, 100, 100, 100, 100, 1.0, {"X": {"mean": 50}}, 100, 100),
            "B": Statistics("B", 100, 0, 100, 100, 100, 100, 1.0, {"X": {"mean": 50}}, 100, 100),
        }
        factors = [Factor("X", 1.0, maximize=True)]
        result = SensitivityEngine.analyze(results, factors)
        assert result["robustness_score"] == 1.0

    def test_weight_sum_not_one(self):
        results = {
            "A": Statistics("A", 150, 0, 150, 150, 150, 150, 1.0, {"X": {"mean": 100}, "Y": {"mean": 50}}, 150, 150),
            "B": Statistics("B", 100, 0, 100, 100, 100, 100, 1.0, {"X": {"mean": 50}, "Y": {"mean": 50}}, 100, 100),
        }
        factors = [Factor("X", 0.3, maximize=True), Factor("Y", 0.3, maximize=True)]
        result = SensitivityEngine.analyze(results, factors)
        assert result["robustness_score"] == 1.0

    def test_single_option_single_factor(self):
        results = {
            "Only": Statistics("Only", 100, 0, 100, 100, 100, 100, 1.0, {"X": {"mean": 50}}, 100, 100),
        }
        factors = [Factor("X", 1.0, maximize=True)]
        result = SensitivityEngine.analyze(results, factors)
        assert result["robustness_score"] == 1.0
