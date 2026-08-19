import numpy as np
import pytest

from decision_maker.core.models import DecisionOption, DistributionType, Factor, Statistics
from decision_maker.core.kelly import KellyCriterionEngine


class TestKellyCriterionEngine:
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
        result = KellyCriterionEngine.analyze({}, [])
        assert result["options"] == {}
        assert result["ranking"] == []

    def test_all_wins_positive_kelly(self):
        scores = np.random.default_rng(42).uniform(1, 10, 1000)
        mc = {"Winner": self._make_stats("Winner", scores)}
        result = KellyCriterionEngine.analyze(mc, [])
        opt = result["options"]["Winner"]
        assert opt["kelly_fraction"] > 0.0
        assert opt["win_probability"] == 1.0
        assert opt["verdict"] in ("moderate_edge", "strong_edge")

    def test_all_losses_zero_kelly(self):
        scores = np.array([-5.0] * 1000)
        mc = {"Loser": self._make_stats("Loser", scores)}
        result = KellyCriterionEngine.analyze(mc, [])
        opt = result["options"]["Loser"]
        assert opt["kelly_fraction"] == 0.0
        assert opt["verdict"] == "do_not_bet"

    def test_mixed_outcomes(self):
        np.random.seed(42)
        wins = np.random.uniform(1, 5, 600)
        losses = np.random.uniform(-3, -0.5, 400)
        scores = np.concatenate([wins, losses])
        mc = {"Mixed": self._make_stats("Mixed", scores)}
        result = KellyCriterionEngine.analyze(mc, [])
        opt = result["options"]["Mixed"]
        assert 0.0 < opt["kelly_fraction"] <= 1.0
        assert opt["win_probability"] == pytest.approx(0.6, abs=0.05)

    def test_fractional_kelly_is_half(self):
        np.random.seed(42)
        wins = np.random.uniform(2, 8, 700)
        losses = np.random.uniform(-2, -0.5, 300)
        scores = np.concatenate([wins, losses])
        mc = {"Opt": self._make_stats("Opt", scores)}
        result = KellyCriterionEngine.analyze(mc, [])
        opt = result["options"]["Opt"]
        assert opt["fractional_kelly_half"] == pytest.approx(opt["kelly_fraction"] * 0.5, abs=1e-10)
        assert opt["fractional_kelly_quarter"] == pytest.approx(opt["kelly_fraction"] * 0.25, abs=1e-10)

    def test_ranking_by_kelly(self):
        np.random.seed(42)
        scores_a = np.random.uniform(1, 10, 1000)
        scores_b = np.concatenate([np.random.uniform(1, 3, 900), np.random.uniform(-5, -1, 100)])
        mc = {
            "A": self._make_stats("A", scores_a),
            "B": self._make_stats("B", scores_b),
        }
        result = KellyCriterionEngine.analyze(mc, [])
        assert result["ranking"][0]["option"] == "A"

    def test_summary_format(self):
        scores = np.random.default_rng(42).uniform(1, 10, 1000)
        mc = {"Opt": self._make_stats("Opt", scores)}
        result = KellyCriterionEngine.analyze(mc, [])
        assert "edge" in result["summary"].lower()

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
        result = KellyCriterionEngine.analyze(mc, [])
        assert "NoRaw" not in result["options"]

    def test_edge_calculation(self):
        np.random.seed(42)
        wins = np.random.uniform(2, 4, 800)
        losses = np.random.uniform(-1, -0.5, 200)
        scores = np.concatenate([wins, losses])
        mc = {"Opt": self._make_stats("Opt", scores)}
        result = KellyCriterionEngine.analyze(mc, [])
        opt = result["options"]["Opt"]
        assert opt["edge"] > 0.0
        assert opt["odds"] > 1.0
        assert opt["win_probability"] == pytest.approx(0.8, abs=0.05)

    def test_max_loss_fraction_range(self):
        np.random.seed(42)
        scores = np.concatenate([np.random.uniform(1, 5, 900), np.random.uniform(-3, -0.5, 100)])
        mc = {"Opt": self._make_stats("Opt", scores)}
        result = KellyCriterionEngine.analyze(mc, [])
        opt = result["options"]["Opt"]
        assert opt["max_loss_fraction"] >= 0.0
        assert opt["max_loss_fraction"] < 10.0
