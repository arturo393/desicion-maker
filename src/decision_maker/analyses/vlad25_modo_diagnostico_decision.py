"""
Decision Analysis - VLAD25: coexistencia de MODO POLLING (legacy) y MODO PUSH (telemetria)
Purpose: Elegir COMO el sistema de diagnostico remoto distingue y opera los dos modos, y CON QUE
         CARGA (payload) lo hace, porque el airtime es el presupuesto de colision de la flota.
Created: 2026-08-13
Last Updated: 2026-08-13
Version: 2.0

CAMBIOS EN ESTA VERSION (v2.0)
------------------------------
- Se agrego el criterio "riqueza_fidelidad_dato" (maximizar): el push actual reporta MENOS
  cobertura que el polling legacy, y sin este criterio el modelo no lo veia.
- El "riesgo_colision_lora" ya NO es un juicio: se DERIVA del airtime LoRa calculado con los
  parametros reales del equipo (SF7, BW125 kHz, CR 4/5) y una carga ALOHA de 100 nodos.
- Se agregaron sub-variantes de payload: push 18 B (actual), push ~32 B (recupera RF por banda),
  y push de dos niveles (trama corta frecuente + trama larga esporadica).

CONTEXTO
--------
Firmware VLAD25 (STM32G474, /home/arturo/uqomm/fw-vlad), backend legacy en
/home/arturo/uqomm/sw-diagnosticoremoto. Flota objetivo ~100 amplificadores en el MISMO canal.

HECHOS VERIFICADOS EN EL REPO (no son supuestos)
------------------------------------------------
 1. Telemetria push APAGADA por defecto:      telemetry_report.cpp:65 -> s_telemetry_on = 0U
 2. El fw YA distingue V1 (0x7E) de V2 pelado: Vlad25Cmd.cpp:110-122
 3. El CRC16 de V1 se parsea y se IGNORA:      Vlad25Cmd.cpp:124-125,155
 4. CLEAR_ALERTS se movio de 0x11 a 0x30 (el polling legacy con 0x11 borraba las alarmas);
    0x11 quedo SIN ATENDER:                    Vlad25Cmd.hpp:202-223, cmd_handlers.cpp:379-381
 5. El push tiene backoff + jitter (+-10 % del periodo) pero NUNCA se midio con dos equipos:
                                               Telemetry.hpp:186-219
 6. El flag de telemetria YA se persiste en EEPROM I2C (verificado en placa):
                                               persist.cpp:179, state_bridge.cpp:62,164
 7. Dos filtros de lista explicita SILENCIOSOS: handlers/vlad.go (allowedCmds -> HTTP 400) y
    gateway_command.py ("Unknown vlad command" -> loguea, DESCARTA, devuelve HTTP 200).
 8. Payload push = 18 B:                       Telemetry.hpp:38 FRAME_LEN = 18U
 9. Periodo push por defecto 60 s (30..3600):  Telemetry.hpp:40-42
10. Cuantizacion del push, medida en el encoder (Telemetry.hpp:138-145):
    vin/500 mV, corrientes/10 mA (saturan a 2,55 A), temp/1000 (1 degC), atten/500 mdB,
    uptime en MINUTOS uint16 -> DA LA VUELTA a los ~45,5 dias.
11. El push NO lleva: agc/ref/level de 152 MHz, agc/ref/level de 172 MHz, tono, +5 V.
    Son 8 de las 13 magnitudes que si viajan en la respuesta de 25 B del polling legacy.
12. Parametros LoRa por defecto = SF7, BW125 (indice 7), CR5 (=4/5):
    Lora.hpp:23-26 (LoraBW::BW125 es el indice 7), Lora.hpp:110,124

TENSION CENTRAL (la que el planteo original no tenia)
-----------------------------------------------------
El push es MAS CHICO que el polling (18 B vs 25 B) porque esta dimensionado para el airtime, que
es el presupuesto de colision con 100 equipos. Recuperar la cobertura de RF y la resolucion exige
crecer el payload, y crecer el payload EMPEORA la colision. No es "polling vs push": es cuanta
observabilidad se puede comprar con el airtime disponible.

SUPUESTOS (marcados; NO son hechos verificados)
-----------------------------------------------
S1. El formato exacto de los 25 B del 0x11 es armable desde el snapshot de estado que el fw ya
    tiene. Riesgo residual de offsets -> cola baja de compat en A/F/G.
S2. El backend legacy, esperando la respuesta de un poll, NO descarta limpiamente una trama de
    push no solicitada que llegue en el medio. Es lo que mas castiga a D.
S3. El comando de habilitacion de modo no esta hoy en allowedCmds ni en gateway_command.py.
S4. Esfuerzos en escala relativa 0..10, no en horas.
S5. Modelo de canal: ALOHA puro, sin ACK, sin escucha-antes-de-transmitir efectiva ->
    p_colision = 1 - exp(-2G) con G = carga ofrecida. Es el PEOR CASO honesto: el jitter de
    +-10 % del hecho 5 la reduce, pero nunca se midio, asi que no se le acredita.
S6. Preambulo LoRa de 8 simbolos, header explicito, CRC activo, sin low-datarate-optimize (SF7).
S7. Payload del pedido de polling ~= 8 B; turnaround gateway->equipo->gateway ~= 40 ms.
S8. Trama larga del push de dos niveles: ~48 B cada 30 min (recupera las 8 magnitudes que faltan
    con resolucion util). Trama corta: los 18 B actuales cada 60 s.
S9. La ampliacion a 32 B recupera cobertura de RF pero NO arregla por si sola el uptime uint16 en
    minutos ni las corrientes que saturan a 2,55 A -> su riqueza no llega a la del legacy.

LO QUE ESTA MAL PLANTEADO EN LAS OPCIONES ORIGINALES (ver bloque MAL_PLANTEADO al final)
"""

