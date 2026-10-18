"""
Analysis: Sniffer de telemetría — bootloader + FOTA (UART y RS485) y estandarización del firmware
Purpose: Decidir CÓMO y CUÁNDO el sniffer (fw-core, STM32G474RE) incorpora bootloader + FOTA y se
  alinea con el resto de los firmwares G474 de UQOMM (driver LoRa, contrato del enlace, FOTA),
  midiendo el impacto en el piloto Nexa Cerro Lindo con el mismo modelo de plazo.
Created: 2026-10-16
Version: 2.0

Hechos de entrada (relevados el 16-Oct-2026, ver fw-snifferTelemetry/docs/proyectos/nexa-cerro-lindo/):
  - fw-ulad NO tiene bootloader ni FOTA (STM32F030, se graba por SWD). La FOTA real de UQOMM es la
    familia A/B dual-bank de VLAD25, gateway y Rutherford, los tres sobre STM32G474 como el sniffer.
  - bootloader.c existe en 4 variantes; FotaService.hpp/FotaCrc.hpp idénticos entre gateway y
    Rutherford; ninguna copia tiene transporte RS485. Sin rollback automático en ninguna.
  - fw-core ocupa ~31 KB de 512 KB: entran bootloader + staging + app.
  - El opcode 0x19 (FOTA_BEGIN en gateway/VLAD25) es CHANGE_SLEEP_TIME_RECIVED en el cable del
    sniffer; fw-core lo declara y no lo atiende.

Opciones:
  O1_DIFERIR          - piloto sin bootloader (SWD); estandarizar después del piloto
  O2_COPIA_LOCAL      - copiar bootloader + FotaService de Rutherford/gateway a fw-core ahora
  O3_LIB_COMUN_AHORA  - crear la biblioteca común (contrato LoRa + driver fw-core + FOTA) y que el
                        sniffer la adopte dentro del piloto
  O4_BASE_GATEWAY     - rehacer fw-core sobre los módulos de fw-gateway2lora (sx127x, fota, stm32)
  O5_COPIA_PREPARADA  - como O2, pero los archivos de FOTA entran byte a byte iguales a los del
                        gateway, con un test que lo exige; la biblioteca común se extrae después
"""

import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))

import nexa_piloto_bombeo_plazo as nexa  # noqa: E402  — mismo modelo de plazo del piloto

from decision_maker.core.models import DecisionOption, DistributionType, Factor, UncertainVariable  # noqa: E402
from decision_maker.core.orchestrator import UnifiedDecisionFramework  # noqa: E402

analysis_name = "sniffer_estandarizacion_fota"
analysis_date = datetime.now().isoformat()

# Días hábiles de FIRMWARE que cada opción agrega DENTRO del piloto (mín, moda, máx).
# Desglose de O2: portar bootloader y FotaSlots al RE 1-2 d · relink a 0x08040000 + VTOR 0,5 d ·
# FotaService sobre el router de comandos por USART1 1-1,5 d · transporte RS485 con DE/RE 1 d ·
# herramienta de PC 0,5-1 d · tests de host + banco con corte de energía 1-2 d.
# Versión 2 (16-Oct, después de la revisión con DeepSeek y Gemini 4, verificada contra el código):
#  - UART y RS485 son buses LOCALES: actualizar por ahí igual exige bajar al tablero. Lo que evita
#    el viaje es la FOTA por LoRa. RiesgoCampo deja de premiar a UART/RS485 como si lo evitaran.
#  - Salir con la app en 0x08000000 (O1) cierra el camino: particionar después exige SWD en la mina.
#  - El bootloader heredado NO tiene vuelta atrás: una app nueva colgada no puede recibir otra FOTA,
#    y se recupera solo por SWD (fw-vlad/vlad25_vhf/bootloader/README.md:6,189-190).
#  - El esfuerzo "después" de O5 estaba sesgado a su favor (10,0 vs 11,7): se iguala a O2.
#  - RS485: el DE está en PC15 como GPIO (no hay DEM por hardware); el bus lo comparte el
#    PLC/arrancador del integrador, que puede ser el maestro.
EXTRA_PILOTO = {
    "O1_DIFERIR": None,                      # app en 0x08000000, sin bootloader
    "O1B_SOLO_PARTICION": (1.5, 2, 3),       # bootloader + app en banco 2, sin FOTA todavía
    "O2_COPIA_LOCAL": (4, 6, 9),             # FOTA por UART y RS485, copia local
    "O3_LIB_COMUN_AHORA": (6, 9, 14),
    "O4_BASE_GATEWAY": (10, 15, 25),
    "O5_COPIA_PREPARADA": (4.5, 6.5, 10),    # como O2, con test de igualdad contra el gateway
    "O6_UART_CONFIRMA": (3, 4.5, 7),         # bootloader + FOTA solo por consola + confirmación de arranque
    "O7_UART_ROLLBACK": (5, 7, 10),          # O6 + imagen anterior conservada y vuelta atrás automática
}

DESPUES = {
    "O1_DIFERIR": (8, 11, 16),
    "O1B_SOLO_PARTICION": (6, 9, 13),
    "O2_COPIA_LOCAL": (3, 5, 8),
    "O3_LIB_COMUN_AHORA": (1, 2, 3),
    "O4_BASE_GATEWAY": (1, 2, 4),
    "O5_COPIA_PREPARADA": (3, 5, 7),
    "O6_UART_CONFIRMA": (4, 6, 9),           # falta RS485 (si se quiere), rollback y biblioteca
    "O7_UART_ROLLBACK": (3, 4.5, 7),
}

