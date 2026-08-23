"""
Unified orchestrator coordinating multi-criteria algorithms and execution pipelines.
Usage: from decision_maker.core.orchestrator import UnifiedDecisionFramework
Does NOT: Implement individual algorithm logic directly.
"""

from __future__ import annotations

__all__ = ["UnifiedDecisionFramework"]

import asyncio
import logging
import os
from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd

from decision_maker.core.adaptive_router import AdaptiveRouter
from decision_maker.core.aggregator import RankAggregator
from decision_maker.core.antifragile import AntifragileEngine
from decision_maker.core.bayesian import BayesianEngine
from decision_maker.core.bootstrap import BootstrapConfig, BootstrapRanking
from decision_maker.core.calibration_scorer import CalibrationScorer
from decision_maker.core.decision_journal import DecisionJournal
from decision_maker.core.decision_theory import DecisionTheoryEngine
from decision_maker.core.ergodicity import ErgodicityAnalyzer
from decision_maker.core.explainability import ExplainabilityEngine, NarrativeContext
from decision_maker.core.game_theory import GameTheoryEngine
from decision_maker.core.gemini_agent import GeminiDeepResearchAgent
from decision_maker.core.genetic import GeneticOptimizer
from decision_maker.core.information_theory import InformationTheoryEngine
from decision_maker.core.kelly import KellyCriterionEngine
from decision_maker.core.ml_surrogate import MLSurrogateEngine
from decision_maker.core.models import DecisionOption, Factor, Statistics
from decision_maker.core.monte_carlo import MonteCarloEngine
from decision_maker.core.outcome_tracker import OutcomeTracker
from decision_maker.core.pareto import ParetoEngine
from decision_maker.core.portfolio import PortfolioOptimizer
from decision_maker.core.promethee import PrometheeConfig, PrometheeEngine
from decision_maker.core.roa import RealOptionsEngine
from decision_maker.core.robust import RobustOptimizer
from decision_maker.core.sensitivity import SensitivityEngine
from decision_maker.core.topsis import TOPSISEngine
from decision_maker.core.utils import (
    DEFAULT_BOOTSTRAP_ITERATIONS,
    SCALE_MISMATCH_THRESHOLD,
)
from decision_maker.core.visualization import PlotContext, VisualizationEngine

logger = logging.getLogger(__name__)


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


def _check_scale_mismatch(factors: list[Factor], mc_results: dict) -> None:
    factor_names = [f.name for f in factors]
    means_per_factor: dict[str, list[float]] = {fn: [] for fn in factor_names}
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
                f"(ratio={max_mean / avg:.1f}x). Consider rescaling factors so weights reflect true importance."
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


