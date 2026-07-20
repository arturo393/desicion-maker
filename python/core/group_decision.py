from __future__ import annotations

__all__ = ["GroupDecisionEngine"]

import logging
from typing import Any, Dict, List

import numpy as np

from python.core.models import Factor

logger = logging.getLogger(__name__)


class GroupDecisionEngine:
    """
    Multi-stakeholder decision aggregation.

    Collects weight sets from multiple stakeholders and finds
    consensus rankings using various aggregation methods.
    """

    @staticmethod
    def aggregate_weights(
        stakeholders: Dict[str, Dict[str, float]],
        method: str = "mean",
    ) -> Dict[str, Any]:
        """
        Aggregate multiple stakeholders' factor weights into consensus.

        Args:
            stakeholders: {name: {factor: weight}}
            method: "mean", "median", or "borda"

        Returns:
            {consensus_weights, method, stakeholder_count, divergence,
             per_stakeholder_rankings, kendall_w}
        """
        if not stakeholders:
            return {"error": "No stakeholders provided"}

        names = list(stakeholders.keys())
        factor_names = list(next(iter(stakeholders.values())).keys())

        # Build weight matrix
        n_stakeholders = len(names)
        n_factors = len(factor_names)
        matrix = np.zeros((n_stakeholders, n_factors))

        for i, s in enumerate(names):
            for j, f in enumerate(factor_names):
                matrix[i, j] = stakeholders[s].get(f, 0.0)

        # Row-normalize so each stakeholder's weights sum to 1
        row_sums = matrix.sum(axis=1, keepdims=True)
        row_sums = np.where(row_sums == 0, 1, row_sums)
        matrix = matrix / row_sums

        if method == "median":
            consensus = np.median(matrix, axis=0)
        elif method == "borda":
            from scipy.stats import rankdata
            ranks = np.apply_along_axis(lambda row: rankdata(-row, method='average'), 1, matrix)
            avg_rank = np.mean(ranks, axis=0)
            borda_points = n_factors - avg_rank
            consensus = borda_points / borda_points.sum()
        else:
            consensus = np.mean(matrix, axis=0)

        consensus = consensus / consensus.sum()

        # Per-stakeholder rankings
        per_stakeholder = {}
        for i, s in enumerate(names):
            ranked = sorted(
                zip(factor_names, matrix[i].tolist()),
                key=lambda x: x[1],
                reverse=True,
            )
            per_stakeholder[s] = {
                "weights": dict(zip(factor_names, matrix[i].tolist())),
                "ranking": [r[0] for r in ranked],
            }

        # Kendall's W (coefficient of concordance)
        kendall_w = GroupDecisionEngine._kendall_w(matrix)

        # Divergence: mean pairwise distance between stakeholders
        divergences = []
        for i in range(n_stakeholders):
            for j in range(i + 1, n_stakeholders):
                dist = float(np.sum(np.abs(matrix[i] - matrix[j])))
                divergences.append(dist)
        mean_divergence = float(np.mean(divergences)) if divergences else 0.0

        return {
            "consensus_weights": dict(zip(factor_names, consensus.tolist())),
            "method": method,
            "stakeholder_count": n_stakeholders,
            "stakeholders": per_stakeholder,
            "kendall_w": float(kendall_w),
            "consensus_level": (
                "high" if kendall_w > 0.7
                else "moderate" if kendall_w > 0.4
                else "low"
            ),
            "mean_divergence": mean_divergence,
        }

    @staticmethod
    def _kendall_w(matrix: np.ndarray) -> float:
        """Kendall's W (coefficient of concordance) for ranks."""
        from scipy.stats import rankdata
        n_stakeholders, n_factors = matrix.shape
        if n_stakeholders < 2 or n_factors < 2:
            return 1.0
        ranks = np.apply_along_axis(lambda row: rankdata(-row, method='average'), 1, matrix)
        # Sum of ranks per factor
        R = np.sum(ranks, axis=0)
        # Mean of R
        R_mean = np.mean(R)
        # Sum of squared deviations
        S = np.sum((R - R_mean) ** 2)
        # Kendall's W
        max_S = (n_stakeholders ** 2 * (n_factors ** 3 - n_factors)) / 12.0
        if max_S == 0:
            return 1.0
        return float(S / max_S)

    @staticmethod
    def aggregate_scores(
        stakeholders: Dict[str, Dict[str, float]],
        factors: List[Factor],
        method: str = "mean",
    ) -> Dict[str, Any]:
        """
        Convenience: aggregate weights and compute factor objects.
        """
        result = GroupDecisionEngine.aggregate_weights(stakeholders, method)
        if "error" in result:
            return result
        consensus = result["consensus_weights"]
        result["factors"] = [
            Factor(name=f.name, weight=consensus.get(f.name, f.weight),
                   maximize=f.maximize, category=f.category)
            for f in factors
        ]
        return result
