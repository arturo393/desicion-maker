#!/usr/bin/env python3
"""Comparativa: PLC puente Modbus vs API CSV vs opciones existentes"""
import math

ALTERNATIVES = [
    {
        "name": "PLC puente (Modbus TCP)",
        "desc": "PLC chico (Click, S7-1200, MicroLogix) entre nuestro server y "
                "la red SCADA. El PLC lee nuestra API/DB cada 1s y escribe a "
                "registros Modbus. El SCADA lee esos tags nativamente.",
        "setup_minutos": 120,
        "needs_dev": 2,
        "tiempo_real": 7,
        "compatibilidad_scada": 10,
        "compatibilidad_pi": 9,
        "documentacion_existente": 0,
        "costo_implementar": 3,
        "costo_hw_usd": 300,
    },
    {
        "name": "API CSV endpoint (/api/export/csv)",
        "desc": "Nuestro backend expone ruta GET /api/export/csv?type=becker&from=... "
                "que devuelve CSV. El cliente necesita un script que haga GET y "
                "lo guarde donde su sistema lo lee.",
        "setup_minutos": 10,
        "needs_dev": 5,
        "tiempo_real": 2,
        "compatibilidad_scada": 6,
        "compatibilidad_pi": 9,
        "documentacion_existente": 0,
        "costo_implementar": 2,
        "costo_hw_usd": 0,
    },
    {
        "name": "Dashboard web (ya existe)",
        "desc": "Acceso directo al dashboard RDSS. El supervisor abre el navegador. "
                "No se integra al SCADA pero cubre el 80% de los casos.",
        "setup_minutos": 5,
        "needs_dev": 0,
        "tiempo_real": 9,
        "compatibilidad_scada": 1,
        "compatibilidad_pi": 1,
        "documentacion_existente": 10,
        "costo_implementar": 0,
        "costo_hw_usd": 0,
    },
    {
        "name": "CSV en carpeta compartida (SMB)",
        "desc": "Scriptcron escribe CSVs a \\servidor\mineria\datos\ cada 5 min. "
                "PI System o cualquier SCADA importa desde carpeta compartida. "
                "Cero desarrollo del lado del cliente.",
        "setup_minutos": 20,
        "needs_dev": 1,
        "tiempo_real": 2,
        "compatibilidad_scada": 7,
        "compatibilidad_pi": 9,
        "documentacion_existente": 5,
        "costo_implementar": 1,
        "costo_hw_usd": 0,
    },
    {
        "name": "Bridge OPC UA (nuevo modulo)",
        "desc": "Servidor OPC UA que expone tags industriales. Compatible directo "
                "con Schneider, Wonderware, Siemens. Maxima compatibilidad SCADA.",
        "setup_minutos": 180,
        "needs_dev": 8,
        "tiempo_real": 8,
        "compatibilidad_scada": 10,
        "compatibilidad_pi": 10,
        "documentacion_existente": 0,
        "costo_implementar": 9,
        "costo_hw_usd": 0,
    },
]

CRITERIA = {
    "setup_minutos":           {"weight": 0.20, "type": "min", "ideal": 5,   "nadir": 240},
    "needs_dev":               {"weight": 0.30, "type": "min", "ideal": 0,   "nadir": 10},
    "tiempo_real":             {"weight": 0.05, "type": "max", "ideal": 10,  "nadir": 1},
    "compatibilidad_scada":    {"weight": 0.20, "type": "max", "ideal": 10,  "nadir": 1},
    "compatibilidad_pi":       {"weight": 0.10, "type": "max", "ideal": 10,  "nadir": 1},
    "documentacion_existente": {"weight": 0.05, "type": "max", "ideal": 10,  "nadir": 0},
    "costo_implementar":       {"weight": 0.05, "type": "min", "ideal": 0,   "nadir": 10},
    "costo_hw_usd":            {"weight": 0.05, "type": "min", "ideal": 0,   "nadir": 500},
}

scores = {}
for a in ALTERNATIVES:
    d_ideal = 0.0
    d_nadir = 0.0
    for crit, params in CRITERIA.items():
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
    scores[a["name"]] = round(d_n / (d_i + d_n) if (d_i + d_n) > 0 else 0, 4)

ranked = sorted(ALTERNATIVES, key=lambda x: scores[x["name"]], reverse=True)

print(f"  {'#':<3} {'Opcion':<38} {'Setup':>6} {'Dev':>5} {'SCADA':>6} {'PI':>5} {'$HW':>5} {'Score':>7}")
print("  " + "-" * 78)
for i, a in enumerate(ranked):
    s = scores[a["name"]]
    bar = int(s * 20) * "#"
    print(f"  {i+1:<3} {a['name']:<38} {a['setup_minutos']:>4}min {a['needs_dev']:>4}/10 {a['compatibilidad_scada']:>5}/10 {a['compatibilidad_pi']:>4}/10 "
          f"${a['costo_hw_usd']:>4} {s:>7.4f}")

# Detalle de los que importan
print(f"\n  --- EL QUE GANA ---")
best = ranked[0]
print(f"  {best['name']}")
print(f"  {best['desc']}")
print(f"  SCADA compat: {best['compatibilidad_scada']}/10 | Necesita dev: {best['needs_dev']}/10")

print(f"\n  --- PLC puente vs OPC UA ---")
plc = next(x for x in ranked if "PLC" in x["name"])
opc = next(x for x in ranked if "OPC" in x["name"])
print(f"  PLC puente:  score={scores[plc['name']]:.4f}, setup={plc['setup_minutos']}min, "
      f"dev={plc['needs_dev']}/10, hw=${plc['costo_hw_usd']}")
print(f"  OPC UA:      score={scores[opc['name']]:.4f}, setup={opc['setup_minutos']}min, "
      f"dev={opc['needs_dev']}/10, hw=${opc['costo_hw_usd']}")
print(f"  Diferencia:  PLC gana por {scores[plc['name']] - scores[opc['name']]:.4f} puntos TOPSIS")
print(f"  Motivo:      PLC usa hardware barato + instrumentista local. OPC UA requiere equipo dev.")
