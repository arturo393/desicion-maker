"""
Analysis: Piloto Nexa Cerro Lindo — ¿llegamos a fin de noviembre, y con qué alcance?
Purpose: Estimar la probabilidad de dejar operativo el piloto de bombeo (ON/OFF remoto +
  tensión y corriente por el cable radiante) antes del 30-Nov-2026, por alcance, y
  ordenar los riesgos por cuánto plazo se comen. Solo software y firmware: el
  hardware (sniffer, gabinete, acople RF) es de Claudio y entra como riesgo externo.
Created: 2026-10-15
Version: 1.0

Dos pasos:
  1. Monte Carlo PROPIO de la red de tareas (días hábiles desde el lunes 19-Oct-2026),
     con riesgos como eventos Bernoulli que agregan demora. Da P(a tiempo), p50/p80 y
     cuánto pesa cada riesgo (P a tiempo con ese riesgo apagado).
  2. El motor multicriterio del framework, con la HOLGURA simulada en el paso 1 como
     uno de los criterios, junto a esfuerzo, riesgo técnico y escalabilidad.

Opciones:
  A_CONTACTOS_FWCORE  - DOUT→relé de interposición, V/I por 4-20 mA, firmware v3 (fw-core)
  B_MODBUS_FWCORE     - igual, pero V/I leídos al arrancador por Modbus RTU (maestro en fw-core)
  C_CONTACTOS_LEGACY  - como A, pero sobre el firmware v2.1 de terreno parchado

Fuente de las duraciones: docs/proyectos/nexa-cerro-lindo/PLAN.md en fw-snifferTelemetry.
Todo número sin medición está marcado [SUPUESTO] en ese plan.
"""

import asyncio
import json
from datetime import date, datetime, timedelta
from pathlib import Path

import numpy as np

from decision_maker.core.models import DecisionOption, DistributionType, Factor, UncertainVariable
from decision_maker.core.orchestrator import UnifiedDecisionFramework

analysis_name = "nexa_piloto_bombeo_plazo"
analysis_date = datetime.now().isoformat()

N = 20_000
RNG = np.random.default_rng(20261015)
INICIO = date(2026, 10, 19)          # lunes: primer día hábil de trabajo
LIMITE = date(2026, 11, 30)          # «operativo antes de finalizar noviembre»


def habiles_hasta(fin: date) -> int:
    d, n = INICIO, 0
    while d < fin:
        if d.weekday() < 5:
            n += 1
        d += timedelta(days=1)
    return n


def fecha_de(habiles: float) -> date:
    d, n = INICIO, 0
    while n < int(np.ceil(habiles)):
        d += timedelta(days=1)
        if d.weekday() < 5:
            n += 1
    return d


PLAZO = habiles_hasta(LIMITE + timedelta(days=1))   # el 30 cuenta


def tri(a, m, b):
    return RNG.triangular(a, m, b, N)


def riesgo(p, a, m, b):
    """Demora que agrega un riesgo: 0 si no ocurre, triangular si ocurre."""
    return (RNG.random(N) < p) * tri(a, m, b)


# ------------------------------------------------------------------ riesgos
# (probabilidad, demora min/moda/max en días hábiles). Cada uno documentado en PLAN.md §Riesgos.
RIESGOS = {
    # R1 NO es una demora: si la cabecera no pasa nuestras frecuencias no hay piloto en plazo
    # (PLAN §6 lo declara fracaso). Se modela como compuerta: el escenario no llega nunca.
    # Corregido el 15-Oct tras la revisión con DeepSeek y Gemini.
    "R1_RF_cabecera_incompatible": (0.30, 0, 0, 0),
    "R2_enlace_fwcore_gateway":    (0.60, 1, 3, 6),     # modulación y CRC no coinciden con el gateway
    "R3_camino_comando_DR":        (0.40, 2, 3, 6),     # el comando 0x22 no tiene camino hecho en DR
    "R4_info_Nexa_tarde":          (0.50, 2, 4, 8),     # arrancador, cabecera, filosofía de falla
    "R5_integrador_tablero":       (0.40, 3, 6, 12),    # relé, transductores y bornera no listos
    "R6_SSMA_acceso_mina":         (0.50, 2, 5, 10),    # inducción y permisos más largos que lo previsto
    "R7_mapa_modbus_arrancador":   (0.50, 3, 5, 10),    # solo B: registros y cableado RS485 del arrancador
    "R8_bugs_legacy":              (0.35, 2, 4, 7),     # solo C: el v2.1 tiene críticos conocidos
}

APLICA = {
    "A_CONTACTOS_FWCORE": ["R1", "R2", "R3", "R4", "R5", "R6"],
    "B_MODBUS_FWCORE":    ["R1", "R2", "R3", "R4", "R5", "R6", "R7"],
    "C_CONTACTOS_LEGACY": ["R1", "R3", "R4", "R5", "R6", "R8"],
}


