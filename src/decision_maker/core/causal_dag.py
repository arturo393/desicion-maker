"""
Minimal causal DAG: generate a causal map before deciding.
Usage: from decision_maker.core.causal_dag import CausalDAG
Does NOT: Run decision algorithms or compute scores.
"""

from __future__ import annotations

__all__ = ["CausalDAG", "CausalNode", "CausalEdge"]

import logging
from dataclasses import dataclass, field
from typing import Any

from decision_maker.core.models import Factor

logger = logging.getLogger(__name__)


@dataclass
class CausalNode:
    """A node in the causal DAG (Parameter Object)."""

    name: str
    node_type: str
    description: str = ""
    is_observed: bool = True
    is_intervened: bool = False
    is_confounder: bool = False


@dataclass
class CausalEdge:
    """A directed edge in the causal DAG (Parameter Object)."""

    source: str
    target: str
    strength: str
    direction: str
    confidence: str
    reasoning: str = ""


class CausalDAG:
    """
    Generates a minimal causal DAG from factors and options.

    Based on Pearl's do-calculus: before deciding, you must separate
    what you OBSERVE from what you INTERVENE on. The DAG makes this
    explicit.

    This is NOT a full causal inference engine. It's a structured
    thinking tool that forces the decision-maker to:
    1. Name the causal variables
    2. Declare which ones you control (intervene) vs observe
    3. Identify potential confounders
    4. Ask "what variable am I ignoring?"

    Pearl's insight: P(y|do(x)) ≠ P(y|x) when confounders exist.
    The DAG makes confounders visible.
    """

    @staticmethod
    def build(
        factors: list[Factor],
        options: list[str],
        context: str = "",
    ) -> dict[str, Any]:
        nodes: list[CausalNode] = []
        edges: list[CausalEdge] = []

        decision_node = CausalNode(
            name="decision",
            node_type="decision",
            description="The choice being made",
            is_observed=False,
            is_intervened=True,
        )
        nodes.append(decision_node)

        outcome_node = CausalNode(
            name="outcome",
            node_type="outcome",
            description="The result of the decision",
            is_observed=False,
        )
        nodes.append(outcome_node)

        for factor in factors:
            node_type = "factor"
            is_confounder = CausalDAG._detect_confounder(factor)
            node = CausalNode(
                name=factor.name,
                node_type=node_type,
                description=f"Weight={factor.weight}, maximize={factor.maximize}",
                is_observed=True,
                is_confounder=is_confounder,
            )
            nodes.append(node)
            edges.append(CausalEdge(
                source=factor.name,
                target="outcome",
                strength="moderate" if factor.weight > 0.3 else "weak",
                direction="→",
                confidence="assumed",
                reasoning=f"Factor '{factor.name}' influences outcome (weight={factor.weight})",
            ))

        for i, f1 in enumerate(factors):
            for f2 in factors[i + 1:]:
                if f1.name != f2.name:
                    edges.append(CausalEdge(
                        source=f1.name,
                        target=f2.name,
                        strength="unknown",
                        direction="↔",
                        confidence="unverified",
                        reasoning=f"Potential correlation between '{f1.name}' and '{f2.name}' — needs verification",
                    ))

        confounders = [n for n in nodes if n.is_confounder]
        warnings = []
        if confounders:
            warnings.append(
                f"Potential confounders detected: {', '.join(n.name for n in confounders)}. "
                f"These may create spurious correlations."
            )

        for option in options:
            edges.append(CausalEdge(
                source="decision",
                target="outcome",
                strength="strong",
                direction="→",
                confidence="hypothesized",
                reasoning=f"Option '{option}' is hypothesized to lead to outcome",
            ))

        do_calculus_reminder = (
            "REMEMBER: P(outcome|do(decision)) ≠ P(outcome|decision). "
            "The decision is an INTERVENTION, not an observation. "
            "Account for confounders before trusting the causal path."
        )

        return {
            "nodes": [{"name": n.name, "type": n.node_type, "is_intervened": n.is_intervened,
                       "is_confounder": n.is_confounder} for n in nodes],
            "edges": [{"source": e.source, "target": e.target, "strength": e.strength,
                       "direction": e.direction, "confidence": e.confidence} for e in edges],
            "confounders": [n.name for n in confounders],
            "warnings": warnings,
            "do_calculus_reminder": do_calculus_reminder,
            "num_nodes": len(nodes),
            "num_edges": len(edges),
            "thinking_questions": CausalDAG._thinking_questions(factors, confounders),
        }

    @staticmethod
    def _detect_confounder(factor: Factor) -> bool:
        return factor.weight > 0.3 and not factor.maximize

    @staticmethod
    def _thinking_questions(
        factors: list[Factor],
        confounders: list[CausalNode],
    ) -> list[str]:
        questions = [
            "What variable is NOT in my model that could explain the outcome?",
            "If I intervene on the decision, what other variables change?",
            "Is there a variable that causes BOTH my decision factors AND the outcome?",
        ]
        if confounders:
            names = ", ".join(n.name for n in confounders)
            questions.append(
                f"The factors {names} may be confounders. "
                f"Are they truly independent of the outcome, or do they share a hidden cause?"
            )
        low_weight = [f for f in factors if f.weight < 0.1]
        if low_weight:
            names = ", ".join(f.name for f in low_weight)
            questions.append(
                f"The factors {names} have very low weight. "
                f"Should they be in the model at all, or are they noise?"
            )
        return questions

    @staticmethod
    def to_dict(dag: dict[str, Any]) -> dict[str, Any]:
        return dag
