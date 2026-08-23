"""
Structured decision journal: record what you saw, assumed, decided, and what happened.
Usage: from decision_maker.core.decision_journal import DecisionJournal
Does NOT: Run decision algorithms or compute scores (see outcome_tracker).
"""

from __future__ import annotations

__all__ = ["DecisionJournal", "JournalEntry"]

import json
import logging
from datetime import datetime, timezone
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any

import numpy as np

from decision_maker.core.models import Factor, Statistics

logger = logging.getLogger(__name__)

DEFAULT_JOURNAL_PATH = "results/decision_journal.jsonl"


@dataclass
class JournalEntry:
    """Structured record of a single decision moment (Parameter Object)."""

    decision_id: str = ""
    timestamp: str = ""
    context: str = ""
    question: str = ""
    options_considered: list[str] = field(default_factory=list)
    factors_visible: list[dict[str, Any]] = field(default_factory=list)
    assumptions_made: list[str] = field(default_factory=list)
    information_missing: list[str] = field(default_factory=list)
    winner: str = ""
    confidence: float = 0.0
    reasoning: str = ""
    engine_used: str = ""
    engine_scores: dict[str, float] = field(default_factory=dict)
    alternative_views: list[str] = field(default_factory=list)
    pre_commitment: str = ""
    tags: list[str] = field(default_factory=list)

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()
        if not self.decision_id:
            self.decision_id = f"dec_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"


class DecisionJournal:
    """
    Structured bitácora for decision-making discipline.

    Based on Tetlock's superforecasting methodology:
    1. State the question clearly BEFORE deciding
    2. Record what you see and what you're missing
    3. Make the decision with explicit reasoning
    4. Record what actually happened
    5. Compare prediction vs outcome to detect bias patterns
    """

    def __init__(self, journal_path: str | Path | None = None):
        self.journal_path = Path(journal_path or DEFAULT_JOURNAL_PATH)
        self._entries: list[JournalEntry] = []
        self._load()

    def _load(self) -> None:
        if self.journal_path.exists():
            try:
                with open(self.journal_path) as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            data = json.loads(line)
                            self._entries.append(JournalEntry(**data))
            except Exception as e:
                logger.warning(f"Failed to load journal: {e}")

    def _save(self) -> None:
        self.journal_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.journal_path, "w") as f:
            for entry in self._entries:
                f.write(json.dumps(asdict(entry)) + "\n")

    def log_decision(
        self,
        context: str,
        question: str,
        options: list[str],
        factors: list[Factor] | None = None,
        assumptions: list[str] | None = None,
        missing_info: list[str] | None = None,
        winner: str = "",
        confidence: float = 0.0,
        reasoning: str = "",
        engine_used: str = "",
        mc_results: dict[str, Statistics] | None = None,
        alternative_views: list[str] | None = None,
        pre_commitment: str = "",
        tags: list[str] | None = None,
    ) -> JournalEntry:
        factors_visible = []
        if factors:
            factors_visible = [{"name": f.name, "weight": f.weight, "maximize": f.maximize} for f in factors]

        engine_scores = {}
        if mc_results:
            engine_scores = {name: s.mean_score for name, s in mc_results.items()}

        entry = JournalEntry(
            context=context,
            question=question,
            options_considered=options,
            factors_visible=factors_visible,
            assumptions_made=assumptions or [],
            information_missing=missing_info or [],
            winner=winner,
            confidence=confidence,
            reasoning=reasoning,
            engine_used=engine_used,
            engine_scores=engine_scores,
            alternative_views=alternative_views or [],
            pre_commitment=pre_commitment,
            tags=tags or [],
        )
        self._entries.append(entry)
        self._save()
        logger.info(f"Journal entry: {entry.decision_id} — {question[:60]}")
        return entry

    def log_outcome(
        self,
        decision_id: str,
        actual_winner: str,
        actual_score: float,
        what_changed: str = "",
        lessons_learned: str = "",
    ) -> bool:
        for entry in self._entries:
            if entry.decision_id == decision_id:
                entry.tags.append(f"outcome:{actual_winner}")
                if what_changed:
                    entry.assumptions_made.append(f"OUTCOME: {what_changed}")
                if lessons_learned:
                    entry.assumptions_made.append(f"LESSON: {lessons_learned}")
                self._save()
                return True
        return False

    def detect_patterns(self) -> dict[str, Any]:
        if not self._entries:
            return {"total": 0, "patterns": []}

        assumption_counts: dict[str, int] = {}
        missing_counts: dict[str, int] = {}
        tag_counts: dict[str, int] = {}
        confidence_values = []
        engine_usage: dict[str, int] = {}

        for entry in self._entries:
            for a in entry.assumptions_made:
                assumption_counts[a] = assumption_counts.get(a, 0) + 1
            for m in entry.information_missing:
                missing_counts[m] = missing_counts.get(m, 0) + 1
            for tag in entry.tags:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
            confidence_values.append(entry.confidence)
            if entry.engine_used:
                engine_usage[entry.engine_used] = engine_usage.get(entry.engine_used, 0) + 1

        patterns = []
        if assumption_counts:
            top_assumptions = sorted(assumption_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            patterns.append({"type": "recurring_assumptions", "items": top_assumptions})
        if missing_counts:
            top_missing = sorted(missing_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            patterns.append({"type": "recurring_information_gaps", "items": top_missing})
        if confidence_values:
            avg_conf = float(np.mean(confidence_values))
            patterns.append({"type": "confidence_level", "avg": avg_conf, "count": len(confidence_values)})

        return {
            "total": len(self._entries),
            "patterns": patterns,
            "tag_distribution": tag_counts,
            "engine_usage": engine_usage,
            "avg_confidence": float(np.mean(confidence_values)) if confidence_values else 0.0,
        }

    def entries(self) -> list[JournalEntry]:
        return list(self._entries)

    def get_entry(self, decision_id: str) -> JournalEntry | None:
        for entry in self._entries:
            if entry.decision_id == decision_id:
                return entry
        return None

    def search(self, query: str) -> list[JournalEntry]:
        query_lower = query.lower()
        return [
            e for e in self._entries
            if query_lower in e.question.lower()
            or query_lower in e.context.lower()
            or query_lower in e.reasoning.lower()
            or any(query_lower in tag.lower() for tag in e.tags)
        ]

    def summary(self) -> dict[str, Any]:
        n = len(self._entries)
        if n == 0:
            return {"total_entries": 0}

        with_outcome = sum(1 for e in self._entries if any(t.startswith("outcome:") for t in e.tags))
        return {
            "total_entries": n,
            "with_outcome": with_outcome,
            "without_outcome": n - with_outcome,
            "avg_confidence": float(np.mean([e.confidence for e in self._entries])),
            "patterns": self.detect_patterns(),
        }
