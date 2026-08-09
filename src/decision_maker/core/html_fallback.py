"""
Renders self-contained HTML reports fallback visualizer when external dependencies are missing.
Usage: from decision_maker.core.html_fallback import generate_html_inline
Does NOT: Perform decision matrix computations or stochastic sampling.
"""

from __future__ import annotations

__all__ = ["generate_html_inline"]

import os
from datetime import datetime
from typing import Any

from decision_maker.core.content import REPORT_CSS
from decision_maker.core.models import Statistics
from decision_maker.core.reporting import ReportData
from decision_maker.core.utils import resolve_winner


def generate_html_inline(data: ReportData) -> str:
    bluf_winner, bluf_reason = resolve_winner(data.topsis_scores, data.mc_results)

    best_mc = max(data.mc_results.items(), key=lambda x: x[1].mean_score)[0]
    robustness = f"{data.sensitivity.get('robustness_score', 0) * 100:.0f}%" if data.sensitivity else "N/A"
    pareto_count = len(data.pareto.get("efficient_frontier", [])) if data.pareto else 0
    max_score = max(s.mean_score for s in data.mc_results.values()) if data.mc_results else 1

    html_head = (
        "<!DOCTYPE html>\n<html lang=\"en\">\n"
        "<head><meta charset=\"UTF-8\"><meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">\n"
        "<title>Decision Analysis Report</title>\n<style>\n"
        + REPORT_CSS
        + "\n</style></head>\n<body><div class=\"dashboard\">\n"
    )

    html = html_head + f"""<header class="header"><h1>Decision Intelligence Report</h1><div><span style="color:#8b949e;margin-right:1rem">{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</span><span class="badge">{data.mode.upper()} TIER</span></div></header>
<div class="kpi-card"><div class="kpi-title">Optimal Recommendation</div><div class="kpi-value success">{bluf_winner}</div><div class="kpi-sub">{bluf_reason}</div></div>
<div class="kpi-card"><div class="kpi-title">Max Expected Value</div><div class="kpi-value">{best_mc}</div><div class="kpi-sub">Highest MC mean</div></div>
<div class="kpi-card"><div class="kpi-title">Robustness</div><div class="kpi-value accent">{robustness}</div><div class="kpi-sub">Weight shock stability</div></div>
<div class="kpi-card"><div class="kpi-title">Pareto Efficient</div><div class="kpi-value">{pareto_count} Options</div><div class="kpi-sub">Non-dominated frontier</div></div>"""

    first_opt = next(iter(data.decision_matrix.values())) if data.decision_matrix else {}
    if first_opt:
        html += '<div class="panel col-12"><h2 class="panel-title">Criteria & Assumptions</h2><div style="display:flex;gap:1rem;flex-wrap:wrap">'
        for k, v in first_opt.items():
            if k != "total_score":
                color = "#3fb950" if v["maximize"] else "#f85149"
                html += f'<div style="flex:1;background:#0d1117;padding:1rem;border-radius:6px;border:1px solid #30363d;min-width:250px"><div style="font-weight:600;color:#58a6ff">{k}</div><div style="font-size:.85rem;color:#8b949e">Weight: <strong style="color:#e6edf3">{v["weight"] * 100:.0f}%</strong></div><div style="font-size:.85rem;color:{color};margin-top:.25rem">{"Maximize" if v["maximize"] else "Minimize"}</div></div>'
        html += "</div></div>"

    html += '<div class="panel col-8"><h2 class="panel-title">Expected Value Distribution</h2><table><tbody>'
    for name, stats in data.mc_results.items():
        pct = (stats.mean_score / max_score) * 100 if max_score > 0 else 0
        html += f'<tr><td style="font-weight:600">{name}</td><td><div class="bar-track"><div class="bar-fill" style="width:{pct}%"></div><span class="bar-label">{stats.mean_score:,.0f}</span></div></td></tr>'
    html += "</tbody></table></div>"

    html += '<div class="panel col-4"><h2 class="panel-title">Algorithm Rankings</h2><table><thead><tr><th>Option</th><th>MC</th><th>F-TOP</th>'
    has_prom = data.mode == "advanced" and data.future and "promethee_scores" in data.future
    if has_prom:
        html += "<th>PROM</th>"
    html += "</tr></thead><tbody>"
    for name, algo in data.algo_comp.items():
        mc_r = f"#{algo.get('mc_rank', '-')}"
        top_r = f"#{algo.get('topsis_rank', '-')}"
        mc_r = f'<span style="color:#3fb950;font-weight:bold">{mc_r}</span>' if algo.get("mc_rank") == 1 else mc_r
        top_r = (
            f'<span style="color:#3fb950;font-weight:bold">{top_r}</span>' if algo.get("topsis_rank") == 1 else top_r
        )
        html += f"<tr><td>{name}</td><td>{mc_r}</td><td>{top_r}</td>"
        if has_prom:
            prom_r = f"#{algo.get('promethee_rank', '-')}"
            prom_r = (
                f'<span style="color:#3fb950;font-weight:bold">{prom_r}</span>'
                if algo.get("promethee_rank") == 1
                else prom_r
            )
            html += f"<td>{prom_r}</td>"
        html += "</tr>"
    html += "</tbody></table></div>"

    if data.mode == "advanced" and data.future:
        html += '<div class="panel col-12"><h2 class="panel-title">Advanced Insights</h2><div style="display:flex;gap:2rem">'
        ideal = data.future.get("ideal_option")
        if ideal:
            html += f'<div style="flex:1"><div class="kpi-title">Theoretical Gap</div><div style="font-size:.9rem;margin-top:.5rem">Composite option is <strong style="color:#a371f7">{ideal["improvement_potential"]:.1f}%</strong> better than current winner.</div></div>'
        bayesian_probs = data.future.get("bayesian_probs", {})
        bayesian_leader = max(bayesian_probs, key=bayesian_probs.get, default=None)
        if bayesian_leader:
            html += f'<div style="flex:1;border-left:1px solid #30363d;padding-left:2rem"><div class="kpi-title">Bayesian Confidence</div><div style="font-size:.9rem;margin-top:.5rem"><strong>{bayesian_leader}</strong> probability: <strong style="color:#58a6ff">{data.future["bayesian_probs"][bayesian_leader] * 100:.1f}%</strong></div></div>'
        html += "</div></div>"

    html += (
        '<div class="panel col-12"><h2 class="panel-title">Risk Profiles (95% Confidence)</h2><div class="stats-grid">'
    )
    for name, stats in data.mc_results.items():
        html += f'<div class="stat-box"><div style="font-weight:600;margin-bottom:1rem;border-bottom:1px solid #30363d;padding-bottom:.5rem">{name}</div>'
        html += f'<div class="stat-row"><span class="stat-label">Expected</span><span class="stat-val">{stats.mean_score:,.2f}</span></div>'
        html += f'<div class="stat-row"><span class="stat-label">Volatility</span><span class="stat-val">±{stats.std_dev:,.2f}</span></div>'
        html += f'<div class="stat-row"><span class="stat-label">VaR</span><span class="stat-val" style="color:#f85149">{stats.var_95:,.2f}</span></div>'
        html += f'<div class="stat-row"><span class="stat-label">CVaR</span><span class="stat-val" style="color:#f85149">{stats.cvar_95:,.2f}</span></div>'
        html += "</div>"
    html += "</div></div>"

    if data.explanation:
        html += f'<div class="panel col-12"><h2 class="panel-title">Decision Explanation</h2><div style="padding:1rem;line-height:1.7">{data.explanation.replace(chr(10), "<br>")}</div></div>'

    html += "</div></div></div></body></html>"

    html_path = os.path.join(data.results_dir, f"report_{data.timestamp}.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)
    return html_path
