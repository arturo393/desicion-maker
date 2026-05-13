#!/usr/bin/env python3
from __future__ import annotations

import asyncio
import logging
import os
import sys
from pathlib import Path
from typing import Optional

import typer
from typing_extensions import Annotated

# Add project root to path so imports work
_project_root = str(Path(__file__).resolve().parent.parent)
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

import numpy as np

from python.core.config_runner import run_from_config
from python.core.models import DecisionOption, DistributionType, Factor
from python.core.orchestrator import UnifiedDecisionFramework

app = typer.Typer(
    name="decision-maker",
    help="Multi-Criteria Decision Intelligence Framework with Monte Carlo simulation",
    add_completion=False,
)

logging.basicConfig(
    level=logging.WARNING,
    format="%(levelname)s: %(message)s",
)


@app.command()
def run(
    config: Annotated[
        Optional[str],
        typer.Option("--config", "-c", help="Path to YAML config file"),
    ] = None,
    mode: Annotated[
        str,
        typer.Option("--mode", "-m", help="Execution tier: express, standard, advanced"),
    ] = "standard",
    simulations: Annotated[
        int,
        typer.Option("--sims", "-s", help="Number of Monte Carlo simulations"),
    ] = 10000,
    ai: Annotated[
        bool,
        typer.Option("--ai", help="Enable Gemini AI deep research"),
    ] = False,
    output: Annotated[
        Optional[str],
        typer.Option("--output", "-o", help="Results output directory"),
    ] = None,
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-v", help="Enable debug logging"),
    ] = False,
    correlation: Annotated[
        Optional[float],
        typer.Option("--correlation", help="Pairwise correlation between factors (0-1)"),
    ] = None,
    pref_type: Annotated[
        Optional[str],
        typer.Option("--pref-type", help="PROMETHEE preference type: usual, ushape, vshape, level, linear, gaussian"),
    ] = None,
):
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    corr_matrix = None
    if correlation is not None:
        n_factors = 0
        if config:
            import yaml
            with open(config) as f:
                cfg = yaml.safe_load(f)
            n_factors = len(cfg.get("decision", {}).get("factors", []))
        if n_factors > 0:
            off_diag = correlation
            corr_matrix = np.full((n_factors, n_factors), off_diag)
            np.fill_diagonal(corr_matrix, 1.0)

    pref_types = [pref_type] if pref_type else None

    if config:
        asyncio.run(run_from_config(config, mode, ai, output))
    else:
        asyncio.run(_run_interactive(mode, simulations, ai, output, corr_matrix, pref_types))


@app.command()
def list_distributions():
    """List all available probability distributions and their parameters."""
    typer.echo("Available Distributions:")
    typer.echo("")
    typer.echo("  deterministic  params: [value]")
    typer.echo("  normal         params: [mean, std]")
    typer.echo("  uniform        params: [low, high]")
    typer.echo("  triangular     params: [left, mode, right]")
    typer.echo("  bernoulli      params: [p]")
    typer.echo("  exponential    params: [scale]")
    typer.echo("  beta           params: [alpha, beta]")
    typer.echo("  lognormal      params: [mean, sigma]")
    typer.echo("  gamma          params: [shape, scale]")
    typer.echo("  poisson        params: [lam]")


async def _run_interactive(
    mode: str,
    simulations: int,
    use_ai: bool,
    output: Optional[str],
    correlation_matrix: Optional[np.ndarray] = None,
    pref_types: Optional[list[str]] = None,
):
    framework = UnifiedDecisionFramework(
        correlation_matrix=correlation_matrix,
        promethee_pref_types=pref_types,
    )
    framework.mc_engine.num_simulations = simulations

    framework.add_factor(Factor("Cost", 0.4, maximize=False))
    framework.add_factor(Factor("ROI", 0.4, maximize=True))
    framework.add_factor(Factor("Risk", 0.2, maximize=False))

    opt_a = DecisionOption("Conservative Option", "Safe bet")
    opt_a.add_variable("Cost", DistributionType.DETERMINISTIC, 1000)
    opt_a.add_variable("ROI", DistributionType.NORMAL, 1.2, 0.1)
    opt_a.add_variable("Risk", DistributionType.DETERMINISTIC, 2)
    framework.add_option(opt_a)

    opt_b = DecisionOption("Aggressive Option", "High risk, high reward")
    opt_b.add_variable("Cost", DistributionType.TRIANGULAR, 800, 1200, 1500)
    opt_b.add_variable("ROI", DistributionType.NORMAL, 2.5, 0.8)
    opt_b.add_variable("Risk", DistributionType.UNIFORM, 5, 9)
    framework.add_option(opt_b)

    typer.echo(f"Running {mode} analysis with {simulations} simulations...")
    result = await framework.run_analysis(mode=mode, use_ai=use_ai, results_dir=output)

    files = result.get("files", {})
    if files:
        typer.echo(f"\nReports saved:")
        for fmt, path in files.items():
            typer.echo(f"  {fmt.upper()}: {path}")


def main():
    if len(sys.argv) == 1:
        sys.argv.append("--help")
    app()


if __name__ == "__main__":
    main()
