"""
CLI commands for the decision ledger: decide, review, close, calibration.
Usage: decision-maker decide --option B --confidence 0.7 --metric "piloto operativo" --review-by 2026-12-01
Does NOT: run analyses (cli.run does), or decide anything a person did not type.
"""

from __future__ import annotations

__all__ = ["register", "show_commitment_draft"]

import json
from dataclasses import asdict
from datetime import date
from typing import Annotated

import typer

from decision_maker.core.decision_commitment import DecisionCommitment, ledger_path


def register(app: typer.Typer) -> None:
    """Attach the ledger commands to the main CLI."""
    app.command()(decide)
    app.command()(review)
    app.command()(close)
    app.command()(calibration)


def show_commitment_draft(result: dict) -> None:
    """After a run: show what the analysis recommends and the command that would commit to it."""
    draft = result.get("commitment_draft")
    if not draft:
        return
    typer.echo(f"\nRecommendation: {draft['chosen_option']} (confidence {draft['confidence']:.2f})")
    typer.echo("Nothing was committed. If you take this decision, record it:")
    typer.echo(
        f'  decision-maker decide --option "{draft["chosen_option"]}" --confidence {draft["confidence"]:.2f} '
        '--metric "<what you will observe if it worked>" --review-by YYYY-MM-DD'
    )


def decide(
    option: Annotated[str, typer.Option("--option", help="The option you chose")],
    confidence: Annotated[float, typer.Option("--confidence", help="Probability it works, in (0, 1]")],
    metric: Annotated[str, typer.Option("--metric", help="What you will observe if it worked")],
    review_by: Annotated[str, typer.Option("--review-by", help="Date to check the outcome, YYYY-MM-DD")],
    reasoning: Annotated[str, typer.Option("--reasoning", help="Why this option")] = "",
    exit_criteria: Annotated[str, typer.Option("--exit", help="What would make you reverse it")] = "",
    pre_mortem: Annotated[str, typer.Option("--pre-mortem", help="The most likely way this fails")] = "",
    irreversible: Annotated[bool, typer.Option("--irreversible", help="It cannot be undone")] = False,
    tag: Annotated[list[str] | None, typer.Option("--tag", help="Repeatable")] = None,
) -> None:
    """Record a decision you took in the ledger."""
    ledger = DecisionCommitment()
    try:
        c = ledger.create(
            option, confidence, metric, review_by,
            reasoning=reasoning, reversible=not irreversible,
            exit_criteria=exit_criteria, pre_mortem=pre_mortem, tags=tag or [],
        )
    except ValueError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1) from e
    typer.echo(f"{c.decision_id}: {c.chosen_option}, review on {c.review_date} ({ledger.path})")


JsonFlag = Annotated[bool, typer.Option("--json", help="Machine-readable output, for other tools and repos")]


def review(as_json: JsonFlag = False) -> None:
    """List open decisions: the ones whose review date arrived first."""
    ledger = DecisionCommitment()
    due = ledger.due()
    later = [e for e in ledger.open() if e not in due]
    if as_json:
        rows = [{**asdict(e), "due": e in due} for e in due + sorted(later, key=lambda e: e.review_date)]
        typer.echo(json.dumps({"ledger": str(ledger.path), "today": date.today().isoformat(), "open": rows}))
        return
    if not due and not later:
        typer.echo(f"No open decisions in {ledger_path()}")
        return
    for title, section in (("DUE", due), ("Upcoming", sorted(later, key=lambda e: e.review_date))):
        if section:
            typer.echo(f"\n{title}:")
            for e in section:
                typer.echo(f"  {e.review_date}  {e.decision_id}  {e.chosen_option}  p={e.confidence:.2f}  — {e.success_metric}")
    if due:
        typer.echo("\nClose each one: decision-maker close <id> --success|--failure --result \"...\"")


def close(
    decision_id: Annotated[str, typer.Argument(help="Id printed by decide / review")],
    success: Annotated[bool, typer.Option("--success/--failure", help="Did the metric hold?")],
    result: Annotated[str, typer.Option("--result", help="What actually happened")] = "",
    post_mortem: Annotated[str, typer.Option("--post-mortem", help="What you would do differently")] = "",
) -> None:
    """Close a decision with its outcome."""
    if not DecisionCommitment().record_outcome(decision_id, success, result, post_mortem):
        typer.echo(f"Error: {decision_id} is not in {ledger_path()}", err=True)
        raise typer.Exit(code=1)
    typer.echo(f"{decision_id}: {'success' if success else 'failure'} recorded")


def calibration(as_json: JsonFlag = False) -> None:
    """How well stated confidence matched outcomes, over closed decisions."""
    ledger = DecisionCommitment()
    s = ledger.summary()
    cal = ledger.calibration()
    if as_json:
        typer.echo(json.dumps({"summary": s, "calibration": cal}))
        return
    typer.echo(f"Ledger {ledger.path}: {s['total']} decisions, {s['closed']} closed, {s['due']} due")
    if cal["num_predictions"] == 0:
        typer.echo("No closed decisions yet: calibration needs outcomes, not runs.")
        return
    typer.echo(f"Brier score: {cal['brier_score']:.3f}  (0 is perfect, 0.25 is a coin flip at 50%)")
    typer.echo(f"ECE: {cal['ece']:.3f}   verdict: {cal['verdict']}")
