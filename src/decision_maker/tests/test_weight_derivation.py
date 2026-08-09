from __future__ import annotations

from decision_maker.core.weight_derivation import WeightDerivationEngine


class TestSwingWeights:
    def test_basic_swing(self):
        result = WeightDerivationEngine.swing_weights({"Cost": 80, "Quality": 100, "Speed": 20})
        assert "weights" in result
        w = result["weights"]
        assert abs(sum(w.values()) - 1.0) < 1e-6
        assert w["Quality"] > w["Cost"] > w["Speed"]

    def test_swing_normalizes_to_sum_one(self):
        result = WeightDerivationEngine.swing_weights({"A": 10, "B": 30, "C": 60})
        assert abs(sum(result["weights"].values()) - 1.0) < 1e-6

    def test_swing_zero_ratings(self):
        result = WeightDerivationEngine.swing_weights({"A": 0, "B": 0})
        assert abs(sum(result["weights"].values()) - 1.0) < 1e-6

    def test_swing_empty(self):
        result = WeightDerivationEngine.swing_weights({})
        assert result["weights"] == {}

    def test_swing_all_zero(self):
        result = WeightDerivationEngine.swing_weights({"A": 0, "B": 0, "C": 0})
        assert abs(sum(result["weights"].values()) - 1.0) < 1e-6
        assert "equal" in result.get("note", "").lower()

    def test_swing_single_factor(self):
        result = WeightDerivationEngine.swing_weights({"Only": 50})
        assert abs(result["weights"]["Only"] - 1.0) < 1e-6


class TestSwingFromRanking:
    def test_linear_decay(self):
        result = WeightDerivationEngine.swing_from_ranking(["A", "B", "C"])
        w = result["weights"]
        assert abs(sum(w.values()) - 1.0) < 1e-6
        assert w["A"] > w["B"] > w["C"]

    def test_exponential_decay(self):
        result = WeightDerivationEngine.swing_from_ranking(["A", "B", "C"], decay="exponential")
        w = result["weights"]
        assert abs(sum(w.values()) - 1.0) < 1e-6
        assert w["A"] > w["B"] > w["C"]

    def test_empty_ranking(self):
        result = WeightDerivationEngine.swing_from_ranking([])
        assert "error" in result

    def test_single_factor_ranking(self):
        result = WeightDerivationEngine.swing_from_ranking(["Only"])
        assert abs(result["weights"]["Only"] - 1.0) < 1e-6


class TestPairwiseWeights:
    def test_perfectly_consistent(self):
        comparisons = {
            ("A", "B"): 3,
            ("A", "C"): 5,
            ("B", "C"): 3,
        }
        result = WeightDerivationEngine.pairwise_weights(comparisons, ["A", "B", "C"])
        assert "error" not in result
        assert abs(sum(result["weights"].values()) - 1.0) < 1e-6
        assert result["weights"]["A"] > result["weights"]["B"] > result["weights"]["C"]

    def test_equal_importance(self):
        comparisons = {("A", "B"): 1}
        result = WeightDerivationEngine.pairwise_weights(comparisons, ["A", "B"])
        assert abs(result["weights"]["A"] - result["weights"]["B"]) < 0.01

    def test_reciprocal_handling(self):
        # Only provide one direction; engine should auto-infer reciprocal
        comparisons = {("A", "B"): 5}
        result = WeightDerivationEngine.pairwise_weights(comparisons, ["A", "B"])
        assert "error" not in result
        assert result["weights"]["A"] > result["weights"]["B"]

    def test_fewer_than_two_labels(self):
        result = WeightDerivationEngine.pairwise_weights({}, ["Only"])
        assert "error" in result

    def test_empty_labels(self):
        result = WeightDerivationEngine.pairwise_weights({}, [])
        assert "error" in result

    def test_consistency_ratio_returned(self):
        comparisons = {("A", "B"): 2, ("A", "C"): 4, ("B", "C"): 2}
        result = WeightDerivationEngine.pairwise_weights(comparisons, ["A", "B", "C"])
        assert "consistency_ratio" in result

    def test_interactive_prompt_generation(self):
        questions = WeightDerivationEngine.pairwise_interactive_prompt(["A", "B", "C"])
        assert len(questions) == 3
        assert "A" in questions[0]
        assert "B" in questions[0]
        assert "A" in questions[1]
        assert "C" in questions[1]
        assert "B" in questions[2]
        assert "C" in questions[2]


class TestPaprikaWeights:
    def test_basic_paprika(self):
        answers = {
            ("Cost", "Quality"): "A",
            ("Cost", "Speed"): "A",
            ("Quality", "Speed"): "B",
        }
        result = WeightDerivationEngine.paprika_weights(["Cost", "Quality", "Speed"], answers)
        assert "weights" in result
        assert abs(sum(result["weights"].values()) - 1.0) < 1e-6
        assert result["pairwise_wins"]["Cost"] >= result["pairwise_wins"]["Speed"]

    def test_paprika_no_answers(self):
        result = WeightDerivationEngine.paprika_weights(["A", "B", "C"], {})
        assert "error" not in result
        assert abs(sum(result["weights"].values()) - 1.0) < 1e-6
        assert "equal" in result.get("note", "").lower()

    def test_paprika_fewer_than_two(self):
        result = WeightDerivationEngine.paprika_weights(["Only"], {})
        assert "error" in result

    def test_paprika_generates_questions(self):
        questions = WeightDerivationEngine.paprika_generate_questions(
            ["Cost", "Quality", "Speed", "Risk"], max_questions=4
        )
        assert len(questions) == 4
        for a, b, text in questions:
            assert a in text
            assert b in text

    def test_paprika_ranking_order(self):
        answers = {
            ("A", "B"): "A",
            ("A", "C"): "A",
        }
        result = WeightDerivationEngine.paprika_weights(["A", "B", "C"], answers)
        assert result["rankings"][0] == "A"
        assert sum(result["pairwise_wins"].values()) > 0


class TestDeriveConvenience:
    def test_derive_swing(self):
        result = WeightDerivationEngine.derive("swing", ratings={"A": 80, "B": 20})
        assert "weights" in result

    def test_derive_swing_ranked(self):
        result = WeightDerivationEngine.derive("swing_ranked", ranked_factors=["A", "B", "C"])
        assert "weights" in result

    def test_derive_pairwise(self):
        result = WeightDerivationEngine.derive("pairwise", comparisons={("A", "B"): 3}, labels=["A", "B"])
        assert "weights" in result

    def test_derive_paprika(self):
        result = WeightDerivationEngine.derive("paprika", factors=["A", "B"], tradeoff_answers={("A", "B"): "A"})
        assert "weights" in result

    def test_derive_unknown_method(self):
        result = WeightDerivationEngine.derive("unknown")
        assert "error" in result
