"""
Autonomous agent integrating Gemini deep research into decision analysis models.
Usage: from decision_maker.core.deep_research_decision_agent import DeepResearchDecisionAgent
Does NOT: Execute local shell commands or modify system settings.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

from decision_maker.core.gemini_agent import GeminiDeepResearchAgent as _GeminiAgent
from decision_maker.core.models import DecisionOption, DistributionType, Factor
from decision_maker.core.orchestrator import UnifiedDecisionFramework


@dataclass
class CareerOption:
    """Legacy CareerOption class."""

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


@dataclass
class AnalysisResult:
    """Legacy analysis result with attribute-style access."""

    option_name: str = ""
    overall_score: float = 0.0
    monte_carlo_score: float = 0.0
    topsis_rank: int = 0
    pareto_optimal: bool = False
    regret_analysis: float = 0.0
    risk_score: float = 0.0
    scenario_robustness: float = 0.0
    confidence: float = 0.0
    recommendation: str = ""


class DecisionAnalysisEngine:
    """Legacy DecisionAnalysisEngine — wraps UnifiedDecisionFramework."""

    def __init__(self, debug: bool = False):
        self.framework = UnifiedDecisionFramework()
        self._options: list[CareerOption] = []
        self._cached_results: dict[str, AnalysisResult] = {}

    def add_option(self, option: CareerOption) -> None:
        self._options.append(option)
        do = option.to_decision_option()
        self.framework.add_option(do)

    def add_factor(self, name: str, weight: float, maximize: bool = True) -> None:
        self.framework.add_factor(Factor(name, weight, maximize))

    def _run_full_analysis(self) -> dict[str, AnalysisResult]:
        import asyncio

        result = asyncio.run(self.framework.run_analysis(mode="standard"))
        mc_results = result.get("mc_results", {})
        topsis = result.get("topsis_scores")
        pareto = result.get("pareto", {})
        sensitivity = result.get("sensitivity", {})

        if topsis is not None and hasattr(topsis, "empty") and not topsis.empty:
            topsis_ranks = {name: rank + 1 for rank, name in enumerate(topsis.sort_values(ascending=False).index)}
        else:
            sorted_names = sorted(mc_results.keys(), key=lambda n: mc_results[n].mean_score, reverse=True)
            topsis_ranks = {name: rank + 1 for rank, name in enumerate(sorted_names)}

        efficient = set(pareto.get("efficient_frontier", []))
        robustness = sensitivity.get("robustness_score", 1.0)

        regret_values = {}
        if mc_results:
            max_score = max(s.mean_score for s in mc_results.values())
            regret_values = {n: max_score - s.mean_score for n, s in mc_results.items()}

        results = {}
        for name, stats in mc_results.items():
            results[name] = AnalysisResult(
                option_name=name,
                overall_score=stats.mean_score,
                monte_carlo_score=stats.mean_score,
                topsis_rank=topsis_ranks.get(name, 99),
                pareto_optimal=name in efficient,
                regret_analysis=regret_values.get(name, 0.0),
                risk_score=stats.std_dev,
                scenario_robustness=robustness * (1.0 - stats.std_dev / (abs(stats.mean_score) + 1e-9)),
                confidence=stats.success_rate,
                recommendation="Recommended"
                if name
                == (
                    topsis.index[0]
                    if topsis is not None and hasattr(topsis, "empty") and not topsis.empty
                    else (max(mc_results.items(), key=lambda x: x[1].mean_score)[0] if mc_results else "")
                )
                else "",
            )
        return results

    def analyze_option(self, option: CareerOption, all_options: list[CareerOption]) -> AnalysisResult:
        if not self._cached_results:
            self._cached_results = self._run_full_analysis()
        return self._cached_results.get(option.name, AnalysisResult(option_name=option.name))

    @staticmethod
    def _calculate_overall_score(result: AnalysisResult) -> float:
        """Composite score penalizing risk, used by legacy scripts."""
        return result.monte_carlo_score * (1.0 - result.risk_score)

    @staticmethod
    def topsis_rank(alternatives: list[str], criteria: dict[str, Any]) -> dict[str, float]:
        names = list(criteria.keys())
        weights = [criteria[n]["weight"] for n in names]
        max_bools = [criteria[n].get("maximize", True) for n in names]

        matrix = np.zeros((len(alternatives), len(names)))
        for i, alt in enumerate(alternatives):
            for j, name in enumerate(names):
                matrix[i, j] = criteria[name].get(alt, 0)

        norms = np.sqrt((matrix**2).sum(axis=0))
        norms = np.where(norms == 0, 1, norms)
        normalized = matrix / norms

        weighted = normalized * weights

        ideal = np.where(max_bools, weighted.max(axis=0), weighted.min(axis=0))
        anti_ideal = np.where(max_bools, weighted.min(axis=0), weighted.max(axis=0))

        d_pos = np.sqrt(((weighted - ideal) ** 2).sum(axis=1))
        d_neg = np.sqrt(((weighted - anti_ideal) ** 2).sum(axis=1))

        scores = d_neg / (d_pos + d_neg + 1e-9)
        return dict(zip(alternatives, scores))


class GeminiDeepResearchAgent:
    """Legacy Gemini agent — wraps current API."""

    def __init__(self):
        self._agent = _GeminiAgent()

    async def research(self, topic: str, context: str = "") -> str:
        return await self._agent.research(topic, context)

    @property
    def is_available(self) -> bool:
        return self._agent.is_available
