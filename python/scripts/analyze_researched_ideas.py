
import os
import sys
import asyncio

# Ensure we can import from core and scripts
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from python.core.models import DecisionOption, Factor, DistributionType
from python.core.orchestrator import UnifiedDecisionFramework

async def main():
    print("🚀 Auto-Business Analysis with Antigravity & Google Cloud (Researched Data)")
    print("-------------------------------------------------------------------------")
    print("Note: Using manually researched data as Gemini API unavailable in this env.")
    
    # 1. Initialize Decision Framework
    framework = UnifiedDecisionFramework()
    
    # 2. Define Factors for 'Passive/Automated' Business
    # Revised Weights to include Marketing/Sales reality (All units in $)
    # We convert "Effort" into "Dollar Cost of Time/Stress" to make them comparable in Monte Carlo.
    framework.add_factor(Factor(name="Monthly Revenue ($)", weight=1.0, maximize=True)) # Principal
    framework.add_factor(Factor(name="Setup Cost ($)", weight=1.0, maximize=False)) # One-time vs Monthly? Let's assume amortized or just keep separate.
    # Actually, Setup is one-time. Revenue is monthly. Mixing them is tricky. 
    # Let's treat Setup as amortized over 12 months for this view? Or just weight it lower.
    framework.add_factor(Factor(name="Setup Cost (Amortized $)", weight=1.0, maximize=False))
    
    # Psychological Costs (converted to $)
    framework.add_factor(Factor(name="Tech Difficulty Cost ($)", weight=1.0, maximize=False)) 
    framework.add_factor(Factor(name="Maintenance Cost ($)", weight=1.0, maximize=False))
    framework.add_factor(Factor(name="Acquisition Effort Cost ($)", weight=1.0, maximize=False))
    framework.add_factor(Factor(name="Marketing Cash Cost ($)", weight=1.0, maximize=False))
    
    # 3. Add Researched Options
    # CONVERSION RATES:
    # Difficulty 1 pt = $200 (Tech), $300 (Maint), $600 (Sales - User hates this)
    
    # Option 1: AI Customer Service Agency
    opt1 = DecisionOption(name="AI Customer Service Agency", description="Deploy Vertex AI agents for SMB customer support")
    opt1.add_variable("Monthly Revenue ($)", DistributionType.NORMAL, 5000, 1500) 
    opt1.add_variable("Setup Cost (Amortized $)", DistributionType.TRIANGULAR, 50, 100, 200) # $1000/10 months
    opt1.add_variable("Tech Difficulty Cost ($)", DistributionType.DETERMINISTIC, 6*200, 0, 0) # $1200
    opt1.add_variable("Maintenance Cost ($)", DistributionType.NORMAL, 7*300, 100) # $2100
    opt1.add_variable("Acquisition Effort Cost ($)", DistributionType.NORMAL, 8*600, 200) # $4800 (Heavy sales)
    opt1.add_variable("Marketing Cash Cost ($)", DistributionType.NORMAL, 300, 100)
    framework.add_option(opt1)

    # Option 2: Niche AI Micro-SaaS
    opt2 = DecisionOption(name="Niche AI Micro-SaaS", description="Specific tool like Resume Optimizer using Gemini API")
    opt2.add_variable("Monthly Revenue ($)", DistributionType.NORMAL, 2000, 1000) 
    opt2.add_variable("Setup Cost (Amortized $)", DistributionType.TRIANGULAR, 20, 50, 100) 
    opt2.add_variable("Tech Difficulty Cost ($)", DistributionType.DETERMINISTIC, 8*200, 0, 0) # $1600
    opt2.add_variable("Maintenance Cost ($)", DistributionType.NORMAL, 3*300, 50) # $900
    opt2.add_variable("Acquisition Effort Cost ($)", DistributionType.NORMAL, 5*600, 200) # $3000 (SEO is work)
    opt2.add_variable("Marketing Cash Cost ($)", DistributionType.NORMAL, 500, 200)
    framework.add_option(opt2)

    # Option 3: Automated Content Engine
    opt3 = DecisionOption(name="Automated Content Engine", description="Generate SEO blogs/newsletters")
    opt3.add_variable("Monthly Revenue ($)", DistributionType.NORMAL, 1500, 800) 
    opt3.add_variable("Setup Cost (Amortized $)", DistributionType.DETERMINISTIC, 10, 0, 0) 
    opt3.add_variable("Tech Difficulty Cost ($)", DistributionType.DETERMINISTIC, 4*200, 0, 0) # $800
    opt3.add_variable("Maintenance Cost ($)", DistributionType.NORMAL, 2*300, 50) # $600
    opt3.add_variable("Acquisition Effort Cost ($)", DistributionType.NORMAL, 7*600, 200) # $4200 (Fighting algorithms is tiring)
    opt3.add_variable("Marketing Cash Cost ($)", DistributionType.DETERMINISTIC, 50, 0, 0)
    framework.add_option(opt3)

    # Option 4: B2B Process Automation Service
    opt4 = DecisionOption(name="B2B Process Automation", description="Custom Vertex AI pipelines")
    opt4.add_variable("Monthly Revenue ($)", DistributionType.NORMAL, 8000, 3000) 
    opt4.add_variable("Setup Cost (Amortized $)", DistributionType.TRIANGULAR, 0, 20, 50) 
    opt4.add_variable("Tech Difficulty Cost ($)", DistributionType.DETERMINISTIC, 9*200, 0, 0) # $1800
    opt4.add_variable("Maintenance Cost ($)", DistributionType.NORMAL, 6*300, 100) # $1800
    opt4.add_variable("Acquisition Effort Cost ($)", DistributionType.NORMAL, 9*600, 100) # $5400 (Very hard sales)
    opt4.add_variable("Marketing Cash Cost ($)", DistributionType.NORMAL, 100, 50)
    framework.add_option(opt4)

    # Option 5: Digital Asset Factory
    opt5 = DecisionOption(name="Digital Asset Factory", description="Sell AI generated assets")
    opt5.add_variable("Monthly Revenue ($)", DistributionType.NORMAL, 800, 400) 
    opt5.add_variable("Setup Cost (Amortized $)", DistributionType.DETERMINISTIC, 5, 0, 0) 
    opt5.add_variable("Tech Difficulty Cost ($)", DistributionType.DETERMINISTIC, 3*200, 0, 0) # $600
    opt5.add_variable("Maintenance Cost ($)", DistributionType.NORMAL, 4*300, 50) # $1200
    opt5.add_variable("Acquisition Effort Cost ($)", DistributionType.NORMAL, 4*600, 100) # $2400
    opt5.add_variable("Marketing Cash Cost ($)", DistributionType.DETERMINISTIC, 0, 0, 0)
    framework.add_option(opt5)

    # 4. Run Analysis
    await framework.run_analysis(use_ai=False)

if __name__ == "__main__":
    asyncio.run(main())
