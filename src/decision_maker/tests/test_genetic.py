from decision_maker.core.genetic import GeneticOptimizer
from decision_maker.core.models import Factor, Statistics


class TestGeneticOptimizer:
    def test_ideal_evolution(self):
        results = {
            "A": Statistics(
                "A", 100, 10, 80, 120, 85, 115, 0.9, {"Cost": {"mean": 50}, "Quality": {"mean": 80}}, 85, 80
            ),
            "B": Statistics(
                "B", 120, 15, 70, 160, 80, 150, 0.85, {"Cost": {"mean": 30}, "Quality": {"mean": 95}}, 80, 75
            ),
        }
        factors = [Factor("Cost", 0.5, maximize=False), Factor("Quality", 0.5, maximize=True)]
        result = GeneticOptimizer.evolve_ideal(results, factors)
        assert "Cost" in result["ideal_composition"]
        assert "Quality" in result["ideal_composition"]
        assert result["improvement_potential"] >= 0

    def test_single_option(self):
        results = {
            "Only": Statistics("Only", 10, 0, 10, 10, 10, 10, 1.0, {"X": {"mean": 10}}, 10, 10),
        }
        factors = [Factor("X", 1.0, maximize=True)]
        result = GeneticOptimizer.evolve_ideal(results, factors)
        assert result["improvement_potential"] == 0.0
        assert result["source_options"]["X"] == "Only"

    def test_empty_results(self):
        result = GeneticOptimizer.evolve_ideal({}, [Factor("X", 1.0, maximize=True)])
        assert result["improvement_potential"] == 0

    def test_penalty_effect(self):
        results = {
            "A": Statistics("A", 7.5, 0, 7.5, 7.5, 7.5, 7.5, 1.0, {"X": {"mean": 10}, "Y": {"mean": 5}}, 7.5, 7.5),
            "B": Statistics("B", 8.5, 0, 8.5, 8.5, 8.5, 8.5, 1.0, {"X": {"mean": 8}, "Y": {"mean": 9}}, 8.5, 8.5),
        }
        factors = [Factor("X", 0.5, maximize=True), Factor("Y", 0.5, maximize=True)]
        result = GeneticOptimizer.evolve_ideal(results, factors, penalty_variance=0.1)
        assert len(result["source_options"]) == 2

    def test_penalty_variance_zero(self):
        results = {
            "A": Statistics("A", 7.5, 0, 7.5, 7.5, 7.5, 7.5, 1.0, {"X": {"mean": 10}, "Y": {"mean": 5}}, 7.5, 7.5),
            "B": Statistics("B", 8.5, 0, 8.5, 8.5, 8.5, 8.5, 1.0, {"X": {"mean": 8}, "Y": {"mean": 9}}, 8.5, 8.5),
        }
        factors = [Factor("X", 0.5, maximize=True), Factor("Y", 0.5, maximize=True)]
        result = GeneticOptimizer.evolve_ideal(results, factors, penalty_variance=0)
        assert "theoretical_max_score" in result

    def test_identical_options(self):
        results = {
            "A": Statistics("A", 10, 0, 10, 10, 10, 10, 1.0, {"X": {"mean": 5}}, 10, 10),
            "B": Statistics("B", 10, 0, 10, 10, 10, 10, 1.0, {"X": {"mean": 5}}, 10, 10),
        }
        factors = [Factor("X", 1.0, maximize=True)]
        result = GeneticOptimizer.evolve_ideal(results, factors)
        assert len(result["source_options"]) == 1

    def test_zero_factors(self):
        results = {
            "A": Statistics("A", 10, 0, 10, 10, 10, 10, 1.0, {}, 10, 10),
        }
        result = GeneticOptimizer.evolve_ideal(results, [])
        assert result["improvement_potential"] == 0
