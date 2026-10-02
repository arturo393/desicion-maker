from decision_maker.core.decision_theory import DecisionTheoryEngine
from decision_maker.core.models import Statistics


class TestDecisionTheoryEngine:
    def test_all_strategies(self):
        results = {
            "A": Statistics("A", 100, 10, 80, 150, 85, 130, 0.9, {"X": {"mean": 10}}, 85, 80),
            "B": Statistics("B", 120, 15, 90, 140, 95, 135, 0.85, {"X": {"mean": 12}}, 95, 90),
        }
        strategies = DecisionTheoryEngine.analyze(results)
        assert "Maximax (Optimistic)" in strategies
        assert "Maximin (Conservative)" in strategies
        assert "Hurwicz (Balanced)" in strategies
        assert "Laplace (Risk Neutral)" in strategies
        assert "Minimax Regret" in strategies

    def test_single_option(self):
        results = {
            "Only": Statistics("Only", 100, 0, 100, 100, 100, 100, 1.0, {}, 100, 100),
        }
        strategies = DecisionTheoryEngine.analyze(results)
        assert "Only" in strategies["Maximax (Optimistic)"]
        assert strategies["Minimax Regret"].endswith("0.00)")

    def test_empty_results(self):
        strategies = DecisionTheoryEngine.analyze({})
        assert strategies == {}

    def test_all_identical_payoffs(self):
        results = {
            "A": Statistics("A", 100, 0, 100, 100, 100, 100, 1.0, {}, 100, 100),
            "B": Statistics("B", 100, 0, 100, 100, 100, 100, 1.0, {}, 100, 100),
        }
        strategies = DecisionTheoryEngine.analyze(results)
        choices = set(s.split(" ")[0] for s in strategies.values())
        assert len(choices) == 1

    def test_strategies_consistency(self):
        results = {
            "Low": Statistics("Low", 50, 5, 40, 60, 42, 58, 0.5, {"X": {"mean": 5}}, 42, 41),
            "Mid": Statistics("Mid", 100, 10, 80, 120, 85, 115, 0.8, {"X": {"mean": 10}}, 85, 82),
            "High": Statistics("High", 150, 20, 100, 200, 110, 190, 0.9, {"X": {"mean": 15}}, 110, 105),
        }
        strategies = DecisionTheoryEngine.analyze(results)
        assert "High" in strategies["Maximax (Optimistic)"]
        assert "High" in strategies["Minimax Regret"]

    def test_minimax_regret_uses_percentile_states(self):
        """Regret must compare quantile states (comonotonic assumption) rather than arbitrary simulation indices."""
        import numpy as np
        scores_a = np.array([10.0, 20.0, 30.0, 40.0, 50.0])
        scores_b = np.array([50.0, 40.0, 30.0, 20.0, 10.0])
        results = {
            "A": Statistics("A", 30.0, 14.14, 10.0, 50.0, 12.0, 48.0, 1.0, {}, 12.0, 10.0, raw_scores=scores_a),
            "B": Statistics("B", 30.0, 14.14, 10.0, 50.0, 12.0, 48.0, 1.0, {}, 12.0, 10.0, raw_scores=scores_b),
        }
        strategies = DecisionTheoryEngine.analyze(results)
        assert "Max Regret: 0.00" in strategies["Minimax Regret"]