import asyncio
import json
import math
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from decision_maker.core.models import DecisionOption, DistributionType, Factor, UncertainVariable
from decision_maker.core.orchestrator import UnifiedDecisionFramework

analysis_name = "VLAD25 modo diagnostico polling vs push v2"
analysis_date = datetime.now().isoformat()

TRI = DistributionType.TRIANGULAR

# ============================================================
# FISICA DEL CANAL: airtime LoRa y carga de la flota
# ============================================================

SF = 7
BW_HZ = 125_000.0        # LoraBW::BW125 == indice 7 (hecho 12)
CR_CODED = 5             # CR5 = 4/5 (hecho 12)
N_PREAMBLE = 8           # S6
FLEET_N = 100            # flota objetivo
PERIOD_S = 60            # hecho 9: PERIOD_DEFAULT_S
POLL_REQ_B = 8           # S7
TURNAROUND_MS = 40.0     # S7
P_COLL_FULL_SCALE = 0.35 # p_colision que se mapea a 10/10 de riesgo


def airtime_ms(payload_b: int) -> float:
    """Tiempo en el aire de un paquete LoRa (SX127x, header explicito, CRC on)."""
    t_sym = (2.0**SF) / BW_HZ
    t_preamble = (N_PREAMBLE + 4.25) * t_sym
    num = 8.0 * payload_b - 4.0 * SF + 28.0 + 16.0  # CRC=1, IH=0
    den = 4.0 * SF                                   # DE=0 en SF7
    n_payload = 8 + max(math.ceil(num / den) * CR_CODED, 0)
    return (t_preamble + n_payload * t_sym) * 1000.0


def p_collision(load_terms) -> float:
    """ALOHA puro (S5). load_terms = [(payload_b, periodo_s), ...] por nodo."""
    g = sum(FLEET_N * airtime_ms(pl) / (per * 1000.0) for pl, per in load_terms)
    return 1.0 - math.exp(-2.0 * g)


def risk_from_load(load_terms) -> float:
    """Mapea p_colision a la escala 0..10 del criterio de riesgo."""
    return min(10.0, 10.0 * p_collision(load_terms) / P_COLL_FULL_SCALE)


def risk_tri(pl_min: int, pl_mode: int, pl_max: int, period_s: int = PERIOD_S, extra=()):
    """Triangular de riesgo derivada de la incertidumbre en el tamano de payload."""
    return (
        risk_from_load([(pl_min, period_s), *extra]),
        risk_from_load([(pl_mode, period_s), *extra]),
        risk_from_load([(pl_max, period_s), *extra]),
    )


