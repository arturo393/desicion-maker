from __future__ import annotations

from typing import Dict

import numpy as np

from python.core.models import Statistics


class BayesianEngine:
    @staticmethod
    def analyze(
        mc_results: Dict[str, Statistics],
        num_posterior_samples: int = 10000,
        seed: int = 42,
    ) -> Dict[str, float]:
        if not mc_results:
            return {}
        if len(mc_results) == 1:
            return {next(iter(mc_results)): 1.0}

        rng = np.random.default_rng(seed)
        names = list(mc_results.keys())
        stats_list = [mc_results[n] for n in names]
        best_counts = np.zeros(len(names), dtype=int)

        for _ in range(num_posterior_samples):
            best_score = -float("inf")
            best_idx = 0
            for i, s in enumerate(stats_list):
                score = rng.normal(s.mean_score, max(s.std_dev, 1e-12))
                if score > best_score:
                    best_score = score
                    best_idx = i
            best_counts[best_idx] += 1

        posteriors = {name: float(count / num_posterior_samples) for name, count in zip(names, best_counts)}

        return posteriors
