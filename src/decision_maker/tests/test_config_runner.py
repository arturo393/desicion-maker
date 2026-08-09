import asyncio
import os
import tempfile

import pytest
import yaml
from pydantic import ValidationError

from decision_maker.core.config_runner import (
    build_framework_from_config,
    load_decision_config,
    run_from_config,
)


class TestConfigRunner:
    def test_load_decision_config(self):
        config_data = {
            "decision": {
                "name": "Test Decision",
                "simulations": 100,
                "factors": [{"name": "Cost", "weight": 0.5, "maximize": False}],
                "options": [
                    {
                        "name": "Option A",
                        "variables": {"Cost": {"distribution": "deterministic", "params": [100]}},
                    }
                ],
            }
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(config_data, f)
            config_path = f.name

        try:
            config = load_decision_config(config_path)
            assert config["decision"]["name"] == "Test Decision"
        finally:
            os.unlink(config_path)

    def test_build_framework_from_config(self):
        config = {
            "decision": {
                "simulations": 100,
                "factors": [
                    {"name": "Cost", "weight": 0.5, "maximize": False},
                    {"name": "Quality", "weight": 0.5, "maximize": True},
                ],
                "options": [
                    {
                        "name": "Cheap",
                        "description": "Low cost option",
                        "variables": {
                            "Cost": {"distribution": "deterministic", "params": [50]},
                            "Quality": {"distribution": "normal", "params": [5, 1]},
                        },
                    },
                    {
                        "name": "Good",
                        "description": "High quality option",
                        "variables": {
                            "Cost": {"distribution": "deterministic", "params": [100]},
                            "Quality": {"distribution": "normal", "params": [9, 0.5]},
                        },
                    },
                ],
            }
        }

        framework = build_framework_from_config(config)
        assert len(framework.mc_engine.factors) == 2
        assert len(framework.mc_engine.options) == 2
        assert framework.mc_engine.num_simulations == 100

    def test_empty_config_dict_builds_default(self):
        framework = build_framework_from_config({})
        assert framework.mc_engine.num_simulations == 10000
        assert len(framework.mc_engine.factors) == 0
        assert len(framework.mc_engine.options) == 0

    def test_empty_decision_builds_default(self):
        framework = build_framework_from_config({"decision": {}})
        assert framework.mc_engine.num_simulations == 10000
        assert len(framework.mc_engine.factors) == 0
        assert len(framework.mc_engine.options) == 0

    def test_missing_factor_name_raises_keyerror(self):
        config = {"decision": {"factors": [{"weight": 1.0}]}}
        with pytest.raises(ValidationError):
            build_framework_from_config(config)

    def test_invalid_yaml_raises_error(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("invalid: yaml: [broken\n  bad")
            config_path = f.name
        try:
            with pytest.raises(Exception, match=".*"):
                load_decision_config(config_path)
        finally:
            os.unlink(config_path)

    def test_build_framework_default_simulations(self):
        config = {
            "decision": {
                "factors": [{"name": "X", "weight": 1.0, "maximize": True}],
                "options": [{"name": "A", "variables": {"X": {"distribution": "deterministic", "params": [10]}}}],
            }
        }
        framework = build_framework_from_config(config)
        assert framework.mc_engine.num_simulations == 10000

    def _write_config(self, mode: str):
        config_data = {
            "decision": {
                "name": "Mode Test",
                "mode": mode,
                "simulations": 10,
                "factors": [{"name": "Cost", "weight": 1.0, "maximize": False}],
                "options": [
                    {
                        "name": "Option A",
                        "variables": {"Cost": {"distribution": "deterministic", "params": [100]}},
                    }
                ],
            }
        }
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(config_data, f)
            return f.name

    @pytest.mark.asyncio
    async def test_run_from_config_respects_cli_mode_override(self):
        config_path = self._write_config(mode="advanced")
        try:
            result = await run_from_config(config_path, mode="express")
            assert result.get("mode") == "express"
        finally:
            os.unlink(config_path)

    @pytest.mark.asyncio
    async def test_run_from_config_uses_config_mode_when_no_override(self):
        config_path = self._write_config(mode="advanced")
        try:
            result = await run_from_config(config_path)
            assert result.get("mode") == "advanced"
        finally:
            os.unlink(config_path)
