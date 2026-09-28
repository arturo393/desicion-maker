"""
Analysis v2: Destino de sw-snifferTelemetry — con respuestas de Arturo (2026-08-24)
Purpose: Re-decidir donde vive la telemetria del sniffer, ahora con:
  - SmartLocalTe como opcion nueva (zonificacion minera, sniffer-tags + tags activos,
    tiene su propio frontend)
  - Destinatario confirmado: CLIENTE EN SU NMS (no pide panel uqomm)
  - Horizonte estrategico, sin presion de fecha
  - Criterio #1 declarado por Arturo: MENOS QUE MANTENER

Cambios v1 -> v2:
  - Nuevo factor MantenimientoBajo (0.30): criterio #1 del usuario
  - Nuevo factor ClienteNMS (0.25): el dato comercial confirmado
  - Nueva opcion E_smartlocalte: absorber vistas en SmartLocalTe
  - Nueva opcion F_exportador_nms: congelar paneles + modelo canonico + exportador
    al NMS del cliente (la via de PLAN_MODELO_CANONICO.md)
  - Bajan Esfuerzo (0.10, sin presion) y CalidadProducto (0.10)
"""

import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from decision_maker.core.models import DecisionOption, DistributionType, Factor, UncertainVariable
from decision_maker.core.orchestrator import UnifiedDecisionFramework

analysis_name = "sniffertelemetry_destino_v2"
analysis_date = datetime.now().isoformat()

factors = [
    Factor(name="MantenimientoBajo", weight=0.30, maximize=True),   # criterio #1 de Arturo
    Factor(name="ClienteNMS", weight=0.25, maximize=True),          # cliente lo ve en SU sistema
    Factor(name="ReutilizacionDominio", weight=0.15, maximize=True),
    Factor(name="BajoEsfuerzo", weight=0.10, maximize=True),        # sin presion de fecha
    Factor(name="FosoNegocio", weight=0.10, maximize=True),
    Factor(name="CalidadProducto", weight=0.10, maximize=True),
]

# (media, std) escala 0-100, mayor = mejor
S = {
    "A_diagnosticoremoto": {
        # El producto es capa de protocolo/gateway; meterle un dashboard agranda su frente
        "MantenimientoBajo": (60, 10),
        "ClienteNMS": (88, 8),       # los contratos viven aqui: camino mas corto al NMS
        "ReutilizacionDominio": (30, 10),
        "BajoEsfuerzo": (45, 12),
        "FosoNegocio": (90, 6),
        "CalidadProducto": (55, 12),
    },
    "B_smarttag": {
        # Dominio sniffer ya existe (services, history, websocket, 104 tests)
        "MantenimientoBajo": (70, 8),   # un frontend menos, pero suma superficie a un producto grande
        "ClienteNMS": (40, 10),         # sigue siendo panel propio
        "ReutilizacionDominio": (95, 5),
        "BajoEsfuerzo": (60, 10),
        "FosoNegocio": (78, 8),
        "CalidadProducto": (85, 7),
    },
    "C_nuevo": {
        "MantenimientoBajo": (10, 6),
        "ClienteNMS": (40, 12),
        "ReutilizacionDominio": (20, 8),
        "BajoEsfuerzo": (20, 8),
        "FosoNegocio": (30, 10),
        "CalidadProducto": (50, 18),
    },
    "D_vistas_sniffer": {
        # Mantener los 7 contenedores del .205 vivos
        "MantenimientoBajo": (15, 8),
        "ClienteNMS": (35, 10),
        "ReutilizacionDominio": (40, 10),
        "BajoEsfuerzo": (90, 6),
        "FosoNegocio": (20, 8),
        "CalidadProducto": (35, 10),
    },
    "E_smartlocalte": {
        # Zonificacion minera con snifter-tags: comparte HARDWARE, no dominio de software
        # (deteccion/zonas vs io_reads de telemetria). Las vistas son lo barato;
        # la cadena monitor/writer/mapper/rabbit/mongo es lo caro, y habria que tenerla ahi.
        "MantenimientoBajo": (62, 10),
        "ClienteNMS": (45, 12),
        "ReutilizacionDominio": (55, 12),   # mismo ecosistema de tags, otro problema de negocio
        "BajoEsfuerzo": (55, 12),
        "FosoNegocio": (58, 10),
        "CalidadProducto": (55, 12),
    },
    "F_exportador_nms": {
        # Congelar paneles + modelo canonico sobre contracts/ + exportador SNMP/REST/MQTT
        # al NMS del cliente (via PLAN_MODELO_CANONICO.md). Los paneles congelados cuestan cero.
        "MantenimientoBajo": (90, 6),
        "ClienteNMS": (95, 5),           # ES literalmente lo que el cliente dijo querer
        "ReutilizacionDominio": (50, 12),# mete al sniffer bajo contrato por primera vez
        "BajoEsfuerzo": (42, 12),        # modelado + decodificadores; sin prisa, sin requisito 90d
        "FosoNegocio": (95, 4),
        "CalidadProducto": (62, 12),     # el cliente ve el dato en SU NMS maduro
    },
}

desc = {
    "A_diagnosticoremoto": "Panel dentro de sw-diagnosticoremoto (donde viven los contratos).",
    "B_smarttag": "Consolidar telemetria como tipo de dispositivo dentro de SmartTag.",
    "C_nuevo": "Producto nuevo standalone.",
    "D_vistas_sniffer": "Mantener sw-sniffertelemetry y solo crear vistas.",
    "E_smartlocalte": "Vistas de telemetria dentro de SmartLocalTe (zonificacion minera).",
    "F_exportador_nms": "Sin panel nuevo: congelar + modelo canonico + exportador al NMS del cliente.",
}

options = []
for key, fac in S.items():
    options.append(
        DecisionOption(
            name=key,
            description=desc[key],
            variables={
                f: UncertainVariable(f, DistributionType.NORMAL, fac[f]) for f in fac
            },
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
                    "smartlocalte": "Zonificacion minera, sniffer-tags + tags activos, frontend propio",
                    "destinatario": "Cliente en SU NMS (confirmado)",
                    "horizonte": "Estrategico, sin fecha",
                    "criterio_1": "Menos que mantener",
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
