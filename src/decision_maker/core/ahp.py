"""
Analytic Hierarchy Process (AHP) engine for pairwise comparison and consistency calculation.
Usage: from decision_maker.core.ahp import AHPEngine
Does NOT: Handle non-pairwise multi-criteria decision algorithms like TOPSIS or PROMETHEE.
"""

from __future__ import annotations

__all__ = ["AHPHelper"]

from typing import Optional

import numpy as np


class AHPHelper:
    RI_TABLE = {1: 0, 2: 0, 3: 0.58, 4: 0.9, 5: 1.12, 6: 1.24, 7: 1.32, 8: 1.41, 9: 1.45}

    @staticmethod
    def calculate_weights(matrix: np.ndarray, labels: list[str]) -> dict[str, float | None]:
        try:
            n = len(labels)
            if n != matrix.shape[0] or n != matrix.shape[1]:
                return {
                    "error": f"Label count ({n}) does not match matrix dimensions ({matrix.shape[0]}x{matrix.shape[1]})"
                }
            if np.any(matrix <= 0):
                return {"error": "Pairwise matrix contains zero or negative values; AHP requires positive values"}
            if np.any(np.isnan(matrix)) or np.any(np.isinf(matrix)):
                return {"error": "Pairwise matrix contains NaN or Inf values"}
            if n > 1:
                reciprocal_check = np.abs(matrix * matrix.T - np.ones((n, n)))
                np.fill_diagonal(reciprocal_check, 0)
                if np.any(reciprocal_check > 0.01):
                    i, j = np.unravel_index(np.argmax(reciprocal_check), reciprocal_check.shape)
                    expected = 1.0 / matrix[i, j]
                    return {
                        "error": (
                            f"Matrix is not reciprocal: a[{labels[i]}][{labels[j]}]={matrix[i, j]:.4f} "
                            f"but a[{labels[j]}][{labels[i]}]={matrix[j, i]:.4f} "
                            f"(expected {expected:.4f}). "
                            f"AHP requires a_ij = 1/a_ji for all i,j."
                        )
                    }
            col_sums = matrix.sum(axis=0)
            norm_matrix = matrix / col_sums
            weights = norm_matrix.mean(axis=1)

            weighted_sum_vec = matrix.dot(weights)
            lambda_max = (weighted_sum_vec / weights).mean()

            ci = (lambda_max - n) / (n - 1) if n > 1 else 0
            ri = AHPHelper.RI_TABLE.get(n, 1.49)
            cr = ci / ri if ri != 0 else 0

            result: dict[str, Optional] = {
                "weights": dict(zip(labels, weights, strict=False)),
                "consistency_ratio": float(cr),
                "is_consistent": cr <= 0.1,
                "correction_advice": None,
            }

            if cr > 0.1 and n > 2:
                expected_matrix = np.outer(weights, 1.0 / weights)
                deviation = np.abs(matrix - expected_matrix)
                np.fill_diagonal(deviation, 0)
                i, j = np.unravel_index(np.argmax(deviation, axis=None), deviation.shape)

                if matrix[i, j] > expected_matrix[i, j]:
                    advice = (
                        f"Warning: The importance of '{labels[i]}' over '{labels[j]}' "
                        f"(currently {matrix[i, j]:.1f}) is too high. "
                        f"Consider lowering it towards {expected_matrix[i, j]:.1f}."
                    )
                else:
                    advice = (
                        f"Warning: The importance of '{labels[i]}' over '{labels[j]}' "
                        f"(currently {matrix[i, j]:.1f}) is too low. "
                        f"Consider raising it towards {expected_matrix[i, j]:.1f}."
                    )
                result["correction_advice"] = advice

            return result
        except (ValueError, np.linalg.LinAlgError) as e:
            return {"error": str(e)}
