from __future__ import annotations

from typing import Any, Dict, List

from python.core.models import Factor, Statistics


class GeneticOptimizer:
    @staticmethod
    def evolve_ideal(
        mc_results: Dict[str, Statistics],
        factors: List[Factor],
        penalty_variance: float = 0.1,
    ) -> Dict[str, Any]:
        if not mc_results or not factors:
            return {
                "ideal_composition": {},
                "source_options": {},
                "raw_max": 0,
                "tradeoff_penalty": 0,
                "theoretical_max_score": 0,
                "best_actual_score": 0,
                "gap": 0,
                "improvement_potential": 0,
            }

        ideal_genes = {}
        source_options = {}

        for f in factors:
            best_val = -float("inf")
            best_opt = None
            for opt_name, stats in mc_results.items():
                if f.name in stats.factor_stats:
                    val = stats.factor_stats[f.name]["mean"]
                    if val > best_val:
                        best_val = val
                        best_opt = opt_name
            if best_opt:
                ideal_genes[f.name] = best_val
                source_options[f.name] = best_opt

        unique_sources = len(set(source_options.values()))
        raw_theoretical_max = sum(ideal_genes.values())
        tradeoff_penalty = raw_theoretical_max * (penalty_variance * (unique_sources - 1))
        theoretical_max = raw_theoretical_max - tradeoff_penalty

        best_actual_stats = max(mc_results.values(), key=lambda x: x.mean_score)
        gap = theoretical_max - best_actual_stats.mean_score

        return {
            "ideal_composition": ideal_genes,
            "source_options": source_options,
            "raw_max": raw_theoretical_max,
            "tradeoff_penalty": tradeoff_penalty,
            "theoretical_max_score": theoretical_max,
            "best_actual_score": best_actual_stats.mean_score,
            "gap": gap,
            "improvement_potential": (
                (gap / max(abs(best_actual_stats.mean_score), 1e-12)) * 100
                if gap > 0
                else 0.0
            ),
        }
