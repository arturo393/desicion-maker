from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional

import numpy as np


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
        try:
            if self.dist_type == DistributionType.DETERMINISTIC:
                p = self._sanitize(self.params, [0])
                return np.full(size, p[0])
            elif self.dist_type == DistributionType.NORMAL:
                p = self._sanitize(self.params, [0, 1])
                return np.random.normal(p[0], max(p[1], 1e-9), size)
            elif self.dist_type == DistributionType.UNIFORM:
                p = self._sanitize(self.params, [0, 1])
                low, high = min(p[0], p[1]), max(p[0], p[1])
                return np.random.uniform(low, high, size)
            elif self.dist_type == DistributionType.TRIANGULAR:
                p = self._sanitize(self.params, [0, 1, 2])[:3]
                left, mode, right = sorted(p)
                return np.random.triangular(left, mode, right, size)
            elif self.dist_type == DistributionType.BERNOULLI:
                p = self._sanitize(self.params, [0.5])[0]
                return np.random.binomial(1, np.clip(p, 0, 1), size).astype(float)
            elif self.dist_type == DistributionType.EXPONENTIAL:
                p = self._sanitize(self.params, [1])
                return np.random.exponential(max(p[0], 1e-9), size)
            elif self.dist_type == DistributionType.BETA:
                p = self._sanitize(self.params, [1, 1])
                return np.random.beta(max(p[0], 1e-9), max(p[1], 1e-9), size)
            elif self.dist_type == DistributionType.LOGNORMAL:
                p = self._sanitize(self.params, [0, 1])
                return np.random.lognormal(p[0], max(p[1], 1e-9), size)
            elif self.dist_type == DistributionType.GAMMA:
                p = self._sanitize(self.params, [1, 1])
                return np.random.gamma(max(p[0], 1e-9), max(p[1], 1e-9), size)
            elif self.dist_type == DistributionType.POISSON:
                p = self._sanitize(self.params, [1])
                return np.random.poisson(max(int(p[0]), 0), size).astype(float)
            else:
                return np.zeros(size)
        except Exception:
            return np.zeros(size)

    def validate(self) -> List[str]:
        errors = []
        if self.dist_type == DistributionType.DETERMINISTIC and len(self.params) < 1:
            errors.append(f"{self.name}: DETERMINISTIC requires 1 param (value)")
        elif self.dist_type == DistributionType.NORMAL and len(self.params) < 2:
            errors.append(f"{self.name}: NORMAL requires 2 params (mean, std)")
        elif self.dist_type == DistributionType.UNIFORM and len(self.params) < 2:
            errors.append(f"{self.name}: UNIFORM requires 2 params (low, high)")
        elif self.dist_type == DistributionType.TRIANGULAR and len(self.params) < 3:
            errors.append(f"{self.name}: TRIANGULAR requires 3 params (left, mode, right)")
        elif self.dist_type in (DistributionType.BETA, DistributionType.LOGNORMAL, DistributionType.GAMMA) and len(self.params) < 2:
            errors.append(f"{self.name}: {self.dist_type.value} requires 2 params")
        elif self.dist_type in (DistributionType.BERNOULLI, DistributionType.EXPONENTIAL, DistributionType.POISSON) and len(self.params) < 1:
            errors.append(f"{self.name}: {self.dist_type.value} requires 1 param")
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

    def add_variable(self, name: str, dist_type: DistributionType, *params):
        self.variables[name] = UncertainVariable(name, dist_type, list(params))
