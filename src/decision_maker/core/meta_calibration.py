"""
Meta-calibration engine: measure whether the adaptive router chose the right mode.
Usage: from decision_maker.core.meta_calibration import MetaCalibration
Does NOT: Run decision algorithms or compute routing (see adaptive_router).
"""

from __future__ import annotations

__all__ = ["MetaCalibration", "MetaCalibrationResult"]

import logging
from dataclasses import dataclass
from typing import Any


from decision_maker.core.outcome_tracker import OutcomeEntry
from decision_maker.core.reasoning_trace import TraceEntry

logger = logging.getLogger(__name__)


@dataclass
class MetaCalibrationResult:
    """Measures whether routing decisions were correct in hindsight (Parameter Object)."""

    total_routed: int
    mode_accuracy: dict[str, float]
    complexity_vs_outcome: float
    should_have_used_advanced: int
    should_have_used_express: int
    over_engineered: int
    under_engineered: int
    routing_quality: float
    verdict: str
    reasoning: str


class MetaCalibration:
    """
    Meta-calibration: did the router choose the right engine suite?

    This measures the second-order question: not "did the engines work?"
    but "did we use the RIGHT engines for this problem?"

    Compares routing decisions (from ReasoningTrace) against actual outcomes
    (from OutcomeTracker) to detect:
    - Over-engineering: used advanced mode for a simple problem
    - Under-engineering: used express mode for a complex problem
    - Correct routing: matched complexity to outcome quality
    """

    @staticmethod
    def evaluate(
        traces: list[TraceEntry],
        outcomes: list[OutcomeEntry],
    ) -> MetaCalibrationResult:
        if not traces:
            return MetaCalibrationResult(
                total_routed=0, mode_accuracy={}, complexity_vs_outcome=0.0,
                should_have_used_advanced=0, should_have_used_express=0,
                over_engineered=0, under_engineered=0, routing_quality=0.0,
                verdict="no_data", reasoning="No routing traces to evaluate",
            )

        outcome_map = {e.decision_id: e for e in outcomes}

        mode_correct: dict[str, list[bool]] = {}
        over_engineered = 0
        under_engineered = 0

        for trace in traces:
            outcome = outcome_map.get(trace.decision_id)
            if not outcome:
                continue

            mode = trace.recommended_mode
            mode_correct.setdefault(mode, []).append(outcome.was_correct)

            if trace.complexity_score < 0.3 and mode in ("standard", "advanced"):
                over_engineered += 1
            elif trace.complexity_score > 0.6 and mode in ("express",):
                under_engineered += 1

        mode_accuracy = {}
        for mode, results in mode_correct.items():
            mode_accuracy[mode] = sum(results) / len(results) if results else 0.0

        total_with_outcomes = sum(len(v) for v in mode_correct.values())
        overall_accuracy = sum(sum(v) for v in mode_correct.values()) / max(total_with_outcomes, 1)

        total_traces_with_outcomes = len([t for t in traces if t.decision_id in outcome_map])
        over_ratio = over_engineered / max(total_traces_with_outcomes, 1)
        under_ratio = under_engineered / max(total_traces_with_outcomes, 1)
        routing_quality = overall_accuracy * (1.0 - over_ratio * 0.3 - under_ratio * 0.3)

        if routing_quality > 0.7 and over_ratio < 0.1 and under_ratio < 0.1:
            verdict = "well_routed"
            reasoning = (
                f"Router quality {routing_quality:.2f}. "
                f"Engine suites match problem complexity. "
                f"Over-engineering {over_ratio:.0%}, under-engineering {under_ratio:.0%}."
            )
        elif over_ratio > 0.3:
            verdict = "over_engineered"
            reasoning = (
                f"Router quality {routing_quality:.2f}. "
                f"{over_engineered}/{total_traces_with_outcomes} problems used heavier "
                f"engines than needed. Simplify the express threshold."
            )
        elif under_ratio > 0.3:
            verdict = "under_engineered"
            reasoning = (
                f"Router quality {routing_quality:.2f}. "
                f"{under_engineered}/{total_traces_with_outcomes} problems needed more "
                f"engines than were used. Lower the complexity threshold."
            )
        else:
            verdict = "acceptable"
            reasoning = (
                f"Router quality {routing_quality:.2f}. "
                f"Routing is adequate but could be refined."
            )

        return MetaCalibrationResult(
            total_routed=total_traces_with_outcomes,
            mode_accuracy=mode_accuracy,
            complexity_vs_outcome=overall_accuracy,
            should_have_used_advanced=under_engineered,
            should_have_used_express=over_engineered,
            over_engineered=over_engineered,
            under_engineered=under_engineered,
            routing_quality=routing_quality,
            verdict=verdict,
            reasoning=reasoning,
        )

    @staticmethod
    def to_dict(result: MetaCalibrationResult) -> dict[str, Any]:
        return {
            "total_routed": result.total_routed,
            "mode_accuracy": result.mode_accuracy,
            "complexity_vs_outcome": result.complexity_vs_outcome,
            "should_have_used_advanced": result.should_have_used_advanced,
            "should_have_used_express": result.should_have_used_express,
            "over_engineered": result.over_engineered,
            "under_engineered": result.under_engineered,
            "routing_quality": result.routing_quality,
            "verdict": result.verdict,
            "reasoning": result.reasoning,
        }
