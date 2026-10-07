"""Property-based testing for multicriteria decision engines using Hypothesis.

Properties tested:
a) Dominance:
   If an option is equal or better on all criteria and strictly better on at least one,
   it is never ranked below the dominated option in Monte Carlo mean score, TOPSIS,
   or PROMETHEE II.
b) Weight scaling:
   Multiplying all factor weights by an arbitrary positive scalar k > 0 preserves the
   ranking across options in Monte Carlo (normalized), TOPSIS, and PROMETHEE II.
c) Permutation invariance:
   The insertion order of options into the decision model does not alter the score
   of any option (evaluated with deterministic variables to eliminate sampling noise).
d) Rank reversal:
   Adding an irrelevant alternative that is strictly dominated by all existing options
   should not invert the relative ranking between the existing options.
   In min-max normalized weighted sum / Chen fuzzy TOPSIS, introducing a dominated
   alternative expands the range (max - min) disproportionately across criteria, which
   alters the relative weights of criteria and flips the winner.
   Hypothesis discovered a minimal counterexample:
     Weights: w = [0.25, 0.75], both criteria maximize.
     Option A = [1.0, 7.0], Option B = [2.0, 6.0].
     Before C: Score(A) = 0.75 > Score(B) = 0.25 (A wins).
     Dominated Option C = [0.0, 0.0] added (C < A and C < B on both criteria).
     After C:  Score(A) = 0.875 < Score(B) = 0.8929 (B wins!).
   Marked as pytest.mark.xfail(strict=True) per the golden rule.
"""

from __future__ import annotations

from typing import Any

import pandas as pd
import pytest
from hypothesis import example, given, settings
from hypothesis import strategies as st

from decision_maker.core.models import DecisionOption, DistributionType, Factor
from decision_maker.core.monte_carlo import MonteCarloEngine
from decision_maker.core.promethee import PrometheeConfig, PrometheeEngine
from decision_maker.core.topsis import TOPSISEngine

# Named constants to avoid magic numbers (per AGENTS.md conventions)
MAX_HYPOTHESIS_EXAMPLES: int = 40
FLOAT_SCORE_TOLERANCE: float = 1e-9
SIMULATION_RUN_SIZE: int = 50
SIMULATION_FIXED_SEED: int = 42


# ==============================================================================
# Strategies
# ==============================================================================

@st.composite
def dominance_strategy(draw: Any) -> tuple[list[float], list[bool], list[float], list[float]]:
    """Generates (weights, maximize_flags, values_A, values_B) where A dominates B."""
    n_criteria = 3
    weights = [draw(st.floats(min_value=0.1, max_value=2.0)) for _ in range(n_criteria)]
    maxs = [draw(st.booleans()) for _ in range(n_criteria)]
    base_b = [draw(st.floats(min_value=10.0, max_value=50.0)) for _ in range(n_criteria)]
    deltas = [draw(st.floats(min_value=0.0, max_value=10.0)) for _ in range(n_criteria)]
    # Ensure criterion 0 is strictly better
    deltas[0] = draw(st.floats(min_value=0.5, max_value=10.0))

    vals_a = [base_b[i] + deltas[i] if maxs[i] else base_b[i] - deltas[i] for i in range(n_criteria)]
    vals_b = list(base_b)
    return weights, maxs, vals_a, vals_b


@st.composite
def weight_scaling_strategy(draw: Any) -> tuple[list[float], float, list[float], list[float]]:
    """Generates criteria weights, a scaling factor k > 0, and values for options A and B."""
    weights = [
        draw(st.floats(min_value=0.1, max_value=2.0)),
        draw(st.floats(min_value=0.1, max_value=2.0)),
    ]
    k = draw(st.floats(min_value=0.1, max_value=10.0))
    a_vals = [
        draw(st.floats(min_value=5.0, max_value=50.0)),
        draw(st.floats(min_value=5.0, max_value=50.0)),
    ]
    b_vals = [
        draw(st.floats(min_value=5.0, max_value=50.0)),
        draw(st.floats(min_value=5.0, max_value=50.0)),
    ]
    return weights, k, a_vals, b_vals


@st.composite
def permutation_strategy(draw: Any) -> dict[str, list[float]]:
    """Generates deterministic attribute values for 3 distinct options."""
    return {
        "A": [draw(st.floats(min_value=1.0, max_value=50.0)), draw(st.floats(min_value=1.0, max_value=50.0))],
        "B": [draw(st.floats(min_value=1.0, max_value=50.0)), draw(st.floats(min_value=1.0, max_value=50.0))],
        "C": [draw(st.floats(min_value=1.0, max_value=50.0)), draw(st.floats(min_value=1.0, max_value=50.0))],
    }


