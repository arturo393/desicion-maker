from __future__ import annotations

__all__ = ["RobustOptimizer"]

import logging
from typing import Any, Dict, List, Optional

import numpy as np

from python.core.models import Factor, Statistics

logger = logging.getLogger(__name__)


class RobustOptimizer:
    """
    Advanced Robustness Engine implementing Distributionally Robust Optimization (DRO)
    concepts and weight sensitivity analysis.
    """

    def analyze(
        self,
        mc_results: Dict[str, Statistics],
        factors: List[Factor],
        epsilon: float = 0.05,  # Wasserstein ambiguity radius
        weight_shock: float = 0.2,
    ) -> Dict[str, Any]:
        """
        Performs a dual robustness analysis:
        1. Weight Shock Sensitivity (Local)
        2. Distributionally Robust Expectation (Global/Stochastic)
        """
        if not mc_results or not factors:
            return {}

        results = {
            "robust_ranking": {},
            "dro_scores": {},
            "stability_metrics": {},
            "weight_sensitivity": {},
        }

        # 1. Weight Sensitivity Analysis (Local)
        # Identifies which factors are most likely to flip the decision
        for opt_name, stats in mc_results.items():
            f_stats = stats.factor_stats
            worst_score = stats.mean_score
            sensitive_factors = []

            for f in factors:
                if f.name not in f_stats:
                    continue

                # Apply positive and negative shocks to the weight
                for delta in [weight_shock, -weight_shock]:
                    new_weight = f.weight * (1 + delta)
                    # Recalculate mean score with modified weight
                    # Score = Sum(mean_i * weight_i)
                    diff = (new_weight - f.weight) * f_stats[f.name]["mean"]
                    if not f.maximize:
                        diff = -diff
                    
                    shocked_score = stats.mean_score + diff
                    if shocked_score < worst_score:
                        worst_score = shocked_score
                    
                    # If shock changes rank, log it (simplified logic here)
                    if abs(diff) > abs(stats.mean_score * 0.1): # 10% impact threshold
                        sensitive_factors.append({
                            "factor": f.name,
                            "impact": diff,
                            "shock": delta
                        })
            
            results["weight_sensitivity"][opt_name] = sensitive_factors

        # 2. Distributionally Robust Optimization (DRO) Analysis
        # Using a Wasserstein-based variance regularization approach
        # DRO_Value = E[Y] - sqrt(2 * epsilon * Var(Y))
        dro_ranking_list = []
        for opt_name, stats in mc_results.items():
            if stats.raw_scores is not None:
                samples = stats.raw_scores
                mean = np.mean(samples)
                variance = np.var(samples)
                
                # The DRO score represents the worst-case mean within a 
                # Wasserstein ball of radius epsilon around the empirical distribution.
                dro_score = mean - np.sqrt(2 * epsilon * variance)
                
                # Confidence interval width penalty
                stability = 1.0 - (np.sqrt(variance) / (abs(mean) + 1e-9))
            else:
                # Fallback if raw data is missing
                dro_score = stats.mean_score - (stats.std_dev * epsilon * 2)
                stability = 1.0 - (stats.std_dev / (abs(stats.mean_score) + 1e-9))

            results["dro_scores"][opt_name] = float(dro_score)
            results["stability_metrics"][opt_name] = float(np.clip(stability, 0, 1))
            dro_ranking_list.append((opt_name, float(dro_score)))

        # Sort results by DRO score (The "True" Robust Winner)
        dro_ranking_list.sort(key=lambda x: x[1], reverse=True)
        results["robust_ranking"] = dict(dro_ranking_list)
        results["winner"] = dro_ranking_list[0][0] if dro_ranking_list else None

        return results
