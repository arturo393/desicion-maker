"""
Generates natural language explanations and feature contributions for decision outcomes.
Usage: from decision_maker.core.explainability import ExplainabilityEngine
Does NOT: Render HTML or save reports directly to disk.
"""

from __future__ import annotations

__all__ = ["ExplainabilityEngine"]

import logging
from typing import Any, Dict, List

import numpy as np
import pandas as pd

from decision_maker.core.models import Factor, Statistics
from decision_maker.core.utils import compute_global_bounds

logger = logging.getLogger(__name__)


class ExplainabilityEngine:
    """
    Explains WHY a decision was made in human terms.

    Three modes:
    1. Factor Contribution Waterfall — per-option, per-factor breakdown
    2. Counterfactual Analysis — what would flip the winner
    3. Narrative Generation — plain-text summary
    """

    def factor_waterfall(
        self,
        mc_results: Dict[str, Statistics],
        factors: List[Factor],
    ) -> Dict[str, Any]:
        """
        Returns a detailed breakdown of how each factor contributed to each
        option's total score.

        Returns: {
            "options": {
                "OptionA": {
                    "total_score": 0.85,
                    "factors": [
                        {"name": "Cost", "weight": 0.4, "raw": 100, "normalized": 0.75,
                         "direction": "minimize", "contribution": 0.30, "pct_of_total": 35.3},
                        ...
                    ]
                }
            },
            "max_possible": 1.0,
        }
        """
        if not mc_results or not factors:
            return {"options": {}, "max_possible": 0.0}

        global_bounds = compute_global_bounds(mc_results, [f.name for f in factors])
        max_possible = sum(f.weight for f in factors)
        result: Dict[str, Any] = {"options": {}, "max_possible": max_possible}

        for opt_name, stats in mc_results.items():
            option_factors = []
            for f in factors:
                if f.name not in stats.factor_stats:
                    continue

                raw_mean = stats.factor_stats[f.name]["mean"]
                f_min = global_bounds[f.name]["min"]
                f_max = global_bounds[f.name]["max"]

                if f_max > f_min:
                    normalized = (raw_mean - f_min) / (f_max - f_min)
                else:
                    normalized = 1.0

                if f.maximize:
                    contribution = normalized * f.weight
                else:
                    contribution = (1.0 - normalized) * f.weight

                option_factors.append(
                    {
                        "name": f.name,
                        "weight": f.weight,
                        "raw": float(raw_mean),
                        "normalized": float(normalized),
                        "direction": "maximize" if f.maximize else "minimize",
                        "contribution": float(contribution),
                    }
                )

            total_score = stats.mean_score
            for item in option_factors:
                item["pct_of_total"] = (item["contribution"] / total_score * 100) if total_score != 0 else 0.0

            option_factors.sort(key=lambda x: x["contribution"], reverse=True)
            result["options"][opt_name] = {
                "total_score": total_score,
                "factors": option_factors,
            }

        return result

    def counterfactual(
        self,
        mc_results: Dict[str, Statistics],
        factors: List[Factor],
    ) -> Dict[str, Any]:
        """
        For each losing option, finds the minimal change needed to flip the winner.

        Returns: {
            "winner": "OptionA",
            "runner_up": "OptionB",
            "gap": 0.15,  # score difference between winner and runner-up
            "flip_scenarios": {
                "OptionB": [
                    {
                        "factor": "Cost",
                        "change_type": "weight",
                        "current_weight": 0.4,
                        "needed_weight": 0.62,
                        "change_pct": "+55%",
                        "feasible": True,
                    },
                    {
                        "factor": "ROI",
                        "change_type": "score",
                        "current_score": 1.2,
                        "needed_score": 2.8,
                        "change_pct": "+133%",
                        "feasible": False,
                    },
                ]
            }
        }
        """
        if not mc_results or len(mc_results) < 2 or not factors:
            return {"winner": None, "runner_up": None, "gap": 0, "flip_scenarios": {}}

        sorted_options = sorted(mc_results.items(), key=lambda x: x[1].mean_score, reverse=True)
        winner_name, winner_stats = sorted_options[0]
        runner_name, runner_stats = sorted_options[1]
        gap = winner_stats.mean_score - runner_stats.mean_score

        global_bounds = compute_global_bounds(mc_results, [f.name for f in factors])
        flip_scenarios: Dict[str, List[Dict]] = {}

        for opt_name, stats in mc_results.items():
            if opt_name == winner_name:
                continue

            scenarios = []
            our_score = stats.mean_score
            needed_total = winner_stats.mean_score + 1e-9  # must beat this

            score_deficit = needed_total - our_score

            for f in factors:
                if f.name not in stats.factor_stats:
                    continue

                f_stats = stats.factor_stats[f.name]
                raw_val = f_stats["mean"]
                f_min = global_bounds[f.name]["min"]
                f_max = global_bounds[f.name]["max"]

                if f_max > f_min:
                    norm_val = (raw_val - f_min) / (f_max - f_min)
                else:
                    norm_val = 1.0

                weight_adjustment = f.weight

                if weight_adjustment > 0:
                    effective = norm_val if f.maximize else (1.0 - norm_val)
                    if effective < 1e-9:
                        extra_weight_needed = float("inf")
                    else:
                        extra_weight_needed = score_deficit / effective
                    if np.isfinite(extra_weight_needed) and extra_weight_needed > 0:
                        pct_change_weight = (extra_weight_needed / weight_adjustment) * 100
                        scenarios.append(
                            {
                                "factor": f.name,
                                "change_type": "weight",
                                "current_value": weight_adjustment,
                                "needed_value": weight_adjustment + extra_weight_needed,
                                "change_pct": f"{pct_change_weight:+.0f}%",
                                "feasible": pct_change_weight < 100,
                            }
                        )

            flip_scenarios[opt_name] = sorted(scenarios, key=lambda x: abs(float(x["change_pct"].rstrip("%"))))

        return {
            "winner": winner_name,
            "runner_up": runner_name,
            "gap": gap,
            "score_deficit": winner_stats.mean_score - runner_stats.mean_score,
            "flip_scenarios": flip_scenarios,
        }

    def narrative(
        self,
        mc_results: Dict[str, Statistics],
        factors: List[Factor],
        waterfall: Dict[str, Any],
        counterfactual: Dict[str, Any],
        topsis_scores: pd.Series,
        mode: str = "standard",
        use_ai: bool = False,
    ) -> str:
        """Generates a human-readable explanation of the decision."""
        if not mc_results:
            return "No data to analyze."

        lines: List[str] = []
        sorted_opts = sorted(mc_results.items(), key=lambda x: x[1].mean_score, reverse=True)
        winner_name = sorted_opts[0][0]
        winner_score = sorted_opts[0][1].mean_score

        lines.append("**Decision Explanation**")
        lines.append("")
        lines.append(f"**{winner_name}** is the recommended option")
        lines.append(f"with a weighted score of **{winner_score:.3f}** ")
        lines.append(f"out of a maximum possible **{waterfall.get('max_possible', 1.0):.1f}**.")
        lines.append("")

        if not topsis_scores.empty:
            topsis_winner = topsis_scores.index[0]
            if topsis_winner != winner_name:
                lines.append(
                    f"Note: TOPSIS (risk-adjusted distance to ideal) favors **{topsis_winner}**, "
                    f"while Monte Carlo expected value favors **{winner_name}**. "
                    f"This disagreement suggests the decision is sensitive to your risk tolerance."
                )
                lines.append("")

        if counterfactual.get("flip_scenarios"):
            runner_up = counterfactual.get("runner_up")
            gap = counterfactual.get("gap", 0)
            lines.append(f"**Why not {runner_up}?**")
            lines.append(
                f"The gap is **{gap:.3f}** points. "
                f"Here is what would need to change for {runner_up} to overtake {winner_name}:"
            )
            lines.append("")

            flip_list = counterfactual["flip_scenarios"].get(runner_up, [])
            feasible = [s for s in flip_list if s.get("feasible")]
            if feasible:
                best = feasible[0]
                lines.append(
                    f"- If the weight of **{best['factor']}** changed from "
                    f"{best['current_value']:.2f} to {best['needed_value']:.2f} "
                    f"({best['change_pct']}), {runner_up} would win."
                )
            if flip_list:
                lines.append("- Other scenarios that would flip the outcome:")
                for s in flip_list[:3]:
                    feasibility = "feasible" if s.get("feasible") else "requires significant change"
                    lines.append(f"  - Adjust **{s['factor']}** weight by {s['change_pct']} ({feasibility})")
            lines.append("")

        winner_factors = waterfall.get("options", {}).get(winner_name, {}).get("factors", [])
        if winner_factors:
            lines.append("**Key drivers for the winner:**")
            for item in winner_factors[:3]:
                lines.append(
                    f"- **{item['name']}** contributed "
                    f"{item['contribution']:.3f} points ({item['pct_of_total']:.0f}% of total), "
                    f"with a normalized score of {item['normalized']:.2f} "
                    f"(direction: {item['direction']}, weight: {item['weight']:.2f})"
                )
            lines.append("")

        if use_ai:
            try:
                from decision_maker.core.gemini_agent import GeminiDeepResearchAgent

                agent = GeminiDeepResearchAgent()
                if agent.is_available:
                    prompt = (
                        f"Explain this multi-criteria decision analysis in simple terms:\n"
                        f"- Winner: {winner_name}\n"
                        f"- Score: {winner_score:.3f}\n"
                        f"- Options: {list(mc_results.keys())}\n"
                        f"- Factors: {[f'{f.name} (w={f.weight})' for f in factors]}\n"
                        f"- Waterfall: {waterfall}\n"
                        f"- Counterfactual: {counterfactual}\n"
                        f"Provide a short paragraph a business executive would understand."
                    )
                    ai_text = agent.research("Explain decision", prompt)
                    lines.append("**AI-Generated Analysis:**")
                    lines.append(ai_text if isinstance(ai_text, str) else str(ai_text))
            except (ConnectionError, TimeoutError, ValueError) as e:
                logger.warning(f"AI narrative generation failed: {e}")

        return "\n".join(lines)
