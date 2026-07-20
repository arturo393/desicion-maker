from __future__ import annotations

__all__ = ["MonteCarloEngine"]

import logging
from typing import Dict, List, Optional

import numpy as np

from python.core.models import DecisionOption, Factor, Statistics

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

    def add_factor(self, factor: Factor) -> None:
        self.factors.append(factor)

    def add_option(self, option: DecisionOption) -> None:
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

    def run(self, normalize: bool = True) -> Dict[str, Statistics]:
        if not self.options or not self.factors:
            return {}

        # 1. Collection Phase: Gather all samples and find global bounds for normalization
        all_samples = {}
        global_bounds = {f.name: {"min": float('inf'), "max": float('-inf')} for f in self.factors}

        for option in self.options:
            sampled_data = {}
            for var_name, var in option.variables.items():
                sampled_data[var_name] = var.sample(self.num_simulations)

            sampled_data = self._apply_correlation(sampled_data)
            for fn in sampled_data:
                sampled_data[fn] = np.nan_to_num(sampled_data[fn], nan=0.0, posinf=1e10, neginf=-1e10)
            all_samples[option.name] = sampled_data

            # Update global bounds across all options
            for fn, values in sampled_data.items():
                if fn in global_bounds:
                    global_bounds[fn]["min"] = min(global_bounds[fn]["min"], np.min(values))
                    global_bounds[fn]["max"] = max(global_bounds[fn]["max"], np.max(values))

        # 2. Calculation Phase: Normalize and compute scores
        results: Dict[str, Statistics] = {}

        for option in self.options:
            sampled_data = all_samples[option.name]
            total_scores = np.zeros(self.num_simulations)

            for factor in self.factors:
                if factor.name in sampled_data:
                    raw_values = sampled_data[factor.name]

                    if normalize:
                        f_min = global_bounds[factor.name]["min"]
                        f_max = global_bounds[factor.name]["max"]

                        if f_max > f_min:
                            # Standard Min-Max Normalization to [0, 1]
                            norm_values = (raw_values - f_min) / (f_max - f_min)
                        else:
                            norm_values = np.full_like(raw_values, 1.0) # Equal values get top score

                        # If maximize: 1.0 is best. If minimize: 0.0 is best (so we invert it).
                        if factor.maximize:
                            total_scores += norm_values * factor.weight
                        else:
                            total_scores += (1.0 - norm_values) * factor.weight
                    else:
                        # Raw calculation (deprecated/absurd for mismatched scales)
                        if not factor.maximize:
                            total_scores -= raw_values * factor.weight
                        else:
                            total_scores += raw_values * factor.weight

            mean = float(np.mean(total_scores))
            std = float(np.std(total_scores)) if len(total_scores) > 1 else 0.0
            p5 = float(np.percentile(total_scores, 5))
            p95 = float(np.percentile(total_scores, 95))

            var_95 = p5
            cvar_95 = float(np.mean(total_scores[total_scores <= p5])) if np.any(total_scores <= p5) else p5

            total_weight = sum(f.weight for f in self.factors)
            success_threshold = 0.5 * total_weight if normalize else 0.0
            success_rate = float(np.mean(total_scores > success_threshold))

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
                raw_scores=total_scores,
                raw_factor_data=sampled_data,
            )
            results[option.name] = stats

        return results
