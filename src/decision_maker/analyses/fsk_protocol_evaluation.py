"""
Protocolo de Comunicacion FSK - Evaluacion de Alternativas
Proposito: Evaluar alternativas de protocolo serial para reemplazar el protocolo
legacy 0x7E/0x7F del fsk-scanner (fw-gateway2Lora).
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
        name="VLAD25-V2 (CMD+DATA raw)",
        description="Formato minimal: [CMD][DATA...]. Sin framing, sin CRC, sin campos de modulo. 0 bytes overhead. Timeout-based framing. Inspirado en fw-vlad25 V2.",
        salary_expected=0, probability_success=0.9, timeline_months=1,
        tech_growth=8, income_stability=5, work_life_balance=7, prestige=4,
        remote_flexibility=5, learning_opportunity=6, career_ceiling=7,
        unemployment_risk=0.1, burnout_risk=0.1, market_risk=0.1,
        pros=["Overhead 0", "Ya probado en produccion", "Facil migracion"],
        cons=["Sin deteccion errores", "Timeout-based framing"],
    ),
    CareerOption(
        name="Simple-framed (0x7E CMD LEN DATA 0x7F)",
        description="[0x7E][CMD][LEN][DATA...][0x7F]. Sin CRC, sin reserved byte, sin module fields. 4 bytes overhead. Framing explicito.",
        salary_expected=0, probability_success=0.85, timeline_months=1,
        tech_growth=5, income_stability=5, work_life_balance=8, prestige=3,
        remote_flexibility=5, learning_opportunity=4, career_ceiling=5,
        unemployment_risk=0.1, burnout_risk=0.1, market_risk=0.1,
        pros=["Framing explicito", "Bajo overhead", "Facil extraer frames"],
        cons=["Nuevo formato, sin testear"],
    ),
    CareerOption(
        name="COBS+TLV",
        description="COBS stuffing + Type-Length-Value. Sin bytes reservados. Overhead variable 1-255 bytes. Maxima extensibilidad.",
        salary_expected=0, probability_success=0.6, timeline_months=3,
        tech_growth=9, income_stability=3, work_life_balance=4, prestige=7,
        remote_flexibility=3, learning_opportunity=8, career_ceiling=9,
        unemployment_risk=0.2, burnout_risk=0.3, market_risk=0.15,
        pros=["Extensible", "Sin bytes reservados", "Elegante"],
        cons=["Complejo firmware+host", "Overhead variable", "No probado"],
    ),
    CareerOption(
        name="JSON-newline",
        description='{"cmd":"start_scan"}\\n. Maxima legibilidad humana. Debuggable con cualquier terminal serie.',
        salary_expected=0, probability_success=0.75, timeline_months=2,
        tech_growth=6, income_stability=4, work_life_balance=9, prestige=5,
        remote_flexibility=5, learning_opportunity=5, career_ceiling=4,
        unemployment_risk=0.1, burnout_risk=0.1, market_risk=0.1,
        pros=["Legible", "Debuggable", "Estandar"],
        cons=["Overhead ~20 bytes", "Lento en MCU", "Fragil en embedded"],
    ),
    CareerOption(
        name="Legacy limpiado (con CRC)",
        description="[0x7E][CMD][LEN_H][LEN_L][DATA...][CRC][0x7F]. Protocolo actual sin reserved byte ni module fields. 7 bytes overhead. Mantiene CRC.",
        salary_expected=0, probability_success=0.8, timeline_months=1,
        tech_growth=3, income_stability=6, work_life_balance=7, prestige=2,
        remote_flexibility=5, learning_opportunity=3, career_ceiling=3,
        unemployment_risk=0.1, burnout_risk=0.1, market_risk=0.1,
        pros=["CRC incluido", "Cambio minimo", "Familiar"],
        cons=["Sigue siendo complejo", "7 bytes overhead"],
    ),
]

CRITERIA_WEIGHTS = {
    "firmware_complexity": 0.20,
    "host_complexity": 0.15,
    "overhead_bytes": 0.10,
    "debuggability": 0.15,
    "extensibility": 0.10,
    "migration_ease": 0.10,
    "proven_in_production": 0.10,
    "wire_efficiency": 0.10,
}

SUBJECTIVE_SCORES = {
    "VLAD25-V2 (CMD+DATA raw)": {
        "firmware_complexity": 9, "host_complexity": 7,
        "overhead_bytes": 10, "debuggability": 3,
        "extensibility": 3, "migration_ease": 9,
        "proven_in_production": 8, "wire_efficiency": 10,
    },
    "Simple-framed (0x7E CMD LEN DATA 0x7F)": {
        "firmware_complexity": 8, "host_complexity": 9,
        "overhead_bytes": 7, "debuggability": 7,
        "extensibility": 5, "migration_ease": 9,
        "proven_in_production": 2, "wire_efficiency": 7,
    },
    "COBS+TLV": {
        "firmware_complexity": 3, "host_complexity": 4,
        "overhead_bytes": 6, "debuggability": 4,
        "extensibility": 9, "migration_ease": 3,
        "proven_in_production": 1, "wire_efficiency": 8,
    },
    "JSON-newline": {
        "firmware_complexity": 5, "host_complexity": 9,
        "overhead_bytes": 2, "debuggability": 10,
        "extensibility": 10, "migration_ease": 6,
        "proven_in_production": 7, "wire_efficiency": 2,
    },
    "Legacy limpiado (con CRC)": {
        "firmware_complexity": 7, "host_complexity": 8,
        "overhead_bytes": 5, "debuggability": 5,
        "extensibility": 4, "migration_ease": 6,
        "proven_in_production": 6, "wire_efficiency": 5,
    },
}

def compute_weighted_score(name: str) -> dict:
    scores = SUBJECTIVE_SCORES[name]
    weighted = sum(CRITERIA_WEIGHTS[k] * (scores[k] / 10.0) for k in CRITERIA_WEIGHTS)
    return {"name": name, "weighted_score": round(weighted, 4), "scores": scores}

async def main():
    print("=" * 60)
    print("EVALUACION DE PROTOCOLO FSK")
    print("=" * 60)

    engine = DecisionAnalysisEngine()
    results = []

    for alt in alternatives:
        result = engine.analyze_option(alt, alternatives)
        results.append(result)
        print(f"\n{alt.name}:")
        print(f"  Monte Carlo: {result.monte_carlo_score:.4f}")
        print(f"  Risk Score:  {result.risk_score:.4f}")
        print(f"  Regret:      {result.regret_analysis:.4f}")
        print(f"  Scenario:    {result.scenario_robustness:.4f}")
        overall = engine._calculate_overall_score(result)
        print(f"  Overall:     {overall:.4f}")

    scores = {r.option_name: engine._calculate_overall_score(r) for r in results}
    top_name = max(scores, key=scores.get)
    print("\n" + "=" * 60)
    print(f"RECOMENDACION: {top_name} (score: {scores[top_name]:.4f})")
    for r in results:
        s = engine._calculate_overall_score(r)
        print(f"  {r.option_name}: overall={s:.4f}, mc={r.monte_carlo_score:.4f}, risk={r.risk_score:.4f}")

    # Weighted subjective ranking
    print("\n--- Ranking Subjetivo (criterios tecnicos) ---")
    ranked = sorted(alternatives, key=lambda a: CRITERIA_WEIGHTS["firmware_complexity"] * (SUBJECTIVE_SCORES[a.name]["firmware_complexity"]/10), reverse=True)
    for i, a in enumerate(ranked):
        ws = compute_weighted_score(a.name)
        print(f"  {i+1}. {a.name}: {ws['weighted_score']:.4f}")

    # Save results
    output = {
        "date": datetime.now().isoformat(),
        "recommended": top_name,
        "results": [{"name": r.option_name, "overall": engine._calculate_overall_score(r), "mc": r.monte_carlo_score, "risk": r.risk_score} for r in results],
    }
    output_dir = Path(__file__).parent.parent.parent / "results" / "fsk_protocol_evaluation"
    output_dir.mkdir(parents=True, exist_ok=True)
    with open(output_dir / f"evaluation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", "w") as f:
        json.dump(output, f, indent=2)
    print("\nResultados guardados")

if __name__ == "__main__":
    asyncio.run(main())
