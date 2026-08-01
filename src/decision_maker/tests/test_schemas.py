import pytest
from pydantic import ValidationError

from decision_maker.core.schemas import DecisionConfig, FactorConfig, OptionConfig, RootConfig, VariableConfig


class TestVariableConfig:
    def test_defaults(self):
        v = VariableConfig()
        assert v.distribution == "deterministic"
        assert v.params == [0]

    def test_custom_params(self):
        v = VariableConfig(distribution="normal", params=[100, 15])
        assert v.distribution == "normal"
        assert v.params == [100, 15]

    def test_empty_params(self):
        v = VariableConfig()
        assert v.params == [0]


class TestFactorConfig:
    def test_defaults(self):
        f = FactorConfig(name="Cost", weight=0.5)
        assert f.maximize is True
        assert f.category == "General"

    def test_minimize(self):
        f = FactorConfig(name="Cost", weight=0.5, maximize=False, category="Financial")
        assert f.maximize is False
        assert f.category == "Financial"

    def test_negative_weight_raises(self):
        with pytest.raises(ValidationError):
            FactorConfig(name="Bad", weight=-1)

    def test_zero_weight_allowed(self):
        f = FactorConfig(name="Zero", weight=0)
        assert f.weight == 0


class TestOptionConfig:
    def test_defaults(self):
        o = OptionConfig(name="OptA")
        assert o.description == ""
        assert o.variables == {}

    def test_with_variables(self):
        o = OptionConfig(
            name="OptA",
            description="Test",
            variables={"X": VariableConfig(distribution="normal", params=[0, 1])},
        )
        assert o.variables["X"].distribution == "normal"


class TestDecisionConfig:
    def test_defaults(self):
        d = DecisionConfig()
        assert d.name == "Untitled Decision"
        assert d.mode == "standard"
        assert d.simulations == 10000
        assert d.factors == []
        assert d.options == []

    def test_zero_simulations_raises(self):
        with pytest.raises(ValidationError):
            DecisionConfig(simulations=0)

    def test_negative_simulations_raises(self):
        with pytest.raises(ValidationError):
            DecisionConfig(simulations=-1)

    def test_invalid_mode_allowed(self):
        d = DecisionConfig(mode="unknown")
        assert d.mode == "unknown"


class TestRootConfig:
    def test_defaults(self):
        r = RootConfig()
        assert r.decision.name == "Untitled Decision"

    def test_full_config(self):
        config = {
            "decision": {
                "name": "Test",
                "simulations": 5000,
                "factors": [
                    {"name": "Cost", "weight": 0.3, "maximize": False},
                    {"name": "Quality", "weight": 0.7, "maximize": True},
                ],
                "options": [
                    {
                        "name": "A",
                        "variables": {
                            "Cost": {"distribution": "deterministic", "params": [50]},
                            "Quality": {"distribution": "normal", "params": [8, 1]},
                        },
                    }
                ],
            }
        }
        r = RootConfig.model_validate(config)
        assert r.decision.name == "Test"
        assert len(r.decision.factors) == 2
        assert len(r.decision.options) == 1
        assert r.decision.factors[0].name == "Cost"
        assert r.decision.options[0].variables["Cost"].params == [50]

    def test_empty_config_dict(self):
        r = RootConfig.model_validate({})
        assert r.decision.simulations == 10000
        assert r.decision.factors == []

    def test_empty_decision(self):
        r = RootConfig.model_validate({"decision": {}})
        assert r.decision.simulations == 10000
        assert r.decision.factors == []

    def test_missing_factor_name_raises(self):
        with pytest.raises(ValidationError):
            RootConfig.model_validate({"decision": {"factors": [{"weight": 1.0}]}})
