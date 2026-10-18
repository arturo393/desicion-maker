"""
Unified orchestrator coordinating multi-criteria algorithms and execution pipelines.
Usage: from decision_maker.core.orchestrator import UnifiedDecisionFramework
Does NOT: Implement individual algorithm logic directly.
"""

from __future__ import annotations

__all__ = ["UnifiedDecisionFramework"]

import asyncio
import logging
from typing import Any

import numpy as np
import pandas as pd

from decision_maker.core.action_threshold import MinimumActionThreshold
from decision_maker.core.adaptive_router import AdaptiveRouter
from decision_maker.core.aggregator import RankAggregator
from decision_maker.core.antifragile import AntifragileEngine
from decision_maker.core.bayesian import BayesianEngine
from decision_maker.core.bootstrap import BootstrapRanking
from decision_maker.core.calibration_scorer import CalibrationScorer
from decision_maker.core.causal_dag import CausalDAG
from decision_maker.core.decision_gates import DecisionGate
from decision_maker.core.decision_journal import DecisionJournal
from decision_maker.core.decision_theory import DecisionTheoryEngine
from decision_maker.core.engine_maturity import resolve_run_engine_maturity
from decision_maker.core.ergodicity import ErgodicityAnalyzer
from decision_maker.core.explainability import ExplainabilityEngine, NarrativeContext
from decision_maker.core.game_theory import GameTheoryEngine
from decision_maker.core.gemini_agent import GeminiDeepResearchAgent
from decision_maker.core.genetic import GeneticOptimizer
from decision_maker.core.information_theory import InformationTheoryEngine
from decision_maker.core.kelly import KellyCriterionEngine
from decision_maker.core.meta_calibration import MetaCalibration
from decision_maker.core.ml_surrogate import MLSurrogateEngine
from decision_maker.core.models import DecisionOption, Factor, Statistics
from decision_maker.core.monte_carlo import MonteCarloEngine
from decision_maker.core.orchestrator_steps import (
    WEIGHT_SEED_OFFSET,
    AdvancedAnalysis,
    _add_advanced_engine_metrics,
    _analyze_uncertainty,
    _build_analysis_inputs,
    _check_range_amplification,
    _generate_plots,
    _promethee_with_uncertainty,
    _run_advanced_analysis,
)
from decision_maker.core.outcome_tracker import OutcomeTracker
from decision_maker.core.pareto import ParetoEngine
from decision_maker.core.portfolio import PortfolioOptimizer
from decision_maker.core.promethee import PrometheeConfig, PrometheeEngine
from decision_maker.core.reasoning_trace import ReasoningTrace
from decision_maker.core.roa import RealOptionsEngine
from decision_maker.core.robust import RobustOptimizer
from decision_maker.core.sensitivity import SensitivityEngine
from decision_maker.core.topsis import TOPSISEngine
from decision_maker.core.unknown_scanner import UnknownUnknownsScanner
from decision_maker.core.value_of_information import calculate_value_of_information
from decision_maker.core.visualization import VisualizationEngine
from decision_maker.core.weight_robustness import weight_robustness

