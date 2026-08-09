#!/usr/bin/env python3
"""
Título: Análisis de Decisión - Mining Career (v1 - Archived)
Propósito: Decisión de buscar trabajo en minería en Chile con objetivo $4.5M+ CLP/mes
Fecha de Creación: 2025-11-15
Última Actualización: 2025-12-15
Versión: 1.0
Status: Archivado (ver mining_improved.py para versión actualizada)

DESCRIPCIÓN:
🏔️ Análisis inicial de decisión de trabajo en minería Chile
- Objetivo: $4.5M+ CLP/mes antes de Marzo 2026
- Compara minería vs trabajo actual vs otras opciones
- Primera iteración del análisis de carrera minera

CAMBIOS EN ESTA VERSIÓN (1.0):
- Movido a python/analyses/ directory
- Actualizado import paths
- Versión original archivada para referencia

METODOLOGÍAS USADAS:
- Decision Trees
- Expected Value
- Scenario Analysis

ESTADO: ARCHIVADO
Esta es la versión 1.0 del análisis. Ver mining_improved.py (v2.0) para:
- Análisis más robusto con Monte Carlo y VaR
- Tres escenarios en lugar de dos
- Análisis de sensibilidad mejorado
- Datos actualizados 2025-2026

NOTAS:
- Preservado para referencia histórica
- No actualizar, usar mining_improved.py en su lugar
- Resultados guardados en results/mining/
"""

import sys
from pathlib import Path

# Add core to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'core'))

from deep_research_decision_agent import CareerOption, DecisionAnalysisEngine


def create_mining_options():
    """Crear opciones de carrera incluyendo minería"""

    # OPCIÓN 1: Trabajo Minería Chile (target)
    mining = CareerOption(
        name="Minería Chile - Ingeniero Senior",

        # Salario objetivo
        salary_expected=4_500_000,  # $4.5M CLP/mes

        # Probabilidad de éxito (70-80% según plan)
        probability_success=0.75,  # 75%

        # Timeline realista
        timeline_months=3,  # 12 semanas = 3 meses

        # Factores técnicos/profesionales (0-10)
        tech_growth=7.5,            # Tecnología minera avanzada
        income_stability=9.0,        # Minería estable, contratos largos
        work_life_balance=5.0,       # Turnos 7x7 o similar, lejos de Santiago
        prestige=8.5,                # Minería en Chile es prestigioso
        remote_flexibility=2.0,      # Requiere presencia en faena
        learning_opportunity=8.0,    # Tecnologías IoT, automatización
        career_ceiling=9.0,          # Path a líder, gerente

        # Riesgos
        unemployment_risk=0.15,      # 15% - minería es cíclica
        burnout_risk=0.35,           # 35% - trabajo exigente, lejos de casa
        market_risk=0.20,            # 20% - depende de precio commodities

        description="Trabajo en gran minería Chile (Codelco, BHP, Anglo American). Salario $4.5M+, turnos rotativos, Norte de Chile (Antofagasta, Calama). Tecnología avanzada, carrera sólida, lejos de familia."
    )

    # OPCIÓN 2: UQOMM actual (baseline)
    uqomm = CareerOption(
        name="UQOMM - Actual",

        salary_expected=2_600_000,  # Salario actual

        probability_success=1.0,    # Ya lo tienes

        timeline_months=0,  # Ya estás ahí

        # Factores
        tech_growth=6.0,            # Tecnología OK
        income_stability=7.0,       # Estable pero limitado
        work_life_balance=8.0,      # En Santiago, buenos horarios
        prestige=6.0,               # Menos prestigio que minería
        remote_flexibility=7.0,     # Posiblemente híbrido
        learning_opportunity=6.0,   # Limitado a sistemas actuales
        career_ceiling=6.0,         # Techo bajo ($3.5M max)

        # Riesgos
        unemployment_risk=0.10,     # 10% - empresa estable
        burnout_risk=0.20,          # 20% - trabajo moderado
        market_risk=0.25,           # 25% - sector específico

        description="Trabajo actual en UQOMM. Salario $2.6M, Santiago, estable pero con techo limitado. Zona de confort."
    )

    # OPCIÓN 3: Trabajo remoto internacional
    remote = CareerOption(
        name="Remoto Internacional - Tech",

        salary_expected=5_500_000,  # ~$3k USD = ~$5.5M CLP

        probability_success=0.50,   # 50% - competitivo

        timeline_months=6,  # 6 meses búsqueda

        # Factores
        tech_growth=9.0,            # Tecnología cutting-edge
        income_stability=6.0,       # Contratos, puede cambiar
        work_life_balance=9.0,      # Remoto, horarios flexibles
        prestige=8.0,               # Tech internacional
        remote_flexibility=10.0,    # 100% remoto
        learning_opportunity=9.0,   # Aprende mucho
        career_ceiling=9.5,         # Techo muy alto

        # Riesgos
        unemployment_risk=0.30,     # 30% - mercado volátil
        burnout_risk=0.40,          # 40% - siempre on, timezones
        market_risk=0.35,           # 35% - layoffs tech

        description="Trabajo remoto para empresa USA/Europa. Salario USD alto, 100% remoto, pero requiere inglés fluido y experiencia específica."
    )

    # OPCIÓN 4: Emprendimiento (DeFi Monitor)
    startup = CareerOption(
        name="Emprendimiento - DeFi Monitor",

        salary_expected=3_000_000,  # Proyección 6-12 meses

        probability_success=0.40,   # 40% - startups difíciles

        timeline_months=12,  # 1 año para tener ingresos

        # Factores
        tech_growth=10.0,           # Aprendes todo
        income_stability=3.0,       # Muy inestable
        work_life_balance=2.0,      # Trabajas 24/7
        prestige=7.0,               # Founder
        remote_flexibility=10.0,    # Tu horario
        learning_opportunity=10.0,  # Aprendes TODO
        career_ceiling=10.0,        # Ilimitado si funciona

        # Riesgos
        unemployment_risk=0.60,     # 60% - puede fallar
        burnout_risk=0.70,          # 70% - muy demandante
        market_risk=0.50,           # 50% - crypto volátil

        description="Lanzar DeFi Monitor como producto. Potencial alto pero riesgo máximo. Requiere inversión tiempo y dinero."
    )

    return [mining, uqomm, remote, startup]


