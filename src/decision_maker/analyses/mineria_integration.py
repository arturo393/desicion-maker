#!/usr/bin/env python3
"""
Titulo: Analisis de Decision - Integracion de datos RDSS a sistemas mineros
Proposito: Evaluar la forma mas simple y efectiva para que una operacion minera
           integre los datos de diagnostico remoto (VLAD, TG, Becker Varis,
           TinySA) a sus sistemas existentes (SCADA, PI System, dashboards, etc.)

Fecha: 2026-06-24
Version: 1.0

CONTEXTO:
- Nuestro sistema RDSS ya expone: API REST, WebSocket, RabbitMQ, MongoDB
- Tipico cliente minero tiene: SCADA (Schneider/Wonderware), PI System (AVEVA),
  Grafana, Excel/SAP, integraciones MQTT/OPC UA
- Perfil del usuario en mina: ingeniero de mantenimiento o supervisor de planta
- Necesitan: ver estado de amplificadores, recibir alertas, exportar reportes
- NO son desarrolladores — necesitan algo simple de conectar
"""

import json
import math
import os
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

env_file = Path(__file__).parent.parent / ".env.gemini"
if env_file.exists():
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ[key.strip()] = value.strip()

from decision_maker.core.gemini_helper import search_with_gemini

# ============================================================
# ALTERNATIVAS DE INTEGRACION
# ============================================================

ALTERNATIVES = [
    {
        "name": "API REST (HTTP GET)",
        "description": "El sistema minero hace llamadas HTTP a nuestros endpoints "
                       "(/api/tg/devices, /api/alerts, etc.) cada X segundos. "
                       "Devuelve JSON. Cualquier sistema que sepa hacer HTTP lo soporta.",
        "setup_minutos": 30,
        "needs_dev": 1,       # 1=no, 10=requiere equipo dev completo
        "tiempo_real": 3,     # 1=pobre, 10=streaming instantaneo
        "compatibilidad_scada": 5,
        "compatibilidad_pi": 7,
        "documentacion_existente": 10,  # OpenAPI completo
        "costo_implementar": 1,  # 1=bajo, 10=alto
        "requiere_instalacion": 1,  # 1=nada, 10=servidor dedicado
    },
    {
        "name": "WebSocket (Socket.IO)",
        "description": "Conexion persistente ws://backend:8080/ws. Recibe eventos "
                       "en tiempo real: tg_measurement, vlad_measurement, alert, "
                       "gateway_status. Ideal para dashboards en vivo.",
        "setup_minutos": 45,
        "needs_dev": 3,
        "tiempo_real": 10,
        "compatibilidad_scada": 2,
        "compatibilidad_pi": 4,
        "documentacion_existente": 10,
        "costo_implementar": 3,
        "requiere_instalacion": 2,
    },
    {
        "name": "RabbitMQ (cola de mensajes)",
        "description": "Suscribirse directamente a las colas tg_data, vlad_data "
                       "o al exchange ex.alerts. Recibe cada medicion como mensaje. "
                       "Para sistemas que ya usan message brokers.",
        "setup_minutos": 90,
        "needs_dev": 6,
        "tiempo_real": 9,
        "compatibilidad_scada": 3,
        "compatibilidad_pi": 6,
        "documentacion_existente": 10,
        "costo_implementar": 5,
        "requiere_instalacion": 4,
    },
    {
        "name": "MongoDB directo (lectura)",
        "description": "Dar acceso read-only a las colecciones de MongoDB. "
                       "El sistema minero consulta directamente la base de datos. "
                       "Requiere conocer el schema.",
        "setup_minutos": 20,
        "needs_dev": 4,
        "tiempo_real": 2,
        "compatibilidad_scada": 3,
        "compatibilidad_pi": 8,
        "documentacion_existente": 8,
        "costo_implementar": 2,
        "requiere_instalacion": 1,
    },
    {
        "name": "Exportacion CSV programada",
        "description": "Un scriptcron en el servidor genera CSV cada N minutos "
                       "y los deja en una carpeta compartida (SMB/NFS). "
                       "El sistema minero lee los archivos. Lo mas simple.",
        "setup_minutos": 15,
        "needs_dev": 1,
        "tiempo_real": 1,
        "compatibilidad_scada": 7,
        "compatibilidad_pi": 9,
        "documentacion_existente": 5,
        "costo_implementar": 1,
        "requiere_instalacion": 2,
    },
    {
        "name": "Bridge MQTT (nuevo modulo)",
        "description": "Desarrollar un modulo puente que publique los datos "
                       "en un broker MQTT. Protocolo standard IIoT, compatible "
                       "con SCADA modernos, Node-RED, AWS IoT, etc.",
        "setup_minutos": 120,
        "needs_dev": 7,
        "tiempo_real": 9,
        "compatibilidad_scada": 9,
        "compatibilidad_pi": 8,
        "documentacion_existente": 0,
        "costo_implementar": 7,
        "requiere_instalacion": 5,
    },
    {
        "name": "Bridge OPC UA (nuevo modulo)",
        "description": "Desarrollar servidor OPC UA que exponga los datos como tags "
                       "industriales. Estandar minero por excelencia. Compatible "
                       "con todos los SCADA sin programacion.",
        "setup_minutos": 180,
        "needs_dev": 8,
        "tiempo_real": 8,
        "compatibilidad_scada": 10,
        "compatibilidad_pi": 10,
        "documentacion_existente": 0,
        "costo_implementar": 9,
        "requiere_instalacion": 6,
    },
    {
        "name": "Grafana embed (iframe)",
        "description": "Crear dashboards de Grafana que lean de MongoDB y embeberlos "
                       "via iframe en el SCADA del cliente. Sin desarrollo extra. "
                       "Grafana ya esta instalado en muchos sitios mineros.",
        "setup_minutos": 60,
        "needs_dev": 3,
        "tiempo_real": 7,
        "compatibilidad_scada": 8,
        "compatibilidad_pi": 5,
        "documentacion_existente": 4,
        "costo_implementar": 3,
        "requiere_instalacion": 4,
    },
    {
        "name": "Webhook (HTTP POST out)",
        "description": "Nuestro backend envia HTTP POST a una URL del cliente "
                       "cada vez que hay un evento (alerta, medicion nueva). "
                       "Ellos solo exponen un endpoint.",
        "setup_minutos": 45,
        "needs_dev": 5,
        "tiempo_real": 8,
        "compatibilidad_scada": 6,
        "compatibilidad_pi": 7,
        "documentacion_existente": 0,
        "costo_implementar": 5,
        "requiere_instalacion": 3,
    },
]


