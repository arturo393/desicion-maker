import pytest

from decision_maker.core.decision_gates import DecisionGate, GateResult, GateVerdict
from decision_maker.core.models import DecisionOption, DistributionType, Factor, Statistics


class TestDecisionGate:
    def _make_stats(self, name: str, mean: float, std: float) -> Statistics:
        return Statistics(
            option_name=name, mean_score=mean, std_dev=std,
            min_score=mean - 2 * std, max_score=mean + 2 * std,
            percentile_5=mean - 1.645 * std, percentile_95=mean + 1.645 * std,
            success_rate=0.7, factor_stats={}, var_95=mean - 1.645 * std, cvar_95=mean - 2 * std,
        )

    def test_all_pass(self):
        mc = {"A": self._make_stats("A", 10.0, 1.0), "B": self._make_stats("B", 5.0, 1.0)}
        result = DecisionGate.apply(mc, [], signal_to_noise=5.0)
        assert result.pipeline_halted is False
        assert len(result.options_approved) == 2
        assert result.veto_count == 0

    def test_ergodicity_is_informational_not_veto(self):
        # Ergodicity on additive normalized MC scores is a scale artifact,
        # not evidence of wealth destruction — it must NOT reject options.
        mc = {"A": self._make_stats("A", 10.0, 1.0)}
        ergodicity = {"options": {"A": {"temporal_log_growth": -0.05}}}
        result = DecisionGate.apply(mc, [], ergodicity_data=ergodicity, signal_to_noise=5.0)
        assert "A" in result.options_approved
        assert result.pipeline_halted is False

    def test_low_snh_halts(self):
        mc = {"A": self._make_stats("A", 5.0, 3.0), "B": self._make_stats("B", 4.8, 3.0)}
        result = DecisionGate.apply(mc, [], signal_to_noise=0.5)
        assert result.pipeline_halted is True
        assert "noise" in result.halt_reason.lower()

    def test_to_dict(self):
        mc = {"A": self._make_stats("A", 10.0, 1.0)}
        result = DecisionGate.apply(mc, [], signal_to_noise=5.0)
        d = DecisionGate.to_dict(result)
        assert "options_approved" in d
        assert "gate_verdicts" in d

    def test_empty_mc(self):
        result = DecisionGate.apply({}, [], signal_to_noise=5.0)
        assert result.pipeline_halted is True
        assert "0 options" in result.halt_reason.lower() or "all" in result.halt_reason.lower()

    def test_partial_veto_by_other_gates(self):
        mc = {
            "A": self._make_stats("A", 10.0, 1.0),
            "B": self._make_stats("B", 5.0, 1.0),
        }
        # Ruin probability is a valid veto gate; ergodicity is informational.
        ergodicity = {"options": {"A": {"temporal_log_growth": 0.05}, "B": {"temporal_log_growth": -0.1}}}
        ruin = {"B": 0.5}
        result = DecisionGate.apply(mc, [], ergodicity_data=ergodicity, ruin_probabilities=ruin, signal_to_noise=5.0)
        assert "A" in result.options_approved
        assert "B" in result.options_vetoed

    def test_summary(self):
        mc = {"A": self._make_stats("A", 10.0, 1.0)}
        result = DecisionGate.apply(mc, [], signal_to_noise=5.0)
        assert "approved" in result.summary().lower()
