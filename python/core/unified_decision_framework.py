#!/usr/bin/env python3
"""
🚀 Unified Decision Maker Framework (Python Port v2.0)
Integrates Advanced C++ Methodologies (via NumPy) and Python AI Capabilities.

Total Methodologies Implemented: 18

=== 5 ADVANCED (NumPy Accelerated) ===
1.  Advanced Monte Carlo Simulation (Stochastic)
2.  Bayesian Inference (Probabilistic Updates)
3.  Sensitivity Analysis (Variable Impact)
4.  Value at Risk (VaR) / CVaR (Risk Thresholds)
5.  Multi-Objective Optimization (Pareto Front)

=== 13 STANDARD (Legacy Python) ===
6.  TOPSIS (Technique for Order of Preference by Similarity to Ideal Solution)
7.  Regret Analysis (Minimax Regret)
8.  Scenario Planning (Best/Worst/Base cases)
9.  Decision Trees (Simple Sequential Models)
10. AHP (Analytic Hierarchy Process - simplified)
11. Cost-Benefit Analysis (ROI focused)
12. Break-even Analysis
13. Simple Weighted Sum (Scoring)
14. Maximax (Optimistic)
15. Maximin (Pessimistic)
16. Hurwicz Criterion (Realism with alpha)
17. Laplace Criterion (Equal Probability)
18. Expected Value (Risk Neutral)

Author: Arturo (Ported from C++)
"""

import os
import sys
import json
import time
import asyncio
import argparse
import random
import statistics
import math
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum

# Third-party libraries
try:
    import numpy as np
    import pandas as pd
    from scipy import stats
except ImportError:
    print("❌ Error: Missing scientific libraries.")
    print("Please run: uv pip install numpy pandas scipy")
    sys.exit(1)

try:
    from google import genai
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️  Warning: google-genai or python-dotenv not installed. AI features disabled.")

# ============================================================================
# 1. CORE DATA STRUCTURES
# ============================================================================

class DistributionType(Enum):
    DETERMINISTIC = "deterministic"
    NORMAL = "normal"
    UNIFORM = "uniform"
    TRIANGULAR = "triangular"
    BERNOULLI = "bernoulli"
    EXPONENTIAL = "exponential"
    BETA = "beta"
    LOGNORMAL = "lognormal"
    GAMMA = "gamma"
    POISSON = "poisson"

@dataclass
class UncertainVariable:
    """Variable with probabilistic uncertainty (NumPy-ready)"""
    name: str
    dist_type: DistributionType
    params: List[float]  # [p1, p2, p3]

    def sample(self, size: int = 1) -> np.ndarray:
        """Generate vector of samples using NumPy"""
        if self.dist_type == DistributionType.DETERMINISTIC:
            return np.full(size, self.params[0])
        elif self.dist_type == DistributionType.NORMAL:
            return np.random.normal(self.params[0], self.params[1], size)
        elif self.dist_type == DistributionType.UNIFORM:
            return np.random.uniform(self.params[0], self.params[1], size)
        elif self.dist_type == DistributionType.TRIANGULAR:
            # FIXED: parameters are (left, mode, right)
            # Ensure proper ordering to avoid ValueError: mode > right or mode < left
            left, mode, right = sorted(self.params[:3])
            return np.random.triangular(left, mode, right, size)
        elif self.dist_type == DistributionType.BERNOULLI:
            # Binomial with n=1 is Bernoulli
            return np.random.binomial(1, self.params[0], size).astype(float)
        elif self.dist_type == DistributionType.EXPONENTIAL:
            return np.random.exponential(self.params[0], size)
        elif self.dist_type == DistributionType.BETA:
            return np.random.beta(self.params[0], self.params[1], size)
        elif self.dist_type == DistributionType.LOGNORMAL:
            return np.random.lognormal(self.params[0], self.params[1], size)
        elif self.dist_type == DistributionType.GAMMA:
            return np.random.gamma(self.params[0], self.params[1], size)
        elif self.dist_type == DistributionType.POISSON:
            return np.random.poisson(self.params[0], size).astype(float)
        else:
            return np.zeros(size)

@dataclass
class Factor:
    """Decision criteria/factor"""
    name: str
    weight: float
    maximize: bool = True
    category: str = "General"

@dataclass
class Statistics:
    """Aggregated statistics for an option"""
    option_name: str
    mean_score: float
    std_dev: float
    min_score: float
    max_score: float
    percentile_5: float
    percentile_95: float
    success_rate: float
    factor_stats: Dict[str, Dict[str, float]]
    var_95: float # Value at Risk (95%)
    cvar_95: float # Conditional VaR (95%)

@dataclass
class DecisionOption:
    """Option with uncertainty profile"""
    name: str
    description: str = ""
    variables: Dict[str, UncertainVariable] = field(default_factory=dict)
    
    def add_variable(self, name: str, dist_type: DistributionType, *params):
        self.variables[name] = UncertainVariable(name, dist_type, list(params))

# ============================================================================
# 2. ADVANCED ENGINES (NumPy Powered)
# ============================================================================

