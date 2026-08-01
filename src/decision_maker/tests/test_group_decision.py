from decision_maker.core.group_decision import GroupDecisionEngine
from decision_maker.core.models import Factor


class TestGroupDecision:
    def test_aggregate_weights_mean(self):
        stakeholders = {
            "Alice": {"Cost": 0.5, "Quality": 0.3, "Speed": 0.2},
            "Bob": {"Cost": 0.4, "Quality": 0.4, "Speed": 0.2},
        }
        result = GroupDecisionEngine.aggregate_weights(stakeholders, method="mean")
        assert "consensus_weights" in result
        w = result["consensus_weights"]
        assert abs(sum(w.values()) - 1.0) < 1e-6
        assert "stakeholder_count" in result
        assert result["stakeholder_count"] == 2

    def test_aggregate_weights_median(self):
        stakeholders = {
            "A": {"X": 0.8, "Y": 0.2},
            "B": {"X": 0.6, "Y": 0.4},
            "C": {"X": 0.7, "Y": 0.3},
        }
        result = GroupDecisionEngine.aggregate_weights(stakeholders, method="median")
        assert abs(sum(result["consensus_weights"].values()) - 1.0) < 1e-6

    def test_aggregate_weights_borda(self):
        stakeholders = {
            "A": {"X": 0.7, "Y": 0.2, "Z": 0.1},
            "B": {"X": 0.3, "Y": 0.5, "Z": 0.2},
        }
        result = GroupDecisionEngine.aggregate_weights(stakeholders, method="borda")
        assert abs(sum(result["consensus_weights"].values()) - 1.0) < 1e-6

    def test_empty_stakeholders(self):
        result = GroupDecisionEngine.aggregate_weights({})
        assert "error" in result

    def test_kendall_w_perfect_agreement(self):
        stakeholders = {
            "A": {"X": 0.5, "Y": 0.3, "Z": 0.2},
            "B": {"X": 0.5, "Y": 0.3, "Z": 0.2},
        }
        result = GroupDecisionEngine.aggregate_weights(stakeholders)
        assert result["kendall_w"] > 0.9

    def test_kendall_w_low_agreement(self):
        stakeholders = {
            "A": {"X": 0.8, "Y": 0.1, "Z": 0.1},
            "B": {"X": 0.1, "Y": 0.1, "Z": 0.8},
        }
        result = GroupDecisionEngine.aggregate_weights(stakeholders)
        assert result["kendall_w"] < 0.5

    def test_consensus_level(self):
        stakeholders = {
            "A": {"X": 0.5, "Y": 0.3, "Z": 0.2},
            "B": {"X": 0.5, "Y": 0.3, "Z": 0.2},
        }
        result = GroupDecisionEngine.aggregate_weights(stakeholders)
        assert result["consensus_level"] in ("high", "moderate", "low")

    def test_per_stakeholder_rankings(self):
        stakeholders = {"A": {"Cost": 0.6, "Benefit": 0.4}}
        result = GroupDecisionEngine.aggregate_weights(stakeholders)
        assert "stakeholders" in result
        assert "A" in result["stakeholders"]
        assert "ranking" in result["stakeholders"]["A"]
        assert "weights" in result["stakeholders"]["A"]

    def test_aggregate_scores(self):
        stakeholders = {"A": {"Cost": 0.6, "Quality": 0.4}}
        factors = [Factor("Cost", 0.5, maximize=False), Factor("Quality", 0.5, maximize=True)]
        result = GroupDecisionEngine.aggregate_scores(stakeholders, factors)
        assert "factors" in result
        assert len(result["factors"]) == 2
