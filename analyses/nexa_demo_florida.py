"""
Analysis: Demo en Florida para Nexa — ¿llega funcionando el lunes 16-Nov-2026, con qué alcance, y cuándo
hay que salir con el equipo?
Purpose: Nueva meta del 19-Oct-2026: el sistema tiene que estar funcionando en Florida el 16-Nov para
  mostrárselo a Nexa. Se reutiliza el modelo en paralelo (nexa_trabajo_paralelo: agentes, revisión
  humana y banco como recursos únicos) con tres alcances de demo y uno o dos revisores, y se le agrega
  la cadena hacia atrás desde el 16-Nov: kit, salida, viaje, inducción, montaje y ensayo.
Created: 2026-10-19
Version: 1.0

Supuestos sin fuente [SUPUESTO], los que más pesan:
  - En sitio (viaje + inducción + montaje + ensayo): 2-3-4 días hábiles.
  - La unidad de demo de hardware (sniffer en gabinete con relés) está lista entre el día hábil 10 y
    el 18 desde hoy (moda 14 = 6-Nov).
  - Para la demo la cadena externa de Nexa (adjudicación, acceso a Cerro Lindo, cabecera RF) NO aplica.
"""

import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))

import nexa_piloto_bombeo_plazo as nexa  # noqa: E402
import nexa_trabajo_paralelo as par  # noqa: E402

from decision_maker.core.models import DecisionOption, DistributionType, Factor, UncertainVariable  # noqa: E402
from decision_maker.core.orchestrator import UnifiedDecisionFramework  # noqa: E402

analysis_name = "nexa_demo_florida"
analysis_date = datetime.now().isoformat()
RNG = np.random.default_rng(20261019)
N = 2000
LIMITE = 20  # días hábiles del 19-Oct al viernes 13-Nov inclusive: el lunes 16 se muestra

LATIDO = {"T47_latido": (1.0, 0.0, ["T1_radio", "T2b_tuberia"], False, False)}

# Qué entra en cada alcance (ids de nexa_trabajo_paralelo.TAREAS).
MINIMA = {"T18v_vectores", "T1_radio", "T20_uid", "T21_opcodes", "T18_fw_v3", "T5_fw_piloto",
          "T9_bootloader", "T2_decoder", "T19_poller", "T2b_tuberia", "T3_ordenes", "T3b_rol",
          "T22_ritmo", "T23_umbral", "T26_alta", "T4_tarjeta", "T24_alarmas", "T25_ntp"}
ALCANCES = {
    # Lo que se ve en la demo: mando con confirmación, V/I con su edad, alarmas, falla segura.
    "DEMO_MINIMA": MINIMA,
    # + actualizar por cable y la Suite reconociendo el v3 (no hay que llevar ST-Link para corregir).
    "DEMO_MAS_FOTA_CONSOLA": MINIMA | {"T10_fota_consola", "T11_rollback", "T15_suite"},
    # Todo lo del plan, incluida la FOTA por LoRa y los convenientes.
    "TODO": set(par.TAREAS),
}
FAT_DEMO = (1.5, 1.5)  # FAT reducida a los casos de la demo: días humanos, días de banco


def correr(alcance: str, revisores: int):
    tareas = {k: v for k, v in par.TAREAS.items() if k in ALCANCES[alcance]}
    tareas.update(LATIDO)
    original_t, original_f = par.TAREAS, par.FINALES
    par.TAREAS = tareas
    par.FINALES = {"T6_fat": FAT_DEMO if alcance != "TODO" else original_f["T6_fat"], "T8_kit": (1, 0)}
    try:
        fat = np.array([par.simular_dev(convenientes=True, revisores=revisores, agentes=5, humanos=False)
                        for _ in range(N)])
    finally:
        par.TAREAS, par.FINALES = original_t, original_f
    kit = RNG.triangular(0.5, 1, 1.5, N)
    unidad = RNG.triangular(10, 14, 18, N)
    salida = np.maximum(fat + kit, unidad)
    en_sitio = RNG.triangular(2, 3, 4, N)
    lista = salida + en_sitio
    return {
        "fat_p80": nexa.fecha_de(float(np.percentile(fat, 80))).isoformat(),
        "salida_p50": nexa.fecha_de(float(np.percentile(salida, 50))).isoformat(),
        "salida_p80": nexa.fecha_de(float(np.percentile(salida, 80))).isoformat(),
        "p_demo_a_tiempo": round(float(np.mean(lista <= LIMITE)), 3),
        "p_si_unidad_lista_dia10": round(float(np.mean(np.maximum(fat + kit, 10) + en_sitio <= LIMITE)), 3),
    }


async def main():
    casos = {(a, r): correr(a, r) for a in ALCANCES for r in (1, 2)}
    for (a, r), m in casos.items():
        print(f"{a:<22} {r} revisor(es)  FAT p80={m['fat_p80']}  salida p50={m['salida_p50']} "
              f"p80={m['salida_p80']}  P(demo el 16-Nov)={m['p_demo_a_tiempo']:.0%}  "
              f"(unidad lista el 30-Oct: {m['p_si_unidad_lista_dia10']:.0%})")
    # La salida más tardía que todavía llega, con el sitio en su p80 (3,6 días hábiles).
    p80_sitio = float(np.percentile(RNG.triangular(2, 3, 4, 100000), 80))
    print(f"\nSalida más tardía para llegar con el sitio en su p80: {nexa.fecha_de(LIMITE - p80_sitio)}")

    valor = {"DEMO_MINIMA": (55, 8), "DEMO_MAS_FOTA_CONSOLA": (70, 8), "TODO": (85, 8)}
    riesgo = {"DEMO_MINIMA": (25, 8), "DEMO_MAS_FOTA_CONSOLA": (35, 8), "TODO": (65, 10)}
    fw = UnifiedDecisionFramework()
    for f in [Factor(name="PDemo", weight=0.55, maximize=True),
              Factor(name="ValorDemo", weight=0.20, maximize=True),
              Factor(name="RiesgoFrenteANexa", weight=0.25, maximize=False)]:
        fw.add_factor(f)
    for (a, r), m in casos.items():
        fw.add_option(DecisionOption(name=f"{a}_{r}rev", description=f"{a}, {r} revisor(es)", variables={
            "PDemo": UncertainVariable("PDemo", DistributionType.NORMAL, [m["p_demo_a_tiempo"] * 100, 2]),
            "ValorDemo": UncertainVariable("ValorDemo", DistributionType.NORMAL, list(valor[a])),
            "RiesgoFrenteANexa": UncertainVariable("RiesgoFrenteANexa", DistributionType.NORMAL, list(riesgo[a])),
        }))
    results = await fw.run_analysis(mode="standard")
    print("\n" + "=" * 60)
    print(results.get("explanation", "N/A"))

    out = Path(__file__).resolve().parent.parent / "results" / f"{analysis_name}.json"
    out.parent.mkdir(exist_ok=True)
    with open(out, "w") as f:
        json.dump({"name": analysis_name, "date": analysis_date,
                   "alcances": {k: sorted(v) for k, v in ALCANCES.items()},
                   "casos": {f"{a}_{r}rev": m for (a, r), m in casos.items()},
                   "raw": {k: v for k, v in results.items() if k != "explanation"}}, f, indent=2, default=str)
    print(f"\nResultados guardados en {out}")


if __name__ == "__main__":
    asyncio.run(main())
