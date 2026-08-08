"""
Validation rules and JSON schemas for validating decision configuration payloads.
Usage: from decision_maker.core.schemas import validate_config
Does NOT: Execute decision algorithms or manage database storage.
"""

from __future__ import annotations

__all__ = [
    "VariableConfig",
    "OptionConfig",
    "FactorConfig",
    "DecisionConfig",
    "RootConfig",
]


from pydantic import BaseModel, Field, model_validator


class VariableConfig(BaseModel):
    distribution: str = "deterministic"
    params: list[float] = Field(default_factory=lambda: [0.0])


class OptionConfig(BaseModel):
    name: str = Field(min_length=1)
    description: str = ""
    variables: dict[str, VariableConfig] = Field(default_factory=dict)


class FactorConfig(BaseModel):
    name: str = Field(min_length=1)
    weight: float = Field(ge=0)
    maximize: bool = True
    category: str = "General"


class DecisionConfig(BaseModel):
    name: str = "Untitled Decision"
    mode: str = "standard"
    simulations: int = Field(default=10000, ge=1)
    factors: list[FactorConfig] = Field(default_factory=list, min_length=1)
    options: list[OptionConfig] = Field(default_factory=list, min_length=1)
    correlation: float | None = Field(default=None, ge=0, le=1)
    promethee_pref_type: str | None = None

    @model_validator(mode="after")
    def validate_options_have_required_variables(self) -> DecisionConfig:
        factor_names = {f.name for f in self.factors}
        for opt in self.options:
            opt_factor_names = set(opt.variables.keys())
            missing = factor_names - opt_factor_names
            if missing:
                raise ValueError(f"Option '{opt.name}' is missing variables for factors: {missing}")
        return self


class RootConfig(BaseModel):
    decision: DecisionConfig = Field(default_factory=DecisionConfig)