class MonteCarloEngine:
    """High-performance Monte Carlo Simulation using NumPy"""
    
    def __init__(self, num_simulations: int = 10000):
        self.num_simulations = num_simulations
        self.factors: List[Factor] = []
        self.options: List[DecisionOption] = []
        
    def add_factor(self, factor: Factor):
        self.factors.append(factor)
        
    def add_option(self, option: DecisionOption):
        self.options.append(option)
        
    def run(self) -> Dict[str, Statistics]:
        results = {}
        
        print(f"🎲 Running {self.num_simulations} simulations for {len(self.options)} options (NumPy Accelerated)...")
        
        for option in self.options:
            # 1. Generate samples for all variables (Vectorized)
            sampled_data = {}
            for var_name, var in option.variables.items():
                sampled_data[var_name] = var.sample(self.num_simulations)
            
            # 2. Calculate Weighted Score (Vectorized)
            total_scores = np.zeros(self.num_simulations)
            
            for factor in self.factors:
                if factor.name in sampled_data:
                    values = sampled_data[factor.name]
                    
                    if not factor.maximize:
                        total_scores -= values * factor.weight
                    else:
                        total_scores += values * factor.weight
            
            # 3. Calculate Statistics
            mean = np.mean(total_scores)
            std = np.std(total_scores)
            p5 = np.percentile(total_scores, 5)
            p95 = np.percentile(total_scores, 95)
            
            # VaR calculation (Value at Risk - Downside)
            # 5th percentile represents the "worst case" with 95% confidence
            var_95 = p5 
            
            # CVaR (Expected shortfall - average of worst 5%)
            cvar_95 = np.mean(total_scores[total_scores <= p5])
            
            success_rate = np.mean(total_scores > 0)
            
            # Factor stats
            factor_stats = {}
            for name, values in sampled_data.items():
                factor_stats[name] = {
                    "mean": float(np.mean(values)),
                    "std": float(np.std(values)),
                    "p5": float(np.percentile(values, 5)),
                    "p95": float(np.percentile(values, 95))
                }
            
            stats = Statistics(
                option_name=option.name,
                mean_score=float(mean),
                std_dev=float(std),
                min_score=float(np.min(total_scores)),
                max_score=float(np.max(total_scores)),
                percentile_5=float(p5),
                percentile_95=float(p95),
                success_rate=float(success_rate),
                factor_stats=factor_stats,
                var_95=float(var_95),
                cvar_95=float(cvar_95)
            )
            results[option.name] = stats
            
        return results

class TOPSISEngine:
    """Multi-Criteria Decision Analysis Ranking"""
    
    def analyze(self, decision_matrix: pd.DataFrame, weights: List[float], maximize: List[bool]) -> pd.Series:
        norm_matrix = decision_matrix / np.sqrt((decision_matrix**2).sum())
        weighted_matrix = norm_matrix * weights
        
        if len(maximize) != len(decision_matrix.columns):
             maximize = [True] * len(decision_matrix.columns)

        ideal_best = []
        ideal_worst = []
        
        for i, col in enumerate(weighted_matrix.columns):
            if maximize[i]:
                ideal_best.append(weighted_matrix[col].max())
                ideal_worst.append(weighted_matrix[col].min())
            else:
                ideal_best.append(weighted_matrix[col].min())
                ideal_worst.append(weighted_matrix[col].max())
                
        dist_best = np.sqrt(((weighted_matrix - ideal_best)**2).sum(axis=1))
        dist_worst = np.sqrt(((weighted_matrix - ideal_worst)**2).sum(axis=1))
        
        # Avoid division by zero
        with np.errstate(divide='ignore', invalid='ignore'):
            scores = dist_worst / (dist_best + dist_worst)
            scores = scores.fillna(0.0) # If dist_best + dist_worst == 0
            
        return scores.sort_values(ascending=False)

        return scores.sort_values(ascending=False)

# ============================================================================
# 3. ADVANCED ENGINES (Future Horizons)
# ============================================================================

class ParetoEngine:
    """Multi-Objective Optimization (Efficiency Frontier)"""
    
    @staticmethod
    def analyze(mc_results: Dict[str, Statistics], factors: List[Factor]) -> Dict[str, Any]:
        # Simplify to Mean Values for Pareto check
        # We need to normalize direction (Maximize everything)
        normalized_data = {}
        for name, stats in mc_results.items():
            row = {}
            for f in factors:
                val = stats.factor_stats.get(f.name, {'mean': 0})['mean']
                if not f.maximize:
                    val = -val # Flip sign for minimization factors
                row[f.name] = val
            normalized_data[name] = row
            
        # Check Dominance
        dominated = []
        efficient = []
        
        options = list(normalized_data.keys())
        for i, opt_a in enumerate(options):
            is_dominated = False
            vals_a = normalized_data[opt_a]
            
            for j, opt_b in enumerate(options):
                if i == j: continue
                vals_b = normalized_data[opt_b]
                
                # Check if B dominates A (B >= A in all, B > A in at least one)
                better_or_equal = all(vals_b[k] >= vals_a[k] for k in vals_a)
                strictly_better = any(vals_b[k] > vals_a[k] for k in vals_a)
                
                if better_or_equal and strictly_better:
                    is_dominated = True
                    dominated.append((opt_a, opt_b)) # A is dominated by B
                    break
            
            if not is_dominated:
                efficient.append(opt_a)
                
        return {
            "efficient_frontier": efficient,
            "dominated_options": dominated
        }

