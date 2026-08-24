import os
import tempfile

import pandas as pd
import pytest

from decision_maker.core.models import Factor, Statistics
from decision_maker.core.report_schema import REPORT_SCHEMA, validate_report
from decision_maker.core.reporting import (
    ReportData,
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
            report_data = ReportData(
                mode="standard",
                mc_results=results,
                topsis_scores=pd.Series(),
                strategies={},
                pareto={"efficient_frontier": ["A"], "dominated_options": []},
                sensitivity={"base_winner": "A", "weight_changes": [], "score_changes": [], "robustness_score": 1.0},
                future={},
                ai_reports={},
                factors=factors,
                results_dir=tmpdir,
            ).prepare()
            paths = save_report(report_data)
            assert os.path.exists(paths["json"])
            assert os.path.exists(paths["md"])
            assert os.path.exists(paths["html"])

    def test_generate_html_inline_imports_and_renders(self):
        from decision_maker.core.html_fallback import generate_html_inline

        results = {
            "A": Statistics("A", 100, 10, 80, 120, 85, 115, 0.9, {"X": {"mean": 50}}, 85, 80),
            "B": Statistics("B", 80, 10, 60, 100, 65, 95, 0.7, {"X": {"mean": 30}}, 65, 60),
        }
        factors = [Factor("X", 0.5, maximize=True)]
        topsis = pd.Series({"A": 0.8, "B": 0.2}).sort_values(ascending=False)

        with tempfile.TemporaryDirectory() as tmpdir:
            report_data = ReportData(
                mode="advanced",
                mc_results=results,
                topsis_scores=topsis,
                strategies={},
                pareto={"efficient_frontier": ["A"], "dominated_options": []},
                sensitivity={"base_winner": "A", "weight_changes": [], "score_changes": [], "robustness_score": 1.0},
                future={"bayesian_probs": {"A": 0.9, "B": 0.1}, "ideal_option": {"improvement_potential": 5.0}},
                ai_reports={},
                factors=factors,
                results_dir=tmpdir,
            ).prepare()
            html_path = generate_html_inline(report_data)
            assert os.path.exists(html_path)
            with open(html_path, encoding="utf-8") as f:
                html = f.read()
            assert "Decision Intelligence Report" in html
            assert "A" in html
            assert "B" in html
            assert html_path == os.path.join(tmpdir, f"report_{report_data.timestamp}.html")

    def test_save_report_creates_missing_results_dir(self):
        results = {
            "A": Statistics("A", 100, 10, 80, 120, 85, 115, 0.9, {"X": {"mean": 50}}, 85, 80),
        }
        factors = [Factor("X", 0.5, maximize=True)]

        with tempfile.TemporaryDirectory() as tmpdir:
            nested = os.path.join(tmpdir, "does", "not", "exist")
            report_data = ReportData(
                mode="standard",
                mc_results=results,
                topsis_scores=pd.Series(),
                strategies={},
                pareto={"efficient_frontier": ["A"], "dominated_options": []},
                sensitivity={"base_winner": "A", "weight_changes": [], "score_changes": [], "robustness_score": 1.0},
                future={},
                ai_reports={},
                factors=factors,
                results_dir=nested,
            ).prepare()
            paths = save_report(report_data)
            assert os.path.exists(paths["json"])
            assert os.path.exists(paths["md"])
            assert os.path.exists(paths["html"])

    def test_json_report_conforms_to_schema(self):
        results = {
            "A": Statistics("A", 100, 10, 80, 120, 85, 115, 0.9, {"X": {"mean": 50}}, 85, 80),
            "B": Statistics("B", 80, 10, 60, 100, 65, 95, 0.7, {"X": {"mean": 30}}, 65, 60),
        }
        factors = [Factor("X", 0.5, maximize=True)]

        with tempfile.TemporaryDirectory() as tmpdir:
            report_data = ReportData(
                mode="standard",
                mc_results=results,
                topsis_scores=pd.Series({"A": 0.8, "B": 0.2}),
                strategies={},
                pareto={"efficient_frontier": ["A"], "dominated_options": []},
                sensitivity={"base_winner": "A", "weight_changes": [], "score_changes": [], "robustness_score": 1.0},
                future={},
                ai_reports={},
                factors=factors,
                results_dir=tmpdir,
            ).prepare()
            paths = save_report(report_data)
            import json

            with open(paths["json"]) as f:
                data = json.load(f)
            validate_report(data)  # should not raise

    def test_schema_rejects_missing_required_field(self):
        from jsonschema import ValidationError

        bad = {
            "timestamp": "x",
            "decision_matrix": {},
            "topsis": {},
            "algorithm_comparison": {},
            "ai_insights": {},
        }
        with pytest.raises(ValidationError):
            validate_report(bad)
