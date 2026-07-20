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

from python.core.models import Factor, Statistics
from python.core.utils import resolve_winner

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
    return bool(
        mode == "advanced"
        and future
        and "promethee_scores" in future
        and not future["promethee_scores"].empty
    )


def _rank_scores(scores: pd.Series, prefix: str) -> Dict[str, Dict[str, Any]]:
    """Rank a Series and return dict with rank/score per option."""
    result: Dict[str, Dict[str, Any]] = {}
    for rank, (name, score) in enumerate(scores.sort_values(ascending=False).items(), 1):
        result.setdefault(name, {})
        result[name][f"{prefix}_rank"] = rank
        result[name][f"{prefix}_score"] = score
    return result


def prepare_decision_matrix(
    mc_results: Dict[str, Statistics], factors: List[Factor]
) -> Dict[str, Any]:
    decision_matrix = {}
    for name, stats in mc_results.items():
        decision_matrix[name] = {"total_score": stats.mean_score}
        for factor in factors:
            if factor.name in stats.factor_stats:
                f_stats = stats.factor_stats[factor.name]
                mean_val = f_stats["mean"]
                contribution = mean_val * factor.weight
                if not factor.maximize:
                    contribution = -contribution
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

    md = "# Decision Analysis Report\n\n"
    md += f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
    md += f"**Execution Tier:** {data.mode.upper()}\n\n"

    md += "## Visual Insights\n\n"
    md += f"![Risk Profiles](risk_profiles_{data.timestamp}.png)\n\n"
    md += f"![Factor Importance](factor_importance_{data.timestamp}.png)\n\n"
    md += f"![Robustness Audit](robustness_audit_{data.timestamp}.png)\n\n"

    md += "## 1. Executive Summary\n\n"
    mc_winner = max(data.mc_results.values(), key=lambda x: x.mean_score).option_name
    md += f"> **Recommended Strategy:** **{bluf_winner}** is the most balanced option ({bluf_reason}), ideal for minimizing risk across all fronts. However, **{mc_winner}** offers the highest direct expected value (Monte Carlo).\n\n"
    md += f"**Situation Analysis:** {bluf_reason}. "
    robustness_val = data.sensitivity.get('robustness_score', 0) * 100
    if robustness_val < 30:
        md += "Warning: **Low Robustness:** The current decision is volatile. A minor change in priorities could tip the balance toward another option."
    md += "\n\n"

    md += "### 1.1 Algorithm Consensus\n"
    has_prom = _has_promethee(data.mode, data.future)
    if has_prom:
        headers = ["Option", "MC Rank", "F-TOPSIS Rank", "PROMETHEE Rank"]
    else:
        headers = ["Option", "MC Rank", "F-TOPSIS Rank"]
    rows = []
    for name, comp_data in data.algo_comp.items():
        row = [f"**{name}**", f"#{comp_data.get('mc_rank')}", f"#{comp_data.get('topsis_rank', '-')}"]
        if has_prom:
            row.append(f"#{comp_data.get('promethee_rank', '-')}")
        rows.append(row)
    md += _md_table(headers, rows)

    md += "\n### 1.2 Visual Summary (Expected Value)\n"
    md += "```text\n"
    md += _bar_chart(data.mc_results) + "\n"
    md += "```\n"

    md += "\n### 1.3 Strategic Option Set (Pareto Efficiency)\n"
    md += f"- **Pareto Efficient Options:** {', '.join(data.pareto.get('efficient_frontier', []))}\n"
    if data.pareto.get("dominated_options"):
        md += "- **Dominated Options:**\n"
        for loser, winner in data.pareto["dominated_options"]:
            md += f"  - {loser} (Dominated by {winner})\n"

    if data.mode in ("standard", "advanced") and data.sensitivity:
        md += "\n### 1.4 Stability Diagnosis\n"
        md += f"- **Priority Consistency:** {data.sensitivity.get('robustness_score', 0) * 100:.0f}%\n"
        md += "  *(How stable the winner is if your weights vary by 20%)*\n"
        weight_changes = data.sensitivity.get("weight_changes", [])
        score_changes = data.sensitivity.get("score_changes", [])
        if weight_changes:
            md += "- **Warning:** The decision is sensitive to weight changes:\n"
            for change in weight_changes:
                md += f"  - If **{change['factor']}** weight changes by {change['change']} -> Winner flips to **{change['new_winner']}**\n"
        if score_changes:
            md += "- **Warning:** The decision is sensitive to score changes:\n"
            for change in score_changes:
                md += f"  - If **{change['factor']}** score changes by {change['change']} -> Winner flips to **{change['new_winner']}**\n"
        if not weight_changes and not score_changes:
            md += "- **Verdict:** Stable Decision.\n"

        if data.future.get("robust_optimizer"):
            robust_data = data.future["robust_optimizer"]
            md += "\n### 1.5 Distributionally Robust Optimization (DRO)\n"
            dro_rows = []
            for opt, score in robust_data.get("dro_scores", {}).items():
                stability = robust_data.get("stability_metrics", {}).get(opt, 0)
                dro_rows.append([opt, f"{score:.2f}", f"{stability*100:.1f}%"])
            md += _md_table(["Option", "DRO Score (Worst-Case)", "Stability Index"], dro_rows)

        if data.future.get("info_theory"):
            md += "\n### 1.6 Information Theory (Non-linear Importance)\n"
            for opt_name, mi_data in data.future["info_theory"].items():
                md += f"- **{opt_name}:**\n"
                sorted_mi = sorted(mi_data.items(), key=lambda x: x[1], reverse=True)
                for fn, val in sorted_mi:
                    md += f"  - {fn}: {val*100:.1f}%\n"

    if data.mode == "advanced" and data.future:
        md += "\n### 1.7 Advanced Predictive Insights\n"
        bayesian_probs = data.future.get("bayesian_probs", {})
        bayesian_leader = max(bayesian_probs, key=bayesian_probs.get, default=None)
        if bayesian_leader:
            md += f"- **Bayesian Highest Probability:** {bayesian_leader} ({data.future['bayesian_probs'][bayesian_leader] * 100:.1f}% confidence)\n"
        ideal = data.future.get("ideal_option")
        if ideal:
            md += f"- **Theoretical Gap:** The ultimate composite option is {ideal['improvement_potential']:.1f}% better than the current winner. Consider combining traits from {list(ideal['source_options'].values())}.\n"

    md += "\n## 2. Detailed Analysis\n\n"
    md += "### 2.1 Decision Matrix\n"
    dm_headers = ["Option"] + [f"{f.name} (w={f.weight})" for f in data.factors] + ["**Total Score**"]
    dm_alignments = [":---"] + ["---:"] * len(data.factors) + ["---:"]
    dm_rows = []
    for name, dm_data in data.decision_matrix.items():
        row = [f"**{name}**"]
        for factor in data.factors:
            if factor.name in dm_data:
                item = dm_data[factor.name]
                row.append(f"{item['raw']:.2f} ({item['contribution']:+.2f})")
            else:
                row.append("N/A")
        row.append(f"**{dm_data['total_score']:.2f}**")
        dm_rows.append(row)
    md += _md_table(dm_headers, dm_rows, dm_alignments)

    if data.explanation:
        md += "\n## 2. Decision Explanation\n\n"
        md += data.explanation + "\n\n"
        if data.waterfall:
            for opt_name, opt_data in data.waterfall.get("options", {}).items():
                md += f"### Factor Breakdown: {opt_name}\n"
                md += "| Factor | Weight | Raw | Normalized | Direction | Contribution | % of Total |\n"
                md += "| :--- | :---: | :---: | :---: | :---: | ---: | ---: |\n"
                for item in opt_data["factors"]:
                    md += f"| {item['name']} | {item['weight']:.2f} | {item['raw']:.2f} | {item['normalized']:.2f} | {item['direction']} | {item['contribution']:.3f} | {item['pct_of_total']:.1f}% |\n"
                md += "\n"
        if data.counterfactual and data.counterfactual.get("flip_scenarios"):
            for loser, scenarios in data.counterfactual["flip_scenarios"].items():
                if scenarios:
                    md += f"### How {loser} Could Win\n"
                    for s in scenarios[:3]:
                        md += f"- Adjust **{s['factor']}** weight from {s['current_value']:.2f} to {s['needed_value']:.2f} ({s['change_pct']})\n"
                    md += "\n"

    if data.mode in ("standard", "advanced") and data.strategies:
        md += "\n## 3. Classical Decision Theory\n"
        for strat, val in data.strategies.items():
            md += f"- **{strat}:** {val}\n"

    if data.mode == "advanced" and data.future:
        md += "\n### 3.1 Extended Analysis\n"
        if "promethee_scores" in data.future and not data.future["promethee_scores"].empty:
            md += "#### PROMETHEE II\n"
            for idx, val in data.future["promethee_scores"].items():
                md += f"- **{idx}**: {val:.4f}\n"
        md += "\n#### Bayesian Posterior\n"
        for k, v in data.future.get("bayesian_probs", {}).items():
            md += f"- **{k}**: {v * 100:.1f}%\n"

    if data.mode in ("standard", "advanced"):
        md += "\n## 4. Appendix: Statistical Deep Dive\n"
        for name, stats in data.mc_results.items():
            md += f"\n### {name}\n"
            md += f"- **Mean Score:** {stats.mean_score:.2f} (SD: {stats.std_dev:.2f})\n"
            md += f"- **95% VaR:** {stats.var_95:.2f}\n"
            md += f"- **Success Rate:** {stats.success_rate * 100:.1f}%\n"
            for factor in data.factors:
                if factor.name in stats.factor_stats:
                    f_stats = stats.factor_stats[factor.name]
                    direction = "Maximize" if factor.maximize else "Minimize"
                    contribution = f_stats["mean"] * factor.weight
                    if not factor.maximize:
                        contribution = -contribution
                    md += f"- **{factor.name}** ({direction}, w={factor.weight}): Mean={f_stats['mean']:.2f}, Impact={contribution:+.2f}\n"

    if data.ai_reports:
        md += "\n## AI Insights\n"
        for name, report in data.ai_reports.items():
            md += f"\n### {name}\n> {report}\n"

    md_path = os.path.join(data.results_dir, f"report_{data.timestamp}.md")
    with open(md_path, "w") as f:
        f.write(md)
    logger.debug(f"Markdown report saved to {md_path}")
    return md_path


