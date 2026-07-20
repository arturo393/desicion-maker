from __future__ import annotations

import numpy as np
import pytest

from python.core.models import Factor, Statistics
from python.core.what_if import WhatIfEngine


@pytest.fixture
def factors():
    return [
        Factor("Cost", 0.3, maximize=False),
        Factor("Quality", 0.5, maximize=True),
        Factor("Speed", 0.2, maximize=True),
    ]


@pytest.fixture
def mc_results():
    np.random.seed(42)
    n_sims = 1000

    opt_a_raw = {
        "Cost": np.random.normal(200, 30, n_sims),
        "Quality": np.random.normal(8, 1, n_sims),
        "Speed": np.random.normal(5, 1, n_sims),
    }
    opt_b_raw = {
        "Cost": np.random.normal(300, 40, n_sims),
        "Quality": np.random.normal(6, 1.5, n_sims),
        "Speed": np.random.normal(7, 2, n_sims),
    }
    opt_c_raw = {
        "Cost": np.random.normal(250, 35, n_sims),
        "Quality": np.random.normal(9, 0.8, n_sims),
        "Speed": np.random.normal(4, 1.2, n_sims),
    }

    all_raw_data = {"OptA": opt_a_raw, "OptB": opt_b_raw, "OptC": opt_c_raw}

    # Compute global bounds across all options (matching WhatIfEngine._compute_global_bounds)
    global_bounds = {}
    for raw_data in all_raw_data.values():
        for fn, data in raw_data.items():
            if fn not in global_bounds:
                global_bounds[fn] = {"min": float("inf"), "max": float("-inf")}
            global_bounds[fn]["min"] = min(global_bounds[fn]["min"], float(np.min(data)))
            global_bounds[fn]["max"] = max(global_bounds[fn]["max"], float(np.max(data)))

    factors = [
        Factor("Cost", 0.3, maximize=False),
        Factor("Quality", 0.5, maximize=True),
        Factor("Speed", 0.2, maximize=True),
    ]

    def _compute_mean_score(raw_data):
        total = np.zeros(n_sims)
        for f in factors:
            vals = raw_data[f.name]
            b = global_bounds[f.name]
            if b["max"] > b["min"]:
                norm = (vals - b["min"]) / (b["max"] - b["min"])
            else:
                norm = np.ones_like(vals)
            if f.maximize:
                total += norm * f.weight
            else:
                total += (1.0 - norm) * f.weight
        return float(np.mean(total))

    def _make_stats(name, raw_data):
        return Statistics(
            option_name=name,
            mean_score=_compute_mean_score(raw_data),
            std_dev=0.0,
            min_score=0.0,
            max_score=0.0,
            percentile_5=0.0,
            percentile_95=0.0,
            success_rate=0.0,
            factor_stats={
                fn: {
                    "mean": float(np.mean(vals)),
                    "std": float(np.std(vals)),
                    "p5": float(np.percentile(vals, 5)),
                    "p95": float(np.percentile(vals, 95)),
                }
                for fn, vals in raw_data.items()
            },
            var_95=0.0,
            cvar_95=0.0,
            raw_scores=np.zeros(n_sims),
            raw_factor_data=raw_data,
        )

    return {
        "OptA": _make_stats("OptA", opt_a_raw),
        "OptB": _make_stats("OptB", opt_b_raw),
        "OptC": _make_stats("OptC", opt_c_raw),
    }


@pytest.fixture
def engine(factors, mc_results):
    return WhatIfEngine(mc_results, factors)


