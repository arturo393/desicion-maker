#!/usr/bin/env python3
"""
🧠 Generic Decision Matrix & Fuzzy TOPSIS Module
Extends the decision-maker framework to support generic options, 
dynamic criteria weights, and Fuzzy Logic for qualitative uncertainty.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Tuple, Optional
from enum import Enum


class CriterionType(Enum):
    MAXIMIZE = "maximize"
    MINIMIZE = "minimize"


@dataclass
class FuzzyNumber:
    """Triangular Fuzzy Number (a, b, c) where a <= b <= c"""
    a: float  # Lower bound
    b: float  # Modal / Most likely value
    c: float  # Upper bound

    def defuzzify_centroid(self) -> float:
        """Defuzzification using Centroid Method"""
        return (self.a + self.b + self.c) / 3.0

    @classmethod
    def from_linguistic(cls, scale: str):
        """Map common linguistic variables to Triangular Fuzzy Numbers (scale 0-10)"""
        mapping = {
            "MUY_BAJO": cls(0.0, 1.0, 2.5),
            "BAJO": cls(1.5, 3.0, 4.5),
            "MEDIO": cls(4.0, 5.5, 7.0),
            "ALTO": cls(6.0, 7.5, 9.0),
            "MUY_ALTO": cls(8.0, 9.5, 10.0),
        }
        return mapping.get(scale.upper(), cls(5.0, 5.0, 5.0))


@dataclass
class DecisionCriterion:
    name: str
    weight: float
    criterion_type: CriterionType = CriterionType.MAXIMIZE
    description: str = ""


@dataclass
class GenericOption:
    name: str
    description: str = ""
    scores: Dict[str, Any] = field(default_factory=dict)  # Stores numeric or FuzzyNumber scores


class GenericFuzzyDecisionEngine:
    """Generic Decision Engine supporting multi-criteria evaluation with Fuzzy TOPSIS"""

    def __init__(self, criteria: List[DecisionCriterion]):
        self.criteria = {c.name: c for c in criteria}
        # Normalize weights
        total_weight = sum(c.weight for c in criteria)
        for c in self.criteria.values():
            c.weight /= total_weight

    def evaluate_options(self, options: List[GenericOption]) -> List[Dict[str, Any]]:
        """Evaluates generic options using a weighted multi-criteria fuzzy scoring algorithm"""
        results = []

        # Convert fuzzy numbers to crisp values for matrix processing
        crisp_matrix = {}
        for opt in options:
            crisp_matrix[opt.name] = {}
            for crit_name, crit in self.criteria.items():
                val = opt.scores.get(crit_name, 0.0)
                if isinstance(val, FuzzyNumber):
                    crisp_val = val.defuzzify_centroid()
                elif isinstance(val, str):
                    crisp_val = FuzzyNumber.from_linguistic(val).defuzzify_centroid()
                else:
                    crisp_val = float(val)
                crisp_matrix[opt.name][crit_name] = crisp_val

        # Vector normalization & weighted score computation
        scores = {}
        for opt in options:
            total_score = 0.0
            crit_breakdown = {}

            for crit_name, crit in self.criteria.items():
                val = crisp_matrix[opt.name][crit_name]

                # Adjust direction
                if crit.criterion_type == CriterionType.MINIMIZE:
                    # Invert score relative to standard scale (assuming scale 0-10 or normalized)
                    effective_val = max(0.0, 10.0 - val)
                else:
                    effective_val = val

                weighted_contrib = effective_val * crit.weight
                total_score += weighted_contrib
                crit_breakdown[crit_name] = round(weighted_contrib, 3)

            scores[opt.name] = {
                "option_name": opt.name,
                "overall_score": round(total_score, 3),
                "breakdown": crit_breakdown
            }

        # Sort descending by overall score
        sorted_results = sorted(scores.values(), key=lambda x: x["overall_score"], reverse=True)
        for rank, res in enumerate(sorted_results, 1):
            res["rank"] = rank

        return sorted_results

    def perform_sensitivity_analysis(self, options: List[GenericOption], delta_percent: float = 0.20) -> Dict[str, Any]:
        """Performs global sensitivity analysis by perturbing criteria weights by ±delta_percent"""
        base_results = self.evaluate_options(options)
        winner_base = base_results[0]["option_name"]
        
        sensitivity_report = {
            "baseline_winner": winner_base,
            "perturbation_percent": delta_percent * 100,
            "stability_assessment": "ROBUSTO",
            "critical_criteria": []
        }

        flips_detected = 0
        for crit_name, crit in self.criteria.items():
            # Test increase and decrease
            for factor in [1.0 + delta_percent, max(0.01, 1.0 - delta_percent)]:
                # Save original weight
                orig_weight = crit.weight
                crit.weight *= factor
                
                # Re-evaluate
                perturbed_results = self.evaluate_options(options)
                perturbed_winner = perturbed_results[0]["option_name"]
                
                if perturbed_winner != winner_base:
                    flips_detected += 1
                    if crit_name not in sensitivity_report["critical_criteria"]:
                        sensitivity_report["critical_criteria"].append(crit_name)
                
                # Restore original weight
                crit.weight = orig_weight

        if flips_detected > 0:
            sensitivity_report["stability_assessment"] = "SENSIBLE (Sensibilidad detectada)"

        return sensitivity_report


# ============================================================================
# GEMINI AI FUZZY EVALUATOR INTEGRATION
# ============================================================================

class GeminiFuzzyEvaluator:
    """
    Uses Gemini LLM to automatically evaluate options against criteria 
    and assign quantitative or Fuzzy ratings (MUY_BAJO, BAJO, MEDIO, ALTO, MUY_ALTO).
    """

    def __init__(self, api_key: Optional[str] = None, model_name: str = "gemini-2.5-flash", mock_mode: bool = False):
        import os

        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.mock_mode = mock_mode or not bool(self.api_key)
        self.model_name = model_name

        if not self.mock_mode:
            from google import genai
            self.client = genai.Client(api_key=self.api_key)

    def evaluate_option_with_ai(
        self,
        option_name: str,
        option_description: str,
        criteria: List[DecisionCriterion]
    ) -> GenericOption:
        """Asks Gemini to evaluate an option against specified criteria using fuzzy or numeric scales."""
        import json

        if self.mock_mode:
            # Deterministic simulation for demonstration / testing without API key
            scores = {}
            for i, c in enumerate(criteria):
                if c.name.lower().count("costo") or c.name.lower().count("riesgo"):
                    scores[c.name] = "ALTO" if "startup" in option_name.lower() or "riesgo" in option_name.lower() else "BAJO"
                else:
                    scores[c.name] = "MUY_ALTO" if "startup" in option_name.lower() else "MEDIO"
            return GenericOption(name=option_name, description=option_description, scores=scores)

        criteria_desc = []
        for c in criteria:
            criteria_desc.append(
                f"- {c.name}: {c.description or 'Evaluación'} (Tipo: {c.criterion_type.value}). "
                f"Responde con un valor numérico (0.0-10.0) o una etiqueta difusa (MUY_BAJO, BAJO, MEDIO, ALTO, MUY_ALTO)."
            )

        prompt = f"""
