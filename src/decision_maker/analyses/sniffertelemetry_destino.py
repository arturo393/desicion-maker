"""
Template-derived Analysis: Destino de sw-sniffertelemetry
Purpose: Decidir donde vivira el software de telemetria del sniffer (17 funcionalidades
         de frontend + 7 contenedores), segun ANALISIS_SOFTWARE_TELEMETRIA.md (2026-08-20).

Opciones evaluadas (pedidas por el usuario):
  A. Integrar en sw-diagnosticoremoto (capa de protocolo/gateway/contratos)
  B. Integrar en SmartTag (ya tiene el dominio del sniffer, v3.1.0, 104 tests)
  C. Crear un producto nuevo y separado
  D. Mantener sniffertelemetry y solo crear vistas (keep-as-is + views)

Criterios derivados del propio analisis:
  - Consolidacion: menos frontends separados (el doc dice 3 frontends es malo)
  - ReutilizacionDominio: el dominio del sniffer ya existe en SmartTag
  - BajoEsfuerzo: menor trabajo de implementacion (maximize=True => score= poco esfuerzo)
  - Seguridad: baseline de auth/rate-limit (doc 4.5/5.1: ambos hoy expuestos)
  - FosoNegocio: acercarse al foso real = capa de dispositivo + contratos (panel es commodity)
  - CalidadProducto: arquitectura, tests, websocket, UX final

Escala 0-100, mayor = mejor (todos benefit). Incertidumbre como NORMAL(std).
"""

import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from decision_maker.core.models import DecisionOption, DistributionType, Factor, UncertainVariable
from decision_maker.core.orchestrator import UnifiedDecisionFramework

analysis_name = "sniffertelemetry_destino"
analysis_date = datetime.now().isoformat()

factors = [
    Factor(name="Consolidacion", weight=0.20, maximize=True),
    Factor(name="ReutilizacionDominio", weight=0.20, maximize=True),
    Factor(name="BajoEsfuerzo", weight=0.15, maximize=True),
    Factor(name="Seguridad", weight=0.15, maximize=True),
    Factor(name="FosoNegocio", weight=0.15, maximize=True),
    Factor(name="CalidadProducto", weight=0.15, maximize=True),
]

# (mean, std) por (opcion, factor)
S = {
    "A_diagnosticoremoto": {
        "Consolidacion": (70, 10),
        "ReutilizacionDominio": (30, 10),
        "BajoEsfuerzo": (45, 12),
        "Seguridad": (50, 10),
        "FosoNegocio": (85, 8),
        "CalidadProducto": (55, 12),
    },
    "B_smarttag": {
        "Consolidacion": (90, 6),
        "ReutilizacionDominio": (95, 5),
        "BajoEsfuerzo": (60, 10),
        "Seguridad": (55, 10),
        "FosoNegocio": (80, 8),
        "CalidadProducto": (85, 7),
    },
    "C_nuevo": {
        "Consolidacion": (15, 8),
        "ReutilizacionDominio": (20, 8),
        "BajoEsfuerzo": (20, 8),
        "Seguridad": (40, 12),
        "FosoNegocio": (30, 10),
        "CalidadProducto": (50, 18),
    },
    "D_vistas_sniffer": {
        "Consolidacion": (20, 8),
        "ReutilizacionDominio": (40, 10),
        "BajoEsfuerzo": (90, 6),
        "Seguridad": (25, 8),
        "FosoNegocio": (20, 8),
        "CalidadProducto": (35, 10),
    },
}

desc = {
    "A_diagnosticoremoto": "Integrar telemetria en sw-diagnosticoremoto (capa protocolo/contratos/gateway).",
    "B_smarttag": "Consolidar como tipo de dispositivo dentro de SmartTag (dominio sniffer ya existe).",
    "C_nuevo": "Nuevo repositorio/producto standalone para el sniffer.",
    "D_vistas_sniffer": "Mantener sw-sniffertelemetry y solo anadir vistas (keep-as-is).",
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
    # Top-level ranking summary
    expl = results.get("explanation", "N/A")
    print(f"Explicacion (TOPSIS/Borda):\n{expl}\n")

    # Save full results
    out = Path("results") / f"{analysis_name}.json"
    out.parent.mkdir(exist_ok=True)
    with open(out, "w") as f:
        json.dump(
            {
                "name": analysis_name,
                "date": analysis_date,
                "factors": [(fac.name, fac.weight) for fac in factors],
                "options": desc,
                "raw": {k: v for k, v in results.items() if k != "explanation"},
            },
            f,
            indent=2,
            default=str,
        )
    print(f"Resultados guardados en {out}")


if __name__ == "__main__":
    asyncio.run(main())
