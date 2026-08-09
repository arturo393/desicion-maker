from __future__ import annotations

import pytest
from typer.testing import CliRunner

from decision_maker.cli import app


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
