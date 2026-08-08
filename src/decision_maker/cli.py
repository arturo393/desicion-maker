"""
Command-line interface for executing decision analysis workflows and viewing reports.
Usage: python -m python.cli run --config config.json
Does NOT: Host persistent web service endpoints.
"""

#!/usr/bin/env python3
from __future__ import annotations

import asyncio
import logging
import sys
from pathlib import Path
from typing import Annotated

import typer

# Add project root to path so imports work
_project_root = str(Path(__file__).resolve().parent.parent)
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

import numpy as np  # noqa: E402

from decision_maker.core.config_runner import run_from_config  # noqa: E402
from decision_maker.core.models import DecisionOption, DistributionType, Factor  # noqa: E402
from decision_maker.core.orchestrator import UnifiedDecisionFramework  # noqa: E402
from decision_maker.core.what_if import WhatIfEngine  # noqa: E402

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
        str | None,
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
        str | None,
        typer.Option("--output", "-o", help="Results output directory"),
    ] = None,
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-v", help="Enable debug logging"),
    ] = False,
    correlation: Annotated[
        float | None,
        typer.Option("--correlation", help="Pairwise correlation between factors (0-1)"),
    ] = None,
    pref_type: Annotated[
        str | None,
        typer.Option("--pref-type", help="PROMETHEE preference type: usual, ushape, vshape, level, linear, gaussian"),
    ] = None,
    what_if: Annotated[
        bool,
        typer.Option("--what-if", "-w", help="Enter interactive what-if mode after analysis"),
    ] = False,
    explain: Annotated[
        bool,
        typer.Option("--explain", "-e", help="Generate AI narrative explanation via Gemini"),
    ] = False,
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
        result = asyncio.run(run_from_config(config, mode, ai, output))
    else:
        result = asyncio.run(_run_interactive(mode, simulations, ai, output, corr_matrix, pref_types))

    if explain and result:
        _generate_explanation(result)

    if what_if and result:
        _launch_what_if(result)


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
    output: str | None,
    correlation_matrix: np.ndarray | None = None,
    pref_types: list[str] | None = None,
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
        typer.echo("\nReports saved:")
        for fmt, path in files.items():
            typer.echo(f"  {fmt.upper()}: {path}")

    return result


def _launch_what_if(result: dict) -> None:
    """Launch interactive what-if REPL from analysis results."""
    mc_results = result.get("mc_results")
    factors = result.get("factors")
    if not mc_results or not factors:
        typer.echo("No results to explore in what-if mode.")
        return
    engine = WhatIfEngine(mc_results, factors)
    engine.repl()


def _generate_explanation(result: dict) -> None:
    """Generate AI narrative explanation from analysis results."""
    from decision_maker.core.gemini_agent import GeminiDeepResearchAgent

    mc = result.get("mc_results", {})
    if not mc:
        typer.echo("No results to explain.")
        return

    rankings = sorted(mc.items(), key=lambda x: x[1].mean_score, reverse=True)

    summary = (
        f"Decision analysis with {len(mc)} options:\n"
        + "\n".join(
            f"{i + 1}. {name}: mean={s.mean_score:.3f}, std={s.std_dev:.3f}, "
            f"VaR={s.var_95:.3f}, CVaR={s.cvar_95:.3f}, success_rate={s.success_rate:.1%}"
            for i, (name, s) in enumerate(rankings)
        )
        + "\n\n"
    )

    factors = result.get("factors", [])
    if factors:
        summary += (
            "Factors:\n" + "\n".join(f"  {f.name}: weight={f.weight}, maximize={f.maximize}" for f in factors) + "\n\n"
        )

    explanation = result.get("explanation", "")
    topology = result.get("topology", {})
    if topology and "error" not in topology:
        summary += f"Topology: {topology.get('num_options')} options in {topology.get('num_factors')} dimensions\n"
        if topology.get("clusters"):
            summary += f"Clusters detected: {len(topology['clusters'])}\n"

    agent = GeminiDeepResearchAgent()
    if not agent.is_available:
        typer.echo("Gemini API key not found. Set GEMINI_API_KEY or use --ai flag.")
        return

    typer.echo("\nGenerating AI explanation...")
    narrative = asyncio.run(
        agent.research(
            topic="Explain this decision analysis result in plain language. "
            "Who won, why, what are the key trade-offs, risks, and recommendations?",
            context=summary + "\nExisting Explanation:\n" + explanation,
        )
    )

    typer.echo("\n" + "=" * 70)
    typer.echo("AI NARRATIVE EXPLANATION")
    typer.echo("=" * 70)
    typer.echo(narrative)
    typer.echo("=" * 70 + "\n")


def main():
    if len(sys.argv) == 1:
        sys.argv.append("--help")
    app()


if __name__ == "__main__":
    main()