def save_html_report(data: ReportData) -> str:
    try:
        from jinja2 import Environment, FileSystemLoader

        template_dir = os.path.join(os.path.dirname(__file__), "templates")
        env = Environment(loader=FileSystemLoader(template_dir))
        template = env.get_template("report.html.j2")
    except (ImportError, Exception):
        logger.warning("Jinja2 not available, falling back to inline HTML generation")
        return _generate_html_inline(data)

    bluf_winner, bluf_reason = resolve_winner(data.topsis_scores, data.mc_results)

    best_mc = max(data.mc_results.items(), key=lambda x: x[1].mean_score)[0]
    robust_raw = data.sensitivity.get('robustness_score', 0) * 100 if data.sensitivity else 0
    robustness = f"{robust_raw:.0f}%"
    pareto_count = len(data.pareto.get("efficient_frontier", [])) if data.pareto else 0
    max_score = max(s.mean_score for s in data.mc_results.values()) if data.mc_results else 1

    mc_data = []
    for name, stats in data.mc_results.items():
        pct = (stats.mean_score / max_score) * 100 if max_score > 0 else 0
        mc_data.append({"name": name, "mean": stats.mean_score, "pct": pct})

    kpi_cards = [
        {"title": "Balanced Recommendation", "value": bluf_winner, "sub": "Winner by total balance (F-TOPSIS)", "class": "success"},
        {"title": "Maximum Expected Value", "value": best_mc, "sub": "Best mathematical average (Monte Carlo)", "class": ""},
        {"title": "Criterion Consistency", "value": robustness, "sub": "Stability under weight changes", "class": "accent" if robust_raw > 50 else "warning"},
        {"title": "Efficiency Frontier", "value": f"{pareto_count} Options", "sub": "Technically optimal options", "class": ""},
    ]

    criteria = []
    first_opt = next(iter(data.decision_matrix.values())) if data.decision_matrix else {}
    for k, v in first_opt.items():
        if k != "total_score":
            criteria.append({"name": k, "weight": v["weight"], "direction": "Maximize" if v["maximize"] else "Minimize", "maximize": v["maximize"]})

    risk_profiles = []
    for name, stats in data.mc_results.items():
        risk_profiles.append({
            "name": name,
            "mean": stats.mean_score,
            "std": stats.std_dev,
            "var_95": stats.var_95,
            "cvar_95": stats.cvar_95,
        })

    has_prom = data.mode == "advanced" and data.future and "promethee_scores" in data.future

    advanced_insights = {}
    if data.mode == "advanced" and data.future:
        ideal = data.future.get("ideal_option")
        if ideal:
            advanced_insights["improvement_potential"] = ideal["improvement_potential"]
        bayesian_leader = max(data.future.get("bayesian_probs", {}), key=data.future.get("bayesian_probs", {}).get, default=None)
        if bayesian_leader:
            advanced_insights["bayesian_leader"] = bayesian_leader
            advanced_insights["bayesian_prob"] = data.future["bayesian_probs"][bayesian_leader]

    html = template.render(
        timestamp=data.timestamp,
        mode=data.mode,
        date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        kpi_cards=kpi_cards,
        criteria=criteria,
        mc_data=mc_data,
        algo_comp=data.algo_comp,
        has_prom=has_prom,
        advanced_insights=advanced_insights,
        risk_profiles=risk_profiles,
        explanation=data.explanation,
    )

    html_path = os.path.join(data.results_dir, f"report_{data.timestamp}.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)
    logger.debug(f"HTML report saved to {html_path}")
    return html_path


def _generate_html_inline(data: ReportData) -> str:
    from python.core.html_fallback import generate_html_inline
    return generate_html_inline(
        data.results_dir, data.timestamp, data.mode, data.mc_results, data.topsis_scores,
        data.strategies, data.pareto, data.sensitivity, data.future, data.ai_reports,
        data.algo_comp, data.decision_matrix, data.factors,
        explanation=data.explanation,
    )


def print_report(data: ReportData):
    if data.explanation:
        print("\n" + "-" * 70)
        print("DECISION EXPLANATION")
        print("-" * 70)
        print(data.explanation)

    bluf_winner, bluf_reason = resolve_winner(data.topsis_scores, data.mc_results)

    print("\n" + "=" * 70)
    print(f"DECISION ANALYSIS REPORT ({data.mode.upper()} TIER)")
    print("=" * 70 + "\n")

    print("--- 1. EXECUTIVE SUMMARY ---\n")
    print(f"RECOMMENDATION: {bluf_winner} is the optimal choice based on {bluf_reason}.\n")

    ctx = _mc_context(data.mc_results)
    print(f"Best Monte Carlo: {ctx['best_name']} (Mean: {ctx['best_score']:.2f})")
    print(_bar_chart(data.mc_results))

    if not data.topsis_scores.empty:
        print(f"Best F-TOPSIS: {data.topsis_scores.index[0]} (Score: {data.topsis_scores.iloc[0]:.4f})")

    if _has_promethee(data.mode, data.future):
        print(f"Best PROMETHEE: {data.future['promethee_scores'].index[0]} (Net Flow: {data.future['promethee_scores'].iloc[0]:.4f})")

    print(f"\nPareto Efficient: {', '.join(data.pareto.get('efficient_frontier', []))}")
    if data.pareto.get("dominated_options"):
        print(f"Dominated options: {len(data.pareto['dominated_options'])}")

    if data.mode in ("standard", "advanced") and data.sensitivity:
        print(f"\nRobustness: {data.sensitivity.get('robustness_score', 0) * 100:.0f}%")
        wc = len(data.sensitivity.get("weight_changes", []))
        sc = len(data.sensitivity.get("score_changes", []))
        if wc > 0:
            print(f"Warning: {wc} weight-shock scenarios flip the winner.")
        if sc > 0:
            print(f"Warning: {sc} score-shock scenarios flip the winner.")

        if data.future.get("robust_optimizer"):
            robust_data = data.future["robust_optimizer"]
            print("\nDistributionally Robust Analysis (DRO):")
            for opt, score in robust_data.get("dro_scores", {}).items():
                stability = robust_data.get("stability_metrics", {}).get(opt, 0)
                print(f"  - {opt:20}: Score={score:8.2f} | Stability={stability*100:5.1f}%")

        if data.future.get("info_theory"):
            print("\nNon-linear Factor Importance (Information Theory):")
            for opt_name, mi_data in data.future["info_theory"].items():
                print(f"  - {opt_name}:")
                sorted_mi = sorted(mi_data.items(), key=lambda x: x[1], reverse=True)
                for fn, val in sorted_mi:
                    print(f"    * {fn}: {val*100:.1f}%")

    if data.mode == "advanced" and data.future:
        ideal = data.future.get("ideal_option")
        if ideal:
            print(f"Theoretical Gap: {ideal['improvement_potential']:.1f}%")
        bayesian_probs = data.future.get("bayesian_probs", {})
        bayesian_leader = max(bayesian_probs, key=bayesian_probs.get, default=None)
        if bayesian_leader:
            print(f"Bayesian Pick: {bayesian_leader} ({data.future['bayesian_probs'][bayesian_leader] * 100:.1f}%)")

    if data.mode in ("standard", "advanced") and data.strategies:
        print("\nDecision Theory Lenses:")
        for strat, val in data.strategies.items():
            print(f"  - {strat}: {val}")

    for name, stats in data.mc_results.items():
        print(f"\n{name}: Mean={stats.mean_score:.2f} (SD={stats.std_dev:.2f}), VaR={stats.var_95:.2f}")


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

    json_path = save_json_report(data.results_dir, data.timestamp, data.mc_results,
                                 data.topsis_scores, data.decision_matrix, data.algo_comp, data.ai_reports)
    md_path = save_markdown_report(data)
    html_path = save_html_report(data)

    return {"json": json_path, "md": md_path, "html": html_path, "timestamp": data.timestamp}
