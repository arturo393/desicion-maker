from __future__ import annotations

from typing import Any, Dict, List

from python.core.models import Factor, Statistics
from python.core.utils import EPSILON

# Maximum improvement percentage cap to avoid outliers
MAX_IMPROVEMENT_PCT = 500.0


class GeneticOptimizer:
    """
    Calculates the 'Ideal Option' by harvesting the best traits (genes) 
    from all available options and computing the theoretical efficiency frontier.
    """
    @staticmethod
    def evolve_ideal(
        mc_results: Dict[str, Statistics],
        factors: List[Factor],
        penalty_variance: float = 0.05, # Reduced penalty for more realistic gap
    ) -> Dict[str, Any]:
        if not mc_results or not factors:
            return {
                "ideal_composition": {},
                "source_options": {},
                "improvement_potential": 0,
            }

        # 1. Find the best raw value for each factor across all options
        ideal_genes = {}
        source_options = {}
        
        # We also need the global min/max for each factor to normalize the 'Ideal'
        global_bounds = {f.name: {"min": float('inf'), "max": float('-inf')} for f in factors}
        for opt_stats in mc_results.values():
            for f_name, f_data in opt_stats.factor_stats.items():
                if f_name in global_bounds:
                    global_bounds[f_name]["min"] = min(global_bounds[f_name]["min"], f_data["mean"])
                    global_bounds[f_name]["max"] = max(global_bounds[f_name]["max"], f_data["mean"])

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

        # 2. Calculate the Normalized Weighted Score of this 'Ideal' option
        theoretical_max_score = 0.0
        for f in factors:
            if f.name in ideal_genes:
                raw_val = ideal_genes[f.name]
                f_min = global_bounds[f.name]["min"]
                f_max = global_bounds[f.name]["max"]
                
                # Normalize exactly like the MonteCarloEngine
                if f_max > f_min:
                    norm_val = (raw_val - f_min) / (f_max - f_min)
                else:
                    norm_val = 1.0
                
                # Apply maximization logic
                score_contribution = norm_val if f.maximize else (1.0 - norm_val)
                theoretical_max_score += score_contribution * f.weight

        # 3. Apply a small 'complexity penalty' for being a hybrid
        unique_sources = len(set(source_options.values()))
        if unique_sources > 1:
            theoretical_max_score *= (1.0 - (penalty_variance * (unique_sources - 1) / len(factors)))

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
            "improvement_potential": float(min(improvement_pct, MAX_IMPROVEMENT_PCT)), # Cap at MAX_IMPROVEMENT_PCT to avoid outliers
        }
