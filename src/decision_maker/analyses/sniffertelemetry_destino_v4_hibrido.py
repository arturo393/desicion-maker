"""
Analysis v4: Híbrido elegido por Arturo — diagnosticoremoto + vistas demo + exportador NMS
Purpose: Validar la decisión declarada (2026-08-24):
    "Agregar a diagnóstico remoto, con vistas muy sencillas que demuestren las
     funcionalidades del sniffer y además el NMS"
  = opción nueva H que combina A (hogar de los contratos) + F (exportador NMS)
    pero con vistas MÍNIMAS de demostración, no un quinto producto completo.

Cambios v3 -> v4:
  - Nueva opción H_dr_vistas_nms
  - H mantiene el resto igual para comparación directa
"""

import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from decision_maker.core.models import DecisionOption, DistributionType, Factor, UncertainVariable
from decision_maker.core.orchestrator import UnifiedDecisionFramework

analysis_name = "sniffertelemetry_destino_v4_hibrido"
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
        "CoberturaAmplificadores": (82, 8),
        "ReutilizacionDominio": (30, 10),
        "BajoEsfuerzo": (45, 12),
        "CalidadProducto": (55, 12),
    },
    "B_smarttag": {
        "MantenimientoBajo": (70, 8),
        "ClienteNMS": (40, 10),
        "CoberturaAmplificadores": (25, 10),
        "ReutilizacionDominio": (95, 5),
        "BajoEsfuerzo": (60, 10),
        "CalidadProducto": (85, 7),
    },
    "D_vistas_sniffer": {
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
        "CoberturaAmplificadores": (30, 10),
        "ReutilizacionDominio": (55, 12),
        "BajoEsfuerzo": (55, 12),
        "CalidadProducto": (55, 12),
    },
    "F_exportador_nms": {
        "MantenimientoBajo": (88, 6),
        "ClienteNMS": (95, 5),
        "CoberturaAmplificadores": (92, 5),
        "ReutilizacionDominio": (50, 12),
        "BajoEsfuerzo": (42, 12),
        "CalidadProducto": (62, 12),
    },
    "H_dr_vistas_nms": {
        # diagnosticoremoto absorbe: contrato + decoder sniffer + vistas demo mínimas
        # + exportador NMS. Un solo producto activo; el .205 se congela y migra después.
        "MantenimientoBajo": (87, 6),   # consolida en producto ya operado; vistas mínimas
        "ClienteNMS": (93, 5),          # exportador incluido
        "CoberturaAmplificadores": (90, 5),  # ambas familias bajo el mismo techo, literalmente
        "ReutilizacionDominio": (48, 12),    # patrones existen (becker_varis/, decoders/, 521 tests)
        "BajoEsfuerzo": (52, 12),       # contrato + decoder + 3 vistas + exportador
        "CalidadProducto": (72, 10),    # vista demo sobre pipeline maduro
    },
}

desc = {
    "A_diagnosticoremoto": "Panel dentro de sw-diagnosticoremoto (sin exportador explícito).",
    "B_smarttag": "Consolidar dentro de SmartTag.",
    "D_vistas_sniffer": "Mantener sw-sniffertelemetry y crear vistas.",
    "E_smartlocalte": "Vistas dentro de SmartLocalTe.",
    "F_exportador_nms": "Modelo canónico multi-familia + exportador NMS, paneles congelados.",
    "H_dr_vistas_nms": "DECIDIDO: integrar en sw-diagnosticoremoto con vistas demo mínimas "
                       "de las funcionalidades del sniffer + exportador al NMS.",
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
                "decision_arturo": desc["H_dr_vistas_nms"],
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
