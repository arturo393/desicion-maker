#!/usr/bin/env python3
"""
💻 Decision Case: Mac Upgrade (2026 Edition)
Unified Framework v2.0 Demo

Decision:
1. Upgrade current MacBook Pro RAM (32GB -> 64GB)
2. Buy new MacBook Pro M4 Max (Brand New)
3. Wait for M5 (Risk/Reward)

Factors:
- Cost (Minimize)
- Performance Multiplier (Maximize)
- Longevity (Years) (Maximize)
"""

import sys
import os
import asyncio

# Fix path to import core logic
sys.path.append(os.path.join(os.path.dirname(__file__), "../python"))

from python.core.orchestrator import UnifiedDecisionFramework
from python.core.models import DecisionOption, Factor, DistributionType

async def main():
    print("🍎 Setting up Mac Upgrade Decision...")
    
    framework = UnifiedDecisionFramework()
    framework.mc_engine.num_simulations = 50000  # High precision
    
    # =========================================================================
    # 1. DEFINE FACTORS (All standardized to 0-100 Utility Score)
    # =========================================================================
    
    # Weights sum to 1.0 ideally
    framework.add_factor(Factor("Score_Performance", 0.30, maximize=True))
    framework.add_factor(Factor("Score_CostEfficiency", 0.20, maximize=True)) # Higher is better (Cheaper)
    framework.add_factor(Factor("Score_Longevity", 0.15, maximize=True))
    framework.add_factor(Factor("Score_Battery", 0.15, maximize=True))
    framework.add_factor(Factor("Score_Comfort", 0.10, maximize=True))
    framework.add_factor(Factor("Score_Resale", 0.05, maximize=True))
    framework.add_factor(Factor("Score_Productivity", 0.05, maximize=True))

    
    # =========================================================================
    # 2. DEFINE OPTIONS
    # =========================================================================

    # =========================================================================
    # helper: Utility Functions
    # =========================================================================
    def cost_score(price):      return max(0, 100 - (price / 50))       # $5000 = 0, $0 = 100
    def perf_score(mult):       return min(100, mult * 10)              # 10x = 100, 1x = 10
    def long_score(years):      return min(100, years * 12)             # 8y = 96, 1y = 12
    def bat_score(hours):       return min(100, hours * 4)              # 25h = 100, 5h = 20
    def comfort_score(val):     return val * 10                         # 10 = 100
    def resale_score(val):      return min(100, val / 25)               # $2500 = 100
    def prod_score(hours):      return min(100, hours * 10)             # 10h = 100
    
    # --- Option A: Upgrade RAM (Keep Intel) ---
    opt_ram = DecisionOption("Upgrade RAM (Keep Intel)", "Low Cost, Low Performance")
    
    # Cost: $450 -> Score ~91
    opt_ram.add_variable("Score_CostEfficiency", DistributionType.DETERMINISTIC, cost_score(450))
    # Performance: 1.1x -> Score ~11
    opt_ram.add_variable("Score_Performance", DistributionType.NORMAL, perf_score(1.1), 2)
    # Longevity: 1.5y -> Score ~18
    opt_ram.add_variable("Score_Longevity", DistributionType.NORMAL, long_score(1.5), 5)
    # Battery: 3h -> Score ~12
    opt_ram.add_variable("Score_Battery", DistributionType.NORMAL, bat_score(3.0), 5)
    # Comfort: 3/10 -> Score 30
    opt_ram.add_variable("Score_Comfort", DistributionType.DETERMINISTIC, comfort_score(3))
    # Resale: $200 -> Score 8
    opt_ram.add_variable("Score_Resale", DistributionType.NORMAL, resale_score(200), 2)
    # Productivity: 0.5h -> Score 5
    opt_ram.add_variable("Score_Productivity", DistributionType.NORMAL, prod_score(0.5), 2)
    
    framework.add_option(opt_ram)
    
    # --- Option B: Buy M4 Max (Powerhouse) ---
    opt_m4 = DecisionOption("New MacBook Pro M4 Max", "High Cost, Max Performance")
    
    # Cost: $3800 -> Score ~24
    opt_m4.add_variable("Score_CostEfficiency", DistributionType.NORMAL, cost_score(3800), 5)
    # Performance: 6.0x -> Score 60
    opt_m4.add_variable("Score_Performance", DistributionType.NORMAL, perf_score(6.0), 5)
    # Longevity: 6.0y -> Score 72
    opt_m4.add_variable("Score_Longevity", DistributionType.NORMAL, long_score(6.0), 5)
    # Battery: 18h -> Score 72
    opt_m4.add_variable("Score_Battery", DistributionType.NORMAL, bat_score(18.0), 5)
    # Comfort: 9/10 -> Score 90
    opt_m4.add_variable("Score_Comfort", DistributionType.DETERMINISTIC, comfort_score(9))
    # Resale: $1800 -> Score 72
    opt_m4.add_variable("Score_Resale", DistributionType.NORMAL, resale_score(1800), 5)
    # Productivity: 10h -> Score 100
    opt_m4.add_variable("Score_Productivity", DistributionType.NORMAL, prod_score(10.0), 5)
    
    framework.add_option(opt_m4)
    
    # --- Option C: Wait for M5 (Future) ---
    opt_m5 = DecisionOption("Wait for M5 (Late 2027)", "Higher Risk/Reward")
    
    # Cost: $4500 -> Score ~10
    opt_m5.add_variable("Score_CostEfficiency", DistributionType.TRIANGULAR, cost_score(5000), cost_score(4500), cost_score(4000))
    # Performance: 7.5x -> Score 75
    opt_m5.add_variable("Score_Performance", DistributionType.NORMAL, perf_score(7.5), 5)
    # Longevity: 7.0y -> Score 84
    opt_m5.add_variable("Score_Longevity", DistributionType.NORMAL, long_score(7.0), 5)
    # Battery: 20h -> Score 80
    opt_m5.add_variable("Score_Battery", DistributionType.NORMAL, bat_score(20.0), 5)
    # Comfort: 10/10 -> Score 100
    opt_m5.add_variable("Score_Comfort", DistributionType.DETERMINISTIC, comfort_score(10))
    # Resale: $2200 -> Score 88
    opt_m5.add_variable("Score_Resale", DistributionType.NORMAL, resale_score(2200), 5)
    # Productivity: 11h -> Score 100
    opt_m5.add_variable("Score_Productivity", DistributionType.NORMAL, prod_score(11.0), 5)
    
    framework.add_option(opt_m5)
    
    # =========================================================================
    # 3. RUN ANALYSIS
    # =========================================================================
    
    # Check if user wants AI research
    use_ai = "--ai" in sys.argv
    await framework.run_analysis(use_ai=use_ai)

if __name__ == "__main__":
    asyncio.run(main())
