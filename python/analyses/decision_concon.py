#!/usr/bin/env python3
"""
🌊 Decision Analysis: Mudanza a Concón vs Alternativas (Santiago / Trabajo Remoto / Híbrido)
Motor: GenericFuzzyDecisionEngine con Soporte Difuso (Fuzzy TOPSIS) + Análisis de Sensibilidad (±20%)
"""

import sys
from pathlib import Path

# Configurar path para importar core
sys.path.insert(0, str(Path(__file__).parent.parent / 'core'))

from generic_fuzzy_decision import (
    GenericFuzzyDecisionEngine,
    DecisionCriterion,
    CriterionType,
    GenericOption,
    GeminiFuzzyEvaluator
)

def run_concon_decision_analysis():
    print("======================================================================")
    print("🌊 ANÁLISIS DE DECISIÓN REAL: MUDANZA A CONCÓN vs SANTIAGO")
    print("   (Restricciones: Sin Crédito/Compra, Viaje en Moto, Modelo Híbrido, Colegios Subvencionados)")
    print("======================================================================")

    # 1. Definición de Criterios ajustados a la realidad explícita
    criteria = [
        DecisionCriterion(
            name="Costo_Arriendo_y_Gastos",
            weight=0.25,
            criterion_type=CriterionType.MINIMIZE,
            description="Costo mensual de arriendo de departamento/casa dentro del presupuesto (sin crédito/compra)"
        ),
        DecisionCriterion(
            name="Viabilidad_y_Costo_Traslado_Moto",
            weight=0.20,
            criterion_type=CriterionType.MINIMIZE,
            description="Costo de combustible, peajes de Ruta 68/Las Palmas y peligro/fatiga de viajar en moto a Santiago"
        ),
        DecisionCriterion(
            name="Acceso_a_Colegios_Subvencionados",
            weight=0.20,
            criterion_type=CriterionType.MAXIMIZE,
            description="Disponibilidad y calidad de cupos en colegios particulares subvencionados (Concón/Viña vs Santiago)"
        ),
        DecisionCriterion(
            name="Calidad_de_Vida_y_Entorno_Familiar",
            weight=0.15,
            criterion_type=CriterionType.MAXIMIZE,
            description="Tranquilidad, aire marino y ambiente para la familia"
        ),
        DecisionCriterion(
            name="Estabilidad_y_Formato_Laboral",
            weight=0.20,
            criterion_type=CriterionType.MAXIMIZE,
            description="Compatibilidad con trabajo presencial/híbrido (ya que no existe contrato 100% remoto)"
        ),
    ]

    # 2. Opciones Realistas basadas en tus Restricciones
    options = [
        GenericOption(
            name="Opción A: Mudarse a Concón + Viaje a Santiago en Moto (Híbrido 1-2 días)",
            description="Arriendo en Concón, niños a colegio subvencionado local, viajes a Santiago en moto 1-2 veces por semana.",
            scores={
                "Costo_Arriendo_y_Gastos": "MEDIO",                  # Arriendos en Concón variados
                "Viabilidad_y_Costo_Traslado_Moto": "ALTO",           # Peligro en carretera + peajes + frío/lluvia
                "Acceso_a_Colegios_Subvencionados": "MEDIO",         # Cupos limitados en Concón, alternativas en Viña/Quintero
                "Calidad_de_Vida_y_Entorno_Familiar": "MUY_ALTO",
                "Estabilidad_y_Formato_Laboral": "MEDIO"              # Desgaste físico del trayecto en moto
            }
        ),
        GenericOption(
            name="Opción B: Vivir en Concón + Trabajar Localmente (Viña/Valparaíso/Concón)",
            description="Arriendo en Concón, colegio subvencionado local, buscar trabajo/clientes en la V Región (sin viajar a Santiago).",
            scores={
                "Costo_Arriendo_y_Gastos": "MEDIO",
                "Viabilidad_y_Costo_Traslado_Moto": "MUY_BAJO",       # Traslados cortos locales en moto
                "Acceso_a_Colegios_Subvencionados": "MEDIO",
                "Calidad_de_Vida_y_Entorno_Familiar": "MUY_ALTO",
                "Estabilidad_y_Formato_Laboral": "BAJO"               # Mercado laboral en V región es más reducido que Santiago
            }
        ),
        GenericOption(
            name="Opción C: Permanecer en Santiago (Arriendo + Colegio Subvencionado)",
            description="Arriendo en comuna conveniente de Santiago, colegio subvencionado cercano, traslado corto en moto a oficina.",
            scores={
                "Costo_Arriendo_y_Gastos": "ALTO",                  # Arriendos caros en Santiago
                "Viabilidad_y_Costo_Traslado_Moto": "BAJO",           # Moto en ciudad (distancias cortas, sin peajes interurbanos)
                "Acceso_a_Colegios_Subvencionados": "ALTO",          # Mayor oferta de colegios subvencionados
                "Calidad_de_Vida_y_Entorno_Familiar": "BAJO",        # Más contaminación, ruido y estrés
                "Estabilidad_y_Formato_Laboral": "MUY_ALTO"          # Cercanía total a oportunidades laborales presenciales/híbridas
            }
        ),
    ]

    # 3. Evaluar
    engine = GenericFuzzyDecisionEngine(criteria)
    results = engine.evaluate_options(options)

    print("\n🏆 RANKING RESULTANTE CON RESTRICCIONES REALES:")
    for res in results:
        print(f"\n🥇 Posición {res['rank']}: {res['option_name']}")
        print(f"   Puntaje Global: {res['overall_score']} / 10.0")
        print("   Desglose Ponderado por Criterio:")
        for crit, score in res['breakdown'].items():
            print(f"     - {crit}: {score}")

    # 4. Sensibilidad
    print("\n" + "=" * 70)
    print("🔍 ANÁLISIS DE SENSIBILIDAD GLOBAL (Perturbación ±20% en Criterios)")
    print("=" * 70)

    sensitivity = engine.perform_sensitivity_analysis(options, delta_percent=0.20)
    print(f"   Opción Ganadora Baseline: {sensitivity['baseline_winner']}")
    print(f"   Evaluación de Estabilidad: {sensitivity['stability_assessment']}")
    print(f"   Criterios Críticos: {sensitivity['critical_criteria']}")


if __name__ == "__main__":
    run_concon_decision_analysis()
