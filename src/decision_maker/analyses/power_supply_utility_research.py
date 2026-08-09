#!/usr/bin/env python3
"""
Power Supply Utility Research - Gemini Deep Research
Enfoque: Utilidad para operaciones minería, no arquitectura técnica

Queries enfocadas en:
1. Métricas críticas de poder en minería subterránea (ROI, uptime, safety)
2. Soluciones competencia desde punto de vista de utilidad operacional
3. Análisis costo-beneficio de monitoreo power supply
4. Datos críticos para leaky feeder + headend
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Agregar parent directory al path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import google.generativeai as genai
    from dotenv import load_dotenv
except ImportError:
    print("❌ Falta instalar: pip install google-generativeai python-dotenv")
    sys.exit(1)

# Cargar configuración
load_dotenv(".env.gemini")
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    print("❌ Error: GEMINI_API_KEY no configurada en .env.gemini")
    sys.exit(1)

genai.configure(api_key=API_KEY)

# Queries enfocadas en UTILIDAD
UTILITY_QUERIES = {
    "metricas_criticas_mineria": """
    CONTEXTO: Sistema de minería subterránea con amplificadores en leaky feeder alimentados
    por fuentes de poder en headend (cabecera de la red).

    PREGUNTA: ¿Cuáles son las MÉTRICAS MÁS CRÍTICAS de fuentes de poder que impactan
    directamente la operación minera? Enfócate en:

    1. UPTIME y DISPONIBILIDAD: ¿Qué datos predecirían fallos antes de ocurrir?
    2. SEGURIDAD: ¿Qué alertas evitan daños a equipamiento o personal?
    3. EFICIENCIA: ¿Qué métricas optimizan consumo energético y costos?
    4. DIAGNÓSTICO REMOTO: ¿Qué datos permiten resolver problemas sin ir al sitio?
    5. CUMPLIMIENTO: ¿Qué mediciones requieren regulaciones minería?

    Dame análisis detallado de ROI de cada métrica (costo de no tenerla vs beneficio de tenerla).
    """,

    "utilidad_competencia_soluciones": """
    CONTEXTO: Evaluando soluciones de monitoreo power supply para minería subterránea.

    PREGUNTA: Comparar UTILIDAD PRÁCTICA de estas soluciones:

    1. GRAFANA + Prometheus (open source)
    2. Schneider Electric PowerLogic (enterprise)
    3. Victron Energy Venus OS (especializado baterías)
    4. ABB MicroSCADA (industrial)
    5. Solución CUSTOM (desarrollo propio)

    Para CADA UNA analizar:
    - ¿Qué problemas operacionales REALES resuelve?
    - ¿Costo total de propiedad (TCO) realista?
    - ¿Tiempo para tener alerts remoto funcionando?
    - ¿Capacidad diagnóstico remoto (sin ir al sitio)?
    - ¿Casos reales en minería subterránea?
    - ¿Qué NO hace que sí necesitaríamos?

    Usa ejemplos reales si existen.
    """,

    "datos_criticos_leaky_feeder_headend": """
    CONTEXTO: Red leaky feeder con amplificadores distribuidos alimentados desde fuentes
    en headend. Necesitamos entender qué datos de power supply son ESENCIALES para
    mantener la red operativa.

    PREGUNTA: Para un sistema leaky feeder + headend, ¿cuál es el SET MÍNIMO de datos
    de fuente de poder que permitiría:

    1. Detectar caídas de amplificador en tiempo real
    2. Diagnosticar "no hay señal" sin ir al sitio
    3. Planificar mantenimiento preventivo
    4. Cumplir SLAs de operación minería
    5. Optimizar eficiencia energética

    Estructura respuesta como:
    - Datos CRÍTICOS (sin estos no funciona diagnóstico)
    - Datos IMPORTANTES (mejoran mucho la operación)
    - Datos OPCIONALES (nice to have)

    Incluye cómo correlacionar datos power con eventos leaky feeder.
    """,

    "analisis_costo_beneficio_monitoreo": """
    CONTEXTO: Sistema minería subterránea, costo promedio de downtime = $50k-200k por hora,
    costo reparación sitio remoto = $5k-15k (personal, transporte).

    PREGUNTA: Análisis costo-beneficio de implementar monitoreo predictivo de power supply:

    1. ¿Cuántos problemas de downtime son causados por power supply? (% realista)
    2. ¿Cuál es el ROI de detectar fallo 24h antes vs 1h después?
    3. ¿Costo de implementar monitoreo remoto vs costo downtime anual?
    4. ¿Payback period realista para solución?
    5. ¿Qué KPIs deberían trackear para demostrar valor?

    Dame números reales si existen, o estimaciones conservadoras.
    """,

    "mejor_solucion_mineria_subterranea": """
    CONTEXTO: Minería subterránea, infraestructura existente (serial/TCP → MongoDB →
    Backend/Frontend similar a sw-diagnosticoremoto), presupuesto limitado, team pequeño.

    PREGUNTA: ¿Cuál es la MEJOR SOLUCIÓN para monitoreo power supply en este contexto?

    Considerar:
    1. Extensión sistema existente vs nueva solución
    2. Costo implementación realista (horas dev)
    3. Capacidades diagnóstico remoto
    4. Escalabilidad a múltiples headends
    5. Mantenimiento y soporte a largo plazo
    6. Uptime SLA alcanzable (99%, 99.5%, 99.9%?)

    Proponer arquitectura ESPECÍFICA para minería subterránea, no genérica.
    """
}

def execute_deep_research():
    """Ejecutar investigación Gemini sobre utilidad power supply"""

    print("=" * 80)
    print("🚀 DEEP RESEARCH: POWER SUPPLY UTILITY ANALYSIS")
    print("=" * 80)
    print(f"Fecha: {datetime.now().isoformat()}")
    print("Enfoque: UTILIDAD y VALOR DE NEGOCIO para minería subterránea")
    print()

    results = {}
    model = genai.GenerativeModel("gemini-2.0-flash")

    for idx, (query_name, query_prompt) in enumerate(UTILITY_QUERIES.items(), 1):
        print(f"📊 [{idx}/{len(UTILITY_QUERIES)}] {query_name.replace('_', ' ').title()}...")

        try:
            response = model.generate_content(query_prompt)

            results[query_name] = {
                "query": query_prompt[:200] + "...",
                "response": response.text,
                "timestamp": datetime.now().isoformat()
            }

            print(f"   ✅ Completado ({len(response.text)} caracteres)")

        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            results[query_name] = {
                "query": query_prompt[:200] + "...",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    # Guardar resultados
    output_path = Path(__file__).parent / "power_supply_utility_results.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print()
    print("=" * 80)
    print("✅ Investigación completada")
    print(f"📁 Guardado en: {output_path}")
    print("=" * 80)

    return results

if __name__ == "__main__":
    results = execute_deep_research()

    # Mostrar resumen
    print("\n📋 RESUMEN DE INVESTIGACIONES:\n")
    for query_name, result in results.items():
        status = "✅" if "response" in result else "❌"
        print(f"{status} {query_name.replace('_', ' ').title()}")
        if "error" not in result:
            print(f"   └─ {len(result['response'])} caracteres de respuesta\n")
