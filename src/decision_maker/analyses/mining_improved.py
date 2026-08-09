#!/usr/bin/env python3
"""
Título: Análisis de Decisión - Mining Career (Improved)
Propósito: Comparar 3 escenarios de carrera en minería con análisis de riesgo robusto
Fecha de Creación: 2025-12-20
Última Actualización: 2026-01-03
Versión: 2.0
Status: Activo

DESCRIPCIÓN:
🏔️ Decisión sobre carrera en minería - Versión mejorada
Analiza 3 escenarios diferentes:
1. Minería Faena Norte Chile (tradicional - 4x3)
2. Minería Oficina Santiago (modalidad mejorada)
3. Minería Híbrida (balance faena/oficina)

CAMBIOS EN ESTA VERSIÓN (2.0):
- Movido a src/decision_maker/analyses/
- Actualizado import paths
- Análisis de riesgo más robusto con VaR
- Comparación con baseline (trabajo actual)
- Más metodologías: Monte Carlo, TOPSIS, Decision Trees, Sensitivity, VaR

MEJORAS SOBRE v1.0 (mining_decision.py):
- Tercer escenario híbrido agregado
- Análisis de sensibilidad para variables clave
- Value at Risk (VaR) al 95% de confianza
- Datos salariales actualizados 2025-2026

METODOLOGÍAS USADAS:
- Monte Carlo Simulation (10k iteraciones)
- TOPSIS (multi-criteria ranking)
- Decision Trees
- Sensitivity Analysis (impacto variables)
- Value at Risk (VaR 95%)

PRÓXIMOS PASOS:
- [ ] Agregar datos reales de ofertas laborales 2026
- [ ] Incluir análisis de calidad de vida por escenario
- [ ] Comparar con sector tecnología

NOTAS:
- Basado en salarios promedio sector minero chileno 2025
- Considera riesgo de accidentes y burnout en faena
- Resultados guardados en results/mining/
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'core'))

from deep_research_decision_agent import CareerOption, DecisionAnalysisEngine


def create_mining_scenarios():
    """Crear 3 escenarios de minería + baseline"""

    # ESCENARIO 1: Minería Faena (original)
    mining_faena = CareerOption(
        name="Minería Faena - Norte Chile",
        salary_expected=4_500_000,
        probability_success=0.75,
        timeline_months=3,
        tech_growth=7.5,
        income_stability=9.0,
        work_life_balance=5.0,      # ❌ Lejos, turnos
        prestige=8.5,
        remote_flexibility=2.0,      # ❌ Presencial
        learning_opportunity=8.0,
        career_ceiling=9.0,
        unemployment_risk=0.15,
        burnout_risk=0.35,           # ⚠️ Alto
        market_risk=0.20,
        description="Minería tradicional en faena. Turnos 7x7, Antofagasta/Calama. Alto salario pero lejos de familia."
    )

    # ESCENARIO 2: Minería Oficina Santiago (mejorada)
    mining_santiago = CareerOption(
        name="Minería Oficina - Santiago",
        salary_expected=4_200_000,  # Poco menos pero en Santiago
        probability_success=0.65,   # Menos posiciones disponibles
        timeline_months=4,          # Más difícil encontrar
        tech_growth=8.0,            # Más tech en oficina
        income_stability=8.5,       # Igual de estable
        work_life_balance=7.5,      # ✅ En Santiago, horario normal
        prestige=8.0,               # Similar prestigio
        remote_flexibility=6.0,     # ✅ Puede ser híbrido
        learning_opportunity=8.5,   # Más colaboración
        career_ceiling=8.5,         # Path claro pero menos opciones
        unemployment_risk=0.15,
        burnout_risk=0.20,          # ✅ Mucho menor
        market_risk=0.20,
        description="Trabajo en oficinas mineras Santiago (Codelco HQ, BHP). Salario alto, vida normal, híbrido posible."
    )

    # ESCENARIO 3: Minería Híbrida (temporal)
    mining_hybrid = CareerOption(
        name="Minería Híbrida - 2 años + Transición",
        salary_expected=4_500_000,
        probability_success=0.75,
        timeline_months=3,
        tech_growth=8.5,            # ✅ Aprendes + planeas siguiente
        income_stability=9.0,
        work_life_balance=6.0,      # Mejor porque es temporal
        prestige=9.0,
        remote_flexibility=4.0,     # ⚠️ Limitado pero planeas remoto después
        learning_opportunity=9.0,   # ✅ Experiencia + networking
        career_ceiling=9.5,         # ✅ Opens doors para remoto después
        unemployment_risk=0.10,     # Menor porque es estratégico
        burnout_risk=0.25,          # ✅ Menor porque tiene fin planeado
        market_risk=0.15,
        description="2 años minería → experiencia + ahorro + network → transición a remoto internacional. Plan estratégico."
    )

    # Baseline: UQOMM actual
    uqomm = CareerOption(
        name="UQOMM - Actual",
        salary_expected=2_600_000,
        probability_success=1.0,
        timeline_months=0,
        tech_growth=6.0,
        income_stability=7.0,
        work_life_balance=8.0,
        prestige=6.0,
        remote_flexibility=7.0,
        learning_opportunity=6.0,
        career_ceiling=6.0,
        unemployment_risk=0.10,
        burnout_risk=0.20,
        market_risk=0.25,
        description="Status quo. Seguro pero limitado."
    )

    return [mining_faena, mining_santiago, mining_hybrid, uqomm]


def main():
    print("\n" + "="*70)
    print("   🏔️ ANÁLISIS: ¿Qué versión de minería es mejor?")
    print("="*70 + "\n")

    options = create_mining_scenarios()

    print("📋 Escenarios a evaluar:\n")
    for i, opt in enumerate(options, 1):
        print(f"{i}. {opt.name}")
        print(f"   💰 ${opt.salary_expected:,.0f} | ⏱️ {opt.timeline_months}m | 🎯 {opt.probability_success*100:.0f}%")
        print(f"   ⚖️  WLB: {opt.work_life_balance}/10 | 🏠 Remote: {opt.remote_flexibility}/10 | 🔥 Burnout: {opt.burnout_risk*100:.0f}%")
        print(f"   📝 {opt.description[:70]}...")
        print()

    print("🔄 Analizando con Python Framework (13 metodologías)...\n")
    engine = DecisionAnalysisEngine(debug=False)

    results = []
    for option in options:
        print(f"   ▶ {option.name}...")
        result = engine.analyze_option(option, options)
        results.append(result)

    print("\n" + "="*70)
    print("   📊 RESULTADOS COMPARATIVOS")
    print("="*70 + "\n")

    sorted_results = sorted(zip(options, results, strict=False),
                          key=lambda x: x[1].overall_score,
                          reverse=True)

    for rank, (option, result) in enumerate(sorted_results, 1):
        emoji = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else "  "
        print(f"{emoji} RANK {rank}: {option.name}")
        print(f"   📊 Score: {result.overall_score:.2f}/10 | 🎯 Confianza: {result.confidence*100:.0f}%")
        print(f"   💰 Salario: ${option.salary_expected:,.0f}")
        print(f"   ⚖️  WLB: {option.work_life_balance}/10 | 🏠 Remote: {option.remote_flexibility}/10")
        print(f"   ⚠️  Risk: {result.risk_score:.2f} | 🏆 TOPSIS: #{result.topsis_rank}")
        print(f"   {result.recommendation}")
        print()

    # Comparación de mejoras
    print("="*70)
    print("   📈 ANÁLISIS DE MEJORA")
    print("="*70 + "\n")

    faena_score = results[0].overall_score
    santiago_score = results[1].overall_score
    hybrid_score = results[2].overall_score

    print(f"   Faena Original:     {faena_score:.2f}/10 (baseline)")
    print(f"   Santiago Oficina:   {santiago_score:.2f}/10 (mejora: {santiago_score-faena_score:+.2f})")
    print(f"   Híbrida Temporal:   {hybrid_score:.2f}/10 (mejora: {hybrid_score-faena_score:+.2f})")

    best_mining = max([(results[i].overall_score, i) for i in range(3)])[1]
    best_name = options[best_mining].name
    best_score = results[best_mining].overall_score

    print(f"\n   🎯 MEJOR OPCIÓN MINERÍA: {best_name}")
    print(f"   📊 Score: {best_score:.2f}/10")

    if best_score >= 5.0:
        print("   ✅ Score aceptable (≥5.0)")
    elif best_score >= 3.5:
        print("   ⚠️  Score moderado (3.5-5.0)")
    else:
        print("   ⚠️  Score bajo (<3.5)")

    # Comparar con UQOMM
    uqomm_score = results[3].overall_score
    print(f"\n   📊 vs UQOMM actual ({uqomm_score:.2f}/10):")
    if best_score > uqomm_score:
        diff = best_score - uqomm_score
        print(f"   ✅ Minería {best_name} es mejor (+{diff:.2f})")
    else:
        diff = uqomm_score - best_score
        print(f"   ⚠️  UQOMM es más seguro (+{diff:.2f})")

    print("\n" + "="*70)
    print("   💡 RECOMENDACIÓN FINAL")
    print("="*70)

    if best_mining == 1:  # Santiago
        print("\n   🏙️ Busca trabajo minería en SANTIAGO")
        print("   • Mejor work-life balance")
        print("   • Híbrido posible")
        print("   • Mantiene salario alto ($4.2M)")
    elif best_mining == 2:  # Híbrida
        print("\n   🎯 Estrategia HÍBRIDA TEMPORAL")
        print("   • 2 años en faena (experiencia + $$)")
        print("   • Network minería")
        print("   • Transición a remoto internacional")
    else:  # Faena
        print("\n   ⚠️  Si eliges faena, ten plan claro")
        print("   • Cuánto tiempo estarás")
        print("   • Qué ahorrarás")
        print("   • Exit plan")

    print("\n" + "="*70 + "\n")

    return best_name, best_score


if __name__ == "__main__":
    winner, score = main()
    print(f"✨ Mejor opción: {winner} ({score:.2f}/10)\n")
