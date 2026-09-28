#!/usr/bin/env python3
"""
Título: Análisis estocástico — Refactor de CommandMessage (protocolo RDSS del gateway)
Propósito: Decidir entre (A) dejar igual, (B) refactor conservador, (C) eliminar+reimpl,
           (D) híbrido codec-puro + allowlist en llamador. Bajo incertidumbre de
           "romper el cable" al reescribir.
Creado: 2026-08-23
Versión: 1.0

CONTEXTO VERIFICADO EN CÓDIGO (no asumido):
- CommandMessage.cpp hoy: 350 líns, SIN heap (uint8_t message[MAX_FRAME_SIZE]).
  Compila con -Werror en gateway.
- API viva usada por ComandosGateway.cpp: validate(), getCommandId(), getDataAsUint8(),
  freqDecode(), composeAndSendMessage(), reset(). También external: setCommandId(5),
  getDataAsUint32(6). Las demás (isReady, isListening, setVars, .ready/.listening,
  OperationMode, getLastMessageTrace, saveMessageTrace, last_message_buffer,
  isQueryParameter*, isSetPout*, setModuleFunction/Id, getModuleFunction/Id,
  getDataAsUint16, getDataAsFloat, getMaxSize/setMaxSize) -> 0 refs externas: MUERTO.
- Miembros muertos (nunca leídos/escritos en camino vivo): cmd, buff, buffSize,
  crc_calculated, crc_received, id_query, id_received, id, status, last_status,
  query_buffer[30], last_update_ticks, num_byte_data, data_frame, listening, ready.
- ENABLE_CRC_VALIDATION = 0: el CRC se TRANSMITE (crc_get en compose) pero NO se
  VERIFICA al recibir. EL FIRMWARE DESPLEGADO (-simple) TAMBIÉN lo tiene en 0:
  por tanto "no validar CRC rx" es el comportamiento de terreno (decision 2: hablar
  igual). El refactor NO debe cambiar eso salvo decisión consciente y testeada.
- Allowlist checkModule (byte-exacta al -simple, alineada 20-Ago):
  rangos 0x20-0x28, 0xB0-0xB9, 0x50-0x53, 0xD0-0xD3, 0x70-0x7C;
  singletons 0x30,0x60,0x80,0x81,0xF0,0xF1. 0x10 y 0xBB -> RETRANSMIT.
- Test host Tier-2 existente: test_commandmessage_host.cpp, 15 checks verdes.
  Fija framing/CRC/allowlist/getDataAsUint8. Debe seguir verde.
"""

import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent))

from decision_maker.core.models import DecisionOption, DistributionType, Factor, UncertainVariable

# ============================================================
# CRITERIOS (pesos suman 1.0). Escala 0-10, maximize=True salvo costos.
#   SeguridadCable      = probabilidad de PRESERVAR el cable exacto (mayor=menor riesgo)
#   CumplimientoFundacion = heap-free, -Werror, test Tier-2, honestidad de verificación
#   Mantenibilidad      = simplicidad / un-propósito / sin estado muerto
#   Verificabilidad     = confianza de validar con host tests sin banco
#   Reutilizacion       = el codec puede usarse en otro módulo
#   BajoEsfuerzo        = menor esfuerzo de implementación (mayor=menos esfuerzo)
# ============================================================

factors = [
    Factor("SeguridadCable", weight=0.30, maximize=True),
    Factor("CumplimientoFundacion", weight=0.20, maximize=True),
    Factor("Mantenibilidad", weight=0.20, maximize=True),
    Factor("Verificabilidad", weight=0.10, maximize=True),
    Factor("Reutilizacion", weight=0.05, maximize=True),
    Factor("BajoEsfuerzo", weight=0.15, maximize=True),
]

