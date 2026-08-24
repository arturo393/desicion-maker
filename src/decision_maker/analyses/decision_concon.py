#!/usr/bin/env python3
"""
Decision Analysis: Mudanza a Concón vs Alternativas (Santiago / Trabajo Remoto / Híbrido)
Motor: FuzzyWeightedSum con Soporte Difuso (lingüístico) + Análisis de Sensibilidad (±20%)
Uses: decision_maker.core.fuzzy_weighted_sum
"""

from decision_maker.core.fuzzy_weighted_sum import (
    FuzzyWeightedSum,
    FuzzyCriterion,
    FuzzyOption,
    CriterionDirection,
)


def run_concon_decision_analysis() -> None:
    print("======================================================================")
    print("ANÁLISIS DE DECISIÓN REAL: MUDANZA A CONCÓN vs SANTIAGO")
    print("   (Restricciones: Sin Crédito/Compra, Viaje en Moto, Modelo Híbrido, Colegios Subvencionados)")
    print("======================================================================")

    criteria = [
        FuzzyCriterion(
            name="Costo_Arriendo_y_Gastos",
            weight=0.25,
            direction=CriterionDirection.MINIMIZE,
            description="Costo mensual de arriendo de departamento/casa dentro del presupuesto (sin crédito/compra)",
        ),
        FuzzyCriterion(
            name="Viabilidad_y_Costo_Traslado_Moto",
            weight=0.20,
            direction=CriterionDirection.MINIMIZE,
            description="Costo de combustible, peajes de Ruta 68/Las Palmas y peligro/fatiga de viajar en moto a Santiago",
        ),
        FuzzyCriterion(
            name="Acceso_a_Colegios_Subvencionados",
            weight=0.20,
            direction=CriterionDirection.MAXIMIZE,
            description="Disponibilidad y calidad de cupos en colegios particulares subvencionados (Concón/Viña vs Santiago)",
        ),
        FuzzyCriterion(
            name="Calidad_de_Vida_y_Entorno_Familiar",
            weight=0.15,
            direction=CriterionDirection.MAXIMIZE,
            description="Tranquilidad, aire marino y ambiente para la familia",
        ),
        FuzzyCriterion(
            name="Estabilidad_y_Formato_Laboral",
            weight=0.20,
            direction=CriterionDirection.MAXIMIZE,
            description="Compatibilidad con trabajo presencial/híbrido (ya que no existe contrato 100% remoto)",
        ),
    ]

    options = [
        FuzzyOption(
            name="Opción A: Mudarse a Concón + Viaje a Santiago en Moto (Híbrido 1-2 días)",
            description="Arriendo en Concón, niños a colegio subvencionado local, viajes a Santiago en moto 1-2 veces por semana.",
            scores={
                "Costo_Arriendo_y_Gastos": "MEDIO",
                "Viabilidad_y_Costo_Traslado_Moto": "ALTO",
                "Acceso_a_Colegios_Subvencionados": "MEDIO",
                "Calidad_de_Vida_y_Entorno_Familiar": "MUY_ALTO",
                "Estabilidad_y_Formato_Laboral": "MEDIO",
            },
        ),
        FuzzyOption(
            name="Opción B: Vivir en Concón + Trabajar Localmente (Viña/Valparaíso/Concón)",
            description="Arriendo en Concón, colegio subvencionado local, buscar trabajo/clientes en la V Región (sin viajar a Santiago).",
            scores={
                "Costo_Arriendo_y_Gastos": "MEDIO",
                "Viabilidad_y_Costo_Traslado_Moto": "MUY_BAJO",
                "Acceso_a_Colegios_Subvencionados": "MEDIO",
                "Calidad_de_Vida_y_Entorno_Familiar": "MUY_ALTO",
                "Estabilidad_y_Formato_Laboral": "BAJO",
            },
        ),
        FuzzyOption(
            name="Opción C: Permanecer en Santiago (Arriendo + Colegio Subvencionado)",
            description="Arriendo en comuna conveniente de Santiago, colegio subvencionado cercano, traslado corto en moto a oficina.",
            scores={
                "Costo_Arriendo_y_Gastos": "ALTO",
                "Viabilidad_y_Costo_Traslado_Moto": "BAJO",
                "Acceso_a_Colegios_Subvencionados": "ALTO",
                "Calidad_de_Vida_y_Entorno_Familiar": "BAJO",
                "Estabilidad_y_Formato_Laboral": "MUY_ALTO",
            },
        ),
    ]

    engine = FuzzyWeightedSum(criteria)
    results = engine.evaluate(options)

    print("\nRANKING RESULTANTE CON RESTRICCIONES REALES:")
    for res in results:
        print(f"\nPosición {res['rank']}: {res['option_name']}")
        print(f"   Puntaje Global: {res['overall_score']} / 10.0")
        print("   Desglose Ponderado por Criterio:")
        for crit, score in res["breakdown"].items():
            print(f"     - {crit}: {score}")

    print("\n" + "=" * 70)
    print("ANÁLISIS DE SENSIBILIDAD GLOBAL (Perturbación ±20% en Criterios)")
    print("=" * 70)

    sensitivity = engine.sensitivity(options, delta=0.20)
    print(f"   Opción Ganadora Baseline: {sensitivity['baseline_winner']}")
    print(f"   Evaluación de Estabilidad: {sensitivity['stability_assessment']}")
    print(f"   Criterios Críticos: {sensitivity['critical_criteria']}")


if __name__ == "__main__":
    run_concon_decision_analysis()
