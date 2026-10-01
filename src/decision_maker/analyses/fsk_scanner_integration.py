"""
Decision Analysis - Integracion del FSK scanner Becker Varis
Purpose: Decidir donde vive la integracion del FSK scanner en el ecosistema de diagnostico remoto.
Created: 2026-06-25
Last Updated: 2026-10-01
Version: 2.0

CHANGES IN THIS VERSION:
- v1 no corria: pasaba `pros=` a un `CareerOption` que no lo acepta, importaba `core.` (ruta vieja) y
  llamaba `asyncio.run` dentro de un loop ya corriendo.
- Y aunque hubiera corrido, su Monte Carlo no media nada: no registraba ningun factor y modelaba
  protocolos con atributos de carrera (salario, burnout, prestigio). Lo unico real era la tabla de
  puntajes y pesos, que se conserva tal cual.
- Ahora la tabla alimenta el framework: un factor por criterio, cada puntaje con incertidumbre
  triangular +/-SCORE_SPREAD. La suma ponderada puntual se imprime al lado como control.

SUPUESTOS:
- Los puntajes 0..10 son juicio del autor (v1, 2026-06-25), no mediciones.
- SCORE_SPREAD = 1: un juicio 0..10 vale +/-1 punto. Es el unico numero que agrega v2.

NOTES:
- `pros`/`cons` quedan como datos para el lector; no entran al calculo.
- Escribe un JSON en results/fsk_scanner_integration/ (no versionado).
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

ANALYSIS_NAME = "fsk_scanner_integration"
TITLE = "INTEGRACION DEL FSK SCANNER BECKER VARIS"
SCALE_MIN, SCALE_MAX = 0.0, 10.0
SCORE_SPREAD = 1.0

ALTERNATIVES: list[dict[str, Any]] = [{'name': 'sw-vlad-dac-tools (Tauri Rust)',
  'description': 'Mantener todo en la app Rust/Tauri de escritorio. FSK scanner conectado a .101, '
                 'datos solo locales. Interfaz nativa, sin red. La app ya tiene protocolo V2 y tab '
                 'FSK Scanner.',
  'pros': ['Ya funciona', 'Sin dependencias externas', 'Simple'],
  'cons': ['Solo local', 'Sin integracion red', 'Duplica esfuerzo']},
 {'name': 'monitor-serial (Python RabbitMQ)',
  'description': 'Extender el monitor-serial Python existente para leer tramas V2 del fsk-scanner '
                 'via USB y publicarlas a RabbitMQ. Los datos quedan disponibles para cualquier '
                 'dashboard web. Ya tiene arquitectura de decodificadores plugin.',
  'pros': ['Datos en red', 'Reutiliza arquitectura existente', 'Escalable'],
  'cons': ['Requiere RabbitMQ', 'Mas componentes', 'Curva aprendizaje']},
 {'name': 'fw-diagnostico-remoto-vlad (firmware)',
  'description': 'Integrar FSK scanner directamente en el firmware STM32WB09. El chip ya tiene '
                 'SX1278 (LoRa+FSK) y BLE. Podria recibir tramas Becker directamente sin gateway '
                 'externo.',
  'pros': ['Integracion total', 'Sin HW extra', 'Elegante'],
  'cons': ['Riesgo alto', 'Complejo', 'Largo plazo']},
 {'name': 'Hybrid: fsk-scanner + monitor-serial',
  'description': 'fsk-scanner (STM32G474) conectado por USB a .101. monitor-serial lee tramas V2 '
                 'via serial y publica a RabbitMQ. Dashboard web consume datos. Combina firmware '
                 'probado + infraestructura existente. Lo mejor de ambos mundos.',
  'pros': ['Firmware ya funciona V2',
           'monitor-serial existente',
           'Datos en red',
           'Escalable',
           'Diagnostico y dashboard separados'],
  'cons': ['Requiere integracion', 'Dos sistemas que mantener']},
 {'name': 'Tauri + servidor HTTP embebido',
  'description': 'Extender el Tauri actual con un mini servidor HTTP/WS embebido (axum) ademas del '
                 'WebView. Los datos serial se comparten via WebSocket con otros clientes web en '
                 'la red. App hibrida desktop+web.',
  'pros': ['Un solo binario', 'Desktop + web', 'Moderno'],
  'cons': ['No probado', 'Complejidad media', 'Duplica con monitor-serial']}]

# Peso de cada criterio (suman 1). Todos son "mas alto es mejor".
WEIGHTS: dict[str, float] = {'speed': 0.2,
 'simplicity': 0.15,
 'robustness': 0.2,
 'diagnostics': 0.2,
 'improvement': 0.1,
 'scalability': 0.15}

# Juicio 0..10 por alternativa y criterio (mas alto es mejor).
SCORES: dict[str, dict[str, float]] = {'sw-vlad-dac-tools (Tauri Rust)': {'speed': 9,
                                    'simplicity': 9,
                                    'robustness': 8,
                                    'diagnostics': 7,
                                    'improvement': 4,
                                    'scalability': 2},
 'monitor-serial (Python RabbitMQ)': {'speed': 7,
                                      'simplicity': 6,
                                      'robustness': 8,
                                      'diagnostics': 7,
                                      'improvement': 8,
                                      'scalability': 9},
 'fw-diagnostico-remoto-vlad (firmware)': {'speed': 3,
                                           'simplicity': 3,
                                           'robustness': 5,
                                           'diagnostics': 5,
                                           'improvement': 9,
                                           'scalability': 8},
 'Hybrid: fsk-scanner + monitor-serial': {'speed': 8,
                                          'simplicity': 7,
                                          'robustness': 9,
                                          'diagnostics': 9,
                                          'improvement': 9,
                                          'scalability': 9},
 'Tauri + servidor HTTP embebido': {'speed': 5,
                                    'simplicity': 5,
                                    'robustness': 6,
                                    'diagnostics': 7,
                                    'improvement': 7,
                                    'scalability': 6}}


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