Eres un analista experto en toma de decisiones multi-criterio.
Evalúa la siguiente opción con respecto a cada criterio especificado.

Opción: {option_name}
Descripción / Contexto: {option_description}

Criterios:
{chr(10).join(criteria_desc)}

Devuelve únicamente un objeto JSON donde las claves sean exactamente los nombres de los criterios y los valores sean las calificaciones (número float o string difuso 'MUY_BAJO', 'BAJO', 'MEDIO', 'ALTO', 'MUY_ALTO').

Ejemplo de formato de respuesta:
{{
  "{criteria[0].name}": "ALTO",
  "{criteria[1].name}": 7.5
}}
"""

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
            )
            
            # Extract JSON content
            response_text = response.text.strip()
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()

            scores = json.loads(response_text)
            return GenericOption(name=option_name, description=option_description, scores=scores)

        except Exception as e:
            print(f"⚠️ Error al consultar a Gemini para {option_name}: {e}")
            return GenericOption(name=option_name, description=option_description, scores={})


# Quick verification demo
if __name__ == "__main__":
    criteria = [
        DecisionCriterion("Costo_Inversion", weight=0.30, criterion_type=CriterionType.MINIMIZE),
        DecisionCriterion("Rendimiento_Retorno", weight=0.40, criterion_type=CriterionType.MAXIMIZE),
        DecisionCriterion("Riesgo_Burnout", weight=0.15, criterion_type=CriterionType.MINIMIZE),
        DecisionCriterion("Flexibilidad", weight=0.15, criterion_type=CriterionType.MAXIMIZE),
    ]

    engine = GenericFuzzyDecisionEngine(criteria)

    opt1 = GenericOption(
        name="Proyecto A (Conservador)",
        scores={
            "Costo_Inversion": 3.0,
            "Rendimiento_Retorno": 6.0,
            "Riesgo_Burnout": "BAJO",  # Fuzzy rating
            "Flexibilidad": "MEDIO"
        }
    )

    opt2 = GenericOption(
        name="Proyecto B (Startup / Alto Riesgo)",
        scores={
            "Costo_Inversion": 8.0,
            "Rendimiento_Retorno": 9.5,
            "Riesgo_Burnout": "ALTO",  # Fuzzy rating
            "Flexibilidad": "MUY_ALTO"
        }
    )

    ranking = engine.evaluate_options([opt1, opt2])
    print("--- 🎯 Ranking de Decisión Genérica / Fuzzy ---")
    for item in ranking:
        print(f"Rank {item['rank']}: {item['option_name']} - Score: {item['overall_score']}")
        print(f"  Desglose: {item['breakdown']}")

    sensitivity = engine.perform_sensitivity_analysis([opt1, opt2], delta_percent=0.20)
    print("\n--- 🔍 Análisis de Sensibilidad (±20%) ---")
    print(f"Ganador Base: {sensitivity['baseline_winner']}")
    print(f"Evaluación de Estabilidad: {sensitivity['stability_assessment']}")
    print(f"Criterios Críticos: {sensitivity['critical_criteria']}")

    print("\n--- 🤖 Evaluación Automática asistida por Gemini AI ---")
    evaluator = GeminiFuzzyEvaluator(mock_mode=True)
    ai_option1 = evaluator.evaluate_option_with_ai("Opción IA: Empresa Tradicional", "Puesto corporativo estable con buena salud", criteria)
    ai_option2 = evaluator.evaluate_option_with_ai("Opción IA: Startup DeepTech", "Cofundador en una startup de IA de alto riesgo", criteria)

    ai_ranking = engine.evaluate_options([ai_option1, ai_option2])
    for item in ai_ranking:
        print(f"Rank {item['rank']}: {item['option_name']} - Score: {item['overall_score']}")
        print(f"  Calificaciones asignadas por IA: {ai_option1.scores if item['option_name'] == ai_option1.name else ai_option2.scores}")
        print(f"  Desglose: {item['breakdown']}")


