from __future__ import annotations

from typing import Any, Dict, List

from python.core.models import Factor, Statistics


class SensitivityEngine:
    @staticmethod
    def analyze(
        mc_results: Dict[str, Statistics], factors: List[Factor]
    ) -> Dict[str, Any]:
        if not mc_results or not factors:
            return {"base_winner": None, "changes": [], "score_changes": [], "robustness_score": 1.0}

        base_winner = max(mc_results.items(), key=lambda x: x[1].mean_score)[0]

        sensitivity_report: Dict[str, Any] = {
            "base_winner": base_winner,
            "weight_changes": [],
            "score_changes": [],
        }

        total_weight = sum(f.weight for f in factors)
        if total_weight == 0:
            return {**sensitivity_report, "robustness_score": 1.0}

        raw_scores = {}
        for name, stats in mc_results.items():
            raw_scores[name] = {k: v["mean"] for k, v in stats.factor_stats.items()}

        def compute_winner(scores_dict):
            return max(scores_dict.items(), key=lambda x: x[1])[0]

        weight_changes_count = 0
        total_weight_checks = 0

        for f in factors:
            for delta in [0.2, -0.2]:
                new_weight = f.weight * (1 + delta)
                new_ranking = {}
                for name, f_vals in raw_scores.items():
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
                    new_ranking[name] = score

                new_winner = compute_winner(new_ranking)
                total_weight_checks += 1
                if new_winner != base_winner:
                    weight_changes_count += 1
                    sensitivity_report["weight_changes"].append({
                        "factor": f.name,
                        "change": f"+{int(delta * 100)}%" if delta > 0 else f"{int(delta * 100)}%",
                        "new_winner": new_winner,
                    })

        score_changes_count = 0
        total_score_checks = 0

        for f in factors:
            for delta in [0.1, -0.1, 0.2, -0.2]:
                new_ranking = {}
                for name, f_vals in raw_scores.items():
                    score = 0.0
                    for other_f in factors:
                        val = f_vals.get(other_f.name, 0)
                        if other_f.name == f.name:
                            val = val * (1 + delta)
                        if other_f.maximize:
                            score += val * other_f.weight
                        else:
                            score -= val * other_f.weight
                    new_ranking[name] = score

                new_winner = compute_winner(new_ranking)
                total_score_checks += 1
                if new_winner != base_winner:
                    score_changes_count += 1
                    sensitivity_report["score_changes"].append({
                        "factor": f.name,
                        "change": f"+{int(delta * 100)}%" if delta > 0 else f"{int(delta * 100)}%",
                        "new_winner": new_winner,
                    })

        total_checks = total_weight_checks + total_score_checks
        total_changes = weight_changes_count + score_changes_count
        sensitivity_report["robustness_score"] = (
            1.0 - (total_changes / total_checks) if total_checks > 0 else 1.0
        )
        return sensitivity_report
