"""
Core package exports for the multi-criteria decision intelligence framework.
Usage: from decision_maker.core import UnifiedDecisionFramework, NormalizationEngine
Does NOT: Execute CLI commands directly or start API servers.
"""

from decision_maker.core.aggregator import RankAggregator
from decision_maker.core.ahp import AHPHelper
from decision_maker.core.antifragile import AntifragileEngine
from decision_maker.core.bayesian import BayesianEngine
from decision_maker.core.bootstrap import BootstrapRanking
from decision_maker.core.decision_theory import DecisionTheoryEngine
from decision_maker.core.explainability import ExplainabilityEngine
from decision_maker.core.gemini_agent import GeminiDeepResearchAgent
from decision_maker.core.genetic import GeneticOptimizer
from decision_maker.core.group_decision import GroupDecisionEngine
from decision_maker.core.information_theory import InformationTheoryEngine
from decision_maker.core.models import DecisionOption, DistributionType, Factor, Statistics, UncertainVariable
from decision_maker.core.monte_carlo import MonteCarloEngine
from decision_maker.core.normalization import NormalizationEngine, NormalizationMethod
from decision_maker.core.orchestrator import UnifiedDecisionFramework
from decision_maker.core.pareto import ParetoEngine
from decision_maker.core.portfolio import PortfolioOptimizer
from decision_maker.core.promethee import PrometheeEngine
from decision_maker.core.registry import DecisionRegistry
from decision_maker.core.reporting import build_algorithm_comparison, prepare_decision_matrix, save_report
from decision_maker.core.robust import RobustOptimizer
from decision_maker.core.schemas import DecisionConfig
from decision_maker.core.sensitivity import SensitivityEngine
from decision_maker.core.topology import TopologicalDataAnalysis
from decision_maker.core.topsis import TOPSISEngine
from decision_maker.core.visualization import VisualizationEngine
from decision_maker.core.weight_derivation import WeightDerivationEngine
from decision_maker.core.what_if import WhatIfEngine

__all__ = [
    "DistributionType",
    "UncertainVariable",
    "Factor",
    "Statistics",
    "DecisionOption",
    "MonteCarloEngine",
    "TOPSISEngine",
    "PrometheeEngine",
    "ParetoEngine",
    "SensitivityEngine",
    "BayesianEngine",
    "GeneticOptimizer",
    "AHPHelper",
    "DecisionTheoryEngine",
    "GeminiDeepResearchAgent",
    "UnifiedDecisionFramework",
    "InformationTheoryEngine",
    "VisualizationEngine",
    "RobustOptimizer",
    "RankAggregator",
    "BootstrapRanking",
    "WhatIfEngine",
    "AntifragileEngine",
    "WeightDerivationEngine",
    "DecisionRegistry",
    "GroupDecisionEngine",
    "PortfolioOptimizer",
    "TopologicalDataAnalysis",
    "ExplainabilityEngine",
    "NormalizationEngine",
    "NormalizationMethod",
    "prepare_decision_matrix",
    "build_algorithm_comparison",
    "save_report",
    "DecisionConfig",
]
