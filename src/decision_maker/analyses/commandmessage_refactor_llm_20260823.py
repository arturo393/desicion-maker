#!/usr/bin/env python3
"""
Título: Análisis estocástico — Refactor de CommandMessage (protocolo RDSS del gateway) — REV 2
Propósito: Re-ejecutar commandmessage_refactor_decision.py AGREGANDO el criterio
           MantenimientoAsistidoLLM (legibilidad para iteración por LLM hy3 + opencode),
           sin tocar los demás datos del análisis anterior. Reajustar pesos a suma 1.00.
Creado: 2026-08-23 (REV 2)
Versión: 2.0

CONTEXTO VERIFICADO EN CÓDIGO (idéntico a REV 1, no re-derivado):
- firmware/shared/protocol/CommandMessage.cpp (350 líns, SIN heap, compila -Werror en gateway).
- API viva (ComandosGateway): validate(), getCommandId(), getDataAsUint8(), freqDecode(),
  composeAndSendMessage(), reset(); external setCommandId(5), getDataAsUint32(6).
- Estado muerto / engañoso presente HOY: `listening`, `num_byte_data` (asignado, no leído en
  camino vivo), `ready` (leído solo en setVars, que es ruta de receive no usada por el caller
  vivo), getDataAsUint16/getDataAsFloat (sin refs), y el andamiaje CRC bajo
  `#if ENABLE_CRC_VALIDATION` (checkCRC/checkCRCValidity) que NO compila (flag=0) pero permanece
  en el archivo como código muerto que un LLM podría "activar" o malinterpretar.
- ENABLE_CRC_VALIDATION = 0: CRC se TRANSMITE (crc_get en compose) pero NO se VERIFICA al recibir.
  El desplegado (-simple) también 0 -> "no validar CRC rx" es comportamiento de terreno.
- Allowlist checkModule (byte-exacta al -simple, alineada 20-Ago): rangos 0x20-0x28, 0xB0-0xB9,
  0x50-0x53, 0xD0-0xD3, 0x70-0x7C; singletons 0x30,0x60,0x80,0x81,0xF0,0xF1; 0x10 y 0xBB ->
  RETRANSMIT. Hoy es un bloque de `if` anidados con un comment de ~50 líneas que explica por qué.
  Ese comment es ÚTIL para un humano, pero es un punto de riesgo para un LLM: al "ayudar" a
  añadir un opcode tiende a editar la lista y NO a re-alinearla con -simple, o a creer que el
  comment es la fuente de verdad en vez del binario desplegado.
- Host test Tier-2: test_commandmessage_host.cpp, 15 checks verdes (framing/CRC/allowlist/
  getDataAsUint8). Debe seguir verde; se extiende con checks por opcode.

CRITERIO NUEVO (REV 2):
- MantenimientoAsistidoLLM: legibilidad/robustez del módulo frente a que un LLM (modelo hy3)
  itere sobre él junto con opencode sin introducir defectos. La clave es AUSENCIA DE ESTADO
  ENGAÑOSO: código muerto que el modelo cree vivo, flags (#if) que invitan a "enchufar", y
  comentarios largos que el asistente trata como especificación en vez de verificar contra el
  binario. Distinción con Mantenibilidad: Mantenibilidad mide simplicidad/un-propósito para un
  revisor humano (que lee el comment de 50 líneas y entiende); MantenimientoAsistidoLLM mide el
  riesgo específico de que UN MODELO de propósito general, al tocar el archivo, incurra en un bug
  por pattern-matching sobre lo muerto/lo flags/lo comentado. Se solapan, pero se mantienen ambos.

REAJUSTE DE PESOS (REV 2): se suma MantenimientoAsistidoLLM=0.12 y se escalan los 6 anteriores
por 0.88 para conservar su proporción relativa y sumar 1.00.
  SeguridadCable          0.30*0.88 = 0.264
  CumplimientoFundacion   0.20*0.88 = 0.176
  Mantenibilidad          0.20*0.88 = 0.176
  BajoEsfuerzo            0.15*0.88 = 0.132
  Verificabilidad         0.10*0.88 = 0.088
  Reutilizacion           0.05*0.88 = 0.044
  MantenimientoAsistidoLLM          0.120   (nuevo)
  SUMA = 1.000

FUENTES:
- firmware/shared/protocol/CommandMessage.cpp (lectura directa, 23-Ago)
- firmware/shared/protocol/CommandMessage.hpp (miembros muertos)
- projects/gateway-2lora-simple/Core/Src/CommandMessage.cpp (copia desplegada, allowlist 20-Ago)
- software-foundation.md / firmware-foundation.md (reglas de mantenibilidad, -Werror, host test)
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
# CRITERIOS (pesos REV 2, suman 1.00). Escala 0-10, maximize=True.
#   SeguridadCable           = PRESERVAR el cable exacto (mayor=menor riesgo de romperlo)
#   CumplimientoFundacion    = heap-free, -Werror, host test Tier-2, honestidad de verificación
#   Mantenibilidad           = simplicidad/un-propósito/sin estado muerto (para revisor humano)
#   BajoEsfuerzo             = menor esfuerzo de implementación (mayor=menos esfuerzo)
#   Verificabilidad          = confianza de validar con host tests sin banco
#   Reutilizacion            = el codec puede usarse en otro módulo
#   MantenimientoAsistidoLLM = legibilidad frente a iteración por LLM (hy3+opencode) sin defectos
# ============================================================

factors = [
    Factor("SeguridadCable", weight=0.264, maximize=True),
    Factor("CumplimientoFundacion", weight=0.176, maximize=True),
    Factor("Mantenibilidad", weight=0.176, maximize=True),
    Factor("BajoEsfuerzo", weight=0.132, maximize=True),
    Factor("Verificabilidad", weight=0.088, maximize=True),
    Factor("Reutilizacion", weight=0.044, maximize=True),
    Factor("MantenimientoAsistidoLLM", weight=0.120, maximize=True),
]

# Distribuciones: media±std (NORMAL), escala 0-10. Los 6 criterios previos mantienen
# EXACTAMENTE las medias/std de REV 1; solo se agrega MantenimientoAsistidoLLM.
options = [
    DecisionOption(
        name="A: Dejar como está",
        description="Status quo. Heap-free y -Werror OK, pero estado muerto + andamiaje "
                    "CRC bajo #if + allowlist con comment de 50 líneas. Máximo riesgo de "
                    "que un LLM 'ayude' y rompa algo por pattern-matching sobre lo muerto.",
        variables={
            "SeguridadCable": UncertainVariable("SeguridadCable", DistributionType.NORMAL, [10.0, 0.2]),
            "CumplimientoFundacion": UncertainVariable("CumplimientoFundacion", DistributionType.NORMAL, [6.0, 1.0]),
            "Mantenibilidad": UncertainVariable("Mantenibilidad", DistributionType.NORMAL, [2.0, 0.5]),
            "BajoEsfuerzo": UncertainVariable("BajoEsfuerzo", DistributionType.NORMAL, [10.0, 0.2]),
            "Verificabilidad": UncertainVariable("Verificabilidad", DistributionType.NORMAL, [8.0, 1.0]),
            "Reutilizacion": UncertainVariable("Reutilizacion", DistributionType.NORMAL, [2.0, 0.5]),
            "MantenimientoAsistidoLLM": UncertainVariable("MantenimientoAsistidoLLM", DistributionType.NORMAL, [3.0, 0.8]),
        },
    ),
    DecisionOption(
        name="B: Refactor conservador (caller intacto)",
        description="Borrar miembros/métodos muertos, allowlist como tabla constexpr, "
                    "CRC rx honesto (se borra el andamiaje muerto, NO se enchufa a ciegas), "
                    "API de ComandosGateway sin cambios. Un solo archivo pequeño y honesto: "
                    "mínimo estado engañoso para un LLM.",
        variables={
            "SeguridadCable": UncertainVariable("SeguridadCable", DistributionType.NORMAL, [9.0, 0.8]),
            "CumplimientoFundacion": UncertainVariable("CumplimientoFundacion", DistributionType.NORMAL, [9.0, 0.5]),
            "Mantenibilidad": UncertainVariable("Mantenibilidad", DistributionType.NORMAL, [9.0, 0.5]),
            "BajoEsfuerzo": UncertainVariable("BajoEsfuerzo", DistributionType.NORMAL, [7.0, 1.0]),
            "Verificabilidad": UncertainVariable("Verificabilidad", DistributionType.NORMAL, [9.0, 0.5]),
            "Reutilizacion": UncertainVariable("Reutilizacion", DistributionType.NORMAL, [5.0, 1.0]),
            "MantenimientoAsistidoLLM": UncertainVariable("MantenimientoAsistidoLLM", DistributionType.NORMAL, [9.0, 0.5]),
        },
    ),
    DecisionOption(
        name="C: Eliminar y reimplementar en gateway",
        description="Sin reemplazo funcional hoy: obliga a reescribir el RDSS en gateway. "
                    "Mayor riesgo de romper el cable y mayor esfuerzo; el LLM escribe mucho "
                    "código nuevo en otro módulo (superficie de defecto alta).",
        variables={
            "SeguridadCable": UncertainVariable("SeguridadCable", DistributionType.NORMAL, [5.0, 2.0]),
            "CumplimientoFundacion": UncertainVariable("CumplimientoFundacion", DistributionType.NORMAL, [8.0, 1.5]),
            "Mantenibilidad": UncertainVariable("Mantenibilidad", DistributionType.NORMAL, [9.0, 1.0]),
            "BajoEsfuerzo": UncertainVariable("BajoEsfuerzo", DistributionType.NORMAL, [2.0, 1.0]),
            "Verificabilidad": UncertainVariable("Verificabilidad", DistributionType.NORMAL, [6.0, 1.5]),
            "Reutilizacion": UncertainVariable("Reutilizacion", DistributionType.NORMAL, [3.0, 1.0]),
            "MantenimientoAsistidoLLM": UncertainVariable("MantenimientoAsistidoLLM", DistributionType.NORMAL, [6.0, 1.5]),
        },
    ),
    DecisionOption(
        name="D: Híbrido codec-puro + allowlist en llamador",
        description="CommandMessage queda como codec de trama puro (framing+CRC+campos); "
                    "la decisión de ruteo (CONFIG vs RETRANSMIT) sube a ComandosGateway como "
                    "tabla constexpr. SoC más limpio, pero el LLM debe razonar sobre DOS "
                    "archivos para tocar el ruteo (acoplamiento cross-file).",
        variables={
            "SeguridadCable": UncertainVariable("SeguridadCable", DistributionType.NORMAL, [8.5, 1.0]),
            "CumplimientoFundacion": UncertainVariable("CumplimientoFundacion", DistributionType.NORMAL, [9.5, 0.5]),
            "Mantenibilidad": UncertainVariable("Mantenibilidad", DistributionType.NORMAL, [9.5, 0.5]),
            "BajoEsfuerzo": UncertainVariable("BajoEsfuerzo", DistributionType.NORMAL, [6.0, 1.0]),
            "Verificabilidad": UncertainVariable("Verificabilidad", DistributionType.NORMAL, [9.0, 0.5]),
            "Reutilizacion": UncertainVariable("Reutilizacion", DistributionType.NORMAL, [7.0, 1.0]),
            "MantenimientoAsistidoLLM": UncertainVariable("MantenimientoAsistidoLLM", DistributionType.NORMAL, [8.0, 0.7]),
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
    return (samples * WEIGHTS[:, None]).sum(axis=0)


def closeness_with_weights(mean_mat, wts):
    ideal = mean_mat.max(axis=0)
    anti = mean_mat.min(axis=0)
    db = np.array([np.sqrt(((mean_mat[r] - ideal) ** 2 * wts).sum()) for r in range(mean_mat.shape[0])])
    dw = np.array([np.sqrt(((mean_mat[r] - anti) ** 2 * wts).sum()) for r in range(mean_mat.shape[0])])
    return dw / (db + dw)


async def main():
    np.random.seed(20260823)
    samples_by_opt = {opt.name: sample_option(opt) for opt in options}
    scores_by_opt = {name: weighted_scores(s) for name, s in samples_by_opt.items()}

    print("=" * 96)
    print(f"MONTE CARLO — score compuesto ponderado (escala 0-10, REV 2 + MantenimientoAsistidoLLM), N={N}")
    print("=" * 96)
    stats = {}
    for name, sc in scores_by_opt.items():
        p5, mean, p95 = np.percentile(sc, 5), sc.mean(), np.percentile(sc, 95)
        stats[name] = (p5, mean, p95)
        print(f"  {name:42s} p5={p5:5.2f}  mean={mean:5.2f}  p95={p95:5.2f}")

    print()
    print(f"FRECUENCIA DE SER LA MEJOR OPCIÓN (de {N} muestras):")
    win = {name: 0 for name in scores_by_opt}
    M = np.stack([scores_by_opt[o.name] for o in options], axis=0)  # (n_opt, N)
    winners = np.argmax(M, axis=0)
    for i, o in enumerate(options):
        win[o.name] = int((winners == i).sum())
    for o in options:
        print(f"  {o.name:42s} {100.0*win[o.name]/N:5.1f}%")

    mean_mat = np.array([[o.variables[c].params[0] for c in CRIT] for o in options])
    closeness = closeness_with_weights(mean_mat, WEIGHTS)
    print()
    print("TOPSIS (medias, pesos REV 2):")
    order = np.argsort(-closeness)
    for rank, i in enumerate(order, 1):
        print(f"  {rank}. {options[i].name:42s} closeness={closeness[i]:.3f}")

    # ---- SENSIBILIDAD 1: mover el peso de SeguridadCable (el cable no debe romperse) ----
    print()
    print("SENSIBILIDAD 1 — ganador (TOPSIS) al mover w(SeguridadCable):")
    idx = CRIT.index("SeguridadCable")
    base = WEIGHTS.copy()
    for w in [0.15, 0.20, 0.25, 0.30, 0.35, 0.45]:
        wts = base.copy()
        rest = 1.0 - w
        others = [i for i in range(len(CRIT)) if i != idx]
        old_others = sum(base[others])
        wts[idx] = w
        for i in others:
            wts[i] = base[i] * (rest / old_others)
        cl = closeness_with_weights(mean_mat, wts)
        best = options[int(np.argmax(cl))].name
        mark = "  <-- cambia" if best != options[int(np.argmax(closeness_with_weights(mean_mat, WEIGHTS)))].name else ""
        print(f"  w(SeguridadCable)={w:.2f} -> ganador: {best}{mark}")

    # ---- SENSIBILIDAD 2: mover el peso del NUEVO criterio MantenimientoAsistidoLLM ----
    print()
    print("SENSIBILIDAD 2 — ganador (TOPSIS) al mover w(MantenimientoAsistidoLLM):")
    idx2 = CRIT.index("MantenimientoAsistidoLLM")
    for w in [0.04, 0.08, 0.12, 0.18, 0.25, 0.35]:
        wts = base.copy()
        rest = 1.0 - w
        others = [i for i in range(len(CRIT)) if i != idx2]
        old_others = sum(base[others])
        wts[idx2] = w
        for i in others:
            wts[i] = base[i] * (rest / old_others)
        cl = closeness_with_weights(mean_mat, wts)
        best = options[int(np.argmax(cl))].name
        mark = "  <-- cambia" if best != options[int(np.argmax(closeness_with_weights(mean_mat, WEIGHTS)))].name else ""
        print(f"  w(MantenimientoAsistidoLLM)={w:.2f} -> ganador: {best}{mark}")

    # ---- SENSIBILIDAD 3: barrido uniforme de todos los pesos (robustez global) ----
    print()
    print("SENSIBILIDAD 3 — ganador bajo shocks uniformes ±40% en CADA peso (Monte Carlo de pesos):")
    rng = np.random.default_rng(20260823)
    winner_shock = {o.name: 0 for o in options}
    NS = 5000
    for _ in range(NS):
        w = rng.dirichlet(WEIGHTS * 1.4)  # perturba la proporción ~±40%
        # renormaliza
        w = w / w.sum()
        cl = closeness_with_weights(mean_mat, w)
        winner_shock[options[int(np.argmax(cl))].name] += 1
    baseline = options[int(np.argmax(closeness))].name
    for o in options:
        pct = 100.0 * winner_shock[o.name] / NS
        mark = "  <-- REEMPLAZA al ganador base" if (pct > 50 and o.name != baseline) else ""
        print(f"  {o.name:42s} {pct:5.1f}%{mark}")

    # ---- Sub-análisis: P(romper el cable) (estimación de experto, inalterada) ----
    print()
    print("SUB-ANÁLISIS — P(romper el cable al reescribir), estimación de experto (igual REV 1):")
    pbreak = {"A: Dejar como está": 0.00,
              "B: Refactor conservador (caller intacto)": 0.04,
              "C: Eliminar y reimplementar en gateway": 0.22,
              "D: Híbrido codec-puro + allowlist en llamador": 0.08}
    for k, v in pbreak.items():
        print(f"  {k:42s} ~{v*100:4.1f}%")

    # ---- Diseño objetivo y plan (entregables 4 y 5) ----
    design = (
        "DISENO OBJETIVO (REV 2 = REV 1): B + allowlist como constexpr.\n"
        "  - Un solo archivo CommandMessage.{cpp,hpp}, caller (ComandosGateway) INTACTO.\n"
        "  - Borrar estado muerto: `listening`, `num_byte_data` (si no se lee en camino vivo),\n"
        "    `ready` (si setVars no es ruta viva), getDataAsUint16/getDataAsFloat (sin refs),\n"
        "    checkCRC/checkCRCValidity (andamiaje bajo #if ENABLE_CRC_VALIDATION=0).\n"
        "  - Allowlist como `static constexpr` (tabla de rangos + singletons) en .hpp; reemplaza\n"
        "    los `if` anidados y el comment de 50 líneas por una tabla + 3 líneas de contexto.\n"
        "  - CRC rx: `constexpr bool kValidateCrcOnRx = false;` con un comment de UNA línea\n"
        "    ('intencional: coincide con gateway-2lora-simple; cambiar exige test en banco'),\n"
        "    SIN `#if` muerto. crc_get + un calculateCRC único usado por composeAndSendMessage.\n"
        "  - composeAndSendMessage: sin cambios de semántica (cable idéntico)."
    )
    plan = (
        "PLAN DE IMPLEMENTACION (REV 2 = REV 1):\n"
        "  Paso 1  Borrar estado muerto (listening, num_byte_data, ready si aplica, getDataAs*16/32?\n"
        "          solo las sin ref, checkCRC/checkCRCValidity). Compilar gateway; correr host test\n"
        "          (15 checks) -> debe seguir VERDE.\n"
        "  Paso 2  Allowlist a tabla constexpr (rangos 0x20-0x28,0xB0-0xB9,0x50-0x53,0xD0-0xD3,\n"
        "          0x70-0x7C + singletons 0x30,0x60,0x80,0x81,0xF0,0xF1; 0x10/0xBB->RETRANSMIT).\n"
        "          Reemplazar ifs. Host test existente fija allowlist -> VERDE; EXTENDER con checks\n"
        "          parametrizados por opcode (fronteras de cada rango + singletons + 0x10/0xBB).\n"
        "  Paso 3  Simplificar compose + borrar calculateCRC/#if: dejar crc_get + 1 calculateCRC\n"
        "          usado por compose; eliminar checkCRC/checkCRCValidity o mover a función opcional\n"
        "          claramente etiquetada. -Werror debe seguir limpio.\n"
        "  Paso 4  CRC rx opcional: constexpr bool kValidateCrcOnRx=false + 1 línea de comment.\n"
        "          Sin #if. Fidelidad a -simple preservada.\n"
        "  Paso 5  Revisión (Code Review Pillars + -Werror + host test 15+ checks VERDE).\n"
        "          NO tocar ComandosGateway (caller intacto)."
    )

    print()
    print(design)
    print()
    print(plan)

    result = {
        "analysis": "commandmessage_refactor_llm",
        "revision": "2.0",
        "date": datetime.now().isoformat(),
        "weights": {f.name: float(f.weight) for f in factors},
        "weights_note": "REV 2: +MantenimientoAsistidoLLM(0.12); los 6 previos escalados x0.88 para sumar 1.00",
        "montecarlo_stats": {k: {"p5": float(v[0]), "mean": float(v[1]), "p95": float(v[2])}
                             for k, v in stats.items()},
        "win_frequency": {k: 100.0 * v / N for k, v in win.items()},
        "topsis_closeness": {options[i].name: float(closeness[i]) for i in range(len(options))},
        "break_probability_estimate": pbreak,
        "design_objective": design,
        "implementation_plan": plan,
    }
    out = Path(__file__).parent.parent.parent.parent / "results" / "commandmessage_refactor_llm_20260823.json"
    out.write_text(json.dumps(result, indent=2))
    print()
    print(f"Resultado escrito en: {out}")


if __name__ == "__main__":
    asyncio.run(main())
