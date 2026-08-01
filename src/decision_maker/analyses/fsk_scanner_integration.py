"""
Evaluacion de estrategia de integracion del FSK scanner Becker Varis
en el ecosistema de diagnostico remoto.
Date: 2026-06-25
"""
import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from core.deep_research_decision_agent import CareerOption, DecisionAnalysisEngine

alternatives = [
    CareerOption(
        name="sw-vlad-dac-tools (Tauri Rust)",
        description="Mantener todo en la app Rust/Tauri de escritorio. FSK scanner conectado a .101, datos solo locales. Interfaz nativa, sin red. La app ya tiene protocolo V2 y tab FSK Scanner.",
        salary_expected=0, probability_success=0.9, timeline_months=1,
        tech_growth=5, income_stability=7, work_life_balance=8, prestige=4,
        remote_flexibility=1, learning_opportunity=4, career_ceiling=3,
        unemployment_risk=0.05, burnout_risk=0.05, market_risk=0.1,
        pros=["Ya funciona", "Sin dependencias externas", "Simple"],
        cons=["Solo local", "Sin integracion red", "Duplica esfuerzo"],
    ),
    CareerOption(
        name="monitor-serial (Python RabbitMQ)",
        description="Extender el monitor-serial Python existente para leer tramas V2 del fsk-scanner via USB y publicarlas a RabbitMQ. Los datos quedan disponibles para cualquier dashboard web. Ya tiene arquitectura de decodificadores plugin.",
        salary_expected=0, probability_success=0.85, timeline_months=2,
        tech_growth=7, income_stability=6, work_life_balance=6, prestige=6,
        remote_flexibility=9, learning_opportunity=7, career_ceiling=8,
        unemployment_risk=0.1, burnout_risk=0.1, market_risk=0.1,
        pros=["Datos en red", "Reutiliza arquitectura existente", "Escalable"],
        cons=["Requiere RabbitMQ", "Mas componentes", "Curva aprendizaje"],
    ),
    CareerOption(
        name="fw-diagnostico-remoto-vlad (firmware)",
        description="Integrar FSK scanner directamente en el firmware STM32WB09. El chip ya tiene SX1278 (LoRa+FSK) y BLE. Podria recibir tramas Becker directamente sin gateway externo.",
        salary_expected=0, probability_success=0.5, timeline_months=4,
        tech_growth=9, income_stability=3, work_life_balance=3, prestige=8,
        remote_flexibility=5, learning_opportunity=9, career_ceiling=9,
        unemployment_risk=0.2, burnout_risk=0.3, market_risk=0.2,
        pros=["Integracion total", "Sin HW extra", "Elegante"],
        cons=["Riesgo alto", "Complejo", "Largo plazo"],
    ),
    CareerOption(
        name="Hybrid: fsk-scanner + monitor-serial",
        description="fsk-scanner (STM32G474) conectado por USB a .101. monitor-serial lee tramas V2 via serial y publica a RabbitMQ. Dashboard web consume datos. Combina firmware probado + infraestructura existente. Lo mejor de ambos mundos.",
        salary_expected=0, probability_success=0.9, timeline_months=1.5,
        tech_growth=7, income_stability=8, work_life_balance=7, prestige=7,
        remote_flexibility=9, learning_opportunity=6, career_ceiling=8,
        unemployment_risk=0.05, burnout_risk=0.05, market_risk=0.05,
        pros=["Firmware ya funciona V2", "monitor-serial existente", "Datos en red", "Escalable", "Diagnostico y dashboard separados"],
        cons=["Requiere integracion", "Dos sistemas que mantener"],
    ),
    CareerOption(
        name="Tauri + servidor HTTP embebido",
        description="Extender el Tauri actual con un mini servidor HTTP/WS embebido (axum) ademas del WebView. Los datos serial se comparten via WebSocket con otros clientes web en la red. App hibrida desktop+web.",
        salary_expected=0, probability_success=0.7, timeline_months=2.5,
        tech_growth=8, income_stability=5, work_life_balance=5, prestige=6,
        remote_flexibility=7, learning_opportunity=8, career_ceiling=6,
        unemployment_risk=0.1, burnout_risk=0.15, market_risk=0.1,
        pros=["Un solo binario", "Desktop + web", "Moderno"],
        cons=["No probado", "Complejidad media", "Duplica con monitor-serial"],
    ),
]

