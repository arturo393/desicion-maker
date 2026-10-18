"""
Pipeline steps of UnifiedDecisionFramework.run_analysis: input building, PROMETHEE under uncertainty, advanced pass, plots.
Usage: internal to core/orchestrator.py — each step takes the framework (`fw`) or plain data, never global state.
Does NOT: decide the order of the pipeline or assemble the result dict (orchestrator.run_analysis does).
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

import numpy as np
import pandas as pd

from decision_maker.core.bootstrap import BootstrapConfig
from decision_maker.core.models import Factor, Statistics
from decision_maker.core.promethee import PrometheeConfig, PrometheeEngine
from decision_maker.core.utils import DEFAULT_BOOTSTRAP_ITERATIONS, RANGE_AMPLIFICATION_THRESHOLD
from decision_maker.core.visualization import PlotContext

if TYPE_CHECKING:
    from decision_maker.core.orchestrator import UnifiedDecisionFramework

logger = logging.getLogger(__name__)

# Offset added to mc_engine.seed to generate an independent pseudorandom stream for bootstrap
BOOTSTRAP_SEED_OFFSET: int = 1
# Own stream for the weight draws, so adding them leaves every other seeded result unchanged.
WEIGHT_SEED_OFFSET: int = 2


@dataclass
class AdvancedAnalysis:
    """Bundles data needed for advanced mode analyses (Parameter Object)."""

    mc_results: dict
    factor_names: list[str]
    weights: list[float]
    max_bools: list[bool]
    data_fuzzy: dict
    future_metrics: dict[str, Any]
    topsis_scores: Any


def _normalize_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Min-max normalize each column to [0, 1]."""
    result = df.copy()
    for col in df.columns:
        cmin, cmax = df[col].min(), df[col].max()
        if cmax > cmin:
            result[col] = (df[col] - cmin) / (cmax - cmin)
        else:
            result[col] = 0.5
    return result


def _check_range_amplification(factors: list[Factor], mc_results: dict) -> None:
    """Warn when options barely differ on a factor that still carries its full weight.

    Min-max normalization stretches whatever gap exists to [0, 1]: $3,000 vs $3,100 counts as much as
    $3,000 vs $9,000. A weight typed without looking at the range then overstates a trivial
    difference. The cure is to weight the swing (weight_derivation.swing_weights), not to rescale.
    """
    for f in factors:
        means = [st.factor_stats[f.name]["mean"] for st in mc_results.values() if f.name in st.factor_stats]
        if len(means) < 2:
            continue
        gap = max(means) - min(means)
        magnitude = max(abs(m) for m in means)
        if gap > 0 and magnitude > 0 and gap / magnitude < RANGE_AMPLIFICATION_THRESHOLD:
            logger.warning(
                f"'{f.name}' differs only {gap / magnitude:.1%} between options, yet min-max gives that gap "
                f"its full weight ({f.weight}). Check the weight against this range (swing weighting)."
            )


def _promethee_with_uncertainty(
    engine: PrometheeEngine,
    mc_results: dict,
    config: PrometheeConfig,
    factor_names: list[str],
) -> pd.Series:
    def _df_for_percentile(key: str) -> pd.DataFrame:
        rows = {}
        for name, stats in mc_results.items():
            row = {}
            for fn in factor_names:
                if fn in stats.factor_stats:
                    row[fn] = stats.factor_stats[fn][key]
            if row:
                rows[name] = row
        return pd.DataFrame.from_dict(rows, orient="index") if rows else pd.DataFrame()

    all_scores = []
    for _label, key in [("p5", "p5"), ("mean", "mean"), ("p95", "p95")]:
        df = _df_for_percentile(key)
        if df.empty:
            continue
        df = _normalize_dataframe(df)
        scores = engine.analyze(df, config)
        all_scores.append(scores)
    if not all_scores:
        return pd.Series()
    all_opts = list({opt for s in all_scores for opt in s.index})
    avg_scores = {opt: float(np.mean([s.get(opt, 0) for s in all_scores])) for opt in all_opts}
    return pd.Series(avg_scores).sort_values(ascending=False)


def _analyze_uncertainty(fw: UnifiedDecisionFramework, mc_results: dict[str, Statistics]) -> dict[str, Any]:
    """Confidence-weighted winner + bootstrap ranking confidence intervals."""
    from decision_maker.core.uncertainty import confidence_weighted_winner, ranking_confidence

    return {
        "confidence_weighted_winner": confidence_weighted_winner(mc_results),
        "ranking_confidence": ranking_confidence(mc_results, seed=fw.mc_engine.seed),
    }