# ============================================================
# CRITERIOS
# pesando simplicidad para el cliente minero (no para nosotros)
# ============================================================

CRITERIA = {
    "setup_minutos":          {"weight": 0.25, "type": "min", "ideal": 5,   "nadir": 240,
                               "note": "Tiempo estimado para que el cliente deje funcionando la integracion"},
    "needs_dev":              {"weight": 0.25, "type": "min", "ideal": 1,   "nadir": 10,
                               "note": "Cuanto desarrollo necesita el cliente (1=nada, 10=equipo completo)"},
    "tiempo_real":            {"weight": 0.10, "type": "max", "ideal": 10,  "nadir": 1,
                               "note": "Que tan en vivo llegan los datos"},
    "compatibilidad_scada":   {"weight": 0.15, "type": "max", "ideal": 10,  "nadir": 1,
                               "note": "Compatibilidad out-of-the-box con SCADA minero"},
    "compatibilidad_pi":      {"weight": 0.10, "type": "max", "ideal": 10,  "nadir": 1,
                               "note": "Facilidad de integracion con AVEVA PI System"},
    "documentacion_existente":{"weight": 0.10, "type": "max", "ideal": 10,  "nadir": 0,
                               "note": "Que tanta documentacion ya tenemos lista para esta opcion"},
    "costo_implementar":      {"weight": 0.05, "type": "min", "ideal": 1,   "nadir": 10,
                               "note": "Costo total para el cliente"},
}


