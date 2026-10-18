"""
Analysis: Piloto Nexa — ¿el plan está completo? Huecos de base de datos, backend, frontend y firmware
Purpose: Ordenar los huecos que todavía no tienen tarea en el plan Nexa (fw-snifferTelemetry
  docs/proyectos/nexa-cerro-lindo/PLAN.md) por lo que cuestan si faltan, y decidir para cada uno:
  entra al PILOTO, entra ANTES DEL SEGUNDO SNIFFER, o va DESPUÉS. Mide además cuánto mueve el piloto
  lo que entra.
Created: 2026-10-16
Version: 1.1

Fuente de los huecos: relevamiento de sw-diagnosticoremoto (commit 35effd41) y de fw-core del
16-Oct-2026, verificado en el código lo marcado como tal en el plan.

Criterios (juicio 0-100 salvo Esfuerzo):
  RiesgoSiFalta - daño, silencio o seguridad si no se hace (una bomba que se mueve sola, un equipo
                  que deja de vigilarse sin error)
  Piloto        - lo exige un RF/RD del PRD Nexa o la SAT
  Escala        - lo exige tener muchos sniffers o varios gateways
  Retrocompat   - protege a las familias que ya existen (VLAD, VLAD25, Becker, NetReference)
  Mantenible    - deja una sola fuente, un test o un mecanismo en vez de una promesa
  Esfuerzo      - días-persona (moda)
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

analysis_name = "nexa_plan_completitud"
analysis_date = datetime.now().isoformat()

# id: (descripción, capa, rama fw|sw, RiesgoSiFalta, Piloto, Escala, Retrocompat, Mantenible, Esfuerzo)
HUECOS = {
    "G01_registrar_0x10": ("monitor-serial: registrar el largo de la familia 0x10; hoy una trama de sniffer se lleva hasta 512 B del COM2, telemetría VLAD25 incluida", "monitor-serial", "sw", 95, 90, 40, 95, 60, 0.3),
    "G02_poller_filtra_tipo": ("monitor-serial: el sondeo VLAD filtra por device_type; hoy sondea todo lo aprovisionado", "monitor-serial", "sw", 75, 70, 40, 90, 60, 0.5),
    "G03_uid_en_set_outputs": ("fw-core: SET_OUTPUTS verifica el UID destino; hoy una orden la ejecutan todos los sniffers del gateway", "firmware", "fw", 90, 60, 95, 40, 60, 0.5),
    "G04_opcodes_radio_libres": ("fw-core: consultas de radio fuera de 0x20-0x25 (chocan con E/S; 0x22 puede mover salidas) + test de no-choque", "firmware", "fw", 80, 80, 50, 50, 85, 1.0),
    "G05_consulta_informacion": ("fw-core + DR + Suite: consulta de información TLV (firmware, id, arranque, enlace, salud, FOTA, configuración)", "firmware", "fw", 40, 75, 70, 30, 70, 2.5),
    "G06_registro_ordenes": ("Mongo + backend: colección de órdenes (quién, qué, cuándo, cmd_count, confirmada) y motor de confirmación por efecto con alarma", "backend", "sw", 85, 95, 60, 40, 70, 2.0),
    "G07_rol_en_backend": ("backend: capacidad 'operar bomba' verificada en Go, no solo en la pantalla", "backend", "sw", 90, 95, 50, 40, 70, 1.0),
    "G08_ritmo_por_equipo": ("backend: una orden en vuelo por equipo y un intervalo mínimo; hoy 100/s por IP", "backend", "sw", 75, 80, 60, 30, 60, 0.5),
    "G09_umbral_unico": ("backend + frontend: un solo umbral de frescura que leen el vigía y la pantalla; sniffer en el vigía (hoy una familia ausente se saltea sin aviso)", "backend", "sw", 85, 90, 60, 50, 90, 1.5),
    "G10_alarmas_contrato": ("contratos + frontend: tipos de alarma nuevos, etiquetas y pestaña sniffer (y la de vlad_telemetry que ya falta)", "frontend", "sw", 55, 85, 40, 40, 60, 0.5),
    "G11_ttl_indices": ("Mongo: sniffer_measurements con TTL e índice (equipo, fecha); crear los índices que el contrato declara", "base de datos", "sw", 45, 50, 90, 40, 70, 1.0),
    "G12_config_por_equipo": ("Mongo + backend: configuración por equipo con versión (escalas 4-20 mA, contrato de radio, tabla de puntos)", "base de datos", "sw", 60, 75, 85, 30, 85, 1.5),
    "G13_fota_persistente": ("monitor-serial + Mongo: sesiones de FOTA guardadas; hoy en memoria, se pierden al reiniciar", "monitor-serial", "sw", 55, 60, 60, 30, 60, 1.0),
    "G14_gateway_id": ("monitor-serial + backend: gateway_id en cada mensaje y en el equipo; órdenes al gateway correcto (hoy uno solo)", "backend", "sw", 40, 20, 95, 40, 60, 4.0),
    "G15_respaldo_mongo": ("operación: respaldo y restauración de Mongo probados (hoy solo el .env)", "base de datos", "sw", 70, 55, 50, 70, 60, 1.0),
    "G16_hora_ntp": ("operación: sincronización de hora del servidor; la edad de cada dato depende del reloj", "operación", "sw", 60, 70, 40, 50, 50, 0.5),
    "G17_ci_dr": ("DR: los tests de Go corren antes de cada push (hoy solo si hay .go en el commit, y no hay CI)", "backend", "sw", 55, 40, 60, 75, 90, 1.5),
    "G18_websocket_no_bloquea": ("backend: el hub de WebSocket con plazo de escritura; un cliente lento hoy frena a todos", "backend", "sw", 45, 30, 85, 40, 50, 1.0),
    "G19_http_monitor_hilos": ("monitor-serial: servidor HTTP con hilos; hoy un POST largo (FOTA) bloquea /health", "monitor-serial", "sw", 55, 60, 50, 50, 50, 0.5),
    "G20_rabbit_definiciones": ("RabbitMQ: definitions.json con vlad_telemetry_data y la cola del sniffer, y política de cola muerta", "backend", "sw", 50, 50, 50, 75, 60, 0.5),
    "G21_rutas_next_sin_guarda": ("frontend: las rutas API de Next sin guarda (device/save, editDeviceProvisioned)", "frontend", "sw", 75, 50, 40, 60, 60, 1.0),
    "G22_guarda_por_pagina": ("frontend: guarda por página con denegación por defecto y test que exige dueño a cada página", "frontend", "sw", 55, 40, 50, 60, 85, 1.5),
    "G23_migraciones": ("Mongo: migraciones versionadas para crear colecciones, índices y TTL", "base de datos", "sw", 45, 40, 75, 70, 90, 1.5),
    "G24_imagen_en_sitio": ("operación: imagen instalable de la plataforma para la red de la mina (R10)", "operación", "sw", 60, 70, 60, 30, 60, 2.5),
    "G25_admision_equipo": ("backend: un sniffer se da de alta en la puesta en marcha, no por la primera trama (lección de los Becker fantasma)", "backend", "sw", 55, 60, 70, 50, 60, 0.5),
    "G26_changelog_dr": ("DR: CHANGELOG y versión alineados con los tags (v4.2.0 contra v3.2.0)", "mantenimiento", "sw", 30, 40, 30, 50, 70, 0.5),
    "G27_modelo_canonico": ("Mongo: una sola clave de identidad para todas las familias (PLAN_MODELO_CANONICO)", "base de datos", "sw", 50, 20, 80, 50, 90, 5.0),
    "G28_exportador": ("backend: exportador Modbus TCP o MQTT desde la tabla de puntos (RF-09)", "backend", "sw", 20, 20, 80, 30, 70, 4.0),
    "G29_retirar_v2": ("terreno: reflashear el único sniffer v2.x con fw-core y retirar el .205", "operación", "fw", 40, 20, 50, 60, 80, 1.0),
}
CRIT = ["RiesgoSiFalta", "Piloto", "Escala", "Retrocompat", "Mantenible"]

factors = [
    Factor(name="RiesgoSiFalta", weight=0.30, maximize=True),
    Factor(name="Piloto", weight=0.25, maximize=True),
    Factor(name="Escala", weight=0.10, maximize=True),
    Factor(name="Retrocompat", weight=0.15, maximize=True),
    Factor(name="Mantenible", weight=0.10, maximize=True),
    Factor(name="Esfuerzo", weight=0.10, maximize=False),
]


# Lo que es requisito de algo que ya está en el piloto: G19, porque la FOTA por LoRa (T14) es un POST
# largo que hoy bloquea /health de monitor-serial.
DEPENDENCIA_DEL_PILOTO = {"G19_http_monitor_hilos"}


def destino(k, h, puntaje: float) -> str:
    """Regla de corte, escrita para que se pueda discutir: el MCDM ordena, esto decide el balde.
    v1.1: además entra lo que puntúa >= 0,48 y cuesta <= 1,5 días (en la v1.0 quedaban afuera el
    respaldo de Mongo, el CI y la admisión del equipo con más puntaje que cosas de adentro)."""
    _, _, _, riesgo, piloto, escala, retro, _, dias = h
    if piloto >= 70 or (riesgo >= 75 and dias <= 1.5) or retro >= 90:
        return "PILOTO"
    if k in DEPENDENCIA_DEL_PILOTO or (puntaje >= 0.48 and dias <= 1.5):
        return "PILOTO"
    if escala >= 80:
        return "ANTES_DEL_2DO_SNIFFER"
    return "DESPUES"


async def main():
    fw = UnifiedDecisionFramework()
    for f in factors:
        fw.add_factor(f)
    for k, h in HUECOS.items():
        v = {c: UncertainVariable(c, DistributionType.NORMAL, [h[3 + i], 8]) for i, c in enumerate(CRIT)}
        v["Esfuerzo"] = UncertainVariable("Esfuerzo", DistributionType.NORMAL, [h[8], max(0.1, h[8] * 0.3)])
        fw.add_option(DecisionOption(name=k, description=h[0], variables=v))
    results = await fw.run_analysis(mode="standard")
    ranking = results["topsis_scores"]

    baldes = {"PILOTO": [], "ANTES_DEL_2DO_SNIFFER": [], "DESPUES": []}
    for k in ranking.index:
        baldes[destino(k, HUECOS[k], float(ranking[k]))].append(k)
    for b, ks in baldes.items():
        dias_fw = sum(HUECOS[k][8] for k in ks if HUECOS[k][2] == "fw")
        dias_sw = sum(HUECOS[k][8] for k in ks if HUECOS[k][2] == "sw")
        print(f"\n{b}: {len(ks)} huecos, fw {dias_fw:.1f} d, sw {dias_sw:.1f} d")
        for k in ks:
            print(f"   {ranking[k]:.2f}  {k:<26} {HUECOS[k][8]:>4} d  {HUECOS[k][1]}")

    piloto = baldes["PILOTO"]
    fw_d = sum(HUECOS[k][8] for k in piloto if HUECOS[k][2] == "fw")
    sw_d = sum(HUECOS[k][8] for k in piloto if HUECOS[k][2] == "sw")
    # Lo que ya estaba en el plan (T2, T3, T3b) se descuenta para no contarlo dos veces.
    ya_en_plan = {"G01_registrar_0x10": 0.3, "G06_registro_ordenes": 2.0, "G07_rol_en_backend": 1.0}
    sw_nuevo = sw_d - sum(v for k, v in ya_en_plan.items() if k in piloto)
    sat, fat = nexa.simular("A_CONTACTOS_FWCORE", con_fat=True,
                            extra_fw=lambda: nexa.tri(fw_d * 0.8, fw_d, fw_d * 1.5),
                            extra_sw=lambda: nexa.tri(sw_nuevo * 0.8, sw_nuevo, sw_nuevo * 1.5))
    impacto = {
        "fw_dias": fw_d, "sw_dias_nuevos": round(sw_nuevo, 1),
        "p_a_tiempo": round(float(np.mean(sat <= nexa.PLAZO)), 3),
        "fat_p80_sobre_plan_15oct": nexa.fecha_de(float(np.percentile(fat, 80))).isoformat(),
    }
    print(f"\nImpacto del balde PILOTO sobre el plan del 15-Oct: {impacto}")

    out = Path("results") / f"{analysis_name}.json"
    out.parent.mkdir(exist_ok=True)
    with open(out, "w") as f:
        json.dump({"name": analysis_name, "date": analysis_date, "huecos": HUECOS,
                   "ranking": {k: float(v) for k, v in ranking.items()}, "baldes": baldes,
                   "impacto_piloto": impacto, "factors": [(x.name, x.weight) for x in factors],
                   "raw": {k: v for k, v in results.items() if k != "explanation"}},
                  f, indent=2, default=str)
    print(f"\nResultados guardados en {out}")


if __name__ == "__main__":
    asyncio.run(main())