def _generate_plots(
    fw: UnifiedDecisionFramework,
    saved: dict[str, Any],
    mc_results: dict[str, Statistics],
    future_metrics: dict[str, Any],
) -> list[str]:
    """Generate the plot suite for standard/advanced modes."""
    return fw.viz_engine.generate_all_plots(
        PlotContext(
            mc_results=mc_results,
            factors=fw.mc_engine.factors,
            future_metrics=future_metrics,
            output_dir=os.path.dirname(saved["json"]),
            timestamp=saved["timestamp"],
        )
    )

def _build_analysis_inputs(
    mc_results: dict[str, Statistics], factors: list[Factor]
) -> tuple[dict[str, dict[str, tuple[float, float, float]]], list[float], list[bool], list[str]]:
    """Build fuzzy decision matrix and extract weights/directions from factors."""
    data_fuzzy: dict[str, dict[str, tuple[float, float, float]]] = {}
    for name, stats in mc_results.items():
        data_fuzzy[name] = {}
        for factor_name, f_stats in stats.factor_stats.items():
            data_fuzzy[name][factor_name] = (f_stats["p5"], f_stats["mean"], f_stats["p95"])

    weights = []
    max_bools = []
    first_opt = list(data_fuzzy.values())[0]
    factor_names = list(first_opt.keys())
    for col in factor_names:
        f = next((f for f in factors if f.name == col), None)
        weights.append(f.weight if f else 1.0)
        max_bools.append(f.maximize if f else True)

    return data_fuzzy, weights, max_bools, factor_names

def _add_advanced_engine_metrics(
    fw: UnifiedDecisionFramework, future_metrics: dict[str, Any], mc_results: dict[str, Statistics]) -> None:
    """Populate advanced-mode metrics: game theory, real options, surrogate, portfolio."""
    future_metrics["game_theory"] = fw.game_theory_engine.analyze(mc_results)
    future_metrics["real_options"] = fw.roa_engine.analyze(mc_results)
    future_metrics["ml_surrogate"] = fw.ml_surrogate_engine.analyze(mc_results, fw.mc_engine.factors)
    future_metrics["portfolio_allocation"] = fw.portfolio_optimizer.optimize_allocation(mc_results)

def _run_advanced_analysis(fw: UnifiedDecisionFramework, ctx: AdvancedAnalysis) -> None:
    """Run advanced mode analyses: crisp PROMETHEE, bootstrap, Bayesian, genetic."""
    mc_results = ctx.mc_results
    weights = ctx.weights
    max_bools = ctx.max_bools
    data_fuzzy = ctx.data_fuzzy
    future_metrics = ctx.future_metrics
    topsis_scores = ctx.topsis_scores

    data_crisp = {}
    for name, stats in mc_results.items():
        data_crisp[name] = {f_name: stats.factor_stats[f_name]["mean"] for f_name in stats.factor_stats}
    df_crisp = pd.DataFrame.from_dict(data_crisp, orient="index")
    if not df_crisp.empty:
        df_crisp = _normalize_dataframe(df_crisp)

    promethee_scores = fw.promethee_engine.analyze(

        df_crisp,
        PrometheeConfig(
            weights=weights,
            maximize=max_bools,
            pref_types=fw.promethee_pref_types,
            pref_params=fw.promethee_pref_params,
        ),
    )

    rankings_advanced: dict[str, pd.Series] = {
        "TOPSIS": topsis_scores,
        "MC": pd.Series({n: s.mean_score for n, s in mc_results.items()}).sort_values(ascending=False),
    }
    if not promethee_scores.empty:
        rankings_advanced["PROMETHEE"] = promethee_scores
    prom_uncert = future_metrics.get("promethee_uncertainty", pd.Series())
    if not prom_uncert.empty:
        rankings_advanced["PROMETHEE_uncertainty"] = prom_uncert
    borda_advanced = fw.aggregator.aggregate(rankings_advanced, method="borda")

    # Derive an independent seed for bootstrap perturbations so that noise draws
    # do not correlate with the Monte Carlo simulation sequence.
    bootstrap_seed = (
        fw.mc_engine.seed + BOOTSTRAP_SEED_OFFSET
        if fw.mc_engine.seed is not None
        else None
    )
    bootstrap_ci = fw.bootstrap_engine.confidence_intervals(
        data_fuzzy,
        BootstrapConfig(
            weights=weights,
            maximize=max_bools,
            n_bootstrap=DEFAULT_BOOTSTRAP_ITERATIONS,
            seed=bootstrap_seed,
        ),
        seed=bootstrap_seed,
    )

    future_metrics.update(
        {
            "bayesian_probs": fw.bayes_engine.analyze(mc_results),
            "ideal_option": fw.gen_engine.evolve_ideal(mc_results, fw.mc_engine.factors),
            "promethee_scores": promethee_scores,
            "rank_aggregation": borda_advanced,
            "bootstrap_ci": bootstrap_ci,
        }
    )
