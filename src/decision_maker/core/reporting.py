"""
Report generation suite saving analysis outcomes to JSON, Markdown, HTML, and terminal outputs.
Usage: from decision_maker.core.reporting import save_report, ReportData
Does NOT: Perform primary decision matrix computations or optimizations.
"""

from __future__ import annotations

__all__ = [
    "prepare_decision_matrix",
    "build_algorithm_comparison",
    "save_json_report",
    "save_markdown_report",
    "save_html_report",
    "print_report",
    "save_report",
    "ReportData",
]

import json
import logging
import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

import pandas as pd

from decision_maker.core.models import Factor, Statistics
from decision_maker.core.utils import resolve_winner

logger = logging.getLogger(__name__)


@dataclass
class ReportData:
    """Bundles all data needed for report generation."""

    mode: str
    mc_results: Dict[str, Statistics]
    topsis_scores: pd.Series
    strategies: Dict[str, str]
    pareto: Dict[str, Any]
    sensitivity: Dict[str, Any]
    future: Dict[str, Any]
    ai_reports: Dict[str, str]
    factors: List[Factor]
    results_dir: str = ""
    timestamp: str = ""
    explanation: str = ""
    waterfall: Optional[Dict] = None
    counterfactual: Optional[Dict] = None
    decision_matrix: Dict[str, Any] = field(default_factory=dict)
    algo_comp: Dict[str, Any] = field(default_factory=dict)

    def prepare(self) -> ReportData:
        """Compute derived fields from raw input data."""
        if not self.decision_matrix:
            self.decision_matrix = prepare_decision_matrix(self.mc_results, self.factors)
        if not self.algo_comp:
            self.algo_comp = build_algorithm_comparison(self.mc_results, self.topsis_scores, self.future)
        if not self.timestamp:
            self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if not self.results_dir:
            self.results_dir = os.path.join(os.getcwd(), "results")
        return self


# ── Shared helper functions ──────────────────────────────────────────


def _md_table(
    headers: List[str],
    rows: List[List[str]],
    alignments: Optional[List[str]] = None,
) -> str:
    """Build a complete markdown table string."""
    if alignments is None:
        alignments = [":---"] * len(headers)
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(alignments) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines) + "\n"


def _mc_context(mc_results: Dict[str, Statistics]) -> Dict[str, Any]:
    """Extract common MC statistics used across report functions."""
    best_name, best_stats = max(mc_results.items(), key=lambda x: x[1].mean_score)
    return {
        "best_name": best_name,
        "best_score": best_stats.mean_score,
        "max_score": best_stats.mean_score,
        "max_label_len": max(len(n) for n in mc_results),
    }


def _bar_chart(mc_results: Dict[str, Statistics], width: int = 40) -> str:
    """Build an ASCII bar chart string from MC results."""
    ctx = _mc_context(mc_results)
    lines = []
    for name, stats in mc_results.items():
        bar_len = int((stats.mean_score / ctx["max_score"]) * width) if ctx["max_score"] > 0 else 0
        bar = "\u2588" * bar_len
        lines.append(f"{name:<{ctx['max_label_len']}} | {bar} {stats.mean_score:.0f}")
    return "\n".join(lines)


def _has_promethee(mode: str, future: Optional[Dict[str, Any]]) -> bool:
    """Check if PROMETHEE data is available."""
    return bool(mode == "advanced" and future and "promethee_scores" in future and not future["promethee_scores"].empty)


def _rank_scores(scores: pd.Series, prefix: str) -> Dict[str, Dict[str, Any]]:
    """Rank a Series and return dict with rank/score per option."""
    result: Dict[str, Dict[str, Any]] = {}
    for rank, (name, score) in enumerate(scores.sort_values(ascending=False).items(), 1):
        result.setdefault(name, {})
        result[name][f"{prefix}_rank"] = rank
        result[name][f"{prefix}_score"] = score
    return result


