
import asyncio
import json
import os
import sys
from typing import Dict, List

# Ensure we can import from core and scripts
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from scripts.gemini_query import GeminiClient

from decision_maker.core.models import DecisionOption, DistributionType, Factor
from decision_maker.core.orchestrator import UnifiedDecisionFramework


def parse_gemini_response(response_text: str) -> List[Dict]:
    """
    Parses the Gemini response to extract business ideas.
    Expected format is JSON or a structured list.
    We will ask Gemini to output JSON.
    """
    cleaned_text = response_text.replace("```json", "").replace("```", "").strip()
    try:
        return json.loads(cleaned_text)
    except json.JSONDecodeError:
        # Try to find list start/end if entire text isn't JSON
        try:
            start = cleaned_text.find('[')
            end = cleaned_text.rfind(']') + 1
            if start != -1 and end != -1:
                return json.loads(cleaned_text[start:end])
        except Exception:
            pass

        print(f"Failed to parse JSON: {response_text[:100]}...")
        return []

async def main():
    print("🤖 Initializing Autonomous Business Search with Antigravity & Google Cloud...")

    # 1. Initialize Gemini Client to get ideas
    client = GeminiClient()

    prompt = """
    I need 5 concrete, automated business ideas that leverage 'Antigravity' (an advanced AI coding agent) and Google Cloud Platform (GCP).
    The goal is to build a "passive income" or "automated service" business.
    
    For each idea, provide:
    1. 'name': A catchy title.
    2. 'description': Brief explanation of how it works.
    3. 'estimated_monthly_revenue': Conservative estimate in USD (number only).
    4. 'setup_cost': Estimated initial cost in USD (number only).
    5. 'technical_difficulty': 1 to 10 (10 is hardest).
    6. 'maintenance_effort': 1 to 10 (10 is highest effort).
    7. 'success_probability': 0.0 to 1.0.
    
    Output purely as a JSON list of objects. No intro text.
    """

    print("\n🔍 Asking Gemini for business ideas...")
    response_text = client.query(prompt)

    ideas = parse_gemini_response(response_text)

    if not ideas:
        print("❌ Could not generate ideas. Exiting.")
        return

    print(f"\n✅ Found {len(ideas)} ideas. Analyzing with Unified Decision Framework...")

    # 2. Initialize Decision Framework
    framework = UnifiedDecisionFramework()

    # Define Factors
    # We want High Revenue, Low Cost, Low Difficulty, Low Maintenance
    framework.add_factor(Factor(name="Monthly Revenue", weight=0.4, maximize=True))
    framework.add_factor(Factor(name="Setup Cost", weight=0.2, maximize=False))
    framework.add_factor(Factor(name="Tech Difficulty", weight=0.1, maximize=False)) # Lower is better
    framework.add_factor(Factor(name="Maintenance", weight=0.3, maximize=False))    # Lower is better

    # 3. Add Options from Gemini
    for idea in ideas:
        opt = DecisionOption(name=idea['name'], description=idea['description'])

        # Determine distributions based on single point estimates + uncertainty
        # Revenue: Normal distribution centered on estimate
        rev = float(idea['estimated_monthly_revenue'])
        opt.add_variable("Monthly Revenue", DistributionType.NORMAL, rev, rev * 0.2) # 20% std dev

        # Setup Cost: Triangular (estimate, estimate, estimate*1.5)
        cost = float(idea['setup_cost'])
        opt.add_variable("Setup Cost", DistributionType.TRIANGULAR, cost*0.8, cost, cost*1.5)

        # Tech Difficulty: Deterministic (or slight variance)
        diff = float(idea['technical_difficulty'])
        opt.add_variable("Tech Difficulty", DistributionType.NORMAL, diff, 1.0)

        # Maintenance: Deterministic
        maint = float(idea['maintenance_effort'])
        opt.add_variable("Maintenance", DistributionType.NORMAL, maint, 1.0)

        framework.add_option(opt)

        print(f"   -> Added option: {idea['name']}")

    # 4. Run Analysis
    # We use await because run_analysis is async
    await framework.run_analysis(use_ai=False) # AI research already done above, we just analyze now

if __name__ == "__main__":
    asyncio.run(main())
