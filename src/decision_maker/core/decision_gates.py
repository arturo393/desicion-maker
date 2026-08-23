"""
Decision gates: kill-switches that automatically reject options or halt the pipeline.
Usage: from decision_maker.core.decision_gates import DecisionGate
Does NOT: Produce scores or rankings (rejects or approves).
"""

from __future__ import annotations

__all__ = ["DecisionGate", "GateResult"]

import logging
from dataclasses import dataclass, field
from typing import Any

import numpy as np

from decision_maker.core.models import Factor, Statistics
from decision_maker.core.utils import EPSILON

logger = logging.getLogger(__name__)


@dataclass
class GateVerdict:
    """Result of a single gate check on a single option (Parameter Object)."""

    gate_name: str
    option_name: str
    passed: bool
    value: float
    threshold: float
    reasoning: str


@dataclass
class GateResult:
    """Aggregated result of all gates on all options (Parameter Object)."""

    options_approved: list[str] = field(default_factory=list)
    options_vetoed: list[str] = field(default_factory=list)
    pipeline_halted: bool = False
    halt_reason: str = ""
    gate_verdicts: list[GateVerdict] = field(default_factory=list)
    veto_count: int = 0
    total_options: int = 0

    def summary(self) -> str:
        if self.pipeline_halted:
            return f"PIPELINE HALTED: {self.halt_reason}"
        if self.options_vetoed:
            return (
                f"{len(self.options_vetoed)}/{self.total_options} options vetoed. "
                f"Approved: {', '.join(self.options_approved)}"
            )
        return f"All {self.total_options} options approved"


class DecisionGate:
    """
    Kill-switches that make the framework say NO with authority.

    Three gates, applied in order:
    1. ERGODICITY: If the option is non-ergodic, it's a Russian roulette bet.
       No amount of positive expected value justifies a non-ergodic bet.
       (Peters: temporal growth rate < 0 → reject)

    2. RUIN: If the ruin probability exceeds the threshold, the option
       has an absorbing barrier. No recovery is possible.
       (Taleb: survival > profit)

    3. ACTION THRESHOLD: If signal-to-noise is too low, the options are
       indistinguishable from noise. Deciding is guessing.
       (Jaynes: if you can't distinguish, don't pretend you can)

    If ANY gate vetoes an option, that option is eliminated from the pipeline.
    If the action threshold halts the pipeline, NO options are recommended.
    """

    RUIN_PROBABILITY_THRESHOLD = 0.10
    ERGODICITY_LOG_GROWTH_MIN = -0.01
    SIGNAL_TO_NOISE_MIN = 1.5

    @staticmethod
    def apply(
        mc_results: dict[str, Statistics],
        factors: list[Factor],
        ergodicity_data: dict[str, Any] | None = None,
        ruin_probabilities: dict[str, float] | None = None,
        signal_to_noise: float | None = None,
    ) -> GateResult:
        result = GateResult(total_options=len(mc_results))

        for name, stats in mc_results.items():
            option_approved = True

            if ergodicity_data and name in ergodicity_data.get("options", {}):
                opt_data = ergodicity_data["options"][name]
                log_growth = opt_data.get("temporal_log_growth", 0.0)
                has_variance = stats.std_dev > EPSILON
                ensemble_mean = float(np.mean(stats.raw_scores)) if stats.raw_scores is not None else stats.mean_score
                if not has_variance:
                    result.gate_verdicts.append(GateVerdict(
                        gate_name="ergodicity",
                        option_name=name,
                        passed=True,
                        value=log_growth,
                        threshold=DecisionGate.ERGODICITY_LOG_GROWTH_MIN,
                        reasoning=f"Deterministic option (std=0), ergodicity gate skipped",
                    ))
                elif ensemble_mean <= 0:
                    result.gate_verdicts.append(GateVerdict(
                        gate_name="ergodicity",
                        option_name=name,
                        passed=True,
                        value=log_growth,
                        threshold=DecisionGate.ERGODICITY_LOG_GROWTH_MIN,
                        reasoning=f"Negative mean score ({ensemble_mean:.2f}) dominates log-growth; gate skipped (scale artifact)",
                    ))
                elif log_growth < DecisionGate.ERGODICITY_LOG_GROWTH_MIN:
                    result.gate_verdicts.append(GateVerdict(
                        gate_name="ergodicity",
                        option_name=name,
                        passed=False,
                        value=log_growth,
                        threshold=DecisionGate.ERGODICITY_LOG_GROWTH_MIN,
                        reasoning=(
                            f"Non-ergodic: temporal log-growth={log_growth:.4f} < 0. "
                            f"This option destroys wealth over time."
                        ),
                    ))
                    option_approved = False
                else:
                    result.gate_verdicts.append(GateVerdict(
                        gate_name="ergodicity",
                        option_name=name,
                        passed=True,
                        value=log_growth,
                        threshold=DecisionGate.ERGODICITY_LOG_GROWTH_MIN,
                        reasoning=f"Ergodic: log-growth={log_growth:.4f} ≥ 0",
                    ))

            if ruin_probabilities and name in ruin_probabilities:
                ruin_p = ruin_probabilities[name]
                if ruin_p > DecisionGate.RUIN_PROBABILITY_THRESHOLD:
                    result.gate_verdicts.append(GateVerdict(
                        gate_name="ruin",
                        option_name=name,
                        passed=False,
                        value=ruin_p,
                        threshold=DecisionGate.RUIN_PROBABILITY_THRESHOLD,
                        reasoning=(
                            f"Ruin probability={ruin_p:.1%} > {DecisionGate.RUIN_PROBABILITY_THRESHOLD:.0%}. "
                            f"Absorbing barrier detected."
                        ),
                    ))
                    option_approved = False
                else:
                    result.gate_verdicts.append(GateVerdict(
                        gate_name="ruin",
                        option_name=name,
                        passed=True,
                        value=ruin_p,
                        threshold=DecisionGate.RUIN_PROBABILITY_THRESHOLD,
                        reasoning=f"Ruin probability={ruin_p:.1%} within tolerance",
                    ))

            if option_approved:
                result.options_approved.append(name)
            else:
                result.options_vetoed.append(name)
                result.veto_count += 1

        if signal_to_noise is not None and signal_to_noise < DecisionGate.SIGNAL_TO_NOISE_MIN and len(mc_results) > 1:
            result.pipeline_halted = True
            result.halt_reason = (
                f"Signal-to-noise={signal_to_noise:.2f} < {DecisionGate.SIGNAL_TO_NOISE_MIN}. "
                f"Options are indistinguishable from noise. No recommendation possible."
            )
            logger.warning(f"PIPELINE HALTED: {result.halt_reason}")

        if not result.options_approved and not result.pipeline_halted:
            result.pipeline_halted = True
            result.halt_reason = (
                f"All {result.total_options} options vetoed by gates. "
                f"No safe options remain."
            )
            logger.warning(f"PIPELINE HALTED: {result.halt_reason}")

        return result

    @staticmethod
    def to_dict(result: GateResult) -> dict[str, Any]:
        return {
            "options_approved": result.options_approved,
            "options_vetoed": result.options_vetoed,
            "pipeline_halted": result.pipeline_halted,
            "halt_reason": result.halt_reason,
            "veto_count": result.veto_count,
            "total_options": result.total_options,
            "gate_verdicts": [
                {
                    "gate": v.gate_name,
                    "option": v.option_name,
                    "passed": v.passed,
                    "value": v.value,
                    "threshold": v.threshold,
                    "reasoning": v.reasoning,
                }
                for v in result.gate_verdicts
            ],
            "summary": result.summary(),
        }
