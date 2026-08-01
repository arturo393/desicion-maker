"""
Pareto efficiency analyzer identifying non-dominated decision options.
Usage: from decision_maker.core.pareto import ParetoAnalyzer
Does NOT: Compute weighted composite scores or rank orders.
"""

from __future__ import annotations

__all__ = ["ParetoEngine"]

from typing import Any, Dict, List

from decision_maker.core.models import Factor, Statistics


class ParetoEngine:
    @staticmethod
    def analyze(mc_results: Dict[str, Statistics], factors: List[Factor]) -> Dict[str, Any]:
        if not mc_results:
            return {"efficient_frontier": [], "dominated_options": []}

        normalized_data = {}
        for name, stats in mc_results.items():
            row = {}
            for f in factors:
                val = stats.factor_stats.get(f.name, {"mean": 0})["mean"]
                if not f.maximize:
                    val = -val
                row[f.name] = val
            normalized_data[name] = row

        dominated = []
        efficient = []

        options = list(normalized_data.keys())
        for i, opt_a in enumerate(options):
            is_dominated = False
            vals_a = normalized_data[opt_a]

            for j, opt_b in enumerate(options):
                if i == j:
                    continue
                vals_b = normalized_data[opt_b]
                better_or_equal = all(vals_b[k] >= vals_a[k] for k in vals_a)
                strictly_better = any(vals_b[k] > vals_a[k] for k in vals_a)
                if better_or_equal and strictly_better:
                    is_dominated = True
                    dominated.append((opt_a, opt_b))
                    break

            if not is_dominated:
                efficient.append(opt_a)

        return {"efficient_frontier": efficient, "dominated_options": dominated}
