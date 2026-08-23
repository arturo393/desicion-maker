"""
Reasoning trace: record WHY a specific engine suite was chosen for a problem.
Usage: from decision_maker.core.reasoning_trace import ReasoningTrace
Does NOT: Run decision algorithms or compute scores.
"""

from __future__ import annotations

__all__ = ["ReasoningTrace", "TraceEntry"]

import json
import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np

logger = logging.getLogger(__name__)

DEFAULT_TRACE_PATH = "results/reasoning_traces.jsonl"


@dataclass
class TraceEntry:
    """Records why a specific routing decision was made (Parameter Object)."""

    decision_id: str = ""
    timestamp: str = ""
    problem_name: str = ""
    complexity_score: float = 0.0
    recommended_mode: str = ""
    engines_run: list[str] = field(default_factory=list)
    engines_skipped: list[str] = field(default_factory=list)
    skip_reasons: dict[str, str] = field(default_factory=dict)
    threshold_verdict: str = ""
    threshold_reasoning: str = ""
    routing_reasoning: str = ""
    dimension_scores: dict[str, float] = field(default_factory=dict)

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()
        if not self.decision_id:
            self.decision_id = f"trace_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"


class ReasoningTrace:
    """
    Records the reasoning behind routing decisions.

    When the adaptive router selects engines, it's making a meta-decision
    about how to make a decision. This trace captures WHY that meta-decision
    was made, enabling auditing and learning from routing mistakes.
    """

    def __init__(self, trace_path: str | Path | None = None):
        self.trace_path = Path(trace_path or DEFAULT_TRACE_PATH)
        self._entries: list[TraceEntry] = []
        self._load()

    def _load(self) -> None:
        if self.trace_path.exists():
            try:
                with open(self.trace_path) as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            data = json.loads(line)
                            self._entries.append(TraceEntry(**data))
            except Exception as e:
                logger.warning(f"Failed to load traces: {e}")

    def _save(self) -> None:
        self.trace_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.trace_path, "w") as f:
            for entry in self._entries:
                f.write(json.dumps(asdict(entry)) + "\n")

    def record(
        self,
        problem_name: str,
        complexity_score: float,
        recommended_mode: str,
        engines_run: list[str],
        engines_skipped: list[str],
        skip_reasons: dict[str, str] | None = None,
        threshold_verdict: str = "",
        threshold_reasoning: str = "",
        routing_reasoning: str = "",
        dimension_scores: dict[str, float] | None = None,
    ) -> TraceEntry:
        entry = TraceEntry(
            problem_name=problem_name,
            complexity_score=complexity_score,
            recommended_mode=recommended_mode,
            engines_run=engines_run,
            engines_skipped=engines_skipped,
            skip_reasons=skip_reasons or {},
            threshold_verdict=threshold_verdict,
            threshold_reasoning=threshold_reasoning,
            routing_reasoning=routing_reasoning,
            dimension_scores=dimension_scores or {},
        )
        self._entries.append(entry)
        self._save()
        logger.info(f"Trace recorded: {entry.decision_id} — {recommended_mode} ({len(engines_run)} engines)")
        return entry

    def entries(self) -> list[TraceEntry]:
        return list(self._entries)

    def get_entry(self, decision_id: str) -> TraceEntry | None:
        for entry in self._entries:
            if entry.decision_id == decision_id:
                return entry
        return None

    def routing_accuracy(self) -> dict[str, Any]:
        if not self._entries:
            return {"total": 0, "by_mode": {}}

        by_mode: dict[str, list[TraceEntry]] = {}
        for entry in self._entries:
            by_mode.setdefault(entry.recommended_mode, []).append(entry)

        mode_stats = {}
        for mode, entries in by_mode.items():
            avg_engines = float(np.mean([len(e.engines_run) for e in entries]))
            avg_skip = float(np.mean([len(e.engines_skipped) for e in entries]))
            mode_stats[mode] = {
                "count": len(entries),
                "avg_engines_run": avg_engines,
                "avg_engines_skipped": avg_skip,
            }

        return {
            "total": len(self._entries),
            "by_mode": mode_stats,
            "most_used_mode": max(by_mode, key=lambda m: len(by_mode[m])) if by_mode else None,
        }

    def summary(self) -> dict[str, Any]:
        if not self._entries:
            return {"total_traces": 0}

        routing = self.routing_accuracy()
        return {
            "total_traces": routing["total"],
            "routing_accuracy": routing,
            "recent_verdicts": [
                {"mode": e.recommended_mode, "verdict": e.threshold_verdict, "complexity": e.complexity_score}
                for e in self._entries[-5:]
            ],
        }
