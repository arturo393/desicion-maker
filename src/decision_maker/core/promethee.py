"""
[What it does] PROMETHEE II engine for outranking and preference flows.
[How to use it] Instantiate PrometheeEngine, call analyze() with criteria preferences.
[What it DOESN'T do] Does not natively handle fuzzy stochastic logic.
"""

from __future__ import annotations

__all__ = ["PrometheeEngine"]

from collections.abc import Callable

import numpy as np
import pandas as pd


class PrometheeEngine:
    PREFERENCE_TYPES = {"usual", "ushape", "vshape", "level", "linear", "gaussian"}

    @staticmethod
    def _build_pref_func(pref_type: str, q: float = 0.0, p: float = 1.0, s: float = 1.0) -> Callable[[float], float]:
        if pref_type == "usual":
            return lambda d: 1.0 if d > 0 else 0.0
        elif pref_type == "ushape":
            return lambda d: 0.0 if d <= q else 1.0
        elif pref_type == "vshape":
            return lambda d: 0.0 if d <= 0 else (1.0 if d >= p else d / p)
        elif pref_type == "level":
            return lambda d: 0.0 if d <= q else (0.5 if d <= p else 1.0)
        elif pref_type == "linear":
            return lambda d: 0.0 if d <= q else (1.0 if d >= p else (d - q) / (p - q))
        elif pref_type == "gaussian":
            return lambda d: 0.0 if d <= 0 else 1.0 - np.exp(-(d**2) / (2 * s**2))
        else:
            return lambda d: 1.0 if d > 0 else 0.0

    def analyze(
        self,
        decision_matrix: pd.DataFrame,
        weights: list[float],
        maximize: list[bool],
        pref_types: list[str] | None = None,
        pref_params: list[dict] | None = None,
    ) -> pd.Series:
        if decision_matrix.empty:
            return pd.Series()

        options = decision_matrix.index.tolist()
        n_options = len(options)
        n_factors = len(decision_matrix.columns)

        if pref_types is None:
            pref_types = ["usual"] * n_factors
        if pref_params is None:
            pref_params = [{} for _ in range(n_factors)]

        pref_funcs = [PrometheeEngine._build_pref_func(pt, **pp) for pt, pp in zip(pref_types, pref_params, strict=False)]

        pi_matrix = np.zeros((n_options, n_options))

        for i, opt_a in enumerate(options):
            for j, opt_b in enumerate(options):
                if i == j:
                    continue
                sum_pref = 0.0
                for col_idx, col in enumerate(decision_matrix.columns):
                    is_max = maximize[col_idx]
                    val_a = decision_matrix.loc[opt_a, col]
                    val_b = decision_matrix.loc[opt_b, col]
                    diff = val_a - val_b if is_max else val_b - val_a
                    sum_pref += weights[col_idx] * pref_funcs[col_idx](diff)
                pi_matrix[i, j] = sum_pref

        if n_options <= 1:
            return pd.Series([0.0], index=options)

        phi_plus = pi_matrix.sum(axis=1) / (n_options - 1)
        phi_minus = pi_matrix.sum(axis=0) / (n_options - 1)
        phi_net = phi_plus - phi_minus

        return pd.Series(phi_net, index=options).sort_values(ascending=False)
