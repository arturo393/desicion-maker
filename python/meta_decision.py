#!/usr/bin/env python3
"""
🎯 DECISIÓN META: ¿Qué arquitectura elegir para el framework?

Usamos el propio framework para decidir qué hacer con él.
¡Meta-decisión paradójica!
"""

import sys
from pathlib import Path

# Add core to path
sys.path.insert(0, str(Path(__file__).parent / 'core'))

from deep_research_decision_agent import CareerOption, DecisionAnalysisEngine

def create_architecture_options():
    """Crear las 3 opciones de arquitectura como CareerOptions"""
    
    # OPCIÓN A: Super C++ (portar Python → C++)
    option_a = CareerOption(
        name="Opción A: Super C++ + Python solo Gemini",
        
        # Tiempo = inverso de meses (menos tiempo = mejor)
        salary_expected=2_000_000,  # 5-6 semanas ~ bajo "salario" (mucho trabajo)
        
        # Probabilidad de éxito
        probability_success=0.70,  # 70% - complejo pero factible
        
        # Timeline
        timeline_months=2,  # 6 semanas ≈ 1.5 meses
        
        # Factores (0-10)
        tech_growth=8.0,           # Aprendes C++ avanzado
        income_stability=6.0,       # Sistema robusto pero complejo
        work_life_balance=3.0,      # Mucho trabajo, debugging complejo
        prestige=9.0,               # Sistema profesional impresionante
        remote_flexibility=5.0,     # Necesitas compilar, menos flexible
        learning_opportunity=9.0,   # Aprendes mucho C++
        career_ceiling=9.0,         # Máximo potencial técnico
        
        # Riesgos
        unemployment_risk=0.3,      # 30% riesgo de abandonar (muy complejo)
        burnout_risk=0.5,           # 50% burnout (mucho trabajo)
        market_risk=0.2,            # 20% - C++ siempre útil
        
        description="Portar 13 metodologías Python a C++, mantener 5 avanzadas C++, Python solo para Gemini API. Resultado: 18 metodologías en C++ súper potente."
    )
    
    # OPCIÓN B: Super Python (portar C++ → Python)
    option_b = CareerOption(
        name="Opción B: Super Python (todo en Python)",
        
        # Tiempo
        salary_expected=4_000_000,  # 2-3 semanas ~ alto "salario" (menos trabajo)
        
        # Probabilidad de éxito
        probability_success=0.90,  # 90% - más simple, ya sabes Python
        
        # Timeline
        timeline_months=1,  # 2-3 semanas < 1 mes
        
        # Factores (0-10)
        tech_growth=7.0,           # Mejoras Python skills
        income_stability=8.0,       # Un solo lenguaje = más estable
        work_life_balance=9.0,      # Rápido de implementar, menos stress
        prestige=7.0,               # Buen sistema pero no "hardcore"
        remote_flexibility=9.0,     # No compilar, uv run anywhere
        learning_opportunity=7.0,   # Aprendes metodologías avanzadas
        career_ceiling=7.5,         # Buen potencial, limitado por Python
        
        # Riesgos
        unemployment_risk=0.1,      # 10% - fácil de completar
        burnout_risk=0.2,           # 20% - trabajo moderado
        market_risk=0.15,           # 15% - Python muy usado
        
        description="Portar 5 metodologías avanzadas C++ a Python, mantener 13 simples Python, Gemini ya integrado. Resultado: 18 metodologías en Python + IA."
    )
    
    # OPCIÓN C: Híbrido (Python orquesta + C++ motor)
    option_c = CareerOption(
        name="Opción C: Híbrido Python + C++",
        
        # Tiempo
        salary_expected=3_000_000,  # 2-3 semanas ~ medio
        
        # Probabilidad de éxito
        probability_success=0.75,  # 75% - bridge puede ser tricky
        
        # Timeline
        timeline_months=1,  # 2-3 semanas
        
        # Factores (0-10)
        tech_growth=8.5,           # Aprendes ambos + integración
        income_stability=6.5,       # Dos sistemas = más frágil
        work_life_balance=5.0,      # Debugging en 2 lenguajes
        prestige=8.5,               # Arquitectura profesional
        remote_flexibility=6.0,     # Necesitas compilar C++
        learning_opportunity=8.5,   # Aprendes arquitectura compleja
        career_ceiling=9.0,         # Máxima flexibilidad futura
        
        # Riesgos
        unemployment_risk=0.25,     # 25% - bridge puede fallar
        burnout_risk=0.35,          # 35% - mantener 2 sistemas
        market_risk=0.2,            # 20% - ambos lenguajes útiles
        
        description="Python para Gemini + orquestación, C++ para análisis pesado. CLI C++ + wrapper Python. Lo mejor de ambos mundos pero más complejo."
    )
    
    return [option_a, option_b, option_c]