# Subjective scores per criteria (1-10, higher is better)
SCORES = {
    "sw-vlad-dac-tools (Tauri Rust)": {
        "speed": 9, "simplicity": 9, "robustness": 8,
        "diagnostics": 7, "improvement": 4, "scalability": 2,
    },
    "monitor-serial (Python RabbitMQ)": {
        "speed": 7, "simplicity": 6, "robustness": 8,
        "diagnostics": 7, "improvement": 8, "scalability": 9,
    },
    "fw-diagnostico-remoto-vlad (firmware)": {
        "speed": 3, "simplicity": 3, "robustness": 5,
        "diagnostics": 5, "improvement": 9, "scalability": 8,
    },
    "Hybrid: fsk-scanner + monitor-serial": {
        "speed": 8, "simplicity": 7, "robustness": 9,
        "diagnostics": 9, "improvement": 9, "scalability": 9,
    },
    "Tauri + servidor HTTP embebido": {
        "speed": 5, "simplicity": 5, "robustness": 6,
        "diagnostics": 7, "improvement": 7, "scalability": 6,
    },
}

WEIGHTS = {
    "speed": 0.20,
    "simplicity": 0.15,
    "robustness": 0.20,
    "diagnostics": 0.20,
    "improvement": 0.10,
    "scalability": 0.15,
}

async def main():
    print("=" * 60)
    print("EVALUACION ESTRATEGIA INTEGRACION FSK SCANNER")
    print("=" * 60)

    engine = DecisionAnalysisEngine()
    results = []

    for alt in alternatives:
        result = engine.analyze_option(alt, alternatives)
        results.append(result)
        s = engine._calculate_overall_score(result)
        print(f"\n{alt.name}:")
        print(f"  MC={result.monte_carlo_score:.3f}  Risk={result.risk_score:.3f}  Scenario={result.scenario_robustness:.3f}  Overall={s:.3f}")
        # Weighted subjective
        sc = SCORES[alt.name]
        ws = sum(WEIGHTS[k] * (sc[k] / 10.0) for k in WEIGHTS)
        print(f"  Subj: speed={sc['speed']} simplicity={sc['simplicity']} robust={sc['robustness']} "
              f"diag={sc['diagnostics']} improve={sc['improvement']} scale={sc['scalability']}")
        print(f"  Weighted subjective score: {ws:.3f}")

    overall = {r.option_name: engine._calculate_overall_score(r) for r in results}
    top = max(overall, key=overall.get)

    print("\n" + "=" * 60)
    print(f"RECOMENDACION ENGINE: {top} ({overall[top]:.3f})")
    print()

    # Subjective ranking
    print("--- Ranking Subjetivo (criterios tecnicos) ---")
    ranked = sorted(SCORES.keys(), key=lambda n: sum(WEIGHTS[k] * (SCORES[n][k] / 10.0) for k in WEIGHTS), reverse=True)
    for i, name in enumerate(ranked):
        ws = sum(WEIGHTS[k] * (SCORES[name][k] / 10.0) for k in WEIGHTS)
        print(f"  {i+1}. {name}: {ws:.3f}")

    output = {
        "date": datetime.now().isoformat(),
        "recommended": top,
        "engine_scores": {r.option_name: round(overall[r.option_name], 3) for r in results},
        "subjective_ranking": [(n, round(sum(WEIGHTS[k] * (SCORES[n][k] / 10.0) for k in WEIGHTS), 3)) for n in ranked],
    }
    output_dir = Path(__file__).parent.parent.parent / "results" / "fsk_scanner_integration"
    output_dir.mkdir(parents=True, exist_ok=True)
    with open(output_dir / f"eval_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", "w") as f:
        json.dump(output, f, indent=2)
    print("\nResultados guardados")

if __name__ == "__main__":
    asyncio.run(main())