def topsis_analysis(alternatives: list, criteria: dict) -> list:
    alts = [{k: v for k, v in a.items() if k in criteria} for a in alternatives]
    for a, orig in zip(alts, alternatives):
        a["name"] = orig["name"]

    scores = {}
    for a in alts:
        d_ideal = 0.0
        d_nadir = 0.0
        for crit, params in criteria.items():
            w = params["weight"]
            ideal = params["ideal"]
            nadir = params["nadir"]
            val = a[crit]
            if nadir == ideal:
                norm = 0.5
            else:
                if params["type"] == "min":
                    norm = (val - ideal) / (nadir - ideal)
                else:
                    norm = (ideal - val) / (ideal - nadir)
            norm = max(0.0, min(1.0, norm))
            d_ideal += (w * norm) ** 2
            d_nadir += (w * (1 - norm)) ** 2
        d_i = math.sqrt(d_ideal)
        d_n = math.sqrt(d_nadir)
        score = d_n / (d_i + d_n) if (d_i + d_n) > 0 else 0
        scores[a["name"]] = round(score, 4)

    ranked = sorted(alts, key=lambda x: scores[x["name"]], reverse=True)
    for i, a in enumerate(ranked):
        a["topsis_score"] = scores[a["name"]]
        a["rank"] = i + 1
    return ranked


