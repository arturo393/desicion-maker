from __future__ import annotations

import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

import pandas as pd

from python.core.models import Factor, Statistics

logger = logging.getLogger(__name__)


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
    algo_comp = {}
    sorted_mc = sorted(mc_results.items(), key=lambda x: x[1].mean_score, reverse=True)
    for rank, (name, stats) in enumerate(sorted_mc, 1):
        if name not in algo_comp:
            algo_comp[name] = {}
        algo_comp[name]["mc_rank"] = rank
        algo_comp[name]["mc_score"] = stats.mean_score

    if not topsis_scores.empty:
        sorted_topsis = topsis_scores.sort_values(ascending=False)
        for rank, (name, score) in enumerate(sorted_topsis.items(), 1):
            if name not in algo_comp:
                algo_comp[name] = {}
            algo_comp[name]["topsis_rank"] = rank
            algo_comp[name]["topsis_score"] = score

    if future and "promethee_scores" in future and not future["promethee_scores"].empty:
        sorted_prom = future["promethee_scores"].sort_values(ascending=False)
        for rank, (name, score) in enumerate(sorted_prom.items(), 1):
            if name not in algo_comp:
                algo_comp[name] = {}
            algo_comp[name]["promethee_rank"] = rank
            algo_comp[name]["promethee_score"] = score

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


