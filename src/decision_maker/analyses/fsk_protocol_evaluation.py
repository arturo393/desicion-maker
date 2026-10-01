"""
Decision Analysis - Protocolo de comunicacion FSK
Purpose: Elegir el protocolo serial que reemplaza al legacy 0x7E/0x7F del fsk-scanner
         (fw-gateway2Lora).
Created: 2026-06-25
Last Updated: 2026-10-01
Version: 2.0

CHANGES IN THIS VERSION:
- v1 no corria: pasaba `pros=` a un `CareerOption` que no lo acepta, importaba `core.` (ruta vieja) y
  llamaba `asyncio.run` dentro de un loop ya corriendo.
- Y aunque hubiera corrido, su Monte Carlo no media nada: no registraba ningun factor y modelaba
  protocolos con atributos de carrera (salario, burnout, prestigio). Lo unico real era la tabla de
  puntajes y pesos, que se conserva tal cual. El "ranking subjetivo" de v1 ordenaba solo por firmware_complexity e imprimia
  la suma ponderada al lado: el orden y los numeros no coincidian.
- Ahora la tabla alimenta el framework: un factor por criterio, cada puntaje con incertidumbre
  triangular +/-SCORE_SPREAD. La suma ponderada puntual se imprime al lado como control.

SUPUESTOS:
- Los puntajes 0..10 son juicio del autor (v1, 2026-06-25), no mediciones.
- SCORE_SPREAD = 1: un juicio 0..10 vale +/-1 punto. Es el unico numero que agrega v2.

NOTES:
- `pros`/`cons` quedan como datos para el lector; no entran al calculo.
- Escribe un JSON en results/fsk_protocol_evaluation/ (no versionado).
"""

import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from decision_maker.core.models import (  # noqa: E402
    DecisionOption,
    DistributionType,
    Factor,
    UncertainVariable,
)
from decision_maker.core.orchestrator import UnifiedDecisionFramework  # noqa: E402

ANALYSIS_NAME = "fsk_protocol_evaluation"
TITLE = "PROTOCOLO DE COMUNICACION FSK"
SCALE_MIN, SCALE_MAX = 0.0, 10.0
SCORE_SPREAD = 1.0

ALTERNATIVES: list[dict[str, Any]] = [{'name': 'VLAD25-V2 (CMD+DATA raw)',
  'description': 'Formato minimal: [CMD][DATA...]. Sin framing, sin CRC, sin campos de modulo. 0 '
                 'bytes overhead. Timeout-based framing. Inspirado en fw-vlad25 V2.',
  'pros': ['Overhead 0', 'Ya probado en produccion', 'Facil migracion'],
  'cons': ['Sin deteccion errores', 'Timeout-based framing']},
 {'name': 'Simple-framed (0x7E CMD LEN DATA 0x7F)',
  'description': '[0x7E][CMD][LEN][DATA...][0x7F]. Sin CRC, sin reserved byte, sin module fields. '
                 '4 bytes overhead. Framing explicito.',
  'pros': ['Framing explicito', 'Bajo overhead', 'Facil extraer frames'],
  'cons': ['Nuevo formato, sin testear']},
 {'name': 'COBS+TLV',
  'description': 'COBS stuffing + Type-Length-Value. Sin bytes reservados. Overhead variable 1-255 '
                 'bytes. Maxima extensibilidad.',
  'pros': ['Extensible', 'Sin bytes reservados', 'Elegante'],
  'cons': ['Complejo firmware+host', 'Overhead variable', 'No probado']},
 {'name': 'JSON-newline',
  'description': '{"cmd":"start_scan"}\\n. Maxima legibilidad humana. Debuggable con cualquier '
                 'terminal serie.',
  'pros': ['Legible', 'Debuggable', 'Estandar'],
  'cons': ['Overhead ~20 bytes', 'Lento en MCU', 'Fragil en embedded']},
 {'name': 'Legacy limpiado (con CRC)',
  'description': '[0x7E][CMD][LEN_H][LEN_L][DATA...][CRC][0x7F]. Protocolo actual sin reserved '
                 'byte ni module fields. 7 bytes overhead. Mantiene CRC.',
  'pros': ['CRC incluido', 'Cambio minimo', 'Familiar'],
  'cons': ['Sigue siendo complejo', '7 bytes overhead']}]

# Peso de cada criterio (suman 1). Todos son "mas alto es mejor".
WEIGHTS: dict[str, float] = {'firmware_complexity': 0.2,
 'host_complexity': 0.15,
 'overhead_bytes': 0.1,
 'debuggability': 0.15,
 'extensibility': 0.1,
 'migration_ease': 0.1,
 'proven_in_production': 0.1,
 'wire_efficiency': 0.1}

