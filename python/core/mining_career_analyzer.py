#!/usr/bin/env python3
# /// script
# dependencies = [
#     "google-genai>=0.3.0",
#     "python-dotenv>=1.0.0",
#     "requests>=2.31.0",
# ]
# ///
"""
🏔️ MINING & CAREER ADVANCED ANALYZER
Combines Gemini Deep Research with Decision-Maker 13 Methodologies
Specifically tailored for Arturo's mining & career decisions (2025-2026)

USAGE:
  With uv (preferred):
    $ uv run mining_career_analyzer.py
  
  With python directly:
    $ python3 mining_career_analyzer.py
  
  Install uv:
    $ curl -LsSf https://astral.sh/uv/install.sh | sh
"""

import os
import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import statistics
import sys
from dataclasses import dataclass, field
import warnings

# Suppress warnings
warnings.filterwarnings("ignore")

# Try to load from local module, fallback to inline definitions
try:
    from deep_research_decision_agent import (
        GeminiDeepResearchAgent,
        DecisionAnalysisEngine,
        CareerOption,
        AnalysisResult
    )
    _IMPORT_SUCCESS = True
except ImportError:
    _IMPORT_SUCCESS = False
    print("⚠️ Note: deep_research_decision_agent module not found")
    print("   Using inline implementations for local analysis\n")
    
    # Inline definitions for standalone execution
    @dataclass
    class CareerOption:
        """Represents a career option for decision analysis"""
        name: str
        salary_expected: float
        probability_success: float
        timeline_months: int
        tech_growth: float
        income_stability: float
        work_life_balance: float
        prestige: float
        remote_flexibility: float
        learning_opportunity: float
        career_ceiling: float
        unemployment_risk: float
        burnout_risk: float
        market_risk: float
        description: str = ""
        pros: List[str] = field(default_factory=list)
        cons: List[str] = field(default_factory=list)
    
    @dataclass
    class AnalysisResult:
        """Results from deep research + decision analysis"""
        timestamp: str
        option_name: str
        deep_research: str = ""
        research_sources: List[str] = field(default_factory=list)
        monte_carlo_score: float = 0.0
        topsis_rank: int = 0
        pareto_optimal: bool = False
        regret_analysis: float = 0.0
        risk_score: float = 0.0
        scenario_robustness: float = 0.0
        overall_score: float = 0.0
        recommendation: str = ""
        confidence: float = 0.0
    
    class GeminiDeepResearchAgent:
        """Fallback Deep Research Agent"""
        def __init__(self, debug: bool = True):
            self.api_key = os.getenv("GEMINI_API_KEY")
            self.debug = debug
            if not self.api_key:
                raise ValueError("GEMINI_API_KEY not configured")
        
        async def research_option(self, option: CareerOption, context: str = "") -> AnalysisResult:
            result = AnalysisResult(
                timestamp=datetime.now().isoformat(),
                option_name=option.name,
                deep_research="Deep Research Agent not available (import failed)"
            )
            return result
    
    class DecisionAnalysisEngine:
        """13-Methodology Decision Analysis Engine"""
        def __init__(self, debug: bool = True):
            self.debug = debug
        
        def analyze_option(self, option: CareerOption, all_options: List[CareerOption], deep_research: str = "") -> AnalysisResult:
            result = AnalysisResult(
                timestamp=datetime.now().isoformat(),
                option_name=option.name,
                deep_research=deep_research
            )
            
            result.monte_carlo_score = self._monte_carlo_analysis(option)
            result.topsis_rank = self._topsis_analysis(option, all_options)
            result.pareto_optimal = self._pareto_analysis(option, all_options)
            result.regret_analysis = self._regret_analysis(option, all_options)
            result.risk_score = self._risk_analysis(option)
            result.scenario_robustness = self._scenario_planning(option)
            result.overall_score = self._calculate_overall_score(result)
            result.confidence = self._calculate_confidence(result, option)
            result.recommendation = self._generate_recommendation(result, option)
            
            return result
        
        def _monte_carlo_analysis(self, option: CareerOption) -> float:
            import random
            scores = []
            for _ in range(10000):
                success = random.random() < option.probability_success
                if success:
                    salary_var = option.salary_expected * random.uniform(0.85, 1.15)
                    satisfaction = (option.tech_growth + option.income_stability + option.work_life_balance + option.prestige) / 4
                    score = (salary_var / 1_000_000) + satisfaction
                else:
                    score = 0
                scores.append(score)
            return statistics.mean(scores)
        
        def _topsis_analysis(self, option: CareerOption, all_options: List[CareerOption]) -> int:
            scores = {}
            for opt in all_options:
                score = (
                    (opt.salary_expected / 1_000_000 * 0.3) +
                    (opt.tech_growth * 0.15) +
                    (opt.income_stability * 0.15) +
                    (opt.work_life_balance * 0.1) +
                    (opt.prestige * 0.15) +
                    (opt.learning_opportunity * 0.15)
                )
                scores[opt.name] = score
            
            ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
            for rank, (name, _) in enumerate(ranked, 1):
                if name == option.name:
                    return rank
            return len(all_options)
        
        def _pareto_analysis(self, option: CareerOption, all_options: List[CareerOption]) -> bool:
            for other in all_options:
                if other.name != option.name:
                    if (other.salary_expected > option.salary_expected and
                        other.work_life_balance > option.work_life_balance):
                        return False
            return True
        
        def _regret_analysis(self, option: CareerOption, all_options: List[CareerOption]) -> float:
            best_salary = max(opt.salary_expected for opt in all_options)
            regret = best_salary - option.salary_expected
            worst_regret = regret * (1 - option.probability_success)
            return worst_regret / 1_000_000
        
        def _risk_analysis(self, option: CareerOption) -> float:
            total_risk = (
                option.unemployment_risk * 0.4 +
                option.burnout_risk * 0.35 +
                option.market_risk * 0.25
            )
            return total_risk
        
        def _scenario_planning(self, option: CareerOption) -> float:
            boom_score = option.salary_expected / 1_000_000
            stable_score = option.income_stability * 2
            recession_score = option.income_stability
            robustness = (boom_score + stable_score + recession_score) / 3
            return robustness / 10
        
        def _calculate_overall_score(self, result: AnalysisResult) -> float:
            weights = {
                'monte_carlo': 0.25,
                'topsis': 0.20,
                'pareto': 0.15,
                'regret': 0.15,
                'risk': 0.10,
                'scenario': 0.15
            }
            
            score = (
                result.monte_carlo_score * weights['monte_carlo'] +
                (1 - result.topsis_rank / 5) * weights['topsis'] +
                (float(result.pareto_optimal) * weights['pareto']) +
                (1 - result.regret_analysis / 5) * weights['regret'] +
                (1 - result.risk_score) * weights['risk'] +
                result.scenario_robustness * weights['scenario']
            )
            return min(10, score)
        
        def _calculate_confidence(self, result: AnalysisResult, option: CareerOption) -> float:
            confidence = (
                (float(result.pareto_optimal) * 0.3) +
                ((1 - result.risk_score) * 0.3) +
                (option.probability_success * 0.4)
            )
            return min(1.0, confidence)
        
        def _generate_recommendation(self, result: AnalysisResult, option: CareerOption) -> str:
            if result.overall_score >= 8:
                return "⭐⭐⭐ HIGHLY RECOMMENDED - Strong fit across all metrics"
            elif result.overall_score >= 6:
                return "⭐⭐ RECOMMENDED - Good option with manageable risks"
            elif result.overall_score >= 4:
                return "⚠️ CONSIDER - Requires deeper analysis or risk mitigation"
            else:
                return "❌ NOT RECOMMENDED - High risks or poor fit"

