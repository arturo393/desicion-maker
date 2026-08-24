"""
Devil's Advocate: AI-driven challenge of a decision model's assumptions.
Usage: from decision_maker.core.devils_advocate import DevilsAdvocate, ChallengeRequest
Does NOT: Modify the decision model directly or override the recommendation.
"""

from __future__ import annotations

__all__ = ["DevilsAdvocate", "ChallengeRequest"]

import json
import re
from dataclasses import dataclass
from typing import Any

from decision_maker.core.content import ChallengeContext, challenge_prompt


@dataclass
class ChallengeRequest:
    """Bundles the decision context the challenger should attack (Parameter Object)."""

    winner: str
    options: list[str]
    factors: list[dict[str, Any]]
    mc_results: dict[str, Any]
    sensitivity: dict[str, Any] | None = None
    explanation: str = ""


class DevilsAdvocate:
    """Questions the robustness of a decision by attacking model assumptions."""

    def __init__(self, use_ai: bool = True):
        self.use_ai = use_ai

    def challenge(self, req: ChallengeRequest) -> dict[str, Any]:
        """Return structured challenges. Falls back to deterministic heuristics when AI is off."""
        heuristic = self._heuristic_challenges(req)
        ai_challenges: list[str] = []

        if self.use_ai:
            ai_challenges = self._ai_challenges(req)

        return {
            "heuristic": heuristic,
            "ai": ai_challenges,
            "n_ai_challenges": len(ai_challenges),
            "source": "ai" if ai_challenges else "heuristic",
        }

    def _heuristic_challenges(self, req: ChallengeRequest) -> list[dict[str, Any]]:
        """Rule-based challenges that never require an API call."""
        challenges = []

        if req.sensitivity:
            weight_flips = req.sensitivity.get("weight_changes", [])
            score_flips = req.sensitivity.get("score_changes", [])
            if weight_flips:
                for f in weight_flips[:3]:
                    challenges.append(
                        {
                            "type": "weight_sensitivity",
                            "severity": "high",
                            "message": (
                                f"Winner flips if weight of '{f['factor']}' changes by "
                                f"{f['change']}. Weights may be too close to a tipping point."
                            ),
                        }
                    )
            if score_flips:
                for f in score_flips[:3]:
                    challenges.append(
                        {
                            "type": "score_sensitivity",
                            "severity": "medium",
                            "message": (
                                f"Winner flips if score of '{f['factor']}' changes by "
                                f"{f['change']}. Small data errors could change the decision."
                            ),
                        }
                    )
            robustness = req.sensitivity.get("robustness_score", 1.0)
            if robustness < 0.6:
                challenges.append(
                    {
                        "type": "low_robustness",
                        "severity": "high",
                        "message": (
                            f"Robustness score is {robustness:.0%}: the decision is not stable "
                            "under perturbations. Consider gathering more data."
                        ),
                    }
                )

        if req.factors:
            total_weight = sum(f.get("weight", 0) for f in req.factors)
            if abs(total_weight - 1.0) > 0.05:
                challenges.append(
                    {
                        "type": "weight_normalization",
                        "severity": "low",
                        "message": (
                            f"Factor weights sum to {total_weight:.2f} (not 1.0). "
                            "Interpretation of the composite score may be misleading."
                        ),
                    }
                )

        return challenges

    def _ai_challenges(self, req: ChallengeRequest) -> list[str]:
        """Query the LLM for qualitative challenges to the model's assumptions."""
        try:
            from decision_maker.core.gemini_agent import GeminiDeepResearchAgent

            agent = GeminiDeepResearchAgent()
            if not agent.is_available:
                return []

            mc_summary = {
                name: {"mean": s["mean"], "std": s["std"]}
                for name, s in req.mc_results.items()
                if isinstance(s, dict)
            }
            if not mc_summary:
                mc_summary = {
                    name: {"mean": getattr(s, "mean_score", 0), "std": getattr(s, "std_dev", 0)}
                    for name, s in req.mc_results.items()
                }

            prompt = challenge_prompt(
                ChallengeContext(
                    winner=req.winner,
                    options=req.options,
                    factors=[f.get("name", "") for f in req.factors],
                    mc_summary=mc_summary,
                    explanation=req.explanation,
                )
            )

            import asyncio

            text = asyncio.run(agent.research("Challenge decision model", prompt))
            if not text or text.startswith("AI Disabled") or text.startswith("Error"):
                return []

            challenges = _extract_json_list(text)
            if challenges:
                return challenges[:5]
            return [text.strip()[:500]] if len(text.strip()) > 20 else []
        except (ConnectionError, TimeoutError, ValueError, RuntimeError, OSError):
            return []


def _extract_json_list(text: str) -> list[str]:
    """Extract a JSON array of strings from LLM output, tolerating extra prose."""
    match = re.search(r"\[.*\]", text, re.DOTALL)
    if not match:
        return []
    try:
        data = json.loads(match.group(0))
        if isinstance(data, list):
            return [str(x) for x in data if str(x).strip()]
    except json.JSONDecodeError:
        return []
    return []
