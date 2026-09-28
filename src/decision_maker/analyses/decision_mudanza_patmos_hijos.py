#!/usr/bin/env python3
"""
Decision Analysis: Mudanza a Viña/Concón con 2 hijos al Colegio Patmos
Incluye:
- Costo de 2 hijos en Colegio Patmos.
- Arriendo cerca del colegio (Viña/Concón).
- Ahorro de dinero y tiempo por traslado (actual: Santiago -> Los Quillayes 446. Futuro 2027: Copec Camino Internacional).
"""

import asyncio
from decision_maker.core.models import DecisionOption, DistributionType, Factor
from decision_maker.core.orchestrator import UnifiedDecisionFramework

async def run_analysis():
    framework = UnifiedDecisionFramework()
    framework.mc_engine.num_simulations = 10000

    # Factores (Costo financiero y Tiempo)
    # Valores negativos son mejores para costos y tiempo (por eso maximize=False)
    framework.add_factor(Factor("Costo_Mensual_Vivienda", 0.30, maximize=False, category="Financial"))
    framework.add_factor(Factor("Costo_Mensual_Colegio", 0.30, maximize=False, category="Financial"))
    framework.add_factor(Factor("Costo_Mensual_Traslado", 0.20, maximize=False, category="Financial"))
    framework.add_factor(Factor("Tiempo_Traslado_Horas_Mes", 0.20, maximize=False, category="Time"))

    # Opcion 1: Situación Actual (Santiago + Colegio Subvencionado + Viaje Híbrido a Concón)
    opt_actual = DecisionOption("Situación Actual (Santiago)", "Arriendo en Santiago, colegio actual, viaje 2 veces/sem a Los Quillayes 446")
    opt_actual.add_variable("Costo_Mensual_Vivienda", DistributionType.NORMAL, 750000, 50000)
    opt_actual.add_variable("Costo_Mensual_Colegio", DistributionType.NORMAL, 150000, 20000) # Asumiendo subvencionado para 2
    opt_actual.add_variable("Costo_Mensual_Traslado", DistributionType.NORMAL, 200000, 20000)
    opt_actual.add_variable("Tiempo_Traslado_Horas_Mes", DistributionType.NORMAL, 28, 2)
    framework.add_option(opt_actual)

    # Opcion 2: Mudanza Viña/Concón (Patmos x 2 + Casa Cerca + Trabajo Los Quillayes)
    opt_mudanza = DecisionOption("Mudanza (Patmos x 2, Trabajo Los Quillayes)", "Arriendo Viña/Concón, 2 hijos en Patmos, trabajo en Concón")
    opt_mudanza.add_variable("Costo_Mensual_Vivienda", DistributionType.TRIANGULAR, 800000, 1000000, 1200000)
    opt_mudanza.add_variable("Costo_Mensual_Colegio", DistributionType.NORMAL, 720000, 25000)
    opt_mudanza.add_variable("Costo_Mensual_Traslado", DistributionType.NORMAL, 60000, 10000)
    opt_mudanza.add_variable("Tiempo_Traslado_Horas_Mes", DistributionType.NORMAL, 15, 2)
    framework.add_option(opt_mudanza)

    # Opcion 3: Escenario Futuro (Patmos x 2 + Casa Cerca + Trabajo Camino Internacional 2027)
    opt_futuro = DecisionOption("Mudanza 2027 (Trabajo Copec Camino Intl)", "Igual que Mudanza pero con trabajo más cerca (Camino Internacional)")
    opt_futuro.add_variable("Costo_Mensual_Vivienda", DistributionType.TRIANGULAR, 800000, 1000000, 1200000)
    opt_futuro.add_variable("Costo_Mensual_Colegio", DistributionType.NORMAL, 750000, 30000) # Inflación escolar al 2027
    opt_futuro.add_variable("Costo_Mensual_Traslado", DistributionType.NORMAL, 35000, 5000)
    opt_futuro.add_variable("Tiempo_Traslado_Horas_Mes", DistributionType.NORMAL, 8, 1.5)
    framework.add_option(opt_futuro)

    results = await framework.run_analysis(mode="standard")

    print("\n" + "="*80)
    print("ANÁLISIS DE MUDANZA Y CAMBIO AL COLEGIO PATMOS (2 HIJOS)")
    print("================================================================")
    
    # Check if there is rank aggregation
    ranking = []
    if 'rank_aggregation' in results and 'ranking' in results['rank_aggregation']:
        ranking = results['rank_aggregation']['ranking']
    else:
        # Sort manually by mc_results mean_score
        mc = results['mc_results']
        ranking = sorted(mc.keys(), key=lambda x: mc[x].mean_score, reverse=True)

    for i, opt_name in enumerate(ranking, 1):
        stats = results['mc_results'][opt_name]
        print(f"\nPosición {i}: {opt_name}")
        print(f"Puntaje de Utilidad Global: {stats.mean_score:.2f} / 10.0")

        print("\nDesglose de Costos/Tiempo (Valores Medios Esperados):")
        costo_total = 0
        for f, data in stats.factor_stats.items():
            mean_val = data['mean']
            print(f"  - {f}: {mean_val:,.0f}" + (" hrs" if "Tiempo" in f else " CLP"))
            if "Costo" in f:
                costo_total += mean_val
        
        print(f"  >> COSTO TOTAL MENSUAL ESPERADO: {costo_total:,.0f} CLP")

if __name__ == "__main__":
    asyncio.run(run_analysis())
