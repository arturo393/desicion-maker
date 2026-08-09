import numpy as np
import pandas as pd
import pytest

from decision_maker.core.explainability import ExplainabilityEngine, NarrativeContext
from decision_maker.core.models import Factor, Statistics


@pytest.fixture
def mc_results():
    n = 100
    # factor_stats means: Cost: [100, 150], ROI: [1.5, 2.0], Risk: [3, 7]
    # Waterfall computation:
    #   OptionA: Cost=(1-0)*0.4=0.4, ROI=0*0.4=0, Risk=(1-0)*0.2=0.2 → total=0.6
    #   OptionB: Cost=(1-1)*0.4=0, ROI=1*0.4=0.4, Risk=(1-1)*0.2=0 → total=0.4
    return {
        "OptionA": Statistics(
            option_name="OptionA",
            mean_score=0.6,
            std_dev=0.1,
            min_score=0.5,
            max_score=0.95,
            percentile_5=0.6,
            percentile_95=0.9,
            success_rate=0.9,
            factor_stats={
                "Cost": {"mean": 100, "std": 10, "p5": 85, "p95": 115},
                "ROI": {"mean": 1.5, "std": 0.2, "p5": 1.2, "p95": 1.8},
                "Risk": {"mean": 3, "std": 0.5, "p5": 2, "p95": 4},
            },
            var_95=0.6,
            cvar_95=0.55,
            raw_scores=np.random.rand(n) * 0.3 + 0.6,
            raw_factor_data={
                "Cost": np.random.rand(n) * 50 + 75,
                "ROI": np.random.rand(n) * 0.5 + 1.2,
                "Risk": np.random.rand(n) * 2 + 2,
            },
        ),
        "OptionB": Statistics(
            option_name="OptionB",
            mean_score=0.4,
            std_dev=0.15,
            min_score=0.3,
            max_score=0.85,
            percentile_5=0.4,
            percentile_95=0.8,
            success_rate=0.7,
            factor_stats={
                "Cost": {"mean": 150, "std": 15, "p5": 125, "p95": 175},
                "ROI": {"mean": 2.0, "std": 0.3, "p5": 1.5, "p95": 2.5},
                "Risk": {"mean": 7, "std": 1, "p5": 5, "p95": 9},
            },
            var_95=0.4,
            cvar_95=0.35,
            raw_scores=np.random.rand(n) * 0.3 + 0.4,
            raw_factor_data={
                "Cost": np.random.rand(n) * 50 + 125,
                "ROI": np.random.rand(n) * 0.5 + 1.7,
                "Risk": np.random.rand(n) * 3 + 5,
            },
        ),
    }


@pytest.fixture
def factors():
    return [
        Factor("Cost", 0.4, maximize=False),
        Factor("ROI", 0.4, maximize=True),
        Factor("Risk", 0.2, maximize=False),
    ]


@pytest.fixture
def topsis_scores():
    return pd.Series({"OptionA": 0.75, "OptionB": 0.55}, name="TOPSIS")


class TestExplainabilityEngine:
    def setup_method(self):
        self.engine = ExplainabilityEngine()

    def test_factor_waterfall_returns_all_options(self, mc_results, factors):
        result = self.engine.factor_waterfall(mc_results, factors)
        assert "options" in result
        assert "OptionA" in result["options"]
        assert "OptionB" in result["options"]

    def test_factor_waterfall_factor_count(self, mc_results, factors):
        result = self.engine.factor_waterfall(mc_results, factors)
        for opt_name in mc_results:
            assert len(result["options"][opt_name]["factors"]) == len(factors)

    def test_factor_waterfall_contributions_sum(self, mc_results, factors):
        result = self.engine.factor_waterfall(mc_results, factors)
        for opt_name, stats in mc_results.items():
            total = sum(f["contribution"] for f in result["options"][opt_name]["factors"])
            assert abs(total - stats.mean_score) < 0.01

    def test_factor_waterfall_empty(self, factors):
        result = self.engine.factor_waterfall({}, factors)
        assert result["options"] == {}

    def test_factor_waterfall_no_factors(self, mc_results):
        result = self.engine.factor_waterfall(mc_results, [])
        assert result["options"] == {}

    def test_counterfactual_identifies_winner(self, mc_results, factors):
        result = self.engine.counterfactual(mc_results, factors)
        assert result["winner"] == "OptionA"
        assert result["runner_up"] == "OptionB"

    def test_counterfactual_has_flip_scenarios(self, mc_results, factors):
        result = self.engine.counterfactual(mc_results, factors)
        assert "OptionB" in result["flip_scenarios"]
        assert len(result["flip_scenarios"]["OptionB"]) > 0

    def test_counterfactual_gap_is_positive(self, mc_results, factors):
        result = self.engine.counterfactual(mc_results, factors)
        assert result["gap"] >= 0

    def test_counterfactual_single_option(self, factors):
        results = {
            "Only": Statistics(
                "Only",
                10,
                0,
                10,
                10,
                10,
                10,
                1.0,
                {"X": {"mean": 10}},
                10,
                10,
            ),
        }
        result = self.engine.counterfactual(results, [Factor("X", 1.0, maximize=True)])
        assert result["winner"] is None

    def test_counterfactual_empty(self, factors):
        result = self.engine.counterfactual({}, factors)
        assert result["winner"] is None

    def test_counterfactual_empty_factors(self, mc_results):
        result = self.engine.counterfactual(mc_results, [])
        assert result["winner"] is None

    def test_narrative_includes_winner(self, mc_results, factors, topsis_scores):
        waterfall = self.engine.factor_waterfall(mc_results, factors)
        counterfactual = self.engine.counterfactual(mc_results, factors)
        text = self.engine.narrative(
            NarrativeContext(mc_results, factors, waterfall, counterfactual, topsis_scores)
        )
        assert "OptionA" in text
        assert "recommended" in text.lower()

    def test_narrative_includes_key_drivers(self, mc_results, factors, topsis_scores):
        waterfall = self.engine.factor_waterfall(mc_results, factors)
        counterfactual = self.engine.counterfactual(mc_results, factors)
        text = self.engine.narrative(
            NarrativeContext(mc_results, factors, waterfall, counterfactual, topsis_scores)
        )
        assert "key drivers" in text.lower() or "contributed" in text.lower()

    def test_narrative_empty(self, factors, topsis_scores):
        text = self.engine.narrative(
            NarrativeContext({}, factors, {"options": {}, "max_possible": 0}, {}, topsis_scores)
        )
        assert "No data" in text
