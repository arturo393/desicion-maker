import numpy as np
import pytest

from python.core.information_theory import InformationTheoryEngine
from python.core.models import Factor, Statistics


@pytest.fixture
def mock_mc_results():
    n = 1000
    np.random.seed(42)
    raw_cost = np.random.rand(n) * 100
    raw_roi = np.random.normal(1.5, 0.3, n)
    raw_risk = np.random.uniform(1, 10, n)
    # Create a known dependency: score depends on cost (negatively) and roi (positively)
    raw_scores = 0.6 * (1 - raw_cost / 100) + 0.4 * (raw_roi / 3.0) + np.random.normal(0, 0.05, n)
    raw_factor_data = {
        "Cost": raw_cost,
        "ROI": raw_roi,
        "Risk": raw_risk,
    }
    stats = Statistics(
        option_name="TestOption",
        mean_score=0.5,
        std_dev=0.1,
        min_score=0.0,
        max_score=1.0,
        percentile_5=0.3,
        percentile_95=0.7,
        success_rate=0.8,
        factor_stats={},
        var_95=0.3,
        cvar_95=0.2,
        raw_scores=raw_scores,
        raw_factor_data=raw_factor_data,
    )
    return {"TestOption": stats}


@pytest.fixture
def factors():
    return [
        Factor("Cost", 0.3, maximize=False),
        Factor("ROI", 0.4, maximize=True),
        Factor("Risk", 0.3, maximize=False),
    ]


class TestInformationTheoryEngine:
    def test_analyze_returns_dict(self, mock_mc_results, factors):
        engine = InformationTheoryEngine()
        result = engine.analyze(mock_mc_results, factors)
        assert isinstance(result, dict)
        assert "TestOption" in result

    def test_analyze_normalized_scores_sum_to_one(self, mock_mc_results, factors):
        engine = InformationTheoryEngine()
        result = engine.analyze(mock_mc_results, factors)
        mi_values = list(result["TestOption"].values())
        assert abs(sum(mi_values) - 1.0) < 0.01

    def test_analyze_returns_all_factors(self, mock_mc_results, factors):
        engine = InformationTheoryEngine()
        result = engine.analyze(mock_mc_results, factors)
        assert set(result["TestOption"].keys()) == {"Cost", "ROI", "Risk"}

    def test_analyze_empty_results(self, factors):
        engine = InformationTheoryEngine()
        result = engine.analyze({}, factors)
        assert result == {}

    def test_analyze_missing_raw_scores(self, factors):
        stats = Statistics(
            option_name="NoData",
            mean_score=0.5, std_dev=0.1,
            min_score=0.0, max_score=1.0,
            percentile_5=0.3, percentile_95=0.7,
            success_rate=0.8, factor_stats={},
            var_95=0.3, cvar_95=0.2,
            raw_scores=None,
            raw_factor_data=None,
        )
        engine = InformationTheoryEngine()
        result = engine.analyze({"NoData": stats}, factors)
        assert result == {}

    def test_mutual_info_is_non_negative(self, mock_mc_results, factors):
        engine = InformationTheoryEngine()
        result = engine.analyze(mock_mc_results, factors)
        for val in result["TestOption"].values():
            assert val >= 0
