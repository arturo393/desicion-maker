"""
Visualization engine generating decision charts, risk profiles, and sensitivity plots.
Usage: from decision_maker.core.visualization import VisualizationEngine
Does NOT: Perform raw statistical simulation or decision calculations.
"""

from __future__ import annotations

__all__ = ["VisualizationEngine", "PlotContext"]

from dataclasses import dataclass

import logging
import os

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from decision_maker.core.models import Factor, Statistics

logger = logging.getLogger(__name__)


@dataclass
class PlotContext:
    """Bundles data needed to generate the plot suite (Parameter Object)."""

    mc_results: dict[str, Statistics]
    factors: list[Factor]
    future_metrics: dict
    output_dir: str
    timestamp: str


class VisualizationEngine:
    def __init__(self, style: str = "dark_background"):
        plt.style.use(style)
        plt.rcParams["figure.facecolor"] = "#161b22"
        plt.rcParams["axes.facecolor"] = "#161b22"
        plt.rcParams["axes.edgecolor"] = "#30363d"
        plt.rcParams["axes.labelcolor"] = "#8b949e"
        plt.rcParams["xtick.color"] = "#8b949e"
        plt.rcParams["ytick.color"] = "#8b949e"
        plt.rcParams["text.color"] = "#e6edf3"
        plt.rcParams["font.size"] = 10
        plt.rcParams["figure.figsize"] = (12, 7)

    def generate_all_plots(self, ctx: PlotContext) -> list[str]:
        """Generates a suite of plots and returns their paths."""
        mc_results = ctx.mc_results
        factors = ctx.factors
        future_metrics = ctx.future_metrics
        output_dir = ctx.output_dir
        timestamp = ctx.timestamp

        os.makedirs(output_dir, exist_ok=True)
        paths = []

        # 1. Distribution Plot (Risk Profile)
        dist_path = self.plot_risk_distributions(mc_results, output_dir, timestamp)
        paths.append(dist_path)

        # 2. Factor Importance Plot (Mutual Information)
        if "info_theory" in future_metrics:
            info_path = self.plot_factor_importance(future_metrics["info_theory"], output_dir, timestamp)
            paths.append(info_path)

        # 3. Robustness & Stability Plot
        if "robust_optimizer" in future_metrics:
            robust_path = self.plot_robustness(future_metrics["robust_optimizer"], output_dir, timestamp)
            paths.append(robust_path)

        return paths

    def plot_risk_distributions(self, mc_results: dict[str, Statistics], output_dir: str, timestamp: str) -> str:
        plt.figure(figsize=(10, 6))
        for name, stats in mc_results.items():
            if stats.raw_scores is not None:
                sns.kdeplot(stats.raw_scores, label=f"{name}", fill=True, alpha=0.4, linewidth=2)

        plt.title("Risk Profiles: How likely is each outcome?", pad=20, fontsize=14, fontweight="bold")
        plt.xlabel("Quality Score (0-1)", fontsize=12)
        plt.ylabel("Probability Density", fontsize=12)
        plt.legend(frameon=False, loc="upper left")
        plt.grid(True, alpha=0.1)

        path = os.path.join(output_dir, f"risk_profiles_{timestamp}.png")
        plt.savefig(path, dpi=150, bbox_inches="tight")
        plt.close()
        return path

    def plot_factor_importance(self, info_theory_results: dict, output_dir: str, timestamp: str) -> str:
        if not info_theory_results:
            logger.warning("No information theory results to plot")
            return ""
        first_opt = next(iter(info_theory_results))
        mi_data = info_theory_results[first_opt]

        df = pd.DataFrame(list(mi_data.items()), columns=["Factor", "Importance"])
        df = df.sort_values("Importance", ascending=False)

        plt.figure()
        sns.barplot(x="Importance", y="Factor", data=df, hue="Factor", palette="viridis", legend=False)
        plt.title(f"Non-linear Factor Importance (Mutual Information) - {first_opt}")
        plt.xlabel("Relative Information Gain (0-1)")
        plt.ylabel("Decision Factor")

        path = os.path.join(output_dir, f"factor_importance_{timestamp}.png")
        plt.savefig(path, dpi=150, bbox_inches="tight")
        plt.close()
        return path

    def plot_robustness(self, robust_results: dict, output_dir: str, timestamp: str) -> str:
        # Comparison of DRO scores vs Mean scores
        data = []
        for opt, dro_score in robust_results.get("dro_scores", {}).items():
            stability = robust_results.get("stability_metrics", {}).get(opt, 0)
            data.append({"Option": opt, "DRO_Score": dro_score, "Stability": stability})

        df = pd.DataFrame(data)

        fig, ax1 = plt.subplots(figsize=(10, 6))

        # Bar for DRO Score
        sns.barplot(
            x="Option", y="DRO_Score", data=df, ax=ax1, alpha=0.8, hue="Option", palette="viridis", legend=False
        )
        ax1.set_ylabel("Defensive Score (Worst Case)", color="#58a6ff", fontsize=11)
        ax1.set_xlabel("")
        ax1.tick_params(axis="x", rotation=15)

        # Line for Stability
        ax2 = ax1.twinx()
        sns.lineplot(x="Option", y="Stability", data=df, ax=ax2, marker="o", color="#f85149", linewidth=3, markersize=8)
        ax2.set_ylabel("Certainty Level (0-1)", color="#f85149", fontsize=11)
        ax2.set_ylim(0, 1.1)
        ax2.grid(False)

        plt.title("Robustness Audit: Defense vs Consistency", pad=20, fontsize=14, fontweight="bold")

        path = os.path.join(output_dir, f"robustness_audit_{timestamp}.png")
        plt.savefig(path, dpi=150, bbox_inches="tight")
        plt.close()
        return path
