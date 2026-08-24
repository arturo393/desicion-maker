"""
Fuzzy weighted-sum engine for qualitative multi-criteria decisions with linguistic ratings.
Usage: from decision_maker.core.fuzzy_weighted_sum import FuzzyWeightedSum, FuzzyCriterion
Does NOT: Implement fuzzy TOPSIS (FPIS/FNIS distance) — see topsis.py for that.
"""

from __future__ import annotations

__all__ = ["FuzzyWeightedSum", "FuzzyCriterion", "FuzzyNumber", "CriterionDirection"]

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)

SCALE_MAX = 10.0


class CriterionDirection(Enum):
    MAXIMIZE = "maximize"
    MINIMIZE = "minimize"


@dataclass
class FuzzyNumber:
    """Triangular Fuzzy Number (a, b, c) where a <= b <= c."""

    a: float
    b: float
    c: float

    def defuzzify_centroid(self) -> float:
        return (self.a + self.b + self.c) / 3.0

    @classmethod
    def from_linguistic(cls, scale: str) -> FuzzyNumber:
        mapping = {
            "MUY_BAJO": cls(0.0, 1.0, 2.5),
            "BAJO": cls(1.5, 3.0, 4.5),
            "MEDIO": cls(4.0, 5.5, 7.0),
            "ALTO": cls(6.0, 7.5, 9.0),
            "MUY_ALTO": cls(8.0, 9.5, 10.0),
        }
        return mapping.get(scale.upper(), cls(5.0, 5.0, 5.0))


@dataclass
class FuzzyCriterion:
    """A weighted criterion with a maximize/minimize direction (Parameter Object)."""

    name: str
    weight: float
    direction: CriterionDirection = CriterionDirection.MAXIMIZE
    description: str = ""


@dataclass
class FuzzyOption:
    """An option scored against fuzzy criteria; scores can be numeric, FuzzyNumber or linguistic."""

    name: str
    description: str = ""
    scores: dict[str, Any] = field(default_factory=dict)


class FuzzyWeightedSum:
    """
    Weighted-sum multi-criteria engine over fuzzy/linguistic ratings.

    Evaluates options where scores may be:
      - numeric (0-10)
      - FuzzyNumber (triangular, defuzzified by centroid)
      - linguistic strings (MUY_BAJO, BAJO, MEDIO, ALTO, MUY_ALTO)

    Weights are normalized to sum to 1 WITHOUT mutating caller objects.
    """

    def __init__(self, criteria: list[FuzzyCriterion]):
        self._criteria = list(criteria)
        total_weight = sum(c.weight for c in self._criteria)
        if total_weight <= 0:
            raise ValueError("Total criterion weight must be positive")
        self._normalized_weights = {c.name: c.weight / total_weight for c in self._criteria}

    def _to_crisp(self, val: Any) -> float:
        if isinstance(val, FuzzyNumber):
            return val.defuzzify_centroid()
        if isinstance(val, str):
            return FuzzyNumber.from_linguistic(val).defuzzify_centroid()
        return float(val)

    def evaluate(self, options: list[FuzzyOption]) -> list[dict[str, Any]]:
        results = []
        for opt in options:
            total = 0.0
            breakdown = {}
            for crit in self._criteria:
                val = self._to_crisp(opt.scores.get(crit.name, 0.0))
                if crit.direction == CriterionDirection.MINIMIZE:
                    val = SCALE_MAX - val
                contrib = val * self._normalized_weights[crit.name]
                total += contrib
                breakdown[crit.name] = round(contrib, 3)
            results.append({
                "option_name": opt.name,
                "overall_score": round(total, 3),
                "breakdown": breakdown,
            })

        results.sort(key=lambda x: x["overall_score"], reverse=True)
        for rank, res in enumerate(results, 1):
            res["rank"] = rank
        return results

    def sensitivity(self, options: list[FuzzyOption], delta: float = 0.20) -> dict[str, Any]:
        """Perturb each criterion weight by ±delta and detect winner flips."""
        base = self.evaluate(options)
        winner_base = base[0]["option_name"]
        critical: list[str] = []
        flips = 0

        for crit in self._criteria:
            orig = self._normalized_weights[crit.name]
            for factor in (1.0 + delta, max(0.01, 1.0 - delta)):
                self._normalized_weights[crit.name] = orig * factor
                perturbed = self.evaluate(options)
                if perturbed[0]["option_name"] != winner_base:
                    flips += 1
                    if crit.name not in critical:
                        critical.append(crit.name)
            self._normalized_weights[crit.name] = orig

        return {
            "baseline_winner": winner_base,
            "perturbation_percent": delta * 100,
            "stability_assessment": "ROBUSTO" if flips == 0 else "SENSIBLE (Sensibilidad detectada)",
            "critical_criteria": critical,
        }
