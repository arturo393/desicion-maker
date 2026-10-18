"""
Range warning: min-max stretches any gap between options to the full weight; warn when that gap is tiny.
Run: uv run pytest src/decision_maker/tests/test_range_warning.py
Does NOT: change any score — it only warns.

Replaces a "scale mismatch" warning that fired on almost every analysis (2026-10-18): it compared raw
magnitudes across factors, which normalization already cancels, so it was always a false alarm.
"""

import logging

from decision_maker.core.models import DecisionOption, DistributionType, Factor
from decision_maker.core.monte_carlo import MonteCarloEngine
from decision_maker.core.orchestrator_steps import _check_range_amplification


def _mc(values: dict[str, dict[str, float]], factors: list[Factor]) -> dict:
    engine = MonteCarloEngine(num_simulations=200, seed=1)
    for f in factors:
        engine.add_factor(f)
    for name, vals in values.items():
        opt = DecisionOption(name)
        for k, v in vals.items():
            opt.add_variable(k, DistributionType.DETERMINISTIC, v)
        engine.add_option(opt)
    return engine.run()


FACTORS = [Factor("Cost", 0.3, maximize=False), Factor("Risk", 0.7, maximize=False)]


def test_warns_when_a_tiny_gap_gets_the_full_weight(caplog):
    mc = _mc({"A": {"Cost": 3000, "Risk": 0.1}, "B": {"Cost": 3100, "Risk": 0.5}}, FACTORS)
    with caplog.at_level(logging.WARNING):
        _check_range_amplification(FACTORS, mc)
    assert "Cost" in caplog.text
    assert "Risk" not in caplog.text


def test_different_magnitudes_alone_do_not_warn(caplog):
    # Exactly the case the old warning flagged: thousands against fractions. Normalization handles it.
    mc = _mc({"A": {"Cost": 3000, "Risk": 0.1}, "B": {"Cost": 5000, "Risk": 0.5}}, FACTORS)
    with caplog.at_level(logging.WARNING):
        _check_range_amplification(FACTORS, mc)
    assert caplog.text == ""


def test_identical_options_do_not_warn(caplog):
    # No gap at all: normalization gives both the same value, nothing is amplified.
    mc = _mc({"A": {"Cost": 3000, "Risk": 0.1}, "B": {"Cost": 3000, "Risk": 0.5}}, FACTORS)
    with caplog.at_level(logging.WARNING):
        _check_range_amplification(FACTORS, mc)
    assert "Cost" not in caplog.text
