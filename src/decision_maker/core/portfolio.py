"""
Portfolio optimization engine selecting optimal subsets of decision options under constraints.
Usage: from decision_maker.core.portfolio import PortfolioOptimizer
Does NOT: Conduct deep research queries.
"""

from __future__ import annotations

__all__ = ["PortfolioOptimizer"]

import logging
from typing import Any, Dict

import numpy as np

from decision_maker.core.models import Statistics
from decision_maker.core.utils import EPSILON

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
    def _grid_search_2d(returns, cov_matrix, budget, risk_aversion, min_allocation, max_allocation):
        """Exhaustive grid search for 2-option portfolios."""
        best_obj = -np.inf
        best_w = None
        grid = np.linspace(0, budget, 101)
        for w0 in grid:
            if w0 < min_allocation * budget or w0 > max_allocation * budget:
                continue
            w1 = budget - w0
            if w1 < min_allocation * budget or w1 > max_allocation * budget:
                continue
            w = np.array([w0, w1])
            obj = np.dot(w, returns) - risk_aversion * (w @ cov_matrix @ w)
            if obj > best_obj:
                best_obj = obj
                best_w = w.copy()
        return best_obj, best_w

    @staticmethod
    def _random_search(returns, cov_matrix, budget, risk_aversion, n, min_allocation, max_allocation, iterations=10000):
        """Random search for 3+ option portfolios."""
        best_obj = -np.inf
        best_w = None
        rng = np.random.default_rng(42)
        for _ in range(iterations):
            raw = rng.uniform(0, 1, n)
            w = raw / raw.sum() * budget
            w = np.clip(w, min_allocation * budget, max_allocation * budget)
            w = w / w.sum() * budget
            w = np.clip(w, min_allocation * budget, max_allocation * budget)
            obj = np.dot(w, returns) - risk_aversion * (w @ cov_matrix @ w)
            if obj > best_obj:
                best_obj = obj
                best_w = w.copy()
        return best_obj, best_w

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
            cov_matrix = np.diag(stds**2)

        # Search for optimal allocation
        if n == 2:
            best_obj, best_weights = PortfolioOptimizer._grid_search_2d(
                returns,
                cov_matrix,
                budget,
                risk_aversion,
                min_allocation,
                max_allocation,
            )
        else:
            best_obj, best_weights = PortfolioOptimizer._random_search(
                returns,
                cov_matrix,
                budget,
                risk_aversion,
                n,
                min_allocation,
                max_allocation,
            )

        if best_weights is None:
            best_weights = np.full(n, budget / n)

        port_return = float(np.dot(best_weights, returns))
        port_risk = float(np.sqrt(best_weights @ cov_matrix @ best_weights))

        # Efficient frontier (vary risk_aversion)
        frontier = []
        for ra in RISK_AVERSION_GRID:
            if n == 2:
                _, best_w = PortfolioOptimizer._grid_search_2d(
                    returns,
                    cov_matrix,
                    budget,
                    ra,
                    min_allocation,
                    max_allocation,
                )
            else:
                _, best_w = PortfolioOptimizer._random_search(
                    returns,
                    cov_matrix,
                    budget,
                    ra,
                    n,
                    min_allocation,
                    max_allocation,
                )

            if best_w is not None:
                frontier.append(
                    {
                        "risk_aversion": ra,
                        "return": float(np.dot(best_w, returns)),
                        "risk": float(np.sqrt(best_w @ cov_matrix @ best_w)),
                        "allocations": dict(zip(names, best_w.tolist())),
                    }
                )

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

    def __init__(self, risk_aversion: float = 0.5):
        self.risk_aversion = risk_aversion

    def optimize_allocation(self, mc_results: Dict[str, Any], budget: float = 100.0) -> Dict[str, float]:
        result = self.optimize(mc_results, budget=budget, risk_aversion=self.risk_aversion)
        if "allocations" in result:
            return {k: round(v, 2) for k, v in result["allocations"].items()}
        return {}
