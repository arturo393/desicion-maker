"""
Decision theory engine evaluating options under uncertainty using classic decision criteria.
Usage: from decision_maker.core.decision_theory import DecisionTheoryEngine
Does NOT: Calculate fuzzy TOPSIS membership vectors or genetic evolution steps.
"""

from __future__ import annotations

__all__ = ["DecisionTheoryEngine"]


import numpy as np

from decision_maker.core.models import Statistics


class DecisionTheoryEngine:
    OPTIMISTIC_PERCENTILE = 0.95
    CONSERVATIVE_PERCENTILE = 0.05

    @staticmethod
    def analyze(
        mc_results: dict[str, Statistics],
        hurwicz_alpha: float = 0.5,
    ) -> dict[str, str]:
        if not mc_results:
            return {}
        if len(mc_results) == 1:
            name = next(iter(mc_results))
            s = mc_results[name]
            return {
                "Maximax (Optimistic)": f"{name} (P95: {s.percentile_95:.2f})",
                "Maximin (Conservative)": f"{name} (P5: {s.percentile_5:.2f})",
                "Hurwicz (Balanced)": f"{name} (Score: {hurwicz_alpha * s.percentile_95 + (1 - hurwicz_alpha) * s.percentile_5:.2f})",
                "Laplace (Risk Neutral)": f"{name} (Avg: {s.mean_score:.2f})",
                "Minimax Regret": f"{name} (Regret: 0.00)",
            }

        strategies = {}

        maximax = max(mc_results.items(), key=lambda x: x[1].percentile_95)
        strategies["Maximax (Optimistic)"] = f"{maximax[0]} (P95: {maximax[1].percentile_95:.2f})"

        maximin = max(mc_results.items(), key=lambda x: x[1].percentile_5)
        strategies["Maximin (Conservative)"] = f"{maximin[0]} (P5: {maximin[1].percentile_5:.2f})"

        hurwicz_scores = {
            name: hurwicz_alpha * stats.percentile_95 + (1 - hurwicz_alpha) * stats.percentile_5
            for name, stats in mc_results.items()
        }
        best_hurwicz = max(hurwicz_scores.items(), key=lambda x: x[1])
        strategies["Hurwicz (Balanced)"] = f"{best_hurwicz[0]} (Score: {best_hurwicz[1]:.2f})"

        laplace = max(mc_results.items(), key=lambda x: x[1].mean_score)
        strategies["Laplace (Risk Neutral)"] = f"{laplace[0]} (Avg: {laplace[1].mean_score:.2f})"

        # Minimax Regret: per-simulation, find best score per scenario
        first_stats = next(iter(mc_results.values()))
        if first_stats.raw_scores is not None:
            n_sims = len(first_stats.raw_scores)
            regret_matrix = np.zeros((len(mc_results), n_sims))
            for i, (_name, stats) in enumerate(mc_results.items()):
                regret_matrix[i] = stats.raw_scores
            best_per_sim = np.max(regret_matrix, axis=0)
            max_regrets = np.max(best_per_sim - regret_matrix, axis=1)
            min_regret_idx = int(np.argmin(max_regrets))
            min_regret_option = list(mc_results.keys())[min_regret_idx]
            min_regret_val = float(max_regrets[min_regret_idx])
        else:
            means = {name: stats.mean_score for name, stats in mc_results.items()}
            best_possible = max(means.values())
            regrets = {name: best_possible - val for name, val in means.items()}
            min_regret_option = min(regrets.items(), key=lambda x: x[1])[0]
            min_regret_val = min(regrets.values())

        strategies["Minimax Regret"] = f"{min_regret_option} (Max Regret: {min_regret_val:.2f})"

        return strategies
