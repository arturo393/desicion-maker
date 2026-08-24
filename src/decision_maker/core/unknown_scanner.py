"""
Unknown unknowns scanner: detect missing factors by comparing predictions vs outcomes.
Usage: from decision_maker.core.unknown_scanner import UnknownUnknownsScanner
Does NOT: Run decision algorithms or compute scores.
"""

from __future__ import annotations

__all__ = ["UnknownUnknownsScanner", "UnknownReport"]

import logging
from collections import Counter
from dataclasses import dataclass
from typing import Any

import numpy as np

from decision_maker.core.outcome_tracker import OutcomeEntry

logger = logging.getLogger(__name__)


@dataclass
class UnknownReport:
    """Report of potential unknown unknowns detected (Parameter Object)."""

    total_decisions_analyzed: int
    wrong_decisions: int
    factors_recurring_in_wrong: list[tuple[str, int]]
    tags_recurring_in_wrong: list[tuple[str, int]]
    missing_info_patterns: list[tuple[str, int]]
    confidence_when_wrong_avg: float
    confidence_when_right_avg: float
    overconfidence_ratio: float
    potential_unknown_factors: list[str]
    verdict: str
    reasoning: str


class UnknownUnknownsScanner:
    """
    Detects what you don't know you don't know.

    When predictions fail, the failure pattern reveals what factors
    were missing from the analysis. This scanner compares the factors
    and tags of correct vs incorrect decisions to find systematic gaps.

    Based on the concept of "unknown unknowns" from decision theory:
    the things that kill your decisions are the ones you never thought to
    include in your model.
    """

    OVERCONFIDENCE_THRESHOLD = 1.3

    @staticmethod
    def scan(entries: list[OutcomeEntry]) -> UnknownReport:
        if not entries:
            return UnknownReport(
                total_decisions_analyzed=0, wrong_decisions=0,
                factors_recurring_in_wrong=[], tags_recurring_in_wrong=[],
                missing_info_patterns=[], confidence_when_wrong_avg=0.0,
                confidence_when_right_avg=0.0, overconfidence_ratio=0.0,
                potential_unknown_factors=[], verdict="no_data",
                reasoning="No outcomes to analyze",
            )

        wrong = [e for e in entries if not e.was_correct]
        right = [e for e in entries if e.was_correct]

        conf_wrong = float(np.mean([e.predicted_confidence for e in wrong])) if wrong else 0.0
        conf_right = float(np.mean([e.predicted_confidence for e in right])) if right else 0.0
        overconfidence = conf_wrong / (conf_right + 1e-9) if conf_right > 0 else 0.0

        factor_counter: Counter[str] = Counter()
        tag_counter: Counter[str] = Counter()
        missing_counter: Counter[str] = Counter()

        for e in wrong:
            for f in e.factors_used:
                factor_counter[f] += 1
            for t in e.tags:
                tag_counter[t] += 1

        wrong_factor_freq = factor_counter.most_common(10)
        wrong_tag_freq = tag_counter.most_common(10)

        potential_factors = UnknownUnknownsScanner._infer_missing_factors(entries)

        total = len(entries)
        wrong_count = len(wrong)
        wrong_ratio = wrong_count / total if total > 0 else 0.0

        if wrong_ratio > 0.5 and overconfidence > UnknownUnknownsScanner.OVERCONFIDENCE_THRESHOLD:
            verdict = "critical"
            reasoning = (
                f"{wrong_count}/{total} wrong ({wrong_ratio:.0%}), "
                f"and you were {overconfidence:.1f}x more confident when wrong. "
                f"Your model is systematically missing something."
            )
        elif wrong_ratio > 0.3:
            verdict = "warning"
            reasoning = (
                f"{wrong_count}/{total} wrong ({wrong_ratio:.0%}). "
                f"Check the recurring factors in failures for blind spots."
            )
        elif overconfidence > UnknownUnknownsScanner.OVERCONFIDENCE_THRESHOLD:
            verdict = "overconfident"
            reasoning = (
                f"You're {overconfidence:.1f}x more confident when wrong than when right. "
                f"Calibrate down."
            )
        else:
            verdict = "healthy"
            reasoning = (
                f"Error rate {wrong_ratio:.0%} is within normal range. "
                f"No systematic blind spots detected."
            )

        return UnknownReport(
            total_decisions_analyzed=total,
            wrong_decisions=wrong_count,
            factors_recurring_in_wrong=wrong_factor_freq,
            tags_recurring_in_wrong=wrong_tag_freq,
            missing_info_patterns=missing_counter.most_common(10),
            confidence_when_wrong_avg=conf_wrong,
            confidence_when_right_avg=conf_right,
            overconfidence_ratio=overconfidence,
            potential_unknown_factors=potential_factors,
            verdict=verdict,
            reasoning=reasoning,
        )

    @staticmethod
    def _infer_missing_factors(entries: list[OutcomeEntry]) -> list[str]:
        if len(entries) < 5:
            return []

        wrong_tags: Counter[str] = Counter()
        right_tags: Counter[str] = Counter()
        for e in entries:
            c = wrong_tags if not e.was_correct else right_tags
            for t in e.tags:
                c[t] += 1

        missing = []
        for tag, count in wrong_tags.most_common(5):
            if tag not in right_tags or wrong_tags[tag] > right_tags.get(tag, 0) * 2:
                missing.append(f"Tag '{tag}' appears disproportionately in failures")

        return missing

    @staticmethod
    def to_dict(report: UnknownReport) -> dict[str, Any]:
        return {
            "total_decisions_analyzed": report.total_decisions_analyzed,
            "wrong_decisions": report.wrong_decisions,
            "error_rate": report.wrong_decisions / max(report.total_decisions_analyzed, 1),
            "factors_recurring_in_wrong": report.factors_recurring_in_wrong,
            "tags_recurring_in_wrong": report.tags_recurring_in_wrong,
            "confidence_when_wrong_avg": report.confidence_when_wrong_avg,
            "confidence_when_right_avg": report.confidence_when_right_avg,
            "overconfidence_ratio": report.overconfidence_ratio,
            "potential_unknown_factors": report.potential_unknown_factors,
            "verdict": report.verdict,
            "reasoning": report.reasoning,
        }
