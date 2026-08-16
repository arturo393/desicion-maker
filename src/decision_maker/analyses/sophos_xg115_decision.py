"""
Sophos XG115 - Decision: actualizar firmware vs licencia vs otro hardware vs externalizar
Purpose: Decidir el camino para el gateway UQOMM (192.168.60.1), Sophos XG115 sin licencia
Created: 2026-08-10
Version: 1.0

CONTEXTO:
- Equipo: Sophos XG115 (SFOS 18.0.6 MR-6-Build655), S/N C190A2MYWRJ2Q4C
- Es el gateway/firewall de la red UQOMM 192.168.60.0/24 (ver docs/issues/uqomm-seguridad-red)
- SIN licencia: no hay IPS/AV/actualizaciones de firmas, no hay web filtering, no hay sandboxing
- Firmware nuevo disponible: SFOS 19.5.3 MR3-Build652 (maintenance release)
- Modelo XG115 es serie antigua (la familia XG 100 está en ciclo EOL de Sophos)

OPCIONES:
A) Actualizar firmware a 19.5.3 MR3 (sin licencia)
B) Comprar licencia Sophos (subscription: Network Protection / Total Protect)
C) Reemplazar por otro hardware (OPNsense/pfSense en minipc, o modelo Sophos actual XGS)
D) Externalizar el servicio (MSSP / firewall gestionado en nube)
"""

import asyncio
import json
from datetime import datetime
from pathlib import Path

from decision_maker.core.models import DecisionOption, DistributionType, Factor
from decision_maker.core.orchestrator import UnifiedDecisionFramework