# Polling: el maestro serializa, no hay contienda. El riesgo residual viene de reintentos y de
# un backend que pollee en paralelo, no del airtime. Se modela chico y explicito.
RISK_POLLING = (0.1, 0.6, 1.8)

# ============================================================
# FACTORES
# ============================================================

factors = [
    Factor("compat_backend_legacy", weight=0.17, maximize=True),
    Factor("riesgo_colision_lora", weight=0.15, maximize=False),
    Factor("riqueza_fidelidad_dato", weight=0.14, maximize=True),
    Factor("esfuerzo_firmware", weight=0.07, maximize=False),
    Factor("esfuerzo_backend", weight=0.11, maximize=False),
    Factor("riesgo_config_divergente", weight=0.08, maximize=False),
    Factor("testabilidad_hoy", weight=0.12, maximize=True),
    Factor("reversibilidad", weight=0.08, maximize=True),
    Factor("valor_operativo_push", weight=0.08, maximize=True),
]

# ============================================================
# OPCIONES
# ============================================================


def opt(name, desc, compat, colis, riqueza, esf_fw, esf_be, div, test, rev, push):
    return DecisionOption(
        name=name,
        description=desc,
        variables={
            "compat_backend_legacy": UncertainVariable("compat_backend_legacy", TRI, list(compat)),
            "riesgo_colision_lora": UncertainVariable("riesgo_colision_lora", TRI, list(colis)),
            "riqueza_fidelidad_dato": UncertainVariable("riqueza_fidelidad_dato", TRI, list(riqueza)),
            "esfuerzo_firmware": UncertainVariable("esfuerzo_firmware", TRI, list(esf_fw)),
            "esfuerzo_backend": UncertainVariable("esfuerzo_backend", TRI, list(esf_be)),
            "riesgo_config_divergente": UncertainVariable("riesgo_config_divergente", TRI, list(div)),
            "testabilidad_hoy": UncertainVariable("testabilidad_hoy", TRI, list(test)),
            "reversibilidad": UncertainVariable("reversibilidad", TRI, list(rev)),
            "valor_operativo_push": UncertainVariable("valor_operativo_push", TRI, list(push)),
        },
    )


# Cargas de canal por opcion (payload, periodo). Ver S8.
LOAD_PUSH_18 = (16, 18, 22)     # el layout actual, con margen si se le agrega un campo
LOAD_PUSH_32 = (28, 32, 40)     # recupera agc/ref/level de las dos bandas
TWO_TIER_LONG = ((48, 1800),)   # trama larga esporadica, cada 30 min

