from __future__ import annotations

__all__ = ["UnifiedDecisionFramework"]

import asyncio
import logging
import os
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

from python.core.models import DecisionOption, Factor
from python.core.utils import (
    SCALE_MISMATCH_THRESHOLD, DEFAULT_BOOTSTRAP_ITERATIONS,
)
from python.core.monte_carlo import MonteCarloEngine
from python.core.topsis import TOPSISEngine
from python.core.promethee import PrometheeEngine
from python.core.pareto import ParetoEngine
from python.core.sensitivity import SensitivityEngine
from python.core.bayesian import BayesianEngine
from python.core.genetic import GeneticOptimizer
from python.core.decision_theory import DecisionTheoryEngine
from python.core.gemini_agent import GeminiDeepResearchAgent
from python.core.robust import RobustOptimizer
from python.core.aggregator import RankAggregator
from python.core.bootstrap import BootstrapRanking
from python.core.information_theory import InformationTheoryEngine
from python.core.visualization import VisualizationEngine
from python.core.explainability import ExplainabilityEngine
from python.core.antifragile import AntifragileEngine

logger = logging.getLogger(__name__)


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


def _check_scale_mismatch(factors: List[Factor], mc_results: Dict) -> None:
    factor_names = [f.name for f in factors]
    means_per_factor: Dict[str, List[float]] = {fn: [] for fn in factor_names}
    for stats in mc_results.values():
        for fn in factor_names:
            if fn in stats.factor_stats:
                means_per_factor[fn].append(stats.factor_stats[fn]["mean"])
    avg_means = {fn: abs(np.mean(v)) if v else 0.0 for fn, v in means_per_factor.items()}
    max_mean = max(avg_means.values()) if avg_means else 0.0
    for fn, avg in avg_means.items():
        if max_mean > 0 and avg > 0 and max_mean / avg > SCALE_MISMATCH_THRESHOLD:
            logger.warning(
                f"Scale mismatch: '{fn}' avg={avg:.2f} vs max factor avg={max_mean:.2f} "
                f"(ratio={max_mean/avg:.1f}x). Consider rescaling factors so weights reflect true importance."
            )


