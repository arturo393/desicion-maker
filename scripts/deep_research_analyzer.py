#!/usr/bin/env -S uv run --quiet --script
# /// script
# dependencies = [
#   "google-genai",
# ]
# ///
"""
Decision Maker - Análisis con Deep Research Pro
================================================

Integra Google's Deep Research Pro para análisis profundo de decisiones.
Usa el SDK correcto: google-genai (no google-generativeai)

Modelos soportados:
- gemini-2.5-pro (rápido, eficiente)
- deep-research-pro-preview-12-2025 (investigación profunda, 3-5 min)
"""

import time
import json
import sys
from typing import Any

# Fix para Windows console encoding
if sys.platform == "win32":
    import io
    import codecs
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from google import genai
import os

# Configurar cliente con API key desde variable de entorno
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY no encontrado. Configura la variable de entorno.")
client = genai.Client(api_key=api_key)

print("=" * 90)
print("[AI] DECISION MAKER - Deep Research Pro")
print("=" * 90)
print()


def analyze_with_deep_research(question: str, model: str = "deep-research-pro-preview-12-2025", max_wait: int = 600) -> str:
    """
    Analiza una pregunta usando Deep Research Pro.
    
    Args:
        question: Pregunta a analizar
        model: Modelo a usar (default: deep-research-pro-preview-12-2025)
        max_wait: Tiempo máximo de espera en segundos (default: 600 = 10 min)
    
    Returns:
        Respuesta del modelo
    """
    print(f"[INFO] Iniciando investigación con {model}...")
    print(f"[WAIT] Pregunta: {question[:80]}...\n")
    
    try:
        # Crear interacción (ejecución asíncrona)
        interaction = client.interactions.create(
            agent=model,
            input=question,
            background=True
        )
        
        print(f"[OK] ID: {interaction.id}")
        print(f"[WAIT] Esperando resultados (puede tomar 3-5 minutos)...\n")
        
        # Polling para obtener resultados
        poll_interval = 15  # cada 15 segundos
        elapsed = 0
        
        while elapsed < max_wait:
            time.sleep(poll_interval)
            elapsed += poll_interval
            
            # Obtener estado actual
            status = client.interactions.get(id=interaction.id)
            print(f"⏱️  {elapsed}s - Estado: {status.status}")
            
            if status.status == "completed":
                # Extraer respuesta
                if status.outputs and len(status.outputs) > 0:
                    response_text = status.outputs[0].text
                else:
                    response_text = "No response content"
                
                print("\n[OK] Investigacion completada!\n")
                return response_text
            
            elif status.status == "failed":
                error_msg = getattr(status, 'error', 'Unknown error')
                print(f"\n[ERROR] Fallo: {error_msg}\n")
                return f"Error: {error_msg}"
        
        return f"[TIMEOUT] Timeout despues de {max_wait}s"
    
    except Exception as e:
        return f"[ERROR] Excepcion: {e}"


def analyze_decision(decision_name: str, options: dict, criteria: dict) -> None:
    """
    Analiza una decisión usando Deep Research Pro.
    
    Args:
        decision_name: Nombre de la decisión (ej: "Comprar Computadora")
        options: Dict de {nombre_opcion: descripcion}
        criteria: Dict de {nombre_criterio: importancia}
    """
    
    # Construir prompt de análisis
    prompt = f"""
ANÁLISIS DE DECISIÓN: {decision_name}

OPCIONES A CONSIDERAR:
{chr(10).join(f"- {name}: {desc}" for name, desc in options.items())}

CRITERIOS IMPORTANTES:
{chr(10).join(f"- {crit}: {imp}/10" for crit, imp in criteria.items())}

POR FAVOR ANALIZA:

1. MATRIZ DE DECISIÓN
   - Para cada opción vs cada criterio
   - Puntuación 0-10
   - Justificación breve

2. ANÁLISIS COMPARATIVO
   - Fortalezas de cada opción
   - Debilidades críticas
   - Trade-offs principales

3. EVALUACIÓN DE RIESGO
   - Riesgos específicos por opción
   - Probabilidad de arrepentimiento
   - Mitigación recomendada

4. RECOMENDACIÓN FINAL
   - Opción preferida con probabilidad (ej: 75%)
   - Condiciones para cambiar de decisión
   - Próximos pasos de validación

FORMATO: Estructura clara con secciones. Usa datos y lógica, no especulación.
"""

    # Ejecutar análisis
    result = analyze_with_deep_research(prompt)
    
    # Mostrar resultado
    print("=" * 90)
    print(f"[RESULT] {decision_name}")
    print("=" * 90)
    print()
    print(result)
    print()
    print("=" * 90)


# ============================================================================
# EJEMPLOS DE USO
# ============================================================================

if __name__ == "__main__":
    # Ejemplo 1: Análisis de Computadora (del framework decision-maker)
    print("\n" + "=" * 90)
    print("EJEMPLO 1: Que Computadora Comprar?")
    print("=" * 90)
    
    analyze_decision(
        decision_name="Compra de Computadora Portatil",
        options={
            "MacBook Air M2": "Laptop portatil con chip M2, 8GB RAM, 256GB SSD",
            "Lenovo ThinkPad X1": "Laptop profesional 14\", Intel i7, 16GB RAM",
            "Dell XPS 13": "Laptop de diseño, Intel/AMD, pantalla OLED",
            "MacBook Pro 16\"": "Laptop profesional, M3 Pro, 18GB RAM, 512GB"
        },
        criteria={
            "Portabilidad": 8,
            "Potencia Computacional": 7,
            "Precio": 6,
            "Durabilidad": 8,
            "Ecosistema Software": 7,
            "Calidad de Pantalla": 6
        }
    )
    
    # Ejemplo 2: Análisis de Trabajo vs Freelance (del proyecto minería)
    print("\n" + "=" * 90)
    print("EJEMPLO 2: Trabajo vs Emprendimiento?")
    print("=" * 90)
    
    analyze_decision(
        decision_name="Carrera Profesional 2026",
        options={
            "Trabajo Full-Time Chile": "Posicion senior en empresa mineria local",
            "Freelance Internacional": "Proyectos remotos desde Chile",
            "Startup Propia": "Fundar empresa tech/mineria"
        },
        criteria={
            "Ingreso Mensual": 9,
            "Flexibilidad": 7,
            "Crecimiento Profesional": 8,
            "Estabilidad": 7,
            "Impacto Social": 6,
            "Estres": 5
        }
    )
    
    print("\n[DONE] Analisis completado")
    print("=" * 90)
