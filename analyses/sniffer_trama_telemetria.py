"""
Analysis: Sniffer de telemetría — ¿trama de telemetría nueva, o se queda la actual?
Purpose: Decidir el formato del payload de telemetría que el sniffer (fw-core) manda por LoRa y que
  el decodificador nuevo de diagnóstico remoto va a leer, antes de escribir ese decodificador (T2 del
  plan Nexa). Todo va DENTRO de la trama RDSS (decisión D15: no se cambia el encuadre).
Created: 2026-10-16
Version: 2.0

Hechos de entrada (fw-snifferTelemetry/docs/especificaciones/SPEC_Protocolo.md §6, medidos leyendo
el código el 16-Oct-2026):
  - Payload actual 33 B: UID de 12 B en CADA trama + 7 valores digitales de 1 byte + 7 analógicos de
    16 bits (incluye ecos de salidas analógicas que el hardware Candelaria no tiene). Trama 42 B.
  - En SF9 (contrato del gateway propio): 42 B = 366 ms; 23 B = 243 ms. Achicar ahorra ~1/3 del aire.
  - Con gateway propio y un solo sniffer, el canal no escasea (7 % a 5 s).
  - Diagnóstico remoto no tiene NADA del sniffer: el decodificador se escribe de cero en cualquier opción.
  - Los sniffers de terreno (v2.x) siguen con el formato actual y los lee el stack viejo (.205).
  - nanopb cuesta ~7,4 KB de flash (medido en fw-gateway2lora); fw-core ocupa ~31 KB de 512 KB.

Opciones:
  F0_ACTUAL        - se queda el payload actual; el decodificador nuevo lo lee tal cual
  F1_ACTUAL_MAS    - el actual + un comando de identidad aparte; sin secuencia ni versión
  F2_V3_COMPACTA   - opcode nuevo aditivo: versión, secuencia, banderas, E/S en bits, canales
                     configurados; UID solo en trama de identidad
  F3_TLV           - opcode nuevo con campos etiqueta-largo-valor (autodescriptivo)
  F4_PROTOBUF_RDSS - payload protobuf (nanopb) dentro de la trama RDSS
"""

import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))

import nexa_piloto_bombeo_plazo as nexa  # noqa: E402

from decision_maker.core.models import DecisionOption, DistributionType, Factor, UncertainVariable  # noqa: E402
from decision_maker.core.orchestrator import UnifiedDecisionFramework  # noqa: E402

analysis_name = "sniffer_trama_telemetria"
analysis_date = datetime.now().isoformat()

# Versión 2 (16-Oct, después de la revisión con DeepSeek v4 Pro y Gemini 4 Argon, verificada contra
# el código). Correcciones a la v1:
#  - InfoOperativa (secuencia, banderas, frescura) son CAMPOS, no propiedades de F2: F3/F4/F5 los
#    llevan igual. Se iguala entre las opciones nuevas.
#  - Evolución: un formato posicional (F2) no deja saltar lo desconocido; TLV y protobuf sí. F2 baja.
#  - P(a tiempo) no discrimina (25,3-25,5 % en todas): baja de 20 % a 5 % de peso.
#  - Nueva F5, propuesta por los dos revisores: cabecera fija (versión, secuencia, eco del último
#    comando, banderas con un bit de falla invariante, id corto de 4 B) + cuerpo TLV.
#  - Verificado: el module_id de RDSS está fijo en 0x01 en fw-core (app/main.cpp:439), así que no
#    identifica al equipo; F2 "UID solo al arrancar" deja tramas sin dueño tras reiniciar el servidor.
EXTRA = {
    "F0_ACTUAL": (None, None),
    "F1_ACTUAL_MAS": ((0.5, 1, 1.5), (0.3, 0.5, 1)),
    "F2_V3_COMPACTA": ((1.5, 2, 3), (0.5, 1, 1.5)),
    "F3_TLV": ((2, 3, 4), (1, 1.5, 2.5)),
    "F4_PROTOBUF_RDSS": ((2, 3, 5), (1.5, 2.5, 4)),   # nanopb + protobuf en Python, Go y Rust
    "F5_CABECERA_TLV": ((2, 2.5, 3.5), (0.7, 1.2, 2)),
}

