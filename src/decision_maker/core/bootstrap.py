"""
Bootstrap confidence interval estimation for option ranking stability.
Usage: from decision_maker.core.bootstrap import BootstrapRanking
Does NOT: Generate synthetic scenario samples without empirical input distributions.
"""

from __future__ import annotations

__all__ = ["BootstrapRanking"]

from typing import Any, Dict, List, Tuple

import numpy as np

from decision_maker.core.topsis import TOPSISEngine

# Noise scaling factor for bootstrap perturbation
BOOTSTRAP_NOISE_SCALE = 0.1


class BootstrapRanking:
    @staticmethod
    def confidence_intervals(
        decision_matrix_fuzzy: Dict[str, Dict[str, Tuple[float, float, float]]],
        weights: List[float],
        maximize: List[bool],
        n_bootstrap: int = 1000,
        alpha: float = 0.05,
    ) -> Dict[str, Any]:
        if not decision_matrix_fuzzy:
            return {}
        if len(decision_matrix_fuzzy) <= 1:
            opt = next(iter(decision_matrix_fuzzy))
            return {opt: {"mean_rank": 1.0, "ci_low": 1.0, "ci_high": 1.0, "p_best": 1.0}}

        opt_names = list(decision_matrix_fuzzy.keys())
        n_opts = len(opt_names)
        factor_names = list(list(decision_matrix_fuzzy.values())[0].keys())

        engine = TOPSISEngine()

        rank_matrix = np.zeros((n_bootstrap, n_opts), dtype=int)

        for b in range(n_bootstrap):
            boot_data: Dict[str, Dict[str, Tuple[float, float, float]]] = {}
            for opt in opt_names:
                boot_data[opt] = {}
                for f in factor_names:
                    a, b_val, c = decision_matrix_fuzzy[opt][f]
                    noise = np.random.normal(0, (c - a) * BOOTSTRAP_NOISE_SCALE, 3)
                    boot_data[opt][f] = (
                        a + noise[0],
                        b_val + noise[1],
                        c + noise[2],
                    )
            scores = engine.analyze(boot_data, weights, maximize)
            for rank_pos, opt in enumerate(scores.index):
                opt_idx = opt_names.index(opt)
                rank_matrix[b, opt_idx] = rank_pos + 1

        results = {}
        for i, opt in enumerate(opt_names):
            ranks = rank_matrix[:, i]
            p_best = float(np.mean(rank_matrix[:, i] == 1))
            results[opt] = {
                "mean_rank": float(np.mean(ranks)),
                "ci_low": float(np.percentile(ranks, 100 * alpha / 2)),
                "ci_high": float(np.percentile(ranks, 100 * (1 - alpha / 2))),
                "p_best": p_best,
            }

        return results
