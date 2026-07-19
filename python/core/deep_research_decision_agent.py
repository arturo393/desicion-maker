"""Backward-compatible shim for legacy analysis scripts.

Provides CareerOption, DecisionAnalysisEngine, and AnalysisResult
wrapping the current UnifiedDecisionFramework API.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import numpy as np

from python.core.models import DecisionOption, DistributionType, Factor
from python.core.orchestrator import UnifiedDecisionFramework
from python.core.topsis import TOPSISEngine


@dataclass
class CareerOption:
    """Legacy CareerOption class — wraps DecisionOption."""
    name: str
    salary_expected: float = 0.0
    probability_success: float = 0.5
    timeline_months: int = 1
    tech_growth: float = 5.0
    income_stability: float = 5.0
    work_life_balance: float = 5.0
    prestige: float = 5.0
    remote_flexibility: float = 5.0
    learning_opportunity: float = 5.0
    career_ceiling: float = 5.0
    description: str = ""

    def to_decision_option(self) -> DecisionOption:
        opt = DecisionOption(self.name, self.description)
        opt.add_variable("salary_expected", DistributionType.DETERMINISTIC, self.salary_expected)
        opt.add_variable("probability_success", DistributionType.DETERMINISTIC, self.probability_success)
        opt.add_variable("timeline_months", DistributionType.DETERMINISTIC, float(self.timeline_months))
        opt.add_variable("tech_growth", DistributionType.DETERMINISTIC, self.tech_growth)
        opt.add_variable("income_stability", DistributionType.DETERMINISTIC, self.income_stability)
        opt.add_variable("work_life_balance", DistributionType.DETERMINISTIC, self.work_life_balance)
        opt.add_variable("prestige", DistributionType.DETERMINISTIC, self.prestige)
        opt.add_variable("remote_flexibility", DistributionType.DETERMINISTIC, self.remote_flexibility)
        opt.add_variable("learning_opportunity", DistributionType.DETERMINISTIC, self.learning_opportunity)
        opt.add_variable("career_ceiling", DistributionType.DETERMINISTIC, self.career_ceiling)
        return opt


AnalysisResult = Dict[str, Any]


class DecisionAnalysisEngine:
    """Legacy DecisionAnalysisEngine — wraps UnifiedDecisionFramework."""

    def __init__(self):
        self.framework = UnifiedDecisionFramework()
        self._options: List[CareerOption] = []

    def add_option(self, option: CareerOption) -> None:
        self._options.append(option)
        do = option.to_decision_option()
        self.framework.add_option(do)

    def add_factor(self, name: str, weight: float, maximize: bool = True) -> None:
        self.framework.add_factor(Factor(name, weight, maximize))

    def run(self) -> AnalysisResult:
        import asyncio
        result = asyncio.run(self.framework.run_analysis(mode="standard"))
        return result

    @staticmethod
    def topsis_rank(alternatives: List[str], criteria: Dict[str, Any]) -> Dict[str, float]:
        """Simple TOPSIS ranking for legacy scripts."""
        names = list(criteria.keys())
        weights = [criteria[n]["weight"] for n in names]
        max_bools = [criteria[n].get("maximize", True) for n in names]

        matrix = np.zeros((len(alternatives), len(names)))
        for i, alt in enumerate(alternatives):
            for j, name in enumerate(names):
                matrix[i, j] = criteria[name].get(alt, 0)

        # Normalize
        norms = np.sqrt((matrix ** 2).sum(axis=0))
        norms = np.where(norms == 0, 1, norms)
        normalized = matrix / norms

        # Weighted
        weighted = normalized * weights

        # Ideal / anti-ideal
        ideal = np.where(max_bools, weighted.max(axis=0), weighted.min(axis=0))
        anti_ideal = np.where(max_bools, weighted.min(axis=0), weighted.max(axis=0))

        # Distances
        d_pos = np.sqrt(((weighted - ideal) ** 2).sum(axis=1))
        d_neg = np.sqrt(((weighted - anti_ideal) ** 2).sum(axis=1))

        scores = d_neg / (d_pos + d_neg + 1e-9)
        return dict(zip(alternatives, scores))


class GeminiDeepResearchAgent:
    """Legacy Gemini agent — wraps current API."""
    from python.core.gemini_agent import GeminiDeepResearchAgent as _GeminiAgent

    def __init__(self):
        self._agent = self._GeminiAgent()

    async def research(self, topic: str, context: str = "") -> str:
        return await self._agent.research(topic, context)

    @property
    def is_available(self) -> bool:
        return self._agent.is_available
