#!/usr/bin/env python3
"""
Mac Upgrade Decision — Comparación Express vs Standard vs Advanced
Basado en el caso original mac_upgrade_example.py
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from python.core.orchestrator import UnifiedDecisionFramework
from python.core.models import DecisionOption, Factor, DistributionType  # noqa: E402


def cost_score(price):      return max(0, 100 - (price / 50))
def perf_score(mult):       return min(100, mult * 10)
def long_score(years):      return min(100, years * 12)
def bat_score(hours):       return min(100, hours * 4)
def comfort_score(val):     return val * 10
def resale_score(val):      return min(100, val / 25)
def prod_score(hours):      return min(100, hours * 10)


def build_framework():
    fw = UnifiedDecisionFramework()
    fw.mc_engine.num_simulations = 50000

    fw.add_factor(Factor("Score_Performance", 0.30, maximize=True))
    fw.add_factor(Factor("Score_CostEfficiency", 0.20, maximize=True))
    fw.add_factor(Factor("Score_Longevity", 0.15, maximize=True))
    fw.add_factor(Factor("Score_Battery", 0.15, maximize=True))
    fw.add_factor(Factor("Score_Comfort", 0.10, maximize=True))
    fw.add_factor(Factor("Score_Resale", 0.05, maximize=True))
    fw.add_factor(Factor("Score_Productivity", 0.05, maximize=True))

    # Option A: Upgrade RAM
    opt_ram = DecisionOption("Upgrade RAM", "Low Cost, Low Performance")
    opt_ram.add_variable("Score_CostEfficiency", DistributionType.DETERMINISTIC, cost_score(450))
    opt_ram.add_variable("Score_Performance", DistributionType.NORMAL, perf_score(1.1), 2)
    opt_ram.add_variable("Score_Longevity", DistributionType.NORMAL, long_score(1.5), 5)
    opt_ram.add_variable("Score_Battery", DistributionType.NORMAL, bat_score(3.0), 5)
    opt_ram.add_variable("Score_Comfort", DistributionType.DETERMINISTIC, comfort_score(3))
    opt_ram.add_variable("Score_Resale", DistributionType.NORMAL, resale_score(200), 2)
    opt_ram.add_variable("Score_Productivity", DistributionType.NORMAL, prod_score(0.5), 2)
    fw.add_option(opt_ram)

    # Option B: M4 Max
    opt_m4 = DecisionOption("MacBook Pro M4 Max", "High Cost, Max Performance")
    opt_m4.add_variable("Score_CostEfficiency", DistributionType.NORMAL, cost_score(3800), 5)
    opt_m4.add_variable("Score_Performance", DistributionType.NORMAL, perf_score(6.0), 5)
    opt_m4.add_variable("Score_Longevity", DistributionType.NORMAL, long_score(6.0), 5)
    opt_m4.add_variable("Score_Battery", DistributionType.NORMAL, bat_score(18.0), 5)
    opt_m4.add_variable("Score_Comfort", DistributionType.DETERMINISTIC, comfort_score(9))
    opt_m4.add_variable("Score_Resale", DistributionType.NORMAL, resale_score(1800), 5)
    opt_m4.add_variable("Score_Productivity", DistributionType.NORMAL, prod_score(10.0), 5)
    fw.add_option(opt_m4)

    # Option C: Wait for M5
    opt_m5 = DecisionOption("Wait for M5", "Higher Risk/Reward")
    opt_m5.add_variable("Score_CostEfficiency", DistributionType.TRIANGULAR, cost_score(5000), cost_score(4500), cost_score(4000))
    opt_m5.add_variable("Score_Performance", DistributionType.NORMAL, perf_score(7.5), 5)
    opt_m5.add_variable("Score_Longevity", DistributionType.NORMAL, long_score(7.0), 5)
    opt_m5.add_variable("Score_Battery", DistributionType.NORMAL, bat_score(20.0), 5)
    opt_m5.add_variable("Score_Comfort", DistributionType.DETERMINISTIC, comfort_score(10))
    opt_m5.add_variable("Score_Resale", DistributionType.NORMAL, resale_score(2200), 5)
    opt_m5.add_variable("Score_Productivity", DistributionType.NORMAL, prod_score(11.0), 5)
    fw.add_option(opt_m5)

    return fw


async def main():
    print("=" * 72)
    print("  🍎 MAC UPGRADE DECISION — COMPARATIVA DE MODOS")
    print("=" * 72)

    for mode in ("express", "standard", "advanced"):
        print(f"\n{'=' * 72}")
        print(f"  MODO: {mode.upper()}")
        print(f"{'=' * 72}")

        fw = build_framework()
        result = await fw.run_analysis(mode=mode, results_dir=f"results/mac_upgrade_{mode}")

        mc = result["mc_results"]
        topsis = result["topsis_scores"]
        future = result["future"]

        print(f"\n  --- MC RANKING ---")
        for name, s in sorted(mc.items(), key=lambda x: x[1].mean_score, reverse=True):
            print(f"    {name:<22s}  Mean={s.mean_score:7.2f}  SD={s.std_dev:.2f}  VaR={s.var_95:.2f}  CVaR={s.cvar_95:.2f}")

        if not topsis.empty:
            print(f"\n  --- F-TOPSIS ---")
            for name, score in topsis.items():
                print(f"    {name:<22s}  Score={score:.4f}")

        if future:
            if "promethee_uncertainty" in future and not future["promethee_uncertainty"].empty:
                print(f"\n  --- PROMETHEE (con incertidumbre) ---")
                for name, score in future["promethee_uncertainty"].items():
                    print(f"    {name:<22s}  NetFlow={score:.4f}")

            if "robust_optimizer" in future:
                ro = future["robust_optimizer"]
                print(f"\n  --- ROBUST OPTIMIZER ---")
                print(f"    Winner: {ro.get('winner', 'N/A')}")
                for name, score in ro.get("robust_ranking", {}).items():
                    print(f"    {name:<22s}  RobustScore={score:.2f}")

            if "rank_aggregation" in future:
                ra = future["rank_aggregation"]
                print(f"\n  --- RANK AGGREGATION (Borda) ---")
                print(f"    Winner: {ra.get('winner', 'N/A')}")
                print(f"    Ranking: {ra.get('ranking', [])}")

            if "promethee_scores" in future and not future["promethee_scores"].empty:
                print(f"\n  --- PROMETHEE II (crisp) ---")
                for name, score in future["promethee_scores"].items():
                    print(f"    {name:<22s}  NetFlow={score:.4f}")

            if "bayesian_probs" in future:
                print(f"\n  --- BAYESIAN PROBS ---")
                for name, prob in future["bayesian_probs"].items():
                    print(f"    {name:<22s}  Prob={prob:.1%}")

            if "ideal_option" in future:
                ideal = future["ideal_option"]
                print(f"\n  --- GENETIC IDEAL ---")
                print(f"    Improvement: {ideal.get('improvement_potential', 0):.1f}%")
                print(f"    RawMax: {ideal.get('raw_max', 0):.2f}")

            if "bootstrap_ci" in future:
                print(f"\n  --- BOOTSTRAP CI ---")
                for name, ci in future["bootstrap_ci"].items():
                    print(f"    {name:<22s}  MeanRank={ci['mean_rank']:.2f}  CI=[{ci['ci_low']:.1f}, {ci['ci_high']:.1f}]  P(best)={ci['p_best']:.1%}")

        print(f"\n  Resultados guardados en: results/mac_upgrade_{mode}/")

    print(f"\n{'=' * 72}")
    print("  COMPARATIVA COMPLETADA")
    print(f"{'=' * 72}")


if __name__ == "__main__":
    asyncio.run(main())
