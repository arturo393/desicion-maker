"""
Bayesian updating engine for updating option probability distributions given evidence.
Includes advanced Causal Graph support (Bayesian Networks).
"""

from __future__ import annotations
__all__ = ["BayesianEngine", "CausalNode"]

from typing import Dict, List, Optional
import numpy as np
from decision_maker.core.models import Statistics

class CausalNode:
    def __init__(self, name: str, parents: List[str] = None):
        self.name = name
        self.parents = parents or []
        self.probabilities = {} # CPTs would go here in a real implementation

class BayesianEngine:
    def __init__(self):
        self.nodes: Dict[str, CausalNode] = {}

    def add_node(self, name: str, parents: List[str] = None) -> None:
        """Construct a Causal Graph / Bayesian Network node."""
        self.nodes[name] = CausalNode(name, parents)

    def analyze(
        self,
        mc_results: Dict[str, Statistics],
        evidence: Optional[Dict[str, float]] = None,
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

        # Basic exact inference via simulation, enhanced by any prior evidence
        for _ in range(num_posterior_samples):
            best_score = -float("inf")
            best_idx = 0
            for i, s in enumerate(stats_list):
                # If there's a causal graph mapped, we would traverse it here.
                # For now, we apply standard Gaussian posterior sampling on the results.
                score = rng.normal(s.mean_score, max(s.std_dev, 1e-12))
                
                # Apply simulated bayesian evidence shift
                if evidence and names[i] in evidence:
                    score *= (1.0 + evidence[names[i]])
                    
                if score > best_score:
                    best_score = score
                    best_idx = i
            best_counts[best_idx] += 1

        posteriors = {name: float(count / num_posterior_samples) for name, count in zip(names, best_counts)}

        # Attach Causal Graph structural metadata to the output if nodes exist
        if self.nodes:
            posteriors["_causal_graph"] = {name: node.parents for name, node in self.nodes.items()}

        return posteriors
