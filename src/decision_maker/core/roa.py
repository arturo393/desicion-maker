"""
Real Options Analysis (ROA) Engine.
Calculates the value of flexibility (Option to Expand, Delay, or Abandon) using the Black-Scholes framework.
"""

import math

import scipy.stats as st


class RealOptionsEngine:
    @staticmethod
    def calculate_option_value(
        option_type: str,
        S: float, # Present value of cash flows
        K: float, # Investment cost
        T: float, # Time to expiration (years)
        r: float, # Risk-free rate
        sigma: float, # Volatility of cash flows
    ) -> float:
        """
        Calculates the real option value using Black-Scholes formula.
        option_type: 'call' (Expand/Delay) or 'put' (Abandon)
        """
        if T <= 0 or sigma <= 0:
            return max(0, S - K) if option_type == 'call' else max(0, K - S)

        d1 = (math.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))
        d2 = d1 - sigma * math.sqrt(T)

        if option_type == 'call':
            return S * st.norm.cdf(d1) - K * math.exp(-r * T) * st.norm.cdf(d2)
        elif option_type == 'put':
            return K * math.exp(-r * T) * st.norm.cdf(-d2) - S * st.norm.cdf(-d1)
        else:
            raise ValueError(f"Unknown option_type: {option_type}")

    def analyze(self, mc_results: dict) -> dict[str, float]:
        """
        Estimates the intrinsic 'Flexibility Value' of each decision option
        based on its volatility (std_dev) from the Monte Carlo results.
        Assumes a standard 1-year delay option for demonstration.
        """
        roa_values = {}
        for name, stats in mc_results.items():
            # Treat mean score as Present Value (S) and 0.8 * mean as Cost (K) for abstract ROA
            S = max(stats.mean_score, 0.01)
            K = S * 0.8
            # Volatility derived from coefficient of variation
            sigma = stats.std_dev / S if S > 0 else 0.1

            # Calculate option to delay (Call option)
            roa = self.calculate_option_value('call', S, K, T=1.0, r=0.05, sigma=sigma)
            roa_values[name] = roa

        return roa_values