# Cada opción: media±std por criterio (NORMAL). Las std capturan la incertidumbre
# de juicio (p.ej. cuánto riesgo real de romper el cable al reescribir).
options = [
    DecisionOption(
        name="A: Dejar como está",
        description="Status quo. Heap-free y -Werror OK, pero estado muerto + "
                    "ENABLE_CRC_VALIDATION 0 (CRC rx no se verifica).",
        variables={
            "SeguridadCable": UncertainVariable("SeguridadCable", DistributionType.NORMAL, [10.0, 0.2]),
            "CumplimientoFundacion": UncertainVariable("CumplimientoFundacion", DistributionType.NORMAL, [6.0, 1.0]),
            "Mantenibilidad": UncertainVariable("Mantenibilidad", DistributionType.NORMAL, [2.0, 0.5]),
            "Verificabilidad": UncertainVariable("Verificabilidad", DistributionType.NORMAL, [8.0, 1.0]),
            "Reutilizacion": UncertainVariable("Reutilizacion", DistributionType.NORMAL, [2.0, 0.5]),
            "BajoEsfuerzo": UncertainVariable("BajoEsfuerzo", DistributionType.NORMAL, [10.0, 0.2]),
        },
    ),
    DecisionOption(
        name="B: Refactor conservador (caller intacto)",
        description="Borrar miembros/métodos muertos, allowlist como tabla constexpr, "
                    "CRC rx honesto (se borra el andamiaje muerto, NO se enchufa a ciegas), "
                    "API de ComandosGateway sin cambios. Cable idéntico.",
        variables={
            "SeguridadCable": UncertainVariable("SeguridadCable", DistributionType.NORMAL, [9.0, 0.8]),
            "CumplimientoFundacion": UncertainVariable("CumplimientoFundacion", DistributionType.NORMAL, [9.0, 0.5]),
            "Mantenibilidad": UncertainVariable("Mantenibilidad", DistributionType.NORMAL, [9.0, 0.5]),
            "Verificabilidad": UncertainVariable("Verificabilidad", DistributionType.NORMAL, [9.0, 0.5]),
            "Reutilizacion": UncertainVariable("Reutilizacion", DistributionType.NORMAL, [5.0, 1.0]),
            "BajoEsfuerzo": UncertainVariable("BajoEsfuerzo", DistributionType.NORMAL, [7.0, 1.0]),
        },
    ),
    DecisionOption(
        name="C: Eliminar y reimplementar en gateway",
        description="Sin reemplazo funcional hoy: obliga a reescribir el RDSS en gateway. "
                    "Mayor riesgo de romper el cable y mayor esfuerzo.",
        variables={
            "SeguridadCable": UncertainVariable("SeguridadCable", DistributionType.NORMAL, [5.0, 2.0]),
            "CumplimientoFundacion": UncertainVariable("CumplimientoFundacion", DistributionType.NORMAL, [8.0, 1.5]),
            "Mantenibilidad": UncertainVariable("Mantenibilidad", DistributionType.NORMAL, [9.0, 1.0]),
            "Verificabilidad": UncertainVariable("Verificabilidad", DistributionType.NORMAL, [6.0, 1.5]),
            "Reutilizacion": UncertainVariable("Reutilizacion", DistributionType.NORMAL, [3.0, 1.0]),
            "BajoEsfuerzo": UncertainVariable("BajoEsfuerzo", DistributionType.NORMAL, [2.0, 1.0]),
        },
    ),
    DecisionOption(
        name="D: Híbrido codec-puro + allowlist en llamador",
        description="CommandMessage queda como codec de trama puro (framing+CRC+campos); "
                    "la decisión de ruteo (CONFIG vs RETRANSMIT) sube a ComandosGateway como "
                    "tabla constexpr. SoC más limpio, pero toca el llamador.",
        variables={
            "SeguridadCable": UncertainVariable("SeguridadCable", DistributionType.NORMAL, [8.5, 1.0]),
            "CumplimientoFundacion": UncertainVariable("CumplimientoFundacion", DistributionType.NORMAL, [9.5, 0.5]),
            "Mantenibilidad": UncertainVariable("Mantenibilidad", DistributionType.NORMAL, [9.5, 0.5]),
            "Verificabilidad": UncertainVariable("Verificabilidad", DistributionType.NORMAL, [9.0, 0.5]),
            "Reutilizacion": UncertainVariable("Reutilizacion", DistributionType.NORMAL, [7.0, 1.0]),
            "BajoEsfuerzo": UncertainVariable("BajoEsfuerzo", DistributionType.NORMAL, [6.0, 1.0]),
        },
    ),
]

CRIT = [f.name for f in factors]
WEIGHTS = np.array([f.weight for f in factors])
N = 20000


def sample_option(opt):
    rows = []
    for c in CRIT:
        v = opt.variables[c]
        mean, std = v.params[0], v.params[1]
        x = np.random.normal(mean, std, N)
        x = np.clip(x, 0.0, 10.0)
        rows.append(x)
    return np.stack(rows, axis=0)  # (n_crit, N)


def weighted_scores(samples):
    # samples: (n_crit, N) -> (N,)
    return (samples * WEIGHTS[:, None]).sum(axis=0)


def topsis(mean_matrix):
    # mean_matrix: (n_opt, n_crit)
    # ideal = max por columna (todos maximize), anti = min
    ideal = mean_matrix.max(axis=0)
    anti = mean_matrix.min(axis=0)
    d_best, d_worst = [], []
    for r in mean_matrix:
        d_best.append(np.sqrt(((r - ideal) ** 2 * WEIGHTS).sum()))
        d_worst.append(np.sqrt(((r - anti) ** 2 * WEIGHTS).sum()))
    d_best = np.array(d_best)
    d_worst = np.array(d_worst)
    closeness = d_worst / (d_best + d_worst)
    return closeness