def prepare_decision_matrix(mc_results: Dict[str, Statistics], factors: List[Factor]) -> Dict[str, Any]:
    decision_matrix = {}
    for name, stats in mc_results.items():
        decision_matrix[name] = {"total_score": stats.mean_score}
        for factor in factors:
            if factor.name in stats.factor_stats:
                f_stats = stats.factor_stats[factor.name]
                mean_val = f_stats["mean"]
                contribution = mean_val * factor.weight if factor.maximize else -mean_val * factor.weight
                decision_matrix[name][factor.name] = {
                    "raw": mean_val,
                    "weight": factor.weight,
                    "contribution": contribution,
                    "maximize": factor.maximize,
                }
    return decision_matrix


def build_algorithm_comparison(
    mc_results: Dict[str, Statistics],
    topsis_scores: pd.Series,
    future: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    algo_comp: Dict[str, Any] = {}
    sorted_mc = sorted(mc_results.items(), key=lambda x: x[1].mean_score, reverse=True)
    for rank, (name, stats) in enumerate(sorted_mc, 1):
        algo_comp.setdefault(name, {})
        algo_comp[name]["mc_rank"] = rank
        algo_comp[name]["mc_score"] = stats.mean_score

    if not topsis_scores.empty:
        for name, data in _rank_scores(topsis_scores, "topsis").items():
            algo_comp.setdefault(name, {})
            algo_comp[name].update(data)

    if _has_promethee("advanced", future):
        for name, data in _rank_scores(future["promethee_scores"], "promethee").items():
            algo_comp.setdefault(name, {})
            algo_comp[name].update(data)
    return algo_comp


def save_json_report(
    results_dir: str,
    timestamp: str,
    mc_results: Dict[str, Statistics],
    topsis_scores: pd.Series,
    decision_matrix: Dict[str, Any],
    algo_comp: Dict[str, Any],
    ai_reports: Dict[str, str],
) -> str:
    json_data = {
        "timestamp": timestamp,
        "decision_matrix": decision_matrix,
        "monte_carlo": {
            name: {
                "mean": stats.mean_score,
                "std": stats.std_dev,
                "min": stats.min_score,
                "max": stats.max_score,
                "p5": stats.percentile_5,
                "p95": stats.percentile_95,
                "var_95": stats.var_95,
                "cvar_95": stats.cvar_95,
                "success_rate": stats.success_rate,
            }
            for name, stats in mc_results.items()
        },
        "topsis": topsis_scores.to_dict() if not topsis_scores.empty else {},
        "algorithm_comparison": algo_comp,
        "ai_insights": ai_reports,
    }
    json_path = os.path.join(results_dir, f"analysis_{timestamp}.json")
    with open(json_path, "w") as f:
        json.dump(json_data, f, indent=2)
    logger.debug(f"JSON report saved to {json_path}")
    return json_path


def save_markdown_report(data: ReportData) -> str:
    bluf_winner, bluf_reason = resolve_winner(data.topsis_scores, data.mc_results)
    mc_winner = max(data.mc_results.values(), key=lambda x: x.mean_score).option_name
    lines = [
        "# Decision Analysis Report\n",
        f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"**Execution Tier:** {data.mode.upper()}\n",
        "## Visual Insights\n",
        f"![Risk Profiles](risk_profiles_{data.timestamp}.png)\n",
        f"![Factor Importance](factor_importance_{data.timestamp}.png)\n",
        f"![Robustness Audit](robustness_audit_{data.timestamp}.png)\n",
        "## 1. Executive Summary\n",
        f"> **Recommended Strategy:** **{bluf_winner}** is the most balanced option ({bluf_reason}), ideal for minimizing risk across all fronts. However, **{mc_winner}** offers the highest direct expected value (Monte Carlo).\n",
        f"**Situation Analysis:** {bluf_reason}. "
        + (
            "Warning: **Low Robustness:** The current decision is volatile."
            if data.sensitivity.get("robustness_score", 0) * 100 < 30
            else ""
        )
        + "\n",
        "### 1.1 Algorithm Consensus",
    ]

    has_prom = _has_promethee(data.mode, data.future)
    headers = ["Option", "MC Rank", "F-TOPSIS Rank"] + (["PROMETHEE Rank"] if has_prom else [])
    rows = []
    for name, comp_data in data.algo_comp.items():
        r = [f"**{name}**", f"#{comp_data.get('mc_rank')}", f"#{comp_data.get('topsis_rank', '-')}"]
        if has_prom:
            r.append(f"#{comp_data.get('promethee_rank', '-')}")
        rows.append(r)
    lines.append(_md_table(headers, rows))

    lines.extend(
        [
            "### 1.2 Visual Summary (Expected Value)\n```text",
            _bar_chart(data.mc_results),
            "```\n",
            "### 1.3 Strategic Option Set (Pareto Efficiency)",
            f"- **Pareto Efficient Options:** {', '.join(data.pareto.get('efficient_frontier', []))}",
        ]
    )
    if data.pareto.get("dominated_options"):
        lines.append("- **Dominated Options:**")
        for loser, winner in data.pareto["dominated_options"]:
            lines.append(f"  - {loser} (Dominated by {winner})")

    if data.mode in ("standard", "advanced") and data.sensitivity:
        lines.extend(
            [
                "\n### 1.4 Stability Diagnosis",
                f"- **Priority Consistency:** {data.sensitivity.get('robustness_score', 0) * 100:.0f}%",
            ]
        )
        for c in data.sensitivity.get("weight_changes", []):
            lines.append(
                f"  - If **{c['factor']}** weight changes by {c['change']} -> Winner flips to **{c['new_winner']}**"
            )
        for c in data.sensitivity.get("score_changes", []):
            lines.append(
                f"  - If **{c['factor']}** score changes by {c['change']} -> Winner flips to **{c['new_winner']}**"
            )

        if data.future.get("robust_optimizer"):
            dro_rows = [
                [
                    opt,
                    f"{score:.2f}",
                    f"{data.future['robust_optimizer'].get('stability_metrics', {}).get(opt, 0) * 100:.1f}%",
                ]
                for opt, score in data.future["robust_optimizer"].get("dro_scores", {}).items()
            ]
            lines.extend(
                [
                    "\n### 1.5 Distributionally Robust Optimization (DRO)",
                    _md_table(["Option", "DRO Score", "Stability"], dro_rows),
                ]
            )

    dm_headers = ["Option"] + [f"{f.name} (w={f.weight})" for f in data.factors] + ["**Total Score**"]
    dm_rows = [
        [f"**{n}**"]
        + [f"{d[f.name]['raw']:.2f} ({d[f.name]['contribution']:+.2f})" if f.name in d else "N/A" for f in data.factors]
        + [f"**{d['total_score']:.2f}**"]
        for n, d in data.decision_matrix.items()
    ]
    lines.extend(["\n## 2. Detailed Analysis\n\n### 2.1 Decision Matrix", _md_table(dm_headers, dm_rows)])

    if data.explanation:
        lines.extend(["\n## 2. Decision Explanation", data.explanation])

    md_path = os.path.join(data.results_dir, f"report_{data.timestamp}.md")
    with open(md_path, "w") as f:
        f.write("\n".join(lines) + "\n")
    logger.debug(f"Markdown report saved to {md_path}")
    return md_path


def save_html_report(data: ReportData) -> str:
    try:
        from jinja2 import Environment, FileSystemLoader

        env = Environment(loader=FileSystemLoader(os.path.join(os.path.dirname(__file__), "templates")))
        template = env.get_template("report.html.j2")
    except Exception:
        logger.warning("Jinja2 not available, falling back to inline HTML generation")
        return _generate_html_inline(data)

    bluf_winner, _ = resolve_winner(data.topsis_scores, data.mc_results)
    best_mc = max(data.mc_results.items(), key=lambda x: x[1].mean_score)[0]
    robust_raw = data.sensitivity.get("robustness_score", 0) * 100 if data.sensitivity else 0
    max_score = max(s.mean_score for s in data.mc_results.values()) if data.mc_results else 1

    mc_data = [
        {"name": n, "mean": s.mean_score, "pct": (s.mean_score / max_score) * 100 if max_score > 0 else 0}
        for n, s in data.mc_results.items()
    ]
    kpi_cards = [
        {"title": "Balanced Recommendation", "value": bluf_winner, "sub": "Winner by balance", "class": "success"},
        {"title": "Maximum Expected Value", "value": best_mc, "sub": "Best average score", "class": ""},
        {
            "title": "Criterion Consistency",
            "value": f"{robust_raw:.0f}%",
            "sub": "Stability score",
            "class": "accent" if robust_raw > 50 else "warning",
        },
    ]
    criteria = [
        {
            "name": f.name,
            "weight": f.weight,
            "direction": "Maximize" if f.maximize else "Minimize",
            "maximize": f.maximize,
        }
        for f in data.factors
    ]
    risk_profiles = [
        {"name": n, "mean": s.mean_score, "std": s.std_dev, "var_95": s.var_95, "cvar_95": s.cvar_95}
        for n, s in data.mc_results.items()
    ]

    html = template.render(
        timestamp=data.timestamp,
        mode=data.mode,
        date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        kpi_cards=kpi_cards,
        criteria=criteria,
        mc_data=mc_data,
        algo_comp=data.algo_comp,
        has_prom=data.mode == "advanced" and data.future and "promethee_scores" in data.future,
        advanced_insights={},
        risk_profiles=risk_profiles,
        explanation=data.explanation,
    )
    html_path = os.path.join(data.results_dir, f"report_{data.timestamp}.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)
    logger.debug(f"HTML report saved to {html_path}")
    return html_path


def _generate_html_inline(data: ReportData) -> str:
    from decision_maker.core.html_fallback import generate_html_inline

    return generate_html_inline(
        data.results_dir,
        data.timestamp,
        data.mode,
        data.mc_results,
        data.topsis_scores,
        data.strategies,
        data.pareto,
        data.sensitivity,
        data.future,
        data.ai_reports,
        data.algo_comp,
        data.decision_matrix,
        data.factors,
        explanation=data.explanation,
    )


def print_report(data: ReportData):
    if data.explanation:
        print("\n" + "-" * 70 + "\nDECISION EXPLANATION\n" + "-" * 70 + f"\n{data.explanation}")
    bluf_winner, bluf_reason = resolve_winner(data.topsis_scores, data.mc_results)
    print("\n" + "=" * 70 + f"\nDECISION ANALYSIS REPORT ({data.mode.upper()} TIER)\n" + "=" * 70 + "\n")
    print(f"RECOMMENDATION: {bluf_winner} is optimal based on {bluf_reason}.\n")
    print(_bar_chart(data.mc_results))


def save_report(
    mode: str,
    mc_results: Dict[str, Statistics],
    topsis_scores: pd.Series,
    strategies: Dict[str, str],
    pareto: Dict[str, Any],
    sensitivity: Dict[str, Any],
    future: Dict[str, Any],
    ai_reports: Dict[str, str],
    factors: List[Factor],
    results_dir: Optional[str] = None,
    explanation: str = "",
    waterfall: Optional[Dict] = None,
    counterfactual: Optional[Dict] = None,
) -> Dict[str, str]:
    data = ReportData(
        mode=mode,
        mc_results=mc_results,
        topsis_scores=topsis_scores,
        strategies=strategies,
        pareto=pareto,
        sensitivity=sensitivity,
        future=future,
        ai_reports=ai_reports,
        factors=factors,
        results_dir=results_dir or os.path.join(os.getcwd(), "results"),
        timestamp=datetime.now().strftime("%Y%m%d_%H%M%S"),
        explanation=explanation,
        waterfall=waterfall,
        counterfactual=counterfactual,
    ).prepare()

    json_path = save_json_report(
        data.results_dir,
        data.timestamp,
        data.mc_results,
        data.topsis_scores,
        data.decision_matrix,
        data.algo_comp,
        data.ai_reports,
    )
    md_path = save_markdown_report(data)
    html_path = save_html_report(data)
    return {"json": json_path, "md": md_path, "html": html_path, "timestamp": data.timestamp}
