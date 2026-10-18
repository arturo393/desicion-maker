"""
Analysis: Piloto Nexa — ¿cuánto cambia el plazo si el desarrollo lo hacen agentes en paralelo?
Purpose: Re-simular la FAT y la SAT con el trabajo repartido en agentes que corren en paralelo, sin
  suponer paralelismo gratis: lo que NO se multiplica con agentes es la revisión humana, el banco (una
  placa de sniffer y un gateway) y la firma del PRD. Compara la dotación de solo humanos con agentes y
  uno o dos revisores.
Created: 2026-10-16
Version: 1.1

Fuente de las tareas: fw-snifferTelemetry docs/proyectos/nexa-cerro-lindo/PLAN.md §4 y §10 (moda en
días-persona humanos). Todo factor de velocidad de los agentes es [SUPUESTO] sin medición propia.

Modelo (por escenario, 2000 corridas):
  - Cada tarea: desarrollo -> revisión -> banco (si tiene) -> lista. Sale cuando sus dependencias
    están listas, y las que esperan la firma del PRD (H1), además, cuando H1 está.
  - Desarrollo con agente: días humanos × triangular(0,25; 0,4; 0,7). Con 30 % de probabilidad la
    revisión lo devuelve y se repite la mitad del desarrollo y otra revisión.
  - Revisión: 0,1 día + 10 % de los días humanos de la tarea, por revisor (cola única).
  - Banco: un solo recurso; sus días no se aceleran.
  - Agentes simultáneos: 5.
  - La SAT usa la misma cadena externa que nexa_piloto_bombeo_plazo (adjudicación, acceso, tablero,
    riesgo de la cabecera RF como compuerta).
"""

import asyncio
import heapq
import json
import sys
from datetime import datetime
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))

import nexa_piloto_bombeo_plazo as nexa  # noqa: E402

from decision_maker.core.models import DecisionOption, DistributionType, Factor, UncertainVariable  # noqa: E402
from decision_maker.core.orchestrator import UnifiedDecisionFramework  # noqa: E402

analysis_name = "nexa_trabajo_paralelo"
analysis_date = datetime.now().isoformat()
RNG = np.random.default_rng(20261016)
N = 2000

# id: (días humanos, días de banco, dependencias, espera H1, conveniente)
TAREAS = {
    "T18v_vectores": (0.5, 0.0, [], False, False),
    "T1_radio": (4.5, 1.5, [], False, False),
    "T20_uid": (0.5, 0.0, [], False, False),
    "T21_opcodes": (1.0, 0.0, [], False, False),
    "T9_bootloader": (2.0, 0.5, [], False, False),
    "T18_fw_v3": (2.0, 0.0, ["T18v_vectores", "T21_opcodes"], False, False),
    "T5_fw_piloto": (2.0, 0.5, ["T1_radio"], True, False),
    "T10_fota_consola": (2.5, 0.5, ["T9_bootloader"], True, False),
    "T11_rollback": (2.5, 1.0, ["T9_bootloader"], True, False),
    "T13_fota_lora_fw": (1.0, 0.0, ["T10_fota_consola"], True, False),
    "T17b_sf_rollback": (1.0, 0.5, ["T1_radio"], False, False),
    "T2_decoder": (1.5, 0.0, ["T18v_vectores"], False, False),
    "T19_poller": (0.5, 0.0, [], False, False),
    "T27_http_hilos": (0.5, 0.0, [], False, False),
    "T2b_tuberia": (3.0, 0.0, ["T2_decoder"], False, False),
    "T14_fota_lora_srv": (4.0, 0.0, ["T27_http_hilos", "T13_fota_lora_fw"], True, False),
    "T3_ordenes": (4.0, 0.0, ["T2b_tuberia"], True, False),
    "T3b_rol": (2.0, 0.0, [], True, False),
    "T22_ritmo": (0.5, 0.0, ["T3_ordenes"], True, False),
    "T23_umbral": (1.5, 0.0, ["T2b_tuberia"], False, False),
    "T26_alta": (0.5, 0.0, ["T2b_tuberia"], False, False),
    "T4_tarjeta": (3.0, 0.0, ["T2b_tuberia", "T23_umbral"], True, False),
    "T24_alarmas": (0.5, 0.0, ["T2b_tuberia"], False, False),
    "T25_ntp": (0.5, 0.0, [], False, False),
    "T15_suite": (4.5, 0.5, ["T1_radio"], True, False),
    "T29_config": (1.5, 0.0, ["T2b_tuberia"], False, True),
    "T30_respaldo": (1.0, 0.0, [], False, True),
    "T31_ci_go": (1.5, 0.0, [], False, True),
    "T32_guardas_next": (1.0, 0.0, [], False, True),
    "T33_migraciones": (1.5, 0.0, ["T2b_tuberia"], False, True),
    "T34_consulta_info": (2.5, 0.0, ["T18_fw_v3"], False, True),
}
FINALES = {"T6_fat": (2.0, 2.0), "T8_kit": (2.0, 0.0)}  # días humanos, días de banco


