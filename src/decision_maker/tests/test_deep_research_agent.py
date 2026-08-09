from __future__ import annotations

import numpy as np
import pytest

from decision_maker.core.deep_research_decision_agent import (
    AnalysisResult,
    CareerOption,
    DecisionAnalysisEngine,
    GeminiDeepResearchAgent,
)


class TestCareerOption:
    def test_to_decision_option_builds_variables(self):
        opt = CareerOption(
            name="Engineer",
            salary_expected=80000,
            probability_success=0.8,
            timeline_months=12,
            tech_growth=8.0,
            description="Senior role",
        )
        do = opt.to_decision_option()
        assert do.name == "Engineer"
        assert do.description == "Senior role"
        assert "salary_expected" in do.variables
        assert "probability_success" in do.variables
        assert "timeline_months" in do.variables
        assert "tech_growth" in do.variables
        assert do.variables["salary_expected"].params == [80000.0]


class TestDecisionAnalysisEngine:
    def _build_engine(self):
        engine = DecisionAnalysisEngine()
        engine.add_factor("Cost", 0.5, maximize=False)
        engine.add_factor("Quality", 0.5, maximize=True)
        engine.add_option(CareerOption("A", salary_expected=100, probability_success=0.9, income_stability=8.0))
        return engine

    def test_analyze_option_returns_analysis_result(self):
        engine = self._build_engine()
        result = engine.analyze_option(CareerOption(name="A"), [])
        assert isinstance(result, AnalysisResult)
        assert result.option_name == "A"
        assert result.overall_score >= 0

    def test_analyze_unknown_option_returns_default(self):
        engine = self._build_engine()
        result = engine.analyze_option(CareerOption(name="Z"), [])
        assert isinstance(result, AnalysisResult)
        assert result.option_name == "Z"

    def test_calculate_overall_score_penalizes_risk(self):
        result = AnalysisResult(monte_carlo_score=1.0, risk_score=0.2)
        score = DecisionAnalysisEngine._calculate_overall_score(result)
        assert np.isclose(score, 0.8)

    def test_topsis_rank_simple(self):
        scores = DecisionAnalysisEngine.topsis_rank(
            ["A", "B"],
            {"X": {"weight": 1.0, "maximize": True, "A": 10, "B": 20}},
        )
        assert scores["B"] > scores["A"]


class TestGeminiDeepResearchAgent:
    def test_wrapper_delegates_and_availability(self):
        agent = GeminiDeepResearchAgent()
        # is_available reflects underlying client presence; research returns gracefully when unavailable
        assert isinstance(agent.is_available, bool)
