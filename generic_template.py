import asyncio
import sys
import os

# Add python directory to path so we can import core modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'python')))

from python.core.unified_decision_framework import (
    UnifiedDecisionFramework, 
    DecisionOption, 
    Factor, 
    DistributionType
)

async def main():
    """
    GENERIC DECISION TEMPLATE
    -------------------------
    Use this file to model any decision you want to make.
    1. Define what matters to you (Factors).
    2. Define your choices (Options).
    3. Run the simulation.
    """
    
    # 1. Initialize Framework
    # -----------------------
    framework = UnifiedDecisionFramework()
    framework.mc_engine.num_simulations = 10000  # Adjust precision (1k-100k)

    # 2. Define Factors (Criteria)
    # ----------------------------
    # name: Label for the criteria (e.g. "Cost", "Risk", "Happiness")
    # weight: Importance (0.0 to 1.0). Total should ideally sum to 1.0.
    # maximize: True if "higher is better" (Profit), False if "lower is better" (Cost).
    
    framework.add_factor(Factor("Cost", 0.4, maximize=False))      # Minimizing Cost
    framework.add_factor(Factor("ROI", 0.4, maximize=True))        # Maximizing Return
    framework.add_factor(Factor("Risk", 0.2, maximize=False))      # Minimizing Risk

    # 3. Define Options (Choices)
    # ---------------------------
    
    # --- Option A ---
    opt_a = DecisionOption("Option A (Conservative)", "Safe bet")
    # Add variables for each factor defined above.
    # DistributionType.NORMAL: Mean, StdDev
    # DistributionType.TRIANGULAR: Min, Mode, Max
    # DistributionType.DETERMINISTIC: Exact Value
    
    opt_a.add_variable("Cost", DistributionType.DETERMINISTIC, 1000)
    opt_a.add_variable("ROI", DistributionType.NORMAL, 1.2, 0.1)     # 20% return ±10%
    opt_a.add_variable("Risk", DistributionType.DETERMINISTIC, 2)    # Low risk (2/10)
    framework.add_option(opt_a)

    # --- Option B ---
    opt_b = DecisionOption("Option B (Aggressive)", "High risk, high reward")
    
    opt_b.add_variable("Cost", DistributionType.TRIANGULAR, 800, 1200, 1500)
    opt_b.add_variable("ROI", DistributionType.NORMAL, 2.5, 0.8)     # 150% return ±80%
    opt_b.add_variable("Risk", DistributionType.UNIFORM, 5, 9)       # High risk (5-9/10)
    framework.add_option(opt_b)

    # 4. Run Analysis
    # ---------------
    print("🚀 Running Monte Carlo Simulation...")
    await framework.run_analysis(use_ai=False) # Set True to use Gemini for insights (requires API Key)

if __name__ == "__main__":
    asyncio.run(main())
