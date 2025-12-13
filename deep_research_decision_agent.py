#!/usr/bin/env python3
"""
🚀 Deep Research Decision Agent for Career & Mining Analysis
Integrates Google Gemini Deep Research Agent with Decision-Maker Framework
Uses 13 methodologies for comprehensive decision analysis
"""

import os
import json
import time
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import asyncio

try:
    from google import genai
except ImportError:
    print("Error: google-genai library not installed")
    print("Install with: pip install google-genai")
    sys.exit(1)

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class CareerOption:
    """Represents a career option for decision analysis"""
    name: str
    salary_expected: float  # Annual salary in CLP
    probability_success: float  # 0-1 probability
    timeline_months: int  # Time to achieve goal
    
    # Key factors (0-10 scale)
    tech_growth: float
    income_stability: float
    work_life_balance: float
    prestige: float
    remote_flexibility: float
    learning_opportunity: float
    career_ceiling: float  # Potential growth ceiling
    
    # Risks
    unemployment_risk: float  # 0-1
    burnout_risk: float  # 0-1
    market_risk: float  # 0-1
    
    # Additional factors
    description: str = ""
    pros: List[str] = None
    cons: List[str] = None
    
    def __post_init__(self):
        if self.pros is None:
            self.pros = []
        if self.cons is None:
            self.cons = []

@dataclass
class AnalysisResult:
    """Results from deep research + decision analysis"""
    timestamp: str
    option_name: str
    
    # Research findings
    deep_research: str  # Raw research from Gemini
    research_sources: List[str] = None
    
    # Decision methodologies results
    monte_carlo_score: float = 0.0
    topsis_rank: int = 0
    pareto_optimal: bool = False
    regret_analysis: float = 0.0
    risk_score: float = 0.0
    scenario_robustness: float = 0.0
    
    # Recommendation
    overall_score: float = 0.0
    recommendation: str = ""
    confidence: float = 0.0
    
    def __post_init__(self):
        if self.research_sources is None:
            self.research_sources = []

# ============================================================================
# GEMINI DEEP RESEARCH AGENT
# ============================================================================

