"""
Normalization engine for decision matrices using min-max, vector, z-score, and max-relative scaling.
Usage: from decision_maker.core.normalization import NormalizationEngine
Does NOT: Calculate multi-criteria algorithm rankings or handle file I/O operations.
"""

from __future__ import annotations

__all__ = ["NormalizationEngine", "NormalizationMethod"]

from enum import Enum

import numpy as np


class NormalizationMethod(Enum):
    MIN_MAX = "min_max"
    VECTOR = "vector"
    Z_SCORE = "z_score"
    MAX_RELATIVE = "max_relative"


class NormalizationEngine:
    """Provides modular normalization strategies for decision analysis matrices."""

    @staticmethod
    def normalize_array(
        values: list[float] | np.ndarray,
        method: NormalizationMethod = NormalizationMethod.MIN_MAX,
        maximize: bool = True,
        epsilon: float = 1e-9,
    ) -> np.ndarray:
        """Normalize a 1D numeric array according to the specified strategy."""
        arr = np.asarray(values, dtype=float)
        if len(arr) == 0:
            return arr

        if method == NormalizationMethod.MIN_MAX:
            min_val, max_val = np.min(arr), np.max(arr)
            denom = (max_val - min_val) + epsilon
            normed = (arr - min_val) / denom if maximize else (max_val - arr) / denom
        elif method == NormalizationMethod.VECTOR:
            norm = np.sqrt(np.sum(arr**2)) + epsilon
            normed = arr / norm
            if not maximize:
                normed = 1.0 - normed
        elif method == NormalizationMethod.Z_SCORE:
            mean_val = np.mean(arr)
            std_val = np.std(arr) + epsilon
            normed = (arr - mean_val) / std_val
            if not maximize:
                normed = -normed
        elif method == NormalizationMethod.MAX_RELATIVE:
            max_val = np.max(np.abs(arr)) + epsilon
            normed = arr / max_val if maximize else (max_val - arr) / max_val
        else:
            normed = arr

        return (
            np.clip(normed, 0.0, 1.0)
            if method in (NormalizationMethod.MIN_MAX, NormalizationMethod.MAX_RELATIVE)
            else normed
        )

    @staticmethod
    def normalize_matrix(
        matrix: dict[str, dict[str, float]],
        maximize_map: dict[str, bool],
        method: NormalizationMethod = NormalizationMethod.MIN_MAX,
    ) -> dict[str, dict[str, float]]:
        """Normalize a nested decision matrix {option_name: {factor_name: value}}."""
        if not matrix:
            return {}

        options = list(matrix.keys())
        factors = list(next(iter(matrix.values())).keys())

        result: dict[str, dict[str, float]] = {opt: {} for opt in options}

        for factor in factors:
            raw_vals = [matrix[opt].get(factor, 0.0) for opt in options]
            maximize = maximize_map.get(factor, True)
            normed_vals = NormalizationEngine.normalize_array(raw_vals, method=method, maximize=maximize)
            for opt, normed in zip(options, normed_vals, strict=False):
                result[opt][factor] = float(normed)

        return result
