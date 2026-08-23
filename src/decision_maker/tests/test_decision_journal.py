import tempfile
from pathlib import Path

import pytest

from decision_maker.core.decision_journal import DecisionJournal, JournalEntry
from decision_maker.core.models import Factor


class TestDecisionJournal:
    def _make_journal(self, tmp_path: Path) -> DecisionJournal:
        return DecisionJournal(journal_path=tmp_path / "test_journal.jsonl")

    def test_empty_journal(self, tmp_path):
        journal = self._make_journal(tmp_path)
        assert journal.summary()["total_entries"] == 0

    def test_log_decision(self, tmp_path):
        journal = self._make_journal(tmp_path)
        entry = journal.log_decision(
            context="Q3 planning",
            question="Which vendor for RF testing?",
            options=["Keysight", "Rohde", "Anritsu"],
            factors=[Factor("Cost", 0.4, maximize=False), Factor("Performance", 0.6, maximize=True)],
            assumptions=["Budget stays flat"],
            missing_info=["Long-term support pricing"],
            winner="Keysight",
            confidence=0.75,
            reasoning="Best balance of cost and performance",
            engine_used="TOPSIS",
            tags=["rf", "vendor"],
        )
        assert entry.decision_id.startswith("dec_")
        assert entry.winner == "Keysight"
        assert len(journal.entries()) == 1

    def test_log_outcome(self, tmp_path):
        journal = self._make_journal(tmp_path)
        entry = journal.log_decision(
            context="test", question="test q", options=["A", "B"],
        )
        result = journal.log_outcome(
            decision_id=entry.decision_id,
            actual_winner="A",
            actual_score=8.0,
            what_changed="Vendor delivered early",
            lessons_learned="Lead time assumptions were conservative",
        )
        assert result is True
        updated = journal.get_entry(entry.decision_id)
        assert any("OUTCOME:" in a for a in updated.assumptions_made)

    def test_log_outcome_nonexistent(self, tmp_path):
        journal = self._make_journal(tmp_path)
        assert journal.log_outcome("nonexistent", "A", 5.0) is False

    def test_persistence(self, tmp_path):
        path = tmp_path / "persist.jsonl"
        j1 = DecisionJournal(journal_path=path)
        j1.log_decision(context="c", question="q", options=["A"])
        del j1

        j2 = DecisionJournal(journal_path=path)
        assert len(j2.entries()) == 1

    def test_search(self, tmp_path):
        journal = self._make_journal(tmp_path)
        journal.log_decision(context="RF testing", question="Which antenna?", options=["A"])
        journal.log_decision(context="Budget review", question="Cut costs?", options=["A"])
        results = journal.search("antenna")
        assert len(results) == 1
        assert "antenna" in results[0].question.lower()

    def test_detect_patterns(self, tmp_path):
        journal = self._make_journal(tmp_path)
        journal.log_decision(
            context="c", question="q", options=["A"],
            assumptions=["budget flat", "budget flat"],
            tags=["rf"],
        )
        journal.log_decision(
            context="c2", question="q2", options=["A"],
            assumptions=["budget flat"],
            tags=["rf", "network"],
        )
        patterns = journal.detect_patterns()
        assert patterns["total"] == 2
        assert len(patterns["patterns"]) > 0

    def test_summary(self, tmp_path):
        journal = self._make_journal(tmp_path)
        journal.log_decision(context="c", question="q", options=["A"], confidence=0.8)
        journal.log_decision(context="c2", question="q2", options=["B"], confidence=0.6)
        s = journal.summary()
        assert s["total_entries"] == 2
        assert s["avg_confidence"] == pytest.approx(0.7, abs=0.01)
        assert s["without_outcome"] == 2

    def test_get_entry(self, tmp_path):
        journal = self._make_journal(tmp_path)
        entry = journal.log_decision(context="c", question="q", options=["A"])
        found = journal.get_entry(entry.decision_id)
        assert found is not None
        assert found.question == "q"
        assert journal.get_entry("nonexistent") is None