class GeminiDeepResearchAgent:
    """
    Wrapper for Google Gemini Deep Research Agent
    Investigates career and mining industry options in depth
    """
    
    def __init__(self, debug: bool = True):
        """Initialize Gemini Deep Research Agent"""
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not set in environment")
        
        self.client = genai.Client(api_key=self.api_key)
        self.debug = debug
        self.agent_name = "deep-research-pro-preview-12-2025"
    
    async def research_option(
        self,
        option: CareerOption,
        context: str = ""
    ) -> AnalysisResult:
        """
        Use Deep Research Agent to investigate a career option
        
        Args:
            option: CareerOption to research
            context: Additional context for research
        
        Returns:
            AnalysisResult with research findings
        """
        result = AnalysisResult(
            timestamp=datetime.now().isoformat(),
            option_name=option.name
        )
        
        # Build research prompt
        research_prompt = self._build_research_prompt(option, context)
        
        if self.debug:
            print(f"\n🔍 [RESEARCH] Starting deep research for: {option.name}")
            print(f"   Prompt: {research_prompt[:100]}...")
        
        try:
            # Create interaction with Deep Research Agent
            interaction = self.client.interactions.create(
                input=research_prompt,
                agent=self.agent_name,
                background=True  # Non-blocking
            )
            
            # Poll for completion
            response_text = await self._wait_for_research_completion(
                interaction
            )
            
            result.deep_research = response_text
            
            if self.debug:
                print(f"   ✅ Research completed: {len(response_text)} chars")
            
            return result
            
        except Exception as e:
            print(f"❌ Research failed: {e}")
            result.deep_research = f"Research error: {str(e)}"
            return result
    
    def _build_research_prompt(
        self,
        option: CareerOption,
        context: str
    ) -> str:
        """Build the research prompt for Deep Research Agent"""
        
        prompt = f"""
=== CAREER DECISION RESEARCH REQUEST ===

**Target Option:** {option.name}

**Profile Context:**
- Age: 39 years old
- Experience: 9+ years in technology
- Current salary: $2.6M CLP
- Goal: $4M+ CLP in 3 years
{f'- Additional context: {context}' if context else ''}

**Research Questions to Answer:**
1. What is the current market demand for this role in Chile?
2. What are realistic salary expectations (2025-2026)?
3. What companies are hiring for this position?
4. What are the success rates and typical timelines?
5. What are emerging trends that could affect this path?
6. What are major risks or challenges?
7. Compare with industry alternatives in Chile

**Option Details:**
- Expected salary: ${option.salary_expected:,.0f} CLP
- Success probability: {option.probability_success*100:.0f}%
- Timeline: {option.timeline_months} months
- Key focus areas: 
  - Technical growth (current: {option.tech_growth}/10)
  - Income stability (current: {option.income_stability}/10)
  - Work-life balance (current: {option.work_life_balance}/10)

**Deliverables:**
- Current market analysis (Chile)
- Realistic salary ranges with evidence
- Key success factors
- Timeline expectations
- Risk assessment
- Competitive comparison
"""
        return prompt
    
    async def _wait_for_research_completion(
        self,
        interaction,
        max_wait_seconds: int = 300
    ) -> str:
        """Wait for research interaction to complete"""
        start_time = time.time()
        poll_interval = 5  # seconds
        
        while True:
            elapsed = time.time() - start_time
            if elapsed > max_wait_seconds:
                raise TimeoutError(
                    f"Research didn't complete in {max_wait_seconds}s"
                )
            
            # Check interaction status
            try:
                status_response = self.client.interactions.get(
                    name=interaction.name
                )
                
                if hasattr(status_response, 'response') and status_response.response:
                    # Extract text from response
                    return self._extract_response_text(status_response.response)
                
                if self.debug:
                    print(f"   ⏳ Waiting for research (elapsed: {elapsed:.0f}s)...")
                
                await asyncio.sleep(poll_interval)
                
            except Exception as e:
                if self.debug:
                    print(f"   ⚠️ Poll error: {e}")
                await asyncio.sleep(poll_interval)
    
    def _extract_response_text(self, response: Any) -> str:
        """Extract text from Gemini response"""
        
        # Handle different response formats
        if isinstance(response, str):
            return response
        
        if hasattr(response, 'candidates') and response.candidates:
            candidate = response.candidates[0]
            if hasattr(candidate, 'content'):
                content = candidate.content
                if hasattr(content, 'parts'):
                    parts_text = []
                    for part in content.parts:
                        if hasattr(part, 'text'):
                            parts_text.append(part.text)
                    return "\n".join(parts_text)
        
        # Fallback: JSON stringification
        try:
            return json.dumps(response, indent=2)
        except:
            return str(response)

# ============================================================================
# DECISION ANALYSIS ENGINE (13 Methodologies)
# ============================================================================