def _camino(k, tareas, memo=None) -> float:
    """Días humanos de k más la cadena más larga de tareas que dependen de k."""
    memo = {} if memo is None else memo
    if k in memo:
        return memo[k]
    hijos = [h for h, v in tareas.items() if k in v[2]]
    memo[k] = tareas[k][0] + max((_camino(h, tareas, memo) for h in hijos), default=0.0)
    return memo[k]


def simular_dev(convenientes: bool, revisores: int, agentes: int, humanos: bool, detalle: bool = False):
    """Días hábiles hasta terminar la FAT. Con humanos=True: dos personas, sin agentes ni revisión
    aparte (el modelo del 15-Oct, para comparar)."""
    tareas = {k: v for k, v in TAREAS.items() if convenientes or not v[4]}
    h1 = nexa.tri(1, 3, 6)[0]
    fin = {}
    if humanos:
        # dos personas en paralelo (firmware y software), cada una en serie
        fw_ids = [k for k in tareas if k.startswith(("T1_", "T20", "T21", "T9", "T18", "T5", "T10",
                                                         "T11", "T13", "T17", "T34"))]
        fw = sum(tareas[k][0] * RNG.triangular(0.8, 1, 1.5) for k in fw_ids)
        sw = sum(v[0] * RNG.triangular(0.8, 1, 1.5) for k, v in tareas.items() if k not in fw_ids)
        listo = max(fw, sw, h1)
        return listo + FINALES["T6_fat"][0]
    # agentes: cola de eventos
    pendientes = dict(tareas)
    revisores_libres = [0.0] * revisores
    banco_libre = 0.0
    agentes_libres = [0.0] * agentes
    # Prioridad por camino crítico: lo que más trabajo tiene colgado detrás sale primero (v1.1).
    # La v1.0 ordenaba por duración y dejaba para el final tareas cortas que destraban a otras, como
    # los vectores dorados, contra la regla «contratos primero» del plan.
    orden = sorted(pendientes, key=lambda k: -_camino(k, tareas))
    while pendientes:
        avanzo = False
        for k in list(orden):
            if k not in pendientes:
                continue
            dias, banco, deps, espera_h1, _ = pendientes[k]
            if any(d not in fin for d in deps if d in tareas):
                continue
            inicio = max([fin[d] for d in deps if d in fin] + [h1 if espera_h1 else 0.0])
            heapq.heapify(agentes_libres)
            a = heapq.heappop(agentes_libres)
            t = max(inicio, a)
            dev = dias * RNG.triangular(0.25, 0.4, 0.7)
            t += dev
            heapq.heappush(agentes_libres, t)
            rondas = 2 if RNG.random() < 0.3 else 1
            for r in range(rondas):
                if r == 1:
                    t += dev * 0.5
                heapq.heapify(revisores_libres)
                rv = heapq.heappop(revisores_libres)
                t = max(t, rv) + 0.1 + 0.1 * dias
                heapq.heappush(revisores_libres, t)
            if banco > 0:
                t = max(t, banco_libre) + banco
                banco_libre = t
            fin[k] = t
            del pendientes[k]
            orden.remove(k)
            avanzo = True
        if not avanzo:
            raise RuntimeError(f"dependencias sin resolver: {list(pendientes)}")
    listo = max(fin.values())
    fat = max(listo, banco_libre) + FINALES["T6_fat"][1]
    return (fat, fin, h1) if detalle else fat


def sat_desde(fat: np.ndarray) -> np.ndarray:
    """La misma cadena externa que nexa_piloto_bombeo_plazo."""
    adj = nexa.tri(5, 10, 20)
    r6 = nexa.riesgo(*nexa.RIESGOS["R6_SSMA_acceso_mina"])
    r5 = nexa.riesgo(*nexa.RIESGOS["R5_integrador_tablero"])
    acceso = adj + nexa.tri(5, 8, 12) + r6
    tablero = adj + nexa.tri(8, 12, 18) + r5
    inst = np.maximum.reduce([fat, acceso, tablero]) + nexa.tri(2, 3, 5)
    inst = np.where(np.random.default_rng(7).random(nexa.N) < 0.30, np.inf, inst)
    return inst + nexa.tri(1, 2, 3)


