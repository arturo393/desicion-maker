"""
Template: Decision Analysis - [NAME]
Purpose: [What decision is being analyzed]
Created: [YYYY-MM-DD]
Last Updated: [YYYY-MM-DD]
Version: 1.0

CHANGES IN THIS VERSION:
- [Change 1]
- [Change 2]

NEXT STEPS:
- [ ] Step 1
- [ ] Step 2

NOTES:
- Add important notes here
"""

import asyncio
import json
from datetime import datetime
from pathlib import Path

from decision_maker.core.models import DecisionOption, DistributionType, Factor, UncertainVariable
from decision_maker.core.orchestrator import UnifiedDecisionFramework
from decision_maker.core.weight_derivation import WeightDerivationEngine
from decision_maker.ledger_cli import show_commitment_draft

# ============================================================
# ANALYSIS CONFIGURATION
# ============================================================

analysis_name = "TODO_CHANGE_ME"
analysis_date = datetime.now().isoformat()

# ============================================================
# DEFINE FACTORS (criteria for evaluation)
# ============================================================

# Weights by swing, not by gut. Picture every factor at its WORST value among YOUR options. Which one
# factor would you most want to move to its BEST value? That move scores 100; score the others against
# it. You are weighting the gap your options actually span ($8,000 → $2,500), not "cost" in the
# abstract: the engine stretches every gap to the same 0-1 scale, so a weight typed without looking at
# the range overstates small differences. The run warns when a factor's gap is under 5 %.
SWING = {
    "Benefit": 100,  # 3,000 → 8,000
    "Cost": 60,      # 8,000 → 2,500
    "Risk": 30,      # 0.6 → 0.1
}
weights = WeightDerivationEngine.swing_weights(SWING)["weights"]

factors = [
    Factor(name="Cost", weight=weights["Cost"], maximize=False),
    Factor(name="Benefit", weight=weights["Benefit"], maximize=True),
    Factor(name="Risk", weight=weights["Risk"], maximize=False),
]

# ============================================================
# DEFINE OPTIONS (alternatives with uncertain variables)
# Costs and durations: PERT [min, most likely, max]. It stays inside its bounds and skews the way
# estimates do; a NORMAL cost draws negative values. NORMAL is for quantities that can go both ways.
# ============================================================

options = [
    DecisionOption(
        name="Option A",
        description="Description of option A",
        variables={
            "Cost": UncertainVariable("Cost", DistributionType.PERT, [3500, 4500, 8000]),
            "Benefit": UncertainVariable("Benefit", DistributionType.NORMAL, [8000, 800]),
            "Risk": UncertainVariable("Risk", DistributionType.UNIFORM, [0.1, 0.5]),
        },
    ),
    DecisionOption(
        name="Option B",
        description="Description of option B",
        variables={
            "Cost": UncertainVariable("Cost", DistributionType.PERT, [2500, 3000, 4500]),
            "Benefit": UncertainVariable("Benefit", DistributionType.NORMAL, [3000, 500]),
            "Risk": UncertainVariable("Risk", DistributionType.UNIFORM, [0.2, 0.6]),
        },
    ),
]

# ============================================================
# RUN ANALYSIS
# ============================================================


async def main():
    fw = UnifiedDecisionFramework()
    for f in factors:
        fw.add_factor(f)
    for o in options:
        fw.add_option(o)

    results = await fw.run_analysis(mode="standard")
    print(f"\nAnalysis '{analysis_name}'")

    # 1. What the scores say, with their spread. No winner is printed if the gates halted.
    for name, st in sorted(results["mc_results"].items(), key=lambda kv: -kv[1].mean_score):
        print(f"  {name:<12} mean {st.mean_score:.3f}   p5 {st.percentile_5:.3f}   p95 {st.percentile_95:.3f}")
    if results.get("pipeline_halted"):
        print(f"\nNo recommendation: {results['gate_result']['halt_reason']}")
        print("The estimates spread wider than the gap between options: narrow the widest ones first.")
        return

    # 2. Whether the winner survives other defensible weights.
    wr = results["weight_robustness"]
    print(f"\nWeights: {wr['stated_winner']} is {wr['verdict']} — "
          f"wins {wr['informed'][wr['stated_winner']]:.0%} near your weights, "
          f"{wr['uninformed'][wr['stated_winner']]:.0%} with weights unknown")

    # 3. A run never commits. If you take the decision, record it so it can be checked later.
    show_commitment_draft(results)

    output_file = Path("results") / f"{analysis_name.lower().replace(' ', '_')}.json"
    output_file.parent.mkdir(exist_ok=True)
    output_file.write_text(json.dumps({
        "name": analysis_name,
        "date": analysis_date,
        "means": {n: st.mean_score for n, st in results["mc_results"].items()},
        "weight_robustness": wr,
        "commitment_draft": results.get("commitment_draft"),
    }, indent=2))
    print(f"\nSaved {output_file}")


if __name__ == "__main__":
    asyncio.run(main())