JUICIO = {
    #                    Evolucion   InfoOperativa  RiesgoCompat  Mantenimiento  AireUtil
    "F0_ACTUAL":        ((15, 5),   (20, 8),       (10, 5),      (50, 10),      (30, 8)),
    "F1_ACTUAL_MAS":    ((20, 8),   (30, 8),       (15, 6),      (45, 10),      (35, 8)),
    "F2_V3_COMPACTA":   ((35, 10),  (80, 8),       (35, 10),     (50, 10),      (85, 8)),
    "F3_TLV":           ((85, 8),   (80, 8),       (30, 8),      (60, 10),      (70, 10)),
    "F4_PROTOBUF_RDSS": ((90, 6),   (80, 8),       (50, 10),     (70, 12),      (75, 10)),
    "F5_CABECERA_TLV":  ((85, 8),   (85, 8),       (25, 8),      (65, 10),      (80, 8)),
}
CRIT = ["Evolucion", "InfoOperativa", "RiesgoCompat", "Mantenimiento", "AireUtil"]

factors = [
    Factor(name="PATiempo", weight=0.05, maximize=True),
    Factor(name="Evolucion", weight=0.25, maximize=True),
    Factor(name="InfoOperativa", weight=0.15, maximize=True),
    Factor(name="RiesgoCompat", weight=0.20, maximize=False),
    Factor(name="Mantenimiento", weight=0.20, maximize=True),
    Factor(name="AireUtil", weight=0.15, maximize=True),
]

DESC = {
    "F0_ACTUAL": "Payload actual de 33 B tal cual.",
    "F1_ACTUAL_MAS": "Payload actual + comando de identidad aparte.",
    "F2_V3_COMPACTA": "Telemetría v3 compacta y versionada, opcode aditivo.",
    "F3_TLV": "Telemetría con campos etiqueta-largo-valor, opcode aditivo.",
    "F4_PROTOBUF_RDSS": "Payload protobuf (nanopb) dentro de RDSS.",
    "F5_CABECERA_TLV": "Cabecera fija (versión, secuencia, eco de comando, banderas, id corto) + cuerpo TLV.",
}


def medir(op):
    fw_t, sw_t = EXTRA[op]
    fw = None if fw_t is None else (lambda: nexa.tri(*fw_t))
    sw = None if sw_t is None else (lambda: nexa.tri(*sw_t))
    sat, fat = nexa.simular("A_CONTACTOS_FWCORE", con_fat=True, extra_fw=fw, extra_sw=sw)
    return {
        "p_a_tiempo": round(float(np.mean(sat <= nexa.PLAZO)), 3),
        "fat_p80": nexa.fecha_de(float(np.percentile(fat, 80))).isoformat(),
    }


async def main():
    m = {op: medir(op) for op in EXTRA}
    for op, r in m.items():
        print(f"{op:<18} P(a tiempo)={r['p_a_tiempo']:.1%}  FAT p80 (sobre el plan)={r['fat_p80']}")

    fw = UnifiedDecisionFramework()
    for f in factors:
        fw.add_factor(f)
    for op, r in m.items():
        v = {c: UncertainVariable(c, DistributionType.NORMAL, list(JUICIO[op][i])) for i, c in enumerate(CRIT)}
        v["PATiempo"] = UncertainVariable("PATiempo", DistributionType.NORMAL, [r["p_a_tiempo"] * 100, 1.5])
        fw.add_option(DecisionOption(name=op, description=DESC[op], variables=v))

    results = await fw.run_analysis(mode="standard")
    print("\n" + "=" * 60)
    print(f"DECISION: {analysis_name}")
    print("=" * 60)
    print(results.get("explanation", "N/A"))

    out = Path("results") / f"{analysis_name}.json"
    out.parent.mkdir(exist_ok=True)
    with open(out, "w") as f:
        json.dump({"name": analysis_name, "date": analysis_date, "medicion": m, "extra": EXTRA,
                   "juicio": JUICIO, "factors": [(x.name, x.weight) for x in factors], "options": DESC,
                   "raw": {k: v for k, v in results.items() if k != "explanation"}}, f, indent=2, default=str)
    print(f"\nResultados guardados en {out}")


if __name__ == "__main__":
    asyncio.run(main())