def main():
    """Ejecutar análisis de decisión"""
    print("\n" + "="*70)
    print("   🎯 DECISIÓN META: ¿Qué arquitectura elegir?")
    print("   (Usando el propio framework para decidir)")
    print("="*70 + "\n")
    
    # Crear opciones
    options = create_architecture_options()
    
    print("📋 Opciones a evaluar:\n")
    for i, opt in enumerate(options, 1):
        print(f"{i}. {opt.name}")
        print(f"   {opt.description[:80]}...")
        print()
    
    # Inicializar engine
    print("🔄 Ejecutando análisis con 13 metodologías...\n")
    engine = DecisionAnalysisEngine(debug=False)
    
    # Analizar cada opción
    results = []
    for option in options:
        result = engine.analyze_option(option, options)
        results.append(result)
    
    # Mostrar resultados
    print("\n" + "="*70)
    print("   📊 RESULTADOS DEL ANÁLISIS")
    print("="*70 + "\n")
    
    # Ordenar por overall_score
    sorted_results = sorted(zip(options, results), 
                          key=lambda x: x[1].overall_score, 
                          reverse=True)
    
    for rank, (option, result) in enumerate(sorted_results, 1):
        print(f"{'🥇' if rank == 1 else '🥈' if rank == 2 else '🥉'} RANK {rank}: {option.name}")
        print(f"\n   📊 Scores:")
        print(f"   - Overall Score:      {result.overall_score:.2f}/10")
        print(f"   - Monte Carlo:        {result.monte_carlo_score:.2f}")
        print(f"   - TOPSIS Rank:        #{result.topsis_rank}")
        print(f"   - Pareto Optimal:     {'✅ Sí' if result.pareto_optimal else '❌ No'}")
        print(f"   - Risk Score:         {result.risk_score:.2f} (menor = mejor)")
        print(f"   - Scenario Robust:    {result.scenario_robustness:.2f}")
        print(f"   - Confidence:         {result.confidence*100:.1f}%")
        
        print(f"\n   💡 Recomendación:")
        print(f"   {result.recommendation}")
        print("\n" + "-"*70 + "\n")
    
    # Decisión final
    winner = sorted_results[0]
    winner_option = winner[0]
    winner_result = winner[1]
    
    print("="*70)
    print("   ✅ DECISIÓN FINAL (según el framework)")
    print("="*70)
    print(f"\n   🏆 GANADOR: {winner_option.name}")
    print(f"   📊 Score: {winner_result.overall_score:.2f}/10")
    print(f"   🎯 Confianza: {winner_result.confidence*100:.1f}%")
    print(f"\n   📝 Razón:")
    print(f"   {winner_result.recommendation}")
    
    # Análisis adicional
    print(f"\n   🔍 Análisis detallado:")
    print(f"   - Timeline: {winner_option.timeline_months} mes(es)")
    print(f"   - Probabilidad éxito: {winner_option.probability_success*100:.0f}%")
    print(f"   - Work-Life Balance: {winner_option.work_life_balance}/10")
    print(f"   - Flexibilidad: {winner_option.remote_flexibility}/10")
    print(f"   - Riesgo burnout: {winner_option.burnout_risk*100:.0f}%")
    
    print("\n" + "="*70 + "\n")
    
    # Meta-reflexión
    print("🤔 Meta-reflexión:")
    print("   El framework de decisiones analizó su propia arquitectura.")
    print("   La paradoja es hermosa: usamos la herramienta para decidir")
    print("   qué hacer con la herramienta. Y tiene sentido matemático.")
    print("\n" + "="*70 + "\n")
    
    return winner_option.name


if __name__ == "__main__":
    winner = main()
    print(f"✨ Resultado: {winner}\n")