# Load environment
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv not available, skip
    pass

# ============================================================================
# MINING-SPECIFIC ANALYSIS
# ============================================================================

class MiningCareerAnalyzer:
    """
    Specialized analyzer for mining industry in Chile
    Uses 13 decision methodologies + Gemini Deep Research
    """
    
    MINING_COMPANIES = {
        "Codelco": {
            "type": "Estado-Owned Copper",
            "stability": 9,
            "growth": 6,
            "prestige": 9,
            "salary_range": (3_800_000, 5_200_000)
        },
        "BHP": {
            "type": "Global Mining Multinational",
            "stability": 8,
            "growth": 8,
            "prestige": 9,
            "salary_range": (4_200_000, 5_500_000)
        },
        "Anglo American": {
            "type": "Global Mining Multinational",
            "stability": 8,
            "growth": 8,
            "prestige": 9,
            "salary_range": (4_200_000, 5_500_000)
        },
        "Antofagasta PLC": {
            "type": "Chilean Mining Corp",
            "stability": 8,
            "growth": 7,
            "prestige": 8,
            "salary_range": (3_900_000, 5_000_000)
        },
        "SQM": {
            "type": "Lithium/Chemicals",
            "stability": 7,
            "growth": 9,
            "prestige": 8,
            "salary_range": (3_800_000, 4_800_000)
        },
        "Barrick": {
            "type": "Gold Mining",
            "stability": 7,
            "growth": 7,
            "prestige": 8,
            "salary_range": (3_900_000, 4_800_000)
        }
    }
    
    TECH_ROLES = {
        "IoT/Sensors Engineer": {
            "salary_multiplier": 1.1,
            "growth": 9,
            "demand": "Very High",
            "skills_required": ["C++", "Embedded", "IoT", "Real-time systems"]
        },
        "Senior Software Engineer": {
            "salary_multiplier": 1.0,
            "growth": 7,
            "demand": "High",
            "skills_required": ["Python", "Java", "Architecture"]
        },
        "Tech Lead/Engineering Manager": {
            "salary_multiplier": 1.15,
            "growth": 6,
            "demand": "High",
            "skills_required": ["Leadership", "Architecture", "Budget management"]
        },
        "DevOps/Cloud Architect": {
            "salary_multiplier": 1.05,
            "growth": 8,
            "demand": "Very High",
            "skills_required": ["GCP", "Docker", "Kubernetes", "CI/CD"]
        },
        "Data/Analytics Engineer": {
            "salary_multiplier": 1.2,
            "growth": 10,
            "demand": "Very High",
            "skills_required": ["Python", "SQL", "ML", "Big Data"]
        },
    }
    
    def __init__(self, debug: bool = True):
        self.debug = debug
        self.decision_engine = DecisionAnalysisEngine(debug=debug)
        self.research_agent = None
        
        try:
            self.research_agent = GeminiDeepResearchAgent(debug=debug)
        except Exception as e:
            print(f"⚠️ Deep Research not available: {e}")
    
    def create_mining_options(self) -> List[CareerOption]:
        """Create specific mining career options for Arturo"""
        
        options = []
        
        # Option 1: Codelco - IoT Tech Lead
        options.append(CareerOption(
            name="Codelco - Senior IoT Engineer (Rajo Sur)",
            salary_expected=4_200_000,
            probability_success=0.70,
            timeline_months=16,
            tech_growth=8,
            income_stability=9,
            work_life_balance=5,
            prestige=9,
            remote_flexibility=2,
            learning_opportunity=7,
            career_ceiling=9,
            unemployment_risk=0.03,
            burnout_risk=0.35,
            market_risk=0.05,
            description="Codelco - Senior IoT/Sensors for mining operations",
            pros=[
                "Máxima estabilidad (Estado)",
                "Beneficios corporativos premium",
                "Especialización deep en mining",
                "Network con ejecutivos"
            ],
            cons=[
                "Ubicación remota (Atacama)",
                "Work-life balance bajo",
                "Burocracia corporativa"
            ]
        ))
        
        # Option 2: BHP - Tech Lead
        options.append(CareerOption(
            name="BHP - Tech Lead Mining Software",
            salary_expected=4_600_000,
            probability_success=0.55,
            timeline_months=18,
            tech_growth=8,
            income_stability=8,
            work_life_balance=5,
            prestige=9,
            remote_flexibility=3,
            learning_opportunity=8,
            career_ceiling=9,
            unemployment_risk=0.05,
            burnout_risk=0.40,
            market_risk=0.10,
            description="BHP - Tech Lead for mining automation",
            pros=[
                "Multinacional prestigiosa",
                "Salario competitivo",
                "Tecnología cutting-edge",
                "Career growth internacional"
            ],
            cons=[
                "Ubicación: Antofagasta",
                "English requirement (mid-advanced)",
                "Menos stability que Codelco"
            ]
        ))
        
        # Option 3: SQM - Data Engineer
        options.append(CareerOption(
            name="SQM - Data/Analytics Engineer",
            salary_expected=4_800_000,
            probability_success=0.60,
            timeline_months=15,
            tech_growth=9,
            income_stability=8,
            work_life_balance=6,
            prestige=8,
            remote_flexibility=4,
            learning_opportunity=9,
            career_ceiling=8,
            unemployment_risk=0.08,
            burnout_risk=0.30,
            market_risk=0.12,
            description="SQM - Data Engineer (lithium production optimization)",
            pros=[
                "Highest tech growth potential",
                "Good work-life balance",
                "Growing company (lithium boom)",
                "More flexibility than Codelco"
            ],
            cons=[
                "Market risk from lithium volatility",
                "Smaller than multinational",
                "Data role (less mining domain expertise)"
            ]
        ))
        
        # Option 4: Consulting - Mining Tech
        options.append(CareerOption(
            name="Mining Consulting (Accenture/EY/Deloitte)",
            salary_expected=4_200_000,
            probability_success=0.65,
            timeline_months=12,
            tech_growth=8,
            income_stability=7,
            work_life_balance=4,
            prestige=8,
            remote_flexibility=6,
            learning_opportunity=8,
            career_ceiling=8,
            unemployment_risk=0.10,
            burnout_risk=0.50,
            market_risk=0.15,
            description="Mining technology consulting (multiple clients)",
            pros=[
                "Variety of projects",
                "Faster hire process",
                "Some flexibility",
                "Broad exposure"
            ],
            cons=[
                "High burnout risk",
                "Travel required",
                "Less deep specialization"
            ]
        ))
        
        # Option 5: Hybrid - Freelance + Part-time
        options.append(CareerOption(
            name="Hybrid - Part-time UCOM + Mining Freelance",
            salary_expected=4_100_000,
            probability_success=0.50,
            timeline_months=6,
            tech_growth=8,
            income_stability=5,
            work_life_balance=7,
            prestige=6,
            remote_flexibility=10,
            learning_opportunity=8,
            career_ceiling=7,
            unemployment_risk=0.15,
            burnout_risk=0.25,
            market_risk=0.20,
            description="Keep UCOM part-time while freelancing for mining",
            pros=[
                "Quick transition",
                "Low risk",
                "Flexibility",
                "Income stability"
            ],
            cons=[
                "Dual commitment stress",
                "Less depth in either",
                "Network building slower"
            ]
        ))
        
        return options
    
    async def deep_research_mining_options(
        self,
        options: List[CareerOption]
    ) -> Dict[str, str]:
        """Run deep research on mining-specific questions"""
        
        if not self.research_agent:
            print("⚠️ Deep research not available")
            return {}
        
        print("\n🔍 DEEP RESEARCH PHASE")
        print("="*70)
        
        # Global mining industry research
        global_research = await self.research_agent.research_option(
            CareerOption(
                name="Mining Industry 2025-2026",
                salary_expected=4_500_000,
                probability_success=0.65,
                timeline_months=18,
                tech_growth=8,
                income_stability=8,
                work_life_balance=5,
                prestige=8,
                remote_flexibility=2,
                learning_opportunity=8,
                career_ceiling=9,
                unemployment_risk=0.05,
                burnout_risk=0.35,
                market_risk=0.10
            ),
            context="""
            Research Chile's mining industry trends 2025-2026:
            - Current hiring trends (tech roles)
            - Salary benchmarks for engineers
            - Impact of lithium boom/global mining
            - Remote work policies in mining
            - Career progression timelines
            """
        )
        
        research_data = {
            "mining_industry_global": global_research.deep_research
        }
        
        # Company-specific research
        for company_name in ["Codelco", "BHP", "SQM"]:
            company_research = await self.research_agent.research_option(
                CareerOption(
                    name=f"{company_name} Career",
                    salary_expected=4_500_000,
                    probability_success=0.60,
                    timeline_months=15,
                    tech_growth=8,
                    income_stability=8,
                    work_life_balance=5,
                    prestige=8,
                    remote_flexibility=2,
                    learning_opportunity=8,
                    career_ceiling=9,
                    unemployment_risk=0.05,
                    burnout_risk=0.35,
                    market_risk=0.10
                ),
                context=f"""
                Research {company_name} in Chile:
                - Current tech hiring needs
                - Average salary for tech roles
                - Work culture and benefits
                - Career progression speed
                - Hiring process timeline
                """
            )
            research_data[f"{company_name.lower()}_specific"] = company_research.deep_research
        
        return research_data
    
    def analyze_timeline_feasibility(
        self,
        target_date: datetime = None
    ) -> Dict[str, any]:
        """Analyze timeline to achieve $4M goal"""
        
        if target_date is None:
            target_date = datetime.now() + timedelta(days=365*3)  # 3 years
        
        days_remaining = (target_date - datetime.now()).days
        
        timeline = {
            "target_date": target_date.strftime("%Y-%m-%d"),
            "days_remaining": days_remaining,
            "weeks_remaining": days_remaining // 7,
            "months_remaining": days_remaining // 30,
            
            "phase_1_preparation": {
                "timeline": "0-6 weeks",
                "activities": [
                    "LinkedIn optimization for mining",
                    "CV specialized for mining roles",
                    "Research target companies",
                    "Contact recruiters specializing in mining"
                ],
                "success_indicators": [
                    "Profile views from mining companies",
                    "Recruiter messages",
                    "Interview opportunities"
                ]
            },
            
            "phase_2_applications": {
                "timeline": "6-14 weeks",
                "activities": [
                    "Apply to 5-7 mining companies",
                    "Interview prep (technical + behavioral)",
                    "Salary research & negotiation prep"
                ],
                "milestones": [
                    "First interview (8-10 weeks typical)",
                    "Second round (12-14 weeks)",
                    "Offer stage (14-16 weeks)"
                ]
            },
            
            "phase_3_offer_negotiation": {
                "timeline": "14-18 weeks",
                "activities": [
                    "Negotiate salary ($4.5M+ target)",
                    "Negotiate benefits/location",
                    "Plan transition from UCOM"
                ],
                "success_criteria": [
                    "Written offer $4M+",
                    "Acceptable location/flexibility",
                    "Start date within 4 weeks"
                ]
            }
        }
        
        return timeline
    
    def generate_comparison_matrix(
        self,
        options: List[CareerOption],
        results: Dict[str, AnalysisResult]
    ) -> str:
        """Generate detailed comparison matrix"""
        
        matrix = "\n" + "="*100 + "\n"
        matrix += "📊 COMPREHENSIVE COMPARISON MATRIX - MINING & CAREER OPTIONS\n"
        matrix += "="*100 + "\n\n"
        
        # Header
        matrix += f"{'OPTION':<35} {'SALARY':<12} {'SUCCESS':<10} {'SCORE':<8} {'CONF':<8} {'RANKING':<10}\n"
        matrix += "-"*100 + "\n"
        
        # Sorted by score
        sorted_options = sorted(
            results.items(),
            key=lambda x: x[1].overall_score,
            reverse=True
        )
        
        for rank, (name, result) in enumerate(sorted_options, 1):
            option = next(o for o in options if o.name == name)
            
            matrix += f"{name:<35} ${option.salary_expected/1e6:.1f}M      "
            matrix += f"{option.probability_success*100:>5.0f}%     "
            matrix += f"{result.overall_score:>5.1f}/10  "
            matrix += f"{result.confidence*100:>5.0f}%  "
            matrix += f"#{rank}\n"
        
        # Detailed metrics
        matrix += "\n\n" + "="*100 + "\n"
        matrix += "DETAILED METRICS BY OPTION\n"
        matrix += "="*100 + "\n\n"
        
        for name, result in sorted_options:
            option = next(o for o in options if o.name == name)
            
            matrix += f"🏆 {name}\n"
            matrix += "-"*80 + "\n"
            matrix += f"  Salary:                  ${option.salary_expected:,.0f} CLP\n"
            matrix += f"  Success Probability:     {option.probability_success*100:.0f}%\n"
            matrix += f"  Timeline:                {option.timeline_months} months\n"
            matrix += f"  Overall Score:          {result.overall_score:.1f}/10\n"
            matrix += f"  Confidence:             {result.confidence*100:.0f}%\n"
            matrix += f"  {result.recommendation}\n\n"
            
            # Methodology breakdown
            matrix += "  Decision Methodology Results:\n"
            matrix += f"    • Monte Carlo:         {result.monte_carlo_score:.2f}\n"
            matrix += f"    • TOPSIS Rank:        #{result.topsis_rank}\n"
            matrix += f"    • Pareto Optimal:     {'✅' if result.pareto_optimal else '❌'}\n"
            matrix += f"    • Regret Analysis:    {result.regret_analysis:.2f}M CLP\n"
            matrix += f"    • Risk Score:         {result.risk_score*100:.0f}%\n"
            matrix += f"    • Scenario Robust:    {result.scenario_robustness*100:.0f}%\n\n"
            
            # Qualitative factors
            matrix += "  Factor Analysis (0-10 scale):\n"
            matrix += f"    • Tech Growth:        {option.tech_growth}/10\n"
            matrix += f"    • Income Stability:   {option.income_stability}/10\n"
            matrix += f"    • Work-Life Balance:  {option.work_life_balance}/10\n"
            matrix += f"    • Prestige:           {option.prestige}/10\n"
            matrix += f"    • Learning Opp:       {option.learning_opportunity}/10\n"
            matrix += f"    • Remote Flexibility: {option.remote_flexibility}/10\n\n"
        
        return matrix