def save_markdown_report(
    results_dir: str,
    timestamp: str,
    mode: str,
    mc_results: Dict[str, Statistics],
    topsis_scores: pd.Series,
    strategies: Dict[str, str],
    pareto: Dict[str, Any],
    sensitivity: Dict[str, Any],
    future: Dict[str, Any],
    ai_reports: Dict[str, str],
    algo_comp: Dict[str, Any],
    decision_matrix: Dict[str, Any],
    factors: List[Factor],
    explanation: str = "",
    waterfall: Optional[Dict] = None,
    counterfactual: Optional[Dict] = None,
) -> str:
    if not topsis_scores.empty:
        bluf_winner = topsis_scores.index[0]
        bluf_reason = "F-TOPSIS risk-adjusted distance to ideal"
    else:
        bluf_winner = max(mc_results.items(), key=lambda x: x[1].mean_score)[0]
        bluf_reason = "Monte Carlo expected value"

    md = f"# Decision Analysis Report\n\n"
    md += f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
    md += f"**Execution Tier:** {mode.upper()}\n\n"
    
    # Embed plots if they exist in the results_dir with the current timestamp
    md += "## Visual Insights\n\n"
    md += f"![Risk Profiles](risk_profiles_{timestamp}.png)\n\n"
    md += f"![Factor Importance](factor_importance_{timestamp}.png)\n\n"
    md += f"![Robustness Audit](robustness_audit_{timestamp}.png)\n\n"

    md += "## 1. Resumen Ejecutivo\n\n"
    mc_winner = max(mc_results.values(), key=lambda x: x.mean_score).option_name
    md += f"> **Estrategia Recomendada:** Existe un empate técnico de alto nivel. **{bluf_winner}** es la opción más equilibrada (F-TOPSIS), ideal para minimizar riesgos en todos los frentes. Sin embargo, **{mc_winner}** ofrece el mayor beneficio económico directo (Monte Carlo).\n\n"
    md += f"**Análisis de Situación:** {bluf_reason}. "
    robustness_val = sensitivity.get('robustness_score', 0) * 100
    if robustness_val < 30:
        md += "⚠️ **Alerta de Sensibilidad:** La decisión actual es volátil. Un cambio menor en tus prioridades podría inclinar la balanza hacia otro banco."
    md += "\n\n"

    md += "### 1.1 Algorithm Consensus\n"
    has_prom = mode == "advanced" and future and "promethee_scores" in future and not future["promethee_scores"].empty
    if has_prom:
        md += "| Option | MC Rank | F-TOPSIS Rank | PROMETHEE Rank |\n"
        md += "| :--- | :--- | :--- | :--- |\n"
    else:
        md += "| Option | MC Rank | F-TOPSIS Rank |\n"
        md += "| :--- | :--- | :--- |\n"

    for name, data in algo_comp.items():
        mc_r = f"#{data.get('mc_rank')}"
        top_r = f"#{data.get('topsis_rank', '-')}"
        if has_prom:
            prom_r = f"#{data.get('promethee_rank', '-')}"
            md += f"| **{name}** | {mc_r} | {top_r} | {prom_r} |\n"
        else:
            md += f"| **{name}** | {mc_r} | {top_r} |\n"

    md += "\n### 1.2 Visual Summary (Expected Value)\n"
    md += "```text\n"
    max_score = max(s.mean_score for s in mc_results.values())
    max_label_len = max(len(n) for n in mc_results.keys())
    for name, stats in mc_results.items():
        bar_len = int((stats.mean_score / max_score) * 40) if max_score > 0 else 0
        bar = "█" * bar_len
        md += f"{name:<{max_label_len}} | {bar} {stats.mean_score:.0f}\n"
    md += "```\n"

    md += "\n### 1.3 Strategic Option Set (Pareto Efficiency)\n"
    md += f"- **Pareto Efficient Options:** {', '.join(pareto.get('efficient_frontier', []))}\n"
    if pareto.get("dominated_options"):
        md += "- **Dominated Options:**\n"
        for loser, winner in pareto["dominated_options"]:
            md += f"  - {loser} (Dominated by {winner})\n"

    if mode in ("standard", "advanced") and sensitivity:
        md += "\n### 1.4 Diagnóstico de Estabilidad\n"
        md += f"- **Consistencia de Prioridades:** {sensitivity.get('robustness_score', 0) * 100:.0f}%\n"
        md += "  *(Indica qué tan estable es el ganador si tus pesos variaran un 20%)*\n"
        weight_changes = sensitivity.get("weight_changes", [])
        score_changes = sensitivity.get("score_changes", [])
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
        
        if future.get("robust_optimizer"):
            robust_data = future["robust_optimizer"]
            md += "\n### 1.5 Distributionally Robust Optimization (DRO)\n"
            md += "| Option | DRO Score (Worst-Case) | Stability Index |\n"
            md += "| :--- | :---: | :---: |\n"
            for opt, score in robust_data.get("dro_scores", {}).items():
                stability = robust_data.get("stability_metrics", {}).get(opt, 0)
                md += f"| {opt} | {score:.2f} | {stability*100:.1f}% |\n"
        
        if future.get("info_theory"):
            md += "\n### 1.5 Information Theory (Non-linear Importance)\n"
            for opt_name, mi_data in future["info_theory"].items():
                md += f"- **{opt_name}:**\n"
                sorted_mi = sorted(mi_data.items(), key=lambda x: x[1], reverse=True)
                for fn, val in sorted_mi:
                    md += f"  - {fn}: {val*100:.1f}%\n"

    if mode == "advanced" and future:
        md += "\n### 1.5 Advanced Predictive Insights\n"
        bayesian_leader = max(future.get("bayesian_probs", {}), key=future.get("bayesian_probs", {}).get, default=None)
        if bayesian_leader:
            md += f"- **Bayesian Highest Probability:** {bayesian_leader} ({future['bayesian_probs'][bayesian_leader] * 100:.1f}% confidence)\n"
        ideal = future.get("ideal_option")
        if ideal:
            md += f"- **Theoretical Gap:** The ultimate composite option is {ideal['improvement_potential']:.1f}% better than the current winner. Consider combining traits from {list(ideal['source_options'].values())}.\n"

    md += "\n## 2. Detailed Analysis\n\n"
    md += "### 2.1 Decision Matrix\n"
    md += "| Option | " + " | ".join([f"{f.name} (w={f.weight})" for f in factors]) + " | **Total Score** |\n"
    md += "| :--- | " + " | ".join(["---:"] * len(factors)) + " | ---: |\n"

    for name, data in decision_matrix.items():
        row = f"| **{name}** | "
        for factor in factors:
            if factor.name in data:
                item = data[factor.name]
                row += f"{item['raw']:.2f} ({item['contribution']:+.2f}) | "
            else:
                row += "N/A | "
        row += f"**{data['total_score']:.2f}** |\n"
        md += row

    if explanation:
        md += "\n## 2. Decision Explanation\n\n"
        md += explanation + "\n\n"
        if waterfall:
            for opt_name, opt_data in waterfall.get("options", {}).items():
                md += f"### Factor Breakdown: {opt_name}\n"
                md += "| Factor | Weight | Raw | Normalized | Direction | Contribution | % of Total |\n"
                md += "| :--- | :---: | :---: | :---: | :---: | ---: | ---: |\n"
                for item in opt_data["factors"]:
                    md += f"| {item['name']} | {item['weight']:.2f} | {item['raw']:.2f} | {item['normalized']:.2f} | {item['direction']} | {item['contribution']:.3f} | {item['pct_of_total']:.1f}% |\n"
                md += "\n"
        if counterfactual and counterfactual.get("flip_scenarios"):
            for loser, scenarios in counterfactual["flip_scenarios"].items():
                if scenarios:
                    md += f"### How {loser} Could Win\n"
                    for s in scenarios[:3]:
                        md += f"- Adjust **{s['factor']}** weight from {s['current_value']:.2f} to {s['needed_value']:.2f} ({s['change_pct']})\n"
                    md += "\n"

    if mode in ("standard", "advanced") and strategies:
        md += "\n## 3. Classical Decision Theory\n"
        for strat, val in strategies.items():
            md += f"- **{strat}:** {val}\n"

    if mode == "advanced" and future:
        md += "\n### 3.1 Extended Analysis\n"
        if "promethee_scores" in future and not future["promethee_scores"].empty:
            md += "#### PROMETHEE II\n"
            for idx, val in future["promethee_scores"].items():
                md += f"- **{idx}**: {val:.4f}\n"
        md += "\n#### Bayesian Posterior\n"
        for k, v in future.get("bayesian_probs", {}).items():
            md += f"- **{k}**: {v * 100:.1f}%\n"

    if mode in ("standard", "advanced"):
        md += "\n## 4. Appendix: Statistical Deep Dive\n"
        for name, stats in mc_results.items():
            md += f"\n### {name}\n"
            md += f"- **Mean Score:** {stats.mean_score:.2f} (SD: {stats.std_dev:.2f})\n"
            md += f"- **95% VaR:** {stats.var_95:.2f}\n"
            md += f"- **Success Rate:** {stats.success_rate * 100:.1f}%\n"
            for factor in factors:
                if factor.name in stats.factor_stats:
                    f_stats = stats.factor_stats[factor.name]
                    direction = "Maximize" if factor.maximize else "Minimize"
                    contribution = f_stats["mean"] * factor.weight
                    if not factor.maximize:
                        contribution = -contribution
                    md += f"- **{factor.name}** ({direction}, w={factor.weight}): Mean={f_stats['mean']:.2f}, Impact={contribution:+.2f}\n"

    if ai_reports:
        md += "\n## AI Insights\n"
        for name, report in ai_reports.items():
            md += f"\n### {name}\n> {report}\n"

    md_path = os.path.join(results_dir, f"report_{timestamp}.md")
    with open(md_path, "w") as f:
        f.write(md)
    logger.debug(f"Markdown report saved to {md_path}")
    return md_path


