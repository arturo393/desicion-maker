from __future__ import annotations

__all__ = ["TOPSISEngine"]

import math
import logging
from typing import Dict, List, Tuple

import pandas as pd

logger = logging.getLogger(__name__)


class TOPSISEngine:
    def analyze(
        self,
        decision_matrix_fuzzy: Dict[str, Dict[str, Tuple[float, float, float]]],
        weights: List[float],
        maximize: List[bool],
    ) -> pd.Series:
        if not decision_matrix_fuzzy:
            return pd.Series()

        if len(decision_matrix_fuzzy) == 1:
            opt_name = next(iter(decision_matrix_fuzzy))
            return pd.Series({opt_name: 1.0})

        first_opt_factors = list(decision_matrix_fuzzy.values())[0]
        factor_names = list(first_opt_factors.keys())

        if len(weights) != len(factor_names):
            logger.warning(
                f"Weights count ({len(weights)}) != factor count ({len(factor_names)}). Truncating."
            )
            weights = weights[:len(factor_names)]
        if len(maximize) != len(factor_names):
            logger.warning(
                f"Maximize count ({len(maximize)}) != factor count ({len(factor_names)}). Truncating."
            )
            maximize = maximize[:len(factor_names)]

        norm_matrix: Dict[str, Dict[str, Tuple[float, float, float]]] = {}
        for factor_idx, factor in enumerate(factor_names):
            is_max = maximize[factor_idx]

            max_c = max(decision_matrix_fuzzy[opt][factor][2] for opt in decision_matrix_fuzzy)
            min_a = min(decision_matrix_fuzzy[opt][factor][0] for opt in decision_matrix_fuzzy)

            for opt in decision_matrix_fuzzy:
                if opt not in norm_matrix:
                    norm_matrix[opt] = {}
                a, b, c = decision_matrix_fuzzy[opt][factor]

                if is_max:
                    div = max_c if max_c != 0 else 1.0
                    norm_matrix[opt][factor] = (a / div, b / div, c / div)
                else:
                    a_div = c if c != 0 else 1.0
                    b_div = b if b != 0 else 1.0
                    c_div = a if a != 0 else 1.0
                    norm_matrix[opt][factor] = (min_a / a_div, min_a / b_div, min_a / c_div)

        weighted_matrix: Dict[str, Dict[str, Tuple[float, float, float]]] = {}
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
            return math.sqrt(
                ((fn1[0] - fn2[0]) ** 2 + (fn1[1] - fn2[1]) ** 2 + (fn1[2] - fn2[2]) ** 2) / 3.0
            )

        scores = {}
        for opt in weighted_matrix:
            d_plus = sum(fuzzy_distance(weighted_matrix[opt][factor], fpis[factor]) for factor in factor_names)
            d_minus = sum(fuzzy_distance(weighted_matrix[opt][factor], fnis[factor]) for factor in factor_names)
            scores[opt] = 0.0 if (d_plus + d_minus) == 0 else d_minus / (d_plus + d_minus)

        return pd.Series(scores).sort_values(ascending=False)
