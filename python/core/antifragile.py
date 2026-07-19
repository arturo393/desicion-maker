from __future__ import annotations

__all__ = ["AntifragileEngine"]

import logging
from itertools import combinations
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from python.core.models import Factor, Statistics
from python.core.utils import EPSILON

logger = logging.getLogger(__name__)

# Fragility index weights
FRAGILITY_CVAR_WEIGHT = 0.4
FRAGILITY_VAR_WEIGHT = 0.3
FRAGILITY_TAIL_WEIGHT = 0.2
FRAGILITY_SUCCESS_WEIGHT = 0.1
FRAGILITY_CVAR_SCALE = 5.0
FRAGILITY_TAIL_SCALE = 5.0

# Verdict thresholds
CONVEXITY_THRESHOLD = 0.01
FRAGILE_THRESHOLD = 0.6
ROBUST_THRESHOLD = 0.3

# Convexity perturbation multipliers
CONVEXITY_PERTURBATIONS = [0.5, 0.8, 1.2, 1.5]


class AntifragileEngine:
    """
    Antifragile decision analysis inspired by Taleb's concepts.

    Four modes:
      1. Barbell Analysis     — pairs of extreme options vs single options
      2. Convexity / Option   — which options benefit from volatility
      3. Fragility Index      — which options are harmed by tail events
      4. Via Negativa         — what to remove rather than add
    """

    @staticmethod
    def analyze(
        mc_results: Dict[str, Statistics],
        factors: List[Factor],
    ) -> Dict[str, Any]:
        if not mc_results or not factors:
            return {
                "barbell": {},
                "convexity": {},
                "fragility": {},
                "via_negativa": [],
            }

        return {
            "barbell": AntifragileEngine.barbell_analysis(mc_results, factors),
            "convexity": AntifragileEngine.convexity_analysis(mc_results, factors),
            "fragility": AntifragileEngine.fragility_index(mc_results),
            "via_negativa": AntifragileEngine.via_negativa(mc_results, factors),
        }

    # ── 1. Barbell Analysis ──────────────────────────────────────────

    @staticmethod
    def barbell_analysis(
        mc_results: Dict[str, Statistics],
        factors: List[Factor],
    ) -> Dict[str, Any]:
        """
        Test all pairs of options as a 50/50 barbell portfolio.

        A barbell combines a safe option (low risk) with a risky option
        (high upside).  If the portfolio beats every single option, it
        reveals an antifragile opportunity.
        """
        names = list(mc_results.keys())
        if len(names) < 3:
            return {"barbells": [], "summary": "Need at least 3 options for barbell analysis"}

        single_scores = {n: s.mean_score for n, s in mc_results.items()}
        single_risk = {n: s.std_dev for n, s in mc_results.items()}
        best_single = max(single_scores, key=single_scores.get)

        barbells = []
        for a, b in combinations(names, 2):
            portfolio_score = (single_scores[a] + single_scores[b]) / 2.0
            portfolio_risk = np.sqrt(single_risk[a] ** 2 + single_risk[b] ** 2) / 2.0

            beats_all = all(portfolio_score >= single_scores[n] for n in names)

            if beats_all:
                diversification = (
                    f"{single_scores[a]:.3f} + {single_scores[b]:.3f} "
                    f"= {portfolio_score:.3f} (avg)"
                )
                barbells.append({
                    "option_a": a,
                    "option_b": b,
                    "a_score": single_scores[a],
                    "b_score": single_scores[b],
                    "portfolio_score": portfolio_score,
                    "portfolio_risk": portfolio_risk,
                    "diversification_gain": portfolio_score - max(single_scores[a], single_scores[b]),
                    "beats_best_single": portfolio_score > best_single,
                })

        barbells.sort(key=lambda x: x["portfolio_score"], reverse=True)

        return {
            "barbells": barbells,
            "best_single": best_single,
            "best_single_score": single_scores[best_single],
            "num_barbells_found": len(barbells),
        }

    # ── 2. Convexity / Option Value ──────────────────────────────────

    @staticmethod
    def convexity_analysis(
        mc_results: Dict[str, Statistics],
        factors: List[Factor],
    ) -> Dict[str, Any]:
        """
        Measure each option's convexity by perturbing factor variances.

        For each option × factor, scale the factor's variance by
        [0.5x, 0.8x, 1.2x, 1.5x] and recompute the mean score.

        Positive delta = benefits from volatility (antifragile).
        Negative delta = harmed by volatility (fragile).

        Uses raw_factor_data for per-simulation recomputation when
        available, otherwise falls back to a deterministic estimate.
        """
        if not mc_results or not factors:
            return {}

        result: Dict[str, Any] = {}
        perturbations = CONVEXITY_PERTURBATIONS

        for opt_name, stats in mc_results.items():
            if stats.raw_factor_data is None:
                logger.warning(f"No raw_factor_data for {opt_name}, skipping convexity")
                continue

            raw_data = stats.raw_factor_data
            if not raw_data or not all(f.name in raw_data for f in factors):
                continue

            original_score = stats.mean_score
            convexity_scores: Dict[str, Any] = {}

            for f in factors:
                if f.name not in raw_data:
                    continue

                vals = raw_data[f.name]
                f_mean = float(np.mean(vals))
                f_std = float(np.std(vals))

                if f_std < EPSILON:
                    continue

                centered = vals - f_mean
                deltas: Dict[str, float] = {}

                for p in perturbations:
                    new_vals = centered * p + f_mean
                    score = AntifragileEngine._compute_option_score(
                        mc_results, factors, opt_name, f.name, new_vals, raw_data,
                    )
                    deltas[f"{p:.1f}x"] = score - original_score

                # Convexity coefficient: regression slope of score ~ variance_mult
                xs = np.array(perturbations)
                ys = np.array([original_score + deltas.get(f"{p:.1f}x", 0.0) for p in perturbations])
                if np.std(xs) > EPSILON:
                    coeff = np.polyfit(xs, ys, 2)[0]  # quadratic coefficient
                else:
                    coeff = 0.0

                convexity_scores[f.name] = {
                    "mean": f_mean,
                    "std": f_std,
                    "original_score": original_score,
                    "deltas": deltas,
                    "convexity_coefficient": float(coeff),
                    "verdict": (
                        "antifragile" if coeff > CONVEXITY_THRESHOLD
                        else "fragile" if coeff < -CONVEXITY_THRESHOLD
                        else "neutral"
                    ),
                }

            result[opt_name] = convexity_scores

        return result

    @staticmethod
    def _compute_option_score(
        mc_results: Dict[str, Statistics],
        factors: List[Factor],
        opt_name: str,
        target_factor: str,
        new_factor_vals: np.ndarray,
        raw_data: Dict[str, np.ndarray],
    ) -> float:
        """Recompute an option's score with one factor's data replaced."""
        # Build global bounds from all options' raw data, using perturbed
        # values for the target option × factor
        bounds: Dict[str, Dict[str, float]] = {}
        for name, stats in mc_results.items():
            src = stats.raw_factor_data or {}
            for fn, vals in src.items():
                if name == opt_name and fn == target_factor:
                    vals = new_factor_vals
                if fn not in bounds:
                    bounds[fn] = {"min": float("inf"), "max": float("-inf")}
                bounds[fn]["min"] = min(bounds[fn]["min"], float(np.min(vals)))
                bounds[fn]["max"] = max(bounds[fn]["max"], float(np.max(vals)))

        # Compute score for this option
        modified_data = dict(raw_data)
        modified_data[target_factor] = new_factor_vals
        total = np.zeros(len(new_factor_vals))

        for f in factors:
            if f.name not in modified_data:
                continue
            vals = modified_data[f.name]
            b = bounds.get(f.name, {"min": 0.0, "max": 1.0})
            if b["max"] > b["min"]:
                norm = (vals - b["min"]) / (b["max"] - b["min"])
            else:
                norm = np.ones_like(vals)
            if f.maximize:
                total += norm * f.weight
            else:
                total += (1.0 - norm) * f.weight

        return float(np.mean(total))

    # ── 3. Fragility Index ───────────────────────────────────────────

    @staticmethod
    def fragility_index(
        mc_results: Dict[str, Statistics],
    ) -> Dict[str, Any]:
        """
        Quantify fragility per option based on tail-risk metrics.

        Fragility is higher when:
        - CVaR (expected loss in worst 5%) is far from the mean
        - Variance is high relative to the mean
        - Success rate is low

        Returns a fragility score in [0, 1] where 1 = most fragile.
        """
        if not mc_results:
            return {}

        scores: Dict[str, Dict] = {}
        all_fragilities = []

        for name, stats in mc_results.items():
            mean = stats.mean_score
            std = stats.std_dev
            cvar = stats.cvar_95
            var_95 = stats.var_95
            success = stats.success_rate

            # CVaR gap: how far the tail is from the mean (normalized by std)
            cvar_gap = (mean - cvar) / (std + EPSILON)

            # Variance ratio: std relative to mean range
            var_ratio = std / (abs(mean) + EPSILON)

            # Tail fragility: how far the 5th percentile is from the mean
            tail_gap = (mean - var_95) / (std + EPSILON)

            # Composite fragility score (heuristic, 0-1 range)
            raw = (
                FRAGILITY_CVAR_WEIGHT * np.clip(cvar_gap / FRAGILITY_CVAR_SCALE, 0, 1)
                + FRAGILITY_VAR_WEIGHT * np.clip(var_ratio * 2.0, 0, 1)
                + FRAGILITY_TAIL_WEIGHT * np.clip(tail_gap / FRAGILITY_TAIL_SCALE, 0, 1)
                + FRAGILITY_SUCCESS_WEIGHT * (1.0 - success)
            )
            fragility = float(np.clip(raw, 0, 1))

            entry = {
                "fragility_score": fragility,
                "cvar_gap": float(cvar_gap),
                "var_ratio": float(var_ratio),
                "tail_gap": float(tail_gap),
                "cvar_95": cvar,
                "var_95": var_95,
                "success_rate": success,
                "verdict": (
                    "fragile" if fragility > FRAGILE_THRESHOLD
                    else "robust" if fragility < ROBUST_THRESHOLD
                    else "moderate"
                ),
            }
            scores[name] = entry
            all_fragilities.append((name, fragility))

        # Rank by fragility (most fragile first)
        ranking = sorted(all_fragilities, key=lambda x: x[1], reverse=True)

        return {
            "options": scores,
            "ranking": [{"option": n, "fragility_score": s} for n, s in ranking],
            "most_fragile": ranking[0][0] if ranking else None,
            "most_robust": ranking[-1][0] if ranking else None,
        }

    # ── 4. Via Negativa ──────────────────────────────────────────────

    @staticmethod
    def via_negativa(
        mc_results: Dict[str, Statistics],
        factors: List[Factor],
    ) -> List[Dict[str, Any]]:
        """
        Identify factors that, if removed (weight → 0), improve all options.

        This implements the 'Via Negativa' concept: what to stop doing
        rather than start doing.
        """
        if not mc_results or not factors:
            return []

        names = list(mc_results.keys())
        original_scores = {n: s.mean_score for n, s in mc_results.items()}
        original_winner = max(original_scores, key=original_scores.get)
        candidates = []

        for factor_to_remove in factors:
            remaining = [f for f in factors if f.name != factor_to_remove]
            if not remaining:
                continue

            total_remaining_weight = sum(f.weight for f in remaining)
            if total_remaining_weight == 0:
                continue

            new_scores = {}
            for name, stats in mc_results.items():
                if stats.raw_factor_data is not None:
                    raw_data = stats.raw_factor_data
                else:
                    raw_data = {
                        fn: np.array([fstats["mean"]])
                        for fn, fstats in stats.factor_stats.items()
                    }

                total = None
                for f in remaining:
                    if f.name not in raw_data:
                        continue
                    # Renormalize weights
                    w = f.weight / total_remaining_weight
                    vals = raw_data[f.name]
                    total = (vals * w) if total is None else total + vals * w

                new_scores[name] = float(np.mean(total)) if total is not None else 0.0

            all_improved = all(
                new_scores[n] >= original_scores[n] - EPSILON for n in names
            )
            new_winner = max(new_scores, key=new_scores.get)
            winner_flipped = new_winner != original_winner

            candidates.append({
                "removed_factor": factor_to_remove.name,
                "original_weight": factor_to_remove.weight,
                "original_winner": original_winner,
                "new_winner": new_winner,
                "winner_flipped": winner_flipped,
                "all_options_improved": all_improved,
                "score_changes": {
                    n: {
                        "before": original_scores[n],
                        "after": new_scores[n],
                        "delta": new_scores[n] - original_scores[n],
                    }
                    for n in names
                },
            })

        candidates.sort(key=lambda x: sum(
            v["delta"] for v in x["score_changes"].values()
        ), reverse=True)

        return candidates
