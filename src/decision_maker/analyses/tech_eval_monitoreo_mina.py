"""
Título: Evaluación de tecnologías - Monitoreo general en la nube para faenas mineras
Propósito: Rankear stacks candidatos para un sistema de monitoreo cloud en minas con
           conectividad intermitente, usando @decision-maker (MCDM bajo incertidumbre).
Creado: 2026-08-23
Versión: 1.0

CRITERIOS (Factores), escala 0-10 salvo donde se indica:
- OfflineResilience : capacidad store-and-forward / autonomía sin link (max)
- EdgeInstallEase  : facilidad de instalar en edge SIN internet (max)
- CostoEficiencia  : menor costo = mayor puntaje (max)
- Escalabilidad    : crecer a flota de sitios (max)
- Seguridad        : auth, TLS, RBAC (max)
- BajoConsumo      : menor CPU/RAM en edge = mayor puntaje (max)
- Madurez          : ecosistema/soporte (max)

OPCIONES (stacks candidatos):
A: MQTT edge (Mosquitto) + TimescaleDB + Grafana + decision-maker edge
B: HTTP batch + MongoDB + dashboard propio (reusa stack sw-diagnosticoremoto)
C: RabbitMQ + Mongo + Go backend (stack actual) federado por sitio
D: Kafka / Redpanda edge + cloud
E: LoRaWAN / IIoT gateway nativo + nube gestionada

NOTA: Gemini (extra ai) NO se usa: requiere internet y la mina es intermitente.
El núcleo de decision-maker corre 100% local en el edge.
"""

import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from decision_maker.core.models import DecisionOption, DistributionType, Factor, UncertainVariable
from decision_maker.core.orchestrator import UnifiedDecisionFramework

analysis_name = "tech_eval_monitoreo_mina"
analysis_date = datetime.now().isoformat()

factors = [
    Factor(name="OfflineResilience", weight=0.25, maximize=True),
    Factor(name="EdgeInstallEase", weight=0.15, maximize=True),
    Factor(name="CostoEficiencia", weight=0.15, maximize=True),
    Factor(name="Escalabilidad", weight=0.15, maximize=True),
    Factor(name="Seguridad", weight=0.15, maximize=True),
    Factor(name="BajoConsumo", weight=0.05, maximize=True),
    Factor(name="Madurez", weight=0.10, maximize=True),
]