options = [
    opt(
        "A. Solo polling legacy 25 B",
        "Implementar 0x11 con los 25 B en formato viejo. Push apagado permanentemente.",
        compat=(8.0, 9.5, 10.0),        # S1
        colis=RISK_POLLING,             # maestro serializado: sin contienda
        riqueza=(7.5, 8.5, 9.5),        # 13 magnitudes, ADC crudo (maxima fidelidad disponible)
        esf_fw=(2.0, 3.5, 5.0),
        esf_be=(0.0, 0.5, 1.5),
        div=(0.0, 0.3, 1.0),
        test=(8.0, 9.0, 10.0),
        rev=(7.0, 8.5, 9.5),
        push=(0.0, 0.5, 1.5),           # no entrega deteccion autonoma
    ),
    opt(
        "B18. Solo push 18 B (trama actual)",
        "El equipo emite los 18 B de hoy y el backend se adapta. Pierde 8 de 13 magnitudes.",
        compat=(0.0, 1.0, 2.0),
        colis=risk_tri(*LOAD_PUSH_18),
        riqueza=(1.5, 2.5, 3.5),        # hechos 10 y 11: menos cobertura Y menos resolucion
        esf_fw=(1.0, 2.0, 3.0),         # ya existe; alcanza con prenderlo
        esf_be=(6.0, 8.0, 10.0),        # ingest nuevo + los 2 filtros (hecho 7, S3)
        div=(0.0, 0.5, 1.5),
        test=(1.0, 2.5, 4.0),           # la anticolision NO es verificable hoy (hecho 5)
        rev=(2.0, 3.5, 5.0),
        push=(7.5, 8.5, 9.5),
    ),
    opt(
        "B32. Solo push ~32 B (recupera RF por banda)",
        "Push ampliado con agc/ref/level de 152 y 172 MHz. Mas cobertura, mas airtime.",
        compat=(0.0, 1.0, 2.0),
        colis=risk_tri(*LOAD_PUSH_32),
        riqueza=(5.5, 6.5, 7.5),        # S9: recupera cobertura, no arregla uptime ni saturacion
        esf_fw=(3.0, 4.5, 6.0),         # layout nuevo + versionado de trama
        esf_be=(6.5, 8.5, 10.0),
        div=(0.0, 0.5, 1.5),
        test=(1.0, 2.5, 4.0),
        rev=(2.0, 3.0, 4.5),
        push=(8.0, 9.0, 10.0),
    ),
    opt(
        "C. Ambos, modo por comando persistido en EEPROM",
        "Un modo por equipo elegido al provisionar. Push 18 B donde este activo.",
        compat=(6.0, 8.0, 9.5),
        colis=risk_tri(*LOAD_PUSH_18),  # peor caso: toda la flota provisionada en push
        riqueza=(4.0, 5.5, 7.0),        # depende del modo en que quedo cada equipo
        esf_fw=(3.0, 4.5, 6.0),
        esf_be=(3.0, 5.0, 7.0),
        div=(5.0, 7.0, 9.0),            # 100 unidades con un flag de modo: deriva
        test=(4.0, 6.0, 8.0),
        rev=(6.0, 7.5, 9.0),
        push=(6.0, 7.5, 9.0),
    ),
    opt(
        "D. Ambos simultaneos, discriminando por enmarcado",
        "V1 (0x7E) -> respuesta legacy; el push 18 B sale igual por su cuenta. Sin configuracion.",
        compat=(5.0, 7.0, 8.5),         # S2
        colis=risk_tri(*LOAD_PUSH_18),
        riqueza=(7.0, 8.0, 9.0),        # 25 B on-demand + 18 B autonomo
        esf_fw=(1.0, 2.0, 3.5),         # el fw ya distingue los enmarcados (hecho 2)
        esf_be=(2.0, 4.0, 6.0),
        div=(0.0, 0.5, 1.5),
        test=(3.0, 5.0, 7.0),
        rev=(5.0, 7.0, 8.5),
        push=(7.0, 8.5, 9.5),
    ),
    opt(
        "E. Push 18 B por defecto + supresion N periodos tras polling",
        "Push default ON; cada polling suprime el push N periodos.",
        compat=(6.0, 8.0, 9.5),
        colis=risk_tri(*LOAD_PUSH_18),  # la supresion no baja la carga si casi no hay polling
        riqueza=(6.5, 7.5, 8.5),
        esf_fw=(3.0, 4.5, 6.5),
        esf_be=(2.0, 4.0, 6.0),
        div=(1.0, 2.0, 3.5),
        test=(2.0, 4.0, 6.0),
        rev=(3.0, 5.0, 7.0),            # el estado riesgoso es el DEFAULT
        push=(8.0, 9.0, 10.0),
    ),
    opt(
        "F. Polling legacy 25 B + push 18 B opt-in (default OFF)",
        "0x11 contestado siempre; push disponible y persistido pero apagado por defecto.",
        compat=(8.0, 9.5, 10.0),
        colis=RISK_POLLING,             # default OFF -> el canal es el de hoy
        riqueza=(7.5, 8.7, 9.5),
        esf_fw=(2.0, 3.5, 5.0),         # 0x11 + reusar el flag persistido (hecho 6)
        esf_be=(0.0, 1.0, 2.0),
        div=(1.0, 2.0, 4.0),            # default seguro: no configurar es lo correcto
        test=(7.0, 8.5, 9.5),
        rev=(8.0, 9.0, 10.0),
        push=(4.0, 6.0, 7.5),           # capacidad disponible, no activa
    ),
    opt(
        "G. Polling 25 B + push de dos niveles opt-in (18 B/60 s + 48 B/30 min)",
        "Trama corta frecuente para liveness, trama larga esporadica que recupera RF, tono y +5 V.",
        compat=(8.0, 9.5, 10.0),
        colis=risk_tri(16, 18, 22, extra=TWO_TIER_LONG),
        riqueza=(8.5, 9.3, 10.0),       # cobertura completa por las dos vias
        esf_fw=(4.0, 5.5, 7.5),         # dos layouts + planificador de dos ritmos
        esf_be=(2.0, 3.5, 5.5),
        div=(2.0, 3.0, 5.0),
        test=(5.0, 6.5, 8.0),
        rev=(7.0, 8.5, 9.5),
        push=(6.0, 7.5, 9.0),
    ),
]

