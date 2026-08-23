"""
Outcome tracking engine: record real results vs predictions and learn from feedback.
Usage: from decision_maker.core.outcome_tracker import OutcomeTracker
Does NOT: Run decision algorithms or produce rankings.
"""

from __future__ import annotations

__all__ = ["OutcomeTracker", "OutcomeEntry"]

import json
import logging
from datetime import datetime, timezone
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any

import numpy as np

from decision_maker.core.models import Statistics

logger = logging.getLogger(__name__)

DEFAULT_OUTCOMES_PATH = "results/outcomes.jsonl"


@dataclass
class OutcomeEntry:
    """Records what happened after a decision was made (Parameter Object)."""

    decision_id: str
    timestamp: str = ""
    predicted_winner: str = ""
    predicted_confidence: float = 0.0
    actual_winner: str = ""
    actual_score: float = 0.0
    options_evaluated: list[str] = field(default_factory=list)
    factors_used: list[str] = field(default_factory=list)
    engine_scores: dict[str, float] = field(default_factory=dict)
    was_correct: bool = False
    regret: float = 0.0
    notes: str = ""
    tags: list[str] = field(default_factory=list)

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()


class OutcomeTracker:
    """
    Records decision outcomes and computes learning metrics.

    Tracks: prediction accuracy, regret (what you left on the table),
    cumulative accuracy over time, and tag-based pattern detection.
    """

    def __init__(self, outcomes_path: str | Path | None = None):
        self.outcomes_path = Path(outcomes_path or DEFAULT_OUTCOMES_PATH)
        self._entries: list[OutcomeEntry] = []
        self._load()

    def _load(self) -> None:
        if self.outcomes_path.exists():
            try:
                with open(self.outcomes_path) as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            data = json.loads(line)
                            self._entries.append(OutcomeEntry(**data))
            except Exception as e:
                logger.warning(f"Failed to load outcomes: {e}")

    def _save(self) -> None:
        self.outcomes_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.outcomes_path, "w") as f:
            for entry in self._entries:
                f.write(json.dumps(asdict(entry)) + "\n")

    def record(
        self,
        decision_id: str,
        predicted_winner: str,
        predicted_confidence: float,
        actual_winner: str,
        actual_score: float,
        options_evaluated: list[str] | None = None,
        factors_used: list[str] | None = None,
        engine_scores: dict[str, float] | None = None,
        notes: str = "",
        tags: list[str] | None = None,
    ) -> OutcomeEntry:
        was_correct = predicted_winner == actual_winner
        best_actual = actual_score
        predicted_score = engine_scores.get(predicted_winner, 0.0) if engine_scores else 0.0
        regret = best_actual - predicted_score if was_correct else 0.0

        entry = OutcomeEntry(
            decision_id=decision_id,
            predicted_winner=predicted_winner,
            predicted_confidence=predicted_confidence,
            actual_winner=actual_winner,
            actual_score=actual_score,
            options_evaluated=options_evaluated or [],
            factors_used=factors_used or [],
            engine_scores=engine_scores or {},
            was_correct=was_correct,
            regret=regret,
            notes=notes,
            tags=tags or [],
        )
        self._entries.append(entry)
        self._save()
        logger.info(f"Recorded outcome: {decision_id} — {'CORRECT' if was_correct else 'WRONG'}")
        return entry

    def accuracy(self, last_n: int | None = None) -> float:
        entries = self._entries[-last_n:] if last_n else self._entries
        if not entries:
            return 0.0
        correct = sum(1 for e in entries if e.was_correct)
        return correct / len(entries)

    def cumulative_accuracy(self) -> list[tuple[str, float]]:
        result = []
        correct_so_far = 0
        for i, entry in enumerate(self._entries, 1):
            if entry.was_correct:
                correct_so_far += 1
            result.append((entry.decision_id, correct_so_far / i))
        return result

    def average_regret(self, last_n: int | None = None) -> float:
        entries = self._entries[-last_n:] if last_n else self._entries
        if not entries:
            return 0.0
        return float(np.mean([e.regret for e in entries]))

    def tag_accuracy(self) -> dict[str, float]:
        tag_correct: dict[str, int] = {}
        tag_total: dict[str, int] = {}
        for entry in self._entries:
            for tag in entry.tags:
                tag_total[tag] = tag_total.get(tag, 0) + 1
                if entry.was_correct:
                    tag_correct[tag] = tag_correct.get(tag, 0) + 1
        return {tag: tag_correct.get(tag, 0) / total for tag, total in tag_total.items()}

    def summary(self) -> dict[str, Any]:
        n = len(self._entries)
        if n == 0:
            return {"total_decisions": 0, "accuracy": 0.0, "avg_regret": 0.0}

        recent_10 = self.accuracy(last_n=min(10, n))
        recent_50 = self.accuracy(last_n=min(50, n))
        overall = self.accuracy()

        return {
            "total_decisions": n,
            "accuracy_overall": overall,
            "accuracy_last_10": recent_10,
            "accuracy_last_50": recent_50,
            "avg_regret": self.average_regret(),
            "tag_accuracy": self.tag_accuracy(),
            "best_tag": max(self.tag_accuracy(), key=self.tag_accuracy().get) if self.tag_accuracy() else None,
            "worst_tag": min(self.tag_accuracy(), key=self.tag_accuracy().get) if self.tag_accuracy() else None,
            "trend": "improving" if recent_10 > overall else "declining" if recent_10 < overall else "stable",
        }

    def entries(self) -> list[OutcomeEntry]:
        return list(self._entries)

    def delete(self, decision_id: str) -> bool:
        before = len(self._entries)
        self._entries = [e for e in self._entries if e.decision_id != decision_id]
        if len(self._entries) < before:
            self._save()
            return True
        return False