options = [
    DecisionOption(
        name="A: MQTT edge + TimescaleDB + Grafana",
        description="Mosquitto en cada sitio (binario unico, persistent sessions, store-and-forward) -> bridge TLS a la nube; TS DB + Grafana. decision-maker edge local.",
        variables={
            "OfflineResilience": UncertainVariable("OfflineResilience", DistributionType.NORMAL, [9.0, 0.5]),
            "EdgeInstallEase": UncertainVariable("EdgeInstallEase", DistributionType.NORMAL, [8.0, 0.6]),
            "CostoEficiencia": UncertainVariable("CostoEficiencia", DistributionType.NORMAL, [8.0, 0.6]),
            "Escalabilidad": UncertainVariable("Escalabilidad", DistributionType.NORMAL, [8.0, 0.6]),
            "Seguridad": UncertainVariable("Seguridad", DistributionType.NORMAL, [7.0, 0.6]),
            "BajoConsumo": UncertainVariable("BajoConsumo", DistributionType.NORMAL, [8.0, 0.5]),
            "Madurez": UncertainVariable("Madurez", DistributionType.NORMAL, [9.0, 0.4]),
        },
    ),
    DecisionOption(
        name="B: HTTP batch + MongoDB + dashboard propio",
        description="Buffer local SQLite/cola -> upload HTTPS batch cuando hay link; MongoDB + dashboard Next/Go (reusa sw-diagnosticoremoto). decision-maker cloud.",
        variables={
            "OfflineResilience": UncertainVariable("OfflineResilience", DistributionType.NORMAL, [6.0, 0.8]),
            "EdgeInstallEase": UncertainVariable("EdgeInstallEase", DistributionType.NORMAL, [7.0, 0.7]),
            "CostoEficiencia": UncertainVariable("CostoEficiencia", DistributionType.NORMAL, [7.0, 0.6]),
            "Escalabilidad": UncertainVariable("Escalabilidad", DistributionType.NORMAL, [7.0, 0.6]),
            "Seguridad": UncertainVariable("Seguridad", DistributionType.NORMAL, [7.0, 0.6]),
            "BajoConsumo": UncertainVariable("BajoConsumo", DistributionType.NORMAL, [6.0, 0.7]),
            "Madurez": UncertainVariable("Madurez", DistributionType.NORMAL, [8.0, 0.5]),
        },
    ),
    DecisionOption(
        name="C: RabbitMQ + Mongo + Go (stack actual) federado",
        description="El stack sw-diagnosticoremoto por sitio + federation/shovel a la nube. Maduro pero pesado en edge.",
        variables={
            "OfflineResilience": UncertainVariable("OfflineResilience", DistributionType.NORMAL, [7.0, 0.7]),
            "EdgeInstallEase": UncertainVariable("EdgeInstallEase", DistributionType.NORMAL, [5.0, 0.8]),
            "CostoEficiencia": UncertainVariable("CostoEficiencia", DistributionType.NORMAL, [6.0, 0.6]),
            "Escalabilidad": UncertainVariable("Escalabilidad", DistributionType.NORMAL, [8.0, 0.5]),
            "Seguridad": UncertainVariable("Seguridad", DistributionType.NORMAL, [8.0, 0.5]),
            "BajoConsumo": UncertainVariable("BajoConsumo", DistributionType.NORMAL, [5.0, 0.7]),
            "Madurez": UncertainVariable("Madurez", DistributionType.NORMAL, [8.0, 0.5]),
        },
    ),
    DecisionOption(
        name="D: Kafka / Redpanda edge + cloud",
        description="Log duradero con replay; excelente escalabilidad pero JVM/Redpanda pesado y dificil offline en edge.",
        variables={
            "OfflineResilience": UncertainVariable("OfflineResilience", DistributionType.NORMAL, [8.0, 0.6]),
            "EdgeInstallEase": UncertainVariable("EdgeInstallEase", DistributionType.NORMAL, [4.0, 0.8]),
            "CostoEficiencia": UncertainVariable("CostoEficiencia", DistributionType.NORMAL, [5.0, 0.7]),
            "Escalabilidad": UncertainVariable("Escalabilidad", DistributionType.NORMAL, [10.0, 0.3]),
            "Seguridad": UncertainVariable("Seguridad", DistributionType.NORMAL, [8.0, 0.5]),
            "BajoConsumo": UncertainVariable("BajoConsumo", DistributionType.NORMAL, [4.0, 0.8]),
            "Madurez": UncertainVariable("Madurez", DistributionType.NORMAL, [9.0, 0.4]),
        },
    ),
    DecisionOption(
        name="E: LoRaWAN / IIoT gateway nativo + nube gestionada",
        description="Gateway IIoT/LPWAN; muy liviano pero ancho de banda tiny: bueno para sensores, no para monitoreo general de equipos.",
        variables={
            "OfflineResilience": UncertainVariable("OfflineResilience", DistributionType.NORMAL, [7.0, 0.7]),
            "EdgeInstallEase": UncertainVariable("EdgeInstallEase", DistributionType.NORMAL, [6.0, 0.7]),
            "CostoEficiencia": UncertainVariable("CostoEficiencia", DistributionType.NORMAL, [6.0, 0.7]),
            "Escalabilidad": UncertainVariable("Escalabilidad", DistributionType.NORMAL, [6.0, 0.8]),
            "Seguridad": UncertainVariable("Seguridad", DistributionType.NORMAL, [6.0, 0.8]),
            "BajoConsumo": UncertainVariable("BajoConsumo", DistributionType.NORMAL, [10.0, 0.3]),
            "Madurez": UncertainVariable("Madurez", DistributionType.NORMAL, [7.0, 0.6]),
        },
    ),
    DecisionOption(
        name="F: Prometheus (remote_write) + Grafana + Alertmanager",
        description="Edge ya define buffer (Mosquitto+SQLite) y un bridge que hace Prometheus remote_write (WAL+retry) a Prometheus central; Alertmanager para alertas; Grafana para dashboards. Prometheus es pull nativo, pero el edge EMPUJA via remote_write -> apto para link intermitente.",
        variables={
            "OfflineResilience": UncertainVariable("OfflineResilience", DistributionType.NORMAL, [8.5, 0.5]),
            "EdgeInstallEase": UncertainVariable("EdgeInstallEase", DistributionType.NORMAL, [8.0, 0.6]),
            "CostoEficiencia": UncertainVariable("CostoEficiencia", DistributionType.NORMAL, [8.0, 0.6]),
            "Escalabilidad": UncertainVariable("Escalabilidad", DistributionType.NORMAL, [7.0, 0.7]),
            "Seguridad": UncertainVariable("Seguridad", DistributionType.NORMAL, [7.0, 0.6]),
            "BajoConsumo": UncertainVariable("BajoConsumo", DistributionType.NORMAL, [8.0, 0.6]),
            "Madurez": UncertainVariable("Madurez", DistributionType.NORMAL, [10.0, 0.3]),
        },
    ),
]


async def main():
    fw = UnifiedDecisionFramework()
    for f in factors:
        fw.add_factor(f)
    for o in options:
        fw.add_option(o)

    results = await fw.run_analysis(mode="standard")

    print(f"\n=== Analysis '{analysis_name}' ({analysis_date}) ===")
    print("RESULT KEYS:", list(results.keys()))
    ranking = (
        results.get("ranking")
        or results.get("ranked_options")
        or results.get("options")
        or results.get("scores")
    )
    if ranking:
        print("\n--- Ranking (raw) ---")
        for i, item in enumerate(ranking, 1):
            print(f"  {i}.", item)
    print("\n--- TOPSIS scores ---")
    ts = results.get("topsis_scores")
    if hasattr(ts, "to_dict"):
        ts = ts.to_dict()
    if isinstance(ts, dict):
        for k, v in ts.items():
            print(f"  {k}: {v}")
    else:
        print("  ", ts)
    print("\n--- Strategies (weighted) ---")
    st = results.get("strategies")
    if hasattr(st, "to_dict"):
        st = st.to_dict()
    if isinstance(st, dict):
        for k, v in st.items():
            print(f"  {k}: {v}")
    else:
        print("  ", st)
    print("\nWinner explanation:", results.get("explanation", "N/A"))

    # Dump full structured result for inspection
    try:
        ranked = results.get("ranking") or results.get("ranked_options") or results.get("options")
        if ranked:
            print("\n--- Ranking ---")
            for i, item in enumerate(ranked, 1):
                name = item.get("name") if isinstance(item, dict) else getattr(item, "name", item)
                score = item.get("score") if isinstance(item, dict) else getattr(item, "score", None)
                print(f"  {i}. {name}  score={score}")
    except Exception as e:
        print("ranking parse skip:", e)

    out = f"results/{analysis_name}.json"
    Path("results").mkdir(exist_ok=True)
    with open(out, "w") as f:
        json.dump({"name": analysis_name, "date": analysis_date, "results": str(results)}, f, indent=2, default=str)
    print(f"\nResults (stringified) saved to {out}")


if __name__ == "__main__":
    asyncio.run(main())