def save_html_report(
    results_dir: str,
    timestamp: str,
    mode: str,
    mc_results: Dict[str, Statistics],
    topsis_scores: pd.Series,
    strategies: Dict[str, str],
    pareto: Dict[str, Any],
    sensitivity: Dict[str, Any],
    future: Dict[str, Any],
    ai_reports: Dict[str, str],
    algo_comp: Dict[str, Any],
    decision_matrix: Dict[str, Any],
    factors: List[Factor],
    explanation: str = "",
    waterfall: Optional[Dict] = None,
    counterfactual: Optional[Dict] = None,
) -> str:
    try:
        from jinja2 import Environment, FileSystemLoader

        template_dir = os.path.join(os.path.dirname(__file__), "templates")
        env = Environment(loader=FileSystemLoader(template_dir))
        template = env.get_template("report.html.j2")
    except (ImportError, Exception):
        logger.warning("Jinja2 not available, falling back to inline HTML generation")
        return _generate_html_inline(
            results_dir, timestamp, mode, mc_results, topsis_scores,
            strategies, pareto, sensitivity, future, ai_reports,
            algo_comp, decision_matrix, factors,
        )

    if not topsis_scores.empty:
        bluf_winner = topsis_scores.index[0]
        bluf_reason = "F-TOPSIS risk-adjusted distance"
    else:
        bluf_winner = max(mc_results.items(), key=lambda x: x[1].mean_score)[0]
        bluf_reason = "MC Expected Value"

    best_mc = max(mc_results.items(), key=lambda x: x[1].mean_score)[0]
    robust_raw = sensitivity.get('robustness_score', 0) * 100 if sensitivity else 0
    robustness = f"{robust_raw:.0f}%"
    pareto_count = len(pareto.get("efficient_frontier", [])) if pareto else 0
    max_score = max(s.mean_score for s in mc_results.values()) if mc_results else 1

    mc_data = []
    for name, stats in mc_results.items():
        pct = (stats.mean_score / max_score) * 100 if max_score > 0 else 0
        mc_data.append({"name": name, "mean": stats.mean_score, "pct": pct})

    kpi_cards = [
        {"title": "Recomendación Balanceada", "value": bluf_winner, "sub": "Ganador por equilibrio total (F-TOPSIS)", "class": "success"},
        {"title": "Máximo Valor Esperado", "value": best_mc, "sub": "Mejor promedio matemático (Monte Carlo)", "class": ""},
        {"title": "Consistencia de Criterio", "value": robustness, "sub": "Estabilidad ante cambios de pesos", "class": "accent" if robust_raw > 50 else "warning"},
        {"title": "Frontera de Eficiencia", "value": f"{pareto_count} Opciones", "sub": "Opciones técnicamente óptimas", "class": ""},
    ]

    criteria = []
    first_opt = next(iter(decision_matrix.values())) if decision_matrix else {}
    for k, v in first_opt.items():
        if k != "total_score":
            criteria.append({"name": k, "weight": v["weight"], "direction": "Maximize" if v["maximize"] else "Minimize", "maximize": v["maximize"]})

    risk_profiles = []
    for name, stats in mc_results.items():
        risk_profiles.append({
            "name": name,
            "mean": stats.mean_score,
            "std": stats.std_dev,
            "var_95": stats.var_95,
            "cvar_95": stats.cvar_95,
        })

    has_prom = mode == "advanced" and future and "promethee_scores" in future

    advanced_insights = {}
    if mode == "advanced" and future:
        ideal = future.get("ideal_option")
        if ideal:
            advanced_insights["improvement_potential"] = ideal["improvement_potential"]
        bayesian_leader = max(future.get("bayesian_probs", {}), key=future.get("bayesian_probs", {}).get, default=None)
        if bayesian_leader:
            advanced_insights["bayesian_leader"] = bayesian_leader
            advanced_insights["bayesian_prob"] = future["bayesian_probs"][bayesian_leader]

    html = template.render(
        timestamp=timestamp,
        mode=mode,
        date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        kpi_cards=kpi_cards,
        criteria=criteria,
        mc_data=mc_data,
        algo_comp=algo_comp,
        has_prom=has_prom,
        advanced_insights=advanced_insights,
        risk_profiles=risk_profiles,
        explanation=explanation,
    )

    html_path = os.path.join(results_dir, f"report_{timestamp}.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)
    logger.debug(f"HTML report saved to {html_path}")
    return html_path


def _generate_html_inline(*args, **kwargs) -> str:
    from python.core.html_fallback import generate_html_inline
    kwargs.setdefault("explanation", "")
    return generate_html_inline(*args, **kwargs)


def print_report(
    mode: str,
    mc_results: Dict[str, Statistics],
    topsis_scores: pd.Series,
    strategies: Dict[str, str],
    pareto: Dict[str, Any],
    sensitivity: Dict[str, Any],
    future: Dict[str, Any],
    ai_reports: Dict[str, str],
    factors: List[Factor],
    explanation: str = "",
):
    if explanation:
        print("\n" + "-" * 70)
        print("DECISION EXPLANATION")
        print("-" * 70)
        print(explanation)

    if not topsis_scores.empty:
        bluf_winner = topsis_scores.index[0]
        bluf_reason = "F-TOPSIS risk-adjusted distance"
    else:
        bluf_winner = max(mc_results.items(), key=lambda x: x[1].mean_score)[0]
        bluf_reason = "Monte Carlo expected value"

    print("\n" + "=" * 70)
    print(f"DECISION ANALYSIS REPORT ({mode.upper()} TIER)")
    print("=" * 70 + "\n")

    print("--- 1. EXECUTIVE SUMMARY ---\n")
    print(f"RECOMMENDATION: {bluf_winner} is the optimal choice based on {bluf_reason}.\n")

    best_mc = max(mc_results.items(), key=lambda x: x[1].mean_score)
    print(f"Best Monte Carlo: {best_mc[0]} (Mean: {best_mc[1].mean_score:.2f})")

    max_score = max(s.mean_score for s in mc_results.values())
    max_label_len = max(len(name) for name in mc_results.keys())
    for name, stats in mc_results.items():
        bar_len = int((stats.mean_score / max_score) * 40) if max_score > 0 else 0
        bar = "█" * bar_len
        print(f"{name:<{max_label_len}} | {bar} {stats.mean_score:.0f}")

    if not topsis_scores.empty:
        print(f"Best F-TOPSIS: {topsis_scores.index[0]} (Score: {topsis_scores.iloc[0]:.4f})")

    if mode == "advanced" and future and "promethee_scores" in future and not future["promethee_scores"].empty:
        print(f"Best PROMETHEE: {future['promethee_scores'].index[0]} (Net Flow: {future['promethee_scores'].iloc[0]:.4f})")

    print(f"\nPareto Efficient: {', '.join(pareto.get('efficient_frontier', []))}")
    if pareto.get("dominated_options"):
        print(f"Dominated options: {len(pareto['dominated_options'])}")

    if mode in ("standard", "advanced") and sensitivity:
        print(f"\nRobustness: {sensitivity.get('robustness_score', 0) * 100:.0f}%")
        wc = len(sensitivity.get("weight_changes", []))
        sc = len(sensitivity.get("score_changes", []))
        if wc > 0:
            print(f"Warning: {wc} weight-shock scenarios flip the winner.")
        if sc > 0:
            print(f"Warning: {sc} score-shock scenarios flip the winner.")
        
        if future.get("robust_optimizer"):
            robust_data = future["robust_optimizer"]
            print("\nDistributionally Robust Analysis (DRO):")
            for opt, score in robust_data.get("dro_scores", {}).items():
                stability = robust_data.get("stability_metrics", {}).get(opt, 0)
                print(f"  - {opt:20}: Score={score:8.2f} | Stability={stability*100:5.1f}%")
        
        if future.get("info_theory"):
            print("\nNon-linear Factor Importance (Information Theory):")
            for opt_name, mi_data in future["info_theory"].items():
                print(f"  - {opt_name}:")
                sorted_mi = sorted(mi_data.items(), key=lambda x: x[1], reverse=True)
                for fn, val in sorted_mi:
                    print(f"    * {fn}: {val*100:.1f}%")

    if mode == "advanced" and future:
        ideal = future.get("ideal_option")
        if ideal:
            print(f"Theoretical Gap: {ideal['improvement_potential']:.1f}%")
        bayesian_leader = max(future.get("bayesian_probs", {}), key=future.get("bayesian_probs", {}).get, default=None)
        if bayesian_leader:
            print(f"Bayesian Pick: {bayesian_leader} ({future['bayesian_probs'][bayesian_leader] * 100:.1f}%)")

    if mode in ("standard", "advanced") and strategies:
        print("\nDecision Theory Lenses:")
        for strat, val in strategies.items():
            print(f"  - {strat}: {val}")

    for name, stats in mc_results.items():
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
    if results_dir is None:
        results_dir = os.path.join(os.getcwd(), "results")
    os.makedirs(results_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    decision_matrix = prepare_decision_matrix(mc_results, factors)
    algo_comp = build_algorithm_comparison(mc_results, topsis_scores, future)

    json_path = save_json_report(results_dir, timestamp, mc_results, topsis_scores, decision_matrix, algo_comp, ai_reports)
    md_path = save_markdown_report(results_dir, timestamp, mode, mc_results, topsis_scores, strategies, pareto, sensitivity, future, ai_reports, algo_comp, decision_matrix, factors, explanation=explanation, waterfall=waterfall, counterfactual=counterfactual)
    html_path = save_html_report(results_dir, timestamp, mode, mc_results, topsis_scores, strategies, pareto, sensitivity, future, ai_reports, algo_comp, decision_matrix, factors, explanation=explanation, waterfall=waterfall, counterfactual=counterfactual)

    return {"json": json_path, "md": md_path, "html": html_path, "timestamp": timestamp}
