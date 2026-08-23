import pytest

from decision_maker.core.outcome_tracker import OutcomeEntry
from decision_maker.core.reasoning_trace import TraceEntry
from decision_maker.core.meta_calibration import MetaCalibration, MetaCalibrationResult


class TestMetaCalibration:
    def test_empty_traces(self):
        result = MetaCalibration.evaluate([], [])
        assert result.total_routed == 0
        assert result.verdict == "no_data"

    def test_well_routed(self):
        traces = [
            TraceEntry(decision_id="d1", problem_name="p1", complexity_score=0.2, recommended_mode="express",
                       engines_run=["MC"], engines_skipped=[]),
            TraceEntry(decision_id="d2", problem_name="p2", complexity_score=0.8, recommended_mode="advanced",
                       engines_run=["MC", "TOPSIS", "Bayesian"], engines_skipped=[]),
        ]
        outcomes = [
            OutcomeEntry(decision_id="d1", predicted_winner="A", predicted_confidence=0.7,
                         actual_winner="A", actual_score=5.0, was_correct=True),
            OutcomeEntry(decision_id="d2", predicted_winner="B", predicted_confidence=0.8,
                         actual_winner="B", actual_score=8.0, was_correct=True),
        ]
        result = MetaCalibration.evaluate(traces, outcomes)
        assert result.total_routed == 2
        assert result.routing_quality > 0.5

    def test_over_engineered(self):
        traces = [
            TraceEntry(decision_id="d1", problem_name="p1", complexity_score=0.1, recommended_mode="standard",
                       engines_run=["MC", "TOPSIS", "Bayesian"], engines_skipped=[]),
            TraceEntry(decision_id="d2", problem_name="p2", complexity_score=0.2, recommended_mode="advanced",
                       engines_run=["MC", "TOPSIS", "Bayesian", "Genetic"], engines_skipped=[]),
        ]
        outcomes = [
            OutcomeEntry(decision_id="d1", predicted_winner="A", predicted_confidence=0.7,
                         actual_winner="A", actual_score=5.0, was_correct=True),
            OutcomeEntry(decision_id="d2", predicted_winner="B", predicted_confidence=0.8,
                         actual_winner="B", actual_score=8.0, was_correct=True),
        ]
        result = MetaCalibration.evaluate(traces, outcomes)
        assert result.over_engineered == 2

    def test_under_engineered(self):
        traces = [
            TraceEntry(decision_id="d1", problem_name="p1", complexity_score=0.9, recommended_mode="express",
                       engines_run=["MC"], engines_skipped=["Bayesian", "Genetic"]),
        ]
        outcomes = [
            OutcomeEntry(decision_id="d1", predicted_winner="A", predicted_confidence=0.7,
                         actual_winner="B", actual_score=5.0, was_correct=False),
        ]
        result = MetaCalibration.evaluate(traces, outcomes)
        assert result.under_engineered == 1

    def test_to_dict(self):
        result = MetaCalibration.evaluate([], [])
        d = MetaCalibration.to_dict(result)
        assert "verdict" in d
        assert "routing_quality" in d

    def test_mode_accuracy(self):
        traces = [
            TraceEntry(decision_id="d1", problem_name="p1", complexity_score=0.2, recommended_mode="express",
                       engines_run=["MC"], engines_skipped=[]),
            TraceEntry(decision_id="d2", problem_name="p2", complexity_score=0.3, recommended_mode="express",
                       engines_run=["MC"], engines_skipped=[]),
        ]
        outcomes = [
            OutcomeEntry(decision_id="d1", predicted_winner="A", predicted_confidence=0.7,
                         actual_winner="A", actual_score=5.0, was_correct=True),
            OutcomeEntry(decision_id="d2", predicted_winner="B", predicted_confidence=0.8,
                         actual_winner="A", actual_score=8.0, was_correct=False),
        ]
        result = MetaCalibration.evaluate(traces, outcomes)
        assert "express" in result.mode_accuracy
        assert result.mode_accuracy["express"] == pytest.approx(0.5, abs=0.01)