@st.composite
def rank_reversal_scenario(draw: Any) -> tuple[float, float, float, float, float, float, float, float]:
    """Generates options A, B and a strictly dominated option C with 2 criteria."""
    w1 = draw(st.floats(min_value=0.1, max_value=0.9))
    w2 = 1.0 - w1
    a1 = draw(st.floats(min_value=1.0, max_value=20.0))
    a2 = draw(st.floats(min_value=1.0, max_value=20.0))
    b1 = draw(st.floats(min_value=1.0, max_value=20.0))
    b2 = draw(st.floats(min_value=1.0, max_value=20.0))
    # Option C is strictly dominated by both A and B on both criteria
    c1 = draw(st.floats(min_value=-50.0, max_value=min(a1, b1) - 0.5))
    c2 = draw(st.floats(min_value=-50.0, max_value=min(a2, b2) - 0.5))
    return w1, w2, a1, a2, b1, b2, c1, c2


# ==============================================================================
# Property Tests
# ==============================================================================

class TestPropertyBasedVerification:
    """Verifies axiomatic multicriteria decision properties using hypothesis."""

    @settings(max_examples=MAX_HYPOTHESIS_EXAMPLES, deadline=None)
    @given(data=dominance_strategy())
    def test_dominance_property_monte_carlo(
        self,
        data: tuple[list[float], list[bool], list[float], list[float]],
    ) -> None:
        """Dominance: dominant option A must achieve mean_score >= dominated option B in Monte Carlo."""
        weights, maxs, vals_a, vals_b = data
        mc = MonteCarloEngine(num_simulations=SIMULATION_RUN_SIZE, seed=SIMULATION_FIXED_SEED)
        for i, (w, m) in enumerate(zip(weights, maxs, strict=True)):
            mc.add_factor(Factor(name=f"f{i}", weight=w, maximize=m))

        opt_a = DecisionOption(name="Dominant")
        opt_b = DecisionOption(name="Dominated")
        for i in range(len(weights)):
            opt_a.add_variable(f"f{i}", DistributionType.DETERMINISTIC, vals_a[i])
            opt_b.add_variable(f"f{i}", DistributionType.DETERMINISTIC, vals_b[i])
        mc.add_option(opt_a)
        mc.add_option(opt_b)

        results = mc.run(normalize=True)
        assert results["Dominant"].mean_score >= results["Dominated"].mean_score - FLOAT_SCORE_TOLERANCE

    @settings(max_examples=MAX_HYPOTHESIS_EXAMPLES, deadline=None)
    @given(data=dominance_strategy())
    def test_dominance_property_topsis(
        self,
        data: tuple[list[float], list[bool], list[float], list[float]],
    ) -> None:
        """Dominance: dominant option A must achieve score >= dominated option B in TOPSIS."""
        weights, maxs, vals_a, vals_b = data
        n_crit = len(weights)
        matrix = {
            "Dominant": {f"f{i}": (vals_a[i],) * 3 for i in range(n_crit)},
            "Dominated": {f"f{i}": (vals_b[i],) * 3 for i in range(n_crit)},
        }
        scores = TOPSISEngine().analyze(matrix, weights, maxs)
        assert scores["Dominant"] >= scores["Dominated"] - FLOAT_SCORE_TOLERANCE

    @settings(max_examples=MAX_HYPOTHESIS_EXAMPLES, deadline=None)
    @given(data=dominance_strategy())
    def test_dominance_property_promethee_ii(
        self,
        data: tuple[list[float], list[bool], list[float], list[float]],
    ) -> None:
        """Dominance: dominant option A must achieve net flow >= dominated option B in PROMETHEE II."""
        weights, maxs, vals_a, vals_b = data
        n_crit = len(weights)
        col_names = [f"f{i}" for i in range(n_crit)]
        df = pd.DataFrame([vals_a, vals_b], index=["Dominant", "Dominated"], columns=col_names)
        cfg = PrometheeConfig(weights=weights, maximize=maxs, pref_types=["usual"] * n_crit)
        flows = PrometheeEngine().analyze(df, cfg)
        assert flows["Dominant"] >= flows["Dominated"] - FLOAT_SCORE_TOLERANCE

    @settings(max_examples=MAX_HYPOTHESIS_EXAMPLES, deadline=None)
    @given(data=weight_scaling_strategy())
    def test_weight_scaling_property_monte_carlo(
        self,
        data: tuple[list[float], float, list[float], list[float]],
    ) -> None:
        """Weight scaling: scaling weights by k > 0 preserves relative ordering in Monte Carlo."""
        weights, k, a_vals, b_vals = data
        scaled_weights = [w * k for w in weights]
        maxs = [True, False]

        def _evaluate(w_list: list[float]) -> dict[str, float]:
            engine = MonteCarloEngine(num_simulations=SIMULATION_RUN_SIZE, seed=SIMULATION_FIXED_SEED)
            for i, w in enumerate(w_list):
                engine.add_factor(Factor(name=f"f{i}", weight=w, maximize=maxs[i]))
            for name, vals in [("A", a_vals), ("B", b_vals)]:
                opt = DecisionOption(name=name)
                for i, v in enumerate(vals):
                    opt.add_variable(f"f{i}", DistributionType.DETERMINISTIC, v)
                engine.add_option(opt)
            res = engine.run(normalize=True)
            return {name: res[name].mean_score for name in ("A", "B")}

        base_res = _evaluate(weights)
        scaled_res = _evaluate(scaled_weights)
        base_diff = base_res["A"] - base_res["B"]
        scaled_diff = scaled_res["A"] - scaled_res["B"]
        assert (base_diff * scaled_diff) >= -FLOAT_SCORE_TOLERANCE

    @settings(max_examples=MAX_HYPOTHESIS_EXAMPLES, deadline=None)
    @given(data=weight_scaling_strategy())
    def test_weight_scaling_property_topsis(
        self,
        data: tuple[list[float], float, list[float], list[float]],
    ) -> None:
        """Weight scaling: scaling weights by k > 0 preserves relative ordering in TOPSIS."""
        weights, k, a_vals, b_vals = data
        scaled_weights = [w * k for w in weights]
        maxs = [True, False]
        matrix = {
            "A": {f"f{i}": (a_vals[i],) * 3 for i in range(2)},
            "B": {f"f{i}": (b_vals[i],) * 3 for i in range(2)},
        }
        s1 = TOPSISEngine().analyze(matrix, weights, maxs)
        s2 = TOPSISEngine().analyze(matrix, scaled_weights, maxs)
        diff1 = s1["A"] - s1["B"]
        diff2 = s2["A"] - s2["B"]
        assert (diff1 * diff2) >= -FLOAT_SCORE_TOLERANCE

    @settings(max_examples=MAX_HYPOTHESIS_EXAMPLES, deadline=None)
    @given(data=weight_scaling_strategy())
    def test_weight_scaling_property_promethee_ii(
        self,
        data: tuple[list[float], float, list[float], list[float]],
    ) -> None:
        """Weight scaling: scaling weights by k > 0 preserves relative ordering in PROMETHEE II."""
        weights, k, a_vals, b_vals = data
        scaled_weights = [w * k for w in weights]
        maxs = [True, False]
        df = pd.DataFrame([a_vals, b_vals], index=["A", "B"], columns=["f0", "f1"])
        f1 = PrometheeEngine().analyze(df, PrometheeConfig(weights=weights, maximize=maxs))
        f2 = PrometheeEngine().analyze(df, PrometheeConfig(weights=scaled_weights, maximize=maxs))
        diff1 = f1["A"] - f1["B"]
        diff2 = f2["A"] - f2["B"]
        assert (diff1 * diff2) >= -FLOAT_SCORE_TOLERANCE

    @settings(max_examples=MAX_HYPOTHESIS_EXAMPLES, deadline=None)
    @given(data=permutation_strategy())
    def test_permutation_invariance_monte_carlo(self, data: dict[str, list[float]]) -> None:
        """Permutation: insertion order of options does not alter any option's score in Monte Carlo."""
        weights = [0.6, 0.4]
        maxs = [True, False]

        def _run_with_order(order: list[str]) -> dict[str, float]:
            engine = MonteCarloEngine(num_simulations=SIMULATION_RUN_SIZE, seed=SIMULATION_FIXED_SEED)
            for i, w in enumerate(weights):
                engine.add_factor(Factor(name=f"f{i}", weight=w, maximize=maxs[i]))
            for name in order:
                opt = DecisionOption(name=name)
                for i, v in enumerate(data[name]):
                    opt.add_variable(f"f{i}", DistributionType.DETERMINISTIC, v)
                engine.add_option(opt)
            res = engine.run(normalize=True)
            return {name: res[name].mean_score for name in ("A", "B", "C")}

        r1 = _run_with_order(["A", "B", "C"])
        r2 = _run_with_order(["C", "A", "B"])
        for name in ("A", "B", "C"):
            assert pytest.approx(r1[name], abs=FLOAT_SCORE_TOLERANCE) == r2[name]

    @settings(max_examples=MAX_HYPOTHESIS_EXAMPLES, deadline=None)
    @given(data=permutation_strategy())
    def test_permutation_invariance_topsis(self, data: dict[str, list[float]]) -> None:
        """Permutation: insertion order does not alter option scores in TOPSIS."""
        weights = [0.6, 0.4]
        maxs = [True, False]
        mat1 = {name: {f"f{i}": (data[name][i],) * 3 for i in range(2)} for name in ["A", "B", "C"]}
        mat2 = {name: {f"f{i}": (data[name][i],) * 3 for i in range(2)} for name in ["C", "B", "A"]}
        s1 = TOPSISEngine().analyze(mat1, weights, maxs)
        s2 = TOPSISEngine().analyze(mat2, weights, maxs)
        for name in ("A", "B", "C"):
            assert pytest.approx(s1[name], abs=FLOAT_SCORE_TOLERANCE) == s2[name]

    @settings(max_examples=MAX_HYPOTHESIS_EXAMPLES, deadline=None)
    @given(data=permutation_strategy())
    def test_permutation_invariance_promethee_ii(self, data: dict[str, list[float]]) -> None:
        """Permutation: row order does not alter option net flows in PROMETHEE II."""
        weights = [0.6, 0.4]
        maxs = [True, False]
        df1 = pd.DataFrame([data[name] for name in ["A", "B", "C"]], index=["A", "B", "C"], columns=["f0", "f1"])
        df2 = pd.DataFrame([data[name] for name in ["B", "C", "A"]], index=["B", "C", "A"], columns=["f0", "f1"])
        f1 = PrometheeEngine().analyze(df1, PrometheeConfig(weights=weights, maximize=maxs))
        f2 = PrometheeEngine().analyze(df2, PrometheeConfig(weights=weights, maximize=maxs))
        for name in ("A", "B", "C"):
            assert pytest.approx(f1[name], abs=FLOAT_SCORE_TOLERANCE) == f2[name]

    @pytest.mark.xfail(
        strict=True,
        reason=(
            "Rank reversal confirmed in min-max TOPSIS (kanban card: 'Puntaje relativo y rank reversal'). "
            "Minimal counterexample found by hypothesis: "
            "Weights w=[0.25, 0.75], criteria both benefit. Option A=[1.0, 7.0], Option B=[2.0, 6.0]. "
            "Without Option C: Score(A)=0.7500 > Score(B)=0.2500 (A wins, gap +0.5000). "
            "Dominated Option C=[0.0, 0.0] added (C < A and C < B on both criteria). "
            "With Option C: Score(A)=0.8750 < Score(B)=0.8929 (B wins, gap -0.0179). "
            "Introducing the dominated alternative expands criterion ranges non-uniformly, flipping the ranking."
        ),
    )
    @settings(max_examples=MAX_HYPOTHESIS_EXAMPLES, deadline=None)
    @given(data=rank_reversal_scenario())
    # The known counterexample runs on every invocation. Without it, strict xfail depended on the
    # random search finding one again: a CI run that missed it would XPASS and go red for no reason.
    @example(data=(0.25, 0.75, 1.0, 7.0, 2.0, 6.0, 0.0, 0.0))
    def test_rank_reversal_topsis_with_dominated_third_option(
        self,
        data: tuple[float, float, float, float, float, float, float, float],
    ) -> None:
        """Rank reversal: adding a third option strictly dominated by A and B should not flip rank(A) vs rank(B).

        This property is known to fail in min-max normalization because introducing an extreme
        dominated alternative expands the denominator (max - min) on some criteria and not others,
        distorting the relative weights.
        """
        w1, w2, a1, a2, b1, b2, c1, c2 = data
        engine = TOPSISEngine()
        weights = [w1, w2]
        maxs = [True, True]

        mat2 = {
            "A": {"f1": (a1, a1, a1), "f2": (a2, a2, a2)},
            "B": {"f1": (b1, b1, b1), "f2": (b2, b2, b2)},
        }
        res2 = engine.analyze(mat2, weights, maxs)
        # Skip if initial scores are indistinguishable
        if abs(res2["A"] - res2["B"]) < 1e-4:
            return

        a_better_before = res2["A"] > res2["B"]

        # Add Option C, which is strictly dominated by both A and B
        mat3 = dict(mat2)
        mat3["C"] = {"f1": (c1, c1, c1), "f2": (c2, c2, c2)}
        res3 = engine.analyze(mat3, weights, maxs)
        a_better_after = res3["A"] > res3["B"]

        assert a_better_before == a_better_after, (
            f"Rank reversal occurred! Before C: A={res2['A']:.4f}, B={res2['B']:.4f}. "
            f"After adding dominated C: A={res3['A']:.4f}, B={res3['B']:.4f}"
        )
