#!/usr/bin/env python3
"""
Generic Decision Template
------------------------
Use this file to model any decision using the config-driven approach.
Option 1: Define your decision in decision_config.yaml
Option 2: Define factors/options inline below
"""

import asyncio

from python.core.config_runner import run_from_config
from python.core.models import DecisionOption, DistributionType, Factor
from python.core.orchestrator import UnifiedDecisionFramework


async def from_yaml():
    """Run from YAML config (recommended). Edit python/config/decision_config.yaml"""
    result = await run_from_config("python/config/decision_config.yaml")
    files = result.get("files", {})
    for fmt, path in files.items():
        print(f"{fmt.upper()}: {path}")


async def inline():
    """Define factors and options directly in code"""
    framework = UnifiedDecisionFramework()
    framework.mc_engine.num_simulations = 10000

    framework.add_factor(Factor("Cost", 0.4, maximize=False))
    framework.add_factor(Factor("ROI", 0.4, maximize=True))
    framework.add_factor(Factor("Risk", 0.2, maximize=False))

    opt_a = DecisionOption("Conservative Option", "Safe bet")
    opt_a.add_variable("Cost", DistributionType.DETERMINISTIC, 1000)
    opt_a.add_variable("ROI", DistributionType.NORMAL, 1.2, 0.1)
    opt_a.add_variable("Risk", DistributionType.DETERMINISTIC, 2)
    framework.add_option(opt_a)

    opt_b = DecisionOption("Aggressive Option", "High risk, high reward")
    opt_b.add_variable("Cost", DistributionType.TRIANGULAR, 800, 1200, 1500)
    opt_b.add_variable("ROI", DistributionType.NORMAL, 2.5, 0.8)
    opt_b.add_variable("Risk", DistributionType.UNIFORM, 5, 9)
    framework.add_option(opt_b)

    await framework.run_analysis(use_ai=False)


if __name__ == "__main__":
    import sys

    if "--yaml" in sys.argv or "-y" in sys.argv:
        asyncio.run(from_yaml())
    else:
        asyncio.run(inline())
