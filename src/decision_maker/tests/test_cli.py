from __future__ import annotations

import os
import tempfile

import pytest
import yaml
from typer.testing import CliRunner

from decision_maker.cli import app


def _write_config(tmpdir, mode="express"):
    config = {
        "decision": {
            "name": "CLI Config Test",
            "mode": mode,
            "simulations": 10,
            "factors": [{"name": "Cost", "weight": 1.0, "maximize": False}],
            "options": [
                {
                    "name": "A",
                    "variables": {"Cost": {"distribution": "deterministic", "params": [50]}},
                },
                {
                    "name": "B",
                    "variables": {"Cost": {"distribution": "deterministic", "params": [100]}},
                },
            ],
        }
    }
    path = os.path.join(tmpdir, "config.yaml")
    with open(path, "w") as f:
        yaml.dump(config, f)
    return path


class TestCli:
    def test_help_exits_zero(self):
        runner = CliRunner()
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "run" in result.output
        assert "list-distributions" in result.output

    def test_list_distributions(self):
        runner = CliRunner()
        result = runner.invoke(app, ["list-distributions"])
        assert result.exit_code == 0
        assert "normal" in result.output
        assert "poisson" in result.output
        assert "deterministic" in result.output

    def test_run_missing_config_raises(self):
        runner = CliRunner()
        result = runner.invoke(app, ["run", "--config", "/nonexistent/config.yaml"])
        assert result.exit_code != 0
        assert "not found" in result.output.lower() or "FileNotFoundError" in result.output

    def test_run_interactive_express(self):
        runner = CliRunner()
        result = runner.invoke(
            app,
            ["run", "--mode", "express", "--sims", "10", "--output", "/tmp/opencode/cli_test_out"],
        )
        assert result.exit_code == 0
        assert "Reports saved" in result.output

    def test_run_invalid_mode_falls_back(self):
        runner = CliRunner()
        result = runner.invoke(
            app,
            ["run", "--mode", "bogus", "--sims", "10", "--output", "/tmp/opencode/cli_test_out2"],
        )
        assert result.exit_code == 0
        assert "Reports saved" in result.output

    def test_run_with_config(self, tmp_path):
        config = _write_config(str(tmp_path))
        runner = CliRunner()
        result = runner.invoke(
            app,
            ["run", "--config", config, "--output", str(tmp_path / "out")],
        )
        assert result.exit_code == 0, result.output
        assert "Reports saved" in result.output

    def test_run_with_config_mode_override(self, tmp_path):
        config = _write_config(str(tmp_path), mode="advanced")
        runner = CliRunner()
        result = runner.invoke(
            app,
            ["run", "--config", config, "--mode", "express", "--output", str(tmp_path / "out2")],
        )
        assert result.exit_code == 0, result.output
        assert "Reports saved" in result.output

    def test_run_what_if_exits_on_eof(self):
        runner = CliRunner()
        result = runner.invoke(
            app,
            ["run", "--mode", "express", "--sims", "10", "--what-if"],
            input="quit\n",
        )
        assert result.exit_code == 0
