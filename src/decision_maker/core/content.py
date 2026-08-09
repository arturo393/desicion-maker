"""
Centralized content templates for AI prompts and report copy.
Usage: from decision_maker.core.content import research_prompt, calibration_prompt, narrative_prompt
Does NOT: Query any model directly or render reports.
"""

from __future__ import annotations

__all__ = ["REPORT_CSS", "NarrativeContext", "research_prompt", "calibration_prompt", "narrative_prompt"]

from dataclasses import dataclass, field
from typing import Any


@dataclass
class NarrativeContext:
    """Bundles the decision facts needed to build an executive explanation prompt."""

    winner_name: str
    winner_score: float
    options: list[str] = field(default_factory=list)
    factors: list[str] = field(default_factory=list)
    waterfall: dict[str, Any] = field(default_factory=dict)
    counterfactual: dict[str, Any] = field(default_factory=dict)

REPORT_CSS = """
:root {
    --bg: #0d1117;
    --panel: #161b22;
    --border: #30363d;
    --text: #c9d1d9;
    --text-bright: #f0f6fc;
    --accent: #58a6ff;
    --success: #3fb950;
    --danger: #f85149;
    --warning: #d29922;
}

* { box-sizing: border-box; }
body {
    font-family: 'Inter', 'Segoe UI', system-ui, sans-serif;
    background: var(--bg);
    color: var(--text);
    margin: 0;
    padding: 2rem;
    line-height: 1.6;
}

.dashboard {
    display: grid;
    grid-template-columns: repeat(12, 1fr);
    gap: 1.5rem;
    max-width: 1400px;
    margin: 0 auto;
}

header {
    grid-column: span 12;
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
    padding-bottom: 2rem;
    border-bottom: 1px solid var(--border);
}

header h1 {
    margin: 0;
    font-size: 2rem;
    color: var(--text-bright);
    letter-spacing: -0.02em;
}

.badge {
    background: rgba(88, 166, 255, 0.1);
    color: var(--accent);
    padding: 0.4rem 1rem;
    border-radius: 6px;
    font-size: 0.75rem;
    font-weight: 700;
    border: 1px solid var(--border);
    text-transform: uppercase;
}

.kpi-card {
    grid-column: span 3;
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.5rem;
}

.kpi-title { font-size: 0.7rem; color: #8b949e; text-transform: uppercase; letter-spacing: 0.1em; font-weight: 700; margin-bottom: 0.5rem; }
.kpi-value { font-size: 2rem; font-weight: 700; color: var(--text-bright); }
.kpi-value.success { color: var(--success); }
.kpi-value.accent { color: var(--accent); }
.kpi-sub { font-size: 0.8rem; color: #8b949e; margin-top: 0.4rem; }

.panel {
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 2rem;
}

.panel-title {
    margin: 0 0 1.5rem 0;
    font-size: 1.2rem;
    font-weight: 600;
    color: var(--text-bright);
    display: flex;
    align-items: center;
    gap: 0.75rem;
}

.panel-title::before {
    content: '';
    display: block;
    width: 3px;
    height: 1.2rem;
    background: var(--accent);
    border-radius: 2px;
}

.col-8 { grid-column: span 8; }
.col-4 { grid-column: span 4; }
.col-12 { grid-column: span 12; }

table { width: 100%; border-collapse: collapse; }
th, td { padding: 1rem; text-align: left; border-bottom: 1px solid var(--border); }
th { color: #8b949e; font-weight: 600; font-size: 0.75rem; text-transform: uppercase; }

.stat-box {
    background: #0d1117;
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 1.25rem;
}
.stat-row { display: flex; justify-content: space-between; margin-bottom: 0.5rem; font-size: 0.9rem; }
.stat-label { color: #8b949e; }
.stat-val { font-family: 'JetBrains Mono', monospace; font-weight: 600; color: var(--text-bright); }

.stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1rem; }

.bar-track { width: 100%; background: var(--bg); border-radius: 4px; height: 1.75rem; position: relative; border: 1px solid var(--border); }
.bar-fill { height: 100%; background: linear-gradient(90deg, var(--accent) 0%, #388bfd 100%); position: absolute; left: 0; top: 0; border-radius: 3px; }
.bar-label { position: relative; z-index: 2; font-size: 0.8rem; font-weight: 600; margin-left: 0.75rem; color: #fff; line-height: 1.75rem; }

.viz-container {
    margin-top: 1rem;
    border-radius: 8px;
    overflow: hidden;
    border: 1px solid var(--border);
    background: #161b22;
}
.viz-container img { width: 100%; display: block; }

.explanation {
    font-size: 0.85rem;
    color: #8b949e;
    margin-top: 1rem;
    font-style: italic;
}

@media (max-width: 1100px) {
    .kpi-card, .col-8, .col-4 { grid-column: span 12; }
}
"""


def research_prompt(topic: str, context: str = "") -> str:
    """Build the prompt for open-ended AI research on a decision topic."""
    return f"Research Topic: {topic}\nContext: {context}\nProvide analysis."


def calibration_prompt(context_data: str) -> str:
    """Build the prompt asking the model to adjust distribution priors from real-world context."""
    return (
        "Given this context: "
        f"{context_data}\n"
        'Return ONLY a JSON dictionary where keys are variables and values are multiplier '
        'adjustments for their standard deviation. E.g. {"Cost": 1.2}'
    )


def narrative_prompt(ctx: NarrativeContext) -> str:
    """Build the prompt asking for a plain-language executive explanation of a decision."""
    return (
        "Explain this multi-criteria decision analysis in simple terms:\n"
        f"- Winner: {ctx.winner_name}\n"
        f"- Score: {ctx.winner_score:.3f}\n"
        f"- Options: {ctx.options}\n"
        f"- Factors: {ctx.factors}\n"
        f"- Waterfall: {ctx.waterfall}\n"
        f"- Counterfactual: {ctx.counterfactual}\n"
        "Provide a short paragraph a business executive would understand."
    )
