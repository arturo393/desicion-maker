from __future__ import annotations

import numpy as np
import pytest

from decision_maker.core.models import Factor, Statistics
from decision_maker.core.what_if import WhatIfEngine, _compute_raw_bounds


def _build_mc_results():
    return {
        "A": Statistics(
            option_name="A",
            mean_score=80.0,
            std_dev=10.0,
            min_score=50.0,
            max_score=100.0,
            percentile_5=60.0,
            percentile_95=95.0,
            success_rate=0.9,
            factor_stats={"Cost": {"mean": 10.0, "std": 1.0}, "Quality": {"mean": 8.0, "std": 0.5}},
            var_95=60.0,
            cvar_95=55.0,
            raw_scores=np.array([70.0, 80.0, 90.0]),
            raw_factor_data={"Cost": np.array([10.0, 11.0, 12.0]), "Quality": np.array([7.0, 8.0, 9.0])},
        ),
        "B": Statistics(
            option_name="B",
            mean_score=60.0,
            std_dev=20.0,
            min_score=20.0,
            max_score=95.0,
            percentile_5=30.0,
            percentile_95=90.0,
            success_rate=0.6,
            factor_stats={"Cost": {"mean": 20.0, "std": 2.0}, "Quality": {"mean": 5.0, "std": 1.0}},
            var_95=30.0,
            cvar_95=25.0,
            raw_scores=np.array([40.0, 60.0, 80.0]),
            raw_factor_data={"Cost": np.array([18.0, 20.0, 22.0]), "Quality": np.array([4.0, 5.0, 6.0])},
        ),
    }


def _build_factors():
    return [Factor("Cost", 0.5, maximize=False), Factor("Quality", 0.5, maximize=True)]


class TestWhatIfEngine:
    @pytest.fixture
    def engine(self):
        return WhatIfEngine(_build_mc_results(), _build_factors())

    def test_init_raises_on_empty(self):
        with pytest.raises(ValueError, match="must not be empty"):
            WhatIfEngine({}, [])
        with pytest.raises(ValueError, match="must not be empty"):
            WhatIfEngine(_build_mc_results(), [])

    def test_assign_weight_updates(self, engine):
        assert engine.assign_weight("Cost", 0.8) is True
        assert engine.assign_weight("Unknown", 0.5) is False
        assert engine.current_factors[0].weight == 0.8

    def test_toggle_maximize(self, engine):
        result = engine.toggle_maximize("Cost")
        assert result is True  # was maximize=False -> toggles to True
        assert engine.toggle_maximize("Nope") is None

    def test_assign_all_weights(self, engine):
        missing = engine.assign_all_weights({"Cost": 0.9, "Nope": 0.1})
        assert missing == ["Nope"]

    def test_reset_restores_original(self, engine):
        engine.assign_weight("Cost", 0.99)
        engine.reset()
        assert engine.current_factors[0].weight == 0.5

    def test_recompute_ranking(self, engine):
        ranking = engine.recompute()
        assert len(ranking) == 2
        assert ranking[0][0] == "A"
        assert ranking[0][1] > ranking[1][1]

    def test_recompute_with_weights_restores_state(self, engine):
        before = [f.weight for f in engine.current_factors]
        scores = engine.recompute_with_weights({"Cost": 0.9})
        assert len(scores) == 2
        after = [f.weight for f in engine.current_factors]
        assert before == after

    def test_diff_empty_by_default(self, engine):
        assert engine.diff() == []

    def test_diff_after_weight_change(self, engine):
        engine.assign_weight("Cost", 0.7)
        changes = engine.diff()
        assert any("Cost" in c for c in changes)

    def test_original_ranking(self, engine):
        ranking = engine.original_ranking()
        assert ranking[0][0] == "A"

    def test_summary_table(self, engine):
        table = engine.summary_table(engine.recompute())
        assert "A" in table
        assert "B" in table
        assert WhatIfEngine.summary_table([]) == "No results."

    def test_factor_table(self, engine):
        table = engine.factor_table(engine.current_factors)
        assert "Cost" in table
        assert "Quality" in table

    def test_comparison_table(self, engine):
        table = engine.comparison_table(engine.original_ranking(), engine.recompute())
        assert "Before" in table
        assert "After" in table

    def test_suggest_returns_list(self, engine):
        suggestions = engine._suggest()
        assert isinstance(suggestions, list)
        if suggestions:
            assert all(isinstance(s, str) and s for s in suggestions)

    def test_compute_raw_bounds(self):
        bounds = _compute_raw_bounds(_build_mc_results(), ["Cost", "Quality"])
        assert bounds["Cost"]["min"] == 10.0
        assert bounds["Cost"]["max"] == 22.0
