#!/usr/bin/env python3
"""
Título: Análisis de Decisión - SQM Santiago Career Option
Propósito: Evaluar oportunidad laboral en SQM Santiago vs otras opciones
Fecha de Creación: 2025-12-10
Última Actualización: 2025-12-10
Versión: 1.0
Status: Activo

DESCRIPCIÓN:
🏢 Análisis de oportunidad SQM Santiago
- Empresa: SQM (Sociedad Química y Minera de Chile)
- Posición: Ingeniero Senior
- Ubicación: Santiago (oficinas, no faena)
- Sector: Minería/Químicos (litio, potasio, yodo)

CONTEXTO:
Análisis específico de oportunidad en SQM Santiago comparando con:
- Otras opciones de minería
- Trabajo actual
- Otras empresas del sector

CAMBIOS EN ESTA VERSIÓN (1.0):
- Movido a src/decision_maker/analyses/
- Actualizado import paths
- Primera versión del análisis SQM

METODOLOGÍAS USADAS:
- TOPSIS (multi-criteria ranking)
- Multi-Criteria Decision Analysis
- Scenario Analysis (mejor caso, caso base, peor caso)

FACTORES EVALUADOS:
- Salario: $4.8M CLP/mes (competitivo)
- Estabilidad: 9.5/10 (empresa sólida)
- Crecimiento técnico: 8.5/10 (innovación litio)
- Ubicación: Santiago (no faena)
- Work-life balance: Mejor que faena

PRÓXIMOS PASOS:
- [ ] Actualizar con datos reales si hay oferta
- [ ] Comparar con minería faena vs oficina
- [ ] Análisis de compensación total (no solo sueldo)

NOTAS:
- Análisis confidencial para decisión personal
- SQM = líder mundial en litio y yodo
- Ventaja: Ubicación Santiago (sin 4x3)
- Resultados guardados en results/sqm/
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'core'))

from deep_research_decision_agent import CareerOption, DecisionAnalysisEngine


def create_improved_options():
    """Crear opciones incluyendo SQM Santiago"""

    # NUEVA OPCIÓN: SQM Santiago
    sqm_santiago = CareerOption(
        name="SQM Santiago - Ingeniero Senior",
        salary_expected=4_800_000,  # SQM paga muy bien
        probability_success=0.70,   # Buena empresa, competitivo
        timeline_months=3,          # 3 meses búsqueda
        tech_growth=8.5,            # Innovación en litio
        income_stability=9.5,       # SQM muy estable
        work_life_balance=8.5,      # ✅ Santiago, buenos horarios
        prestige=9.5,               # ✅ SQM es top tier Chile
        remote_flexibility=7.0,     # ✅ Híbrido probable
        learning_opportunity=9.0,   # Tecnología punta litio
        career_ceiling=9.0,         # Path a líder
        unemployment_risk=0.05,     # ✅ Muy bajo
        burnout_risk=0.15,          # ✅ Muy bajo
        market_risk=0.15,           # Litio en auge
        description="SQM Santiago. Líder mundial litio. Salario top, Santiago, híbrido, prestigio máximo, estabilidad."
    )

    # Minería Faena (baseline)
    mining_faena = CareerOption(
        name="Minería Faena - Norte",
        salary_expected=4_500_000,
        probability_success=0.75,
        timeline_months=3,
        tech_growth=7.5,
        income_stability=9.0,
        work_life_balance=5.0,
        prestige=8.5,
        remote_flexibility=2.0,
        learning_opportunity=8.0,
        career_ceiling=9.0,
        unemployment_risk=0.15,
        burnout_risk=0.35,
        market_risk=0.20,
        description="Faena norte. Alto salario pero lejos, turnos."
    )

    # Minería Híbrida Temporal
    mining_hybrid = CareerOption(
        name="Minería Híbrida - 2 años",
        salary_expected=4_500_000,
        probability_success=0.75,
        timeline_months=3,
        tech_growth=8.5,
        income_stability=9.0,
        work_life_balance=6.0,
        prestige=9.0,
        remote_flexibility=4.0,
        learning_opportunity=9.0,
        career_ceiling=9.5,
        unemployment_risk=0.10,
        burnout_risk=0.25,
        market_risk=0.15,
        description="2 años faena → remoto. Plan estratégico."
    )

    # UQOMM Actual
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
        description="Status quo. Seguro, limitado."
    )

    # Remoto Internacional
    remote_intl = CareerOption(
        name="Remoto Internacional",
        salary_expected=5_500_000,
        probability_success=0.50,
        timeline_months=6,
        tech_growth=9.0,
        income_stability=6.0,
        work_life_balance=9.0,
        prestige=8.0,
        remote_flexibility=10.0,
        learning_opportunity=9.0,
        career_ceiling=9.5,
        unemployment_risk=0.30,
        burnout_risk=0.40,
        market_risk=0.35,
        description="Tech remoto USA/Europa. Alto salario USD, 100% remoto."
    )

    return [sqm_santiago, mining_hybrid, mining_faena, uqomm, remote_intl]


def analyze_score_improvements():
    """Analizar cómo mejorar scores"""

    print("\n" + "="*70)
    print("   📊 ¿POR QUÉ SCORES BAJOS? ¿CÓMO MEJORAR?")
    print("="*70 + "\n")

    print("🔍 RAZÓN DE SCORES BAJOS (2.6-3.1/10):")
    print("-" * 70)
    print()
    print("El framework Python es CONSERVADOR y penaliza:")
    print()
    print("1. ❌ Work-Life Balance bajo (<7/10)")
    print("   Minería faena: 5/10")
    print("   → Penalización fuerte")
    print()
    print("2. ❌ Remote Flexibility bajo (<5/10)")
    print("   Minería: 2-4/10")
    print("   → Framework valora remoto")
    print()
    print("3. ❌ Burnout Risk alto (>25%)")
    print("   Minería: 25-35%")
    print("   → Resta puntos directamente")
    print()
    print("4. ⚠️  Trade-offs necesarios")
    print("   Salario alto ↔ WLB bajo")
    print("   → Ninguna opción es \"perfecta\"")
    print()

    print("="*70)
    print("   💡 CÓMO MEJORAR SCORES")
    print("="*70 + "\n")

    print("✅ ESTRATEGIA 1: Buscar opciones que maximicen múltiples factores")
    print("-" * 70)
    print()
    print("SQM Santiago es EXACTAMENTE esto:")
    print("  • Salario alto: $4.8M ✅")
    print("  • WLB: 8.5/10 (Santiago) ✅")
    print("  • Remote: 7/10 (híbrido) ✅")
    print("  • Burnout: 15% (bajo) ✅")
    print("  • Prestigio: 9.5/10 ✅")
    print()
    print("→ Score proyectado: ~5-6/10 (mucho mejor)")
    print()

    print("✅ ESTRATEGIA 2: Ajustar pesos del framework")
    print("-" * 70)
    print()
    print("Si NO te importa tanto remoto:")
    print("  • Reducir peso Remote Flexibility: 10% → 5%")
    print("  • Aumentar peso Salary: implícito → 15%")
    print("  → Minería sube a ~4-5/10")
    print()

    print("✅ ESTRATEGIA 3: Cambiar perspectiva temporal")
    print("-" * 70)
    print()
    print("Framework asume \"permanente\"")
    print("Si cambias a \"2 años temporal\":")
    print("  • WLB bajo es \"aceptable temporalmente\"")
    print("  • Burnout reduce (sabes que es corto plazo)")
    print("  → Score mejora +0.5 a +1.0")
    print()

    print("="*70 + "\n")


def main():
    print("\n" + "="*70)
    print("   🏢 ANÁLISIS: SQM Santiago + Opciones Mejoradas")
    print("="*70 + "\n")

    # Análisis de mejora
    analyze_score_improvements()

    # Crear opciones
    options = create_improved_options()

    print("📋 Opciones a evaluar (incluyendo SQM):\n")
    for i, opt in enumerate(options, 1):
        print(f"{i}. {opt.name}")
        print(f"   💰 ${opt.salary_expected:,.0f} | ⏱️ {opt.timeline_months}m | 🎯 {opt.probability_success*100:.0f}%")
        print(f"   ⚖️  WLB: {opt.work_life_balance}/10 | 🏠 Remote: {opt.remote_flexibility}/10")
        print(f"   🔥 Burnout: {opt.burnout_risk*100:.0f}% | 🏆 Prestige: {opt.prestige}/10")
        print(f"   📝 {opt.description[:65]}...")
        print()

    print("🔄 Analizando con Python Framework...\n")
    engine = DecisionAnalysisEngine(debug=False)

    results = []
    for option in options:
        print(f"   ▶ {option.name}...")
        result = engine.analyze_option(option, options)
        results.append(result)

    print("\n" + "="*70)
    print("   📊 RESULTADOS CON SQM SANTIAGO")
    print("="*70 + "\n")

    sorted_results = sorted(zip(options, results, strict=False),
                          key=lambda x: x[1].overall_score,
                          reverse=True)

    for rank, (option, result) in enumerate(sorted_results, 1):
        emoji = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else "  "
        print(f"{emoji} RANK {rank}: {option.name}")
        print(f"   📊 Score: {result.overall_score:.2f}/10")
        print(f"   🎯 Confianza: {result.confidence*100:.0f}%")
        print(f"   💰 Salario: ${option.salary_expected:,.0f}")
        print(f"   ⚖️  WLB: {option.work_life_balance}/10 | Remote: {option.remote_flexibility}/10")
        print(f"   ⚠️  Risk: {result.risk_score:.2f} | Burnout: {option.burnout_risk*100:.0f}%")

        # Recomendación con color
        if result.overall_score >= 5.0:
            print("   ✅ RECOMENDADO - Score ≥5.0")
        elif result.overall_score >= 3.5:
            print("   ⚠️  VIABLE - Score moderado")
        else:
            print(f"   {result.recommendation}")
        print()

    # Análisis SQM específico
    sqm_idx = 0
    sqm_result = results[sqm_idx]
    sqm_option = options[sqm_idx]

    print("="*70)
    print("   🎯 ANÁLISIS ESPECÍFICO: SQM SANTIAGO")
    print("="*70 + "\n")

    print(f"   📊 Score: {sqm_result.overall_score:.2f}/10")
    print(f"   🎯 Confianza: {sqm_result.confidence*100:.0f}%\n")

    print("   💎 VENTAJAS SQM:")
    print("   ✅ Salario top tier: $4.8M (+85% vs UQOMM)")
    print("   ✅ Work-Life Balance: 8.5/10 (excelente)")
    print("   ✅ Prestigio máximo: 9.5/10 (SQM = top Chile)")
    print("   ✅ Santiago: Con familia, sin turnos")
    print("   ✅ Híbrido: 7/10 remote flexibility")
    print("   ✅ Estabilidad: 9.5/10 (líder mundial litio)")
    print("   ✅ Burnout bajo: 15% (vs 35% faena)")
    print("   ✅ Tecnología: 8.5/10 (innovación litio)\n")

    print("   ⚠️  CONSIDERACIONES:")
    print("   • Competitivo (70% probabilidad)")
    print("   • 3 meses timeline búsqueda")
    print("   • Proceso selectivo riguroso\n")

    print("   💰 ROI vs UQOMM:")
    print(f"   • Incremento: +${sqm_option.salary_expected - 2_600_000:,.0f}/mes (+85%)")
    print(f"   • Anual: +${(sqm_option.salary_expected - 2_600_000) * 12:,.0f}")
    print(f"   • 3 años: +${(sqm_option.salary_expected - 2_600_000) * 36:,.0f}\n")

    print("="*70)
    print("   💡 RECOMENDACIÓN FINAL")
    print("="*70 + "\n")

    best_score = sorted_results[0][1].overall_score
    best_name = sorted_results[0][0].name

    if best_name == "SQM Santiago - Ingeniero Senior":
        print("   🎉 SQM SANTIAGO ES LA MEJOR OPCIÓN\n")
        print("   Supera a todas las demás por:")
        print("   • Combina salario alto + WLB excelente")
        print("   • Santiago (familia, vida normal)")
        print("   • Prestigio máximo en Chile")
        print("   • Estabilidad y tecnología punta")
        print("   • Sin necesidad de plan temporal\n")

        print("   🎯 SIGUIENTE PASO:")
        print("   1. Preparar CV enfocado SQM")
        print("   2. Investigar posiciones abiertas")
        print("   3. Network con gente en SQM")
        print("   4. Aplicar en próximas 2-4 semanas\n")
    else:
        print(f"   🏆 Mejor opción: {best_name}\n")
        print(f"   SQM Santiago rank #{[x[0].name for x in sorted_results].index('SQM Santiago - Ingeniero Senior') + 1}\n")

    # Comparación SQM vs otras minería
    print("   📊 SQM vs Otras opciones minería:\n")
    mining_options = [(opt.name, res.overall_score) for opt, res in zip(options, results, strict=False)
                      if 'Minería' in opt.name or 'SQM' in opt.name]

    for name, score in sorted(mining_options, key=lambda x: x[1], reverse=True):
        marker = "✅" if score >= 4.0 else "⚠️" if score >= 3.0 else "❌"
        print(f"   {marker} {name}: {score:.2f}/10")

    print("\n" + "="*70 + "\n")

    return best_name, best_score


if __name__ == "__main__":
    winner, score = main()
    print(f"✨ Mejor opción: {winner} ({score:.2f}/10)\n")