logger = logging.getLogger(__name__)



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
        self.action_threshold = MinimumActionThreshold()
        self.reasoning_trace = ReasoningTrace()
        self.unknown_scanner = UnknownUnknownsScanner()
        self.meta_calibration = MetaCalibration()
        self.decision_gates = DecisionGate()
        self.causal_dag = CausalDAG()
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
        if new_session.id is None:  # the database assigns it on commit
            raise RuntimeError("AnalysisSession was committed without an id")
        self.session_id = new_session.id
        return new_session.id

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
        if mode not in ("express", "standard", "advanced", "auto"):
            logger.warning(f"Unknown mode '{mode}', falling back to 'standard'")
            mode = "standard"

        logger.info(f"Starting analysis in {mode.upper()} mode")

        mc_results = self.mc_engine.run()  # raises on an empty or incomplete model

        profile = self.adaptive_router.profile(
            self.mc_engine.options,
            self.mc_engine.factors,
            mc_results=mc_results,
            has_correlation=self.mc_engine.correlation_matrix is not None,
        )
        if mode == "auto":
            mode = profile.recommended_mode
            logger.info(f"Adaptive routing: complexity={profile.complexity_score:.2f} → {mode}")

        self.reasoning_trace.record(
            problem_name=self.mc_engine.options[0].name if self.mc_engine.options else "untitled",
            complexity_score=profile.complexity_score,
            recommended_mode=profile.recommended_mode,
            engines_run=profile.recommended_engines,
            engines_skipped=profile.skip_engines,
            skip_reasons={e: "not needed at this complexity level" for e in profile.skip_engines},
            routing_reasoning=profile.reasoning,
            dimension_scores={
                "num_options": float(profile.num_options),
                "num_factors": float(profile.num_factors),
                "uncertainty": profile.factor_uncertainty,
                "diversity": profile.option_diversity,
                "correlation": float(profile.has_correlation),
            },
        )

        threshold = self.action_threshold.evaluate(mc_results, self.mc_engine.factors)

        causal_dag = self.causal_dag.build(self.mc_engine.factors, [o.name for o in self.mc_engine.options])

        ergodicity = self.ergodicity_engine.analyze(mc_results, self.mc_engine.factors)
        ruin_probabilities = {
            name: opt_data.get("ruin_probability")
            for name, opt_data in ergodicity.get("options", {}).items()
        }

        gate_result = self.decision_gates.apply(
            mc_results=mc_results,
            factors=self.mc_engine.factors,
            ergodicity_data=ergodicity,
            ruin_probabilities=ruin_probabilities,
            signal_to_noise=threshold.signal_to_noise,
        )

        if gate_result.pipeline_halted:
            logger.warning(f"PIPELINE HALTED by gates: {gate_result.halt_reason}")
            return {
                "pipeline_halted": True,
                "gate_result": DecisionGate.to_dict(gate_result),
                "threshold": MinimumActionThreshold.to_dict(threshold),
                "causal_dag": causal_dag,
                "mc_results": mc_results,
                "factors": self.mc_engine.factors,
                "convergence": self.mc_engine.last_convergence,
            }

        # Filter vetoed options BEFORE computing subsequent rankings (TOPSIS, PROMETHEE,
        # Borda, narrative, etc.) so that vetoed options are not ranked or recommended.
        if gate_result.options_vetoed:
            for vetoed in gate_result.options_vetoed:
                mc_results.pop(vetoed, None)
            logger.info(f"Options vetoed by gates: {gate_result.options_vetoed}")

        _check_range_amplification(self.mc_engine.factors, mc_results)

        data_fuzzy, weights, max_bools, factor_names = _build_analysis_inputs(mc_results, self.mc_engine.factors)

        topsis_scores = self.topsis_engine.analyze(data_fuzzy, weights, max_bools) if data_fuzzy else pd.Series()
        pareto_results = self.pareto_engine.analyze(mc_results, self.mc_engine.factors)
        strategies = {}
        sensitivity_results = {}
        weight_robust: dict[str, Any] | None = None
        future_metrics: dict[str, Any] = {}

        if mode in ("standard", "advanced"):
            strategies = self.dt_engine.analyze(
                mc_results,
                is_fully_shared=self.mc_engine.is_fully_shared(),
            )
            sensitivity_results = self.sens_engine.analyze(mc_results, self.mc_engine.factors)
            if len(mc_results) >= 2:
                weight_robust = weight_robustness(
                    mc_results, self.mc_engine.factors, seed=self.mc_engine.seed + WEIGHT_SEED_OFFSET
                ).to_dict()

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
            _run_advanced_analysis(
                self,
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
            _add_advanced_engine_metrics(self, future_metrics, mc_results)

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
        kelly = self.kelly_engine.analyze(mc_results, self.mc_engine.factors)

        approved_winner = (
            max(mc_results.items(), key=lambda x: x[1].mean_score)[0]
            if mc_results else None
        )

        # Winner agreement: checks whether topsis, promethee, and borda agree with the MC mean winner.
        # Engines not calculated in this run are omitted.
        winner_agreement: dict[str, bool] = {}
        if approved_winner:
            if not topsis_scores.empty:
                winner_agreement["topsis"] = bool(topsis_scores.index[0] == approved_winner)
            prom_ranks = future_metrics.get("promethee_uncertainty")
            if isinstance(prom_ranks, pd.Series) and not prom_ranks.empty:
                winner_agreement["promethee"] = bool(prom_ranks.index[0] == approved_winner)
            borda_dict = future_metrics.get("rank_aggregation")
            if isinstance(borda_dict, dict) and borda_dict.get("winner") is not None:
                winner_agreement["borda"] = bool(borda_dict["winner"] == approved_winner)


        # A run drafts a commitment; only a person commits (`decision-maker decide`). Writing one per
        # run filled the store with 1300 entries nobody had decided and nobody reviewed.
        commitment_draft = None
        if approved_winner and threshold.should_decide:
            commitment_draft = {
                "chosen_option": approved_winner,
                "confidence": threshold.confidence_in_winner,
                "reasoning": threshold.reasoning,
            }

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
            results_dir=results_dir or "",  # "" -> ReportData.prepare() picks results_dir()
            weight_robustness=weight_robust,
        ).prepare()

        print_report(report_data)
        saved: dict[str, Any] = dict(save_report(report_data))

        if mode in ("standard", "advanced"):
            saved["plots"] = _generate_plots(self, saved, mc_results, future_metrics)

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
            "uncertainty": _analyze_uncertainty(self, mc_results),
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
            "action_threshold": MinimumActionThreshold.to_dict(threshold),
            "gate_result": DecisionGate.to_dict(gate_result),
            "winner_agreement": winner_agreement,
            "convergence": self.mc_engine.last_convergence,
            "causal_dag": causal_dag,

            "commitment_draft": commitment_draft,
            "learning": {
                "outcome_accuracy": self.outcome_tracker.accuracy(),
                "calibration": self.calibration_scorer.score(self.outcome_tracker.entries()),
                "journal_summary": self.decision_journal.summary(),
                "unknowns": UnknownUnknownsScanner.to_dict(
                    self.unknown_scanner.scan(self.outcome_tracker.entries())
                ),
                "meta_calibration": MetaCalibration.to_dict(
                    self.meta_calibration.evaluate(
                        self.reasoning_trace.entries(),
                        self.outcome_tracker.entries(),
                    )
                ),
                "routing_trace": self.reasoning_trace.summary(),
            },
            "weight_robustness": weight_robust,
            "value_of_information": calculate_value_of_information(
                mc_results=mc_results,
                is_fully_shared=self.mc_engine.is_fully_shared(),
                drivers=self.mc_engine.drivers(),
                driver_samples=self.mc_engine.driver_samples,
            ),
            "engine_maturity": resolve_run_engine_maturity(
                mode=mode,
                recommended_engines=profile.recommended_engines if mode == "auto" else None,
            ),
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
