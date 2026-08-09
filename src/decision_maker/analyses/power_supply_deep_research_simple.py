"""
Power Supply Diagnostic Module - Gemini Deep Research Analysis (Simplified)
Investigación usando Google Gemini 2.0 Flash
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import google.generativeai as genai
from dotenv import load_dotenv

# =============================================================================
# CONFIGURACIÓN
# =============================================================================

env_file = Path(__file__).parent / ".env.gemini"
load_dotenv(env_file)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

if not GEMINI_API_KEY:
    raise ValueError("❌ GEMINI_API_KEY no configurada")

genai.configure(api_key=GEMINI_API_KEY)

# =============================================================================
# CONTEXT
# =============================================================================

PROJECT_CONTEXT = """
PROYECTO: Módulo Power Supply - sw-diagnosticoremoto
- Monitoreo remoto de fuentes de poder en túneles subterráneos
- Control de 2 salidas de potencia + medición de voltaje/corriente
- Integración con baterías existentes
- Protocolos: Leaky Feeder + evaluación MQTT/Modbus TCP
"""

# =============================================================================
# QUERIES
# =============================================================================

QUERIES = {
    "Competencia": """
    ¿Cuáles son los 3 mejores softwares open-source o comerciales para:
    - Monitoreo en tiempo real de fuentes de poder
    - Control remoto de encendido/apagado
    - Histórico de eventos y tendencias
    - Dashboard industrial intuitivo

    Para cada uno: nombre, ventajas, protocolo (MQTT/REST/Modbus), costo aproximado.
    """,

    "Vistas_Recomendadas": """
    ¿Qué 5 vistas/dashboards son esenciales para software de diagnóstico de fuentes de poder?
    Detalla: nombre, componentes clave, métricas a mostrar, prioridad (MVP o Fase 2).
    """,

    "Stack_Tecnologia": """
    Para MVP en 4-5 semanas con team de 5 personas:
    - Frontend: ¿React.js vs Vue.js vs Svelte?
    - Backend: Node.js vs Python vs Go?
    - Database: InfluxDB vs Prometheus vs TimescaleDB?
    - Dashboards: Grafana vs custom?

    Recomendación final con justificación.
    """,

    "Arquitectura": """
    Propón arquitectura técnica para:
    - ADC datos → microcontroller → MQTT → Backend → Frontend
    - Escalable a 10+ fuentes
    - Histórico 30 días mínimo
    - Alertas en tiempo real

    Incluye: componentes, flujos de datos, APIs.
    """
}

# =============================================================================
# MAIN
# =============================================================================

def gemini_research(query_name: str, query: str) -> str:
    """Realiza research con Gemini"""
    try:
        print(f"   📍 {query_name}...", end=" ", flush=True)
        model = genai.GenerativeModel(GEMINI_MODEL)
        response = model.generate_content(f"{PROJECT_CONTEXT}\n\n{query}")
        print("✅")
        return response.text
    except Exception as e:
        print(f"❌ Error: {e}")
        return f"Error: {str(e)}"

def main():
    print("\n" + "="*80)
    print("🚀 DEEP RESEARCH: POWER SUPPLY MODULE")
    print("="*80 + "\n")

    results = {
        "fecha": datetime.now().isoformat(),
        "proyecto": "Power Supply - sw-diagnosticoremoto",
        "investigaciones": {}
    }

    print("⏳ Ejecutando investigaciones con Gemini...\n")

    for nombre, query in QUERIES.items():
        resultado = gemini_research(nombre, query)
        results["investigaciones"][nombre] = resultado

    # Guardar
    output_file = Path(__file__).parent / "power_supply_research_results.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print("\n✅ Investigación completada")
    print(f"📁 Guardado en: {output_file}")

    # Mostrar resumen
    print("\n" + "="*80)
    print("📄 RESUMEN")
    print("="*80 + "\n")

    for nombre, contenido in results["investigaciones"].items():
        print(f"\n{'─'*80}")
        print(f"📌 {nombre}")
        print(f"{'─'*80}\n")
        # Primeros 600 caracteres
        preview = contenido[:600] + "\n\n[... ver archivo completo ...]" if len(contenido) > 600 else contenido
        print(preview)

if __name__ == "__main__":
    main()