class UnifiedDecisionFramework:
    def __init__(
        self,
        correlation_matrix: np.ndarray | None = None,
        promethee_pref_types: list[str] | None = None,
        promethee_pref_params: list[dict] | None = None,
        session_id: str | None = None,
    ):
        self.session_id = session_id
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
        self.game_theory_engine = GameTheoryEngine()
        self.roa_engine = RealOptionsEngine()
        self.ml_surrogate_engine = MLSurrogateEngine()
        self.portfolio_optimizer = PortfolioOptimizer()
        self.ergodicity_engine = ErgodicityAnalyzer()
        self.kelly_engine = KellyCriterionEngine()
        self.outcome_tracker = OutcomeTracker()
        self.calibration_scorer = CalibrationScorer()
        self.decision_journal = DecisionJournal()
        self.adaptive_router = AdaptiveRouter()
        self.promethee_pref_types = promethee_pref_types
        self.promethee_pref_params = promethee_pref_params

    def add_option(self, option: DecisionOption) -> None:
        self.mc_engine.add_option(option)

    def add_factor(self, factor: Factor) -> None:
        self.mc_engine.add_factor(factor)

    def save_session(self, name: str, description: str = "") -> str:

        from decision_maker.core.db import create_session
        from decision_maker.core.db_models import AnalysisSession

        factors_json = [f.model_dump() for f in self.mc_engine.factors]
        options_json = [o.model_dump() for o in self.mc_engine.options]

        session = next(create_session())

        if self.session_id:
            db_session = session.get(AnalysisSession, self.session_id)
            if db_session:
                db_session.name = name
                db_session.description = description
                db_session.factors_json = factors_json
                db_session.options_json = options_json
                session.add(db_session)
                session.commit()
                return self.session_id

        new_session = AnalysisSession(
            name=name,
            description=description,
            factors_json=factors_json,
            options_json=options_json
        )
        session.add(new_session)
        session.commit()
        session.refresh(new_session)
        self.session_id = new_session.id
        return self.session_id

    @classmethod
    def load_session(cls, session_id: str) -> UnifiedDecisionFramework:
        from decision_maker.core.db import create_session
        from decision_maker.core.db_models import AnalysisSession

        session = next(create_session())
        db_session = session.get(AnalysisSession, session_id)
        if not db_session:
            raise ValueError(f"Session {session_id} not found in database.")

        instance = cls(session_id=session_id)
        for f_dict in db_session.factors_json:
            instance.add_factor(Factor(**f_dict))

        for o_dict in db_session.options_json:
            instance.add_option(DecisionOption(**o_dict))

        return instance

    async def run_analysis(
        self,
        mode: str = "standard",
        use_ai: bool = False,
        results_dir: str | None = None,
    ) -> dict[str, Any]:
        if mode not in ("express", "standard", "advanced"):
            logger.warning(f"Unknown mode '{mode}', falling back to 'standard'")
            mode = "standard"

        logger.info(f"Starting analysis in {mode.upper()} mode")

        profile = self.adaptive_router.profile(
            self.mc_engine.options,
            self.mc_engine.factors,
            has_correlation=self.mc_engine.correlation_matrix is not None,
        )
        if mode == "auto":
            mode = profile.recommended_mode
            logger.info(f"Adaptive routing: complexity={profile.complexity_score:.2f} → {mode}")

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
        future_metrics: dict[str, Any] = {}

        if mode in ("standard", "advanced"):
            strategies = self.dt_engine.analyze(mc_results)
            sensitivity_results = self.sens_engine.analyze(mc_results, self.mc_engine.factors)

            promethee_uncertainty = _promethee_with_uncertainty(
                self.promethee_engine,
                mc_results,
                PrometheeConfig(
                    weights=weights,
                    maximize=max_bools,
                    pref_types=self.promethee_pref_types,
                    pref_params=self.promethee_pref_params,
                ),
                factor_names,
            )

            robust = self.robust_engine.analyze(mc_results, self.mc_engine.factors)
            info_theory = self.info_theory_engine.analyze(mc_results, self.mc_engine.factors)

            rankings: dict[str, pd.Series] = {
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
            self._run_advanced_analysis(
                AdvancedAnalysis(
                    mc_results=mc_results,
                    factor_names=factor_names,
                    weights=weights,
                    max_bools=max_bools,
                    data_fuzzy=data_fuzzy,
                    future_metrics=future_metrics,
                    topsis_scores=topsis_scores,
                )
            )
            self._add_god_mode_metrics(future_metrics, mc_results)

        waterfall = self.explain_engine.factor_waterfall(mc_results, self.mc_engine.factors)
        counterfactual = self.explain_engine.counterfactual(mc_results, self.mc_engine.factors)
        explanation = self.explain_engine.narrative(
            NarrativeContext(
                mc_results=mc_results,
                factors=self.mc_engine.factors,
                waterfall=waterfall,
                counterfactual=counterfactual,
                topsis_scores=topsis_scores,
            ),
            mode,
            use_ai=False,
        )

        antifragile = self.antifragile_engine.analyze(mc_results, self.mc_engine.factors)

        ergodicity = self.ergodicity_engine.analyze(mc_results, self.mc_engine.factors)
        kelly = self.kelly_engine.analyze(mc_results, self.mc_engine.factors)

        ai_reports = {}
        if use_ai and self.ai_agent.is_available:
            tasks = [self.ai_agent.research(opt.name, opt.description) for opt in self.mc_engine.options]
            results = await asyncio.gather(*tasks)
            for opt, res in zip(self.mc_engine.options, results, strict=False):
                ai_reports[opt.name] = res

            # Phase 4: Self-updating Priors via LLM
            future_metrics["llm_priors"] = await self.ai_agent.calibrate_priors("Market volatility is high.")

        from decision_maker.core.reporting import ReportData, print_report, save_report

        report_data = ReportData(
            mode=mode,
            mc_results=mc_results,
            topsis_scores=topsis_scores,
            strategies=strategies,
            pareto=pareto_results,
            sensitivity=sensitivity_results,
            future=future_metrics,
            ai_reports=ai_reports,
            factors=self.mc_engine.factors,
            explanation=explanation,
            waterfall=waterfall,
            counterfactual=counterfactual,
            results_dir=results_dir,
        ).prepare()

        print_report(report_data)
        saved = save_report(report_data)

        if mode in ("standard", "advanced"):
            saved["plots"] = self._generate_plots(saved, mc_results, future_metrics)

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
            "ergodicity": ergodicity,
            "kelly": kelly,
            "factors": self.mc_engine.factors,
            "uncertainty": self._analyze_uncertainty(mc_results),
            "challenges": self._analyze_challenges(
                mc_results=mc_results,
                sensitivity_results=sensitivity_results,
                explanation=explanation,
                use_ai=use_ai,
            ),
            "adaptive_profile": {
                "complexity_score": profile.complexity_score,
                "recommended_mode": profile.recommended_mode,
                "reasoning": profile.reasoning,
                "recommended_engines": profile.recommended_engines,
                "skip_engines": profile.skip_engines,
            },
            "learning": {
                "outcome_accuracy": self.outcome_tracker.accuracy(),
                "calibration": self.calibration_scorer.score(self.outcome_tracker.entries()),
                "journal_summary": self.decision_journal.summary(),
            },
        }

    def _analyze_uncertainty(self, mc_results: dict[str, Statistics]) -> dict[str, Any]:
        """Confidence-weighted winner + bootstrap ranking confidence intervals."""
        from decision_maker.core.uncertainty import confidence_weighted_winner, ranking_confidence

        return {
            "confidence_weighted_winner": confidence_weighted_winner(mc_results),
            "ranking_confidence": ranking_confidence(mc_results),
        }

    def _analyze_challenges(
        self,
        mc_results: dict[str, Statistics],
        sensitivity_results: dict[str, Any],
        explanation: str,
        use_ai: bool,
    ) -> dict[str, Any]:
        """Devil's advocate challenges to the model's assumptions."""
        from decision_maker.core.devils_advocate import ChallengeRequest, DevilsAdvocate

        options = [o.name for o in self.mc_engine.options]
        winner = (
            max(mc_results.items(), key=lambda x: x[1].mean_score)[0]
            if mc_results
            else None
        )
        factors = [
            {"name": f.name, "weight": f.weight, "maximize": f.maximize}
            for f in self.mc_engine.factors
        ]
        return DevilsAdvocate(use_ai=use_ai).challenge(
            ChallengeRequest(
                winner=winner or "",
                options=options,
                factors=factors,
                mc_results=mc_results,
                sensitivity=sensitivity_results,
                explanation=explanation,
            )
        )

    def _generate_plots(
        self,
        saved: dict[str, Any],
        mc_results: dict[str, Statistics],
        future_metrics: dict[str, Any],
    ) -> list[str]:
        """Generate the plot suite for standard/advanced modes."""
        return self.viz_engine.generate_all_plots(
            PlotContext(
                mc_results=mc_results,
                factors=self.mc_engine.factors,
                future_metrics=future_metrics,
                output_dir=os.path.dirname(saved["json"]),
                timestamp=saved["timestamp"],
            )
        )

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

    def _add_god_mode_metrics(self, future_metrics: dict[str, Any], mc_results: dict[str, Statistics]) -> None:
        """Populate advanced-mode metrics: game theory, real options, surrogate, portfolio."""
        future_metrics["game_theory"] = self.game_theory_engine.analyze(mc_results)
        future_metrics["real_options"] = self.roa_engine.analyze(mc_results)
        future_metrics["ml_surrogate"] = self.ml_surrogate_engine.analyze(mc_results, self.mc_engine.factors)
        future_metrics["portfolio_allocation"] = self.portfolio_optimizer.optimize_allocation(mc_results)

    def _run_advanced_analysis(self, ctx: AdvancedAnalysis):
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

        promethee_scores = self.promethee_engine.analyze(
            df_crisp,
            PrometheeConfig(
                weights=weights,
                maximize=max_bools,
                pref_types=self.promethee_pref_types,
                pref_params=self.promethee_pref_params,
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
        borda_advanced = self.aggregator.aggregate(rankings_advanced, method="borda")

        bootstrap_ci = self.bootstrap_engine.confidence_intervals(
            data_fuzzy,
            BootstrapConfig(
                weights=weights,
                maximize=max_bools,
                n_bootstrap=DEFAULT_BOOTSTRAP_ITERATIONS,
            ),
        )

        future_metrics.update(
            {
                "bayesian_probs": self.bayes_engine.analyze(mc_results),
                "ideal_option": self.gen_engine.evolve_ideal(mc_results, self.mc_engine.factors),
                "promethee_scores": promethee_scores,
                "rank_aggregation": borda_advanced,
                "bootstrap_ci": bootstrap_ci,
            }
        )
