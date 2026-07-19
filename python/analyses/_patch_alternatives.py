"""Script de parche: reemplaza bloques ALTERNATIVES, CRITERIA, INTEGRATION_SCORE con datos reales verificados."""
import re

path = r'C:\Users\artur\development\desicion-maker\python\analyses\spectrum_analyzer_selection.py'

with open(path, encoding='utf-8') as f:
    lines = f.readlines()

NEW_BLOCK = """\
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
"""

# Find start (line 93, index 92) and end (line before def topsis_analysis)
start_idx = 92  # ALTERNATIVES = [ is line 93

# Find the line with "def topsis_analysis"
end_idx = None
for i, line in enumerate(lines):
    if line.startswith("def topsis_analysis"):
        end_idx = i
        break

if end_idx is None:
    print("ERROR: could not find def topsis_analysis")
    exit(1)

print(f"Replacing lines {start_idx+1} to {end_idx} ({end_idx - start_idx} lines)")

new_lines = lines[:start_idx] + [NEW_BLOCK + "\n"] + lines[end_idx:]

with open(path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("OK: file updated successfully")
print(f"New total lines: {len(new_lines)}")
