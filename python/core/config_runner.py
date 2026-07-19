from __future__ import annotations

__all__ = [
    "load_decision_config",
    "validate_config",
    "build_framework_from_config",
    "run_from_config",
]

import logging
import os
from typing import Any, Dict, Optional

import numpy as np
import yaml

from python.core.models import DecisionOption, DistributionType, Factor
from python.core.orchestrator import UnifiedDecisionFramework
from python.core.schemas import DecisionConfig, RootConfig
from python.core.utils import DISTRIBUTION_MAP

logger = logging.getLogger(__name__)


def load_decision_config(path: str) -> Dict[str, Any]:
    with open(path, "r") as f:
        return yaml.safe_load(f)


def validate_config(config: Dict[str, Any]) -> DecisionConfig:
    root = RootConfig.model_validate(config)
    return root.decision


def build_framework_from_config(config: Dict[str, Any]) -> UnifiedDecisionFramework:
    decision = validate_config(config)

    corr_matrix = None
    if decision.correlation is not None and len(decision.factors) > 1:
        off_diag = decision.correlation
        n = len(decision.factors)
        corr_matrix = np.full((n, n), off_diag)
        np.fill_diagonal(corr_matrix, 1.0)

    pref_types = [decision.promethee_pref_type] if decision.promethee_pref_type else None

    framework = UnifiedDecisionFramework(
        correlation_matrix=corr_matrix,
        promethee_pref_types=pref_types,
    )
    framework.mc_engine.num_simulations = decision.simulations

    for f_config in decision.factors:
        framework.add_factor(
            Factor(
                name=f_config.name,
                weight=f_config.weight,
                maximize=f_config.maximize,
                category=f_config.category,
            )
        )

    for opt_config in decision.options:
        option = DecisionOption(
            name=opt_config.name,
            description=opt_config.description,
        )
        for var_name, var_config in opt_config.variables.items():
            dist_type = DISTRIBUTION_MAP.get(var_config.distribution)
            if dist_type is None:
                logger.warning(f"Unknown distribution '{var_config.distribution}', using DETERMINISTIC")
                dist_type = DistributionType.DETERMINISTIC
            option.add_variable(var_name, dist_type, *var_config.params)
        framework.add_option(option)

    return framework


async def run_from_config(
    config_path: str,
    mode: str = "standard",
    use_ai: bool = False,
    results_dir: Optional[str] = None,
) -> Dict[str, Any]:
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")

    config = load_decision_config(config_path)
    decision = validate_config(config)

    framework = build_framework_from_config(config)

    return await framework.run_analysis(
        mode=decision.mode,
        use_ai=use_ai,
        results_dir=results_dir,
    )
