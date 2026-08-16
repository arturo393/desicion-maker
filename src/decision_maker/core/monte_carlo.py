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

                    # Removed Min-Max normalization to preserve true tail risks (Taleb)
                    # Using Geometric/Multiplicative penalization for dynamic survival logic
                    if f.maximize:
                        total_scores += vals * f.weight
                    else:
                        total_scores -= vals * f.weight
                        
                    # Geometric ruin penalty: if a critical factor drops too low, it acts as an absorbing state
                    if not f.maximize and np.any(vals > (np.mean(vals) + 3*np.std(vals))):
                        # Extreme negative tail event (e.g. ruin), dynamically penalize
                        total_scores[vals > (np.mean(vals) + 3*np.std(vals))] *= 0.1

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
