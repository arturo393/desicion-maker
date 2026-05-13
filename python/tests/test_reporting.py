import os
import tempfile

import pandas as pd
import pytest

from python.core.models import Factor, Statistics
from python.core.reporting import (
    build_algorithm_comparison,
    prepare_decision_matrix,
    save_report,
)


class TestReporting:
    def test_prepare_decision_matrix(self):
        results = {
            "A": Statistics("A", 100, 10, 80, 120, 85, 115, 0.9, {"X": {"mean": 50}}, 85, 80),
            "B": Statistics("B", 80, 10, 60, 100, 65, 95, 0.7, {"X": {"mean": 30}}, 65, 60),
        }
        factors = [Factor("X", 0.5, maximize=True)]
        matrix = prepare_decision_matrix(results, factors)
        assert "A" in matrix
        assert "B" in matrix
        assert matrix["A"]["total_score"] == 100.0
        assert matrix["A"]["X"]["raw"] == 50.0
        assert matrix["A"]["X"]["weight"] == 0.5

    def test_build_algorithm_comparison(self):
        results = {
            "A": Statistics("A", 100, 10, 80, 120, 85, 115, 0.9, {"X": {"mean": 50}}, 85, 80),
            "B": Statistics("B", 80, 10, 60, 100, 65, 95, 0.7, {"X": {"mean": 30}}, 65, 60),
        }
        topsis = pd.Series({"A": 0.8, "B": 0.2}).sort_values(ascending=False)
        comp = build_algorithm_comparison(results, topsis)
        assert "A" in comp
        assert "B" in comp
        assert comp["A"]["mc_rank"] == 1
        assert comp["A"]["topsis_rank"] == 1

    def test_save_report_creates_all_files(self):
        results = {
            "A": Statistics("A", 100, 10, 80, 120, 85, 115, 0.9, {"X": {"mean": 50}}, 85, 80),
            "B": Statistics("B", 80, 10, 60, 100, 65, 95, 0.7, {"X": {"mean": 30}}, 65, 60),
        }
        factors = [Factor("X", 0.5, maximize=True)]

        with tempfile.TemporaryDirectory() as tmpdir:
            paths = save_report(
                mode="standard",
                mc_results=results,
                topsis_scores=pd.Series(),
                strategies={},
                pareto={"efficient_frontier": ["A"], "dominated_options": []},
                sensitivity={"base_winner": "A", "changes": [], "robustness_score": 1.0},
                future={},
                ai_reports={},
                factors=factors,
                results_dir=tmpdir,
            )
            assert os.path.exists(paths["json"])
            assert os.path.exists(paths["md"])
            assert os.path.exists(paths["html"])
