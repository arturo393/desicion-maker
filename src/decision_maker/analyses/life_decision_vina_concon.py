"""
Life Decision Analysis: Financial Upfront Costs and Savings Plan for Viña Move.
Usage: python python/analyses/life_decision_vina_concon.py
Does NOT: Access external APIs.
"""

import asyncio

from decision_maker.core.models import DecisionOption, DistributionType, Factor
from decision_maker.core.orchestrator import UnifiedDecisionFramework


async def run_life_decision():
    framework = UnifiedDecisionFramework()
    framework.mc_engine.num_simulations = 50000

    # 1. DEFINE FACTORS (Utility scores 0-100)
    framework.add_factor(Factor("Cobertura_Gastos_Entrada", 0.40, maximize=True))        # Capacidad de cubrir matrículas, garantía y mudanza
    framework.add_factor(Factor("Reserva_Emergencia_Post_Mudanza", 0.30, maximize=True)) # Dinero restante en caja tras instalarse
    framework.add_factor(Factor("Cero_Endeudamiento", 0.30, maximize=True))              # Hacer la mudanza 100% con dinero propio

    # 2. DEFINE FINANCING STRATEGIES

    # --- Plan A: Plan de Ahorro 5 Meses en Santiago ($1.3MM/mes de ahorro) ---
    opt_ahorro = DecisionOption("Plan Ahorro 5 Meses Stgo ($1.3MM/mes)", "Ahorrar $1.3MM/mes de Ago a Dic. Total ahorrado: $6.5MM vs Gastos entrada: $4.3MM")
    opt_ahorro.add_variable("Cobertura_Gastos_Entrada", DistributionType.NORMAL, 98, 1)        # Cobertura 100% holgada
    opt_ahorro.add_variable("Reserva_Emergencia_Post_Mudanza", DistributionType.NORMAL, 90, 3) # Quedan +$2.2MM de colchón
    opt_ahorro.add_variable("Cero_Endeudamiento", DistributionType.DETERMINISTIC, 100)         # Cero créditos

    framework.add_option(opt_ahorro)

    # --- Plan B: Mudanza Precipitada (Pedir Crédito o Usar Tarjeta) ---
    opt_credito = DecisionOption("Plan B: Mudanza Inmediata con Crédito", "Pedir préstamo de consumo para pagar matrículas y garantía ya")
    opt_credito.add_variable("Cobertura_Gastos_Entrada", DistributionType.NORMAL, 70, 5)        # Cubre pero con interés
    opt_credito.add_variable("Reserva_Emergencia_Post_Mudanza", DistributionType.NORMAL, 30, 8) # Queda endeudado pagando cuota
    opt_credito.add_variable("Cero_Endeudamiento", DistributionType.DETERMINISTIC, 20)          # Endeudado

    framework.add_option(opt_credito)

    # 3. RUN ANALYSIS
    results = await framework.run_analysis(mode="standard")
    return results


if __name__ == "__main__":
    asyncio.run(run_life_decision())
