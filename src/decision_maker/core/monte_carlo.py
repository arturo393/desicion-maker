"""
Monte Carlo simulation engine producing per-option score distributions and statistics.
Usage: from decision_maker.core.monte_carlo import MonteCarloEngine
Does NOT: Rank options (use TOPSIS/PROMETHEE) or persist results (see reporting/registry).
"""

from __future__ import annotations

__all__ = ["MonteCarloEngine"]

import logging

import numpy as np

from decision_maker.core.models import DecisionOption, Factor, Statistics

logger = logging.getLogger(__name__)

RUIN_THRESHOLD_PERCENTILE = 5.0
EPSILON_SCORE = 1e-12


class MonteCarloEngine:
    def __init__(self, num_simulations: int = 10000, correlation_matrix: np.ndarray | None = None):
        if num_simulations < 1:
            raise ValueError(f"num_simulations must be >= 1, got {num_simulations}")
        self.num_simulations = num_simulations
        self.factors: list[Factor] = []
        self.options: list[DecisionOption] = []
        self._option_names: set = set()
        self.correlation_matrix = correlation_matrix

    def add_factor(self, factor: Factor) -> None:
        self.factors.append(factor)

    def add_option(self, option: DecisionOption) -> None:
        if option.name in self._option_names:
            logger.warning(f"Duplicate option name '{option.name}' — previous will be overwritten")
        self._option_names.add(option.name)
        self.options.append(option)

    def _apply_correlation(self, samples: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
        """Apply Cholesky decomposition to induce correlation between factors."""
        if self.correlation_matrix is None:
            return samples

        factor_names = [f.name for f in self.factors if any(f.name in opt.variables for opt in self.options)]
        n_factors = len(factor_names)
        if n_factors < 2:
            return samples

        if self.correlation_matrix.shape != (n_factors, n_factors):
            logger.warning(
                f"Correlation matrix shape {self.correlation_matrix.shape} "
                f"doesn't match {n_factors} factors — skipping correlation"
            )
            return samples

        try:
            L = np.linalg.cholesky(self.correlation_matrix)
        except np.linalg.LinAlgError:
            logger.warning("Correlation matrix not positive definite — skipping correlation")
            return samples

        for opt in self.options:
            available = [fn for fn in factor_names if fn in opt.variables]
            if len(available) < 2:
                continue

            idx_map = {fn: i for i, fn in enumerate(factor_names) if fn in opt.variables}
            idx_list = [idx_map[fn] for fn in available]

            raw = np.column_stack([samples[opt.name][fn] for fn in available if fn in samples[opt.name]])
            if raw.shape[1] < 2:
                continue

            from scipy.stats import rankdata
            ranked = np.apply_along_axis(rankdata, 0, raw) / (self.num_simulations + 1)
            from scipy.stats import norm
            normal_scores = norm.ppf(np.clip(ranked, 0.001, 0.999))

            correlated = normal_scores @ L[np.ix_(idx_list, idx_list)].T
            from scipy.stats import norm as norm_dist
            uniform_correlated = norm_dist.cdf(correlated)

            for j, fn in enumerate(available):
                if fn in samples[opt.name]:
                    original = samples[opt.name][fn]
                    order = np.argsort(original)
                    template = np.zeros(self.num_simulations)
                    rank_order = np.argsort(np.argsort(uniform_correlated[:, j]))
                    template[rank_order] = original[order]
                    samples[opt.name][fn] = template

        return samples

    def run(self, normalize: bool = True) -> dict[str, Statistics]:
        if not self.options or not self.factors:
            return {}

        logger.info(f"Running {self.num_simulations} Monte Carlo simulations in Python...")

        sampled_data = {}
        for opt in self.options:
            opt_data = {}
            for v_name, var in opt.variables.items():
                opt_data[v_name] = var.sample(self.num_simulations)
            sampled_data[opt.name] = opt_data

        sampled_data = self._apply_correlation(sampled_data)

        global_bounds = {}
        if normalize:
            for f in self.factors:
                all_vals = []
                for opt in self.options:
                    if f.name in sampled_data[opt.name]:
                        all_vals.append(sampled_data[opt.name][f.name])
                if all_vals:
                    conc = np.concatenate(all_vals)
                    global_bounds[f.name] = (np.min(conc), np.max(conc))

        results: dict[str, Statistics] = {}
        for opt in self.options:
            opt_data = sampled_data[opt.name]
            total_scores = np.zeros(self.num_simulations)
            factor_stats = {}

            for f in self.factors:
                if f.name in opt_data:
                    vals = opt_data[f.name]
                    factor_stats[f.name] = {
                        "mean": float(np.mean(vals)),
                        "std": float(np.std(vals)),
                        "p5": float(np.percentile(vals, 5)),
                        "p95": float(np.percentile(vals, 95))
                    }

                    if f.maximize:
                        total_scores += vals * f.weight
                    else:
                        total_scores -= vals * f.weight

            if np.std(total_scores) > EPSILON_SCORE:
                ruin_threshold = np.percentile(total_scores, RUIN_THRESHOLD_PERCENTILE)
                ruin_mask = total_scores <= ruin_threshold
                ruin_count = np.sum(ruin_mask)
                if ruin_count > 0:
                    ruin_penalty = 1.0 - (ruin_count / self.num_simulations)
                    total_scores[ruin_mask] *= ruin_penalty

            results[opt.name] = Statistics(
                option_name=opt.name,
                mean_score=float(np.mean(total_scores)),
                std_dev=float(np.std(total_scores)),
                min_score=float(np.min(total_scores)),
                max_score=float(np.max(total_scores)),
                percentile_5=float(np.percentile(total_scores, 5)),
                percentile_95=float(np.percentile(total_scores, 95)),
                success_rate=float(np.mean(total_scores > 0)),
                factor_stats=factor_stats,
                var_95=float(np.percentile(total_scores, 5)),
                cvar_95=float(np.mean(total_scores[total_scores <= np.percentile(total_scores, 5)]) if len(total_scores[total_scores <= np.percentile(total_scores, 5)]) > 0 else np.percentile(total_scores, 5)),
                raw_scores=total_scores,
                raw_factor_data=opt_data,
            )

        return results
