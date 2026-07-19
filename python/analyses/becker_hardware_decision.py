#!/usr/bin/env python3
"""
Titulo: Analisis de Decision - Hardware Receptor FSK para Becker Varis en Gateway Leaky Feeder
Proposito: Evaluar 4 opciones para integrar recepcion Becker Varis (174.925 MHz FSK) en el
           gateway fsk-scanner existente (STM32G474 + 2x SX1276), para ser incluido en el
           case rack 3U del Noise Analyzer.

Fecha: 2026-06-24
Version: 1.0
Autor: Arturo Veras

CONTEXTO:
- Gateway existente: STM32G474 con 2 modulos SX1276 (LoRa TX y LoRa RX)
- Becker Varis: amplificadores leaky feeder que transmiten datos de diagnostico
  en 174.925 MHz, 2-FSK, 1920 bps, tramas de 13/14 bytes
- Los SX1276 soportan FSK (multi-modo: LoRa/FSK/OOK) pero no simultaneamente
- El case rack 3U ya contiene TinySA + SBC con RDSS Docker stack
- Se evaluo previamente el protocolo Becker (becker_ota_spec.md) y se tiene
  firmware fsk-scanner funcionando con FSK en SX1276

ALTERNATIVAS:
A = Reconfigurar SX1276 RX actual como receptor FSK permanente, el otro como LoRa TX/RX
B = Agregar modulo CC1125 dedicado para FSK (mismo chip que usa Becker)
C = Time-sharing: alternar un SX1276 entre LoRa y FSK periodicamente
D = Agregar un tercer modulo SX1276 dedicado para FSK
"""

import sys
import os
import json
import math
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

env_file = Path(__file__).parent.parent / ".env.gemini"
if env_file.exists():
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ[key.strip()] = value.strip()

from python.core.gemini_helper import GEMINI_AVAILABLE, search_with_gemini


# ============================================================
# ALTERNATIVAS
# ============================================================

ALTERNATIVES = [
    {
        "name": "A: Dual-mode SX1276 (reconfigurar)",
        "description": "SX1276 RX actual se configura permanentemente como receptor FSK Becker. "
                       "El otro SX1276 maneja LoRa TX/RX. Sin hardware adicional.",
        "cost_extra_usd": 0,
        "dev_time_days": 3,
        "hw_risk": 1,       # 1=bajo, 5=alto
        "sw_complexity": 3,  # 1=bajo, 5=alto
        "maintainability": 9, # 1-10
        "rf_performance": 7,  # 1-10 (SX1276 no optimizado para FSK pero funciona)
        "time_to_deploy_days": 5,
        "scalability": 8,    # si se necesita mas, se agrega HW
        "antenna_conflict": 7, # 10=no conflicto
    },
    {
        "name": "B: CC1125 adicional (chip nativo FSK Becker)",
        "description": "Agregar modulo CC1125 (mismo chip del DRX Becker) al STM32 por SPI. "
                       "Receptor FSK optimizado. Los SX1276 quedan intactos para LoRa.",
        "cost_extra_usd": 25,
        "dev_time_days": 8,
        "hw_risk": 3,
        "sw_complexity": 2,
        "maintainability": 8,
        "rf_performance": 10,
        "time_to_deploy_days": 15,
        "scalability": 9,
        "antenna_conflict": 10,
    },
    {
        "name": "C: Time-sharing (alternar modo)",
        "description": "Un solo SX1276 alterna entre modo LoRa y modo FSK periodicamente "
                       "(ej: 200ms FSK, 200ms LoRa). Sin hardware adicional.",
        "cost_extra_usd": 0,
        "dev_time_days": 5,
        "hw_risk": 1,
        "sw_complexity": 5,
        "maintainability": 3,
        "rf_performance": 3,
        "time_to_deploy_days": 7,
        "scalability": 2,
        "antenna_conflict": 5,
    },
    {
        "name": "D: Tercer SX1276 extra",
        "description": "Agregar un tercer modulo SX1276 por SPI al STM32G474, "
                       "configurado exclusivo para FSK Becker. Mismo chip, mismo driver.",
        "cost_extra_usd": 12,
        "dev_time_days": 5,
        "hw_risk": 2,
        "sw_complexity": 2,
        "maintainability": 9,
        "rf_performance": 7,
        "time_to_deploy_days": 10,
        "scalability": 8,
        "antenna_conflict": 7,
    },
]


