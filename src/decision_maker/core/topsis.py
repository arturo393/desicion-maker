"""
[What it does] TOPSIS multi-criteria decision making algorithm.
[How to use it] Instantiate TOPSISEngine and call analyze(data, weights, maximize_flags).
[What it DOESN'T do] Does not handle missing values automatically.
"""

from __future__ import annotations

__all__ = ["TOPSISEngine"]

import logging
import math

import pandas as pd

logger = logging.getLogger(__name__)


DEFAULT_NORMALIZATION_DIVISOR: float = 1.0


class TOPSISEngine:
    def analyze(
        self,
        decision_matrix_fuzzy: dict[str, dict[str, tuple[float, float, float]]],
        weights: list[float],
        maximize: list[bool],
    ) -> pd.Series:
        if not decision_matrix_fuzzy:
            return pd.Series()

        first_opt_factors = list(decision_matrix_fuzzy.values())[0]
        factor_names = list(first_opt_factors.keys())

        # Weights and maximize flags must match factor dimensionality exactly.
        # Truncating or ignoring length mismatches masks caller configuration bugs.
        if len(weights) != len(factor_names):
            raise ValueError(
                f"Weights count ({len(weights)}) does not match factor count ({len(factor_names)})."
            )
        if len(maximize) != len(factor_names):
            raise ValueError(
                f"Maximize count ({len(maximize)}) does not match factor count ({len(factor_names)})."
            )

        if len(decision_matrix_fuzzy) == 1:
            opt_name = next(iter(decision_matrix_fuzzy))
            return pd.Series({opt_name: 1.0})

        norm_matrix: dict[str, dict[str, tuple[float, float, float]]] = {}
        for factor_idx, factor in enumerate(factor_names):
            is_max = maximize[factor_idx]

            max_c = max(decision_matrix_fuzzy[opt][factor][2] for opt in decision_matrix_fuzzy)
            min_a = min(decision_matrix_fuzzy[opt][factor][0] for opt in decision_matrix_fuzzy)
            divisor = (max_c - min_a) if max_c != min_a else DEFAULT_NORMALIZATION_DIVISOR

            for opt in decision_matrix_fuzzy:
                if opt not in norm_matrix:
                    norm_matrix[opt] = {}
                a, b, c = decision_matrix_fuzzy[opt][factor]

                if is_max:
                    # Linear min-max normalization for benefit criteria: (x - min_a) / (max_c - min_a).
                    # Consistent with cost criteria and invariant to translation, preventing rank inversion
                    # when all factor values are negative.
                    norm_matrix[opt][factor] = (
                        (a - min_a) / divisor,
                        (b - min_a) / divisor,
                        (c - min_a) / divisor,
                    )
                else:
                    # Linear min-max normalization for cost criteria: (max_c - x) / (max_c - min_a).
                    norm_matrix[opt][factor] = (
                        (max_c - c) / divisor,
                        (max_c - b) / divisor,
                        (max_c - a) / divisor,
                    )


        weighted_matrix: dict[str, dict[str, tuple[float, float, float]]] = {}
        for opt in norm_matrix:
            weighted_matrix[opt] = {}
            for i, factor in enumerate(factor_names):
                w = weights[i]
                a, b, c = norm_matrix[opt][factor]
                weighted_matrix[opt][factor] = (a * w, b * w, c * w)

        fpis = {}
        fnis = {}
        for factor in factor_names:
            fpis[factor] = (
                max(weighted_matrix[opt][factor][0] for opt in weighted_matrix),
                max(weighted_matrix[opt][factor][1] for opt in weighted_matrix),
                max(weighted_matrix[opt][factor][2] for opt in weighted_matrix),
            )
            fnis[factor] = (
                min(weighted_matrix[opt][factor][0] for opt in weighted_matrix),
                min(weighted_matrix[opt][factor][1] for opt in weighted_matrix),
                min(weighted_matrix[opt][factor][2] for opt in weighted_matrix),
            )

        def fuzzy_distance(fn1, fn2):
            return math.sqrt(((fn1[0] - fn2[0]) ** 2 + (fn1[1] - fn2[1]) ** 2 + (fn1[2] - fn2[2]) ** 2) / 3.0)

        scores = {}
        for opt in weighted_matrix:
            d_plus = sum(fuzzy_distance(weighted_matrix[opt][factor], fpis[factor]) for factor in factor_names)
            d_minus = sum(fuzzy_distance(weighted_matrix[opt][factor], fnis[factor]) for factor in factor_names)
            scores[opt] = 0.0 if (d_plus + d_minus) == 0 else d_minus / (d_plus + d_minus)

        return pd.Series(scores).sort_values(ascending=False)
