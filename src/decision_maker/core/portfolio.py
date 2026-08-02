import numpy as np
from typing import Dict, Any

class PortfolioOptimizer:
    def __init__(self, risk_aversion: float = 0.5):
        self.risk_aversion = risk_aversion

    def optimize_allocation(self, mc_results: Dict[str, Any], budget: float = 100.0) -> Dict[str, float]:
        """
        Calculates optimal percentage allocation across options using a mean-variance approach.
        Allocates 'budget' units across the available options.
        """
        options = list(mc_results.keys())
        if not options:
            return {}

        means = []
        stds = []
        for opt in options:
            stats = mc_results[opt]
            means.append(stats.mean_score)
            stds.append(max(stats.std_dev, 1e-9))
        
        means = np.array(means)
        stds = np.array(stds)
        
        # Normalize means to be positive for the sake of allocation weights
        min_mean = np.min(means)
        if min_mean < 0:
            means = means - min_mean + 1e-6
            
        # Fitness = Mean - Risk_Aversion * StdDev (simplified)
        fitness = means - (self.risk_aversion * stds)
        
        # Ensure fitness is positive for Softmax/proportional allocation
        min_fit = np.min(fitness)
        if min_fit < 0:
            fitness = fitness - min_fit + 1e-6
            
        # Softmax allocation
        exp_fit = np.exp(fitness / np.max(fitness))
        weights = exp_fit / np.sum(exp_fit)
        
        allocation = {opt: round(float(w * budget), 2) for opt, w in zip(options, weights)}
        return allocation
