import pytest

from decision_maker.core.outcome_tracker import OutcomeEntry
from decision_maker.core.unknown_scanner import UnknownUnknownsScanner, UnknownReport


class TestUnknownUnknownsScanner:
    def test_empty_entries(self):
        result = UnknownUnknownsScanner.scan([])
        assert result.total_decisions_analyzed == 0
        assert result.verdict == "no_data"

    def test_healthy_outcomes(self):
        entries = [
            OutcomeEntry(decision_id=f"d{i}", predicted_winner="A", predicted_confidence=0.6,
                         actual_winner="A", actual_score=5.0, was_correct=True, tags=["t1"])
            for i in range(10)
        ]
        result = UnknownUnknownsScanner.scan(entries)
        assert result.verdict == "healthy"
        assert result.wrong_decisions == 0

    def test_overconfident_wrong(self):
        entries = [
            OutcomeEntry(decision_id=f"d{i}", predicted_winner="A", predicted_confidence=0.95,
                         actual_winner="B", actual_score=5.0, was_correct=False, tags=["rf"])
            for i in range(10)
        ] + [
            OutcomeEntry(decision_id="d_ok", predicted_winner="A", predicted_confidence=0.3,
                         actual_winner="A", actual_score=5.0, was_correct=True, tags=["net"]),
        ]
        result = UnknownUnknownsScanner.scan(entries)
        assert result.verdict in ("critical", "overconfident")
        assert result.overconfidence_ratio > 1.0

    def test_mixed_outcomes(self):
        entries = []
        for i in range(20):
            was_correct = i % 3 != 0
            entries.append(OutcomeEntry(
                decision_id=f"d{i}", predicted_winner="A", predicted_confidence=0.7,
                actual_winner="A" if was_correct else "B", actual_score=5.0,
                was_correct=was_correct, tags=["rf"] if not was_correct else ["net"],
            ))
        result = UnknownUnknownsScanner.scan(entries)
        assert result.total_decisions_analyzed == 20
        assert result.wrong_decisions > 0

    def test_to_dict(self):
        result = UnknownUnknownsScanner.scan([])
        d = UnknownUnknownsScanner.to_dict(result)
        assert "verdict" in d
        assert "reasoning" in d
        assert "error_rate" in d

    def test_confidence_comparison(self):
        entries = [
            OutcomeEntry(decision_id="d1", predicted_winner="A", predicted_confidence=0.9,
                         actual_winner="B", actual_score=5.0, was_correct=False, tags=[]),
            OutcomeEntry(decision_id="d2", predicted_winner="A", predicted_confidence=0.3,
                         actual_winner="A", actual_score=5.0, was_correct=True, tags=[]),
        ]
        result = UnknownUnknownsScanner.scan(entries)
        assert result.confidence_when_wrong_avg > result.confidence_when_right_avg