# ============================================================
# EJECUCION
# ============================================================


def _shock_weights(base_factors, target_name, mult):
    return [
        Factor(f.name, weight=max(f.weight * mult if f.name == target_name else f.weight, 1e-6),
               maximize=f.maximize)
        for f in base_factors
    ]


async def _run(fs, os_):
    fw = UnifiedDecisionFramework()
    for f in fs:
        fw.add_factor(f)
    for o in os_:
        fw.add_option(o)
    return await fw.run_analysis(mode="standard")


def print_airtime_table():
    print("\n" + "=" * 96)
    print("  FISICA DEL CANAL — airtime LoRa SF7 / BW 125 kHz / CR 4/5 (hecho 12), 100 equipos")
    print("=" * 96)
    print(f"  {'payload':>8} {'airtime':>10} {'carga G @60s':>14} {'p_colision':>12}   que es")
    print("  " + "-" * 92)
    rows = [
        (8, False, "pedido de polling (S7) — serializado"),
        (25, False, "respuesta polling legacy — serializado"),
        (18, True, "PUSH ACTUAL (hecho 8)"),
        (32, True, "push ampliado con RF por banda"),
        (48, True, "trama larga de dos niveles (S8)"),
    ]
    for pl, contends, what in rows:
        at = airtime_ms(pl)
        if contends:
            g = FLEET_N * at / (PERIOD_S * 1000.0)
            p = 1.0 - math.exp(-2.0 * g)
            print(f"  {pl:>6} B {at:>8.1f} ms {g * 100:>13.1f}% {p * 100:>11.1f}%   {what}")
        else:
            print(f"  {pl:>6} B {at:>8.1f} ms {'n/a':>14} {'n/a':>12}   {what}")

    sweep = FLEET_N * (airtime_ms(POLL_REQ_B) + airtime_ms(25) + TURNAROUND_MS) / 1000.0
    print(f"\n  Barrido completo de polling (100 equipos, serializado): {sweep:.1f} s de canal")
    print("  -> el polling NO tiene contienda: el airtime le limita el RITMO DE BARRIDO, no la")
    print("     probabilidad de colision. El push si contiende: el airtime le limita el PAYLOAD.")
    p18 = p_collision([(18, PERIOD_S)]) * 100
    p32 = p_collision([(32, PERIOD_S)]) * 100
    p2t = p_collision([(18, PERIOD_S), *TWO_TIER_LONG]) * 100
    print(f"\n  Costo de recuperar cobertura: 18 B -> 32 B sube p_colision de {p18:.1f}% a "
          f"{p32:.1f}% (+{p32 - p18:.1f} pp)")
    print(f"  Dos niveles (18 B/60 s + 48 B/30 min) la deja en {p2t:.1f}% "
          f"(+{p2t - p18:.1f} pp): casi toda la cobertura por casi nada de airtime")


