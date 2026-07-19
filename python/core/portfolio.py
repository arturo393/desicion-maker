from __future__ import annotations

import logging
from itertools import combinations
from typing import Any, Dict, List, Tuple

import numpy as np

from python.core.models import Statistics
from python.core.utils import EPSILON

logger = logging.getLogger(__name__)

# Risk aversion grid for efficient frontier
RISK_AVERSION_GRID = [0.0, 0.5, 1.0, 2.0, 5.0, 10.0]
RANDOM_SEARCH_ITERATIONS = 10000


class PortfolioOptimizer:
    """
    Allocates budget/resources across decision options.

    Uses mean-variance optimization to find efficient portfolios
    and identifies the optimal allocation given a risk budget.
    """

    @staticmethod
    def optimize(
        mc_results: Dict[str, Statistics],
        budget: float = 1.0,
        risk_aversion: float = 1.0,
        min_allocation: float = 0.0,
        max_allocation: float = 1.0,
    ) -> Dict[str, Any]:
        """
        Find optimal budget allocation across options.

        Uses a simplified mean-variance approach:
        maximize: E[portfolio] - risk_aversion * Var[portfolio]
        subject to: sum(weights) = budget, min <= w_i <= max

        Args:
            mc_results: from Monte Carlo analysis
            budget: total budget to allocate (default 1.0 = 100%)
            risk_aversion: higher = more conservative (default 1.0)
            min_allocation: minimum per option (default 0.0)
            max_allocation: maximum per option (default 1.0)

        Returns:
            {allocations: {name: weight}, expected_return, portfolio_risk,
             efficient_frontier: [{return, risk}]}
        """
        names = list(mc_results.keys())
        n = len(names)
        if n == 0:
            return {"error": "No options"}
        if n == 1:
            return {
                "allocations": {names[0]: budget},
                "expected_return": mc_results[names[0]].mean_score,
                "portfolio_risk": mc_results[names[0]].std_dev,
                "efficient_frontier": [],
            }

        # Build return vector and covariance matrix from raw_scores
        returns = np.array([mc_results[n].mean_score for n in names])
        if all(s.raw_scores is not None for s in mc_results.values()):
            score_matrix = np.column_stack([mc_results[n].raw_scores for n in names])
            cov_matrix = np.cov(score_matrix, rowvar=False)
        else:
            stds = np.array([mc_results[n].std_dev for n in names])
            cov_matrix = np.diag(stds ** 2)

        # Simple grid search over allocations
        best_return = -np.inf
        best_weights = None

        if n == 2:
            grid = np.linspace(0, budget, 101)
            for w0 in grid:
                if w0 < min_allocation * budget or w0 > max_allocation * budget:
                    continue
                w1 = budget - w0
                if w1 < min_allocation * budget or w1 > max_allocation * budget:
                    continue
                weights = np.array([w0, w1])
                port_return = np.dot(weights, returns)
                port_var = weights @ cov_matrix @ weights
                objective = port_return - risk_aversion * port_var
                if objective > best_return:
                    best_return = objective
                    best_weights = weights.copy()
        else:
            # For 3+ options, use a simple random search
            rng = np.random.default_rng(42)
            for _ in range(10000):
                raw = rng.uniform(0, 1, n)
                weights = raw / raw.sum() * budget
                # Clip to bounds
                weights = np.clip(weights, min_allocation * budget, max_allocation * budget)
                weights = weights / weights.sum() * budget
                port_return = np.dot(weights, returns)
                port_var = weights @ cov_matrix @ weights
                objective = port_return - risk_aversion * port_var
                if objective > best_return:
                    best_return = objective
                    best_weights = weights.copy()

        if best_weights is None:
            best_weights = np.full(n, budget / n)

        port_return = float(np.dot(best_weights, returns))
        port_risk = float(np.sqrt(best_weights @ cov_matrix @ best_weights))

        # Efficient frontier (vary risk_aversion)
        frontier = []
        for ra in RISK_AVERSION_GRID:
            best_obj = -np.inf
            best_w = None

            if n == 2:
                for w0 in grid:
                    if w0 < min_allocation * budget or w0 > max_allocation * budget:
                        continue
                    w1 = budget - w0
                    if w1 < min_allocation * budget or w1 > max_allocation * budget:
                        continue
                    w = np.array([w0, w1])
                    obj = np.dot(w, returns) - ra * (w @ cov_matrix @ w)
                    if obj > best_obj:
                        best_obj = obj
                        best_w = w.copy()
            else:
                rng = np.random.default_rng(42)
                for _ in range(RANDOM_SEARCH_ITERATIONS):
                    raw = rng.uniform(0, 1, n)
                    w = raw / raw.sum() * budget
                    w = np.clip(w, min_allocation * budget, max_allocation * budget)
                    w = w / w.sum() * budget
                    obj = np.dot(w, returns) - ra * (w @ cov_matrix @ w)
                    if obj > best_obj:
                        best_obj = obj
                        best_w = w.copy()

            if best_w is not None:
                frontier.append({
                    "risk_aversion": ra,
                    "return": float(np.dot(best_w, returns)),
                    "risk": float(np.sqrt(best_w @ cov_matrix @ best_w)),
                    "allocations": dict(zip(names, best_w.tolist())),
                })

        # Compute diversification ratio
        weighted_risk = np.sum(best_weights * np.sqrt(np.diag(cov_matrix)))
        div_ratio = weighted_risk / (port_risk + EPSILON)

        return {
            "allocations": dict(zip(names, best_weights.tolist())),
            "expected_return": port_return,
            "portfolio_risk": port_risk,
            "sharpe_ratio": port_return / (port_risk + EPSILON),
            "diversification_ratio": float(div_ratio),
            "risk_aversion_used": risk_aversion,
            "budget": budget,
            "num_options": n,
            "efficient_frontier": frontier,
        }

    @staticmethod
    def equal_weight(mc_results: Dict[str, Statistics]) -> Dict[str, float]:
        """Equal-weight allocation across all options."""
        names = list(mc_results.keys())
        w = 1.0 / len(names) if names else 0
        return {n: w for n in names}