# RiesgoCampo: consecuencia de tener que actualizar la unidad instalada (viaje + posibilidad de
# dejarla inservible). UART/RS485 ya no lo bajan a 25: solo evitan el ST-Link. Lo que lo baja es la
# vuelta atrás (no queda inservible) y, a futuro, la FOTA por LoRa (fuera del piloto en todas).
JUICIO = {
    "O1_DIFERIR":         {"RiesgoCampo": (90, 5),  "DeudaCopias": (40, 10), "RiesgoTecnico": (10, 5)},
    "O1B_SOLO_PARTICION": {"RiesgoCampo": (75, 8),  "DeudaCopias": (45, 10), "RiesgoTecnico": (15, 6)},
    "O2_COPIA_LOCAL":     {"RiesgoCampo": (60, 10), "DeudaCopias": (80, 8),  "RiesgoTecnico": (40, 10)},
    "O3_LIB_COMUN_AHORA": {"RiesgoCampo": (60, 10), "DeudaCopias": (15, 8),  "RiesgoTecnico": (60, 12)},
    "O4_BASE_GATEWAY":    {"RiesgoCampo": (60, 10), "DeudaCopias": (30, 10), "RiesgoTecnico": (80, 10)},
    "O5_COPIA_PREPARADA": {"RiesgoCampo": (60, 10), "DeudaCopias": (35, 10), "RiesgoTecnico": (40, 10)},
    "O6_UART_CONFIRMA":   {"RiesgoCampo": (60, 10), "DeudaCopias": (60, 10), "RiesgoTecnico": (25, 8)},
    "O7_UART_ROLLBACK":   {"RiesgoCampo": (40, 10), "DeudaCopias": (60, 10), "RiesgoTecnico": (35, 10)},
}

DESC = {
    "O1_DIFERIR": "Piloto sin bootloader, app en 0x08000000; todo después (exige SWD en la mina para particionar).",
    "O1B_SOLO_PARTICION": "Bootloader y app en banco 2 desde el piloto, sin FOTA todavía.",
    "O2_COPIA_LOCAL": "Copia del bootloader y FotaService, FOTA por UART y RS485 en el piloto.",
    "O3_LIB_COMUN_AHORA": "Biblioteca común nueva (contrato + driver + FOTA), adoptada por el sniffer en el piloto.",
    "O4_BASE_GATEWAY": "fw-core rehecho sobre los módulos del gateway.",
    "O5_COPIA_PREPARADA": "Como O2, con test de igualdad contra el gateway; biblioteca común después.",
    "O6_UART_CONFIRMA": "Bootloader + FOTA solo por consola UART + confirmación de arranque; RS485 después.",
    "O7_UART_ROLLBACK": "O6 + imagen anterior conservada y vuelta atrás automática si la nueva no confirma.",
}

factors = [
    Factor(name="PATiempo", weight=0.30, maximize=True),       # P(piloto operativo al 30-Nov), en %
    Factor(name="RiesgoCampo", weight=0.20, maximize=False),
    Factor(name="RiesgoTecnico", weight=0.20, maximize=False),
    Factor(name="DeudaCopias", weight=0.15, maximize=False),
    Factor(name="Esfuerzo12m", weight=0.15, maximize=False),   # días-persona piloto + después
]


def medir(op: str) -> dict:
    tri_args = EXTRA_PILOTO[op]
    extra = None if tri_args is None else (lambda: nexa.tri(*tri_args))
    sat, fat = nexa.simular("A_CONTACTOS_FWCORE", con_fat=True, extra_fw=extra)
    ok = np.isfinite(sat)
    a = 0.0 if tri_args is None else (tri_args[0] + tri_args[1] + tri_args[2]) / 3
    d = sum(DESPUES[op]) / 3
    return {
        "p_a_tiempo": round(float(np.mean(sat <= nexa.PLAZO)), 3),
        "fat_p50": nexa.fecha_de(float(np.percentile(fat, 50))).isoformat(),
        "fat_p80": nexa.fecha_de(float(np.percentile(fat, 80))).isoformat(),
        "sat_p80_si_rf_ok": nexa.fecha_de(float(np.percentile(sat[ok], 80))).isoformat(),
        "esfuerzo_piloto": round(a, 1),
        "esfuerzo_12m": round(a + d, 1),
    }


async def main():
    m = {op: medir(op) for op in EXTRA_PILOTO}
    for op, r in m.items():
        print(f"{op:<20} P(a tiempo)={r['p_a_tiempo']:.1%}  FAT p50/p80={r['fat_p50']}/{r['fat_p80']}  "
              f"SAT p80 (RF ok)={r['sat_p80_si_rf_ok']}  esfuerzo piloto={r['esfuerzo_piloto']} d  "
              f"12 meses={r['esfuerzo_12m']} d")

    fw = UnifiedDecisionFramework()
    for f in factors:
        fw.add_factor(f)
    for op, r in m.items():
        v = {f: UncertainVariable(f, DistributionType.NORMAL, list(x)) for f, x in JUICIO[op].items()}
        v["PATiempo"] = UncertainVariable("PATiempo", DistributionType.NORMAL, [r["p_a_tiempo"] * 100, 1.5])
        v["Esfuerzo12m"] = UncertainVariable("Esfuerzo12m", DistributionType.NORMAL,
                                             [r["esfuerzo_12m"], r["esfuerzo_12m"] * 0.2 + 0.5])
        fw.add_option(DecisionOption(name=op, description=DESC[op], variables=v))

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
                "medicion": {k: {kk: vv for kk, vv in r.items() if not kk.startswith("_")} for k, r in m.items()},
                "extra_piloto": EXTRA_PILOTO,
                "despues": DESPUES,
                "juicio": JUICIO,
                "factors": [(fac.name, fac.weight) for fac in factors],
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
