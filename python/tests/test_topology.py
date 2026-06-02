import numpy as np
import pytest

from python.core.models import Factor, Statistics
from python.core.topology import TopologicalDataAnalysis


@pytest.fixture
def three_options():
    np.random.seed(42)
    n = 200
    return {
        "A": Statistics("A", 0.8, 0.1, 0.5, 0.95, 0.6, 0.9, 0.9,
                       {"Cost": {"mean": 100, "std": 10, "p5": 85, "p95": 115},
                        "Quality": {"mean": 9, "std": 0.5, "p5": 8, "p95": 10}},
                       0.6, 0.55, raw_scores=np.random.rand(n) * 0.3 + 0.6),
        "B": Statistics("B", 0.6, 0.15, 0.3, 0.85, 0.4, 0.8, 0.7,
                       {"Cost": {"mean": 200, "std": 20, "p5": 170, "p95": 230},
                        "Quality": {"mean": 6, "std": 1, "p5": 4.5, "p95": 7.5}},
                       0.4, 0.35, raw_scores=np.random.rand(n) * 0.3 + 0.4),
        "C": Statistics("C", 0.4, 0.2, 0.1, 0.75, 0.2, 0.7, 0.5,
                       {"Cost": {"mean": 150, "std": 15, "p5": 125, "p95": 175},
                        "Quality": {"mean": 7, "std": 0.8, "p5": 6, "p95": 8}},
                       0.2, 0.15, raw_scores=np.random.rand(n) * 0.3 + 0.2),
    }


@pytest.fixture
def factors():
    return [
        Factor("Cost", 0.5, maximize=False),
        Factor("Quality", 0.5, maximize=True),
    ]


class TestTopologicalDataAnalysis:
    def test_analyze_returns_keys(self, three_options, factors):
        result = TopologicalDataAnalysis.analyze(three_options, factors)
        assert "num_options" in result
        assert "distance_matrix" in result
        assert "embedding_2d" in result
        assert "connectivity" in result
        assert "average_distance" in result
        assert result["num_options"] == 3

    def test_distance_matrix_dimensions(self, three_options, factors):
        result = TopologicalDataAnalysis.analyze(three_options, factors)
        dm = result["distance_matrix"]
        assert len(dm) == 3
        assert len(dm[0]) == 3

    def test_distance_matrix_self_zero(self, three_options, factors):
        result = TopologicalDataAnalysis.analyze(three_options, factors)
        dm = result["distance_matrix"]
        for i in range(3):
            assert dm[i][i] == 0.0

    def test_embedding_2d_shape(self, three_options, factors):
        result = TopologicalDataAnalysis.analyze(three_options, factors)
        emb = result["embedding_2d"]
        assert emb is not None
        assert len(emb) == 3
        assert len(emb[0]) == 2

    def test_mds_stress_present(self, three_options, factors):
        result = TopologicalDataAnalysis.analyze(three_options, factors)
        assert "mds_stress" in result
        assert result["mds_stress"] is not None

    def test_connectivity_has_components(self, three_options, factors):
        result = TopologicalDataAnalysis.analyze(three_options, factors)
        for c in result["connectivity"]:
            assert "threshold" in c
            assert "components" in c

    def test_less_than_two_options(self, factors):
        result = TopologicalDataAnalysis.analyze({
            "Only": Statistics("Only", 0.5, 0, 0.5, 0.5, 0.5, 0.5, 1.0,
                              {"X": {"mean": 1}}, 0.5, 0.5),
        }, factors)
        assert "error" in result

    def test_empty_results(self, factors):
        result = TopologicalDataAnalysis.analyze({}, factors)
        assert "error" in result

    def test_no_factor_data(self, three_options):
        # Remove factor_stats
        for opt in three_options.values():
            opt.factor_stats = {}
        factors = [Factor("Nope", 1.0)]
        result = TopologicalDataAnalysis.analyze(three_options, factors)
        assert "error" in result
