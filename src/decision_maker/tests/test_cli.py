from __future__ import annotations

import os

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
            ["run", "--mode", "express", "--sims", "1000", "--output", "/tmp/opencode/cli_test_out"],
        )
        assert result.exit_code == 0
        assert "Reports saved" in result.output

    def test_run_invalid_mode_falls_back(self):
        runner = CliRunner()
        result = runner.invoke(
            app,
            ["run", "--mode", "bogus", "--sims", "1000", "--output", "/tmp/opencode/cli_test_out2"],
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


class TestLedgerCommands:
    """decide → review → close → calibration, end to end through the CLI, against a temp ledger."""

    def test_full_cycle(self, tmp_path, monkeypatch):
        ledger = tmp_path / "ledger.jsonl"
        monkeypatch.setenv("DM_LEDGER_PATH", str(ledger))
        runner = CliRunner()

        r = runner.invoke(app, ["decide", "--option", "B", "--confidence", "0.8",
                                "--metric", "piloto operativo en faena", "--review-by", "2099-01-01"])
        assert r.exit_code == 0, r.output
        decision_id = r.output.split(":")[0].strip()
        assert ledger.exists()

        r = runner.invoke(app, ["review"])
        assert decision_id in r.output
        assert "Upcoming" in r.output

        r = runner.invoke(app, ["close", decision_id, "--failure", "--result", "llegó tarde"])
        assert r.exit_code == 0, r.output

        r = runner.invoke(app, ["calibration"])
        assert "Brier score: 0.640" in r.output  # (0.8 - 0)^2

    def test_decide_refuses_a_model_statistic_as_metric(self, tmp_path, monkeypatch):
        monkeypatch.setenv("DM_LEDGER_PATH", str(tmp_path / "ledger.jsonl"))
        r = CliRunner().invoke(app, ["decide", "--option", "B", "--confidence", "0.8",
                                     "--metric", "mean_score >= 0.6", "--review-by", "2099-01-01"])
        assert r.exit_code == 1
        assert not (tmp_path / "ledger.jsonl").exists()

    def test_json_output_is_parseable(self, tmp_path, monkeypatch):
        import json

        monkeypatch.setenv("DM_LEDGER_PATH", str(tmp_path / "ledger.jsonl"))
        runner = CliRunner()
        runner.invoke(app, ["decide", "--option", "B", "--confidence", "0.6",
                            "--metric", "piloto operativo", "--review-by", "2099-01-01"])
        open_rows = json.loads(runner.invoke(app, ["review", "--json"]).output)["open"]
        assert [(r["chosen_option"], r["due"]) for r in open_rows] == [("B", False)]
        cal = json.loads(runner.invoke(app, ["calibration", "--json"]).output)
        assert cal["summary"]["open"] == 1
        assert cal["calibration"]["num_predictions"] == 0

    def test_close_unknown_id_fails(self, tmp_path, monkeypatch):
        monkeypatch.setenv("DM_LEDGER_PATH", str(tmp_path / "ledger.jsonl"))
        r = CliRunner().invoke(app, ["close", "commit_nope", "--success"])
        assert r.exit_code == 1