async def main():
    np.random.seed(20260823)
    samples_by_opt = {opt.name: sample_option(opt) for opt in options}
    scores_by_opt = {name: weighted_scores(s) for name, s in samples_by_opt.items()}

    # Estadísticas por opción
    print("=" * 92)
    print(f"MONTE CARLO — score compuesto ponderado (escala 0-10), N={N}")
    print("=" * 92)
    stats = {}
    for name, sc in scores_by_opt.items():
        p5, mean, p95 = np.percentile(sc, 5), sc.mean(), np.percentile(sc, 95)
        stats[name] = (p5, mean, p95)
        print(f"  {name:42s} p5={p5:5.2f}  mean={mean:5.2f}  p95={p95:5.2f}")

    # Frecuencia de victoria (qué opción queda en el puesto 1 en cada muestra)
    print()
    print(f"FRECUENCIA DE SER LA MEJOR OPCIÓN (de {N} muestras):")
    win = {name: 0 for name in scores_by_opt}
    M = np.stack([scores_by_opt[n] for n in [o.name for o in options]], axis=0)  # (n_opt, N)
    winners = np.argmax(M, axis=0)
    for i, o in enumerate(options):
        win[o.name] = int((winners == i).sum())
    for o in options:
        print(f"  {o.name:42s} {100.0*win[o.name]/N:5.1f}%")

    # TOPSIS determinista con medias
    mean_mat = np.array([[o.variables[c].params[0] for c in CRIT] for o in options])
    closeness = topsis(mean_mat)
    print()
    print("TOPSIS (medias):")
    order = np.argsort(-closeness)
    for rank, i in enumerate(order, 1):
        print(f"  {rank}. {options[i].name:42s} closeness={closeness[i]:.3f}")

    # Sensibilidad: variar el peso de SeguridadCable (0.15..0.45) y ver si cambia el ganador
    print()
    print("SENSIBILIDAD — ganador (TOPSIS) al mover el peso de SeguridadCable:")
    base = WEIGHTS.copy()
    idx = CRIT.index("SeguridadCable")
    for w in [0.15, 0.20, 0.25, 0.30, 0.35, 0.45]:
        wts = base.copy()
        # redistribuir el resto proporcionalmente
        rest = 1.0 - w
        others = [i for i in range(len(CRIT)) if i != idx]
        old_others = sum(base[others])
        wts[idx] = w
        for i in others:
            wts[i] = base[i] * (rest / old_others)
        cl = topsis(mean_mat * 1.0)  # closeness usa weights globales; recomputar con wts
        # recompute closeness manually with wts
        ideal = mean_mat.max(axis=0)
        anti = mean_mat.min(axis=0)
        db = np.array([np.sqrt(((mean_mat[r]-ideal)**2*wts).sum()) for r in range(len(options))])
        dw = np.array([np.sqrt(((mean_mat[r]-anti)**2*wts).sum()) for r in range(len(options))])
        cl = dw/(db+dw)
        best = options[int(np.argmax(cl))].name
        print(f"  w(SeguridadCable)={w:.2f} -> ganador: {best}")

    # Probabilidad de romper el cable (sub-análisis explícito, independiente)
    print()
    print("SUB-ANÁLISIS — P(romper el cable al reescribir), estimación de experto:")
    pbreak = {"A: Dejar como está": 0.00,
              "B: Refactor conservador (caller intacto)": 0.04,
              "C: Eliminar y reimplementar en gateway": 0.22,
              "D: Híbrido codec-puro + allowlist en llamador": 0.08}
    for k, v in pbreak.items():
        print(f"  {k:42s} ~{v*100:4.1f}%")

    # JSON resultado
    result = {
        "analysis": "commandmessage_refactor",
        "date": datetime.now().isoformat(),
        "weights": {f.name: f.weight for f in factors},
        "montecarlo_stats": {k: {"p5": float(v[0]), "mean": float(v[1]), "p95": float(v[2])}
                             for k, v in stats.items()},
        "win_frequency": {k: 100.0 * v / N for k, v in win.items()},
        "topsis_closeness": {options[i].name: float(closeness[i]) for i in range(len(options))},
        "break_probability_estimate": pbreak,
    }
    out = Path(__file__).parent.parent.parent.parent / "results" / "commandmessage_refactor_20260823.json"
    out.write_text(json.dumps(result, indent=2))
    print()
    print(f"Resultado escrito en: {out}")


if __name__ == "__main__":
    asyncio.run(main())
