"""
Value of Information (VoI) calculations: EVPI and EVPPI.

What it does:
Calculates the Expected Value of Perfect Information (EVPI) and the Expected Value
of Partial Perfect Information (EVPPI) for risk drivers in decision models.
- EVPI: The maximum amount of score increase achievable by learning the true state
  of the world across all variables before committing to an option.
- EVPPI: The value of resolving uncertainty on a single shared risk driver before
  deciding, prioritizing which research or data collection to fund first.

How to use it:
from decision_maker.core.value_of_information import calculate_value_of_information

What it DOESN'T do:
Does not sample Monte Carlo draws or run multi-criteria rank aggregators.
"""

from __future__ import annotations

__all__ = [
    "DEFAULT_EVPPI_BINS",
    "MIN_SAMPLES_PER_BIN",
    "calculate_value_of_information",
]

import logging
from typing import TYPE_CHECKING, Any

import numpy as np

if TYPE_CHECKING:
    from decision_maker.core.models import Statistics

logger = logging.getLogger(__name__)

# Named constants to avoid magic numbers (per AGENTS.md conventions)
# DEFAULT_EVPPI_BINS = 20: partitions the continuous risk factor into 20 quantile bins
# (5% probability mass per bin). For typical Monte Carlo runs (N = 10,000), each bin contains
# ~500 draws, providing sufficient sample depth for stable conditional mean estimates
# while offering adequate granularity to resolve non-linear threshold effects.
DEFAULT_EVPPI_BINS: int = 20

# Minimum samples required per bin to prevent degenerate single-sample conditional means
MIN_SAMPLES_PER_BIN: int = 5

# Numerical tolerance for division by winner's mean score
EPSILON_DENOMINATOR: float = 1e-9


