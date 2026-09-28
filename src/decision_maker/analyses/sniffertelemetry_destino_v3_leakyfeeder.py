"""
Analysis v3: Destino de sw-snifferTelemetry — con restricción de red leaky feeder
Purpose: v2 + hecho nuevo aportado por Arturo (2026-08-24):
  En una red leaky feeder SIEMPRE hay amplificadores (obligatorios por diseño del
  cable radiante). Dos familias:
    - Amp CON diagnóstico remoto -> sw-diagnosticoremoto
    - Amp SIN diagnóstico remoto -> se suscribirían al soft de telemetría,
      que puede terminar siendo el mismo NMS del cliente.
  La telemetría entonces no es solo del sniffer: es del ENLACE completo.

Cambios v2 -> v3:
  - Nuevo factor CoberturaAmplificadores (0.20): qué tan bien cada opción sirve
    a las dos familias de amplificadores de una instalación leaky feeder real.
  - Sale FosoNegocio (se solapaba con ClienteNMS; los contratos ya son el mecanismo).
  - Descripción de F actualizada: incluye el PASO 2 del plan canónico (el panel
    existente apuntado al modelo canónico sigue vivo como consumidor #1), porque
    sitios chicos sin NMS igual necesitan mirar algo.

Pesos: MantenimientoBajo 0.25 · ClienteNMS 0.20 · CoberturaAmplificadores 0.20 ·
       ReutilizacionDominio 0.15 · BajoEsfuerzo 0.10 · CalidadProducto 0.10
"""

import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from decision_maker.core.models import DecisionOption, DistributionType, Factor, UncertainVariable
from decision_maker.core.orchestrator import UnifiedDecisionFramework

analysis_name = "sniffertelemetry_destino_v3_leakyfeeder"
analysis_date = datetime.now().isoformat()

factors = [
    Factor(name="MantenimientoBajo", weight=0.25, maximize=True),
    Factor(name="ClienteNMS", weight=0.20, maximize=True),
    Factor(name="CoberturaAmplificadores", weight=0.20, maximize=True),
    Factor(name="ReutilizacionDominio", weight=0.15, maximize=True),
    Factor(name="BajoEsfuerzo", weight=0.10, maximize=True),
    Factor(name="CalidadProducto", weight=0.10, maximize=True),
]

S = {
    "A_diagnosticoremoto": {
        "MantenimientoBajo": (60, 10),
        "ClienteNMS": (88, 8),
        "CoberturaAmplificadores": (82, 8),   # es EL producto de amps con diag; los básicos no corren ese fw
        "ReutilizacionDominio": (30, 10),
        "BajoEsfuerzo": (45, 12),
        "CalidadProducto": (55, 12),
    },
    "B_smarttag": {
        "MantenimientoBajo": (70, 8),
        "ClienteNMS": (40, 10),
        "CoberturaAmplificadores": (25, 10),  # amps no pertenecen a un portal de personas/zonas
        "ReutilizacionDominio": (95, 5),
        "BajoEsfuerzo": (60, 10),
        "CalidadProducto": (85, 7),
    },
    "C_nuevo": {
        "MantenimientoBajo": (10, 6),
        "ClienteNMS": (40, 12),
        "CoberturaAmplificadores": (45, 12),
        "ReutilizacionDominio": (20, 8),
        "BajoEsfuerzo": (20, 8),
        "CalidadProducto": (50, 18),
    },
    "D_vistas_sniffer": {
        # El soft actual YA mostró campos de amp (AlertsSniffer.js) y su modelo declarativo
        # de campos serviría para amps básicos; pero mantiene 7 contenedores vivos
        "MantenimientoBajo": (15, 8),
        "ClienteNMS": (35, 10),
        "CoberturaAmplificadores": (72, 10),
        "ReutilizacionDominio": (40, 10),
        "BajoEsfuerzo": (90, 6),
        "CalidadProducto": (35, 10),
    },
    "E_smartlocalte": {
        "MantenimientoBajo": (62, 10),
        "ClienteNMS": (45, 12),
        "CoberturaAmplificadores": (30, 10),  # zonificación no habla de AGC ni potencia
        "ReutilizacionDominio": (55, 12),
        "BajoEsfuerzo": (55, 12),
        "CalidadProducto": (55, 12),
    },
    "F_exportador_nms": {
        # Modelo canónico con decodificador POR FAMILIA (sniffer, amp c/diag, amp básico)
        # -> exportador al NMS. El panel actual apuntado al modelo queda como consumidor #1
        # (paso 2 del plan): sitios sin NMS siguen teniendo vistas, con inversión cero nueva.
        "MantenimientoBajo": (88, 6),
        "ClienteNMS": (95, 5),
        "CoberturaAmplificadores": (92, 5),   # las dos familias bajo el mismo contrato
        "ReutilizacionDominio": (50, 12),
        "BajoEsfuerzo": (42, 12),
        "CalidadProducto": (62, 12),
    },
}

desc = {
    "A_diagnosticoremoto": "Panel dentro de sw-diagnosticoremoto.",
    "B_smarttag": "Consolidar telemetría dentro de SmartTag.",
    "C_nuevo": "Producto nuevo standalone.",
    "D_vistas_sniffer": "Mantener sw-sniffertelemetry y crear vistas (también para amps básicos).",
    "E_smartlocalte": "Vistas dentro de SmartLocalTe (zonificación).",
    "F_exportador_nms": "Modelo canónico multi-familia + exportador al NMS; panel actual queda "
                        "apuntado al modelo como consumidor interno (sitios sin NMS).",
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
                    "leaky_feeder": "Los amplificadores son obligatorios en toda red leaky feeder; "
                                    "dos familias: con diag remoto (diagnosticoremoto) y sin él "
                                    "(telemetría), pudiendo ambas terminar en el mismo NMS",
                    "destinatario": "Cliente en SU NMS (confirmado)",
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
