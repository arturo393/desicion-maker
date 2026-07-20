from __future__ import annotations

__all__ = ["SensitivityEngine"]

from typing import Any, Dict, List

from python.core.models import Factor, Statistics
from python.core.utils import WEIGHT_DELTA, SCORE_DELTAS


class SensitivityEngine:
    @staticmethod
    def _compute_scores(
        raw_scores: Dict[str, Dict[str, float]],
        factors: List[Factor],
        target_factor: Factor = None,
        target_delta: float = 0.0,
        modify_weight: bool = False,
    ) -> Dict[str, float]:
        """Compute composite scores with normalization, matching Monte Carlo logic."""
        # Compute global bounds per factor across all options
        bounds: Dict[str, Dict[str, float]] = {}
        for f in factors:
            vals = [s.get(f.name, 0) for s in raw_scores.values()]
            bounds[f.name] = {"min": min(vals), "max": max(vals)}

        result = {}
        for name, f_vals in raw_scores.items():
            score = 0.0
            for f in factors:
                val = f_vals.get(f.name, 0)
                w = f.weight
                if target_factor and f.name == target_factor.name:
                    if modify_weight:
                        w = f.weight * (1 + target_delta)
                    else:
                        val = val * (1 + target_delta)
                f_min = bounds[f.name]["min"]
                f_max = bounds[f.name]["max"]
                norm_val = (val - f_min) / (f_max - f_min) if f_max > f_min else 1.0
                score += norm_val * w if f.maximize else (1.0 - norm_val) * w
            result[name] = score
        return result

    @staticmethod
    def analyze(
        mc_results: Dict[str, Statistics], factors: List[Factor]
    ) -> Dict[str, Any]:
        if not mc_results or not factors:
            return {"base_winner": None, "weight_changes": [], "score_changes": [], "robustness_score": 1.0}

        base_winner = max(mc_results.items(), key=lambda x: x[1].mean_score)[0]

        sensitivity_report: Dict[str, Any] = {
            "base_winner": base_winner,
            "weight_changes": [],
            "score_changes": [],
        }

        total_weight = sum(f.weight for f in factors)
        if total_weight == 0:
            return {**sensitivity_report, "robustness_score": 1.0}

        raw_scores = {
            name: {k: v["mean"] for k, v in stats.factor_stats.items()}
            for name, stats in mc_results.items()
        }

        def compute_winner(scores_dict):
            return max(scores_dict.items(), key=lambda x: x[1])[0]

        weight_changes_count = 0
        score_changes_count = 0
        total_checks = 0

        # Weight sensitivity
        for f in factors:
            for delta in [WEIGHT_DELTA, -WEIGHT_DELTA]:
                new_ranking = SensitivityEngine._compute_scores(
                    raw_scores, factors, target_factor=f,
                    target_delta=delta, modify_weight=True,
                )
                total_checks += 1
                if compute_winner(new_ranking) != base_winner:
                    weight_changes_count += 1
                    sensitivity_report["weight_changes"].append({
                        "factor": f.name,
                        "change": f"+{int(delta * 100)}%" if delta > 0 else f"{int(delta * 100)}%",
                        "new_winner": compute_winner(new_ranking),
                    })

        # Score sensitivity
        for f in factors:
            for delta in SCORE_DELTAS:
                new_ranking = SensitivityEngine._compute_scores(
                    raw_scores, factors, target_factor=f,
                    target_delta=delta, modify_weight=False,
                )
                total_checks += 1
                if compute_winner(new_ranking) != base_winner:
                    score_changes_count += 1
                    sensitivity_report["score_changes"].append({
                        "factor": f.name,
                        "change": f"+{int(delta * 100)}%" if delta > 0 else f"{int(delta * 100)}%",
                        "new_winner": compute_winner(new_ranking),
                    })

        total_changes = weight_changes_count + score_changes_count
        sensitivity_report["robustness_score"] = (
            1.0 - (total_changes / total_checks) if total_checks > 0 else 1.0
        )
        return sensitivity_report
