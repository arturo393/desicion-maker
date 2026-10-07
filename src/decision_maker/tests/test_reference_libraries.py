"""Verification of core decision engines against established external library pymcdm.

What is compared:
1. PROMETHEE II:
   - Evaluates `PrometheeEngine.analyze` with `PrometheeConfig` against `pymcdm.methods.PROMETHEE_II`.
   - Tests both the "usual" preference function (Heaviside step) and "vshape" linear criterion
     across fixed and pseudo-random decision matrices with mixed benefit and cost criteria.
   - Compares both net outranking flows (phi) and the resulting option rankings.
   - Note on pymcdm: `pymcdm.methods.PROMETHEE_II` initializes preference functions via a generator
     expression when parameter lists (p, q) are passed; a fresh instance is constructed for each
     evaluation to prevent generator exhaustion.

2. TOPSIS:
   - Evaluates `TOPSISEngine.analyze` on crisp inputs (degenerate fuzzy numbers a = b = c)
     against `pymcdm.methods.TOPSIS`.
   - Expected difference: `TOPSISEngine` implements Chen-style fuzzy TOPSIS, which on crisp inputs
     collapses to an L1 sum of criterion distances (equivalent to a min-max weighted sum).
     In contrast, `pymcdm.methods.TOPSIS` employs Euclidean distance (L2 norm) in the normalized
     criteria space. This produces differing closeness scores and ranking flips on multi-attribute data.
     Marked as pytest.mark.xfail(strict=True) per the golden rule, citing the kanban card
     "Decidir qué TOPSIS queremos: hoy, con datos crisp, es una suma ponderada".
   - Confirmatory characterization: `TOPSISEngine` on crisp inputs is compared against
     an explicit step-by-step min-max weighted sum in numpy and against
     `pymcdm.methods.WSM(normalizations.minmax_normalization)` across multiple random seeds.
     These comparisons are expected to pass identically.

Library versions:
- pymcdm version is dynamically retrieved from `importlib.metadata.version("pymcdm")`.
"""

from __future__ import annotations

import importlib.metadata

import numpy as np
import pandas as pd
import pytest
from pymcdm import normalizations
from pymcdm.methods import PROMETHEE_II, TOPSIS, WSM

from decision_maker.core.promethee import PrometheeConfig, PrometheeEngine
from decision_maker.core.topsis import TOPSISEngine

# Named constants to avoid magic numbers (per AGENTS.md conventions)
PYMCDM_VERSION: str = importlib.metadata.version("pymcdm")
FLOW_TOLERANCE: float = 1e-6
WEIGHTED_SUM_TOLERANCE: float = 1e-9
RANDOM_SEEDS: tuple[int, ...] = (101, 202, 303, 404, 505)