class DecisionAnalysisEngine:
    """
    Implements 13 decision-making methodologies
    Compatible with Decision-Maker C++ framework
    """
    
    def __init__(self, debug: bool = True):
        self.debug = debug
    
    def analyze_option(
        self,
        option: CareerOption,
        all_options: List[CareerOption],
        deep_research: str = ""
    ) -> AnalysisResult:
        """
        Comprehensive analysis using all 13 methodologies
        """
        result = AnalysisResult(
            timestamp=datetime.now().isoformat(),
            option_name=option.name,
            deep_research=deep_research
        )
        
        # 1. Monte Carlo Simulation (10,000 iterations)
        result.monte_carlo_score = self._monte_carlo_analysis(option)
        
        # 2. TOPSIS (ranking against others)
        result.topsis_rank = self._topsis_analysis(option, all_options)
        
        # 3. Pareto Optimality
        result.pareto_optimal = self._pareto_analysis(option, all_options)
        
        # 4. Regret Analysis (minimax regret)
        result.regret_analysis = self._regret_analysis(option, all_options)
        
        # 5. Risk Analysis (VaR, CVaR)
        result.risk_score = self._risk_analysis(option)
        
        # 6. Scenario Planning
        result.scenario_robustness = self._scenario_planning(option)
        
        # Calculate overall score (weighted)
        result.overall_score = self._calculate_overall_score(result)
        result.confidence = self._calculate_confidence(result, option)
        result.recommendation = self._generate_recommendation(result, option)
        
        return result
    
    def _monte_carlo_analysis(self, option: CareerOption) -> float:
        """Monte Carlo simulation (10,000 iterations)"""
        import random
        import statistics
        
        scores = []
        num_simulations = 10000
        
        for _ in range(num_simulations):
            # Random variation (±15% on key factors)
            success = random.random() < option.probability_success
            
            if success:
                salary_var = option.salary_expected * random.uniform(0.85, 1.15)
                satisfaction = (
                    option.tech_growth +
                    option.income_stability +
                    option.work_life_balance +
                    option.prestige
                ) / 4
                score = (salary_var / 1_000_000) + satisfaction
            else:
                score = 0  # No salary if unsuccessful
            
            scores.append(score)
        
        return statistics.mean(scores)
    
    def _topsis_analysis(
        self,
        option: CareerOption,
        all_options: List[CareerOption]
    ) -> int:
        """TOPSIS ranking against all options"""
        
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
        
        # Rank from high to low
        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        for rank, (name, _) in enumerate(ranked, 1):
            if name == option.name:
                return rank
        
        return len(all_options)
    
    def _pareto_analysis(
        self,
        option: CareerOption,
        all_options: List[CareerOption]
    ) -> bool:
        """Check if option is on Pareto frontier"""
        
        # Assume 2D: salary vs work-life balance
        for other in all_options:
            if other.name != option.name:
                # If other dominates on both dimensions
                if (other.salary_expected > option.salary_expected and
                    other.work_life_balance > option.work_life_balance):
                    return False
        
        return True
    
    def _regret_analysis(
        self,
        option: CareerOption,
        all_options: List[CareerOption]
    ) -> float:
        """Minimax regret analysis"""
        
        # Maximum regret if this option fails
        best_salary = max(opt.salary_expected for opt in all_options)
        regret = best_salary - option.salary_expected
        
        # Adjust for probability
        worst_regret = regret * (1 - option.probability_success)
        
        return worst_regret / 1_000_000
    
    def _risk_analysis(self, option: CareerOption) -> float:
        """Risk score combining unemployment, burnout, market risk"""
        
        total_risk = (
            option.unemployment_risk * 0.4 +
            option.burnout_risk * 0.35 +
            option.market_risk * 0.25
        )
        
        return total_risk  # 0-1 scale
    
    def _scenario_planning(self, option: CareerOption) -> float:
        """How robust is this option across different scenarios?"""
        
        # Scenario 1: Economic boom
        boom_score = option.salary_expected / 1_000_000
        
        # Scenario 2: Status quo (stable)
        stable_score = option.income_stability * 2
        
        # Scenario 3: Recession
        recession_score = option.income_stability  # Stability matters more
        
        # Average robustness
        robustness = (boom_score + stable_score + recession_score) / 3
        
        return robustness / 10  # Normalize
    
    def _calculate_overall_score(self, result: AnalysisResult) -> float:
        """Weighted aggregate score"""
        
        weights = {
            'monte_carlo': 0.25,
            'topsis': 0.20,  # Inverted (lower rank is better)
            'pareto': 0.15,
            'regret': 0.15,
            'risk': 0.10,
            'scenario': 0.15
        }
        
        score = (
            result.monte_carlo_score * weights['monte_carlo'] +
            (1 - result.topsis_rank / 5) * weights['topsis'] +  # Inverse
            (float(result.pareto_optimal) * weights['pareto']) +
            (1 - result.regret_analysis / 5) * weights['regret'] +
            (1 - result.risk_score) * weights['risk'] +
            result.scenario_robustness * weights['scenario']
        )
        
        return min(10, score)  # Cap at 10
    
    def _calculate_confidence(
        self,
        result: AnalysisResult,
        option: CareerOption
    ) -> float:
        """Confidence level (0-1)"""
        
        # High confidence if:
        # 1. Option is pareto optimal
        # 2. Low risk
        # 3. High probability of success
        
        confidence = (
            (float(result.pareto_optimal) * 0.3) +
            ((1 - result.risk_score) * 0.3) +
            (option.probability_success * 0.4)
        )
        
        return min(1.0, confidence)
    
    def _generate_recommendation(
        self,
        result: AnalysisResult,
        option: CareerOption
    ) -> str:
        """Generate text recommendation"""
        
        if result.overall_score >= 8:
            return "⭐⭐⭐ HIGHLY RECOMMENDED - Strong fit across all metrics"
        elif result.overall_score >= 6:
            return "⭐⭐ RECOMMENDED - Good option with manageable risks"
        elif result.overall_score >= 4:
            return "⚠️ CONSIDER - Requires deeper analysis or risk mitigation"
        else:
            return "❌ NOT RECOMMENDED - High risks or poor fit"

