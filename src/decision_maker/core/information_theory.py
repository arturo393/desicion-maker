"""
Information theory engine computing mutual information and entropy across factors and options.
Usage: from decision_maker.core.information_theory import InformationTheoryEngine
Does NOT: Solve linear programming or TOPSIS ideal-solution distances.
"""

from __future__ import annotations

__all__ = ["InformationTheoryEngine"]

import logging
from typing import Dict, List

import numpy as np
from sklearn.feature_selection import mutual_info_regression

from decision_maker.core.models import Factor, Statistics

logger = logging.getLogger(__name__)


class InformationTheoryEngine:
    """
    Engine that applies Information Theory to decision analysis.
    Specifically uses Mutual Information to quantify non-linear dependencies.
    """

    def analyze(self, mc_results: Dict[str, Statistics], factors: List[Factor]) -> Dict[str, Dict[str, float]]:
        """
        Calculates Mutual Information (MI) between each input factor and the resulting total score.
        This captures non-linear relationships that standard correlation ignores.

        Returns:
            Dict mapping option names to a dict of {factor_name: importance_score}
            where importance_score is normalized MI.
        """
        results = {}
        factor_names = [f.name for f in factors]

        for name, stats in mc_results.items():
            if stats.raw_scores is None or stats.raw_factor_data is None:
                logger.warning(f"Option '{name}' has no raw data. Skipping Information Theory analysis.")
                continue

            # Prepare target y (total scores) and features X (factor samples)
            y = stats.raw_scores
            available_factors = [fn for fn in factor_names if fn in stats.raw_factor_data]

            if not available_factors:
                continue

            # Matrix of shape (n_samples, n_features)
            X = np.stack([stats.raw_factor_data[fn] for fn in available_factors], axis=1)

            try:
                # Calculate Mutual Information
                # discrete_features=False because samples are continuous distributions
                mi_scores = mutual_info_regression(X, y, discrete_features=False, random_state=42)

                # Normalize scores to provide "Relative Importance"
                total_mi = np.sum(mi_scores)
                if total_mi > 0:
                    normalized_mi = mi_scores / total_mi
                else:
                    normalized_mi = mi_scores

                results[name] = {fn: float(val) for fn, val in zip(available_factors, normalized_mi)}
            except ValueError as e:
                logger.error(f"Error calculating Mutual Information for '{name}': {e}")
                continue

        return results
