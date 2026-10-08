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
        """Regret must compare quantile states when not fully shared."""
        import numpy as np
        scores_a = np.array([10.0, 20.0, 30.0, 40.0, 50.0])
        scores_b = np.array([50.0, 40.0, 30.0, 20.0, 10.0])
        results = {
            "A": Statistics("A", 30.0, 14.14, 10.0, 50.0, 12.0, 48.0, 1.0, {}, 12.0, 10.0, raw_scores=scores_a),
            "B": Statistics("B", 30.0, 14.14, 10.0, 50.0, 12.0, 48.0, 1.0, {}, 12.0, 10.0, raw_scores=scores_b),
        }
        strategies = DecisionTheoryEngine.analyze(results, is_fully_shared=False)
        assert "Max Regret: 0.00" in strategies["Minimax Regret"]
        assert "percentiles" in strategies["Minimax Regret"]

    def test_minimax_regret_uses_simulation_when_fully_shared(self):
        """When fully shared, Minimax Regret evaluates pointwise scenario regret across simulations."""
        import numpy as np
        # Scenario 0: A=10, B=25 (best=25, regret A=15, B=0)
        # Scenario 1: A=50, B=30 (best=50, regret A=0, B=20)
        scores_a = np.array([10.0, 50.0])
        scores_b = np.array([25.0, 30.0])
        results = {
            "A": Statistics("A", 30.0, 20.0, 10.0, 50.0, 12.0, 48.0, 0.5, {}, 12.0, 10.0, raw_scores=scores_a),
            "B": Statistics("B", 27.5, 2.5, 25.0, 30.0, 25.2, 29.8, 0.5, {}, 25.2, 25.0, raw_scores=scores_b),
        }
        # Max regret for A is 15.0 (in scenario 0); max regret for B is 20.0 (in scenario 1).
        # Minimax regret choice is A with max regret 15.00.
        strategies = DecisionTheoryEngine.analyze(results, is_fully_shared=True)
        assert "A (Max Regret: 15.00" in strategies["Minimax Regret"]
        assert "simulación" in strategies["Minimax Regret"]

    def test_minimax_regret_differentiates_simulation_from_percentiles(self):
        """Opposing outcomes produce 0 regret under percentiles but 80 regret under simulation."""
        import numpy as np
        scores_a = np.array([10.0, 90.0])
        scores_b = np.array([90.0, 10.0])
        results = {
            "A": Statistics("A", 50.0, 40.0, 10.0, 90.0, 14.0, 86.0, 0.5, {}, 14.0, 10.0, raw_scores=scores_a),
            "B": Statistics("B", 50.0, 40.0, 10.0, 90.0, 14.0, 86.0, 0.5, {}, 14.0, 10.0, raw_scores=scores_b),
        }
        # Under percentiles: both sorted vectors are identical [10, 90], regret per state is 0.00
        strat_pct = DecisionTheoryEngine.analyze(results, is_fully_shared=False)
        assert "Max Regret: 0.00" in strat_pct["Minimax Regret"]

        # Under simulation: scenario 0 best is B (regret A=80), scenario 1 best is A (regret B=80)
        strat_sim = DecisionTheoryEngine.analyze(results, is_fully_shared=True)
        assert "Max Regret: 80.00" in strat_sim["Minimax Regret"]