def simular(opcion: str, apagado: str | None = None, adjudica: float | None = None,
            con_fat: bool = False, extra_fw=None, extra_sw=None):
    """Días hábiles desde el 19-Oct hasta la SAT firmada, para N escenarios.
    adjudica fija la adjudicación (días hábiles desde el inicio); con_fat devuelve también la FAT.
    extra_fw: función sin argumentos que devuelve N días de firmware ADICIONALES en la rama de
    firmware del piloto (la usa sniffer_estandarizacion_fota.py para medir el impacto).
    extra_sw: lo mismo para la rama de software (diagnóstico remoto)."""
    activos = [k for k in RIESGOS if k.split("_")[0] in APLICA[opcion] and not k.startswith(apagado or "~")]
    d = {k: (riesgo(*RIESGOS[k]) if RIESGOS[k][3] > 0 else np.zeros(N)) for k in activos}
    z = np.zeros(N)
    r = lambda pref: next((v for k, v in d.items() if k.startswith(pref)), z)  # noqa: E731

    # --- hito H1: PRD y arquitectura aprobados (spec-first) ---
    aprobacion = tri(1, 3, 6)

    # --- rama firmware ---
    if opcion == "C_CONTACTOS_LEGACY":  # noqa: SIM108 — las dos ramas llevan su comentario
        enlace = tri(1, 2, 3) + r("R8")                 # parche SET_OUTPUTS + RegPayloadLength en v2.1
    else:
        enlace = tri(1, 2, 4) + r("R2")                 # bring-up paso 5 de fw-core contra gateway
    fw_piloto = aprobacion + tri(1, 2, 3)               # falla segura, realimentación, escalas 4-20
    if opcion == "B_MODBUS_FWCORE":
        fw_piloto = fw_piloto + tri(3, 5, 8) + r("R7")  # maestro Modbus RTU + mapa del arrancador
    if extra_fw is not None:
        fw_piloto = fw_piloto + extra_fw()
    fw_listo = np.maximum(enlace, fw_piloto) + r("R4")

    # --- rama software (diagnóstico remoto) ---
    # Relevado el 15-Oct: DR no tiene NADA del sniffer (ni largo de trama, ni decodificador,
    # ni cola, ni device_type, ni evento WS, ni consumidor Go, ni pantalla).
    decodificador = tri(1, 1.5, 3)                      # register_protocol(0x10) + decodificador
    tuberia = decodificador + tri(2, 3, 4)              # cola, consumidor Go, Mongo, evento WS
    # El mando no es genérico: handler Go + endpoint Python + cmd_type + builder MF 0x10,
    # y el backend no valida rol ni registra quién manda (RF-07 obliga a construirlo).
    comando = np.maximum(aprobacion, decodificador) + tri(3, 4, 6) + tri(1, 2, 3) + r("R3")
    vista = np.maximum(aprobacion, tuberia) + tri(2, 3, 5)
    sw_listo = np.maximum(comando, vista)
    if extra_sw is not None:
        sw_listo = sw_listo + extra_sw()

    # --- hito H3: FAT en banco ---
    fat = np.maximum(fw_listo, sw_listo) + tri(1, 2, 3)

    # --- rama campo (externa a I+D) ---
    adjudicacion = tri(5, 10, 20) if adjudica is None else np.full(N, adjudica)  # [SUPUESTO]
    acceso = adjudicacion + tri(5, 8, 12) + r("R6")     # SSMA, inducción, movilización
    tablero = adjudicacion + tri(8, 12, 18) + r("R5")   # integrador: tablero, relé, transductores

    # --- hito H4/H5: instalación y SAT ---
    instalacion = np.maximum.reduce([fat, acceso, tablero]) + tri(2, 3, 5)
    if "R1_RF_cabecera_incompatible" in d:
        instalacion = np.where(RNG.random(N) < RIESGOS["R1_RF_cabecera_incompatible"][0],
                               np.inf, instalacion)
    sat = instalacion + tri(1, 2, 3)
    return (sat, fat) if con_fat else sat


def resumen(opcion: str) -> dict:
    sat = simular(opcion)
    pesos = {}
    base = float(np.mean(sat <= PLAZO))
    for k in RIESGOS:
        if k.split("_")[0] in APLICA[opcion]:
            sin = float(np.mean(simular(opcion, apagado=k) <= PLAZO))
            pesos[k] = round(sin - base, 3)
    return {
        "p_a_tiempo": round(base, 3),
        "p_viable_rf": round(float(np.mean(np.isfinite(sat))), 3),
        # fechas y holgura: solo de los escenarios donde la RF sirve (los otros no tienen fecha)
        "p50": fecha_de(float(np.percentile(sat[np.isfinite(sat)], 50))).isoformat(),
        "p80": fecha_de(float(np.percentile(sat[np.isfinite(sat)], 80))).isoformat(),
        "holgura_media": round(float(PLAZO - sat[np.isfinite(sat)].mean()), 1),
        "holgura_std": round(float(sat[np.isfinite(sat)].std()), 1),
        "peso_de_cada_riesgo": dict(sorted(pesos.items(), key=lambda kv: -kv[1])),
        "_sat": sat,
    }