async def main():
    print_airtime_table()

    results = await _run(factors, options)
    mc = results["mc_results"]
    topsis = results.get("topsis_scores")

    print("\n" + "=" * 96)
    print("  RANKING VLAD25 — modo de reporte y payload")
    print("=" * 96)
    print(f"  {'#':<3} {'Opcion':<58} {'p5':>7} {'mean':>7} {'p95':>7} {'TOPSIS':>8}")
    print("  " + "-" * 92)
    ranked = sorted(mc.items(), key=lambda kv: kv[1].mean_score, reverse=True)
    for i, (name, st) in enumerate(ranked, 1):
        t = float(topsis.get(name, float("nan"))) if topsis is not None and len(topsis) else float("nan")
        print(f"  {i:<3} {name[:58]:<58} {st.percentile_5:>7.4f} {st.mean_score:>7.4f} "
              f"{st.percentile_95:>7.4f} {t:>8.4f}")

    winner = ranked[0][0]
    print(f"\n  GANADOR (media MC): {winner}")
    conf = results.get("uncertainty", {}).get("confidence_weighted_winner")
    print(f"  Ganador ponderado por confianza: {conf}")
    print(f"  Estrategias de teoria de la decision: {results.get('strategies')}")

    sens = results.get("sensitivity", {})
    print(f"\n  Robustez interna: base_winner={sens.get('base_winner')} "
          f"robustness_score={sens.get('robustness_score')}")

    print("\n  Shock manual de pesos (x2 y x0.25 por criterio):")
    flips = []
    for fname in [f.name for f in factors]:
        for mult, label in ((2.0, "x2.0"), (0.25, "x0.25")):
            r = await _run(_shock_weights(factors, fname, mult), options)
            w = max(r["mc_results"].items(), key=lambda kv: kv[1].mean_score)[0]
            if w != winner:
                flips.append((fname, label, w))
            flag = "  <-- CAMBIA" if w != winner else ""
            print(f"    {fname:<26} {label:<6} -> {w[:50]}{flag}")
    if not flips:
        print("\n  Ningun shock de peso individual cambia al ganador.")

    print(f"\n  Pareto dominadas: {results.get('pareto', {}).get('dominated_options')}")

    print("\n" + "=" * 96)
    print("  MAL_PLANTEADO — opciones originales que el dato nuevo invalida o incompleta")
    print("=" * 96)
    for line in [
        "B (solo push) esta MAL PLANTEADA tal como se enuncio: con la trama de 18 B no es un",
        "  cambio de transporte sino una REGRESION de observabilidad (8 de 13 magnitudes se",
        "  pierden, hecho 11). 'El backend se adapta' no alcanza: no hay nada a que adaptarse.",
        "  Solo tiene sentido como B32 o superior, y ahi el costo se paga en airtime.",
        "",
        "E (supresion tras polling) resuelve el problema EQUIVOCADO. La supresion evita que el",
        "  push choque con la respuesta de un poll, pero la colision dominante es push-contra-push",
        "  entre 100 emisores, no push-contra-respuesta. Si casi no hay polling, la supresion no",
        "  baja la carga del canal en nada.",
        "",
        "C (modo por equipo) le falta la variante que importa: no es 'polling o push' por equipo,",
        "  sino QUE PAYLOAD emite el que esta en push. Un flag de modo sin un contrato de payload",
        "  versionado deja al backend adivinando el layout.",
        "",
        "D (discriminar por enmarcado) es correcta como mecanismo y es de hecho lo que el fw ya",
        "  hace (hecho 2), pero no es una decision sobre el MODO: es una consecuencia. Su costo",
        "  real no es el enmarcado, es que el push queda encendido por defecto.",
        "",
        "FALTA en el planteo original, y es la que gana el criterio de riqueza: el push de DOS",
        "  NIVELES (G). Separar liveness (corto y frecuente) de diagnostico (largo y esporadico)",
        "  compra casi toda la cobertura por casi nada de airtime.",
        "",
        "BUG INDEPENDIENTE DE LA DECISION: uptime uint16 en minutos da la vuelta a los 45,5 dias",
        "  (hecho 10). Se arregla en cualquiera de las opciones y hay que arreglarlo en todas.",
    ]:
        print("  " + line)

    out = {
        "name": analysis_name,
        "date": analysis_date,
        "winner": winner,
        "airtime_ms": {str(pl): airtime_ms(pl) for pl in (8, 18, 25, 32, 48)},
        "p_collision_pct": {
            "push_18B_60s": p_collision([(18, PERIOD_S)]) * 100,
            "push_32B_60s": p_collision([(32, PERIOD_S)]) * 100,
            "two_tier": p_collision([(18, PERIOD_S), *TWO_TIER_LONG]) * 100,
        },
        "ranking": [
            {"option": n, "p5": st.percentile_5, "mean": st.mean_score, "p95": st.percentile_95}
            for n, st in ranked
        ],
        "weight_shock_flips": [{"factor": f, "shock": s, "winner": w} for f, s, w in flips],
    }
    Path("results").mkdir(exist_ok=True)
    with open("results/vlad25_modo_diagnostico.json", "w") as fh:
        json.dump(out, fh, indent=2)
    print("\n  Resultados en results/vlad25_modo_diagnostico.json")


if __name__ == "__main__":
    asyncio.run(main())