# ============================================================
# CRITERIOS (pesos, tipo, ideal, nadir)
# ============================================================

CRITERIA = {
    "cost_extra_usd":    {"weight": 0.20, "type": "min", "ideal": 0,   "nadir": 30},
    "dev_time_days":     {"weight": 0.10, "type": "min", "ideal": 1,   "nadir": 10},
    "hw_risk":           {"weight": 0.15, "type": "min", "ideal": 1,   "nadir": 5},
    "sw_complexity":     {"weight": 0.10, "type": "min", "ideal": 1,   "nadir": 5},
    "maintainability":   {"weight": 0.10, "type": "max", "ideal": 10,  "nadir": 1},
    "rf_performance":    {"weight": 0.15, "type": "max", "ideal": 10,  "nadir": 1},
    "time_to_deploy_days":{"weight": 0.10, "type": "min", "ideal": 3,   "nadir": 20},
    "scalability":       {"weight": 0.05, "type": "max", "ideal": 10,  "nadir": 1},
    "antenna_conflict":  {"weight": 0.05, "type": "max", "ideal": 10,  "nadir": 1},
}


def topsis_analysis(alternatives: list, criteria: dict) -> list:
    """TOPSIS: ranking multicriterio. Mayor score = mejor."""
    alts = [{k: v for k, v in a.items() if k in criteria} for a in alternatives]
    for a, orig in zip(alts, alternatives):
        a["name"] = orig["name"]

    # Normalizar y calcular distancia a ideal/nadir
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


def check_hardware_constraints(alt: dict) -> dict:
    """Verifica restricciones de hardware y riesgos criticos."""
    ok = True
    fails = []
    warns = []

    if alt["hw_risk"] >= 4:
        warns.append(f"Riesgo HW alto ({alt['hw_risk']}/5)")

    if alt["rf_performance"] <= 4:
        fails.append(f"Performance RF insuficiente ({alt['rf_performance']}/10)")

    if alt["sw_complexity"] >= 4:
        warns.append(f"Complejidad SW alta ({alt['sw_complexity']}/5) — riesgo de bugs")

    if alt["time_to_deploy_days"] > 12:
        warns.append(f"Tiempo de despliegue alto ({alt['time_to_deploy_days']} dias)")

    if alt["antenna_conflict"] <= 4:
        fails.append(f"Conflicto de antena: necesita duplexer o antena separada")

    return {"apto": ok, "fails": fails, "warns": warns}


def research_hardware_options() -> str:
    """Investigacion con Gemini sobre opciones de hardware."""
    query = """
    Evaluacion de opciones hardware para recibir senal FSK en 174.925 MHz con SX1276.
    Contexto: sistema leaky feeder con STM32G474 y 2x SX1276 existentes.
    
    Responde especificamente:
    1. Cual es la sensibilidad del SX1276 en modo FSK a 174.925 MHz comparado con un CC1125?
    2. Es viable usar un solo SX1276 alternando entre LoRa y FSK? Que latencia introduce?
    3. Cuanto espacio/memoria adicional consume el driver FSK vs LoRa en el STM32?
    4. Hay problemas conocidos del SX1276 en banda VHF (174 MHz)?
    5. Que recomendarias para un MVP con minimo hardware adicional?
    """
    print("\n" + "=" * 70)
    print("   Investigacion con Gemini sobre hardware de radio")
    print("=" * 70)
    result = search_with_gemini(query)
    return result


