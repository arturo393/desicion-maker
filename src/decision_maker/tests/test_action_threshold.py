import numpy as np
import pytest

from decision_maker.core.action_threshold import MinimumActionThreshold, ThresholdVerdict
from decision_maker.core.models import DecisionOption, DistributionType, Factor, Statistics


class TestMinimumActionThreshold:
    def _make_stats(self, name: str, mean: float, std: float) -> Statistics:
        return Statistics(
            option_name=name, mean_score=mean, std_dev=std,
            min_score=mean - 2 * std, max_score=mean + 2 * std,
            percentile_5=mean - 1.645 * std, percentile_95=mean + 1.645 * std,
            success_rate=0.7, factor_stats={"F": {"mean": mean, "std": std, "p5": mean - std, "p95": mean + std}},
            var_95=mean - 1.645 * std, cvar_95=mean - 2 * std,
        )

    def test_empty_results(self):
        result = MinimumActionThreshold.evaluate({}, [])
        assert result.should_decide is False
        assert result.verdict == "no_data"

    def test_clear_winner(self):
        mc = {
            "A": self._make_stats("A", 10.0, 0.5),
            "B": self._make_stats("B", 2.0, 0.5),
        }
        result = MinimumActionThreshold.evaluate(mc, [])
        assert result.should_decide is True
        assert result.verdict == "decide"
        assert result.winning_option == "A"
        assert result.signal_to_noise > 5.0

    def test_no_clear_winner(self):
        mc = {
            "A": self._make_stats("A", 5.0, 3.0),
            "B": self._make_stats("B", 4.8, 3.0),
        }
        result = MinimumActionThreshold.evaluate(mc, [])
        assert result.verdict in ("defer", "decide_with_caution")
        assert result.signal_to_noise < 2.0

    def test_single_option(self):
        mc = {"Only": self._make_stats("Only", 5.0, 1.0)}
        result = MinimumActionThreshold.evaluate(mc, [])
        assert result.winning_option == "Only"
        assert result.verdict != "no_data"

    def test_to_dict(self):
        mc = {"A": self._make_stats("A", 10.0, 0.1)}
        result = MinimumActionThreshold.evaluate(mc, [])
        d = MinimumActionThreshold.to_dict(result)
        assert "should_decide" in d
        assert "verdict" in d
        assert "reasoning" in d

    def test_signal_strength_computed(self):
        mc = {
            "A": self._make_stats("A", 10.0, 1.0),
            "B": self._make_stats("B", 5.0, 1.0),
        }
        result = MinimumActionThreshold.evaluate(mc, [])
        assert result.signal_strength == pytest.approx(5.0, abs=0.01)

    def test_noise_level_computed(self):
        mc = {
            "A": self._make_stats("A", 10.0, 2.0),
            "B": self._make_stats("B", 5.0, 2.0),
        }
        result = MinimumActionThreshold.evaluate(mc, [])
        assert result.noise_level == pytest.approx(2.0, abs=0.01)
