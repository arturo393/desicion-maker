from __future__ import annotations

from typing import Any, Dict, List

import numpy as np

from python.core.models import Factor, Statistics


class RobustOptimizer:
    @staticmethod
    def analyze(
        mc_results: Dict[str, Statistics],
        factors: List[Factor],
        alpha: float = 0.95,
        weight_shock: float = 0.2,
    ) -> Dict[str, Any]:
        if not mc_results or not factors:
            return {"robust_ranking": {}, "worst_case_scores": {}}

        raw_scores: Dict[str, Dict[str, float]] = {}
        for name, stats in mc_results.items():
            raw_scores[name] = {k: v["mean"] for k, v in stats.factor_stats.items()}

        worst_case_scores: Dict[str, float] = {}

        for opt_name, f_vals in raw_scores.items():
            worst = float("inf")
            for f in factors:
                for delta in [weight_shock, -weight_shock]:
                    new_weight = f.weight * (1 + delta)
                    score = 0.0
                    for other_f in factors:
                        w = other_f.weight
                        if other_f.name == f.name:
                            w = new_weight
                        val = f_vals.get(other_f.name, 0)
                        if other_f.maximize:
                            score += val * w
                        else:
                            score -= val * w
                    if score < worst:
                        worst = score

            cvar = stats.cvar_95
            robust_score = min(worst, cvar)
            worst_case_scores[opt_name] = robust_score

        ranking = sorted(worst_case_scores.items(), key=lambda x: x[1], reverse=True)

        return {
            "robust_ranking": dict(ranking),
            "worst_case_scores": worst_case_scores,
            "winner": ranking[0][0] if ranking else None,
        }
