import tempfile
from pathlib import Path

import pytest

from decision_maker.core.reasoning_trace import ReasoningTrace, TraceEntry


class TestReasoningTrace:
    def _make_trace(self, tmp_path: Path) -> ReasoningTrace:
        return ReasoningTrace(trace_path=tmp_path / "test_trace.jsonl")

    def test_empty_trace(self, tmp_path):
        trace = self._make_trace(tmp_path)
        assert trace.summary()["total_traces"] == 0

    def test_record_trace(self, tmp_path):
        trace = self._make_trace(tmp_path)
        entry = trace.record(
            problem_name="Vendor selection",
            complexity_score=0.4,
            recommended_mode="standard",
            engines_run=["MonteCarlo", "TOPSIS", "Sensitivity"],
            engines_skipped=["Bayesian", "Genetic"],
            skip_reasons={"Bayesian": "too few options", "Genetic": "no constraints"},
            threshold_verdict="decide",
            threshold_reasoning="Strong signal",
            routing_reasoning="Moderate complexity",
            dimension_scores={"options": 0.25, "factors": 0.3},
        )
        assert entry.decision_id.startswith("trace_")
        assert len(trace.entries()) == 1

    def test_persistence(self, tmp_path):
        path = tmp_path / "persist.jsonl"
        t1 = ReasoningTrace(trace_path=path)
        t1.record("p1", 0.3, "express", ["MC"], ["Bayesian"])
        del t1

        t2 = ReasoningTrace(trace_path=path)
        assert len(t2.entries()) == 1

    def test_routing_accuracy(self, tmp_path):
        trace = self._make_trace(tmp_path)
        trace.record("p1", 0.2, "express", ["MC"], ["Bayesian"])
        trace.record("p2", 0.4, "standard", ["MC", "TOPSIS"], ["Genetic"])
        trace.record("p3", 0.2, "express", ["MC"], ["Bayesian"])
        acc = trace.routing_accuracy()
        assert acc["total"] == 3
        assert acc["most_used_mode"] == "express"

    def test_get_entry(self, tmp_path):
        trace = self._make_trace(tmp_path)
        entry = trace.record("p1", 0.5, "standard", ["MC"], [])
        found = trace.get_entry(entry.decision_id)
        assert found is not None
        assert found.problem_name == "p1"
        assert trace.get_entry("nonexistent") is None

    def test_summary(self, tmp_path):
        trace = self._make_trace(tmp_path)
        trace.record("p1", 0.2, "express", ["MC"], ["Bayesian"])
        s = trace.summary()
        assert s["total_traces"] == 1
        assert "routing_accuracy" in s
