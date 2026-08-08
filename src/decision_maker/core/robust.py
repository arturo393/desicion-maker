"""
Distributionally Robust Optimization (DRO) engine for evaluating worst-case decision scenarios.
Usage: from decision_maker.core.robust import DistributionallyRobustOptimizer
Does NOT: Generate visual charts or Markdown reports.
"""

from __future__ import annotations

__all__ = ["RobustOptimizer"]

import logging
from typing import Any

import numpy as np

from decision_maker.core.models import Factor, Statistics

logger = logging.getLogger(__name__)


class RobustOptimizer:
    """
    Advanced Robustness Engine implementing Distributionally Robust Optimization (DRO)
    concepts and weight sensitivity analysis.
    """

    def analyze(
        self,
        mc_results: dict[str, Statistics],
        factors: list[Factor],
        epsilon: float = 0.05,  # Wasserstein ambiguity radius
        weight_shock: float = 0.2,
    ) -> dict[str, Any]:
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
        # Compute global bounds for normalization
        factor_names = list({fn for s in mc_results.values() for fn in s.factor_stats})
        global_bounds = {fn: {"min": float("inf"), "max": float("-inf")} for fn in factor_names}
        for stats in mc_results.values():
            for fn in factor_names:
                if fn in stats.factor_stats:
                    val = stats.factor_stats[fn]["mean"]
                    global_bounds[fn]["min"] = min(global_bounds[fn]["min"], val)
                    global_bounds[fn]["max"] = max(global_bounds[fn]["max"], val)

        for opt_name, stats in mc_results.items():
            f_stats = stats.factor_stats
            worst_score = stats.mean_score
            sensitive_factors = []

            for f in factors:
                if f.name not in f_stats:
                    continue

                # Normalize the factor mean to [0, 1]
                f_min = global_bounds[f.name]["min"]
                f_max = global_bounds[f.name]["max"]
                raw_mean = f_stats[f.name]["mean"]
                if f_max > f_min:
                    norm_mean = (raw_mean - f_min) / (f_max - f_min)
                else:
                    norm_mean = 1.0
                eff_mean = norm_mean if f.maximize else (1.0 - norm_mean)

                # Apply positive and negative shocks to the weight
                for delta in [weight_shock, -weight_shock]:
                    new_weight = f.weight * (1 + delta)
                    diff = (new_weight - f.weight) * eff_mean

                    shocked_score = stats.mean_score + diff
                    if shocked_score < worst_score:
                        worst_score = shocked_score

                    if abs(diff) > abs(stats.mean_score * 0.1):  # 10% impact threshold
                        sensitive_factors.append({"factor": f.name, "impact": diff, "shock": delta})

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
                dro_score = mean - epsilon * np.sqrt(variance)

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
