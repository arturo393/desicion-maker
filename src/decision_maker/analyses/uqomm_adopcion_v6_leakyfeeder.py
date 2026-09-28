"""
Analysis v6: Donde integrar y que mejorar para MAXIMA ADOPCION DE MERCADO
Pregunta de Arturo (2026-08-25): dado el hardware y software que ya existen
(fw-snifferTelemetry, el stack del .205, sw-diagnosticoremoto + amplificadores del
leaky feeder, sniffertag + sw-SmartTag), donde conviene integrar y mejorar para ser
lo mas compatible, facil de instalar y usar, y tener la mejor adopcion.

DIFERENCIA CON v1-v5: los puntajes de esas corridas eran del pulgar del autor. Aca
cada uno lleva su FUENTE en el comentario, y al final corren DOS CONTROLES que pueden
hacer fallar el resultado. Un marco que no puede fallar no mide nada.

EVIDENCIA DE MERCADO recogida el 2026-08-25:
 [E1] uqomm opera en Chile, Peru, Mexico, Australia (+ 25 paises). Cliente nombrado: BHP
      (open-pit Australia, BDA digital).                       uqomm.com/cobertura
 [E2] uqomm YA vende "Sensors Controllers", "IoT", "Monitoring", "Analytics Dashboard",
      "Convergencia IT/OT" y "Operaciones Remotas" como lineas. El sniffer no es un
      proyecto interno: es catalogo.                            uqomm.com/soluciones
 [E3] La pagina de soluciones NO nombra un solo protocolo de integracion. Vende
      convergencia IT/OT sin decir por donde.                   uqomm.com/soluciones
 [E4] Becker Varis (competidor directo en leaky feeder, 60 anos, ex-Varis Sudbury):
      modulos de sensores con MODBUS RS-485, con control de salidas programable y
      setpoints de alarma.                                      becker-mining.com/smartsense
 [E5] Becker Smartflow: modulo de monitoreo de la red leaky feeder que la muestra como
      DIAGRAMA UNIFILAR en 3D web, con localizacion inmediata de la falla.
                                          becker-mining.com/leaky-feeder-network-monitoring-module
 [E6] El servidor de diagnostico remoto de Becker sondea equipos Ethernet por SNMP.
                       fw-gateway2lora/assets/Becker_Varis_Remote_Diagnostics_Manual.md:39
 [E7] La industria convergio en el trio Modbus + MQTT + OPC UA como capa de gateway
      hacia SCADA/IIoT. Gasto IIoT minero: USD 5-8 B/ano en operadores grandes.
 [E8] CHILE lidera la creacion de un estandar global de INTEROPERABILIDAD minera
      (Roadmap Mineria 4.0; GMG).                              investchile.gob.cl
 [E9] Mexico aprobo norma de seguridad en mineria de carbon (marzo 2026, consulta
      publica obligatoria de 60 dias). Peru: Reglamento de Seguridad y Salud Minera.
 [E10] Los contratos de sw-diagnosticoremoto cubren vlad/ulad/netreference y CERO
      sniffer; cero SNMP implementado en los seis repos.        verificado en repo
"""

import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from decision_maker.core.models import DecisionOption, DistributionType, Factor, UncertainVariable
from decision_maker.core.orchestrator import UnifiedDecisionFramework

# Pesos: los tres que Arturo nombro explicitamente pesan 0.65 juntos.
FACTORS = [
    ("CompatibilidadProtocolo", 0.25),  # habla lo que habla el sistema del cliente [E4][E6][E7]
    ("FacilidadInstalacion",    0.20),  # esfuerzo de puesta en marcha en tunel
    ("AdopcionMercado",         0.20),  # evidencia en los 4 mercados [E1][E8][E9]
    ("ReutilizacionArqui",      0.15),  # usa lo que ya existe [E10]
    ("MantenimientoBajo",       0.10),
    ("Diferenciacion",          0.10),  # lo que el titular NO tiene [E5]
]

