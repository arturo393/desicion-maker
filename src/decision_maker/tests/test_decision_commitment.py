"""
Decision ledger: a commitment is a decision a person took, with a date to check it and a metric the world can answer.
Run: uv run pytest src/decision_maker/tests/test_decision_commitment.py
Does NOT: test the CLI wiring (test_cli.py) or the calibration maths (test_calibration_scorer.py).
"""

from datetime import date, timedelta
from pathlib import Path

import pytest

from decision_maker.core.decision_commitment import DecisionCommitment, ledger_path

TODAY = date(2026, 10, 18)
NEXT_MONTH = (TODAY + timedelta(days=30)).isoformat()


def _ledger(tmp_path: Path) -> DecisionCommitment:
    return DecisionCommitment(commitments_path=tmp_path / "ledger.jsonl")


def _commit(ledger: DecisionCommitment, option: str = "A", confidence: float = 0.7, review: str = NEXT_MONTH):
    return ledger.create(
        chosen_option=option,
        confidence=confidence,
        success_metric="piloto operativo en faena",
        review_date=review,
        today=TODAY,
    )


class TestCreate:
    def test_records_the_decision(self, tmp_path):
        ledger = _ledger(tmp_path)
        c = _commit(ledger)
        assert c.chosen_option == "A"
        assert c.decision_id.startswith("commit_")
        assert c.review_date == NEXT_MONTH
        assert ledger.entries() == [c]

    def test_persists_across_instances(self, tmp_path):
        _commit(_ledger(tmp_path))
        assert len(_ledger(tmp_path).entries()) == 1

    @pytest.mark.parametrize("review", ["", "REVIEW NEEDED", "mañana"])
    def test_refuses_a_review_date_that_is_not_a_date(self, tmp_path, review):
        # "REVIEW NEEDED" was the default: 1300 of 1300 commitments carried it and none was ever reviewed.
        with pytest.raises(ValueError, match="review_date"):
            _commit(_ledger(tmp_path), review=review)

    def test_refuses_a_review_date_in_the_past(self, tmp_path):
        with pytest.raises(ValueError, match="past"):
            _commit(_ledger(tmp_path), review=(TODAY - timedelta(days=1)).isoformat())

    @pytest.mark.parametrize("metric", ["", "   ", "mean_score >= 0.62"])
    def test_refuses_a_metric_the_world_cannot_answer(self, tmp_path, metric):
        # The old default was the model's own mean score: a decision judged by the model that made it.
        with pytest.raises(ValueError, match="success_metric"):
            _ledger(tmp_path).create("A", 0.7, metric, NEXT_MONTH, today=TODAY)

    @pytest.mark.parametrize("confidence", [0.0, -0.1, 1.01])
    def test_refuses_a_confidence_outside_0_1(self, tmp_path, confidence):
        with pytest.raises(ValueError, match="confidence"):
            _commit(_ledger(tmp_path), confidence=confidence)

    def test_a_refused_commitment_leaves_nothing_behind(self, tmp_path):
        ledger = _ledger(tmp_path)
        with pytest.raises(ValueError, match="review_date"):
            _commit(ledger, review="")
        assert ledger.entries() == []
        assert not (tmp_path / "ledger.jsonl").exists()


class TestReview:
    def test_due_lists_open_decisions_whose_date_arrived(self, tmp_path):
        ledger = _ledger(tmp_path)
        soon = _commit(ledger, "A", review=(TODAY + timedelta(days=1)).isoformat())
        _commit(ledger, "B", review=(TODAY + timedelta(days=60)).isoformat())
        assert ledger.due(today=TODAY) == []
        assert ledger.due(today=TODAY + timedelta(days=1)) == [soon]

    def test_closed_decisions_are_not_due(self, tmp_path):
        ledger = _ledger(tmp_path)
        c = _commit(ledger)
        ledger.record_outcome(c.decision_id, was_successful=True)
        assert ledger.due(today=TODAY + timedelta(days=365)) == []

    def test_record_outcome_on_unknown_id(self, tmp_path):
        assert _ledger(tmp_path).record_outcome("nope", was_successful=True) is False

    def test_record_outcome_is_persisted(self, tmp_path):
        ledger = _ledger(tmp_path)
        c = _commit(ledger)
        assert ledger.record_outcome(c.decision_id, was_successful=False, actual_result="llegó tarde")
        reread = _ledger(tmp_path).entry(c.decision_id)
        assert reread is not None
        assert reread.outcome_recorded is True
        assert reread.was_successful is False
        assert reread.actual_result == "llegó tarde"


class TestCalibration:
    def test_empty_ledger_has_no_verdict(self, tmp_path):
        cal = _ledger(tmp_path).calibration()
        assert cal["num_predictions"] == 0

    def test_brier_reads_confidence_against_what_happened(self, tmp_path):
        ledger = _ledger(tmp_path)
        right = _commit(ledger, "A", confidence=0.9)
        wrong = _commit(ledger, "B", confidence=0.9)
        _commit(ledger, "C", confidence=0.6)  # open: must not count
        ledger.record_outcome(right.decision_id, was_successful=True)
        ledger.record_outcome(wrong.decision_id, was_successful=False)
        cal = ledger.calibration()
        assert cal["num_predictions"] == 2
        # ((0.9-1)^2 + (0.9-0)^2) / 2
        assert cal["brier_score"] == pytest.approx(0.41)

    def test_summary_counts(self, tmp_path):
        ledger = _ledger(tmp_path)
        a = _commit(ledger, "A")
        _commit(ledger, "B")
        ledger.record_outcome(a.decision_id, was_successful=True)
        s = ledger.summary(today=TODAY)
        assert s == {"total": 2, "closed": 1, "open": 1, "due": 0, "success_rate": 1.0}


def test_ledger_path_defaults_to_a_versioned_directory(monkeypatch):
    monkeypatch.delenv("DM_LEDGER_PATH", raising=False)
    assert ledger_path() == Path("decisions/ledger.jsonl")
    monkeypatch.setenv("DM_LEDGER_PATH", "/tmp/x.jsonl")
    assert ledger_path() == Path("/tmp/x.jsonl")


class TestPublishedSchema:
    """decisions/ledger.schema.json is the contract for readers outside this package.

    Conformance reads the producer — the Commitment dataclass and an entry create() really wrote —
    not a hand-written example, so a field added to the producer and not to the schema goes red.
    """

    SCHEMA = Path(__file__).resolve().parents[3] / "decisions" / "ledger.schema.json"

    def _schema(self) -> dict:
        import json

        return json.loads(self.SCHEMA.read_text(encoding="utf-8"))

    def test_schema_declares_exactly_the_producer_fields(self):
        from dataclasses import fields

        from decision_maker.core.decision_commitment import Commitment

        assert set(self._schema()["properties"]) == {f.name for f in fields(Commitment)}

    def test_a_written_line_validates(self, tmp_path):
        import json

        import jsonschema

        ledger = _ledger(tmp_path)
        c = _commit(ledger)
        ledger.record_outcome(c.decision_id, was_successful=True, actual_result="ok")
        line = json.loads((tmp_path / "ledger.jsonl").read_text(encoding="utf-8").splitlines()[0])
        jsonschema.validate(line, self._schema())

    def test_the_schema_can_fail(self):
        import jsonschema

        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate({"decision_id": "commit_x", "confidence": 1.5}, self._schema())