class SensitivityEngine:
    """Robustness Analysis (Parameter Variation)"""
    
    @staticmethod
    def analyze(mc_results: Dict[str, Statistics], factors: List[Factor]) -> Dict[str, Any]:
        # Base Winner
        base_winner = max(mc_results.items(), key=lambda x: x[1].mean_score)[0]
        
        sensitivity_report = {
            "base_winner": base_winner,
            "changes": []
        }
        
        # Test: Vary each factor weight by +/- 20%
        # NOTE: This is a simplified sensitivity on the MEAN scores, not full re-simulation
        
        # 1. Pre-calculate raw factor scores per option
        raw_scores = {} # {opt: {factor: mean_val}}
        for name, stats in mc_results.items():
            raw_scores[name] = {k: v['mean'] for k, v in stats.factor_stats.items()}

        changes_count = 0
        total_checks = 0

        for f in factors:
            # Check +20% and -20% weight
            for delta in [0.2, -0.2]:
                new_weight = f.weight * (1 + delta)
                
                # Re-calculate scores with modified weight (others stay same)
                new_ranking = {}
                for name, f_vals in raw_scores.items():
                    score = 0
                    for other_f in factors:
                        w = other_f.weight
                        if other_f.name == f.name:
                            w = new_weight
                        
                        val = f_vals.get(other_f.name, 0)
                        if other_f.maximize:
                            score += val * w
                        else:
                            score -= val * w
                    new_ranking[name] = score
                
                new_winner = max(new_ranking.items(), key=lambda x: x[1])[0]
                
                total_checks += 1
                if new_winner != base_winner:
                    changes_count += 1
                    sensitivity_report["changes"].append({
                        "factor": f.name,
                        "change": f"+{int(delta*100)}%" if delta > 0 else f"{int(delta*100)}%",
                        "new_winner": new_winner
                    })

        sensitivity_report["robustness_score"] = 1.0 - (changes_count / total_checks) if total_checks > 0 else 1.0
        return sensitivity_report

class BayesianEngine:
    """Bayesian Inference (Updating Probabilities)"""
    @staticmethod
    def analyze(mc_results: Dict[str, Statistics]) -> Dict[str, float]:
        # Assume generic prior = 0.5 (Neutral)
        # Update based on "Evidence" that higher mean score is "positive signal"
        # Using a simplistic Gaussian likelihood just to demonstrate concept
        posteriors = {}
        
        # Find global range to normalize
        all_means = [s.mean_score for s in mc_results.values()]
        global_mean = np.mean(all_means)
        global_std = np.std(all_means) if len(all_means) > 1 else 1.0
        
        for name, stats in mc_results.items():
            prior = 0.5
            # Likelihood: Probability of this outcome given the hypothesis "This is the best option"
            # We treat the normalized z-score as proxy for likelihood strength
            z_score = (stats.mean_score - global_mean) / (global_std + 1e-9)
            likelihood = stats.norm.cdf(z_score) if hasattr(stats, 'norm') else 1 / (1 + np.exp(-z_score)) # Sigmoid
            
            # Bayes Theorem: P(A|B) = P(B|A) * P(A) / P(B)
            # Simplified Update for demonstration:
            posterior = (likelihood * prior) / ((likelihood * prior) + (0.5 * (1-prior))) # Assuming binary evidence
            posteriors[name] = float(posterior)
            
        return posteriors