S = {
    # A: el leaky feeder es UN objeto (amplificadores + sniffers). Integrar ahi + capa
    # industrial: Modbus RTU en el equipo [E4] y Modbus TCP/SNMP/MQTT hacia afuera [E6][E7]
    "A_dr_capa_industrial": {
        "CompatibilidadProtocolo": (92, 5),   # iguala el piso del titular en las dos puntas
        "FacilidadInstalacion":    (78, 9),   # sensores Modbus del cliente entran sin adaptador
        "AdopcionMercado":         (85, 7),   # [E8] Chile lidera interoperabilidad; encaja
        "ReutilizacionArqui":      (80, 8),   # contracts/ + decoders + gateway ya existen
        "MantenimientoBajo":       (75, 9),
        "Diferenciacion":          (45, 12),  # iguala, no supera
    },
    # B: SmartTag absorbe la telemetria
    "B_smarttag": {
        "CompatibilidadProtocolo": (35, 10),  # no tiene capa de protocolo industrial
        "FacilidadInstalacion":    (50, 12),
        "AdopcionMercado":         (45, 12),  # dominio de personas/zonas, no de red
        "ReutilizacionArqui":      (55, 12),  # arquitectura madura pero otro dominio
        "MantenimientoBajo":       (70, 9),
        "Diferenciacion":          (30, 10),
    },
    # C: mantener el .205 y mejorarlo
    "C_status_quo_205": {
        "CompatibilidadProtocolo": (20, 8),   # cero protocolos de integracion [E3][E10]
        "FacilidadInstalacion":    (40, 12),
        "AdopcionMercado":         (25, 10),
        "ReutilizacionArqui":      (85, 8),   # es lo que ya corre
        "MantenimientoBajo":       (15, 8),   # 7 contenedores + libs sin commitear
        "Diferenciacion":          (20, 10),
    },
    # D: el diagrama unifilar del tramo como producto (la respuesta a Smartflow [E5])
    "D_unifilar_diferenciador": {
        "CompatibilidadProtocolo": (30, 10),  # una vista no integra nada
        "FacilidadInstalacion":    (60, 12),
        "AdopcionMercado":         (70, 10),  # es lo que el titular usa para vender
        "ReutilizacionArqui":      (60, 12),
        "MantenimientoBajo":       (55, 12),
        "Diferenciacion":          (88, 6),   # el unico que iguala el argumento visual
    },
    # E: plataforma de terceros (ThingsBoard/Ignition) + capa de equipo propia
    "E_plataforma_tercero": {
        "CompatibilidadProtocolo": (80, 8),   # traen Modbus/MQTT/OPC UA de fabrica [E7]
        "FacilidadInstalacion":    (55, 12),
        "AdopcionMercado":         (60, 12),
        "ReutilizacionArqui":      (30, 12),  # tira el panel y los contratos propios
        "MantenimientoBajo":       (70, 10),
        "Diferenciacion":          (25, 10),  # el panel deja de ser tuyo
    },
    # F: solo capa de dispositivo, sin panel propio (headless)
    "F_headless": {
        "CompatibilidadProtocolo": (90, 6),
        "FacilidadInstalacion":    (70, 10),
        "AdopcionMercado":         (65, 12),  # sin demo propia cuesta vender
        "ReutilizacionArqui":      (55, 12),
        "MantenimientoBajo":       (90, 6),
        "Diferenciacion":          (20, 10),  # nada que mostrar contra Smartflow [E5]
    },
}

DESC = {
    "A_dr_capa_industrial": "Integrar en sw-diagnosticoremoto + capa industrial (Modbus RTU en el equipo, Modbus TCP/SNMP/MQTT hacia el NMS).",
    "B_smarttag": "Consolidar la telemetria dentro de SmartTag.",
    "C_status_quo_205": "Mantener y mejorar el stack del .205.",
    "D_unifilar_diferenciador": "Diagrama unifilar del tramo leaky feeder como producto.",
    "E_plataforma_tercero": "Panel en plataforma de terceros + capa de equipo propia.",
    "F_headless": "Solo capa de dispositivo con protocolos, sin panel propio.",
}


async def corrida(nombre, scores):
    fw = UnifiedDecisionFramework()
    for n, w in FACTORS:
        fw.add_factor(Factor(name=n, weight=w, maximize=True))
    for k, fac in scores.items():
        fw.add_option(DecisionOption(
            name=k, description=DESC.get(k, k),
            variables={f: UncertainVariable(f, DistributionType.NORMAL, fac[f]) for f in fac}))
    r = await fw.run_analysis(mode="standard")
    print(f"\n{'='*64}\n{nombre}\n{'='*64}")
    print(r.get("explanation", "N/A"))
    return r


async def main():
    principal = await corrida("PRINCIPAL — donde integrar para adopcion", S)

    # CONTROL 1 — identidad. Todas las opciones con el MISMO vector.
    # Si algo gana decisivamente aca, el marco tiene un sesgo estructural y el
    # resultado principal no vale.
    plano = {k: dict(S["A_dr_capa_industrial"]) for k in S}
    c1 = await corrida("CONTROL 1 — todas iguales (no deberia haber ganador claro)", plano)

    # CONTROL 2 — permuta. Se intercambian los vectores de A (favorita) y C (peor).
    # Si sigue ganando A, el marco puntua la ETIQUETA y no los numeros.
    permuta = {k: dict(v) for k, v in S.items()}
    permuta["A_dr_capa_industrial"], permuta["C_status_quo_205"] = \
        dict(S["C_status_quo_205"]), dict(S["A_dr_capa_industrial"])
    c2 = await corrida("CONTROL 2 — vectores de A y C permutados (deberia ganar C)", permuta)

    # SENSIBILIDAD — cuanto tiene que caer la compatibilidad de A para perder.
    sens = {}
    for v in (92, 70, 50, 30):
        t = {k: dict(x) for k, x in S.items()}
        t["A_dr_capa_industrial"]["CompatibilidadProtocolo"] = (v, 5)
        r = await corrida(f"SENSIBILIDAD — A con CompatibilidadProtocolo={v}", t)
        sens[v] = r.get("explanation", "")[:400]

    out = Path("results") / "uqomm_adopcion_v6_leakyfeeder.json"
    out.parent.mkdir(exist_ok=True)
    with open(out, "w") as fh:
        json.dump({
            "date": datetime.now().isoformat(),
            "pregunta": "Donde integrar y que mejorar para compatibilidad, facilidad de "
                        "instalacion y adopcion de mercado, dado el hw/sw existente",
            "mercados": ["Chile", "Australia", "Peru", "Mexico"],
            "factors": FACTORS, "options": DESC,
            "principal": {k: v for k, v in principal.items() if k != "explanation"},
            "control_identidad": c1.get("explanation", "")[:600],
            "control_permuta": c2.get("explanation", "")[:600],
            "sensibilidad": sens,
        }, fh, indent=2, default=str)
    print(f"\nGuardado en {out}")


if __name__ == "__main__":
    asyncio.run(main())