def main():
    print("\n" + "=" * 72)
    print("  ANALISIS DE DECISION — INTEGRACION RDSS A SISTEMAS MINEROS")
    print("  Como un ingeniero de mina conecta nuestros datos a su SCADA/PI/Excel")
    print("=" * 72)
    print(f"\nFecha: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"Alternativas: {len(ALTERNATIVES)} | Criterios: {len(CRITERIA)}")
    print("Foco: simplicidad para el cliente final (no para nosotros)")

    # ---- Investigacion Gemini ----
    query = """
    Contexto: sistema de diagnostico remoto para amplificadores RF en mineria subterranea
    (leaky feeder). El sistema ya tiene API REST, WebSocket, RabbitMQ y MongoDB con datos
    de VLAD, TG, Becker Varis y TinySA (analizador de espectro).

    Responde brevemente:
    1. Como integran tipicamente las mineras datos de monitoreo a sus SCADA (Schneider, Wonderware)?
    2. Que protocolo es mas comun en mineria chilena: OPC UA, MQTT, Modbus TCP, REST?
    3. Que tan viable es para un ingeniero de mantenimiento (no desarrollador) integrar una API REST?
    4. Cual es el camino de menor friccion para que un supervisor de planta vea los datos manana mismo?
    5. Vale la pena desarrollar un bridge OPC UA o MQTT como modulo extra de nuestro producto?
    """
    print("\n" + "=" * 72)
    print("  Investigacion Gemini — integracion minera")
    print("=" * 72)
    research = search_with_gemini(query)
    print(f"\n{research}")

    # ---- TOPSIS ----
    print("\n" + "=" * 72)
    print("  TOPSIS — RANKING DE OPCIONES DE INTEGRACION")
    print("=" * 72)

    ranked = topsis_analysis(ALTERNATIVES, CRITERIA)

    header = f"{'#':<3} {'Opcion':<35} {'Setup':>6} {'Dev':>5} {'T.Real':>6} {'SCADA':>6} {'PI':>5} {'Docs':>5} {'$':>4} {'Score':>7}"
    print(f"\n{header}")
    print("-" * 90)

    for a in ranked:
        alt_data = next(x for x in ALTERNATIVES if x["name"] == a["name"])
        print(
            f"{a['rank']:<3} {a['name']:<35} "
            f"{alt_data['setup_minutos']:>4}min "
            f"{alt_data['needs_dev']:>4}/10 "
            f"{alt_data['tiempo_real']:>5}/10 "
            f"{alt_data['compatibilidad_scada']:>5}/10 "
            f"{alt_data['compatibilidad_pi']:>4}/10 "
            f"{alt_data['documentacion_existente']:>4}/10 "
            f"{alt_data['costo_implementar']:>3}/10 "
            f"{a['topsis_score']:>7.4f}"
        )

    # ---- Recomendacion por perfil ----
    print("\n" + "=" * 72)
    print("  RECOMENDACION POR PERFIL DE CLIENTE")
    print("=" * 72)

    best = ranked[0]
    best_data = next(x for x in ALTERNATIVES if x["name"] == best["name"])

    print(f"\n  [GANADOR ABSOLUTO] {best_data['name']}")
    print(f"  TOPSIS: {best['topsis_score']:.4f}")
    print(f"  Setup estimado: {best_data['setup_minutos']} minutos")
    print(f"  Necesita programador: {'NO' if best_data['needs_dev'] <= 2 else 'SI'} ({best_data['needs_dev']}/10)")
    print(f"  {best_data['description']}")

    # Perfiles especificos
    print("\n  --- Por perfil de cliente ---")

    profiles = {
        "Supervisor que quiere ver manana": [x for x in ranked if "CSV" in x["name"] or x["name"] == "API REST"][:2],
        "SCADA Schneider/Wonderware": [x for x in ranked if x["name"] in ["Bridge OPC UA (nuevo modulo)", "Bridge MQTT (nuevo modulo)", "Exportacion CSV programada"]],
        "PI System AVEVA": [x for x in ranked if x["name"] in ["Exportacion CSV programada", "MongoDB directo (lectura)", "API REST (HTTP GET)"]],
        "Ya tienen developers": [x for x in ranked if x["name"] in ["RabbitMQ (cola de mensajes)", "WebSocket (Socket.IO)", "API REST (HTTP GET)"]],
        "Solo quieren alertas (no datos)": [x for x in ranked if "Webhook" in x["name"] or x["name"] == "API REST"],
    }

    for profile, options in profiles.items():
        if options:
            name = options[0]["name"]
            print(f"\n  {profile}:")
            print(f"    -> {name}")
            if len(options) > 1:
                print(f"       (alternativa: {options[1]['name']})")

    # ---- Plan de accion ----
    print("\n" + "=" * 72)
    print("  PLAN DE ACCION RECOMENDADO")
    print("=" * 72)

    print("""
  FASE INMEDIATA (ya disponible, 0 desarrollo):
    1. Entregar al cliente documentacion OpenAPI (ya lista)
    2. Explicar como hacer GET /api/tg/devices desde su sistema
    3. Script de ejemplo en Python/PowerShell para consultar cada 30s
    4. Exportacion CSV diaria automatica desde MongoDB

  FASE CORTA (1-2 semanas de desarrollo):
    5. Implementar webhook saliente: nuestro backend hace POST
       a URL del cliente cuando hay alerta critica
    6. Endpoint /api/export/csv?type=all&from=YYYY-MM-DD para
       descarga manual desde el dashboard

  FASE MEDIANA (si hay demanda, 3-4 semanas):
    7. Modulo bridge MQTT opcional como add-on del producto
    8. Documentacion de integracion con AVEVA PI System via CSV connector

  FASE LARGA (si el cliente lo paga, 6-8 semanas):
    9. Servidor OPC UA como producto independiente
   10. Certificacion para SCADA Schneider, Wonderware, Siemens
""")

    # ---- Guardar ----
    results = {
        "fecha": datetime.now().isoformat(),
        "objetivo": "Integracion RDSS a sistemas mineros",
        "gemini_research": research,
        "topsis_ranking": [
            {"name": r["name"], "rank": r["rank"], "score": r["topsis_score"]}
            for r in ranked
        ],
        "recomendacion": best_data["name"],
        "plan_accion": "CSV + API REST inmediato; MQTT bridge a 3-4 semanas; OPC UA como producto premium",
    }

    out_dir = Path(__file__).parent.parent.parent / "results" / "mineria_integration_decision"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"  Resultados guardados en: {out_file}")
    print("\n  Analisis completado.")


if __name__ == "__main__":
    main()