class TestPrometheeAgainstPymcdm:
    """Verifies PrometheeEngine against pymcdm.methods.PROMETHEE_II."""

    def test_promethee_ii_usual_preference_fixed_matrix(self) -> None:
        """Compare net flows and ranking using 'usual' preference on a fixed 3x3 matrix."""
        matrix = np.array(
            [
                [4.0, 3.0, 2.0],
                [3.0, 2.0, 4.0],
                [5.0, 1.0, 3.0],
            ]
        )
        weights = [0.5, 0.3, 0.2]
        # Criteria: C1 is benefit (maximize), C2 is cost (minimize), C3 is benefit (maximize)
        maximize = [True, False, True]
        types = np.array([1 if m else -1 for m in maximize])
        names = ["A1", "A2", "A3"]

        # Run reference library (pymcdm)
        pymcdm_body = PROMETHEE_II("usual")
        expected_flows = pymcdm_body(matrix, np.array(weights), types)

        # Run our engine
        df = pd.DataFrame(matrix, index=names, columns=["C1", "C2", "C3"])
        cfg = PrometheeConfig(
            weights=weights,
            maximize=maximize,
            pref_types=["usual", "usual", "usual"],
        )
        our_scores = PrometheeEngine().analyze(df, cfg)

        # Verify net flows match pymcdm exactly
        for i, name in enumerate(names):
            assert pytest.approx(float(expected_flows[i]), abs=FLOW_TOLERANCE) == our_scores[name], (
                f"Net flow mismatch against pymcdm {PYMCDM_VERSION} for {name}: "
                f"expected {expected_flows[i]}, got {our_scores[name]}"
            )

        # Verify option rankings match
        expected_ranking = [names[i] for i in np.argsort(-expected_flows)]
        our_ranking = our_scores.index.tolist()
        assert our_ranking == expected_ranking, (
            f"Ranking mismatch against pymcdm {PYMCDM_VERSION}: "
            f"expected {expected_ranking}, got {our_ranking}"
        )

    def test_promethee_ii_vshape_preference_fixed_matrix(self) -> None:
        """Compare net flows and ranking using 'vshape' preference with parameters p."""
        matrix = np.array(
            [
                [4.0, 3.0, 2.0],
                [3.0, 2.0, 4.0],
                [5.0, 1.0, 3.0],
            ]
        )
        weights = [0.5, 0.3, 0.2]
        maximize = [True, False, True]
        types = np.array([1 if m else -1 for m in maximize])
        names = ["A1", "A2", "A3"]
        p_params = [2.0, 1.5, 2.0]

        # Run reference library (pymcdm)
        pymcdm_body = PROMETHEE_II("vshape", p=p_params)
        expected_flows = pymcdm_body(matrix, np.array(weights), types)

        # Run our engine
        df = pd.DataFrame(matrix, index=names, columns=["C1", "C2", "C3"])
        cfg = PrometheeConfig(
            weights=weights,
            maximize=maximize,
            pref_types=["vshape", "vshape", "vshape"],
            pref_params=[{"p": p_params[0]}, {"p": p_params[1]}, {"p": p_params[2]}],
        )
        our_scores = PrometheeEngine().analyze(df, cfg)

        for i, name in enumerate(names):
            assert pytest.approx(float(expected_flows[i]), abs=FLOW_TOLERANCE) == our_scores[name], (
                f"Net flow mismatch against pymcdm {PYMCDM_VERSION} (vshape) for {name}: "
                f"expected {expected_flows[i]}, got {our_scores[name]}"
            )

        expected_ranking = [names[i] for i in np.argsort(-expected_flows)]
        our_ranking = our_scores.index.tolist()
        assert our_ranking == expected_ranking

    def test_promethee_ii_matches_pymcdm_across_random_matrices(self) -> None:
        """Validate both 'usual' and 'vshape' PROMETHEE II over multiple seeded pseudo-random matrices."""
        for seed in RANDOM_SEEDS:
            rng = np.random.default_rng(seed)
            n_options, n_criteria = 4, 3
            matrix = rng.uniform(10.0, 100.0, (n_options, n_criteria))
            raw_weights = rng.uniform(0.1, 1.0, n_criteria)
            weights = (raw_weights / raw_weights.sum()).tolist()
            maximize = [bool(rng.choice([True, False])) for _ in range(n_criteria)]
            types = np.array([1 if m else -1 for m in maximize])
            names = [f"Alt{i}" for i in range(n_options)]
            col_names = [f"Crit{j}" for j in range(n_criteria)]
            df = pd.DataFrame(matrix, index=names, columns=col_names)

            # 1. Usual preference
            pymcdm_usual = PROMETHEE_II("usual")
            expected_usual = pymcdm_usual(matrix, np.array(weights), types)
            cfg_usual = PrometheeConfig(
                weights=weights,
                maximize=maximize,
                pref_types=["usual"] * n_criteria,
            )
            our_usual = PrometheeEngine().analyze(df, cfg_usual)

            for i, name in enumerate(names):
                assert pytest.approx(float(expected_usual[i]), abs=FLOW_TOLERANCE) == our_usual[name], (
                    f"[Seed {seed}] Usual net flow mismatch against pymcdm {PYMCDM_VERSION} for {name}"
                )

            # 2. V-shape preference
            p_thresholds = (rng.uniform(10.0, 40.0, n_criteria)).tolist()
            pymcdm_vshape = PROMETHEE_II("vshape", p=p_thresholds)
            expected_vshape = pymcdm_vshape(matrix, np.array(weights), types)
            cfg_vshape = PrometheeConfig(
                weights=weights,
                maximize=maximize,
                pref_types=["vshape"] * n_criteria,
                pref_params=[{"p": p} for p in p_thresholds],
            )
            our_vshape = PrometheeEngine().analyze(df, cfg_vshape)

            for i, name in enumerate(names):
                assert pytest.approx(float(expected_vshape[i]), abs=FLOW_TOLERANCE) == our_vshape[name], (
                    f"[Seed {seed}] V-shape net flow mismatch against pymcdm {PYMCDM_VERSION} for {name}"
                )


