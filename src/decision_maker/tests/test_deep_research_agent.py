from __future__ import annotations

import numpy as np
import pytest

from decision_maker.core.deep_research_decision_agent import (
    CAREER_FACTORS,
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
        # +/-15 % salary range, as in the original engine's Monte Carlo
        assert do.variables["salary_expected"].params == pytest.approx([68000.0, 80000.0, 92000.0])


class TestDecisionAnalysisEngine:
    """The original contract: analyze_option(option, all_options) with no setup scores on CAREER_FACTORS.

    Until 2026-10-01 the shim registered no option and no factor, so every option scored 0.0 — and the
    previous tests here asserted `overall_score >= 0`, which held precisely because of that.
    """

    GOOD = CareerOption("Good", salary_expected=5_000_000, tech_growth=9, income_stability=9,
                        work_life_balance=8, prestige=8, learning_opportunity=9, burnout_risk=0.1)
    BAD = CareerOption("Bad", salary_expected=1_000_000, tech_growth=2, income_stability=3,
                       work_life_balance=3, prestige=2, learning_opportunity=2, burnout_risk=0.8)

    def test_scores_differ_and_order_follows_the_attributes(self):
        engine = DecisionAnalysisEngine()
        opts = [self.GOOD, self.BAD]
        good, bad = (engine.analyze_option(o, opts) for o in opts)
        assert good.overall_score > bad.overall_score
        assert 0.0 < good.overall_score <= 10.0
        assert good.recommendation == "Recommended"

    def test_unknown_option_raises(self):
        engine = DecisionAnalysisEngine()
        engine.analyze_option(self.GOOD, [self.GOOD, self.BAD])
        with pytest.raises(KeyError, match="Z"):
            engine.analyze_option(CareerOption(name="Z"), [])

    def test_custom_factors_replace_the_defaults(self):
        engine = DecisionAnalysisEngine()
        engine.add_factor("burnout_risk", 1.0, maximize=True)  # perverse on purpose
        opts = [self.GOOD, self.BAD]
        good, bad = (engine.analyze_option(o, opts) for o in opts)
        assert bad.overall_score > good.overall_score

    def test_career_factor_weights_sum_to_one(self):
        assert sum(w for _, w, _ in CAREER_FACTORS) == pytest.approx(1.0)

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

    def test_scenario_robustness_clamped_and_recommendation_matches_mc(self, monkeypatch):
        """Scenario robustness must be in [0, 1] and recommendation must follow overall_score (MC), not TOPSIS."""
        import pandas as pd

        from decision_maker.core.models import Statistics

        engine = DecisionAnalysisEngine()
        mock_result = {
            "mc_results": {
                "A": Statistics("A", 0.9, 0.05, 0.8, 1.0, 0.85, 0.95, 0.95, {}, 0.85, 0.8),
                "B": Statistics("B", 0.1, 2.0, -1.0, 1.0, 0.0, 0.5, 0.5, {}, 0.0, -0.5),
            },
            "topsis_scores": pd.Series({"B": 0.99, "A": 0.01}),
            "pareto": {},
            "sensitivity": {"robustness_score": 1.0},
        }

        async def mock_run_analysis(**kwargs):
            return mock_result

        monkeypatch.setattr(engine.framework, "run_analysis", mock_run_analysis)
        results = engine._run_full_analysis()

        # Check clamping to [0, 1]
        assert 0.0 <= results["B"].scenario_robustness <= 1.0
        # Check recommendation matches overall_score (A) rather than TOPSIS (B)
        assert results["A"].recommendation == "Recommended"
        assert results["B"].recommendation == ""


class TestGeminiDeepResearchAgent:
    def test_wrapper_delegates_and_availability(self):
        agent = GeminiDeepResearchAgent()
        # is_available reflects underlying client presence; research returns gracefully when unavailable
        assert isinstance(agent.is_available, bool)
