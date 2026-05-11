#!/usr/bin/env python3
"""
🖨️ DECISIÓN: ¿Web Print Service (Docker) vs Network Printer Sharing?

Contexto: Arturo está en Windows, la impresora HP Smart Tank 520 está conectada
a una máquina Linux (Ubuntu 24.04) en 192.168.1.149. Quiere imprimir PDFs
desde Windows/cualquier dispositivo.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'core'))

from deep_research_decision_agent import CareerOption, DecisionAnalysisEngine

def create_options():
    # OPCIÓN A: Web Print Service con Docker + React/Tailwind
    option_a = CareerOption(
        name="Web Print Service (Docker + React + CUPS API)",
        salary_expected=9_000_000,  # Alto valor/utilidad: control total, multi-usuario, preview, historial
        probability_success=0.88,
        timeline_months=1,  # ~1-2 días de setup
        tech_growth=9.0,           # Moderno, extensible
        income_stability=9.0,      # Servicio estable, persistente
        work_life_balance=8.0,     # Una vez hecho, funciona solo
        prestige=9.0,              # Solución profesional
        remote_flexibility=10.0,   # Accesible desde cualquier dispositivo en red
        learning_opportunity=8.0,  # React, Docker, CUPS API
        career_ceiling=9.0,        # Extensible: historial, múltiples impresoras, auth
        unemployment_risk=0.12,    # Bajo: Docker abstrae complejidad
        burnout_risk=0.15,         # Bajo: arquitectura clara
        market_risk=0.05,          # Docker muy estable
        description="""
        Solución completa: Docker compose con backend Python/FastAPI que habla
        con CUPS via SSH o API local, frontend React + Tailwind con preview PDF,
        selección de tamaño/color, historial de impresiones.
        WCAG AAA accesible, responsive, PWA-ready.
        Se instala como systemd service o docker-compose con restart:always.
        Pros: preview antes de imprimir, control de opciones, multi-usuario,
        historial, accesible desde móvil, extensible.
        Contras: más setup inicial (~2-3h), requiere Docker en Linux server.
        """,
        pros=[
            "Preview del PDF antes de imprimir",
            "Control de tamaño, color, copias",
            "Accesible desde cualquier dispositivo (móvil, tablet, otro PC)",
            "Historial de impresiones",
            "Multi-usuario con autenticación opcional",
            "Interfaz profesional WCAG AAA",
            "Extensible: agregar más impresoras, workflows",
            "Servicio permanente con auto-restart",
        ],
        cons=[
            "Mayor setup inicial (2-3 horas)",
            "Requiere Docker en el servidor Linux",
            "Más complejidad técnica",
        ]
    )

    # OPCIÓN B: Compartir impresora en red vía CUPS (IPP/Bonjour)
    option_b = CareerOption(
        name="Network Printer Sharing (CUPS IPP/Bonjour)",
        salary_expected=4_000_000,  # Menor valor: funciona pero sin preview ni control fino
        probability_success=0.80,
        timeline_months=1,  # ~30 min de setup
        tech_growth=3.0,           # Poco nuevo
        income_stability=6.0,      # Depende de que Windows detecte la impresora
        work_life_balance=9.0,     # Setup muy rápido
        prestige=4.0,              # Solución básica
        remote_flexibility=6.0,    # Solo en red local, sin UI web
        learning_opportunity=2.0,  # Poco que aprender
        career_ceiling=3.0,        # No extensible, no escalable
        unemployment_risk=0.20,    # Windows puede tener problemas con driver Linux
        burnout_risk=0.10,
        market_risk=0.25,          # Depende de compatibilidad drivers Windows/Linux
        description="""
        Exponer CUPS como impresora de red IPP. Windows la detecta como impresora
        de red. Simple pero: sin preview, sin selección avanzada de opciones,
        depende de que Windows instale el driver correcto para HP Smart Tank,
        no hay historial, solo en red local.
        Pros: setup en 30 min, sin código.
        Contras: sin preview, sin opciones avanzadas, puede fallar con drivers,
        no accesible fuera de LAN, no extensible.
        """,
        pros=[
            "Setup rapidísimo (30 minutos)",
            "Sin código que mantener",
            "Nativo en el OS",
        ],
        cons=[
            "Sin preview del PDF",
            "Sin control de opciones (tamaño, color)",
            "Puede fallar con drivers en Windows",
            "Solo en red local (no web)",
            "Sin historial",
            "No extensible",
            "Windows necesita instalar driver HP manualmente",
        ]
    )

    return [option_a, option_b]

def main():
    print("=" * 70)
    print("🖨️  DECISIÓN: Solución de impresión desde Windows")
    print("=" * 70)
    print("Contexto: HP Smart Tank 520 en Ubuntu 24.04 (192.168.1.149)")
    print("Objetivo: Imprimir PDFs desde Windows con preview y control")
    print("=" * 70)

    options = create_options()
    engine = DecisionAnalysisEngine(debug=False)

    results = []
    for opt in options:
        print(f"\n📊 Analizando: {opt.name}")
        result = engine.analyze_option(opt, options)
        results.append(result)

    # Mostrar resultados
    print("\n" + "=" * 70)
    print("📈 RESULTADOS DEL ANÁLISIS (13 metodologías)")
    print("=" * 70)

    results_sorted = sorted(results, key=lambda r: r.overall_score, reverse=True)

    for i, result in enumerate(results_sorted):
        rank_emoji = "🥇" if i == 0 else "🥈"
        print(f"\n{rank_emoji} #{i+1}: {result.option_name}")
        print(f"   Overall Score:       {result.overall_score:.4f}")
        print(f"   Monte Carlo:         {result.monte_carlo_score:.4f}")
        print(f"   TOPSIS Rank:         #{result.topsis_rank}")
        print(f"   Pareto Optimal:      {'✅ SÍ' if result.pareto_optimal else '❌ NO'}")
        print(f"   Regret (minimax):    {result.regret_analysis:.4f}")
        print(f"   Risk Score:          {result.risk_score:.4f}")
        print(f"   Scenario Robustness: {result.scenario_robustness:.4f}")
        print(f"   Confidence:          {result.confidence:.1%}")
        print(f"   Recommendation:      {result.recommendation}")

    winner = results_sorted[0]
    print("\n" + "=" * 70)
    print("🎯 DECISIÓN FINAL")
    print("=" * 70)
    print(f"✅ GANADOR: {winner.option_name}")
    print(f"   Confianza: {winner.confidence:.1%}")
    print(f"   Score: {winner.overall_score:.4f} vs {results_sorted[1].overall_score:.4f}")
    print()

    if "Docker" in winner.option_name or "Web" in winner.option_name:
        print("📋 PLAN DE IMPLEMENTACIÓN:")
        print("   1. Crear Dockerfile + docker-compose en servidor Linux")
        print("   2. Backend FastAPI: recibe PDF, llama lp/CUPS")
        print("   3. Frontend React + Tailwind: upload, preview, opciones")
        print("   4. Systemd service para auto-start permanente")
        print("   5. Puerto libre (ej: 8765)")
    else:
        print("📋 PLAN DE IMPLEMENTACIÓN:")
        print("   1. Habilitar CUPS IPP en servidor Linux")
        print("   2. Agregar impresora de red en Windows")
        print("   3. Instalar driver HP en Windows si necesario")

    return winner

if __name__ == "__main__":
    main()