# Juicio 0..10 por alternativa y criterio (mas alto es mejor).
SCORES: dict[str, dict[str, float]] = {'VLAD25-V2 (CMD+DATA raw)': {'firmware_complexity': 9,
                              'host_complexity': 7,
                              'overhead_bytes': 10,
                              'debuggability': 3,
                              'extensibility': 3,
                              'migration_ease': 9,
                              'proven_in_production': 8,
                              'wire_efficiency': 10},
 'Simple-framed (0x7E CMD LEN DATA 0x7F)': {'firmware_complexity': 8,
                                            'host_complexity': 9,
                                            'overhead_bytes': 7,
                                            'debuggability': 7,
                                            'extensibility': 5,
                                            'migration_ease': 9,
                                            'proven_in_production': 2,
                                            'wire_efficiency': 7},
 'COBS+TLV': {'firmware_complexity': 3,
              'host_complexity': 4,
              'overhead_bytes': 6,
              'debuggability': 4,
              'extensibility': 9,
              'migration_ease': 3,
              'proven_in_production': 1,
              'wire_efficiency': 8},
 'JSON-newline': {'firmware_complexity': 5,
                  'host_complexity': 9,
                  'overhead_bytes': 2,
                  'debuggability': 10,
                  'extensibility': 10,
                  'migration_ease': 6,
                  'proven_in_production': 7,
                  'wire_efficiency': 2},
 'Legacy limpiado (con CRC)': {'firmware_complexity': 7,
                               'host_complexity': 8,
                               'overhead_bytes': 5,
                               'debuggability': 5,
                               'extensibility': 4,
                               'migration_ease': 6,
                               'proven_in_production': 6,
                               'wire_efficiency': 5}}


def _option(alt: dict[str, Any]) -> DecisionOption:
    """Each 0..10 judgement becomes a triangular (s-SPREAD, s, s+SPREAD), clipped to the scale."""
    variables = {}
    for criterion, s in SCORES[alt["name"]].items():
        lo, hi = max(SCALE_MIN, s - SCORE_SPREAD), min(SCALE_MAX, s + SCORE_SPREAD)
        variables[criterion] = UncertainVariable(criterion, DistributionType.TRIANGULAR, [lo, s, hi])
    return DecisionOption(name=alt["name"], description=alt["description"], variables=variables)


def weighted_score(name: str) -> float:
    """Deterministic weighted sum of the point judgements: the cross-check for the MC ranking."""
    return sum(WEIGHTS[k] * SCORES[name][k] / SCALE_MAX for k in WEIGHTS)


async def main() -> None:
    if abs(sum(WEIGHTS.values()) - 1.0) > 1e-9:
        raise ValueError(f"weights sum to {sum(WEIGHTS.values())}, not 1")
    if {a["name"] for a in ALTERNATIVES} != set(SCORES):
        raise ValueError("every alternative needs a row in SCORES, and only those")
    fw = UnifiedDecisionFramework()
    for criterion, w in WEIGHTS.items():
        fw.add_factor(Factor(criterion, weight=w, maximize=True))  # every score is higher-is-better
    for alt in ALTERNATIVES:
        fw.add_option(_option(alt))
    r = await fw.run_analysis(mode="standard")

    mc = r["mc_results"]
    topsis = r.get("topsis_scores")
    ranked = sorted(mc.items(), key=lambda kv: kv[1].mean_score, reverse=True)
    print("=" * 96)
    print(f"  {TITLE}")
    print("=" * 96)
    print(f"  {'#':<3} {'Opcion':<44} {'p5':>7} {'mean':>7} {'p95':>7} {'TOPSIS':>7} {'pond.':>7}")
    for i, (n, st) in enumerate(ranked, 1):
        t = float(topsis.get(n, float("nan"))) if topsis is not None and len(topsis) else float("nan")
        print(f"  {i:<3} {n[:44]:<44} {st.percentile_5:>7.3f} {st.mean_score:>7.3f} "
              f"{st.percentile_95:>7.3f} {t:>7.3f} {weighted_score(n):>7.3f}")
    winner = ranked[0][0]
    by_weights = max(SCORES, key=weighted_score)
    print(f"\n  Ganador (media MC): {winner}")
    if by_weights != winner:
        print(f"  OJO: la suma ponderada de los puntajes puntuales elige otra: {by_weights}")
    print(f"  Estrategias: {r.get('strategies')}")
    print(f"  Pareto dominadas: {r.get('pareto', {}).get('dominated_options')}")

    output = {
        "date": datetime.now().isoformat(),
        "analysis": ANALYSIS_NAME,
        "recommended": winner,
        "recommended_by_weighted_sum": by_weights,
        "score_spread": SCORE_SPREAD,
        "results": {
            n: {"mean": st.mean_score, "p5": st.percentile_5, "p95": st.percentile_95,
                "weighted_sum": weighted_score(n)}
            for n, st in ranked
        },
    }
    out_dir = REPO / "results" / ANALYSIS_NAME
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"eval_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    path.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n  Resultados: {path.relative_to(REPO)}")


if __name__ == "__main__":
    asyncio.run(main())
