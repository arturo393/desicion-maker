
from decision_maker.core.decision_gates import DecisionGate
from decision_maker.core.models import Statistics


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
        # Exactly once: the ruin branch and the final bookkeeping both appended it (2026-10-02 review).
        assert result.options_vetoed == ["B"]
        assert result.veto_count == 1

    def test_summary(self):
        mc = {"A": self._make_stats("A", 10.0, 1.0)}
        result = DecisionGate.apply(mc, [], signal_to_noise=5.0)
        assert "approved" in result.summary().lower()

    def test_ruin_gate_not_applicable_on_normalized_scores(self):
        """When scores are normalized in [0, 1], ruin gate must report 'not applicable', not a measured 0."""
        mc = {
            "A": self._make_stats("A", 0.8, 0.05),
            "B": self._make_stats("B", 0.5, 0.05),
        }
        ruin = {"A": 0.0, "B": 0.0}
        result = DecisionGate.apply(mc, [], ruin_probabilities=ruin, signal_to_noise=5.0)
        ruin_verdicts = [v for v in result.gate_verdicts if v.gate_name == "ruin"]
        assert len(ruin_verdicts) == 2
        for v in ruin_verdicts:
            assert v.passed is True
            assert v.value is None
            assert "not applicable" in v.reasoning.lower()

    def test_ruin_gate_vetoes_unnormalized_negative_option(self):
        """With normalize=False and an option with majority negative scores, ruin gate vetoes."""
        import numpy as np
        opt_b_stats = Statistics(
            option_name="B", mean_score=-5.0, std_dev=2.0,
            min_score=-10.0, max_score=-1.0,
            percentile_5=-8.5, percentile_95=-1.5,
            success_rate=0.1, factor_stats={}, var_95=-8.5, cvar_95=-9.0,
            raw_scores=np.array([-5.0, -6.0, -4.0, -7.0, -1.0]),
        )
        mc = {
            "A": self._make_stats("A", 10.0, 1.0),
            "B": opt_b_stats,
        }
        ruin = {"A": 0.0, "B": 0.8}
        result = DecisionGate.apply(
            mc, [],
            ruin_probabilities=ruin,
            signal_to_noise=5.0,
        )
        assert "A" in result.options_approved
        # Exactly once: the ruin branch and the final bookkeeping both appended it (2026-10-02 review).
        assert result.options_vetoed == ["B"]
        assert result.veto_count == 1
