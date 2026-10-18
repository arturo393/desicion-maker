"""
Weight robustness: how often each option wins when the weights are uncertain too, not only the scores.
Run: uv run pytest src/decision_maker/tests/test_weight_robustness.py
Does NOT: test the Monte Carlo sampling itself (test_monte_carlo.py); the inputs here are deterministic on purpose.
"""

import numpy as np
import pytest
from scipy import stats

from decision_maker.core.models import DecisionOption, DistributionType, Factor
from decision_maker.core.monte_carlo import MonteCarloEngine
from decision_maker.core.weight_robustness import weight_robustness

N = 20_000


def _mc(options: dict[str, dict[str, float]], factors: list[Factor], dist: bool = False) -> dict:
    engine = MonteCarloEngine(num_simulations=N, seed=7)
    for f in factors:
        engine.add_factor(f)
    for name, values in options.items():
        opt = DecisionOption(name)
        for factor, v in values.items():
            if dist:
                opt.add_variable(factor, DistributionType.NORMAL, v, 0.3)
            else:
                opt.add_variable(factor, DistributionType.DETERMINISTIC, v)
        engine.add_option(opt)
    return engine.run()


SWAP = {"A": {"f1": 1.0, "f2": 0.0}, "B": {"f1": 0.0, "f2": 1.0}}


class TestAgainstClosedForm:
    """A=(1,0), B=(0,1): A wins exactly when w1 > w2, so P(A first) is a Beta tail."""

    def test_uninformed_weights_split_evenly(self):
        r = weight_robustness(_mc(SWAP, [Factor("f1", 0.7), Factor("f2", 0.3)]), [Factor("f1", 0.7), Factor("f2", 0.3)],
                              seed=1)
        assert r.uninformed["A"] == pytest.approx(0.5, abs=0.015)

    @pytest.mark.parametrize("concentration", [2.0, 10.0, 50.0])
    def test_informed_weights_match_the_beta_tail(self, concentration):
        factors = [Factor("f1", 0.7), Factor("f2", 0.3)]
        r = weight_robustness(_mc(SWAP, factors), factors, concentration=concentration, seed=1)
        # w1 ~ Beta(0.7k, 0.3k); A first iff w1 > 0.5
        expected = stats.beta.sf(0.5, 0.7 * concentration, 0.3 * concentration)
        assert r.informed["A"] == pytest.approx(expected, abs=0.015)

    def test_central_weights_sit_on_the_winning_side(self):
        factors = [Factor("f1", 0.5), Factor("f2", 0.5)]
        r = weight_robustness(_mc(SWAP, factors), factors, seed=1)
        assert r.central_weights["A"]["f1"] > 0.5
        assert r.central_weights["B"]["f2"] > 0.5


class TestProperties:
    def test_a_dominant_option_wins_under_every_weight(self):
        opts = {"A": {"f1": 3.0, "f2": 3.0}, "B": {"f1": 1.0, "f2": 2.0}, "C": {"f1": 2.0, "f2": 1.0}}
        factors = [Factor("f1", 0.5), Factor("f2", 0.5)]
        r = weight_robustness(_mc(opts, factors), factors, seed=1)
        assert r.uninformed["A"] == 1.0
        assert r.informed["A"] == 1.0
        assert r.verdict == "robust"

    def test_acceptability_is_a_doubly_stochastic_matrix(self):
        opts = {"A": {"f1": 3.0, "f2": 1.0}, "B": {"f1": 1.0, "f2": 3.0}, "C": {"f1": 2.0, "f2": 2.0}}
        factors = [Factor("f1", 0.5), Factor("f2", 0.5, maximize=False)]
        r = weight_robustness(_mc(opts, factors, dist=True), factors, seed=1)
        m = np.array([r.rank_acceptability[o] for o in opts])
        assert m.sum(axis=1) == pytest.approx(np.ones(3))  # every option takes some rank
        assert m.sum(axis=0) == pytest.approx(np.ones(3))  # every rank is taken by someone

    def test_minimized_factor_is_inverted(self):
        opts = {"A": {"cost": 1.0}, "B": {"cost": 5.0}}
        factors = [Factor("cost", 1.0, maximize=False)]
        r = weight_robustness(_mc(opts, factors), factors, seed=1)
        assert r.informed["A"] == 1.0

    def test_huge_concentration_reproduces_the_stated_weights(self):
        factors = [Factor("f1", 0.6), Factor("f2", 0.4)]
        r = weight_robustness(_mc(SWAP, factors), factors, concentration=1e6, seed=1)
        assert r.stated_winner == "A"
        assert r.informed["A"] == pytest.approx(1.0, abs=1e-3)

    def test_seeded_runs_are_identical(self):
        factors = [Factor("f1", 0.6), Factor("f2", 0.4)]
        mc = _mc(SWAP, factors, dist=True)
        assert weight_robustness(mc, factors, seed=3) == weight_robustness(mc, factors, seed=3)

    def test_contested_when_the_stated_winner_barely_leads(self):
        # Two options can never be fragile: with weights centred on the stated ones, a Beta whose mean
        # is past the switch point also has its median past it. It takes more options.
        factors = [Factor("f1", 0.52), Factor("f2", 0.48)]
        r = weight_robustness(_mc(SWAP, factors), factors, concentration=2.0, seed=1)
        assert r.stated_winner == "A"
        assert r.verdict == "contested"

    def test_fragile_when_a_specialist_edges_out_a_balanced_option(self):
        # A leads by 0.005 at the stated weights, but wins only when w1 is the largest weight AND
        # above 0.335: about one draw in three. The balanced D takes most of the rest.
        opts = {"A": {"f1": 1, "f2": 0, "f3": 0}, "B": {"f1": 0, "f2": 1, "f3": 0},
                "C": {"f1": 0, "f2": 0, "f3": 1}, "D": {"f1": 0.335, "f2": 0.335, "f3": 0.335}}
        factors = [Factor("f1", 0.34), Factor("f2", 0.33), Factor("f3", 0.33)]
        r = weight_robustness(_mc(opts, factors), factors, seed=1)
        assert r.stated_winner == "A"
        assert r.informed["A"] < 0.5
        assert r.verdict == "fragile"


class TestRefusals:
    def test_needs_two_options(self):
        factors = [Factor("f1", 1.0)]
        with pytest.raises(ValueError, match="two options"):
            weight_robustness(_mc({"A": {"f1": 1.0}}, factors), factors)

    def test_needs_positive_concentration(self):
        factors = [Factor("f1", 0.5), Factor("f2", 0.5)]
        with pytest.raises(ValueError, match="concentration"):
            weight_robustness(_mc(SWAP, factors), factors, concentration=0.0)

    def test_needs_the_raw_samples(self):
        factors = [Factor("f1", 0.5), Factor("f2", 0.5)]
        mc = _mc(SWAP, factors)
        mc["A"].raw_factor_data = None
        with pytest.raises(ValueError, match="raw_factor_data"):
            weight_robustness(mc, factors)
