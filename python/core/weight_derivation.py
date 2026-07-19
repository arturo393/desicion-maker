from __future__ import annotations

__all__ = ["WeightDerivationEngine"]

import itertools
import logging
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from python.core.ahp import AHPHelper

logger = logging.getLogger(__name__)


class WeightDerivationEngine:
    """
    Derives factor weights from human judgment using three methods:

    1. Swing Weighting — rank factors and assign relative importance
    2. Pairwise Comparison (AHP) — Saaty matrix → eigenvector weights
    3. PAPRIKA — tradeoff questions → partial ranking → weights
    """

    # ── 1. Swing Weighting ───────────────────────────────────────────

    @staticmethod
    def swing_weights(
        ratings: Dict[str, float],
    ) -> Dict[str, Any]:
        """
        Derive weights from swing importance ratings (0-100 scale).

        Args:
            ratings: {factor_name: importance} where 100 = most important,
                     0 = irrelevant.  The factor with the highest rating
                     gets the swing baseline.

        Returns:
            {weights: {name: weight}, method: "swing", normalized: bool}
        """
        if not ratings:
            return {"weights": {}, "method": "swing", "error": "No ratings provided"}

        names = list(ratings.keys())
        values = np.array([max(ratings[n], 0.0) for n in names])
        total = np.sum(values)

        if total == 0:
            return {
                "weights": {n: 1.0 / len(names) for n in names},
                "method": "swing",
                "note": "All ratings were zero; using equal weights",
            }

        weights = {n: float(v / total) for n, v in zip(names, values)}

        return {
            "weights": weights,
            "method": "swing",
            "raw_ratings": ratings,
        }

    @staticmethod
    def swing_from_ranking(
        ranked_factors: List[str],
        top_weight: float = 100.0,
        decay: str = "linear",
    ) -> Dict[str, Any]:
        """
        Derive weights from a simple ranked list.

        Args:
            ranked_factors: factors in descending importance order
            top_weight: weight for the most important factor (default 100)
            decay: "linear" — each subsequent factor gets top_weight/(rank)
                   "exponential" — top_weight * 0.5^(rank-1)

        Returns: {weights: {name: weight}, method: "swing_ranked"}
        """
        if not ranked_factors:
            return {"weights": {}, "method": "swing_ranked", "error": "No factors"}

        n = len(ranked_factors)
        values = np.zeros(n)

        for i, name in enumerate(ranked_factors):
            if decay == "exponential":
                values[i] = top_weight * (0.5 ** i)
            else:
                values[i] = top_weight / (i + 1)

        total = np.sum(values)
        weights = {ranked_factors[i]: float(values[i] / total) for i in range(n)}

        return {
            "weights": weights,
            "method": "swing_ranked",
            "decay": decay,
        }

    # ── 2. Pairwise Comparison (AHP) ─────────────────────────────────

    @staticmethod
    def pairwise_weights(
        comparisons: Dict[Tuple[str, str], float],
        labels: List[str],
    ) -> Dict[str, Any]:
        """
        Derive weights from pairwise comparison judgments.

        Args:
            comparisons: {(more_important, less_important): Saaty_value}
                         Saaty scale: 1=equal, 3=moderate, 5=strong,
                         7=very strong, 9=extreme
                         The reciprocal is automatically inferred.
            labels: all factor names (order determines matrix position)

        Returns: AHPHelper result with weights, consistency_ratio, etc.
        """
        if not labels:
            return {"error": "No labels provided"}
        n = len(labels)
        if n < 2:
            return {"error": "Need at least 2 factors for pairwise comparison"}

        matrix = np.ones((n, n))
        label_to_idx = {name: i for i, name in enumerate(labels)}

        for (more, less), value in comparisons.items():
            if more not in label_to_idx or less not in label_to_idx:
                continue
            i = label_to_idx[more]
            j = label_to_idx[less]
            safe_val = max(min(value, 9.0), 1.0 / 9.0)
            matrix[i, j] = safe_val
            matrix[j, i] = 1.0 / safe_val

        result = AHPHelper.calculate_weights(matrix, labels)
        if "error" not in result:
            result["method"] = "pairwise"
            result["comparisons_used"] = len(comparisons)
        return result

    @staticmethod
    def pairwise_interactive_prompt(labels: List[str]) -> List[str]:
        """
        Generate the list of pairwise comparison questions to ask.

        Each question: "How much more important is {A} than {B}?"
        Returns formatted strings for display.
        """
        questions = []
        for i, a in enumerate(labels):
            for b in labels[i + 1:]:
                questions.append(
                    f"How much more important is '{a}' than '{b}'?\n"
                    f"  1 = Equal  3 = Moderate  5 = Strong  "
                    f"7 = Very Strong  9 = Extreme\n"
                    f"  (use fractions like 1/3 if B is more important)"
                )
        return questions

    # ── 3. PAPRIKA ───────────────────────────────────────────────────

    @staticmethod
    def paprika_weights(
        factors: List[str],
        tradeoff_answers: Dict[Tuple[str, str], str],
    ) -> Dict[str, Any]:
        """
        Derive weights from PAPRIKA-style tradeoff questions.

        PAPRIKA: Potentially All Pairwise RanKings of all possible
        Alternatives.  Users choose which improvement is more important:
        "Improve factor A from worst to best" vs "Improve factor B from
        worst to best".

        Args:
            factors: list of factor names
            tradeoff_answers: {(winner, loser): direction}
                where direction is "A" (first is more important) or
                "B" (second is more important)

        Returns:
            {weights: {name: weight}, method: "paprika",
             rankings: [...], pairwise_wins: {...}}
        """
        if len(factors) < 2:
            return {"error": "Need at least 2 factors for PAPRIKA"}

        # Count pairwise wins
        wins = {f: 0 for f in factors}
        total_comparisons = len(tradeoff_answers)

        for (a, b), winner in tradeoff_answers.items():
            if winner == "A":
                wins[a] += 1
            elif winner == "B":
                wins[b] += 1

        # Build partial ranking from win counts
        if total_comparisons == 0:
            return {
                "weights": {f: 1.0 / len(factors) for f in factors},
                "method": "paprika",
                "note": "No tradeoff answers provided; using equal weights",
                "pairwise_wins": wins,
                "rankings": [],
            }

        sorted_factors = sorted(factors, key=lambda f: wins[f], reverse=True)
        max_wins = max(wins.values()) if wins else 1

        # Convert win counts to weights via normalized score
        if max_wins > 0:
            weights = {
                f: float(wins[f] / max_wins) if wins[f] > 0 else 0.01
                for f in factors
            }
        else:
            weights = {f: 1.0 for f in factors}

        total = sum(weights.values())
        weights = {f: w / total for f, w in weights.items()}

        return {
            "weights": weights,
            "method": "paprika",
            "pairwise_wins": wins,
            "total_comparisons": total_comparisons,
            "rankings": sorted_factors,
        }

    @staticmethod
    def paprika_generate_questions(
        factors: List[str],
        max_questions: int = 10,
    ) -> List[Tuple[str, str, str]]:
        """
        Generate PAPRIKA tradeoff questions.

        Each question: "Which improvement matters more?
          A) Improve {factor_a} from worst to best
          B) Improve {factor_b} from worst to best"

        Returns [(factor_a, factor_b, question_text), ...]
        """
        questions = []
        pairs = list(itertools.combinations(factors, 2))
        # Shuffle for variety
        rng = np.random.default_rng(42)
        indices = rng.permutation(len(pairs))

        for idx in indices[:max_questions]:
            a, b = pairs[idx]
            text = (
                f"Which improvement matters more?\n"
                f"  A) Improve '{a}' from worst possible to best possible\n"
                f"  B) Improve '{b}' from worst possible to best possible\n"
                f"Answer A or B:"
            )
            questions.append((a, b, text))

        return questions

    # ── 4. Convenience: derive from any method ───────────────────────

    @staticmethod
    def derive(
        method: str,
        **kwargs,
    ) -> Dict[str, Any]:
        methods = {
            "swing": WeightDerivationEngine.swing_weights,
            "swing_ranked": lambda **kw: WeightDerivationEngine.swing_from_ranking(
                kw.get("ranked_factors", []),
                kw.get("top_weight", 100.0),
                kw.get("decay", "linear"),
            ),
            "pairwise": lambda **kw: WeightDerivationEngine.pairwise_weights(
                kw.get("comparisons", {}),
                kw.get("labels", []),
            ),
            "paprika": lambda **kw: WeightDerivationEngine.paprika_weights(
                kw.get("factors", []),
                kw.get("tradeoff_answers", {}),
            ),
        }
        handler = methods.get(method)
        if not handler:
            return {"error": f"Unknown method: {method}.  Choose from: {list(methods.keys())}"}
        return handler(**kwargs)
