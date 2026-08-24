"""
Genetic algorithm optimizer for finding composite decision solutions.
Usage: from decision_maker.core.genetic import GeneticOptimizer
Does NOT: Run topological data analysis or Bayesian belief networks.
"""

from __future__ import annotations

__all__ = ["GeneticOptimizer"]

from typing import Any

from decision_maker.core.models import Factor, Statistics
from decision_maker.core.utils import EPSILON

# Maximum improvement percentage cap to avoid outliers
MAX_IMPROVEMENT_PCT = 500.0


class GeneticOptimizer:
    """
    Calculates the 'Ideal Option' by harvesting the best traits (genes)
    from all available options and computing the theoretical efficiency frontier.
    """

    @staticmethod
    def evolve_ideal(
        mc_results: dict[str, Statistics],
        factors: list[Factor],
        penalty_variance: float = 0.05,  # Reduced penalty for more realistic gap
    ) -> dict[str, Any]:
        if not mc_results or not factors:
            return {
                "ideal_composition": {},
                "source_options": {},
                "improvement_potential": 0,
            }

        # 1. Find the best raw value for each factor across all options
        ideal_genes = {}
        source_options = {}

        for f in factors:
            best_raw_val = None
            best_opt = None

            for opt_name, stats in mc_results.items():
                if f.name in stats.factor_stats:
                    val = stats.factor_stats[f.name]["mean"]

                    if best_raw_val is None:
                        best_raw_val = val
                        best_opt = opt_name
                    else:
                        # If maximize=True, we want the highest value
                        # If maximize=False, we want the lowest value
                        if f.maximize:
                            if val > best_raw_val:
                                best_raw_val = val
                                best_opt = opt_name
                        else:
                            if val < best_raw_val:
                                best_raw_val = val
                                best_opt = opt_name

            if best_opt is not None:
                ideal_genes[f.name] = best_raw_val
                source_options[f.name] = best_opt

        # 2. Calculate the theoretical max score on the SAME normalized scale the
        #    MonteCarloEngine now produces (each factor normalized to [0,1] via
        #    global min/max; maximize -> norm*w, minimize -> (1-norm)*w).
        #    The ideal option holds every factor at its best value, so each factor
        #    contributes its full weight: theoretical_max = sum of weights.
        theoretical_max_score = 0.0
        for f in factors:
            if f.name in ideal_genes:
                theoretical_max_score += f.weight

        # 3. Apply a small 'complexity penalty' for being a hybrid
        unique_sources = len(set(source_options.values()))
        if unique_sources > 1:
            theoretical_max_score *= 1.0 - (penalty_variance * (unique_sources - 1) / len(factors))

        # 4. Compare against the best actual performer
        best_actual_stats = max(mc_results.values(), key=lambda x: x.mean_score)
        current_best = best_actual_stats.mean_score

        # Calculate improvement potential relative to current best
        # Ensure we don't divide by zero
        denominator = max(abs(current_best), EPSILON)
        gap = theoretical_max_score - current_best
        improvement_pct = (gap / denominator) * 100 if gap > 0 else 0.0

        return {
            "ideal_composition": ideal_genes,
            "source_options": source_options,
            "theoretical_max_score": float(theoretical_max_score),
            "best_actual_score": float(current_best),
            "gap": float(gap),
            "improvement_potential": float(
                min(improvement_pct, MAX_IMPROVEMENT_PCT)
            ),  # Cap at MAX_IMPROVEMENT_PCT to avoid outliers
        }
