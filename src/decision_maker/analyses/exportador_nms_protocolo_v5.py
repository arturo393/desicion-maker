"""
Analysis v5: Protocolo del EXPORTADOR hacia el NMS — ¿Modbus?
Purpose: Evaluar "¿es mejor hacerlo Modbus para soportar lo más común de la industria?"
  Alcance: lado SERVIDOR (exportador). El lado EQUIPO (sniffer como maestro Modbus RTU
  por su RS485) queda fuera: es feature de firmware sobre flota desplegada, con 3
  críticos abiertos y refactor pendiente — decisión separada.

Opciones:
  MODBUS_TCP   - mapa de registros que el SCADA del cliente pollea
  SNMP         - MIB + traps (precedente Becker: su server sondea por SNMP)
  MQTT         - topics + payload JSON con edad
  REST         - OpenAPI (ya existe contracts/openapi.yaml)
  MODELO_PRIMERO - diferir el exportador hasta saber qué habla el NMS del cliente
                   (pregunta #1 de PLAN_MODELO_CANONICO.md §8)

Criterios:
  AdopcionSCADA     .25 - qué tan presente está en SCADA/NMS minero-industrial
  RiquezaSemantica  .20 - puede llevar identidad, unidades, VALOR CON EDAD, alertas
  BajoEsfuerzo      .15 - costo de implementar y mantener el exportador
  PushAlertas       .15 - eventos sin que el cliente pollee
  Evidencia         .15 - precedente documentado en repos o estudio de mercado
  MantenimientoBajo .10 - cuánta superficie propia nueva queda que derivar
"""

import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from decision_maker.core.models import DecisionOption, DistributionType, Factor, UncertainVariable
from decision_maker.core.orchestrator import UnifiedDecisionFramework

analysis_name = "exportador_nms_protocolo_v5"
analysis_date = datetime.now().isoformat()

factors = [
    Factor(name="AdopcionSCADA", weight=0.25, maximize=True),
    Factor(name="RiquezaSemantica", weight=0.20, maximize=True),
    Factor(name="BajoEsfuerzo", weight=0.15, maximize=True),
    Factor(name="PushAlertas", weight=0.15, maximize=True),
    Factor(name="Evidencia", weight=0.15, maximize=True),
    Factor(name="MantenimientoBajo", weight=0.10, maximize=True),
]

S = {
    "MODBUS_TCP": {
        # Ubicuo en SCADA/PLC minero; PERO: solo poll, sin unidades ni edad ni identidad,
        # word-order de floats infame, mapa de registros estático que deriva del modelo
        "AdopcionSCADA": (95, 4),
        "RiquezaSemantica": (25, 8),
        "BajoEsfuerzo": (58, 10),
        "PushAlertas": (12, 6),
        "Evidencia": (55, 10),
        "MantenimientoBajo": (45, 10),
    },
    "SNMP": {
        # Piso de integración DAS/NMS según estudio §9.1; Becker ya sondea SNMP (manual en repo)
        "AdopcionSCADA": (70, 8),
        "RiquezaSemantica": (52, 8),
        "BajoEsfuerzo": (42, 10),
        "PushAlertas": (65, 8),      # traps
        "Evidencia": (85, 6),
        "MantenimientoBajo": (48, 10),  # versionar MIB duele
    },
    "MQTT": {
        # Nativo en plataformas IIoT modernas; payload JSON con edad trivial; LWT para presencia
        "AdopcionSCADA": (55, 10),
        "RiquezaSemantica": (90, 5),
        "BajoEsfuerzo": (75, 8),
        "PushAlertas": (95, 4),
        "Evidencia": (50, 10),
        "MantenimientoBajo": (80, 8),
    },
    "REST": {
        # contracts/openapi.yaml YA existe; moderno; SCADA clásico de planta no lo habla
        "AdopcionSCADA": (60, 10),
        "RiquezaSemantica": (88, 5),
        "BajoEsfuerzo": (90, 5),
        "PushAlertas": (40, 10),
        "Evidencia": (62, 8),
        "MantenimientoBajo": (80, 8),
    },
    "MODELO_PRIMERO": {
        # La fundación manda: la interfaz se aprende en el segundo consumidor, no en el cero.
        # El modelo carga la semántica; el exportador se agrega cuando el cliente responda.
        "AdopcionSCADA": (50, 10),
        "RiquezaSemantica": (85, 6),
        "BajoEsfuerzo": (82, 8),
        "PushAlertas": (50, 10),
        "Evidencia": (78, 8),
        "MantenimientoBajo": (85, 6),
    },
}

desc = {
    "MODBUS_TCP": "Exportador Modbus TCP (mapa de registros polleable por cualquier SCADA).",
    "SNMP": "Agente SNMP con MIB propia + traps (precedente Becker en el repo).",
    "MQTT": "Publicación MQTT con payload JSON del contrato (topics por familia/equipo).",
    "REST": "Exponer la API OpenAPI existente directamente al NMS.",
    "MODELO_PRIMERO": "Modelo canónico primero; exportador recién con la respuesta del cliente.",
}

options = []
for key, fac in S.items():
    options.append(
        DecisionOption(
            name=key,
            description=desc[key],
            variables={f: UncertainVariable(f, DistributionType.NORMAL, fac[f]) for f in fac},
        )
    )


async def main():
    fw = UnifiedDecisionFramework()
    for f in factors:
        fw.add_factor(f)
    for o in options:
        fw.add_option(o)

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
                "contexto": {
                    "alcance": "Solo lado servidor/exportador. Lado equipo (Modbus RTU maestro "
                               "en RS485 del sniffer) es decisión de firmware separada.",
                    "sniffertag": "Confirmado por Arturo: otra familia de equipo, otro rol.",
                },
                "factors": [(fac.name, fac.weight) for fac in factors],
                "options": desc,
                "raw": {k: v for k, v in results.items() if k != "explanation"},
            },
            f,
            indent=2,
            default=str,
        )
    print(f"\nResultados guardados en {out}")


if __name__ == "__main__":
    asyncio.run(main())