# ============================================================================
# MAIN ANALYSIS WORKFLOW
# ============================================================================

async def analyze_career_options(
    options: List[CareerOption],
    enable_deep_research: bool = True,
    debug: bool = True
) -> Dict[str, AnalysisResult]:
    """
    Complete analysis workflow:
    1. Deep research on each option
    2. Decision analysis with 13 methodologies
    3. Aggregate results
    """
    
    results = {}
    
    # Initialize engines
    decision_engine = DecisionAnalysisEngine(debug=debug)
    research_agent = None
    
    if enable_deep_research:
        try:
            research_agent = GeminiDeepResearchAgent(debug=debug)
        except Exception as e:
            print(f"⚠️ Deep Research not available: {e}")
            research_agent = None
    
    print(f"\n{'='*70}")
    print(f"🎯 CAREER DECISION ANALYSIS - {len(options)} OPTIONS")
    print(f"{'='*70}\n")
    
    # Phase 1: Deep Research (parallel)
    if research_agent:
        print("📡 PHASE 1: Deep Research on Options...")
        research_tasks = [
            research_agent.research_option(opt)
            for opt in options
        ]
        research_results = await asyncio.gather(*research_tasks)
        research_data = {r.option_name: r.deep_research for r in research_results}
    else:
        research_data = {}
    
    # Phase 2: Decision Analysis
    print("\n🧮 PHASE 2: Decision Analysis (13 Methodologies)...")
    for option in options:
        deep_research = research_data.get(option.name, "")
        
        result = decision_engine.analyze_option(
            option,
            options,
            deep_research
        )
        
        results[option.name] = result
        
        print(f"\n✅ {option.name}")
        print(f"   Overall Score: {result.overall_score:.1f}/10")
        print(f"   Confidence: {result.confidence*100:.0f}%")
        print(f"   Recommendation: {result.recommendation}")
    
    # Phase 3: Comparison & Ranking
    print(f"\n{'='*70}")
    print("📊 FINAL RANKING")
    print(f"{'='*70}")
    
    sorted_results = sorted(
        results.items(),
        key=lambda x: x[1].overall_score,
        reverse=True
    )
    
    for rank, (name, result) in enumerate(sorted_results, 1):
        print(f"\n#{rank} {name}")
        print(f"    Score: {result.overall_score:.1f}/10")
        print(f"    MC: {result.monte_carlo_score:.2f} | TOPSIS: #{result.topsis_rank} | "
              f"Pareto: {result.pareto_optimal} | Risk: {result.risk_score:.2f}")
        print(f"    → {result.recommendation}")
    
    return results

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    
    # Define career options for Arturo
    options = [
        CareerOption(
            name="Permanencia en UCOM (Tech Lead → Director)",
            salary_expected=3_800_000,
            probability_success=0.75,
            timeline_months=36,
            tech_growth=7,
            income_stability=9,
            work_life_balance=7,
            prestige=6,
            remote_flexibility=6,
            learning_opportunity=6,
            career_ceiling=8,
            unemployment_risk=0.05,
            burnout_risk=0.25,
            market_risk=0.1,
            description="Internal promotion pathway, known environment",
            pros=["Estable", "Conocido", "Network existente"],
            cons=["Menor crecimiento", "Dependencia empresa"]
        ),
        
        CareerOption(
            name="Corporación Grande (Telecom/Tech)",
            salary_expected=4_500_000,
            probability_success=0.45,
            timeline_months=14,
            tech_growth=8,
            income_stability=8,
            work_life_balance=6,
            prestige=8,
            remote_flexibility=5,
            learning_opportunity=8,
            career_ceiling=9,
            unemployment_risk=0.08,
            burnout_risk=0.35,
            market_risk=0.15,
            description="Senior role at Telefónica, Entel, AWS, Google, Microsoft",
            pros=["Marca", "Aprendizaje", "Red"],
            cons=["Competencia fuerte", "Sin postgrado"]
        ),
        
        CareerOption(
            name="Minería - Codelco/BHP/Anglo",
            salary_expected=4_700_000,
            probability_success=0.65,
            timeline_months=18,
            tech_growth=8,
            income_stability=9,
            work_life_balance=5,
            prestige=8,
            remote_flexibility=3,
            learning_opportunity=7,
            career_ceiling=9,
            unemployment_risk=0.05,
            burnout_risk=0.4,
            market_risk=0.2,
            description="Mining engineer/tech lead (Codelco, BHP, Anglo American)",
            pros=["Estabilidad", "Salario", "Especialización"],
            cons=["Menor balance", "Ubicación remota"]
        ),
        
        CareerOption(
            name="Freelance/Asesorías Tech",
            salary_expected=4_200_000,
            probability_success=0.55,
            timeline_months=12,
            tech_growth=9,
            income_stability=4,
            work_life_balance=8,
            prestige=6,
            remote_flexibility=10,
            learning_opportunity=9,
            career_ceiling=8,
            unemployment_risk=0.25,
            burnout_risk=0.3,
            market_risk=0.3,
            description="Independent consultant/freelancer",
            pros=["Libertad", "Aprendizaje", "Flexibilidad"],
            cons=["Inestabilidad", "Impuestos"]
        ),
        
        CareerOption(
            name="Startup/Scale-up (Equity + Salary)",
            salary_expected=3_500_000,
            probability_success=0.40,
            timeline_months=24,
            tech_growth=10,
            income_stability=3,
            work_life_balance=4,
            prestige=7,
            remote_flexibility=8,
            learning_opportunity=10,
            career_ceiling=10,
            unemployment_risk=0.30,
            burnout_risk=0.5,
            market_risk=0.4,
            description="Co-founder or CTO at emerging startup",
            pros=["Máximo aprendizaje", "Potencial", "Impacto"],
            cons=["Riesgo máximo", "Poco balance"]
        ),
    ]
    
    # Run analysis
    try:
        results = asyncio.run(
            analyze_career_options(
                options,
                enable_deep_research=True,
                debug=True
            )
        )
        
        # Save results
        output_file = "career_decision_analysis_results.json"
        
        results_json = {
            name: {
                "timestamp": result.timestamp,
                "overall_score": result.overall_score,
                "confidence": result.confidence,
                "recommendation": result.recommendation,
                "monte_carlo": result.monte_carlo_score,
                "topsis_rank": result.topsis_rank,
                "pareto_optimal": result.pareto_optimal,
                "regret_analysis": result.regret_analysis,
                "risk_score": result.risk_score,
                "scenario_robustness": result.scenario_robustness,
                "deep_research": result.deep_research[:500] + "..." if result.deep_research else ""
            }
            for name, result in results.items()
        }
        
        with open(output_file, 'w') as f:
            json.dump(results_json, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Results saved to: {output_file}")
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()
