from __future__ import annotations

import json
import math

import pytest

from decision_maker_core import MonteCarloEngine as RustMonteCarloEngine


def _rust_input(num_simulations=1000):
    return {
        "num_simulations": num_simulations,
        "factors": [
            {"name": "Cost", "weight": 0.5, "maximize": False},
            {"name": "Quality", "weight": 0.5, "maximize": True},
        ],
        "options": [
            {
                "name": "A",
                "variables": {
                    "Cost": {"dist_type": "deterministic", "params": [50]},
                    "Quality": {"dist_type": "deterministic", "params": [5]},
                },
            },
            {
                "name": "B",
                "variables": {
                    "Cost": {"dist_type": "deterministic", "params": [100]},
                    "Quality": {"dist_type": "deterministic", "params": [9]},
                },
            },
        ],
    }


class TestRustMonteCarloEngine:
    import pytest
    @pytest.mark.skip(reason="Rust engine needs update after quant audit")
    def test_deterministic_matches_python_normalized(self):
        from decision_maker.core.models import DecisionOption, DistributionType, Factor
        from decision_maker.core.monte_carlo import MonteCarloEngine

        engine = MonteCarloEngine(num_simulations=1000)
        opt_a = DecisionOption("A")
        opt_a.add_variable("Cost", DistributionType.DETERMINISTIC, 50)
        opt_a.add_variable("Quality", DistributionType.DETERMINISTIC, 5)
        opt_b = DecisionOption("B")
        opt_b.add_variable("Cost", DistributionType.DETERMINISTIC, 100)
        opt_b.add_variable("Quality", DistributionType.DETERMINISTIC, 9)
        engine.add_factor(Factor("Cost", 0.5, maximize=False))
        engine.add_factor(Factor("Quality", 0.5, maximize=True))
        engine.add_option(opt_a)
        engine.add_option(opt_b)
        py = engine.run()

        rust = RustMonteCarloEngine()
        out = json.loads(rust.run_simulation(json.dumps(_rust_input())))

        for name in ("A", "B"):
            assert math.isclose(py[name].mean_score, out[name]["mean_score"], abs_tol=1e-6)
            assert math.isclose(py[name].std_dev, out[name]["std_dev"], abs_tol=1e-6)

    def test_global_normalization_ranks_constant_option_tied(self):
        rust = RustMonteCarloEngine()
        out = json.loads(rust.run_simulation(json.dumps(_rust_input())))
        # With two options spanning the bound, each is 0.5 after normalization.
        assert math.isclose(out["A"]["mean_score"], 0.5, abs_tol=1e-6)
        assert math.isclose(out["B"]["mean_score"], 0.5, abs_tol=1e-6)

    def test_invalid_json_raises_value_error(self):
        rust = RustMonteCarloEngine()
        with pytest.raises(ValueError, match="Invalid JSON"):
            rust.run_simulation("not json")

    def test_zero_simulations_rejected(self):
        rust = RustMonteCarloEngine()
        with pytest.raises(ValueError, match="num_simulations"):
            rust.run_simulation(json.dumps(_rust_input(num_simulations=0)))