# ------------------------------------------------------------------ multicriterio
factors = [
    Factor(name="Holgura", weight=0.40, maximize=True),          # días hábiles de margen al 30-Nov
    Factor(name="EsfuerzoID", weight=0.15, maximize=False),       # días-persona de I+D
    Factor(name="RiesgoTecnico", weight=0.20, maximize=False),    # deuda y fallas en terreno, 0-100
    Factor(name="Escalabilidad", weight=0.25, maximize=True),     # base para caudal y más bombas, 0-100
]

JUICIO = {
    # (media, desvío). Esfuerzo: suma de modas de las tareas de I+D del plan.
    "A_CONTACTOS_FWCORE": {"EsfuerzoID": (21, 3), "RiesgoTecnico": (45, 10), "Escalabilidad": (65, 10)},
    "B_MODBUS_FWCORE":    {"EsfuerzoID": (26, 4), "RiesgoTecnico": (55, 10), "Escalabilidad": (85, 8)},
    "C_CONTACTOS_LEGACY": {"EsfuerzoID": (19, 3), "RiesgoTecnico": (70, 10), "Escalabilidad": (30, 10)},
}

DESC = {
    "A_CONTACTOS_FWCORE": "Contactos + 4-20 mA sobre fw-core (v3). Recomendada en el plan.",
    "B_MODBUS_FWCORE": "V/I por Modbus RTU del arrancador, maestro en fw-core.",
    "C_CONTACTOS_LEGACY": "Contactos + 4-20 mA sobre el firmware v2.1 de terreno, parchado.",
}


async def main():
    sims = {k: resumen(k) for k in APLICA}

    print(f"\nPlazo: {PLAZO} días hábiles desde {INICIO} hasta {LIMITE} inclusive. N={N}")
    for k, s in sims.items():
        print(f"\n{k}: P(a tiempo)={s['p_a_tiempo']:.0%}  P(RF viable)={s['p_viable_rf']:.0%}  p50={s['p50']}  p80={s['p80']}  "
              f"holgura={s['holgura_media']}±{s['holgura_std']} d")
        for rk, dv in s["peso_de_cada_riesgo"].items():
            print(f"   sin {rk:<30} → +{dv:.0%}")

    # condicional: si la RF de la cabecera ya estuviera confirmada
    cond = {k: round(float(np.mean(simular(k, apagado="R1") <= PLAZO)), 3) for k in APLICA}
    print(f"\nP(a tiempo | cabecera RF compatible): {cond}")

    # lo que controla I+D: la FAT en banco
    _, fat = simular("A_CONTACTOS_FWCORE", con_fat=True)
    fat_p = {q: fecha_de(float(np.percentile(fat, q))).isoformat() for q in (50, 80, 95)}
    print(f"FAT (opción A) p50/p80/p95: {fat_p}")

    # sensibilidad a la fecha de adjudicación (opción A)
    adj = {}
    for dia in (date(2026, 10, 23), date(2026, 10, 30), date(2026, 11, 6), date(2026, 11, 13)):
        h = habiles_hasta(dia)
        sat = simular("A_CONTACTOS_FWCORE", adjudica=h)
        sat_ok = simular("A_CONTACTOS_FWCORE", adjudica=h, apagado="R1")
        adj[dia.isoformat()] = {"p": round(float(np.mean(sat <= PLAZO)), 3),
                                "p_si_rf_ok": round(float(np.mean(sat_ok <= PLAZO)), 3)}
    print(f"P(a tiempo) según adjudicación (A): {adj}")

    fw = UnifiedDecisionFramework()
    for f in factors:
        fw.add_factor(f)
    for k, s in sims.items():
        vars_ = {f: UncertainVariable(f, DistributionType.NORMAL, list(v)) for f, v in JUICIO[k].items()}
        vars_["Holgura"] = UncertainVariable(
            "Holgura", DistributionType.NORMAL, [s["holgura_media"], max(s["holgura_std"], 0.5)]
        )
        fw.add_option(DecisionOption(name=k, description=DESC[k], variables=vars_))

    results = await fw.run_analysis(mode="standard")
    print("\n" + "=" * 60)
    print(f"DECISION: {analysis_name}")
    print("=" * 60)
    print(results.get("explanation", "N/A"))

    out = Path("results") / f"{analysis_name}.json"
    out.parent.mkdir(exist_ok=True)
    with open(out, "w") as f:
        json.dump(
            {
                "name": analysis_name,
                "date": analysis_date,
                "plazo_habiles": PLAZO,
                "riesgos": RIESGOS,
                "simulacion": {k: {kk: vv for kk, vv in s.items() if kk != "_sat"} for k, s in sims.items()},
                "p_a_tiempo_si_rf_ok": cond,
                "fat_opcion_a": fat_p,
                "sensibilidad_adjudicacion_a": adj,
                "factors": [(fac.name, fac.weight) for fac in factors],
                "juicio": JUICIO,
                "options": DESC,
                "raw": {k: v for k, v in results.items() if k != "explanation"},
            },
            f,
            indent=2,
            default=str,
        )
    print(f"\nResultados guardados en {out}")


if __name__ == "__main__":
    asyncio.run(main())