def _promethee_with_uncertainty(
    engine: PrometheeEngine,
    mc_results: Dict,
    factor_names: List[str],
    weights: List[float],
    max_bools: List[bool],
    pref_types: Optional[List[str]] = None,
    pref_params: Optional[List[dict]] = None,
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
    for label, key in [("p5", "p5"), ("mean", "mean"), ("p95", "p95")]:
        df = _df_for_percentile(key)
        if df.empty:
            continue
        df = _normalize_dataframe(df)
        scores = engine.analyze(df, weights, max_bools, pref_types=pref_types, pref_params=pref_params)
        all_scores.append(scores)
    if not all_scores:
        return pd.Series()
    all_opts = list({opt for s in all_scores for opt in s.index})
    avg_scores = {opt: float(np.mean([s.get(opt, 0) for s in all_scores])) for opt in all_opts}
    return pd.Series(avg_scores).sort_values(ascending=False)


class UnifiedDecisionFramework:
    def __init__(
        self,
        correlation_matrix: Optional[np.ndarray] = None,
        promethee_pref_types: Optional[List[str]] = None,
        promethee_pref_params: Optional[List[dict]] = None,
    ):
        self.mc_engine = MonteCarloEngine(correlation_matrix=correlation_matrix)
        self.topsis_engine = TOPSISEngine()
        self.promethee_engine = PrometheeEngine()
        self.dt_engine = DecisionTheoryEngine()
        self.pareto_engine = ParetoEngine()
        self.sens_engine = SensitivityEngine()
        self.bayes_engine = BayesianEngine()
        self.gen_engine = GeneticOptimizer()
        self.ai_agent = GeminiDeepResearchAgent()
        self.robust_engine = RobustOptimizer()
        self.aggregator = RankAggregator()
        self.bootstrap_engine = BootstrapRanking()
        self.info_theory_engine = InformationTheoryEngine()
        self.viz_engine = VisualizationEngine()
        self.explain_engine = ExplainabilityEngine()
        self.antifragile_engine = AntifragileEngine()
        self.promethee_pref_types = promethee_pref_types
        self.promethee_pref_params = promethee_pref_params

    def add_option(self, option: DecisionOption) -> None:
        errors = []
        for var_name, var in option.variables.items():
            errors.extend(var.validate())
        if errors:
            for e in errors:
                logger.warning(f"Validation warning for '{option.name}': {e}")
        self.mc_engine.add_option(option)

    def add_factor(self, factor: Factor) -> None:
        self.mc_engine.add_factor(factor)

    async def run_analysis(
        self,
        mode: str = "standard",
        use_ai: bool = False,
        results_dir: Optional[str] = None,
    ) -> Dict[str, Any]:
        if mode not in ("express", "standard", "advanced"):
            logger.warning(f"Unknown mode '{mode}', falling back to 'standard'")
            mode = "standard"

        logger.info(f"Starting analysis in {mode.upper()} mode")

        mc_results = self.mc_engine.run()
        if not mc_results:
            logger.warning("No results from Monte Carlo engine")
            return {}

        _check_scale_mismatch(self.mc_engine.factors, mc_results)

        data_fuzzy, weights, max_bools, factor_names = self._build_analysis_inputs(mc_results)

        topsis_scores = self.topsis_engine.analyze(data_fuzzy, weights, max_bools) if data_fuzzy else pd.Series()
        pareto_results = self.pareto_engine.analyze(mc_results, self.mc_engine.factors)
        strategies = {}
        sensitivity_results = {}
        future_metrics: Dict[str, Any] = {}

        if mode in ("standard", "advanced"):
            strategies = self.dt_engine.analyze(mc_results)
            sensitivity_results = self.sens_engine.analyze(mc_results, self.mc_engine.factors)

            promethee_uncertainty = _promethee_with_uncertainty(
                self.promethee_engine, mc_results, factor_names,
                weights, max_bools,
                pref_types=self.promethee_pref_types,
                pref_params=self.promethee_pref_params,
            )

            robust = self.robust_engine.analyze(mc_results, self.mc_engine.factors)
            info_theory = self.info_theory_engine.analyze(mc_results, self.mc_engine.factors)

            rankings: Dict[str, pd.Series] = {
                "TOPSIS": topsis_scores,
                "MC": pd.Series({n: s.mean_score for n, s in mc_results.items()}).sort_values(ascending=False),
            }
            if not promethee_uncertainty.empty:
                rankings["PROMETHEE_uncertainty"] = promethee_uncertainty
            borda = self.aggregator.aggregate(rankings, method="borda")

            future_metrics = {
                "promethee_uncertainty": promethee_uncertainty,
                "robust_optimizer": robust,
                "info_theory": info_theory,
                "rank_aggregation": borda,
            }

        if mode == "advanced":
            self._run_advanced_analysis(mc_results, factor_names, weights, max_bools, data_fuzzy, future_metrics, topsis_scores)

        waterfall = self.explain_engine.factor_waterfall(mc_results, self.mc_engine.factors)
        counterfactual = self.explain_engine.counterfactual(mc_results, self.mc_engine.factors)
        explanation = self.explain_engine.narrative(
            mc_results, self.mc_engine.factors,
            waterfall, counterfactual, topsis_scores, mode, use_ai=False,
        )

        antifragile = self.antifragile_engine.analyze(mc_results, self.mc_engine.factors)

        ai_reports = {}
        if use_ai and self.ai_agent.is_available:
            tasks = [self.ai_agent.research(opt.name, opt.description) for opt in self.mc_engine.options]
            results = await asyncio.gather(*tasks)
            for opt, res in zip(self.mc_engine.options, results):
                ai_reports[opt.name] = res

        from python.core.reporting import print_report, save_report, ReportData

        report_data = ReportData(
            mode=mode, mc_results=mc_results, topsis_scores=topsis_scores,
            strategies=strategies, pareto=pareto_results, sensitivity=sensitivity_results,
            future=future_metrics, ai_reports=ai_reports, factors=self.mc_engine.factors,
            explanation=explanation,
        )

        print_report(report_data)
        saved = save_report(
            mode, mc_results, topsis_scores, strategies,
            pareto_results, sensitivity_results, future_metrics,
            ai_reports, self.mc_engine.factors, results_dir,
            explanation=explanation,
            waterfall=waterfall,
            counterfactual=counterfactual,
        )

        if mode in ("standard", "advanced"):
            timestamp = saved["timestamp"]
            plots = self.viz_engine.generate_all_plots(
                mc_results, self.mc_engine.factors, future_metrics,
                os.path.dirname(saved["json"]), timestamp
            )
            saved["plots"] = plots

        return {
            "mode": mode,
            "mc_results": mc_results,
            "topsis_scores": topsis_scores,
            "strategies": strategies,
            "pareto": pareto_results,
            "sensitivity": sensitivity_results,
            "future": future_metrics,
            "ai_reports": ai_reports,
            "files": saved,
            "explanation": explanation,
            "waterfall": waterfall,
            "counterfactual": counterfactual,
            "antifragile": antifragile,
            "factors": self.mc_engine.factors,
        }

    def _build_analysis_inputs(self, mc_results):
        """Build fuzzy decision matrix and extract weights/directions from factors."""
        data_fuzzy = {}
        for name, stats in mc_results.items():
            data_fuzzy[name] = {}
            for factor_name, f_stats in stats.factor_stats.items():
                data_fuzzy[name][factor_name] = (f_stats["p5"], f_stats["mean"], f_stats["p95"])

        weights = []
        max_bools = []
        first_opt = list(data_fuzzy.values())[0]
        factor_names = list(first_opt.keys())
        for col in factor_names:
            f = next((f for f in self.mc_engine.factors if f.name == col), None)
            weights.append(f.weight if f else 1.0)
            max_bools.append(f.maximize if f else True)

        return data_fuzzy, weights, max_bools, factor_names

    def _run_advanced_analysis(self, mc_results, factor_names, weights, max_bools, data_fuzzy, future_metrics, topsis_scores):
        """Run advanced mode analyses: crisp PROMETHEE, bootstrap, Bayesian, genetic."""
        data_crisp = {}
        for name, stats in mc_results.items():
            data_crisp[name] = {f_name: stats.factor_stats[f_name]["mean"] for f_name in stats.factor_stats}
        df_crisp = pd.DataFrame.from_dict(data_crisp, orient="index")

        promethee_scores = self.promethee_engine.analyze(
            df_crisp, weights, max_bools,
            pref_types=self.promethee_pref_types,
            pref_params=self.promethee_pref_params,
        )

        rankings_advanced: Dict[str, pd.Series] = {
            "TOPSIS": topsis_scores,
            "MC": pd.Series({n: s.mean_score for n, s in mc_results.items()}).sort_values(ascending=False),
        }
        if not promethee_scores.empty:
            rankings_advanced["PROMETHEE"] = promethee_scores
        prom_uncert = future_metrics.get("promethee_uncertainty", pd.Series())
        if not prom_uncert.empty:
            rankings_advanced["PROMETHEE_uncertainty"] = prom_uncert
        borda_advanced = self.aggregator.aggregate(rankings_advanced, method="borda")

        bootstrap_ci = self.bootstrap_engine.confidence_intervals(
            data_fuzzy, weights, max_bools, n_bootstrap=DEFAULT_BOOTSTRAP_ITERATIONS,
        )

        future_metrics.update({
            "bayesian_probs": self.bayes_engine.analyze(mc_results),
            "ideal_option": self.gen_engine.evolve_ideal(mc_results, self.mc_engine.factors),
            "promethee_scores": promethee_scores,
            "rank_aggregation": borda_advanced,
            "bootstrap_ci": bootstrap_ci,
        })