def main():
    """Ejecutar análisis de decisión minería"""
    print("\n" + "="*70)
    print("   🏔️ ANÁLISIS: ¿Trabajar en Minería Chile 2026?")
    print("="*70 + "\n")

    # Crear opciones
    options = create_mining_options()

    print("📋 Opciones a evaluar:\n")
    for i, opt in enumerate(options, 1):
        print(f"{i}. {opt.name}")
        print(f"   💰 Salario: ${opt.salary_expected:,.0f} CLP/mes")
        print(f"   ⏱️  Timeline: {opt.timeline_months} mes(es)")
        print(f"   🎯 Prob. éxito: {opt.probability_success*100:.0f}%")
        print(f"   📝 {opt.description[:80]}...")
        print()

    # Inicializar engine
    print("🔄 Ejecutando análisis con 13 metodologías...\n")
    engine = DecisionAnalysisEngine(debug=False)

    # Analizar cada opción
    results = []
    for option in options:
        print(f"   Analizando: {option.name}...")
        result = engine.analyze_option(option, options)
        results.append(result)

    # Mostrar resultados
    print("\n" + "="*70)
    print("   📊 RESULTADOS DEL ANÁLISIS")
    print("="*70 + "\n")

    # Ordenar por overall_score
    sorted_results = sorted(zip(options, results, strict=False),
                          key=lambda x: x[1].overall_score,
                          reverse=True)

    for rank, (option, result) in enumerate(sorted_results, 1):
        emoji = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else "  "
        print(f"{emoji} RANK {rank}: {option.name}")
        print(f"\n   💰 Salario: ${option.salary_expected:,.0f} CLP/mes")
        print(f"   📊 Overall Score: {result.overall_score:.2f}/10")
        print(f"   🎯 Confianza: {result.confidence*100:.1f}%")
        print(f"   📈 Monte Carlo: {result.monte_carlo_score:.2f}")
        print(f"   🏆 TOPSIS Rank: #{result.topsis_rank}")
        print(f"   ⚖️  Pareto Optimal: {'✅ Sí' if result.pareto_optimal else '❌ No'}")
        print(f"   ⚠️  Risk Score: {result.risk_score:.2f}")

        print("\n   💡 Recomendación:")
        print(f"   {result.recommendation}")
        print("\n" + "-"*70 + "\n")

    # Análisis específico minería
    mining_idx = 0  # Primera opción
    mining_option = options[mining_idx]
    mining_result = results[mining_idx]

    print("="*70)
    print("   🎯 ANÁLISIS ESPECÍFICO: MINERÍA CHILE")
    print("="*70)

    print(f"\n   📊 Score General: {mining_result.overall_score:.2f}/10")
    print(f"   🎯 Confianza: {mining_result.confidence*100:.1f}%")

    print("\n   💰 Análisis Financiero:")
    print("   - Salario actual: $2,600,000")
    print("   - Salario minería: $4,500,000")
    print(f"   - Incremento: +${1_900_000:,.0f} (+73%)")
    print(f"   - Anual extra: ~${22_800_000:,.0f}")

    print("\n   ⚖️  Ventajas:")
    print(f"   ✅ Income Stability: {mining_option.income_stability}/10 (contratos largos)")
    print(f"   ✅ Prestige: {mining_option.prestige}/10 (minería es top)")
    print(f"   ✅ Career Ceiling: {mining_option.career_ceiling}/10 (path claro)")
    print(f"   ✅ Tech Growth: {mining_option.tech_growth}/10 (tecnología avanzada)")

    print("\n   ⚠️  Desventajas:")
    print(f"   ❌ Work-Life Balance: {mining_option.work_life_balance}/10 (lejos, turnos)")
    print(f"   ❌ Remote Flexibility: {mining_option.remote_flexibility}/10 (presencial)")
    print(f"   ⚠️  Burnout Risk: {mining_option.burnout_risk*100:.0f}% (demandante)")

    print("\n   📅 Timeline:")
    print("   - Duración plan: 12 semanas (3 meses)")
    print(f"   - Probabilidad éxito: {mining_option.probability_success*100:.0f}%")
    print(f"   - Timeline realista: {mining_option.timeline_months} meses")

    print("\n   🎲 Análisis de Riesgo:")
    print(f"   - Risk Score: {mining_result.risk_score:.2f}")
    print(f"   - Unemployment: {mining_option.unemployment_risk*100:.0f}%")
    print(f"   - Market Risk: {mining_option.market_risk*100:.0f}%")
    print(f"   - Regret si no funciona: {mining_result.regret_analysis:.2f}")

    print("\n" + "="*70)
    print("   ✅ CONCLUSIÓN")
    print("="*70)

    if mining_result.overall_score >= 7.0:
        print("\n   🎉 MINERÍA ES LA MEJOR OPCIÓN")
    elif mining_result.overall_score >= 5.0:
        print("\n   ⚠️  MINERÍA ES VIABLE PERO CON CONSIDERACIONES")
    else:
        print("\n   ⚠️  MINERÍA TIENE RIESGOS SIGNIFICATIVOS")

    print(f"\n   {mining_result.recommendation}")

    # Comparación con UQOMM
    uqomm_result = results[1]
    print("\n   📊 vs UQOMM actual:")
    print(f"   - Score: {mining_result.overall_score:.2f} vs {uqomm_result.overall_score:.2f}")
    print("   - Salario: +73% más")
    print(f"   - Risk: {mining_result.risk_score:.2f} vs {uqomm_result.risk_score:.2f}")

    if mining_result.overall_score > uqomm_result.overall_score:
        print("   ✅ Minería es mejor que UQOMM actual")
    else:
        print("   ⚠️  UQOMM actual es más seguro")

    print("\n" + "="*70 + "\n")

    return mining_option.name, mining_result.overall_score


if __name__ == "__main__":
    winner, score = main()
    print("✨ Análisis completado\n")
    print(f"Minería score: {score:.2f}/10\n")
