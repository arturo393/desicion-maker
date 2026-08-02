"""
Data models and type definitions for decision options, factors, distributions, and statistics.
Uses Pydantic V2 for rigorous runtime validation.
"""

from enum import Enum
from typing import Dict, List, Optional, Callable
import math
import numpy as np
from pydantic import BaseModel, Field, model_validator

EPSILON = 1e-9

class DistributionType(str, Enum):
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
    return np.random.binomial(1, np.clip(params[0], 0.0, 1.0), size).astype(float)

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


class UncertainVariable(BaseModel):
    name: str = Field(..., min_length=1)
    dist_type: DistributionType
    params: List[float] = Field(default_factory=list)

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

    def sample(self, size: int = 1) -> np.ndarray:
        # Defaults fallback logic
        defaults_map = {
            DistributionType.DETERMINISTIC: [0.0],
            DistributionType.NORMAL: [0.0, 1.0],
            DistributionType.UNIFORM: [0.0, 1.0],
            DistributionType.TRIANGULAR: [0.0, 1.0, 2.0],
            DistributionType.BERNOULLI: [0.5],
            DistributionType.EXPONENTIAL: [1.0],
            DistributionType.BETA: [1.0, 1.0],
            DistributionType.LOGNORMAL: [0.0, 1.0],
            DistributionType.GAMMA: [1.0, 1.0],
            DistributionType.POISSON: [1.0],
        }
        defaults = defaults_map.get(self.dist_type, [0.0])
        
        sanitized = []
        for i in range(len(defaults)):
            if i < len(self.params) and not (math.isnan(self.params[i]) or math.isinf(self.params[i])):
                sanitized.append(self.params[i])
            else:
                sanitized.append(defaults[i])

        sampler = SAMPLE_DISPATCH.get(self.dist_type)
        if sampler is None:
            return np.zeros(size)
        try:
            return sampler(sanitized, size)
        except (ValueError, TypeError):
            return np.zeros(size)


class Factor(BaseModel):
    name: str = Field(..., min_length=1)
    weight: float = Field(..., gt=0.0)
    maximize: bool = True
    category: str = "General"
    stakeholder_weights: Optional[Dict[str, float]] = None

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
    factor_stats: Dict[str, Dict[str, float]]
    var_95: float
    cvar_95: float
    raw_scores: Optional[np.ndarray] = Field(default=None, exclude=True) # Exclude from JSON dump
    raw_factor_data: Optional[Dict[str, np.ndarray]] = Field(default=None, exclude=True)

    class Config:
        arbitrary_types_allowed = True


class DecisionOption(BaseModel):
    name: str = Field(..., min_length=1)
    description: str = ""
    variables: Dict[str, UncertainVariable] = Field(default_factory=dict)

    def add_variable(self, name: str, dist_type: DistributionType, *params: float) -> None:
        self.variables[name] = UncertainVariable(
            name=name,
            dist_type=dist_type,
            params=list(params)
        )