class TestWhatIfEngine:
    def test_initialization(self, engine):
        assert len(engine.current_factors) == 3
        assert len(engine.original_factors) == 3
        assert engine._global_bounds is not None
        assert "Cost" in engine._global_bounds
        assert "Quality" in engine._global_bounds
        assert "Speed" in engine._global_bounds

    def test_initial_ranking_matches_mc_results(self, engine):
        original = engine.original_ranking()
        assert len(original) == 3
        names = [n for n, _ in original]
        assert names == sorted(names, key=lambda n: -engine.original_mc_results[n].mean_score)

    def test_recompute_original_matches_original_ranking(self, engine):
        recomputed = engine.recompute()
        original = engine.original_ranking()
        assert len(recomputed) == len(original)
        for (rn, rs), (on, os_) in zip(recomputed, original):
            assert rn == on
            assert abs(rs - os_) < 1e-6

    def test_set_weight_changes_ranking(self, engine):
        scores_before = {n: s for n, s in engine.recompute()}
        engine.set_weight("Cost", 0.9)
        engine.set_weight("Quality", 0.05)
        engine.set_weight("Speed", 0.05)
        scores_after = {n: s for n, s in engine.recompute()}
        # Weights changed — scores should differ
        assert not np.allclose(
            list(scores_before.values()), list(scores_after.values())
        )

    def test_set_weight_unknown_factor(self, engine):
        result = engine.set_weight("NonExistent", 0.5)
        assert result is False

    def test_toggle_maximize_flips_direction(self, engine):
        original = [f.maximize for f in engine.current_factors]
        result = engine.toggle_maximize("Cost")
        assert result is True  # was minimize (False), now maximize (True)
        assert engine.current_factors[0].maximize is True

    def test_toggle_maximize_unknown(self, engine):
        result = engine.toggle_maximize("NonExistent")
        assert result is None

    def test_reset_restores_original(self, engine):
        engine.set_weight("Cost", 0.9)
        engine.toggle_maximize("Cost")
        engine.reset()
        for cf, of in zip(engine.current_factors, engine.original_factors):
            assert abs(cf.weight - of.weight) < 1e-9
            assert cf.maximize == of.maximize

    def test_diff_shows_changes(self, engine):
        engine.set_weight("Cost", 0.6)
        engine.toggle_maximize("Speed")
        changes = engine.diff()
        change_text = "\n".join(changes)
        assert "Cost" in change_text
        assert "Speed" in change_text

    def test_diff_empty_when_no_changes(self, engine):
        assert engine.diff() == []

    def test_set_all_weights(self, engine):
        not_found = engine.set_all_weights({"Cost": 0.5, "Quality": 0.3, "Speed": 0.2})
        assert not_found == []
        assert abs(engine.current_factors[0].weight - 0.5) < 1e-9

    def test_set_all_weights_partial(self, engine):
        not_found = engine.set_all_weights({"Cost": 0.5, "Fake": 0.5})
        assert not_found == ["Fake"]

    def test_recompute_with_weights_temporary(self, engine):
        scores = engine.recompute_with_weights({"Cost": 0.9, "Quality": 0.1})
        assert len(scores) == 3
        # Original should be unchanged
        for f in engine.current_factors:
            of = next(
                of_ for of_ in engine.original_factors if of_.name == f.name
            )
            assert abs(f.weight - of.weight) < 1e-9

    def test_empty_results_raises(self):
        with pytest.raises(ValueError, match="must not be empty"):
            WhatIfEngine({}, [Factor("X", 1.0)])

    def test_empty_factors_raises(self, mc_results):
        with pytest.raises(ValueError, match="must not be empty"):
            WhatIfEngine(mc_results, [])

    def test_summary_table_format(self, engine):
        scores = engine.recompute()
        table = WhatIfEngine.summary_table(scores)
        assert "OptA" in table or "OptB" in table or "OptC" in table
        assert "Rank" in table
        assert "Score" in table
        assert "★" in table

    def test_factor_table_format(self, engine):
        table = WhatIfEngine.factor_table(engine.current_factors)
        assert "Cost" in table
        assert "Quality" in table
        assert "Speed" in table
        assert "↑ max" in table or "↓ min" in table

    def test_comparison_table_format(self, engine):
        orig = engine.original_ranking()
        curr = engine.recompute()
        table = WhatIfEngine.comparison_table(orig, curr)
        assert "Before" in table
        assert "After" in table
        assert "Δ" in table

    def test_suggest_returns_suggestions(self, engine):
        engine.set_weight("Cost", 0.1)
        engine.set_weight("Quality", 0.8)
        engine.set_weight("Speed", 0.1)
        suggestions = engine._suggest()
        assert isinstance(suggestions, list)
        if suggestions:
            assert any("Cost" in s or "Quality" in s for s in suggestions)

    def test_recompute_single_option(self, mc_results, factors):
        single_result = {"OptA": mc_results["OptA"]}
        eng = WhatIfEngine(single_result, factors)
        scores = eng.recompute()
        assert len(scores) == 1
        assert scores[0][0] == "OptA"

    def test_recompute_no_raw_data(self):
        """Fallback to factor_stats means when raw_factor_data is None."""
        stats = Statistics(
            option_name="Test",
            mean_score=0.5,
            std_dev=0.1,
            min_score=0.2,
            max_score=0.8,
            percentile_5=0.3,
            percentile_95=0.7,
            success_rate=0.6,
            factor_stats={
                "X": {"mean": 100.0, "std": 10.0, "p5": 85.0, "p95": 115.0},
                "Y": {"mean": 200.0, "std": 20.0, "p5": 170.0, "p95": 230.0},
            },
            var_95=0.3,
            cvar_95=0.25,
            raw_scores=None,
            raw_factor_data=None,
        )
        eng = WhatIfEngine(
            {"Test": stats},
            [Factor("X", 0.5), Factor("Y", 0.5)],
        )
        scores = eng.recompute()
        assert len(scores) == 1
        assert scores[0][0] == "Test"
        assert scores[0][1] > 0

    def test_original_ranking_order(self, engine):
        engine.set_weight("Cost", 0.9)
        engine.set_weight("Quality", 0.05)
        engine.set_weight("Speed", 0.05)
        # original_ranking should still return original order
        orig = engine.original_ranking()
        for i in range(len(orig) - 1):
            assert orig[i][1] >= orig[i + 1][1]
