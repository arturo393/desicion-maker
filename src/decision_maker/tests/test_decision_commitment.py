import tempfile
from pathlib import Path

import pytest

from decision_maker.core.decision_commitment import DecisionCommitment, Commitment
from decision_maker.core.models import Statistics


class TestDecisionCommitment:
    def _make_commitment(self, tmp_path: Path) -> DecisionCommitment:
        return DecisionCommitment(commitments_path=tmp_path / "test_commitments.jsonl")

    def _make_stats(self, name: str, mean: float) -> Statistics:
        return Statistics(
            option_name=name, mean_score=mean, std_dev=1.0,
            min_score=mean - 2, max_score=mean + 2,
            percentile_5=mean - 1.645, percentile_95=mean + 1.645,
            success_rate=0.7, factor_stats={}, var_95=mean - 1.645, cvar_95=mean - 2,
        )

    def test_create_commitment(self, tmp_path):
        c = self._make_commitment(tmp_path)
        mc = {"OptA": self._make_stats("OptA", 5.0)}
        commitment = c.create(chosen_option="OptA", mc_results=mc, reasoning="Best option")
        assert commitment.chosen_option == "OptA"
        assert commitment.decision_id.startswith("commit_")
        assert len(c.entries()) == 1

    def test_persistence(self, tmp_path):
        path = tmp_path / "persist.jsonl"
        c1 = DecisionCommitment(commitments_path=path)
        c1.create("OptA", {"OptA": self._make_stats("OptA", 5.0)})
        del c1

        c2 = DecisionCommitment(commitments_path=path)
        assert len(c2.entries()) == 1

    def test_record_outcome(self, tmp_path):
        c = self._make_commitment(tmp_path)
        commitment = c.create("OptA", {"OptA": self._make_stats("OptA", 5.0)})
        result = c.record_outcome(commitment.decision_id, was_successful=True, actual_result="Worked great")
        assert result is True
        updated = c.get_entry(commitment.decision_id)
        assert updated.was_successful is True

    def test_record_outcome_nonexistent(self, tmp_path):
        c = self._make_commitment(tmp_path)
        assert c.record_outcome("nonexistent", was_successful=True) is False

    def test_commitment_accuracy(self, tmp_path):
        c = self._make_commitment(tmp_path)
        c1 = c.create("A", {"A": self._make_stats("A", 5.0)})
        c2 = c.create("B", {"B": self._make_stats("B", 5.0)})
        c.record_outcome(c1.decision_id, was_successful=True)
        c.record_outcome(c2.decision_id, was_successful=False)
        acc = c.commitment_accuracy()
        assert acc["total_recorded"] == 2
        assert acc["accuracy"] == pytest.approx(0.5, abs=0.01)

    def test_pending_review(self, tmp_path):
        c = self._make_commitment(tmp_path)
        c.create("A", {"A": self._make_stats("A", 5.0)}, deadline="2026-12-31")
        pending = c.pending_review()
        assert len(pending) == 1

    def test_summary(self, tmp_path):
        c = self._make_commitment(tmp_path)
        c.create("A", {"A": self._make_stats("A", 5.0)})
        s = c.summary()
        assert s["total_commitments"] == 1
        assert s["pending"] == 1

    def test_empty_commitments(self, tmp_path):
        c = self._make_commitment(tmp_path)
        assert c.summary()["total_commitments"] == 0
