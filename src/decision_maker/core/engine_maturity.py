"""
Engine maturity classification for the decision framework's routable engines.

What it does:
Classifies every engine in ENGINE_UNIVERSE by its validation status:
- 'validated': Empirically verified against external reference implementations or
  independent step-by-step analytical derivations (e.g. PROMETHEE with pymcdm and
  hand calculation; Monte Carlo with seeded reproducibility, convergence thresholds,
  and property-based tests).
- 'characterized': Mathematical formulation and divergence from classical standards
  formally understood and tested (e.g. TOPSIS on crisp data collapses to min-max SAW
  and exhibits rank reversal upon addition of dominated alternatives).
- 'experimental': Exploratory or heuristic modules lacking external benchmark validation.

How to use it:
from decision_maker.core.engine_maturity import (
    ENGINE_MATURITY,
    get_engine_maturity,
    get_engine_maturity_for_run,
)

What it DOESN'T do:
Does not dispatch or run the algorithms.
"""

from __future__ import annotations

__all__ = [
    "ENGINE_MATURITY",
    "MaturityEntry",
    "MaturityLevel",
    "resolve_engine_maturity",
    "resolve_run_engine_maturity",
]

from typing import Literal, TypedDict

MaturityLevel = Literal["validated", "characterized", "experimental"]


class MaturityEntry(TypedDict):
    level: MaturityLevel
    evidence: list[str]


# Engine maturity registry covering every engine in ENGINE_UNIVERSE (19 routable engines)
ENGINE_MATURITY: dict[str, MaturityEntry] = {
    "MonteCarlo": {
        "level": "validated",
        "evidence": [
            "src/decision_maker/tests/test_monte_carlo.py",
            "src/decision_maker/tests/test_monte_carlo_convergence.py",
            "src/decision_maker/tests/test_properties.py",
        ],
    },
    "TOPSIS": {
        "level": "characterized",
        "evidence": [
            "src/decision_maker/tests/test_reference_libraries.py",
            "src/decision_maker/tests/test_published_examples.py",
            "src/decision_maker/tests/test_topsis.py",
        ],
    },
    "Pareto": {
        "level": "experimental",
        "evidence": [
            "src/decision_maker/tests/test_pareto.py",
            "src/decision_maker/tests/test_properties.py",
        ],
    },
    "DecisionTheory": {
        "level": "experimental",
        "evidence": [
            "src/decision_maker/tests/test_decision_theory.py",
        ],
    },
    "Sensitivity": {
        "level": "experimental",
        "evidence": [
            "src/decision_maker/tests/test_sensitivity.py",
        ],
    },
    "PROMETHEE": {
        "level": "validated",
        "evidence": [
            "src/decision_maker/tests/test_reference_libraries.py",
            "src/decision_maker/tests/test_published_examples.py",
            "src/decision_maker/tests/test_promethee.py",
        ],
    },
    "Robust": {
        "level": "experimental",
        "evidence": [
            "src/decision_maker/tests/test_robust.py",
        ],
    },
    "Bayesian": {
        "level": "experimental",
        "evidence": [
            "src/decision_maker/tests/test_bayesian.py",
        ],
    },
    "Genetic": {
        "level": "experimental",
        "evidence": [
            "src/decision_maker/tests/test_genetic.py",
        ],
    },
    "Bootstrap": {
        "level": "experimental",
        "evidence": [
            "src/decision_maker/tests/test_bootstrap.py",
        ],
    },
    "Ergodicity": {
        "level": "experimental",
        "evidence": [
            "src/decision_maker/tests/test_ergodicity.py",
        ],
    },
    "Kelly": {
        "level": "experimental",
        "evidence": [
            "src/decision_maker/tests/test_kelly.py",
        ],
    },
    "Antifragile": {
        "level": "experimental",
        "evidence": [
            "src/decision_maker/tests/test_antifragile.py",
        ],
    },
    "Explainability": {
        "level": "experimental",
        "evidence": [
            "src/decision_maker/tests/test_explainability.py",
        ],
    },
    "GameTheory": {
        "level": "experimental",
        "evidence": [],
    },
    "ROA": {
        "level": "experimental",
        "evidence": [],
    },
    "MLSurrogate": {
        "level": "experimental",
        "evidence": [],
    },
    "Portfolio": {
        "level": "experimental",
        "evidence": [
            "src/decision_maker/tests/test_portfolio.py",
        ],
    },
    "InformationTheory": {
        "level": "experimental",
        "evidence": [
            "src/decision_maker/tests/test_information_theory.py",
        ],
    },
}


def resolve_engine_maturity(engine_name: str) -> MaturityLevel:
    """Return the maturity level ('validated', 'characterized', 'experimental') of an engine."""
    entry = ENGINE_MATURITY.get(engine_name)
    if entry is not None:
        return entry["level"]
    return "experimental"


def resolve_run_engine_maturity(
    mode: str,
    recommended_engines: tuple[str, ...] | list[str] | None = None,
) -> dict[str, MaturityLevel]:
    """Return maturity levels for the engines active in a specific execution run.

    Parameters:
        mode: Execution mode ('express', 'standard', 'advanced', 'auto').
        recommended_engines: Optional explicit list of engines selected by the router.

    Returns:
        Mapping from engine name to its maturity level.
    """
    from decision_maker.core.adaptive_router import ROUTES

    if recommended_engines is not None:
        engines = recommended_engines
    else:
        route_tuple = ROUTES.get(mode)
        engines = route_tuple[0] if route_tuple is not None else ()

    return {engine: resolve_engine_maturity(engine) for engine in engines}
