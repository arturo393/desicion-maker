from decision_maker.core.bayesian import BayesianEngine
from decision_maker.core.models import Statistics


class TestBayesianEngine:
    def test_basic_posterior(self):
        results = {
            "A": Statistics("A", 100, 10, 80, 120, 85, 115, 0.9, {"X": {"mean": 10}}, 85, 80),
            "B": Statistics("B", 80, 10, 60, 100, 65, 95, 0.7, {"X": {"mean": 5}}, 65, 60),
        }
        posteriors = BayesianEngine().analyze(results)
        assert "A" in posteriors
        assert "B" in posteriors
        assert posteriors["A"] > posteriors["B"]

    def test_single_option(self):
        results = {
            "Only": Statistics("Only", 100, 10, 80, 120, 85, 115, 0.9, {"X": {"mean": 10}}, 85, 80),
        }
        posteriors = BayesianEngine().analyze(results)
        assert len(posteriors) == 1
        assert posteriors["Only"] == 1.0

    def test_empty_results(self):
        posteriors = BayesianEngine().analyze({})
        assert posteriors == {}

    def test_equal_options(self):
        results = {
            "A": Statistics("A", 100, 10, 80, 120, 85, 115, 0.9, {"X": {"mean": 10}}, 85, 80),
            "B": Statistics("B", 100, 10, 80, 120, 85, 115, 0.9, {"X": {"mean": 10}}, 85, 80),
        }
        posteriors = BayesianEngine().analyze(results)
        assert abs(posteriors["A"] - posteriors["B"]) < 0.01

    def test_extreme_z_scores(self):
        results = {}
        for i in range(100):
            results[f"Base{i}"] = Statistics(f"Base{i}", 0, 1, -1, 1, -1, 1, 0.5, {}, 0, 0)
        results["Extreme"] = Statistics(
            "Extreme", 1e6, 1, 1e6 - 1, 1e6 + 1, 1e6 - 1, 1e6 + 1, 1.0, {}, 1e6 - 1, 1e6 - 1
        )
        posteriors = BayesianEngine().analyze(results, num_posterior_samples=5000)
        assert posteriors["Extreme"] > 0.5
        assert 0 <= posteriors["Extreme"] <= 1
        assert all(0 <= v <= 1 for v in posteriors.values())
