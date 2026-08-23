import json
import tempfile
from pathlib import Path

import numpy as np
import pytest

from decision_maker.core.outcome_tracker import OutcomeTracker, OutcomeEntry


class TestOutcomeTracker:
    def _make_tracker(self, tmp_path: Path) -> OutcomeTracker:
        return OutcomeTracker(outcomes_path=tmp_path / "test_outcomes.jsonl")

    def test_empty_tracker(self, tmp_path):
        tracker = self._make_tracker(tmp_path)
        assert tracker.accuracy() == 0.0
        assert tracker.summary()["total_decisions"] == 0

    def test_record_and_retrieve(self, tmp_path):
        tracker = self._make_tracker(tmp_path)
        entry = tracker.record(
            decision_id="d1",
            predicted_winner="A",
            predicted_confidence=0.8,
            actual_winner="A",
            actual_score=5.0,
            engine_scores={"A": 5.0},
        )
        assert entry.was_correct is True
        assert entry.regret == 0.0
        assert len(tracker.entries()) == 1

    def test_wrong_prediction(self, tmp_path):
        tracker = self._make_tracker(tmp_path)
        entry = tracker.record(
            decision_id="d1",
            predicted_winner="A",
            predicted_confidence=0.9,
            actual_winner="B",
            actual_score=10.0,
            engine_scores={"A": 5.0, "B": 10.0},
        )
        assert entry.was_correct is False

    def test_accuracy_calculation(self, tmp_path):
        tracker = self._make_tracker(tmp_path)
        tracker.record("d1", "A", 0.8, "A", 5.0)
        tracker.record("d2", "A", 0.7, "B", 10.0)
        tracker.record("d3", "A", 0.9, "A", 5.0)
        assert tracker.accuracy() == pytest.approx(2 / 3, abs=0.01)

    def test_accuracy_last_n(self, tmp_path):
        tracker = self._make_tracker(tmp_path)
        tracker.record("d1", "A", 0.8, "B", 5.0)
        tracker.record("d2", "A", 0.7, "A", 5.0)
        tracker.record("d3", "A", 0.9, "A", 5.0)
        assert tracker.accuracy(last_n=2) == 1.0

    def test_cumulative_accuracy(self, tmp_path):
        tracker = self._make_tracker(tmp_path)
        tracker.record("d1", "A", 0.8, "A", 5.0)
        tracker.record("d2", "A", 0.7, "B", 5.0)
        tracker.record("d3", "A", 0.9, "A", 5.0)
        cumulative = tracker.cumulative_accuracy()
        assert len(cumulative) == 3
        assert cumulative[0][1] == 1.0
        assert cumulative[1][1] == pytest.approx(0.5, abs=0.01)
        assert cumulative[2][1] == pytest.approx(2 / 3, abs=0.01)

    def test_average_regret(self, tmp_path):
        tracker = self._make_tracker(tmp_path)
        tracker.record("d1", "A", 0.8, "A", 5.0, engine_scores={"A": 5.0})
        tracker.record("d2", "A", 0.7, "B", 10.0, engine_scores={"A": 3.0})
        assert tracker.average_regret() >= 0.0

    def test_tag_accuracy(self, tmp_path):
        tracker = self._make_tracker(tmp_path)
        tracker.record("d1", "A", 0.8, "A", 5.0, tags=["rf"])
        tracker.record("d2", "A", 0.7, "A", 5.0, tags=["rf"])
        tracker.record("d3", "A", 0.9, "B", 5.0, tags=["network"])
        tag_acc = tracker.tag_accuracy()
        assert tag_acc["rf"] == 1.0
        assert tag_acc["network"] == 0.0

    def test_persistence(self, tmp_path):
        path = tmp_path / "persist.jsonl"
        tracker1 = OutcomeTracker(outcomes_path=path)
        tracker1.record("d1", "A", 0.8, "A", 5.0)
        tracker1.record("d2", "B", 0.7, "B", 5.0)
        del tracker1

        tracker2 = OutcomeTracker(outcomes_path=path)
        assert len(tracker2.entries()) == 2
        assert tracker2.accuracy() == 1.0

    def test_delete_entry(self, tmp_path):
        tracker = self._make_tracker(tmp_path)
        tracker.record("d1", "A", 0.8, "A", 5.0)
        tracker.record("d2", "B", 0.7, "B", 5.0)
        assert tracker.delete("d1") is True
        assert len(tracker.entries()) == 1
        assert tracker.delete("nonexistent") is False

    def test_summary_structure(self, tmp_path):
        tracker = self._make_tracker(tmp_path)
        tracker.record("d1", "A", 0.8, "A", 5.0, tags=["test"])
        s = tracker.summary()
        assert s["total_decisions"] == 1
        assert "accuracy_overall" in s
        assert "trend" in s
