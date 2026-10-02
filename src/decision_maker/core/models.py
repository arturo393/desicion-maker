"""
[What it does] Data models and type definitions for decision options, factors, distributions, and statistics.
[How to use it] Import necessary models (e.g., from decision_maker.core.models import DecisionOption)
[What it DOESN'T do] Does not implement execution logic or orchestration.
"""

import logging
import math
from collections.abc import Callable
from enum import StrEnum
from typing import Any

import numpy as np
from pydantic import BaseModel, ConfigDict, Field, model_validator

logger = logging.getLogger(__name__)

EPSILON = 1e-9

class DistributionType(StrEnum):
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
VALIDATION_RULES = {
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

def _sample_deterministic(params: list[float], size: int, rng: np.random.Generator | None = None) -> np.ndarray:
    return np.full(size, params[0])

def _sample_normal(params: list[float], size: int, rng: np.random.Generator | None = None) -> np.ndarray:
    std = max(params[1], EPSILON)
    if rng is not None:
        return rng.normal(params[0], std, size)
    return np.random.normal(params[0], std, size)

def _sample_uniform(params: list[float], size: int, rng: np.random.Generator | None = None) -> np.ndarray:
    low, high = min(params[0], params[1]), max(params[0], params[1])
    if rng is not None:
        return rng.uniform(low, high, size)
    return np.random.uniform(low, high, size)

def _sample_triangular(params: list[float], size: int, rng: np.random.Generator | None = None) -> np.ndarray:
    left, mode, right = params[0], params[1], params[2]
    if not (left <= mode <= right):
        left, right = min(left, right), max(left, right)
        mode = np.clip(mode, left, right)
    if rng is not None:
        return rng.triangular(left, mode, right, size)
    return np.random.triangular(left, mode, right, size)

def _sample_bernoulli(params: list[float], size: int, rng: np.random.Generator | None = None) -> np.ndarray:
    p = np.clip(params[0], 0.0, 1.0)
    if rng is not None:
        return rng.binomial(1, p, size).astype(float)
    return np.random.binomial(1, p, size).astype(float)

def _sample_exponential(params: list[float], size: int, rng: np.random.Generator | None = None) -> np.ndarray:
    scale = max(params[0], EPSILON)
    if rng is not None:
        return rng.exponential(scale, size)
    return np.random.exponential(scale, size)

def _sample_beta(params: list[float], size: int, rng: np.random.Generator | None = None) -> np.ndarray:
    a, b = max(params[0], EPSILON), max(params[1], EPSILON)
    if rng is not None:
        return rng.beta(a, b, size)
    return np.random.beta(a, b, size)

def _sample_lognormal(params: list[float], size: int, rng: np.random.Generator | None = None) -> np.ndarray:
    sigma = max(params[1], EPSILON)
    if rng is not None:
        return rng.lognormal(params[0], sigma, size)
    return np.random.lognormal(params[0], sigma, size)

def _sample_gamma(params: list[float], size: int, rng: np.random.Generator | None = None) -> np.ndarray:
    shape, scale = max(params[0], EPSILON), max(params[1], EPSILON)
    if rng is not None:
        return rng.gamma(shape, scale, size)
    return np.random.gamma(shape, scale, size)

def _sample_poisson(params: list[float], size: int, rng: np.random.Generator | None = None) -> np.ndarray:
    lam = max(params[0], 0.0)
    if rng is not None:
        return rng.poisson(lam, size).astype(float)
    return np.random.poisson(lam, size).astype(float)



SAMPLE_DISPATCH: dict[DistributionType, Callable] = {
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


class UncertainVariable(BaseModel):
    name: str = Field(..., min_length=1)
    dist_type: DistributionType
    params: list[float] = Field(default_factory=list)

    def __init__(self, name: str, dist_type: DistributionType, params: list[float] = None, **kwargs):
        if params is None:
            params = []
        super().__init__(name=name, dist_type=dist_type, params=params, **kwargs)

    @model_validator(mode='after')
    def validate_params(self) -> 'UncertainVariable':
        rule = VALIDATION_RULES.get(self.dist_type)
        if not rule:
            raise ValueError(f"Unknown distribution type: {self.dist_type}")

        min_params, param_names = rule
        if len(self.params) < min_params:
            names_str = ", ".join(param_names)
            raise ValueError(f"{self.dist_type.value} requires at least {min_params} param(s) ({names_str})")

        if self.dist_type == DistributionType.NORMAL and len(self.params) >= 2 and self.params[1] < 0:
            raise ValueError(f"NORMAL std must be >= 0, got {self.params[1]}")

        return self

    def sample(self, size: int = 1, rng: np.random.Generator | None = None) -> np.ndarray:
        if size == 0:
            return np.array([])

        # Reject NaN or Inf parameters explicitly instead of silently falling back to defaults.
        for i, val in enumerate(self.params):
            if math.isnan(val) or math.isinf(val):
                raise ValueError(
                    f"Parameter {i} for variable '{self.name}' ({self.dist_type.value}) is invalid ({val}). "
                    f"Parameters cannot be NaN or Inf."
                )

        sampler = SAMPLE_DISPATCH.get(self.dist_type)
        if sampler is None:
            raise ValueError(
                f"Unknown distribution type '{self.dist_type}' for variable '{self.name}'"
            )
        try:
            return sampler(self.params, size, rng=rng)
        except (ValueError, TypeError) as e:
            raise ValueError(
                f"Sampling failed for variable '{self.name}' "
                f"({self.dist_type.value}, params={self.params}): {e}"
            ) from e



class Factor(BaseModel):
    name: str = Field(..., min_length=1)
    weight: float = Field(..., gt=0.0)
    maximize: bool = True
    category: str = "General"
    stakeholder_weights: dict[str, float] | None = None

    def __init__(self, name: str, weight: float, maximize: bool = True, category: str = "General", stakeholder_weights: dict[str, float] | None = None, **kwargs):
        super().__init__(name=name, weight=weight, maximize=maximize, category=category, stakeholder_weights=stakeholder_weights, **kwargs)

    @model_validator(mode='before')
    @classmethod
    def compute_weight(cls, data: Any) -> Any:
        if isinstance(data, dict):
            sw = data.get("stakeholder_weights")
            if sw and isinstance(sw, dict) and len(sw) > 0:
                data["weight"] = sum(sw.values()) / len(sw)
        return data


class Statistics(BaseModel):
    option_name: str
    mean_score: float
    std_dev: float
    min_score: float
    max_score: float
    percentile_5: float
    percentile_95: float
    success_rate: float
    factor_stats: dict[str, dict[str, float]]
    var_95: float
    cvar_95: float
    raw_scores: np.ndarray | None = Field(default=None, exclude=True) # Exclude from JSON dump
    raw_factor_data: dict[str, np.ndarray] | None = Field(default=None, exclude=True)

    def __init__(self, option_name: str, mean_score: float, std_dev: float, min_score: float, max_score: float, percentile_5: float, percentile_95: float, success_rate: float, factor_stats: dict[str, dict[str, float]], var_95: float, cvar_95: float, raw_scores: np.ndarray | None = None, raw_factor_data: dict[str, np.ndarray] | None = None, **kwargs):
        super().__init__(option_name=option_name, mean_score=mean_score, std_dev=std_dev, min_score=min_score, max_score=max_score, percentile_5=percentile_5, percentile_95=percentile_95, success_rate=success_rate, factor_stats=factor_stats, var_95=var_95, cvar_95=cvar_95, raw_scores=raw_scores, raw_factor_data=raw_factor_data, **kwargs)

    model_config = ConfigDict(arbitrary_types_allowed=True)


class DecisionOption(BaseModel):
    name: str = Field(..., min_length=1)
    description: str = ""
    variables: dict[str, UncertainVariable] = Field(default_factory=dict)

    def __init__(self, name: str, description: str = "", variables: dict[str, UncertainVariable] = None, **kwargs):
        if variables is None:
            variables = {}
        super().__init__(name=name, description=description, variables=variables, **kwargs)

    def add_variable(self, name: str, dist_type: DistributionType, *params: float) -> None:
        self.variables[name] = UncertainVariable(
            name=name,
            dist_type=dist_type,
            params=list(params)
        )