ESCENARIOS = {
    "S0_dos_humanos_imprescindibles": dict(convenientes=False, revisores=1, agentes=5, humanos=True),
    "S1_agentes_1revisor_imprescindibles": dict(convenientes=False, revisores=1, agentes=5, humanos=False),
    "S2_agentes_1revisor_todo": dict(convenientes=True, revisores=1, agentes=5, humanos=False),
    "S3_agentes_2revisores_todo": dict(convenientes=True, revisores=2, agentes=5, humanos=False),
}


def medir(cfg):
    fats = np.array([simular_dev(**cfg) for _ in range(N)])
    fat_n = np.resize(fats, nexa.N)
    sat = sat_desde(fat_n)
    return {
        "fat_p50": nexa.fecha_de(float(np.percentile(fats, 50))).isoformat(),
        "fat_p80": nexa.fecha_de(float(np.percentile(fats, 80))).isoformat(),
        "p_a_tiempo": round(float(np.mean(sat <= nexa.PLAZO)), 3),
        "p_a_tiempo_si_rf_ok": round(float(np.mean(sat[np.isfinite(sat)] <= nexa.PLAZO)), 3),
        "_fats": fats,
    }


async def main():
    m = {k: medir(c) for k, c in ESCENARIOS.items()}
    for k, r in m.items():
        print(f"{k:<38} FAT p50={r['fat_p50']} p80={r['fat_p80']}  P(a tiempo)={r['p_a_tiempo']:.1%}"
              f"  (si la RF sirve {r['p_a_tiempo_si_rf_ok']:.1%})")

    # Multicriterio sobre la dotación: plazo, carga de revisión y riesgo de calidad (juicio).
    carga = {"S0_dos_humanos_imprescindibles": (20, 8), "S1_agentes_1revisor_imprescindibles": (60, 10),
             "S2_agentes_1revisor_todo": (85, 8), "S3_agentes_2revisores_todo": (55, 10)}
    calidad = {"S0_dos_humanos_imprescindibles": (35, 10), "S1_agentes_1revisor_imprescindibles": (40, 10),
               "S2_agentes_1revisor_todo": (55, 12), "S3_agentes_2revisores_todo": (35, 10)}
    alcance = {"S0_dos_humanos_imprescindibles": (50, 5), "S1_agentes_1revisor_imprescindibles": (50, 5),
               "S2_agentes_1revisor_todo": (90, 5), "S3_agentes_2revisores_todo": (90, 5)}
    fw = UnifiedDecisionFramework()
    for f in [Factor(name="PATiempo", weight=0.35, maximize=True),
              Factor(name="CargaRevision", weight=0.20, maximize=False),
              Factor(name="RiesgoCalidad", weight=0.20, maximize=False),
              Factor(name="Alcance", weight=0.25, maximize=True)]:
        fw.add_factor(f)
    for k, r in m.items():
        fw.add_option(DecisionOption(name=k, description=k, variables={
            "PATiempo": UncertainVariable("PATiempo", DistributionType.NORMAL, [r["p_a_tiempo"] * 100, 1.5]),
            "CargaRevision": UncertainVariable("CargaRevision", DistributionType.NORMAL, list(carga[k])),
            "RiesgoCalidad": UncertainVariable("RiesgoCalidad", DistributionType.NORMAL, list(calidad[k])),
            "Alcance": UncertainVariable("Alcance", DistributionType.NORMAL, list(alcance[k])),
        }))
    results = await fw.run_analysis(mode="standard")
    print("\n" + "=" * 60)
    print(results.get("explanation", "N/A"))

    out = Path("results") / f"{analysis_name}.json"
    out.parent.mkdir(exist_ok=True)
    with open(out, "w") as f:
        json.dump({"name": analysis_name, "date": analysis_date, "tareas": TAREAS,
                   "escenarios": ESCENARIOS,
                   "medicion": {k: {kk: vv for kk, vv in r.items() if not kk.startswith("_")} for k, r in m.items()},
                   "raw": {k: v for k, v in results.items() if k != "explanation"}}, f, indent=2, default=str)
    print(f"\nResultados guardados en {out}")


if __name__ == "__main__":
    asyncio.run(main())
