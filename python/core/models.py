from __future__ import annotations

__all__ = [
    "DistributionType",
    "UncertainVariable",
    "Factor",
    "Statistics",
    "DecisionOption",
    "EPSILON",
    "VALIDATION_RULES",
    "SAMPLE_DISPATCH",
]

import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Dict, List, Optional

import numpy as np


EPSILON = 1e-9


class DistributionType(Enum):
    DETERMINISTIC = "deterministic"
    NORMAL = "normal"
    UNIFORM = "uniform"
    TRIANGULAR = "triangular"
    BERNOULLI = "bernoulli"
    EXPONENTIAL = "exponential"
    BETA = "beta"
    LOGNORMAL = "lognormal"
    GAMMA = "gamma"
    POISSON = "poisson"


# Validation rules: (min_params, param_names)
VALIDATION_RULES: Dict[DistributionType, tuple] = {
    DistributionType.DETERMINISTIC: (1, ("value",)),
    DistributionType.NORMAL: (2, ("mean", "std")),
    DistributionType.UNIFORM: (2, ("low", "high")),
    DistributionType.TRIANGULAR: (3, ("left", "mode", "right")),
    DistributionType.BERNOULLI: (1, ("probability",)),
    DistributionType.EXPONENTIAL: (1, ("scale",)),
    DistributionType.BETA: (2, ("alpha", "beta")),
    DistributionType.LOGNORMAL: (2, ("mean", "sigma")),
    DistributionType.GAMMA: (2, ("shape", "scale")),
    DistributionType.POISSON: (1, ("rate",)),
}


def _sample_deterministic(params: List[float], size: int) -> np.ndarray:
    return np.full(size, params[0])


def _sample_normal(params: List[float], size: int) -> np.ndarray:
    return np.random.normal(params[0], max(params[1], EPSILON), size)


def _sample_uniform(params: List[float], size: int) -> np.ndarray:
    low, high = min(params[0], params[1]), max(params[0], params[1])
    return np.random.uniform(low, high, size)


def _sample_triangular(params: List[float], size: int) -> np.ndarray:
    left, mode, right = params[0], params[1], params[2]
    if not (left <= mode <= right):
        left, right = min(left, right), max(left, right)
        mode = np.clip(mode, left, right)
    return np.random.triangular(left, mode, right, size)


def _sample_bernoulli(params: List[float], size: int) -> np.ndarray:
    return np.random.binomial(1, np.clip(params[0], 0, 1), size).astype(float)


def _sample_exponential(params: List[float], size: int) -> np.ndarray:
    return np.random.exponential(max(params[0], EPSILON), size)


def _sample_beta(params: List[float], size: int) -> np.ndarray:
    return np.random.beta(max(params[0], EPSILON), max(params[1], EPSILON), size)


def _sample_lognormal(params: List[float], size: int) -> np.ndarray:
    return np.random.lognormal(params[0], max(params[1], EPSILON), size)


def _sample_gamma(params: List[float], size: int) -> np.ndarray:
    return np.random.gamma(max(params[0], EPSILON), max(params[1], EPSILON), size)


def _sample_poisson(params: List[float], size: int) -> np.ndarray:
    return np.random.poisson(max(params[0], 0.0), size).astype(float)


SAMPLE_DISPATCH: Dict[DistributionType, Callable] = {
    DistributionType.DETERMINISTIC: _sample_deterministic,
    DistributionType.NORMAL: _sample_normal,
    DistributionType.UNIFORM: _sample_uniform,
    DistributionType.TRIANGULAR: _sample_triangular,
    DistributionType.BERNOULLI: _sample_bernoulli,
    DistributionType.EXPONENTIAL: _sample_exponential,
    DistributionType.BETA: _sample_beta,
    DistributionType.LOGNORMAL: _sample_lognormal,
    DistributionType.GAMMA: _sample_gamma,
    DistributionType.POISSON: _sample_poisson,
}


@dataclass
class UncertainVariable:
    name: str
    dist_type: DistributionType
    params: List[float]

    def _sanitize(self, params: List[float], defaults: List[float]) -> List[float]:
        result = []
        for i in range(len(defaults)):
            if i < len(params) and not (math.isnan(params[i]) or math.isinf(params[i])):
                result.append(params[i])
            else:
                result.append(defaults[i])
        return result

    def sample(self, size: int = 1) -> np.ndarray:
        defaults_map = {
            DistributionType.DETERMINISTIC: [0],
            DistributionType.NORMAL: [0, 1],
            DistributionType.UNIFORM: [0, 1],
            DistributionType.TRIANGULAR: [0, 1, 2],
            DistributionType.BERNOULLI: [0.5],
            DistributionType.EXPONENTIAL: [1],
            DistributionType.BETA: [1, 1],
            DistributionType.LOGNORMAL: [0, 1],
            DistributionType.GAMMA: [1, 1],
            DistributionType.POISSON: [1],
        }
        defaults = defaults_map.get(self.dist_type, [0])
        p = self._sanitize(self.params, defaults)
        sampler = SAMPLE_DISPATCH.get(self.dist_type)
        if sampler is None:
            return np.zeros(size)
        try:
            return sampler(p, size)
        except (ValueError, TypeError):
            return np.zeros(size)

    def validate(self) -> List[str]:
        errors = []
        rule = VALIDATION_RULES.get(self.dist_type)
        if rule is None:
            errors.append(f"{self.name}: unknown distribution type")
            return errors

        min_params, param_names = rule
        if len(self.params) < min_params:
            names_str = ", ".join(param_names)
            errors.append(
                f"{self.name}: {self.dist_type.value} requires {min_params} param(s) ({names_str})"
            )

        if self.dist_type == DistributionType.NORMAL and len(self.params) >= 2 and self.params[1] < 0:
            errors.append(f"{self.name}: NORMAL std must be >= 0, got {self.params[1]}")

        return errors


@dataclass
class Factor:
    name: str
    weight: float
    maximize: bool = True
    category: str = "General"


@dataclass
class Statistics:
    option_name: str
    mean_score: float
    std_dev: float
    min_score: float
    max_score: float
    percentile_5: float
    percentile_95: float
    success_rate: float
    factor_stats: Dict[str, Dict[str, float]]
    var_95: float
    cvar_95: float
    raw_scores: Optional[np.ndarray] = None
    raw_factor_data: Optional[Dict[str, np.ndarray]] = None


@dataclass
class DecisionOption:
    name: str
    description: str = ""
    variables: Dict[str, UncertainVariable] = field(default_factory=dict)

    def add_variable(self, name: str, dist_type: DistributionType, *params: float) -> None:
        self.variables[name] = UncertainVariable(name, dist_type, list(params))
