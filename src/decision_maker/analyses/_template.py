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
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from decision_maker.core.models import DecisionOption, DistributionType, Factor, UncertainVariable
from decision_maker.core.orchestrator import UnifiedDecisionFramework

# ============================================================
# ANALYSIS CONFIGURATION
# ============================================================

analysis_name = "TODO_CHANGE_ME"
analysis_date = datetime.now().isoformat()

# ============================================================
# DEFINE FACTORS (criteria for evaluation)
# ============================================================

factors = [
    Factor(name="Cost", weight=0.3, maximize=False),
    Factor(name="Benefit", weight=0.4, maximize=True),
    Factor(name="Risk", weight=0.3, maximize=False),
]

# ============================================================
# DEFINE OPTIONS (alternatives with uncertain variables)
# ============================================================

options = [
    DecisionOption(
        name="Option A",
        description="Description of option A",
        variables={
            "Cost": UncertainVariable("Cost", DistributionType.NORMAL, [5000, 1000]),
            "Benefit": UncertainVariable("Benefit", DistributionType.NORMAL, [8000, 2000]),
            "Risk": UncertainVariable("Risk", DistributionType.UNIFORM, [0.1, 0.5]),
        },
    ),
    DecisionOption(
        name="Option B",
        description="Description of option B",
        variables={
            "Cost": UncertainVariable("Cost", DistributionType.NORMAL, [3000, 500]),
            "Benefit": UncertainVariable("Benefit", DistributionType.NORMAL, [6000, 1500]),
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

    print(f"\nAnalysis '{analysis_name}' completed.")
    print(f"Winner: {results.get('explanation', 'N/A')[:100]}...")

    # Save results
    output_file = f"results/{analysis_name.lower().replace(' ', '_')}.json"
    Path("results").mkdir(exist_ok=True)
    with open(output_file, "w") as f:
        json.dump({"name": analysis_name, "date": analysis_date}, f, indent=2)
    print(f"Results saved to {output_file}")


if __name__ == "__main__":
    asyncio.run(main())
