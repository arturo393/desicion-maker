#!/usr/bin/env python3
"""
Título: Análisis de Decisión - Analizador de Espectro para Mesa de Pruebas
Propósito: Evaluar analizadores de espectro de bajo costo para sustituir Siglent SSA3015X Plus
           en las suites gain_check y agc_check del sw-testbench.

Fecha de Creación: 2026-03-18
Versión: 1.0

CONTEXTO:
- Suite actual usa Siglent SSA3015X Plus ($1,360) o SA44B ($1,295)
- Se busca alternativa de menor costo que cumpla requisitos mínimos
- El equipo NO necesita pantalla (control por comandos)
- Rango crítico: VHF (30 MHz - 300 MHz), extendido hasta ~1 GHz
- Mediciones: potencia de salida de repetidores (-20 a +10 dBm)
- Precisión mínima requerida: ±1 dB para producción
- Integración: Python via API/DLL/SCPI/serial

REQUISITOS TÉCNICOS MÍNIMOS:
- Rango frecuencial: al menos 30 MHz - 1 GHz (VHF completo)
- DANL: < -90 dBm (señales de -20 a +10 dBm → margen suficiente de >70 dB)
- Precisión amplitud: ±1 dB máximo (producción)
- RBW mínimo: < 10 kHz
- Control programático: API/serial/SCPI (no necesita pantalla)
- Precio objetivo: < $500 USD
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime

# Agregar path al core del framework
sys.path.insert(0, str(Path(__file__).parent.parent))

# Cargar API key desde .env.gemini
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
# ALTERNATIVAS A EVALUAR
# ============================================================

# NOTA: precios verificados directamente en sitios oficiales (marzo 2026)
# rigolna.com | siglentna.com | signalhound.com

ALTERNATIVES = [
    # ---- HEADLESS USB (sin pantalla, solo necesita PC) ----
    {
        "name": "Signal Hound SA44B",
        "price_usd": 1295,  # verificado signalhound.com
        "freq_range": "1 Hz - 4.4 GHz",
        "danl_dbm": -151,
        "amplitude_accuracy_db": 0.25,
        "rbw_min_hz": 1,
        "interface": "USB 2.0 (SDK Python nativo + DLL)",
        "has_screen": False,
        "zero_span": True,
        "headless": True,
        "calibration": "OPCIONAL (costo extra). Base: sin certificado impreso. Con cert. NIST-traceable: ~$450 adicional. Seleccionar al comprar en signalhound.com.",
        "notes": "SIN PANTALLA. USB. SDK Python oficial. 4.4 GHz. $1,295 verificado.",
    },
    {
        "name": "Signal Hound SA124B",
        "price_usd": 2850,  # verificado signalhound.com
        "freq_range": "100 kHz - 12.4 GHz",
        "danl_dbm": -153,
        "amplitude_accuracy_db": 0.5,
        "rbw_min_hz": 1,
        "interface": "USB 2.0 (SDK Python nativo + DLL)",
        "has_screen": False,
        "zero_span": True,
        "headless": True,
        "calibration": "OPCIONAL (costo extra). Mismo esquema que SA44B. Cert. NIST-traceable ~$450-$500 adicional al comprar.",
        "notes": "SIN PANTALLA. USB. 12.4 GHz. SDK Python. $2,850 verificado.",
    },
    # ---- BENCH CON PANTALLA, OPERABLES HEADLESS VIA SCPI/LAN ----
    {
        "name": "Siglent SSA3015X Plus",
        "price_usd": 1360,  # verificado siglentna.com
        "freq_range": "9 kHz - 1.5 GHz",
        "danl_dbm": -156,
        "amplitude_accuracy_db": 1.2,
        "rbw_min_hz": 1,
        "interface": "LAN + USB (SCPI/VISA) - headless via Ethernet",
        "has_screen": True,
        "zero_span": True,
        "headless": True,
        "calibration": "INCLUIDO. Cert. de Calibracion trazable a SI/NIST/NIM/PTB via CIPM MRA. ISO17025 acreditado disponible como opcion adicional al comprar.",
        "notes": "Bench. Headless via LAN SCPI. $1,360 verificado siglentna.com.",
    },
    {
        "name": "Siglent SSA3021X (no Plus)",
        "price_usd": 1595,  # estimado: serie SSA3000X $1,395-$2,595 siglentna.com
        "freq_range": "9 kHz - 2.1 GHz",
        "danl_dbm": -161,
        "amplitude_accuracy_db": 0.7,
        "rbw_min_hz": 1,
        "interface": "LAN + USB (SCPI/VISA) - headless via Ethernet",
        "has_screen": True,
        "zero_span": True,
        "headless": True,
        "calibration": "INCLUIDO. Cert. de Calibracion trazable a SI/NIST/NIM/PTB via CIPM MRA. ISO17025 acreditado disponible como opcion adicional al comprar.",
        "notes": "Bench. DANL -161dBm, 0.7dB. Mejor specs que Plus. ~$1,595 est.",
    },
    {
        "name": "Rigol DSA815",
        "price_usd": 1319,  # verificado rigolna.com (IN STOCK)
        "freq_range": "9 kHz - 1.5 GHz",
        "danl_dbm": -155,
        "amplitude_accuracy_db": 1.5,
        "rbw_min_hz": 10,
        "interface": "USB + LAN + GPIB (SCPI) - headless via LAN",
        "has_screen": True,
        "zero_span": True,
        "headless": True,
        "calibration": "INCLUIDO. Factory Cal Certificate trazable a NIST/NIM/NPL/PTB, basado en ISO9001 e ISO/IEC17025. Recalibracion via Transcat o Navair (~$150-300/año).",
        "notes": "Bench. $1,319 verificado rigolna.com. DANL -155dBm. RBW min 10Hz.",
    },
    {
        "name": "Rigol DSA832E",
        "price_usd": 1999,  # verificado rigolna.com (IN STOCK)
        "freq_range": "9 kHz - 3.2 GHz",
        "danl_dbm": -158,
        "amplitude_accuracy_db": 1.5,
        "rbw_min_hz": 10,
        "interface": "USB + LAN + GPIB (SCPI) - headless via LAN",
        "has_screen": True,
        "zero_span": True,
        "headless": True,
        "calibration": "INCLUIDO. Factory Cal Certificate trazable a NIST/NIM/NPL/PTB, basado en ISO9001 e ISO/IEC17025. Recalibracion via Transcat o Navair (~$150-300/año).",
        "notes": "Bench. Economy 3.2GHz. $1,999 verificado rigolna.com.",
    },
    # ---- LOW-COST REFERENCIA ----
    {
        "name": "tinySA Ultra",
        "price_usd": 120,
        "freq_range": "100 kHz - 800 MHz (Ultra mode 6 GHz)",
        "danl_dbm": -95,
        "amplitude_accuracy_db": 2.0,
        "rbw_min_hz": 200,
        "interface": "USB serial CDC (protocolo custom)",
        "has_screen": True,
        "zero_span": False,
        "headless": False,
        "calibration": "NO INCLUIDO. Sin certificado de calibracion. No apto para trazabilidad metrológica.",
        "notes": "Low-cost referencia. Precision insuficiente para produccion.",
    },
]

# ============================================================
# CRITERIOS DE DECISION (pesos y tipo)
# Precios reales mercado nuevo: $1,295 - $2,850 rango tipico
# ============================================================

CRITERIA = {
    "precio":          {"weight": 0.25, "type": "min", "ideal": 1000, "nadir": 3000},
    "precision_db":    {"weight": 0.35, "type": "min", "ideal": 0.25, "nadir": 5.0},
    "danl_dbm":        {"weight": 0.15, "type": "min", "ideal": -161, "nadir": -70, "note": "mas negativo = mejor"},
    "rbw_min_hz":      {"weight": 0.10, "type": "min", "ideal": 1,   "nadir": 5000},
    "integracion_py":  {"weight": 0.10, "type": "max", "ideal": 10,  "nadir": 1},
    "zero_span":       {"weight": 0.03, "type": "max", "ideal": 1,   "nadir": 0},
    "freq_range_ghz":  {"weight": 0.02, "type": "max", "ideal": 12.4, "nadir": 0.35},
}

# Puntaje de integracion Python (1-10)
INTEGRATION_SCORE = {
    "Signal Hound SA44B": 9,           # SDK Python oficial, excelente documentacion
    "Signal Hound SA124B": 9,          # mismo SDK que SA44B
    "Siglent SSA3015X Plus": 9,        # SCPI socket, pyvisa, estandar
    "Siglent SSA3021X (no Plus)": 9,   # SCPI socket, pyvisa, estandar
    "Rigol DSA815": 8,                 # SCPI/VISA, pyvisa, bien soportado
    "Rigol DSA832E": 8,                # SCPI/VISA, pyvisa, bien soportado
    "tinySA Ultra": 5,                 # Serial CDC, libreria open source limitada
}

def topsis_analysis(alternatives: list, criteria: dict) -> list:
    """
    TOPSIS (Technique for Order of Preference by Similarity to Ideal Solution)
    Ranking multicriterio simplificado.
    """
    alts = []
    for a in alternatives:
        integration = INTEGRATION_SCORE.get(a["name"], 5)
        # Parsear frecuencia máxima del rango (puede ser "100 kHz - 800/900 MHz")
        try:
            right = a["freq_range"].split(" - ")[1] if " - " in a["freq_range"] else "1 GHz"
            parts = right.split()
            raw = parts[0].split("/")[0]  # tomar el primer valor si hay "800/900"
            unit = parts[1] if len(parts) > 1 else "GHz"
            freq_max = float(raw)
            freq_max_ghz = freq_max if "GHz" in unit else freq_max / 1000
        except (IndexError, ValueError):
            freq_max_ghz = 1.0

        alts.append({
            "name": a["name"],
            "precio": a["price_usd"],
            "precision_db": a["amplitude_accuracy_db"],
            "danl_dbm": abs(a["danl_dbm"]),  # más negativo = más abs = mejor
            "rbw_min_hz": a["rbw_min_hz"],
            "integracion_py": integration,
            "zero_span": 1 if a["zero_span"] else 0,
            "freq_range_ghz": freq_max_ghz,
        })

    # Normalizar: ideal = mejor valor, nadir = peor
    scores = {}
    for a in alts:
        d_ideal = 0.0
        d_nadir = 0.0
        for crit, params in criteria.items():
            w = params["weight"]
            ideal = params["ideal"]
            nadir = params["nadir"]
            val = a[crit]

            # Para danl_dbm trabajamos con valor absoluto (mayor = mejor)
            if crit == "danl_dbm":
                ideal = abs(ideal)
                nadir = abs(nadir)

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

        import math
        d_i = math.sqrt(d_ideal)
        d_n = math.sqrt(d_nadir)
        score = d_n / (d_i + d_n) if (d_i + d_n) > 0 else 0
        scores[a["name"]] = round(score, 4)

    ranked = sorted(alts, key=lambda x: scores[x["name"]], reverse=True)
    for i, a in enumerate(ranked):
        a["topsis_score"] = scores[a["name"]]
        a["rank"] = i + 1

    return ranked


def check_minimum_requirements(alt: dict) -> dict:
    """Verifica si el equipo cumple los requisitos mínimos para producción."""
    ok = True
    fails = []
    warns = []

    if alt["amplitude_accuracy_db"] > 1.0:
        ok = False
        fails.append(f"Precision {alt['amplitude_accuracy_db']} dB > 1.0 dB (minimo produccion)")

    if alt["danl_dbm"] > -80:
        ok = False
        fails.append(f"DANL {alt['danl_dbm']} dBm insuficiente (señal -20 dBm, margen solo {alt['danl_dbm'] - (-20)} dB)")

    if alt["price_usd"] > 1000:
        warns.append(f"Precio ${alt['price_usd']} supera objetivo <$1,000 (equipo nuevo)")

    return {"apto": ok, "fails": fails, "warns": warns}


def research_spectrum_analyzers() -> str:
    """Investigación con Gemini sobre analizadores de espectro para mesa de pruebas."""
    
    query = """
    Busca y analiza analizadores de espectro de bajo costo disponibles en el mercado en 2025-2026
    adecuados para una mesa de pruebas de producción con las siguientes características OBLIGATORIAS:

    REQUISITOS MÍNIMOS:
    - Rango de frecuencia: debe cubrir VHF (30 MHz - 300 MHz) y preferiblemente hasta 1 GHz
    - Precisión de amplitud: ±1 dB o mejor (para medición de potencia de salida de amplificadores)
    - DANL: < -90 dBm/Hz (señales de interés: -20 a +10 dBm)
    - Control por software: debe tener API, SCPI, serial, o DLL para Python (NO necesita pantalla)
    - Precio: preferiblemente < $1,200 USD NUEVO (compra de múltiples unidades, NO mercado secundario)
    - IMPORTANTE: equipos NUEVOS únicamente (no de mercado secundario/usado)
    
    SEÑALES A MEDIR:
    - Potencia de salida de repetidores/amplificadores de red leaky feeder
    - Rango: -20 dBm a +10 dBm
    - Frecuencias VHF: 138-174 MHz principalmente (puede llegar a 450 MHz UHF)
    
    CASOS DE USO:
    - Suite de pruebas automatizadas en Python
    - gain_check: verificar ganancia de amplificador (set_center_freq, set_span, get_level_from_marker)
    - agc_check: verificar activación de AGC comparando potencia en 3 lecturas consecutivas
    - Se comprarán múltiples unidades, por lo que precio unitario y disponibilidad son clave
    
    Evalúa y compara con precio actual NUEVO (USD):
    1. Rigol DSA815 (NUEVO - precio actual 2025/2026)
    2. Rigol DSA832 (NUEVO - precio actual 2025/2026)
    3. Rohde & Schwarz FPC1000 o FPC1500 (NUEVO)
    4. Siglent SSA3015X Plus (NUEVO)
    5. Siglent SSA3021X Plus (NUEVO)
    6. BK Precision 2658 o similar (NUEVO)
    7. Owon HSA1016 o HSA1036 (NUEVO)
    8. GW Instek GSP-818 o GSP-830 (NUEVO)
    9. Anritsu MS2711E (NUEVO si disponible)
    10. Keysight N9320B (NUEVO - precio lista)
    11. Cualquier otra opción NUEVA < $1,000 USD con esas características

    NOTA: NO incluir equipos usados, reacondicionados, o de mercado secundario.
    Indicar si el modelo tiene descuentos por volumen o programas de compra múltiple.

    Para cada uno indica:
    - Precio actual en USD (nuevo y/o usado si aplica)
    - Rango exacto de frecuencias
    - DANL especificada
    - Precisión total de amplitud
    - RBW mínimo
    - Protocolo de control (SCPI/VISA/serial/DLL)
    - Soporte de pyvisa o Python
    - Disponibilidad de zero span
    - ¿Apto para producción automatizada sin operador?

    Indica cuáles son las mejores relaciones calidad/precio para este caso de uso específico.
    """

    print("\n" + "=" * 70)
    print("   🔍 INVESTIGACIÓN CON GEMINI - Analizadores de Espectro 2026")
    print("=" * 70 + "\n")
    print("Consultando Gemini API... (puede tomar unos segundos)\n")

    result = search_with_gemini(query)
    return result


def main():
    print("\n" + "=" * 70)
    print("   📡 ANÁLISIS DE DECISIÓN - ANALIZADOR DE ESPECTRO")
    print("   Mesa de Pruebas Automatizada (sw-testbench)")
    print("=" * 70)
    print(f"\n📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("🎯 Objetivo: Seleccionar mejor analizador NUEVO para compra de múltiples unidades")
    print("\nRequisitos mínimos:")
    print("  • Rango: VHF 30-300 MHz (ideal hasta 1+ GHz)")
    print("  • Precisión: ±1 dB máximo")
    print("  • DANL: < -90 dBm")
    print("  • Control Python: SCPI / DLL / serial API")
    print("  • Precio objetivo: < $1,200 USD (NUEVO, compra múltiple)")

    # --------------------------------------------------------
    # 1. INVESTIGACIÓN CON GEMINI
    # --------------------------------------------------------
    research_text = research_spectrum_analyzers()
    print("\n📋 RESULTADOS DE INVESTIGACIÓN GEMINI:\n")
    print(research_text)

    # --------------------------------------------------------
    # 2. ANÁLISIS TOPSIS CON ALTERNATIVAS CONOCIDAS
    # --------------------------------------------------------
    print("\n" + "=" * 70)
    print("   📊 ANÁLISIS TOPSIS — ALTERNATIVAS CONOCIDAS")
    print("=" * 70)

    ranked = topsis_analysis(ALTERNATIVES, CRITERIA)

    print(f"\n{'#':<3} {'Equipo':<35} {'Precio':>7} {'Prec.':>6} {'DANL':>6} {'Score':>7} {'Apto':<6} {'Cal.':<8}")
    print("-" * 92)

    for a in ranked:
        alt_data = next(x for x in ALTERNATIVES if x["name"] == a["name"])
        req = check_minimum_requirements(alt_data)
        apto = "✅" if req["apto"] else "❌"
        precio_flag = "⚠" if alt_data["price_usd"] > 800 else " "
        cal = alt_data.get("calibration", "")
        cal_flag = "✅incl" if cal.startswith("INCLUIDO") else ("💲extra" if cal.startswith("OPCIONAL") else "❌no")
        print(
            f"{a['rank']:<3} {a['name']:<35} "
            f"{precio_flag}${alt_data['price_usd']:>6} "
            f"{alt_data['amplitude_accuracy_db']:>5.2f}dB "
            f"{alt_data['danl_dbm']:>5}dB "
            f"{a['topsis_score']:>7.4f} {apto:<6} {cal_flag}"
        )

    # --------------------------------------------------------
    # 3. REQUISITOS — detalle
    # --------------------------------------------------------
    print("\n" + "=" * 70)
    print("   ✅ VERIFICACIÓN DE REQUISITOS MÍNIMOS")
    print("=" * 70)
    aptos = []
    for alt in ALTERNATIVES:
        req = check_minimum_requirements(alt)
        status = "APTO" if req["apto"] else "NO APTO"
        price_ok = alt["price_usd"] <= 800
        print(f"\n{'✅' if req['apto'] else '❌'} {alt['name']} — {status} | ${alt['price_usd']}")
        if req["fails"]:
            for f in req["fails"]:
                print(f"     ❌ {f}")
        if req["warns"]:
            for w in req["warns"]:
                print(f"     ⚠  {w}")
        cal = alt.get("calibration", "No especificado")
        cal_prefix = "✅" if cal.startswith("INCLUIDO") else ("💲" if cal.startswith("OPCIONAL") else "❌")
        print(f"     {cal_prefix} Calibracion: {cal}")
        if req["apto"]:
            aptos.append(alt)

    # --------------------------------------------------------
    # 4. RECOMENDACIÓN FINAL
    # --------------------------------------------------------
    print("\n" + "=" * 70)
    print("   🏆 RECOMENDACIÓN FINAL")
    print("=" * 70)

    ranked_aptos = [r for r in ranked if any(a["name"] == r["name"] for a in aptos)]

    if ranked_aptos:
        best = ranked_aptos[0]
        best_data = next(x for x in ALTERNATIVES if x["name"] == best["name"])
        def _cal_costo(alt_data: dict) -> str:
            cal = alt_data.get("calibration", "")
            if cal.startswith("INCLUIDO"):
                return "INCLUIDO en precio"
            elif cal.startswith("OPCIONAL"):
                return "~$450 adicional (seleccionar al comprar)"
            return "No disponible"

        def _precio_total(alt_data: dict) -> int:
            cal = alt_data.get("calibration", "")
            extra = 450 if cal.startswith("OPCIONAL") else 0
            return alt_data["price_usd"] + extra

        saving = 1360 - _precio_total(best_data)
        print(f"\n🥇 Mejor opción: {best_data['name']}")
        print(f"   Precio equipo:       ${best_data['price_usd']:,} USD")
        print(f"   Certificado cal.:    {_cal_costo(best_data)}")
        print(f"   ─────────────────────────────────────────")
        print(f"   PRECIO TOTAL:        ${_precio_total(best_data):,} USD  (ahorro ${saving:,} vs Siglent $1,360)")
        print(f"   TOPSIS score:        {best['topsis_score']:.4f}")
        print(f"   Precisión:           ±{best_data['amplitude_accuracy_db']} dB")
        print(f"   DANL:                {best_data['danl_dbm']} dBm")
        print(f"   Rango:               {best_data['freq_range']}")
        print(f"   Interfaz:            {best_data['interface']}")
        print(f"   Notas:               {best_data['notes']}")

        if len(ranked_aptos) > 1:
            second = ranked_aptos[1]
            second_data = next(x for x in ALTERNATIVES if x["name"] == second["name"])
            saving2 = 1360 - _precio_total(second_data)
            print(f"\n🥈 Segunda opción: {second_data['name']}")
            print(f"   Precio equipo:       ${second_data['price_usd']:,} USD")
            print(f"   Certificado cal.:    {_cal_costo(second_data)}")
            print(f"   PRECIO TOTAL:        ${_precio_total(second_data):,} USD  (ahorro ${saving2:,} vs Siglent $1,360)")
    else:
        print("\n⚠ Ningún equipo conocido cumple todos los requisitos dentro del presupuesto.")
        print("Ver resultados de investigación Gemini para candidatos adicionales.")

    # --------------------------------------------------------
    # 5. GUARDAR RESULTADOS
    # --------------------------------------------------------
    results = {
        "fecha": datetime.now().isoformat(),
        "objetivo": "Seleccion analizador espectro mesa de pruebas sw-testbench",
        "precio_referencia_usd": 1360,
        "precio_objetivo_usd": 800,
        "gemini_research": research_text,
        "topsis_ranking": ranked,
        "aptos": [a["name"] for a in aptos],
        "recomendacion": ranked_aptos[0]["name"] if ranked_aptos else "Ver investigacion Gemini",
    }

    out_dir = Path(__file__).parent.parent.parent / "results" / "spectrum_analyzer_selection"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\n💾 Resultados guardados en: {out_file}")
    print("\n✅ Análisis completado.")


if __name__ == "__main__":
    main()
