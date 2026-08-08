"""
Decision model evaluating response strategies for the Becker Varis compatibility project,
explicitly considering developer time overhead (Hands-on Engineering vs Reporting Overhead).
Usage: python python/analyses/becker_response_decision.py
Does NOT: Execute external network calls.
"""

import asyncio

from decision_maker.core.models import DecisionOption, DistributionType, Factor
from decision_maker.core.orchestrator import UnifiedDecisionFramework


async def run_evaluation():
    framework = UnifiedDecisionFramework()
    framework.mc_engine.num_simulations = 50000

    # 1. Define Factors (Utility Scores 0-100)
    # Weights sum to 1.0
    framework.add_factor(Factor("Proteccion_Tiempo_Desarrollo", 0.35, maximize=True)) # Maximizar tiempo libre para programar/RF
    framework.add_factor(Factor("Credibilidad_Jefatura", 0.25, maximize=True))       # Mantener confianza de Federico y Nicanor
    framework.add_factor(Factor("Proteccion_Equipo_Riesgo", 0.20, maximize=True))  # Margen para PCB (2 semanas)
    framework.add_factor(Factor("Bajo_Overhead_Gestion", 0.20, maximize=True))     # Minimizar tiempo perdido en hacer informes/planos

    # 2. Define Options

    # Opción A1: Planificación Macro + Reporte Liviano (Bulleted / 5 min daily)
    opt_a1 = DecisionOption("Opción A1: Cronograma Macro + Reporte Diario Ultra-Liviano", "Plan macro de semanas + reporte diario de 3 viñetas (overhead < 5 min/día)")
    opt_a1.add_variable("Proteccion_Tiempo_Desarrollo", DistributionType.NORMAL, 85, 4) # Alta protección del tiempo de desarrollo
    opt_a1.add_variable("Credibilidad_Jefatura", DistributionType.NORMAL, 88, 3)        # Alta credibilidad
    opt_a1.add_variable("Proteccion_Equipo_Riesgo", DistributionType.NORMAL, 85, 4)     # Absorbe 2 sem de PCB
    opt_a1.add_variable("Bajo_Overhead_Gestion", DistributionType.NORMAL, 90, 3)        # Overhead mínimo (3 viñetas al día)

    # Opción A2: Planificación Detallada Día a Día (Overhead Alto)
    opt_a2 = DecisionOption("Opción A2: Cronograma Ultra-Detallado Día por Día", "Hacer Carta Gantt micro-detallada diariamente")
    opt_a2.add_variable("Proteccion_Tiempo_Desarrollo", DistributionType.NORMAL, 40, 8) # Pierde horas programando Gantts
    opt_a2.add_variable("Credibilidad_Jefatura", DistributionType.NORMAL, 80, 5)        # Alta pero rígida
    opt_a2.add_variable("Proteccion_Equipo_Riesgo", DistributionType.NORMAL, 75, 5)     # Riesgo de desfase por burocracia
    opt_a2.add_variable("Bajo_Overhead_Gestion", DistributionType.NORMAL, 20, 6)        # Pésimo: quita tiempo real de trabajo

    # Opción B: Cronograma Agresivo sin margen PCB (Ago 14)
    opt_b = DecisionOption("Opción B: Promesa Agresiva sin margen PCB", "Prometer fecha antigua sin holgura de hardware")
    opt_b.add_variable("Proteccion_Tiempo_Desarrollo", DistributionType.NORMAL, 30, 10) # Cero tiempo por apuros de última hora
    opt_b.add_variable("Credibilidad_Jefatura", DistributionType.NORMAL, 35, 10)       # Destruida al no llegar en Ago
    opt_b.add_variable("Proteccion_Equipo_Riesgo", DistributionType.NORMAL, 20, 5)        # Sin holgura
    opt_b.add_variable("Bajo_Overhead_Gestion", DistributionType.NORMAL, 60, 8)        # Bajo hoy, pero bomberil después

    framework.add_option(opt_a1)
    framework.add_option(opt_a2)
    framework.add_option(opt_b)

    # 3. Run Analysis
    results = await framework.run_analysis(use_ai=False)
    return results


if __name__ == "__main__":
    asyncio.run(run_evaluation())