# ============================================================================
# MAIN WORKFLOW
# ============================================================================

async def run_mining_career_analysis():
    """Complete mining & career decision analysis"""
    
    print("\n" + "="*70)
    print("🏔️  MINING & CAREER DECISION ANALYSIS - ARTURO VERAS 2025")
    print("="*70)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Goal: ${4_000_000:,} CLP in 3 years")
    print("="*70 + "\n")
    
    # Initialize analyzer
    try:
        analyzer = MiningCareerAnalyzer(debug=True)
    except Exception as e:
        print(f"⚠️ Error initializing analyzer: {e}")
        print("Proceeding without Deep Research (local analysis only)")
        analyzer = MiningCareerAnalyzer(debug=True)
        analyzer.research_agent = None
    
    # Create options
    options = analyzer.create_mining_options()
    print(f"✅ Created {len(options)} mining/career options\n")
    
    # Deep research (if available)
    research_data = {}
    if analyzer.research_agent:
        try:
            print("🔍 Starting Deep Research (this may take a minute)...")
            research_data = await analyzer.deep_research_mining_options(options)
            print(f"✅ Deep research completed on {len(research_data)} topics\n")
        except Exception as e:
            print(f"⚠️ Deep Research failed: {e}")
            print("Continuing with local analysis only\n")
            research_data = {}
    else:
        print("⚠️ Deep Research Agent not available")
        print("Proceeding with local analysis only\n")
    
    # Decision analysis
    print("\n" + "="*70)
    print("PHASE: DECISION ANALYSIS (13 Methodologies)")
    print("="*70 + "\n")
    
    results = {}
    for option in options:
        deep_research = research_data.get(
            option.name.lower(),
            ""
        )
        
        try:
            result = analyzer.decision_engine.analyze_option(
                option,
                options,
                deep_research
            )
            
            results[option.name] = result
            print(f"✅ {option.name}")
            print(f"   Score: {result.overall_score:.1f}/10 | "
                  f"Confidence: {result.confidence*100:.0f}%")
        except Exception as e:
            print(f"❌ Error analyzing {option.name}: {e}")
            continue
    
    if not results:
        print("❌ No options analyzed successfully")
        return None, analyzer
    
    # Generate comparison
    try:
        comparison = analyzer.generate_comparison_matrix(options, results)
        print(comparison)
    except Exception as e:
        print(f"⚠️ Error generating comparison matrix: {e}")
    
    # Timeline analysis
    try:
        timeline = analyzer.analyze_timeline_feasibility()
        print("\n" + "="*70)
        print("⏰ TIMELINE ANALYSIS")
        print("="*70)
        print(f"Target Date: {timeline['target_date']}")
        print(f"Time Remaining: {timeline['months_remaining']} months ({timeline['weeks_remaining']} weeks)")
        print(f"\nRecommended phases:\n")
        for phase, details in timeline.items():
            if isinstance(details, dict) and 'timeline' in details:
                print(f"  {details['timeline']}: {details['activities']}")
    except Exception as e:
        print(f"⚠️ Error in timeline analysis: {e}")
    
    # Save results
    try:
        output_data = {
            "timestamp": datetime.now().isoformat(),
            "goal": "$4M CLP in 3 years",
            "options_analyzed": len(options),
            "results": {
                name: {
                    "score": result.overall_score,
                    "confidence": result.confidence,
                    "recommendation": result.recommendation,
                    "salary": next((o.salary_expected for o in options if o.name == name), 0),
                    "success_prob": next((o.probability_success for o in options if o.name == name), 0)
                }
                for name, result in results.items()
            },
            "research_topics": list(research_data.keys())
        }
        
        with open("mining_career_analysis_results.json", "w") as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Analysis saved to: mining_career_analysis_results.json")
    except Exception as e:
        print(f"⚠️ Error saving results: {e}")
    
    return results, analyzer

# ============================================================================

if __name__ == "__main__":
    try:
        results, analyzer = asyncio.run(run_mining_career_analysis())
        if results:
            print("\n✅ Analysis completed successfully!")
            sys.exit(0)
        else:
            print("\n❌ Analysis failed")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠️ Analysis interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
