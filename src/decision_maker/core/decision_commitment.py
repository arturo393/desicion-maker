"""
Decision commitment: structured commitment with deadline and success metric.
Usage: from decision_maker.core.decision_commitment import DecisionCommitment
Does NOT: Run decision algorithms or compute scores.
"""

from __future__ import annotations

__all__ = ["DecisionCommitment", "Commitment"]

import json
import logging
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np

from decision_maker.core.models import Statistics

logger = logging.getLogger(__name__)

DEFAULT_COMMITMENTS_PATH = "results/commitments.jsonl"


@dataclass
class Commitment:
    """A structured commitment to a decision (Parameter Object)."""

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
            self.timestamp = datetime.now(timezone.utc).isoformat()
        if not self.decision_id:
            self.decision_id = f"commit_{uuid.uuid4().hex[:12]}"


class DecisionCommitment:
    """
    Transforms a recommendation into a binding commitment.

    Based on the superforecasting principle: a recommendation without
    accountability is just an opinion. A commitment specifies:
    1. What you decided
    2. Why (reasoning trace)
    3. How you'll measure success (metric + threshold)
    4. When you'll review (deadline)
    5. When you'll reverse (exit criteria)
    6. What could kill you (pre-mortem)

    This closes the loop from "I recommend X" to "I commit to X,
    and here's how I'll know if I was wrong."
    """

    def __init__(self, commitments_path: str | Path | None = None):
        self.commitments_path = Path(commitments_path or DEFAULT_COMMITMENTS_PATH)
        self._entries: list[Commitment] = []
        self._load()

    def _load(self) -> None:
        if self.commitments_path.exists():
            try:
                with open(self.commitments_path) as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            data = json.loads(line)
                            self._entries.append(Commitment(**data))
            except Exception as e:
                logger.warning(f"Failed to load commitments: {e}")

    def _save(self) -> None:
        self.commitments_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.commitments_path, "w") as f:
            for entry in self._entries:
                f.write(json.dumps(asdict(entry)) + "\n")

    def create(
        self,
        chosen_option: str,
        mc_results: dict[str, Statistics],
        reasoning: str = "",
        confidence: float = 0.0,
        success_metric: str = "",
        success_threshold: float = 0.0,
        deadline: str = "",
        reversible: bool = True,
        exit_criteria: str = "",
        pre_mortem: str = "",
        tags: list[str] | None = None,
    ) -> Commitment:
        if not success_metric and chosen_option in mc_results:
            stats = mc_results[chosen_option]
            success_metric = f"mean_score >= {stats.mean_score:.2f}"
            success_threshold = stats.mean_score

        if not deadline:
            deadline = "REVIEW NEEDED"

        if not exit_criteria:
            exit_criteria = f"Revert if {chosen_option} score drops below {success_threshold * 0.8:.2f}"

        commitment = Commitment(
            chosen_option=chosen_option,
            reasoning=reasoning,
            confidence=confidence,
            success_metric=success_metric,
            success_threshold=success_threshold,
            deadline=deadline,
            reversible=reversible,
            exit_criteria=exit_criteria,
            pre_mortem=pre_mortem,
            tags=tags or [],
        )
        self._entries.append(commitment)
        self._save()
        logger.info(f"Commitment created: {commitment.decision_id} → {chosen_option}")
        return commitment

    def record_outcome(
        self,
        decision_id: str,
        was_successful: bool,
        actual_result: str = "",
        post_mortem: str = "",
    ) -> bool:
        for entry in self._entries:
            if entry.decision_id == decision_id:
                entry.outcome_recorded = True
                entry.was_successful = was_successful
                entry.actual_result = actual_result
                entry.post_mortem = post_mortem
                self._save()
                return True
        return False

    def commitment_accuracy(self) -> dict[str, Any]:
        recorded = [e for e in self._entries if e.outcome_recorded]
        if not recorded:
            return {"total_recorded": 0, "accuracy": 0.0}

        successful = sum(1 for e in recorded if e.was_successful)
        return {
            "total_recorded": len(recorded),
            "successful": successful,
            "accuracy": successful / len(recorded),
            "reversible_count": sum(1 for e in self._entries if e.reversible),
            "irreversible_count": sum(1 for e in self._entries if not e.reversible),
        }

    def pending_review(self) -> list[Commitment]:
        now = datetime.now(timezone.utc).isoformat()
        return [
            e for e in self._entries
            if not e.outcome_recorded and e.deadline != "REVIEW NEEDED"
        ]

    def entries(self) -> list[Commitment]:
        return list(self._entries)

    def get_entry(self, decision_id: str) -> Commitment | None:
        for entry in self._entries:
            if entry.decision_id == decision_id:
                return entry
        return None

    def summary(self) -> dict[str, Any]:
        n = len(self._entries)
        if n == 0:
            return {"total_commitments": 0}

        return {
            "total_commitments": n,
            "with_outcome": sum(1 for e in self._entries if e.outcome_recorded),
            "pending": sum(1 for e in self._entries if not e.outcome_recorded),
            "accuracy": self.commitment_accuracy(),
            "pending_review": len(self.pending_review()),
        }