def main():
    print("\n" + "=" * 70)
    print("   ANALISIS DE DECISION - HARDWARE RECEPTOR BECKER VARIS")
    print("   Gateway Leaky Feeder (fw-gateway2Lora)")
    print("=" * 70)
    print(f"\nFecha: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("Objetivo: Seleccionar la mejor arquitectura de hardware para recibir")
    print("         tramas FSK Becker Varis sin comprometer recepcion LoRa existente")
    print(f"\nAlternativas evaluadas: {len(ALTERNATIVES)}")
    print(f"Criterios: {len(CRITERIA)} (TOPSIS)")

    # ---- Investigacion Gemini ----
    research_text = research_hardware_options()
    print("\nRESULTADOS INVESTIGACION GEMINI:\n")
    print(research_text)

    # ---- TOPSIS ----
    print("\n" + "=" * 70)
    print("   TOPSIS — RANKING DE ALTERNATIVAS")
    print("=" * 70)

    ranked = topsis_analysis(ALTERNATIVES, CRITERIA)

    header = f"{'#':<3} {'Alternativa':<40} {'$Extra':>7} {'Dev(d)':>6} {'HWRisk':>6} {'SWComp':>6} {'RF':>5} {'Mant':>5} {'Score':>7}"
    print(f"\n{header}")
    print("-" * 90)

    for a in ranked:
        alt_data = next(x for x in ALTERNATIVES if x["name"] == a["name"])
        print(
            f"{a['rank']:<3} {a['name']:<40} "
            f"${alt_data['cost_extra_usd']:>6} "
            f"{alt_data['dev_time_days']:>5}d "
            f"{alt_data['hw_risk']:>5}/5 "
            f"{alt_data['sw_complexity']:>5}/5 "
            f"{alt_data['rf_performance']:>4}/10 "
            f"{alt_data['maintainability']:>4}/10 "
            f"{a['topsis_score']:>7.4f}"
        )

    # ---- Verificacion de restricciones ----
    print("\n" + "=" * 70)
    print("   VERIFICACION DE RESTRICCIONES")
    print("=" * 70)

    aptos = []
    for alt in ALTERNATIVES:
        req = check_hardware_constraints(alt)
        status = "APTO" if req["apto"] else "NO APTO"
        print(f"\n{'[APTO]' if req['apto'] else '[NO APTO]'} {alt['name']} — {status}")
        if req["fails"]:
            for f in req["fails"]:
                print(f"     [FAIL] {f}")
        if req["warns"]:
            for w in req["warns"]:
                print(f"     [WARN] {w}")
        if req["apto"]:
            aptos.append(alt)

    # ---- Recomendacion final ----
    print("\n" + "=" * 70)
    print("   RECOMENDACION FINAL")
    print("=" * 70)

    ranked_aptos = [r for r in ranked if any(a["name"] == r["name"] for a in aptos)]

    if ranked_aptos:
        best = ranked_aptos[0]
        best_data = next(x for x in ALTERNATIVES if x["name"] == best["name"])
        print(f"\n  Opcion recomendada: {best_data['name']}")
        print(f"  TOPSIS score:        {best['topsis_score']:.4f}")
        print(f"  Costo extra:          ${best_data['cost_extra_usd']}")
        print(f"  Tiempo desarrollo:    {best_data['dev_time_days']} dias")
        print(f"  Tiempo a despliegue:  {best_data['time_to_deploy_days']} dias")
        print(f"  Performance RF:       {best_data['rf_performance']}/10")
        print(f"  Mantenibilidad:       {best_data['maintainability']}/10")
        print(f"\n  {best_data['description']}")

        if len(ranked_aptos) > 1:
            second = ranked_aptos[1]
            second_data = next(x for x in ALTERNATIVES if x["name"] == second["name"])
            print(f"\n  Alternativa: {second_data['name']}")
            print(f"  TOPSIS score: {second['topsis_score']:.4f}")
    else:
        print("\n  Ninguna opcion cumple todos los requisitos. Ver investigacion Gemini.")

    # ---- Guardar resultados ----
    results = {
        "fecha": datetime.now().isoformat(),
        "objetivo": "Seleccion hardware receptor FSK para Becker Varis en Gateway",
        "gemini_research": research_text,
        "topsis_ranking": [
            {"name": r["name"], "rank": r["rank"], "score": r["topsis_score"]}
            for r in ranked
        ],
        "aptos": [a["name"] for a in aptos],
        "recomendacion": ranked_aptos[0]["name"] if ranked_aptos else "Ver investigacion Gemini",
        "criterios_usados": list(CRITERIA.keys()),
    }

    out_dir = Path(__file__).parent.parent.parent / "results" / "becker_hardware_decision"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\n  Resultados guardados en: {out_file}")
    print("\n  Analisis completado.")


if __name__ == "__main__":
    main()
