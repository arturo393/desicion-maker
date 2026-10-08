"""
Shared scenario drivers for coupling uncertainties across decision options.

What it does:
Implements comonotonic coupling for decision options that share underlying
real-world risk factors (e.g. macro inflation, market demand, regulatory shock).
Each variable bound to the same driver maintains its exact marginal empirical
distribution while aligning its rank order comonotonically across simulations.

How to use it:
from decision_maker.core.scenarios import (
    apply_shared_drivers,
    collect_drivers,
    is_fully_shared_model,
)

What it DOESN'T do:
Does not evaluate decision criteria, compute payoffs, or perform outranking.
"""

from __future__ import annotations

__all__ = [
    "apply_shared_drivers",
    "collect_drivers",
    "is_fully_shared_model",
]

import logging
from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from decision_maker.core.models import DecisionOption

logger = logging.getLogger(__name__)


def collect_drivers(options: list[DecisionOption]) -> dict[str, list[tuple[str, str]]]:
    """Map driver names to the list of (option_name, variable_name) pairs using them."""
    drivers_map: dict[str, list[tuple[str, str]]] = {}
    for opt in options:
        for v_name, var in opt.variables.items():
            if var.driver is not None and len(var.driver.strip()) > 0:
                drivers_map.setdefault(var.driver.strip(), []).append((opt.name, v_name))
    return drivers_map


def is_fully_shared_model(options: list[DecisionOption]) -> bool:
    """Return True if every variable in every option is bound to a shared driver.

    When all variables have an assigned driver, every simulation index k corresponds
    to a coherent, synchronized scenario of the world across all options, making
    pointwise comparisons (such as scenario-level Minimax Regret and EVPI) valid.
    """
    if not options:
        return False
    return all(
        len(opt.variables) > 0
        and all(var.driver is not None and len(var.driver.strip()) > 0 for var in opt.variables.values())
        for opt in options
    )


def apply_shared_drivers(
    sampled_data: dict[str, dict[str, np.ndarray]],
    options: list[DecisionOption],
    num_simulations: int,
    rng: np.random.Generator,
) -> tuple[dict[str, dict[str, np.ndarray]], dict[str, np.ndarray]]:
    """Couple variables sharing the same driver via comonotonic rank ordering.

    COMONOTONICITY ASSUMPTION (Rank correlation = 1.0):
    For each distinct driver, a common latent standard uniform vector U ~ Uniform(0, 1)
    of length N is drawn using the seeded run generator. The empirical samples of every
    variable associated with this driver are reordered such that the k-th smallest sample
    value occupies the position of the k-th smallest uniform draw (order_u[k]).
    This guarantees:
      1. Marginal invariance: sorting the reordered array yields the identical sequence
         of values as the original marginal sample, strictly preserving the marginal
         probability distribution, moments, and support.
      2. Perfect positive rank correlation: any two variables sharing the same driver
         have Spearman rank correlation = 1.0 across all N simulations. They rise and
         fall together in every scenario.

    STRONG ASSUMPTION & WHEN IT DOES NOT APPLY:
    Comonotonicity assumes perfect positive monotonic dependence between all variables
    governed by the risk factor. It is a strong modeling assumption and does NOT apply when:
      - Hedging or counter-cyclical relationships exist: e.g. an operating cost and a hedging
        contract that move in opposite directions (rank correlation -1.0), unless explicitly
        inverted or parameterized.
      - Idiosyncratic basis risk is substantial: e.g. two competing firms subjected to the same
        macroeconomic shock whose firm-specific execution noise dilutes common correlation.
      - Asymmetric tail dependence or non-monotonic relationships: e.g. copula structures
        (Clayton, Gumbel) where correlation concentrates strictly in the downside or upside.

    Parameters:
        sampled_data: Dict mapping option_name -> {variable_name: np.ndarray of shape (N,)}.
        options: List of DecisionOption definitions.
        num_simulations: Total number of Monte Carlo draws N.
        rng: The seeded numpy random Generator of the run.

    Returns:
        tuple (coupled_sampled_data, driver_uniforms_dict)
    """
    drivers_map = collect_drivers(options)
    if not drivers_map:
        # Zero regression guarantee: models without drivers draw zero extra random numbers,
        # ensuring exact reproducibility with legacy unshared Monte Carlo runs.
        return sampled_data, {}

    # Deterministic iteration: sort driver names alphabetically so RNG draws are reproducible
    sorted_drivers = sorted(drivers_map.keys())
    driver_uniforms: dict[str, np.ndarray] = {}

    for driver_name in sorted_drivers:
        # Draw the common latent state of the world for this driver
        u = rng.uniform(0.0, 1.0, size=num_simulations)
        driver_uniforms[driver_name] = u
        order_u = np.argsort(u)

        for opt_name, var_name in drivers_map[driver_name]:
            if opt_name in sampled_data and var_name in sampled_data[opt_name]:
                original = sampled_data[opt_name][var_name]
                sorted_vals = np.sort(original)
                # Assign sorted values to positions corresponding to the rank order of u.
                # The k-th smallest uniform position order_u[k] receives the k-th smallest
                # value of the variable, aligning quantiles identically across options.
                reordered = np.empty_like(original)
                reordered[order_u] = sorted_vals
                sampled_data[opt_name][var_name] = reordered

    return sampled_data, driver_uniforms