async def run_evaluation():
    framework = UnifiedDecisionFramework()
    framework.mc_engine.num_simulations = 50000

    # ============================================================
    # FACTORS (puntajes de utilidad 0-100)
    # ============================================================
    # 1. Cobertura_Seguridad: qué tanto protege (IPS/AV/web filter/sandbox). Maximizar.
    # 2. Costo_Inicial: capex de la decisión (licencia, hardware, mensualidad MSSP). Minimizar.
    # 3. Costo_Operativo_Anual: mantención/suscripción/aumento mensual. Minimizar.
    # 4. Riesgo_Operativo: downtime, migración, soporte, EOL. Minimizar.
    # 5. Tiempo_Implementacion: cuánto tarda en estar protegido. Minimizar.
    # 6. Autonomia_Gestion: control local vs tercero. Maximizar.
    framework.add_factor(Factor("Cobertura_Seguridad", 0.30, maximize=True))
    framework.add_factor(Factor("Bajo_Costo_Inicial", 0.15, maximize=True))
    framework.add_factor(Factor("Bajo_Costo_Operativo", 0.20, maximize=True))
    framework.add_factor(Factor("Bajo_Riesgo_Operativo", 0.15, maximize=True))
    framework.add_factor(Factor("Rapida_Implementacion", 0.10, maximize=True))
    framework.add_factor(Factor("Autonomia_Gestion", 0.10, maximize=True))

    # ============================================================
    # OPCION A: Actualizar firmware a 19.5.3 MR3 (sin licencia)
    # ============================================================
    opt_a = DecisionOption(
        "A: Actualizar firmware 19.5.3 MR3 (sin licencia)",
        "Actualizar el XG115 a SFOS 19.5.3 MR3-Build652 sin comprar licencia. "
        "Mejoras de estabilidad (18.0.6 MR6 es viejo), pero sigue SIN IPS/AV/web filtering activo.",
    )
    opt_a.add_variable("Cobertura_Seguridad", DistributionType.NORMAL, 25, 5)
    opt_a.add_variable("Bajo_Costo_Inicial", DistributionType.NORMAL, 95, 3)
    opt_a.add_variable("Bajo_Costo_Operativo", DistributionType.NORMAL, 90, 5)
    opt_a.add_variable("Bajo_Riesgo_Operativo", DistributionType.UNIFORM, 45, 70)  # riesgo de regresión 19.5 en modelo EOL
    opt_a.add_variable("Rapida_Implementacion", DistributionType.NORMAL, 80, 5)
    opt_a.add_variable("Autonomia_Gestion", DistributionType.NORMAL, 90, 3)

    # ============================================================
    # OPCION B: Comprar licencia Sophos (Network Protection o Total Protect)
    # ============================================================
    opt_b = DecisionOption(
        "B: Comprar licencia Sophos para XG115",
        "Suscripcion Sophos (Network Protection ~USD 300-400/año o Total Protect). "
        "Activa IPS, AV, web filtering y sandboxing en el hardware existente. "
        "Riesgo: XG115 en EOL, soporte limitado y hardware envejecido.",
    )
    opt_b.add_variable("Cobertura_Seguridad", DistributionType.NORMAL, 85, 5)
    opt_b.add_variable("Bajo_Costo_Inicial", DistributionType.NORMAL, 55, 8)
    opt_b.add_variable("Bajo_Costo_Operativo", DistributionType.NORMAL, 55, 8)
    opt_b.add_variable("Bajo_Riesgo_Operativo", DistributionType.UNIFORM, 55, 75)
    opt_b.add_variable("Rapida_Implementacion", DistributionType.NORMAL, 75, 5)
    opt_b.add_variable("Autonomia_Gestion", DistributionType.NORMAL, 85, 3)

    # ============================================================
    # OPCION C: Reemplazar por otro hardware (OPNsense en minipc / XGS actual)
    # ============================================================
    opt_c = DecisionOption(
        "C: Reemplazar por otro hardware",
        "Firewall moderno: OPNsense/pfSense en minipc (~USD 300-500) o Sophos XGS actual. "
        "IPS/AV open-source sin costo de licencia, hardware nuevo con soporte. "
        "Requiere migracion de reglas/VPN (downtime) y curva de aprendizaje.",
    )
    opt_c.add_variable("Cobertura_Seguridad", DistributionType.NORMAL, 80, 8)
    opt_c.add_variable("Bajo_Costo_Inicial", DistributionType.NORMAL, 65, 10)
    opt_c.add_variable("Bajo_Costo_Operativo", DistributionType.NORMAL, 85, 8)
    opt_c.add_variable("Bajo_Riesgo_Operativo", DistributionType.UNIFORM, 60, 85)
    opt_c.add_variable("Rapida_Implementacion", DistributionType.NORMAL, 45, 8)
    opt_c.add_variable("Autonomia_Gestion", DistributionType.NORMAL, 88, 5)

    # ============================================================
    # OPCION D: Externalizar servicio (MSSP / firewall gestionado)
    # ============================================================
    opt_d = DecisionOption(
        "D: Externalizar (MSSP / firewall gestionado)",
        "Contratar MSSP que gestione firewall/SASE (Fortinet, Sophos MTR, Zscaler, etc.). "
        "Seguridad 24/7 y personal experto, pero costo recurrente mensual, dependencia y "
        "perdida de control local.",
    )
    opt_d.add_variable("Cobertura_Seguridad", DistributionType.NORMAL, 90, 5)
    opt_d.add_variable("Bajo_Costo_Inicial", DistributionType.NORMAL, 75, 8)
    opt_d.add_variable("Bajo_Costo_Operativo", DistributionType.NORMAL, 40, 8)
    opt_d.add_variable("Bajo_Riesgo_Operativo", DistributionType.UNIFORM, 75, 92)
    opt_d.add_variable("Rapida_Implementacion", DistributionType.NORMAL, 60, 8)
    opt_d.add_variable("Autonomia_Gestion", DistributionType.NORMAL, 35, 8)

    framework.add_option(opt_a)
    framework.add_option(opt_b)
    framework.add_option(opt_c)
    framework.add_option(opt_d)

    # ============================================================
    # RUN
    # ============================================================
    results = await framework.run_analysis(mode="advanced", use_ai=False)

    # Guardar resultado
    out_dir = Path("results")
    out_dir.mkdir(exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_file = out_dir / f"sophos_xg115_decision_{stamp}.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump({"analysis": "sophos_xg115", "date": stamp, "results": results}, f, indent=2, default=str)
    print(f"\nResultados guardados en {out_file}")
    return results


if __name__ == "__main__":
    asyncio.run(run_evaluation())
