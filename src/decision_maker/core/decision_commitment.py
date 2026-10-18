"""
Decision ledger: the decisions a person actually took, each with a review date and a metric the world can answer.
Usage: DecisionCommitment().create("B", 0.7, "piloto operativo en faena", "2026-12-01"); .due(); .record_outcome(id, True)
Does NOT: run decision algorithms, or create a commitment by itself — an analysis run only drafts one (orchestrator).
"""

from __future__ import annotations

__all__ = ["DecisionCommitment", "Commitment", "ledger_path"]

import logging
import os
import re
import uuid
from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

from decision_maker.core.calibration_scorer import CalibrationScorer
from decision_maker.core.jsonl_store import JsonlStore
from decision_maker.core.outcome_tracker import OutcomeEntry

logger = logging.getLogger(__name__)

# Versioned on purpose, unlike results/: the ledger is the only record of what was decided and how it
# turned out, and calibration needs every entry. Until 2026-10-18 every analysis run wrote a commitment
# to results/ (ignored by git): 1300 entries, 1300 with deadline "REVIEW NEEDED", 3 outcomes ever.
DEFAULT_LEDGER_PATH = "decisions/ledger.jsonl"

# A metric that names one of the model's own statistics is the model grading itself.
_MODEL_STATISTIC = re.compile(r"\b(mean_score|success_rate|percentile_\d+|p\d{1,2}|cvar\w*|var_95|std_dev)\b")


def ledger_path() -> Path:
    """Where the ledger lives: $DM_LEDGER_PATH, else decisions/ledger.jsonl relative to the cwd."""
    return Path(os.getenv("DM_LEDGER_PATH") or DEFAULT_LEDGER_PATH)


@dataclass
class Commitment:
    """One decision taken (Parameter Object). The field names predate the ledger and stay for old files."""

    decision_id: str = ""
    timestamp: str = ""
    chosen_option: str = ""
    reasoning: str = ""
    confidence: float = 0.0
    success_metric: str = ""
    success_threshold: float = 0.0
    deadline: str = ""
    review_date: str = ""
    reversible: bool = True
    exit_criteria: str = ""
    pre_mortem: str = ""
    post_mortem: str = ""
    outcome_recorded: bool = False
    was_successful: bool = False
    actual_result: str = ""
    tags: list[str] = field(default_factory=list)

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(UTC).isoformat()
        if not self.decision_id:
            self.decision_id = f"commit_{uuid.uuid4().hex[:12]}"


class DecisionCommitment(JsonlStore[Commitment]):
    """
    The decision ledger. A commitment answers, before the fact:
    what was chosen, how sure we were, how we will know it worked, and when we will look.

    Its value is the closed entries: confidence against what happened is the only measurement of
    whether this framework's recommendations deserve the confidence they print.
    """

    # ── Construct ────────────────────────────────────────────────────
    def __init__(self, commitments_path: str | Path | None = None):
        super().__init__(commitments_path or ledger_path(), DEFAULT_LEDGER_PATH, id_field="decision_id")

    def _deserialize(self, data: dict[str, Any]) -> Commitment:
        return Commitment(**data)

    # ── Control ──────────────────────────────────────────────────────
    def create(
        self,
        chosen_option: str,
        confidence: float,
        success_metric: str,
        review_date: str,
        *,
        reasoning: str = "",
        reversible: bool = True,
        exit_criteria: str = "",
        pre_mortem: str = "",
        tags: list[str] | None = None,
        today: date | None = None,
    ) -> Commitment:
        """Record a decision. Refuses anything that could never be reviewed or scored."""
        review = _parse_review_date(review_date)
        if review < (today or date.today()):
            raise ValueError(f"review_date {review_date} is in the past: a review that already happened is not a plan")
        if not success_metric.strip():
            raise ValueError("success_metric is empty: say what you will observe if this worked")
        if _MODEL_STATISTIC.search(success_metric):
            raise ValueError(
                f"success_metric {success_metric!r} names a model statistic; the model cannot grade "
                "its own recommendation. Name something you will observe."
            )
        if not 0.0 < confidence <= 1.0:
            raise ValueError(f"confidence {confidence} must be in (0, 1]: it is the probability this works")

        commitment = Commitment(
            chosen_option=chosen_option,
            reasoning=reasoning,
            confidence=confidence,
            success_metric=success_metric.strip(),
            review_date=review.isoformat(),
            reversible=reversible,
            exit_criteria=exit_criteria,
            pre_mortem=pre_mortem,
            tags=tags or [],
        )
        self._entries.append(commitment)
        self._save()
        logger.info(f"Commitment {commitment.decision_id}: {chosen_option}, review on {commitment.review_date}")
        return commitment

    def record_outcome(
        self,
        decision_id: str,
        was_successful: bool,
        actual_result: str = "",
        post_mortem: str = "",
    ) -> bool:
        """Close a decision with what happened. False if the id is not in the ledger."""
        entry = self.entry(decision_id)
        if entry is None:
            return False
        entry.outcome_recorded = True
        entry.was_successful = was_successful
        entry.actual_result = actual_result
        entry.post_mortem = post_mortem
        self._save()
        return True

    # ── Query ────────────────────────────────────────────────────────
    def open(self) -> list[Commitment]:
        return [e for e in self._entries if not e.outcome_recorded]

    def closed(self) -> list[Commitment]:
        return [e for e in self._entries if e.outcome_recorded]

    def due(self, today: date | None = None) -> list[Commitment]:
        """Open decisions whose review date has arrived, oldest first."""
        limit = (today or date.today()).isoformat()
        due = [e for e in self.open() if e.review_date and e.review_date <= limit]
        return sorted(due, key=lambda e: e.review_date)

    def calibration(self) -> dict[str, Any]:
        """Brier, ECE and verdict over closed decisions: stated confidence against what happened."""
        scored = [
            OutcomeEntry(decision_id=e.decision_id, predicted_confidence=e.confidence, was_correct=e.was_successful)
            for e in self.closed()
        ]
        return CalibrationScorer.score(scored)

    def summary(self, today: date | None = None) -> dict[str, Any]:
        closed = self.closed()
        return {
            "total": len(self._entries),
            "closed": len(closed),
            "open": len(self._entries) - len(closed),
            "due": len(self.due(today)),
            "success_rate": (sum(e.was_successful for e in closed) / len(closed)) if closed else None,
        }


def _parse_review_date(value: str) -> date:
    try:
        return date.fromisoformat(value.strip())
    except (ValueError, AttributeError) as exc:
        raise ValueError(f"review_date {value!r} is not an ISO date (YYYY-MM-DD)") from exc
