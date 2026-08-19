import numpy as np
import pytest

from decision_maker.core.models import DecisionOption, DistributionType, Factor, Statistics
from decision_maker.core.ergodicity import ErgodicityAnalyzer


class TestErgodicityAnalyzer:
    def _make_stats(self, name: str, scores: np.ndarray) -> Statistics:
        return Statistics(
            option_name=name,
            mean_score=float(np.mean(scores)),
            std_dev=float(np.std(scores)),
            min_score=float(np.min(scores)),
            max_score=float(np.max(scores)),
            percentile_5=float(np.percentile(scores, 5)),
            percentile_95=float(np.percentile(scores, 95)),
            success_rate=float(np.mean(scores > 0)),
            factor_stats={},
            var_95=float(np.percentile(scores, 5)),
            cvar_95=float(np.mean(scores[scores <= np.percentile(scores, 5)])) if len(scores[scores <= np.percentile(scores, 5)]) > 0 else float(np.percentile(scores, 5)),
            raw_scores=scores,
        )

    def test_empty_results(self):
        result = ErgodicityAnalyzer.analyze({}, [])
        assert result["options"] == {}
        assert result["ranking"] == []

    def test_deterministic_option_is_ergodic(self):
        scores = np.full(1000, 5.0)
        mc = {"OptA": self._make_stats("OptA", scores)}
        result = ErgodicityAnalyzer.analyze(mc, [])
        assert result["options"]["OptA"]["is_ergodic"] is True
        assert result["options"]["OptA"]["verdict"] == "ergodic"
        assert result["options"]["OptA"]["ruin_probability"] == 0.0

    def test_multiplicative_process_non_ergodic(self):
        np.random.seed(42)
        returns = np.random.lognormal(0.0, 0.5, 1000)
        scores = np.cumprod(returns)
        mc = {"Multiplicative": self._make_stats("Multiplicative", scores)}
        result = ErgodicityAnalyzer.analyze(mc, [])
        opt = result["options"]["Multiplicative"]
        assert opt["temporal_log_growth"] != opt["ensemble_mean"]
        assert opt["geometric_mean"] > 0

    def test_high_variance_has_ruin_probability(self):
        np.random.seed(42)
        scores = np.random.normal(0, 10, 1000)
        mc = {"Volatile": self._make_stats("Volatile", scores)}
        result = ErgodicityAnalyzer.analyze(mc, [])
        opt = result["options"]["Volatile"]
        assert opt["ruin_probability"] >= 0.0

    def test_ranking_by_log_growth(self):
        np.random.seed(42)
        scores_a = np.random.lognormal(0.1, 0.1, 1000)
        scores_b = np.random.lognormal(-0.1, 0.1, 1000)
        mc = {
            "A": self._make_stats("A", scores_a),
            "B": self._make_stats("B", scores_b),
        }
        result = ErgodicityAnalyzer.analyze(mc, [])
        assert result["ranking"][0]["option"] == "A"

    def test_custom_time_horizons(self):
        scores = np.full(100, 5.0)
        mc = {"Opt": self._make_stats("Opt", scores)}
        result = ErgodicityAnalyzer.analyze(mc, [], time_horizons=[10, 50])
        assert result["time_horizons_tested"] == [10, 50]

    def test_max_drawdown_range(self):
        np.random.seed(42)
        scores = np.random.lognormal(0, 0.3, 500)
        mc = {"Opt": self._make_stats("Opt", scores)}
        result = ErgodicityAnalyzer.analyze(mc, [])
        opt = result["options"]["Opt"]
        assert 0.0 <= opt["max_drawdown"] <= 1.0

    def test_summary_format(self):
        scores = np.full(100, 5.0)
        mc = {"Opt": self._make_stats("Opt", scores)}
        result = ErgodicityAnalyzer.analyze(mc, [])
        assert "ergodic" in result["summary"].lower()

    def test_no_raw_scores_skipped(self):
        stats = Statistics(
            option_name="NoRaw",
            mean_score=5.0,
            std_dev=1.0,
            min_score=3.0,
            max_score=7.0,
            percentile_5=3.5,
            percentile_95=6.5,
            success_rate=0.9,
            factor_stats={},
            var_95=3.5,
            cvar_95=3.5,
            raw_scores=None,
        )
        mc = {"NoRaw": stats}
        result = ErgodicityAnalyzer.analyze(mc, [])
        assert "NoRaw" not in result["options"]

    def test_ergodic_count(self):
        scores = np.full(100, 5.0)
        mc = {"Opt": self._make_stats("Opt", scores)}
        result = ErgodicityAnalyzer.analyze(mc, [])
        assert result["ergodic_count"] >= 0
        assert result["non_ergodic_count"] >= 0
        assert result["ergodic_count"] + result["non_ergodic_count"] == len(result["options"])
