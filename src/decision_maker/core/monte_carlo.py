"""
Monte Carlo simulation engine sampling uncertain variables across decision options.
Uses the Rust `decision_maker_core` native extension for maximum performance.
"""

from __future__ import annotations

__all__ = ["MonteCarloEngine"]

import json
import logging
from typing import Dict, List, Optional
import numpy as np

from decision_maker_core import MonteCarloEngine as RustMonteCarloEngine
from decision_maker.core.models import DecisionOption, Factor, Statistics

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
        
        # Initialize the Rust Native Engine
        self._rust_engine = RustMonteCarloEngine()

    def add_factor(self, factor: Factor) -> None:
        self.factors.append(factor)

    def add_option(self, option: DecisionOption) -> None:
        if option.name in self._option_names:
            logger.warning(f"Duplicate option name '{option.name}' — previous will be overwritten")
        self._option_names.add(option.name)
        self.options.append(option)

    def run(self, normalize: bool = True) -> Dict[str, Statistics]:
        if not self.options or not self.factors:
            return {}

        logger.info(f"Delegating {self.num_simulations} Monte Carlo simulations to Rust Core Engine...")

        # 1. Serialize definitions to JSON for Rust
        payload = {
            "num_simulations": self.num_simulations,
            "factors": [
                {"name": f.name, "weight": f.weight, "maximize": f.maximize}
                for f in self.factors
            ],
            "options": [
                {
                    "name": opt.name,
                    "variables": {
                        v_name: {"dist_type": v.dist_type.value, "params": v.params}
                        for v_name, v in opt.variables.items()
                    }
                }
                for opt in self.options
            ]
        }
        
        json_payload = json.dumps(payload)

        # 2. Execute Rust Engine
        try:
            results_json = self._rust_engine.run_simulation(json_payload)
            raw_results = json.loads(results_json)
        except Exception as e:
            logger.error(f"Rust Engine Execution Failed: {e}")
            return {}

        # 3. Deserialize Rust JSON back into Pydantic Statistics models
        results: Dict[str, Statistics] = {}
        for opt_name, stats_dict in raw_results.items():
            stats = Statistics(
                option_name=stats_dict["option_name"],
                mean_score=stats_dict["mean_score"],
                std_dev=stats_dict["std_dev"],
                min_score=stats_dict["min_score"],
                max_score=stats_dict["max_score"],
                percentile_5=stats_dict["percentile_5"],
                percentile_95=stats_dict["percentile_95"],
                success_rate=stats_dict["success_rate"],
                factor_stats=stats_dict["factor_stats"],
                var_95=stats_dict["var_95"],
                cvar_95=stats_dict["cvar_95"],
                raw_scores=np.array([]), # TODO: Send full arrays from Rust if needed for Explainability
                raw_factor_data={},
            )
            results[opt_name] = stats

        return results
