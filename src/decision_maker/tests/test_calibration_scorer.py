import numpy as np
import pytest

from decision_maker.core.outcome_tracker import OutcomeEntry
from decision_maker.core.calibration_scorer import CalibrationScorer


class TestCalibrationScorer:
    def _make_entries(self, confidences: list[float], correct: list[bool]) -> list[OutcomeEntry]:
        return [
            OutcomeEntry(
                decision_id=f"d{i}",
                predicted_winner="A",
                predicted_confidence=c,
                actual_winner="A" if was_correct else "B",
                actual_score=5.0,
                was_correct=was_correct,
            )
            for i, (c, was_correct) in enumerate(zip(confidences, correct))
        ]

    def test_empty_entries(self):
        result = CalibrationScorer.score([])
        assert result["num_predictions"] == 0
        assert result["verdict"] == "no_data"

    def test_perfect_calibration(self):
        np.random.seed(42)
        entries = []
        for i in range(100):
            conf = 0.7
            was_correct = np.random.random() < conf
            entries.append(OutcomeEntry(
                decision_id=f"d{i}", predicted_winner="A",
                predicted_confidence=conf, actual_winner="A" if was_correct else "B",
                actual_score=5.0, was_correct=was_correct,
            ))
        result = CalibrationScorer.score(entries)
        assert result["ece"] < 0.3
        assert result["is_calibrated"] or result["verdict"] in ("mildly_miscalibrated", "well_calibrated")

    def test_overconfident(self):
        entries = self._make_entries(
            [0.9] * 50 + [0.1] * 50,
            [True] * 10 + [False] * 40 + [True] * 40 + [False] * 10,
        )
        result = CalibrationScorer.score(entries)
        assert result["ece"] > 0.0
        assert result["num_predictions"] == 100

    def test_bins_count(self):
        entries = self._make_entries([0.5] * 20, [True] * 15 + [False] * 5)
        result = CalibrationScorer.score(entries, bin_count=5)
        assert len(result["bins"]) == 5

    def test_brier_score_range(self):
        entries = self._make_entries([0.8] * 50, [True] * 40 + [False] * 10)
        result = CalibrationScorer.score(entries)
        assert 0.0 <= result["brier_score"] <= 1.0

    def test_sharpness(self):
        entries = self._make_entries([0.5] * 100, [True] * 50 + [False] * 50)
        result = CalibrationScorer.score(entries)
        assert result["sharpness"] == pytest.approx(0.0, abs=0.01)

        entries2 = self._make_entries(
            [0.1] * 50 + [0.9] * 50,
            [True] * 5 + [False] * 45 + [True] * 45 + [False] * 5,
        )
        result2 = CalibrationScorer.score(entries2)
        assert result2["sharpness"] > result["sharpness"]

    def test_verdict_insufficient_data(self):
        entries = self._make_entries([0.8] * 5, [True] * 4 + [False] * 1)
        result = CalibrationScorer.score(entries)
        assert result["verdict"] == "insufficient_data"

    def test_confidence_distribution(self):
        entries = self._make_entries([0.3, 0.5, 0.7, 0.9], [True, False, True, True])
        result = CalibrationScorer.score(entries)
        assert result["confidence_distribution"]["mean"] == pytest.approx(0.6, abs=0.01)
        assert result["confidence_distribution"]["std"] > 0.0

    def test_mce_is_max_bin_error(self):
        entries = self._make_entries(
            [0.2] * 30 + [0.8] * 30,
            [True] * 5 + [False] * 25 + [True] * 25 + [False] * 5,
        )
        result = CalibrationScorer.score(entries)
        assert result["mce"] >= result["ece"]