class TestTopsisAgainstPymcdm:
    """Evaluates TOPSISEngine against pymcdm methods (TOPSIS and WSM)."""

    @pytest.mark.xfail(
        strict=True,
        reason=(
            "Methodological divergence (kanban card: 'Decidir qué TOPSIS queremos: hoy, con datos "
            "crisp, es una suma ponderada'): TOPSISEngine implements Chen-style fuzzy TOPSIS, which on crisp "
            "data computes an L1 sum of distances across criteria (min-max weighted sum). In contrast, "
            "pymcdm.methods.TOPSIS uses Euclidean distance (L2 norm) in normalized criteria space. "
            "On Hwang & Yoon fighter data, our engine scores A3 (0.5917) > A1 (0.5738) > A4 (0.3810) > "
            "A2 (0.3000), whereas pymcdm TOPSIS scores A1 (0.6127) > A3 (0.5306) > A2 (0.3660) > A4 (0.3517)."
        ),
    )
    def test_crisp_topsis_matches_pymcdm_topsis(self) -> None:
        """Compares TOPSISEngine against pymcdm.methods.TOPSIS on crisp multi-criteria data.

        This test is expected to fail strictly because TOPSISEngine uses an L1 sum of distances
        while pymcdm.methods.TOPSIS uses Euclidean (L2) distance to positive and negative ideal solutions.
        """
        matrix = np.array(
            [
                [2.0, 1500.0, 20000.0, 5.5, 5.0, 9.0],
                [2.5, 2700.0, 18000.0, 6.5, 3.0, 5.0],
                [1.8, 2000.0, 21000.0, 4.5, 7.0, 7.0],
                [2.2, 1800.0, 20000.0, 5.0, 5.0, 5.0],
            ]
        )
        weights = [0.2, 0.1, 0.1, 0.1, 0.2, 0.3]
        maximize = [True, True, True, False, True, True]
        types = np.array([1 if m else -1 for m in maximize])
        names = ["A1", "A2", "A3", "A4"]

        # Run pymcdm TOPSIS
        pymcdm_topsis = TOPSIS()
        expected_scores = pymcdm_topsis(matrix, np.array(weights), types)
        expected_ranking = [names[i] for i in np.argsort(-expected_scores)]

        # Run our engine with crisp degenerate triangular fuzzy numbers (a=b=c)
        matrix_fuzzy = {
            names[i]: {f"C{j}": (float(matrix[i, j]),) * 3 for j in range(6)}
            for i in range(len(names))
        }
        our_scores = TOPSISEngine().analyze(matrix_fuzzy, weights, maximize)
        our_ranking = our_scores.index.tolist()

        # Both scores and ranking diverge:
        # pymcdm ranking: ['A1', 'A3', 'A2', 'A4']
        # our ranking:    ['A3', 'A1', 'A4', 'A2']
        assert our_ranking == expected_ranking, (
            f"Against pymcdm {PYMCDM_VERSION} TOPSIS: expected ranking {expected_ranking}, "
            f"got {our_ranking}"
        )

    def test_crisp_topsis_matches_numpy_minmax_weighted_sum_random_matrices(self) -> None:
        """Confirms that TOPSISEngine on crisp inputs is mathematically identical to a min-max weighted sum.

        With a=b=c, Chen fuzzy vertex distance simplifies to |x_ij - x_ideal|, and the sum over
        criteria yields exactly the linear weighted sum of min-max normalized values.
        """
        for seed in RANDOM_SEEDS:
            rng = np.random.default_rng(seed)
            n_options, n_criteria = 4, 3
            matrix = rng.uniform(5.0, 50.0, (n_options, n_criteria))
            raw_weights = rng.uniform(0.1, 1.0, n_criteria)
            weights = (raw_weights / raw_weights.sum()).tolist()
            maximize = [bool(rng.choice([True, False])) for _ in range(n_criteria)]
            names = [f"Opt{i}" for i in range(n_options)]

            # Step-by-step min-max weighted sum in numpy
            lo = matrix.min(axis=0)
            hi = matrix.max(axis=0)
            norm = np.where(np.array(maximize), (matrix - lo) / (hi - lo), (hi - matrix) / (hi - lo))
            expected_scores = norm @ np.array(weights)

            # Our TOPSISEngine on crisp numbers
            matrix_fuzzy = {
                names[i]: {f"C{j}": (float(matrix[i, j]),) * 3 for j in range(n_criteria)}
                for i in range(n_options)
            }
            our_scores = TOPSISEngine().analyze(matrix_fuzzy, weights, maximize)

            for i, name in enumerate(names):
                assert pytest.approx(float(expected_scores[i]), abs=WEIGHTED_SUM_TOLERANCE) == our_scores[name], (
                    f"[Seed {seed}] Mismatch between crisp TOPSIS and numpy min-max weighted sum for {name}"
                )

    def test_crisp_topsis_matches_pymcdm_wsm_minmax(self) -> None:
        """Confirms that TOPSISEngine on crisp inputs matches pymcdm WSM with min-max normalization.

        `pymcdm.methods.WSM(normalizations.minmax_normalization)` serves as a second external
        library reference confirming that our TOPSIS engine produces the exact min-max weighted sum.
        """
        for seed in RANDOM_SEEDS:
            rng = np.random.default_rng(seed)
            n_options, n_criteria = 4, 3
            matrix = rng.uniform(10.0, 100.0, (n_options, n_criteria))
            raw_weights = rng.uniform(0.1, 1.0, n_criteria)
            weights = (raw_weights / raw_weights.sum()).tolist()
            maximize = [bool(rng.choice([True, False])) for _ in range(n_criteria)]
            types = np.array([1 if m else -1 for m in maximize])
            names = [f"A{i}" for i in range(n_options)]

            # pymcdm WSM with minmax_normalization
            wsm = WSM(normalizations.minmax_normalization)
            expected_scores = wsm(matrix, np.array(weights), types)

            # Our TOPSISEngine
            matrix_fuzzy = {
                names[i]: {f"C{j}": (float(matrix[i, j]),) * 3 for j in range(n_criteria)}
                for i in range(n_options)
            }
            our_scores = TOPSISEngine().analyze(matrix_fuzzy, weights, maximize)

            for i, name in enumerate(names):
                assert pytest.approx(float(expected_scores[i]), abs=WEIGHTED_SUM_TOLERANCE) == our_scores[name], (
                    f"[Seed {seed}] Mismatch against pymcdm {PYMCDM_VERSION} WSM for {name}"
                )
