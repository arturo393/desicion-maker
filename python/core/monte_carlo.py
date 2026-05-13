from __future__ import annotations

import logging
from typing import Dict, List, Optional

import numpy as np

from python.core.models import Factor, DecisionOption, Statistics

logger = logging.getLogger(__name__)


class MonteCarloEngine:
    def __init__(self, num_simulations: int = 10000, correlation_matrix: Optional[np.ndarray] = None):
        if num_simulations < 1:
            raise ValueError(f"num_simulations must be >= 1, got {num_simulations}")
        self.num_simulations = num_simulations
        self.factors: List[Factor] = []
        self.options: List[DecisionOption] = []
        self._option_names: set = set()
        self.correlation_matrix = correlation_matrix

    def add_factor(self, factor: Factor):
        self.factors.append(factor)

    def add_option(self, option: DecisionOption):
        if option.name in self._option_names:
            logger.warning(f"Duplicate option name '{option.name}' — previous will be overwritten")
        self._option_names.add(option.name)
        self.options.append(option)

    def _apply_correlation(self, sampled_data: Dict[str, np.ndarray]) -> Dict[str, np.ndarray]:
        if self.correlation_matrix is None:
            return sampled_data
        n_factors = len(self.factors)
        if self.correlation_matrix.shape != (n_factors, n_factors):
            logger.warning(
                f"Correlation matrix shape {self.correlation_matrix.shape} != ({n_factors},{n_factors}). Skipping."
            )
            return sampled_data
        factor_names = [f.name for f in self.factors]
        available = [fn for fn in factor_names if fn in sampled_data]
        if len(available) < 2:
            return sampled_data
        idx_map = {fn: i for i, fn in enumerate(factor_names) if fn in sampled_data}
        available_indices = [idx_map[fn] for fn in available]
        sub_corr = self.correlation_matrix[np.ix_(available_indices, available_indices)]
        try:
            L = np.linalg.cholesky(sub_corr)
        except np.linalg.LinAlgError:
            logger.warning("Correlation matrix not positive definite. Skipping correlation.")
            return sampled_data
        n = self.num_simulations
        m = len(available)
        independent_normal = np.random.normal(0, 1, (n, m))
        correlated_normal = independent_normal @ L.T
        for idx, fn in enumerate(available):
            ranks = correlated_normal[:, idx].argsort().argsort()
            original = sampled_data[fn]
            sampled_data[fn] = np.sort(original)[ranks]
        return sampled_data

    def run(self) -> Dict[str, Statistics]:
        if not self.options:
            return {}
        if not self.factors:
            return {}

        results: Dict[str, Statistics] = {}

        for option in self.options:
            sampled_data = {}
            for var_name, var in option.variables.items():
                sampled_data[var_name] = var.sample(self.num_simulations)
            sampled_data = self._apply_correlation(sampled_data)

            total_scores = np.zeros(self.num_simulations)

            for factor in self.factors:
                if factor.name in sampled_data:
                    values = sampled_data[factor.name]
                    if not factor.maximize:
                        total_scores -= values * factor.weight
                    else:
                        total_scores += values * factor.weight

            mean = float(np.mean(total_scores))
            std = float(np.std(total_scores)) if len(total_scores) > 1 else 0.0
            p5 = float(np.percentile(total_scores, 5))
            p95 = float(np.percentile(total_scores, 95))

            var_95 = p5
            cvar_95 = float(np.mean(total_scores[total_scores <= p5])) if np.any(total_scores <= p5) else p5

            success_rate = float(np.mean(total_scores > 0))

            factor_stats = {}
            for name, values in sampled_data.items():
                factor_stats[name] = {
                    "mean": float(np.mean(values)),
                    "std": float(np.std(values)) if len(values) > 1 else 0.0,
                    "p5": float(np.percentile(values, 5)),
                    "p95": float(np.percentile(values, 95)),
                }

            stats = Statistics(
                option_name=option.name,
                mean_score=mean,
                std_dev=std,
                min_score=float(np.min(total_scores)),
                max_score=float(np.max(total_scores)),
                percentile_5=p5,
                percentile_95=p95,
                success_rate=success_rate,
                factor_stats=factor_stats,
                var_95=var_95,
                cvar_95=cvar_95,
            )
            results[option.name] = stats

        return results
