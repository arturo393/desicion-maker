"""
Tests validating decision engines against published literature and independent calculations.

Strict validation rules:
1. Every test cites its exact source (author, year, book/journal, page/table).
2. If an expected value is independently calculated rather than directly cited from a table,
   the docstring explicitly states that it is an independent step-by-step calculation.
3. Engines with methodological differences (e.g. min-max L1 normalization vs vector L2 TOPSIS)
   are evaluated against literature rankings and marked with pytest.mark.xfail(strict=True)
   when differences in the mathematical formulation produce differing results.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from decision_maker.core.ahp import AHPHelper
from decision_maker.core.promethee import PrometheeConfig, PrometheeEngine
from decision_maker.core.topsis import TOPSISEngine

# Named constants to avoid magic numbers (per AGENTS.md conventions)
SAATY_WEIGHT_TOLERANCE: float = 0.01
SAATY_CR_TOLERANCE: float = 0.001
SAATY_RANDOM_INDEX_3: float = 0.58
CR_CONSISTENCY_THRESHOLD: float = 0.10
FLOW_TOLERANCE: float = 1e-5


class TestPublishedExamples:
    def test_ahp_weights_match_the_principal_eigenvector(self) -> None:
        """AHP weights and CR against Saaty's definition, computed independently in the test.

        INDEPENDENT CALCULATION, not a published table. The first version of this test cited
        "Saaty (1990), Table 1" for this matrix and its values; that citation could not be
        verified, so the reference is now Saaty's definition itself: the priority vector is the
        principal eigenvector of the pairwise matrix, CI = (lambda_max - n) / (n - 1), CR = CI / RI
        with Saaty's random index RI(3) = 0.58.

        The engine uses the column-normalised row-mean approximation, not the eigenvector, so the
        weights agree to ~0.004 here, not exactly. The tolerance says that, and no more.
        """
        pairwise_matrix = np.array(
            [
                [1.0, 3.0, 5.0],
                [1.0 / 3.0, 1.0, 3.0],
                [1.0 / 5.0, 1.0 / 3.0, 1.0],
            ]
        )
        labels = ["Size", "Cost", "Location"]
        n = len(labels)

        eigenvalues, eigenvectors = np.linalg.eig(pairwise_matrix)
        principal = int(np.argmax(eigenvalues.real))
        expected = np.abs(eigenvectors[:, principal].real)
        expected /= expected.sum()
        lambda_max = float(eigenvalues.real[principal])
        expected_cr = (lambda_max - n) / (n - 1) / SAATY_RANDOM_INDEX_3

        result = AHPHelper.calculate_weights(pairwise_matrix, labels)

        assert "error" not in result, f"AHP calculation failed with error: {result.get('error')}"
        assert bool(result["is_consistent"]) is True
        assert result["consistency_ratio"] <= CR_CONSISTENCY_THRESHOLD
        assert pytest.approx(expected_cr, abs=SAATY_CR_TOLERANCE) == result["consistency_ratio"]
        for label, w in zip(labels, expected, strict=True):
            assert pytest.approx(float(w), abs=SAATY_WEIGHT_TOLERANCE) == result["weights"][label]

    @pytest.mark.xfail(
        strict=True,
        reason=(
            "TOPSISEngine is Chen-style fuzzy TOPSIS: it SUMS per-criterion vertex distances. On crisp "
            "input that collapses to a weighted sum of min-max scores (see "
            "test_crisp_topsis_is_a_min_max_weighted_sum), and on this data it ranks A3 > A1 > A4 > A2, "
            "while classic TOPSIS (vector normalisation, Euclidean distance) ranks A1 > A3 > A4 > A2."
        ),
    )
    def test_topsis_ranks_like_classic_topsis_on_the_fighter_aircraft_data(self) -> None:
        """Fighter-aircraft selection data, ranked by classic TOPSIS computed independently in the test.

        Data: the fighter-aircraft example widely reproduced from Hwang & Yoon (1981), "Multiple
        Attribute Decision Making", Springer LNEMS 186: 4 aircraft, 6 criteria, cost is the only
        cost criterion, qualitative ratings on the 1-9 scale.

        INDEPENDENT CALCULATION. The first version of this test asserted a "published ranking"
        A2 > A3 > A4 > A1 with closeness values attributed to p. 101; computing classic TOPSIS on the
        same data gives A1 (0.643) > A3 (0.614) > A4 (0.312) > A2 (0.268), so that "published" result
        was not what the method produces and was removed. Nothing here is quoted from the book.
        """
        names = ["A1", "A2", "A3", "A4"]
        criteria = ["Speed", "Range", "Payload", "Cost", "Reliability", "Maneuverability"]
        x = np.array(
            [
                [2.0, 1500.0, 20000.0, 5.5, 5.0, 9.0],
                [2.5, 2700.0, 18000.0, 6.5, 3.0, 5.0],
                [1.8, 2000.0, 21000.0, 4.5, 7.0, 7.0],
                [2.2, 1800.0, 20000.0, 5.0, 5.0, 5.0],
            ]
        )
        weights = [0.2, 0.1, 0.1, 0.1, 0.2, 0.3]
        maximize = [True, True, True, False, True, True]

        # Classic TOPSIS, written out: vector normalisation, weighting, Euclidean distances.
        w, mx = np.array(weights), np.array(maximize)
        v = x / np.sqrt((x**2).sum(axis=0)) * w
        ideal = np.where(mx, v.max(axis=0), v.min(axis=0))
        anti = np.where(mx, v.min(axis=0), v.max(axis=0))
        d_plus = np.sqrt(((v - ideal) ** 2).sum(axis=1))
        d_minus = np.sqrt(((v - anti) ** 2).sum(axis=1))
        closeness = d_minus / (d_plus + d_minus)
        classic_ranking = [names[i] for i in np.argsort(-closeness)]
        assert classic_ranking == ["A1", "A3", "A4", "A2"], "the independent calculation itself changed"

        matrix = {
            name: {c: (float(x[i, j]),) * 3 for j, c in enumerate(criteria)} for i, name in enumerate(names)
        }
        ranking = TOPSISEngine().analyze(matrix, weights, maximize).index.tolist()
        assert ranking == classic_ranking

    def test_crisp_topsis_is_a_min_max_weighted_sum(self) -> None:
        """Pins what the engine actually computes on crisp input, so a change of method is a decision.

        With a = b = c, min-max normalisation puts each criterion's best option at w_j and its worst
        at 0, so the summed distances satisfy d+ + d- = sum(w) and the closeness d- / (d+ + d-) is the
        weighted sum of min-max scores. INDEPENDENT CALCULATION of that weighted sum below.
        """
        x = np.array([[2.0, 1500.0, 5.5], [2.5, 2700.0, 6.5], [1.8, 2000.0, 4.5], [2.2, 1800.0, 5.0]])
        weights, maximize = [0.5, 0.2, 0.3], [True, True, False]
        lo, hi = x.min(axis=0), x.max(axis=0)
        norm = np.where(maximize, (x - lo) / (hi - lo), (hi - x) / (hi - lo))
        expected = norm @ np.array(weights)

        matrix = {f"A{i}": {f"c{j}": (float(x[i, j]),) * 3 for j in range(3)} for i in range(4)}
        scores = TOPSISEngine().analyze(matrix, weights, maximize)
        for i in range(4):
            assert pytest.approx(float(expected[i]), abs=FLOW_TOLERANCE) == scores[f"A{i}"]

    def test_promethee_ii_brans_vincke_1985(self) -> None:
        """
        Validate PROMETHEE II engine against an independent step-by-step calculation
        following the axiomatic formulas of Brans & Vincke (1985).

        Source for method:
            Brans, J. P., & Vincke, P. (1985). "A Preference Ranking Organisation METHod:
            The PROMETHEE Method for Multiple Criteria Decision-Making".
            Management Science, Vol. 31, No. 6, pp. 647-656.

        Calculation type:
            INDEPENDENT CALCULATION (explicit hand derivation, not a published table).

        Problem formulation:
            3 actions {A, B, C} evaluated on 2 benefit criteria {C1, C2}.
            Weights: w1 = 0.6, w2 = 0.4.
            Preference functions: Usual criterion (Type I): P(d) = 1 if d > 0, 0 otherwise.

        Evaluations:
            A: C1 = 10.0, C2 = 2.0
            B: C1 = 8.0,  C2 = 5.0
            C: C1 = 5.0,  C2 = 1.0

        Step-by-step pairwise preference index pi(a, b) = sum(w_j * P_j(f_j(a) - f_j(b))):
            - pi(A, B) = 0.6 * P(10-8) + 0.4 * P(2-5) = 0.6 * 1 + 0.4 * 0 = 0.6
            - pi(B, A) = 0.6 * P(8-10) + 0.4 * P(5-2) = 0.6 * 0 + 0.4 * 1 = 0.4
            - pi(A, C) = 0.6 * P(10-5) + 0.4 * P(2-1) = 0.6 * 1 + 0.4 * 1 = 1.0
            - pi(C, A) = 0.6 * P(5-10) + 0.4 * P(1-2) = 0.6 * 0 + 0.4 * 0 = 0.0
            - pi(B, C) = 0.6 * P(8-5)  + 0.4 * P(5-1) = 0.6 * 1 + 0.4 * 1 = 1.0
            - pi(C, B) = 0.6 * P(5-8)  + 0.4 * P(1-5) = 0.6 * 0 + 0.4 * 0 = 0.0

        Outranking flows (n = 3, divisor = n - 1 = 2):
            Positive flow phi+(a) = 1/(n-1) * sum_{b != a} pi(a, b):
                phi+(A) = (0.6 + 1.0) / 2 = 0.8
                phi+(B) = (0.4 + 1.0) / 2 = 0.7
                phi+(C) = (0.0 + 0.0) / 2 = 0.0

            Negative flow phi-(a) = 1/(n-1) * sum_{b != a} pi(b, a):
                phi-(A) = (0.4 + 0.0) / 2 = 0.2
                phi-(B) = (0.6 + 0.0) / 2 = 0.3
                phi-(C) = (1.0 + 1.0) / 2 = 1.0

            Net flow phi(a) = phi+(a) - phi-(a):
                phi(A) = 0.8 - 0.2 = +0.6
                phi(B) = 0.7 - 0.3 = +0.4
                phi(C) = 0.0 - 1.0 = -1.0

        Ranking:
            A (+0.6) > B (+0.4) > C (-1.0).
        """
        df = pd.DataFrame(
            [
                {"C1": 10.0, "C2": 2.0},
                {"C1": 8.0, "C2": 5.0},
                {"C1": 5.0, "C2": 1.0},
            ],
            index=["A", "B", "C"],
        )
        config = PrometheeConfig(
            weights=[0.6, 0.4],
            maximize=[True, True],
            pref_types=["usual", "usual"],
        )

        engine = PrometheeEngine()
        net_flows = engine.analyze(df, config)

        # Expected values from independent hand calculation
        expected_phi = {"A": 0.6, "B": 0.4, "C": -1.0}

        for action, expected_val in expected_phi.items():
            assert pytest.approx(expected_val, abs=FLOW_TOLERANCE) == net_flows[action], (
                f"Net flow for {action}: expected {expected_val}, got {net_flows[action]}"
            )

        assert net_flows.index.tolist() == ["A", "B", "C"], (
            f"Expected ranking ['A', 'B', 'C'], got {net_flows.index.tolist()}"
        )

    @pytest.mark.xfail(
        strict=True,
        reason=(
            "Methodological divergence (SAW collapse): TOPSISEngine computes distances "
            "as an L1 sum across criteria (sum(fuzzy_distance(...))) rather than a Euclidean "
            "L2 norm (sqrt(sum d_j^2)). On normalized crisp matrices, d+ + d- = sum(w_j) = 1.0, "
            "which causes the relative closeness C_i = d- / (d+ + d-) to mathematically collapse "
            "to Simple Additive Weighting: C_i = sum(w_j * x_ij). Consequently, TOPSISEngine "
            "ranks Specialist A (0.625) over Balanced B (0.600), whereas classic Euclidean TOPSIS "
            "ranks Balanced B (0.599) over Specialist A (0.579) due to quadratic penalization of extremes."
        ),
    )
    def test_distinguish_topsis_from_simple_additive_weighting(self) -> None:
        """
        Validate that TOPSIS distinguishes itself from Simple Additive Weighting (SAW).

        Theoretical Background:
            SAW uses a linear additive value function V(x) = sum(w_j * x_j), implying a constant
            marginal rate of substitution between criteria.
            Classic Euclidean TOPSIS measures the Euclidean L2 distance to the ideal point
            d+ = sqrt(sum w_j^2 (x_j - x*)^2) and anti-ideal point d-.
            Because Euclidean distance is strictly convex (L2 norm), it penalizes alternatives
            with severe, unbalanced deficiencies much more heavily than SAW.

        Source for construction:
            Designed for this test; no literature value is claimed. INDEPENDENT CALCULATION.

        Construction:
            Two criteria C1, C2, both benefit, weights w = [0.5, 0.5].
            Anchor points establish global min=0.0 and max=1.0:
              - MinRef: (0.0, 0.0)
              - MaxRef: (1.0, 1.0)
            Two competing alternatives:
              - Specialist A: (1.0, 0.25) -> High on C1, but weak on C2
              - Balanced B:   (0.55, 0.65) -> Balanced across both criteria

        Theoretical Evaluations:
            1. Under Simple Additive Weighting (SAW):
               Score(A) = 0.5 * 1.00 + 0.5 * 0.25 = 0.625
               Score(B) = 0.5 * 0.55 + 0.5 * 0.65 = 0.600
               SAW ranking: Specialist A > Balanced B.

            2. Under Classic Euclidean TOPSIS (L2 norm):
               Ideal (0.50, 0.50), Anti-ideal (0.00, 0.00) in weighted space.
               - Option A: wA = (0.500, 0.125)
                 d+(A) = sqrt((0.500-0.500)^2 + (0.125-0.500)^2) = 0.3750
                 d-(A) = sqrt((0.500-0.000)^2 + (0.125-0.000)^2) = sqrt(0.265625) ≈ 0.5154
                 C(A)  = 0.5154 / (0.3750 + 0.5154) ≈ 0.5788

               - Option B: wB = (0.275, 0.325)
                 d+(B) = sqrt((0.275-0.500)^2 + (0.325-0.500)^2) = sqrt(0.050625 + 0.030625) ≈ 0.2850
                 d-(B) = sqrt((0.275-0.000)^2 + (0.325-0.000)^2) = sqrt(0.075625 + 0.105625) ≈ 0.4257
                 C(B)  = 0.4257 / (0.2850 + 0.4257) ≈ 0.5990

               Euclidean TOPSIS ranking: Balanced B (0.5990) > Specialist A (0.5788).

        Assertion:
            Classic TOPSIS must prefer Balanced B over Specialist A (B > A), contradicting SAW.
            If the engine implements an L1 sum across criteria, it collapses to SAW and fails this test.
        """
        # Data with anchors to ensure [0, 1] normalization span
        data = {
            "MinRef": {"C1": (0.0, 0.0, 0.0), "C2": (0.0, 0.0, 0.0)},
            "MaxRef": {"C1": (1.0, 1.0, 1.0), "C2": (1.0, 1.0, 1.0)},
            "Specialist_A": {"C1": (1.0, 1.0, 1.0), "C2": (0.25, 0.25, 0.25)},
            "Balanced_B": {"C1": (0.55, 0.55, 0.55), "C2": (0.65, 0.65, 0.65)},
        }
        weights = [0.5, 0.5]
        maximize = [True, True]

        engine = TOPSISEngine()
        results = engine.analyze(data, weights, maximize)

        score_a = results["Specialist_A"]
        score_b = results["Balanced_B"]

        # Classic Euclidean TOPSIS penalizes the severe deficiency of A on C2, preferring B over A.
        # Simple Additive Weighting (SAW) prefers A (0.625) over B (0.600).
        assert score_b > score_a, (
            f"Expected Balanced_B to score higher than Specialist_A under Euclidean TOPSIS "
            f"(B=0.5990 vs A=0.5788), but got Balanced_B={score_b:.4f} and Specialist_A={score_a:.4f}. "
            f"This indicates the engine collapsed to Simple Additive Weighting (SAW)."
        )
