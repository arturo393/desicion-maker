import pytest

from decision_maker.core.fuzzy_weighted_sum import (
    FuzzyCriterion,
    FuzzyNumber,
    FuzzyOption,
    FuzzyWeightedSum,
    CriterionDirection,
)


class TestFuzzyWeightedSum:
    def _make_engine(self):
        criteria = [
            FuzzyCriterion("Costo", weight=0.3, direction=CriterionDirection.MINIMIZE),
            FuzzyCriterion("Retorno", weight=0.4, direction=CriterionDirection.MAXIMIZE),
            FuzzyCriterion("Riesgo", weight=0.15, direction=CriterionDirection.MINIMIZE),
            FuzzyCriterion("Flex", weight=0.15, direction=CriterionDirection.MAXIMIZE),
        ]
        return FuzzyWeightedSum(criteria)

    def test_weights_not_mutated(self):
        criteria = [
            FuzzyCriterion("A", weight=1.0),
            FuzzyCriterion("B", weight=1.0),
        ]
        FuzzyWeightedSum(criteria)
        assert criteria[0].weight == 1.0
        assert criteria[1].weight == 1.0

    def test_weight_normalization(self):
        criteria = [
            FuzzyCriterion("A", weight=2.0),
            FuzzyCriterion("B", weight=2.0),
        ]
        engine = FuzzyWeightedSum(criteria)
        assert engine._normalized_weights["A"] == pytest.approx(0.5)
        assert engine._normalized_weights["B"] == pytest.approx(0.5)

    def test_zero_total_weight_raises(self):
        with pytest.raises(ValueError, match="positive"):
            FuzzyWeightedSum([FuzzyCriterion("A", weight=0.0)])

    def test_numeric_scores(self):
        engine = self._make_engine()
        opt_a = FuzzyOption("A", scores={"Costo": 3.0, "Retorno": 6.0, "Riesgo": 2.0, "Flex": 7.0})
        opt_b = FuzzyOption("B", scores={"Costo": 8.0, "Retorno": 9.5, "Riesgo": 8.0, "Flex": 9.0})
        ranking = engine.evaluate([opt_a, opt_b])
        assert ranking[0]["option_name"] == "A"
        assert ranking[1]["option_name"] == "B"
        assert ranking[0]["rank"] == 1
        assert ranking[1]["rank"] == 2

    def test_fuzzy_number_scores(self):
        engine = FuzzyWeightedSum([
            FuzzyCriterion("Cost", weight=1.0, direction=CriterionDirection.MINIMIZE),
        ])
        opt = FuzzyOption("X", scores={"Cost": FuzzyNumber(1.0, 2.0, 3.0)})
        ranking = engine.evaluate([opt])
        # centroid = 2.0 -> minimize -> 10-2 = 8
        assert ranking[0]["overall_score"] == pytest.approx(8.0, abs=0.001)

    def test_linguistic_scores(self):
        engine = FuzzyWeightedSum([
            FuzzyCriterion("Quality", weight=1.0, direction=CriterionDirection.MAXIMIZE),
        ])
        opt = FuzzyOption("X", scores={"Quality": "ALTO"})
        ranking = engine.evaluate([opt])
        # ALTO centroid = (6+7.5+9)/3 = 7.5
        assert ranking[0]["overall_score"] == pytest.approx(7.5, abs=0.001)

    def test_breakdown_structure(self):
        engine = self._make_engine()
        opt = FuzzyOption("A", scores={"Costo": 3.0, "Retorno": 6.0, "Riesgo": 2.0, "Flex": 7.0})
        ranking = engine.evaluate([opt])
        assert "Costo" in ranking[0]["breakdown"]
        assert "Retorno" in ranking[0]["breakdown"]

    def test_empty_scores_default_zero(self):
        engine = FuzzyWeightedSum([
            FuzzyCriterion("Cost", weight=1.0, direction=CriterionDirection.MINIMIZE),
        ])
        opt = FuzzyOption("X")
        ranking = engine.evaluate([opt])
        # default 0 -> minimize -> 10
        assert ranking[0]["overall_score"] == pytest.approx(10.0, abs=0.001)

    def test_sensitivity_robust(self):
        engine = self._make_engine()
        opts = [
            FuzzyOption("A", scores={"Costo": 1.0, "Retorno": 9.0, "Riesgo": 1.0, "Flex": 9.0}),
            FuzzyOption("B", scores={"Costo": 9.0, "Retorno": 1.0, "Riesgo": 9.0, "Flex": 1.0}),
        ]
        report = engine.sensitivity(opts, delta=0.05)
        assert report["baseline_winner"] == "A"
        assert report["stability_assessment"] == "ROBUSTO"

    def test_sensitivity_detects_flips(self):
        engine = FuzzyWeightedSum([
            FuzzyCriterion("A", weight=0.5, direction=CriterionDirection.MAXIMIZE),
            FuzzyCriterion("B", weight=0.5, direction=CriterionDirection.MAXIMIZE),
        ])
        opts = [
            FuzzyOption("X", scores={"A": 9.0, "B": 1.0}),
            FuzzyOption("Y", scores={"A": 1.0, "B": 9.0}),
        ]
        report = engine.sensitivity(opts, delta=0.3)
        assert len(report["critical_criteria"]) > 0

    def test_ranking_descending(self):
        engine = FuzzyWeightedSum([
            FuzzyCriterion("S", weight=1.0, direction=CriterionDirection.MAXIMIZE),
        ])
        opts = [
            FuzzyOption("low", scores={"S": 1.0}),
            FuzzyOption("high", scores={"S": 9.0}),
            FuzzyOption("mid", scores={"S": 5.0}),
        ]
        ranking = engine.evaluate(opts)
        assert [r["option_name"] for r in ranking] == ["high", "mid", "low"]