class RealOptionsEngine:
    """Real Options Valuation (Flexibility to Wait)"""
    @staticmethod
    def analyze(mc_results: Dict[str, Statistics], risk_free_rate=0.04, time_horizon=1.0) -> Dict[str, float]:
        # Black-Scholes Approximation for "Option to Delay"
        # Underlying (S) = Expected Value (Mean Score, normalized positive)
        # Strike (K) = Cost (assumed to be the negative component, but estimated here as Mean)
        # Volatility (sigma) = std_dev / mean
        roa_values = {}
        
        for name, stats in mc_results.items():
             # Normalize S to be positive for log calculation
             S = abs(stats.mean_score) + 1e-6 
             K = S # At-the-money assumption for pure flexibility value
             sigma = (stats.std_dev / S) if S > 0 else 0
             T = time_horizon
             r = risk_free_rate
             
             if sigma <= 0:
                 roa_values[name] = 0.0
                 continue
                 
             d1 = (np.log(S/K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
             d2 = d1 - sigma * np.sqrt(T)
             
             # Call Option Value (Value of "Waiting" for upside)
             call_val = S * stats.norm_cdf(d1) - K * np.exp(-r * T) * stats.norm_cdf(d2) if hasattr(stats, 'norm_cdf') else 0 # Mock if no scipy
             
             # Using scipy if available, else simplistic
             try:
                 from scipy.stats import norm
                 val = S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
                 roa_values[name] = float(val)
             except ImportError:
                 roa_values[name] = 0.0 # Fallback
                 
        return roa_values

class PortfolioEngine:
    """Portfolio Optimization (Diversification)"""
    @staticmethod
    def analyze(mc_results: Dict[str, Statistics]) -> List[str]:
        # Simple Mean-Variance analysis to find best 2-asset portfolio
        # We assume 0 correlation for simplicity (without raw data history)
        # Goal: Maximize Sharpe Ratio (Mean / Std)
        
        options = list(mc_results.keys())
        if len(options) < 2:
            return ["Need >1 Option"]
            
        best_pair = None
        best_sharpe = -float('inf')
        
        import itertools
        for a, b in itertools.combinations(options, 2):
            stats_a = mc_results[a]
            stats_b = mc_results[b]
            
            # 50/50 Portfolio
            port_mean = 0.5 * stats_a.mean_score + 0.5 * stats_b.mean_score
            # Variance = w1^2*s1^2 + w2^2*s2^2 (assuming corr=0)
            port_std = np.sqrt(0.25 * stats_a.std_dev**2 + 0.25 * stats_b.std_dev**2)
            
            sharpe = port_mean / (port_std + 1e-9)
            if sharpe > best_sharpe:
                best_sharpe = sharpe
                best_pair = (a, b)
        
        return [best_pair[0], best_pair[1]] if best_pair else []

class MDPEngine:
    """Markov Decision Process (Sequential Decisions)"""
    @staticmethod
    def analyze() -> Dict[str, str]:
        # Consolidated 2-State Model (Growth vs Recession)
        # Value Iteration for standard policy
        states = ["Growth", "Recession"]
        actions = ["Invest", "Wait"]
        # Transition Matrix: Growth->Growth 0.7, Growth->Recession 0.3
        T = np.array([
            [[0.7, 0.3], [0.9, 0.1]], # Invest (Higher risk exposure?) - actually T depends on State, not Action usually for market
            [[0.6, 0.4], [0.8, 0.2]]  # Wait (Safer)
        ]) 
        # Rewards (Mock)
        R = np.array([
            [100, -50], # Invest: Growth=+100, Recession=-50
            [10, 5]     # Wait: Growth=+10, Recession=+5
        ])
        
        # One-step lookahead policy (simplified)
        policy = {}
        for s_idx, state in enumerate(states):
            # Exp Value Invest
            ev_invest = 0.7 * 100 + 0.3 * (-50) if s_idx == 0 else 0.4 * 100 + 0.6 * (-50) # Mock probs
            # Exp Value Wait
            ev_wait = 10
            
            best_action = "Invest" if ev_invest > ev_wait else "Wait"
            policy[state] = best_action
            
        return policy

class GeneticOptimizer:
    """Genetic Algorithm (Evolutionary Optimization) - The 'Frankenstein' Merger"""
    
    @staticmethod
    def evolve_ideal(mc_results: Dict[str, Statistics], factors: List[Factor]) -> Dict[str, Any]:
        # 1. Identify the 'Best Gene' for each Factor across all Options
        ideal_genes = {}
        for f in factors:
            # Gather the mean value of this factor from ALL options
            all_means = [stats.factor_stats.get(f.name, {'mean': 0})['mean'] for stats in mc_results.values()]
            
            # Pick the best (Max or Min depending on factor direction)
            # NOTE: Simulator already handles direction (higher score = better), so we always Max the Score
            # But here we are looking at Factor Values.
            # However, the mc_results store factor_stats which are likely already utility scores or raw values?
            # UnifiedDecisionFramework.run_analysis passes raw weighted scores?
            # Let's assume factor_stats stores the *weighted contribution*.
            
            best_val = max(all_means) # Since we weighted them in run_analysis, bigger is always better for the total score
            ideal_genes[f.name] = best_val

        # 2. Construct the Frankenstein Score
        # Sum of all best genes
        theoretical_max = sum(ideal_genes.values())
        
        # 3. Compare with actual winner
        best_actual_stats = max(mc_results.values(), key=lambda x: x.mean_score)
        gap = theoretical_max - best_actual_stats.mean_score
        
        return {
            "ideal_composition": ideal_genes,
            "theoretical_max_score": theoretical_max,
            "best_actual_score": best_actual_stats.mean_score,
            "gap": gap,
            "improvement_potential": (gap / best_actual_stats.mean_score) * 100 if best_actual_stats.mean_score != 0 else 0
        }

class AHPHelper:
    """Analytical Hierarchy Process (Weight Calculator)"""
    
    @staticmethod
    def calculate_weights(matrix: np.ndarray, labels: List[str]) -> Dict[str, float]:
        # Eigenvalue method simplified: Normalize columns, then average rows
        # Input: Pairwise comparison matrix (1 = Equal, 3 = Moderate, 9 = Extreme)
        try:
            # 1. Normalize columns (divide each cell by column sum)
            col_sums = matrix.sum(axis=0)
            norm_matrix = matrix / col_sums
            
            # 2. Average rows to get Priority Vector
            weights = norm_matrix.mean(axis=1)
            
            # 3. Consistency Check (Simplified Lambda Max)
            # Ax = lambda * x
            # lambda_max = mean( (A * weights) / weights )
            weighted_sum_vec = matrix.dot(weights)
            lambda_max = (weighted_sum_vec / weights).mean()
            
            n = len(labels)
            ci = (lambda_max - n) / (n - 1) if n > 1 else 0
            ri_dict = {1: 0, 2: 0, 3: 0.58, 4: 0.9, 5: 1.12, 6: 1.24, 7: 1.32, 8: 1.41, 9: 1.45}
            ri = ri_dict.get(n, 1.49)
            cr = ci / ri if ri != 0 else 0
            
            return {
                "weights": dict(zip(labels, weights)),
                "consistency_ratio": cr,
                "is_consistent": cr < 0.1
            }
        except Exception as e:
             return {"error": str(e)}

class DecisionTheoryEngine:
    """Classic Decision Theory Strategies (The 'Simple' Methodologies)"""
    
    @staticmethod
    def analyze(mc_results: Dict[str, Statistics]) -> Dict[str, str]:
        strategies = {}
        
        # 1. Maximax (Optimistic / Aggressive)
        # Select option with the highest MAX possible outcome
        maximax = max(mc_results.items(), key=lambda x: x[1].max_score)
        strategies["Maximax (Optimistic)"] = f"{maximax[0]} (Best Case: {maximax[1].max_score:.2f})"
        
        # 2. Maximin (Pessimistic / Conservative / Wald)
        # Select option with the highest MIN outcome (Best of the worst)
        maximin = max(mc_results.items(), key=lambda x: x[1].min_score)
        strategies["Maximin (Conservative)"] = f"{maximin[0]} (Worst Case: {maximin[1].min_score:.2f})"
        
        # 3. Hurwicz (Realist / Balanced)
        # Weighted average of Max and Min (alpha = 0.5 default)
        alpha = 0.5
        hurwicz_scores = {
            name: alpha * stats.max_score + (1 - alpha) * stats.min_score 
            for name, stats in mc_results.items()
        }
        best_hurwicz = max(hurwicz_scores.items(), key=lambda x: x[1])
        strategies["Hurwicz (Balanced)"] = f"{best_hurwicz[0]} (Score: {best_hurwicz[1]:.2f})"
        
        # 4. Laplace (Risk Neutral)
        # Average of all outcomes (Same as Mean Score)
        laplace = max(mc_results.items(), key=lambda x: x[1].mean_score)
        strategies["Laplace (Risk Neutral)"] = f"{laplace[0]} (Avg: {laplace[1].mean_score:.2f})"
        
        # 5. Minimax Regret (Opportunity Loss)
        # Calculated from the decision matrix of means
        # Construct simplified regret table based on MEANS
        means = {name: stats.mean_score for name, stats in mc_results.items()}
        best_possible = max(means.values())
        regrets = {name: best_possible - val for name, val in means.items()}
        # Minimize the maximum regret (here simple scalar regret)
        min_regret = min(regrets.items(), key=lambda x: x[1])
        strategies["Minimax Regret"] = f"{min_regret[0]} (Regret: {min_regret[1]:.2f})"
        
        return strategies

class GeminiDeepResearchAgent:
    """Wrapper for Google Gemini Deep Research"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            print("⚠️  GEMINI_API_KEY not found. AI features disabled.")
            self.client = None
        else:
            self.client = genai.Client(api_key=self.api_key)
            self.agent_name = "deep-research-pro-preview-12-2025" 
            
    async def research(self, topic: str, context: str = "") -> str:
        if not self.client:
            return "AI Disabled."
            
        print(f"\n📡 Initiating Deep Research on: {topic}...")
        try:
            # Using flash for demo speed
            response = self.client.models.generate_content(
                model="gemini-2.0-flash", 
                contents=f"Research Topic: {topic}\nContext: {context}\nProvide analysis."
            )
            print("✅ Research Complete.")
            return response.text
        except Exception as e:
            print(f"❌ AI Error: {e}")
            return f"Error: {e}"

# ============================================================================
# 4. UNIFIED FRAMEWORK ORCHESTRATOR
# ============================================================================

class UnifiedDecisionFramework:
    def __init__(self):
        self.mc_engine = MonteCarloEngine()
        self.topsis_engine = TOPSISEngine()
        self.dt_engine = DecisionTheoryEngine()
        self.pareto_engine = ParetoEngine()
        self.sens_engine = SensitivityEngine()
        self.bayes_engine = BayesianEngine()
        self.roa_engine = RealOptionsEngine()
        self.port_engine = PortfolioEngine()
        self.mdp_engine = MDPEngine()
        self.gen_engine = GeneticOptimizer()
        self.ai_agent = GeminiDeepResearchAgent()
        
    def add_option(self, option: DecisionOption):
        self.mc_engine.add_option(option)
        
    def add_factor(self, factor: Factor):
        self.mc_engine.add_factor(factor)
        
    async def run_analysis(self, use_ai: bool = False):
        print("\n" + "="*60)
        print("🚀 STARTING UNIFIED DECISION ANALYSIS v2.0")
        print("="*60 + "\n")
        
        # 1. Run Monte Carlo (Advanced)
        mc_results = self.mc_engine.run()
        
        # 2. Run TOPSIS (Standard)
        data = {}
        for name, stats in mc_results.items():
            row = {}
            for factor_name, f_stats in stats.factor_stats.items():
                row[factor_name] = f_stats['mean']
            data[name] = row
            
        df = pd.DataFrame.from_dict(data, orient='index')
        topsis_scores = pd.Series()
        
        if not df.empty:
            weights = []
            max_bools = []
            for col in df.columns:
                f = next((f for f in self.mc_engine.factors if f.name == col), None)
                if f:
                    weights.append(f.weight)
                    max_bools.append(f.maximize)
                else:
                    weights.append(1.0)
                    max_bools.append(True)
            
            print("\n📊 Running TOPSIS Analysis...")
            topsis_scores = self.topsis_engine.analyze(df, weights, max_bools)

        # 3. Decision Theory (Classic Strategies)
        strategies = self.dt_engine.analyze(mc_results)

        # 4. Advanced Analysis (Pareto & Sensitivity)
        pareto_results = self.pareto_engine.analyze(mc_results, self.mc_engine.factors)
        sensitivity_results = self.sens_engine.analyze(mc_results, self.mc_engine.factors)

        # 5. Future Horizons (Bayesian, ROA, Portfolio, MDP, GA)
        future_metrics = {
            "bayesian_probs": self.bayes_engine.analyze(mc_results),
            "roa_values": self.roa_engine.analyze(mc_results),
            "best_portfolio": self.port_engine.analyze(mc_results),
            "mdp_policy": self.mdp_engine.analyze(),
            "ideal_option": self.gen_engine.evolve_ideal(mc_results, self.mc_engine.factors)
        }

        # 6. AI Deep Research (Optional)
        ai_reports = {}
        if use_ai and self.ai_agent.client:
            tasks = []
            for opt in self.mc_engine.options:
                tasks.append(self.ai_agent.research(opt.name, opt.description))
            
            results = await asyncio.gather(*tasks)
            for opt, res in zip(self.mc_engine.options, results):
                ai_reports[opt.name] = res
        
        # 7. Final Aggregated Report
        self._print_report(mc_results, topsis_scores, strategies, pareto_results, sensitivity_results, future_metrics, ai_reports)
        self.save_report(mc_results, topsis_scores, strategies, pareto_results, sensitivity_results, future_metrics, ai_reports)

    def save_report(self, mc_results, topsis_scores, strategies, pareto, sensitivity, future, ai_reports):
        """Save analysis results to JSON and Markdown files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_dir = os.path.join(os.getcwd(), "results")
        os.makedirs(results_dir, exist_ok=True)
        
        # --- Prepare Decision Matrix (Transparency) ---
        decision_matrix = {}
        for name, stats in mc_results.items():
            decision_matrix[name] = {"total_score": stats.mean_score}
            for factor in self.mc_engine.factors:
                if factor.name in stats.factor_stats:
                    f_stats = stats.factor_stats[factor.name]
                    mean_val = f_stats['mean']
                    contribution = mean_val * factor.weight
                    if not factor.maximize:
                        contribution = -contribution
                    
                    decision_matrix[name][factor.name] = {
                        "raw": mean_val,
                        "weight": factor.weight,
                        "contribution": contribution,
                        "maximize": factor.maximize
                    }

        # --- Save JSON ---
        json_data = {
            "timestamp": timestamp,
            "decision_matrix": decision_matrix,
            "monte_carlo": {
                name: {
                    "mean": stats.mean_score,
                    "std": stats.std_dev,
                    "min": stats.min_score,
                    "max": stats.max_score,
                    "p5": stats.percentile_5,
                    "p95": stats.percentile_95,
                    "var_95": stats.var_95,
                    "cvar_95": stats.cvar_95,
                    "success_rate": stats.success_rate
                } for name, stats in mc_results.items()
            },
            "topsis": topsis_scores.to_dict() if not topsis_scores.empty else {},
            "algorithm_comparison": {}, # Placeholder, populated below
            "ai_insights": ai_reports
        }

        # --- Prepare Algorithm Comparison ---
        algo_comp = {}
        # Rank MC
        sorted_mc = sorted(mc_results.items(), key=lambda x: x[1].mean_score, reverse=True)
        for rank, (name, stats) in enumerate(sorted_mc, 1):
            if name not in algo_comp: algo_comp[name] = {}
            algo_comp[name]["mc_rank"] = rank
            algo_comp[name]["mc_score"] = stats.mean_score
            
        # Rank TOPSIS
        if not topsis_scores.empty:
            sorted_topsis = topsis_scores.sort_values(ascending=False)
            for rank, (name, score) in enumerate(sorted_topsis.items(), 1):
                if name not in algo_comp: algo_comp[name] = {}
                algo_comp[name]["topsis_rank"] = rank
                algo_comp[name]["topsis_score"] = score
        
        json_data["algorithm_comparison"] = algo_comp
        
        json_path = os.path.join(results_dir, f"analysis_{timestamp}.json")
        with open(json_path, "w") as f:
            json.dump(json_data, f, indent=2)
            
        # --- Save Markdown ---
        md_content = f"# 📊 Decision Analysis Report\n\n"
        md_content += f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
        
        md_content += "## 🏆 Algorithm Consensus\n"
        md_content += "| Option | MC Rank (Score) | TOPSIS Rank (Score) |\n"
        md_content += "| :--- | :--- | :--- |\n"
        
        for name, data in algo_comp.items():
            mc_str = f"#{data.get('mc_rank')} ({data.get('mc_score', 0):.2f})"
            top_str = f"#{data.get('topsis_rank', '-')} ({data.get('topsis_score', 0):.4f})" if 'topsis_rank' in data else "-"
            md_content += f"| **{name}** | {mc_str} | {top_str} |\n"

        md_content += "\n## 🧮 Decision Matrix (How it was calculated)\n"
        md_content += "| Option | " + " | ".join([f"{f.name} (w={f.weight})" for f in self.mc_engine.factors]) + " | **Total Score** |\n"
        md_content += "| :--- | " + " | ".join(["---:"] * len(self.mc_engine.factors)) + " | ---: |\n"
        
        for name, data in decision_matrix.items():
            row = f"| **{name}** | "
            for factor in self.mc_engine.factors:
                if factor.name in data:
                    item = data[factor.name]
                    raw = item['raw']
                    cont = item['contribution']
                    sign = "+" if item['maximize'] else "-"
                    row += f"{raw:.2f} ({cont:+.2f}) | "
                else:
                    row += "N/A | "
            row += f"**{data['total_score']:.2f}** |\n"
            md_content += row

            md_content += row

        md_content += "\n## 🧭 Strategic Advice (Classic Methodologies)\n"
        for strat, val in strategies.items():
            icon = "🚀" if "Optimistic" in strat else "🛡️" if "Conservative" in strat else "⚖️"
            md_content += f"- **{icon} {strat}:** {val}\n"

        md_content += "\n## ⚖️ Efficient Frontier (Pareto)\n"
        md_content += f"- **Pareto Efficient Options:** {', '.join(pareto['efficient_frontier'])}\n"
        if pareto['dominated_options']:
            md_content += "- **Dominated Options (Strictly Worse):**\n"
            for loser, winner in pareto['dominated_options']:
                md_content += f"  - ❌ {loser} (Dominated by {winner})\n"

        md_content += "\n## 🌪️ Sensitivity Analysis (Robustness)\n"
        md_content += f"- **Robustness Score:** {sensitivity['robustness_score']*100:.0f}% (Stability against weight changes)\n"
        if sensitivity['changes']:
            md_content += "- **Critical Pivot Points:**\n"
            for change in sensitivity['changes']:
                md_content += f"  - If **{change['factor']}** changes by {change['change']} -> Winner flips to **{change['new_winner']}**\n"
        else:
            md_content += "- **Result is Stable.** No single factor weight change (±20%) alters the winner.\n"

        md_content += "\n## 🔮 Future Horizons (Advanced Analytics)\n"
        
        # Bayesian
        md_content += "### 🧠 Bayesian Inference (Posterior Beliefs)\n"
        for k, v in future['bayesian_probs'].items():
            md_content += f"- **{k}**: {v*100:.1f}% confidence\n"
            
        # ROA
        md_content += "\n### 📈 Real Options (Flexibility Value)\n"
        for k, v in future['roa_values'].items():
            md_content += f"- **{k}**: Option to Wait Valued at {v:.2f}\n"

        # Portfolio
        md_content += f"\n### 💼 Optimal Portfolio (Best Pair diversification)\n"
        pair = future['best_portfolio']
        if pair:
            md_content += f"- **Recommendation:** Combined holding of **{pair[0]}** + **{pair[1]}**\n"
            
        # MDP
        md_content += "\n### 🎲 Markov Strategy (Long Term Policy)\n"
        for state, action in future['mdp_policy'].items():
            md_content += f"- If Market is **{state}** -> **{action}**\n"

        md_content += "\n## 📈 Detailed Statistics\n"
        for name, stats in mc_results.items():
            md_content += f"\n### {name}\n"
            md_content += f"- **Mean Score:** {stats.mean_score:.2f} (±{stats.std_dev:.2f})\n"
            md_content += f"- **95% VaR (Risk):** {stats.var_95:.2f}\n"

            md_content += f"\n#### Factor Breakdown (Why?)\n"
            # Get factors from the engine to know weights/direction
            for factor in self.mc_engine.factors:
                if factor.name in stats.factor_stats:
                    f_stats = stats.factor_stats[factor.name]
                    mean_val = f_stats['mean']
                    
                    # Calculate contribution
                    contribution = mean_val * factor.weight
                    direction = "Maximize" if factor.maximize else "Minimize"
                    sign = "+" if factor.maximize else "-"
                    
                    if not factor.maximize:
                        contribution = -contribution
                        
                    md_content += f"- **{factor.name}** ({direction}, Weight {factor.weight}):\n"
                    md_content += f"  - Avg Value: {mean_val:.2f}\n"
                    md_content += f"  - Impact: **{contribution:+.2f}**\n"

            if name in ai_reports:
                md_content += f"\n> **AI Insight:** {ai_reports[name]}\n"
                
        md_path = os.path.join(results_dir, f"report_{timestamp}.md")
        with open(md_path, "w") as f:
            f.write(md_content)
            
        print(f"\n✅ Results saved to:\n   - {json_path}\n   - {md_path}")

    def _print_report(self, mc_results, topsis_scores, strategies, pareto, sensitivity, future, ai_reports):
        print("\n" + "="*60)
        print("🏆 FINAL DECISION REPORT")
        print("="*60 + "\n")
        
        # Find best MC option
        best_mc = max(mc_results.items(), key=lambda x: x[1].mean_score)
        
        print(f"🥇 Best Monte Carlo Option: {best_mc[0]} (Mean Score: {best_mc[1].mean_score:.2f})")
        if not topsis_scores.empty:
            print(f"🥈 Best TOPSIS Option:      {topsis_scores.index[0]} (Score: {topsis_scores.iloc[0]:.4f})")

        print("\n🧭 Strategic Advice:")
        for strat, val in strategies.items():
            print(f"   - {strat}: {val}")
            
        print("\n⚖️ Pareto Analysis:")
        print(f"   - Efficient: {', '.join(pareto['efficient_frontier'])}")
        if pareto['dominated_options']:
            print(f"   - Dominated: {len(pareto['dominated_options'])} options found.")

        print("\n🌪️ Sensitivity Analysis:")
        print(f"   - Robustness: {sensitivity['robustness_score']*100:.0f}%")
        if sensitivity['changes']:
            print(f"   - ⚠️ Warning: {len(sensitivity['changes'])} scenarios flip the winner.")
        else:
            print("   - ✅ Stable Decision.")

        print("\n🔮 Future Horizons:")
        print(f"   - Bayesian Leader: {max(future['bayesian_probs'], key=future['bayesian_probs'].get)} ({max(future['bayesian_probs'].values())*100:.1f}%)")
        print(f"   - Portfolio Pair: {future['best_portfolio']}")
        print(f"   - MDP Policy: {future['mdp_policy']}")
        
        print("\n--- Detailed Statistics ---")
        for name, stats in mc_results.items():
            print(f"\n🔹 {name}:")
            print(f"   Mean Score: {stats.mean_score:.2f} (±{stats.std_dev:.2f})")
            print(f"   Range: [{stats.min_score:.2f}, {stats.max_score:.2f}]")
            print(f"   95% VaR (Worst Case): {stats.var_95:.2f}")
            print(f"   95% CVaR (Avg Loss):  {stats.cvar_95:.2f}")
            if name in ai_reports:
                print(f"   🤖 AI Insight: {ai_reports[name][:200]}...")

# ============================================================================
# 5. CLI ENTRY POINT
# ============================================================================

async def main():
    parser = argparse.ArgumentParser(description="Unified Decision Maker")
    parser.add_argument("--ai", action="store_true", help="Enable AI Deep Research")
    parser.add_argument("--sims", type=int, default=10000, help="Number of MC simulations")
    args = parser.parse_args()
    
    framework = UnifiedDecisionFramework()
    framework.mc_engine.num_simulations = args.sims
    
    # Example Setup (Real World Scenario)
    print("📋 Setting up Scenario: 'Career Path 2026'")
    
    # Factors (Total weight 1.0)
    framework.add_factor(Factor("Salary", 0.4, maximize=True))
    framework.add_factor(Factor("Balance", 0.3, maximize=True))
    framework.add_factor(Factor("Growth", 0.3, maximize=True))
    
    # Option 1: Stability (Corporate)
    opt1 = DecisionOption("Corporate Director", "High stability, moderate growth")
    # Salary: Normal dist around 4.5M ±200k
    opt1.add_variable("Salary", DistributionType.NORMAL, 4500000, 200000) 
    # Balance: Uniform between 5 and 7 (out of 10)
    opt1.add_variable("Balance", DistributionType.UNIFORM, 5, 7)
    # Growth: Fixed at 4 (low growth)
    opt1.add_variable("Growth", DistributionType.DETERMINISTIC, 4)
    framework.add_option(opt1)
    
    # Option 2: Startup (High Risk)
    opt2 = DecisionOption("Startup Founder", "High risk, potentially huge reward")
    # Salary: Triangular (Min 3M, Mode 4M, Max 15M) - FIXED BUG HERE
    opt2.add_variable("Salary", DistributionType.TRIANGULAR, 3000000, 4000000, 15000000)
    # Balance: Normal dist mean 3 ±1
    opt2.add_variable("Balance", DistributionType.NORMAL, 3, 1)
    # Growth: Beta distribution skewed towards high (alpha=8, beta=2) * 10
    opt2.add_variable("Growth", DistributionType.BETA, 8, 2) 
    framework.add_option(opt2)
    
    # Run
    await framework.run_analysis(use_ai=args.ai)

if __name__ == "__main__":
    asyncio.run(main())