def calculate_value_of_information(
    mc_results: dict[str, Statistics],
    is_fully_shared: bool,
    drivers: dict[str, list[tuple[str, str]]],
    driver_samples: dict[str, np.ndarray] | None = None,
) -> dict[str, Any]:
    """Calculate EVPI and EVPPI by driver from Monte Carlo simulation results.

    Parameters:
        mc_results: Dictionary mapping option name to its Monte Carlo Statistics.
        is_fully_shared: Whether all variables across all options are bound to shared drivers.
        drivers: Dictionary mapping driver name to list of (option_name, variable_name) pairs.
        driver_samples: Optional dictionary mapping driver name to latent uniform draws (N,).
        num_bins: Number of quantile bins for EVPPI grouping (default DEFAULT_EVPPI_BINS).

    Returns:
        Dictionary containing EVPI, EVPPI by driver, and metadata.
    """
    if not mc_results or len(mc_results) < 2:
        return {
            "evpi": {
                "value": 0.0 if len(mc_results) == 1 else None,
                "fraction_of_winner_mean": 0.0 if len(mc_results) == 1 else None,
                "valid": len(mc_results) == 1,
                "reason": "Una sola opción: no hay decisión que cambiar con información" if len(mc_results) == 1 else "Sin opciones",
            },
            "evppi_by_driver": [],
            "winner_option": next(iter(mc_results.keys()), None),
            "winner_mean_score": float(next(iter(mc_results.values())).mean_score) if mc_results else 0.0,
        }

    # Extract score matrix S of shape (N, M)
    option_names = list(mc_results.keys())
    raws = [mc_results[name].raw_scores for name in option_names]
    if any(r is None for r in raws):  # checked on every option, not only the first
        return {
            "evpi": {
                "value": None,
                "fraction_of_winner_mean": None,
                "valid": False,
                "reason": "raw_scores no disponibles en Statistics",
            },
            "evppi_by_driver": [],
            "winner_option": None,
            "winner_mean_score": 0.0,
        }

    scores_matrix = np.column_stack([r for r in raws if r is not None])
    num_simulations, _num_options = scores_matrix.shape

    # Baseline prior best expected payoff: max_i mean_k(s_i(k))
    mean_scores_per_option = np.mean(scores_matrix, axis=0)
    baseline_expected_score = float(np.max(mean_scores_per_option))
    winner_idx = int(np.argmax(mean_scores_per_option))
    winner_name = option_names[winner_idx]

    # --- 1. Total EVPI ---
    # EVPI = mean_k(max_i s_i(k)) - max_i mean_k(s_i(k))
    # Valid only if the model is fully shared. If options are sampled independently, simulation k
    # does not represent the same scenario in option A as in option B, so taking max_i across
    # simulation draws would simply capitalize on independent sampling noise.
    if not is_fully_shared:
        evpi_value = None
        evpi_fraction = None
        evpi_valid = False
        evpi_reason = "las opciones se muestrean de forma independiente: el EVPI mediría ruido de muestreo, no información"
    else:
        max_score_per_scenario = np.max(scores_matrix, axis=1)
        expected_score_with_perfect_info = float(np.mean(max_score_per_scenario))
        # Ensure non-negativity against numerical float precision
        evpi_value = max(0.0, float(expected_score_with_perfect_info - baseline_expected_score))
        evpi_fraction = (
            float(evpi_value / baseline_expected_score)
            if abs(baseline_expected_score) > EPSILON_DENOMINATOR
            else 0.0
        )
        evpi_valid = True
        evpi_reason = "modelo totalmente compartido con escenarios comunes acoplados"

    # --- 2. EVPPI per Driver ---
    # EVPPI = mean_bins(max_i mean_{k in bin}(s_i(k))) - max_i mean_k(s_i(k))
    # Valid even if the model is not fully shared. Upward bias: the max of noisy per-bin means
    # exceeds the max of the true conditional means, so with independent (non-driver) noise
    # in the scores EVPPI reads slightly positive even for a worthless driver. The bias shrinks
    # as N grows (each bin holds N / bins draws); it is reported, not corrected.
    evppi_results: list[dict[str, Any]] = []

    for driver_name, usages in drivers.items():
        # Computed for every driver: one used only by a losing option can still be worth
        # knowing, if in some of its states that option would win.
        opts_using_driver = {opt_name for opt_name, _var in usages}

        # Retrieve realization vector of the driver
        driver_vals: np.ndarray | None = None
        if driver_samples and driver_name in driver_samples:
            driver_vals = driver_samples[driver_name]
        else:
            # Fall back to raw_factor_data of the first option using this driver
            for opt_name, var_name in usages:
                opt_stats = mc_results.get(opt_name)
                if opt_stats and opt_stats.raw_factor_data and var_name in opt_stats.raw_factor_data:
                    driver_vals = opt_stats.raw_factor_data[var_name]
                    break

        if driver_vals is None or len(driver_vals) != num_simulations:
            evppi_results.append({
                "driver": driver_name,
                "evppi": 0.0,
                "evppi_fraction_of_winner_mean": 0.0,
                "valid": False,
                "reason": "No se encontraron muestras realizadas para el driver",
                "options": sorted(opts_using_driver),
            })
            continue

        # Quantile binning: partition simulations into bins by quantiles of driver_vals
        actual_bins = max(2, min(DEFAULT_EVPPI_BINS, num_simulations // MIN_SAMPLES_PER_BIN))
        sort_idx = np.argsort(driver_vals)
        bin_assignments = np.empty(num_simulations, dtype=int)
        bin_step = num_simulations / actual_bins
        for b in range(actual_bins):
            start = int(b * bin_step)
            end = int((b + 1) * bin_step) if b < actual_bins - 1 else num_simulations
            bin_assignments[sort_idx[start:end]] = b

        # Conditional expectation per bin
        weighted_bin_max = 0.0
        for b in range(actual_bins):
            mask = (bin_assignments == b)
            bin_size = int(np.sum(mask))
            if bin_size == 0:
                continue
            bin_scores = scores_matrix[mask, :]
            # Conditional mean score for each option in bin b: mean_{k in bin}(s_i(k))
            cond_means = np.mean(bin_scores, axis=0)
            best_in_bin = float(np.max(cond_means))
            bin_weight = bin_size / num_simulations
            weighted_bin_max += bin_weight * best_in_bin

        raw_evppi = max(0.0, float(weighted_bin_max - baseline_expected_score))
        # EVPPI cannot exceed EVPI in theory; clip against numerical bin approximation if EVPI is valid
        if evpi_value is not None:
            raw_evppi = min(raw_evppi, evpi_value)

        evppi_frac = (
            float(raw_evppi / baseline_expected_score)
            if abs(baseline_expected_score) > EPSILON_DENOMINATOR
            else 0.0
        )

        evppi_results.append({
            "driver": driver_name,
            "evppi": raw_evppi,
            "evppi_fraction_of_winner_mean": evppi_frac,
            "valid": True,
            "reason": f"Calculado con {actual_bins} bins cuantílicos",
            "options": sorted(opts_using_driver),
        })

    # Sort drivers descending by EVPPI to answer "what risk factor is most valuable to investigate first"
    evppi_results.sort(key=lambda d: d["evppi"], reverse=True)

    return {
        "evpi": {
            "value": evpi_value,
            "fraction_of_winner_mean": evpi_fraction,
            "valid": evpi_valid,
            "reason": evpi_reason,
        },
        "evppi_by_driver": evppi_results,
        "winner_option": winner_name,
        "winner_mean_score": baseline_expected_score,
    }
