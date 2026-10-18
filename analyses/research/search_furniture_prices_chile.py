#!/usr/bin/env python3
"""
Búsqueda de precios de muebles en Chile usando Gemini API
Modelo: gemini-2.0-flash-exp (gratuito)
"""

import os
import sys
from datetime import datetime

from google import genai


def search_furniture_prices():
    """Busca precios reales de muebles en Chile con Gemini"""

    # Configurar API
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ Error: GEMINI_API_KEY no está configurada")
        sys.exit(1)

    client = genai.Client(api_key=api_key)

    # Usar modelo gratuito: gemini-2.0-flash-exp
    model_id = 'gemini-2.0-flash-exp'

    print("="*70)
    print("   🔍 BÚSQUEDA PRECIOS MUEBLES CHILE - GEMINI")
    print("="*70)
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"🤖 Modelo: {model_id} (gratuito)")
    print("="*70)
    print()

    # Especificaciones del mueble
    specs = """
    Mueble tipo rack/mesón con estas características:
    - Dimensiones: 60cm alto × 60cm ancho × 1.8m (180cm) largo
    - Uso: Mesón para bebé + almacenamiento debajo
    - Material: Melamina, MDF o similar
    - Similar a: Rack TV, mueble bajo, estantería horizontal
    - Con espacio inferior para cajas/almacenamiento
    """

    print("📋 ESPECIFICACIONES:")
    print(specs)
    print("="*70)
    print()

    # Preguntas a Gemini
    queries = [
        {
            "title": "Precio materiales DIY Chile 2024",
            "prompt": """
            Necesito estimar el costo de materiales en Chile (CLP) para construir un mueble tipo rack de:
            - 60cm alto × 60cm ancho × 1.8m largo
            - Material: MDF o melamina
            - Incluye: tableros, tornillos, bisagras, pegamento, lija

            Busca precios aproximados en tiendas chilenas como Sodimac, Easy, Homecenter en diciembre 2024.
            Dame un rango de precio total en CLP considerando que soy principiante.
            """
        },
        {
            "title": "Precio rack/mueble tienda Chile 2024",
            "prompt": """
            ¿Cuánto cuesta un rack/mueble bajo para TV o almacenamiento en Chile (CLP) en diciembre 2024?
            - Medidas aproximadas: 60cm alto × 60-80cm ancho × 180cm largo
            - Tiendas: Sodimac, Easy, Falabella, Ripley, Homy
            - Rango de precios bajo, medio y alto

            Dame precios específicos con nombres de modelos si es posible.
            """
        },
        {
            "title": "Kit DIY para armar Chile 2024",
            "prompt": """
            ¿Hay kits de muebles para armar tipo IKEA en Chile en diciembre 2024?
            - Tamaño similar a rack TV: ~60cm alto × 180cm largo
            - Tiendas que vendan kits: Sodimac, Easy, IKEA Chile (si existe)
            - Precio aproximado en CLP

            Menciona marcas/modelos disponibles en Chile.
            """
        },
        {
            "title": "Costo carpintero Chile 2024",
            "prompt": """
            ¿Cuánto cobra un carpintero en Chile (CLP) por hacer un mueble a medida en diciembre 2024?
            - Mueble: 60cm alto × 60cm ancho × 180cm largo
            - Material: MDF/melamina
            - Ubicación: Santiago, Chile
            - Incluye: materiales + mano de obra

            Dame un rango de precios (bajo, medio, alto) considerando diferentes niveles de carpinteros.
            """
        },
        {
            "title": "Dificultad DIY principiante",
            "prompt": """
            Para una persona sin experiencia en carpintería en Chile:
            ¿Qué tan difícil es construir un rack/mueble de 60×60×180cm desde cero?
            - Herramientas necesarias
            - Nivel de dificultad (fácil, medio, difícil)
            - Tiempo estimado
            - Riesgos comunes
            - ¿Vale la pena para un principiante?

            Sé honesto sobre las dificultades reales.
            """
        }
    ]

    results = {}

    for i, query in enumerate(queries, 1):
        print(f"🔍 [{i}/{len(queries)}] {query['title']}")
        print("-"*70)

        try:
            # Hacer consulta a Gemini
            response = client.models.generate_content(
                model=model_id,
                contents=query['prompt']
            )

            # Guardar resultado
            result_text = response.text
            results[query['title']] = result_text

            # Mostrar resultado
            print(result_text)
            print()

        except Exception as e:
            print(f"❌ Error: {e}")
            results[query['title']] = f"Error: {e}"

        print("="*70)
        print()

    # Resumen final
    print()
    print("="*70)
    print("   📊 RESUMEN DE BÚSQUEDA")
    print("="*70)
    print()

    # Extraer precios aproximados
    print("💰 PRECIOS ESTIMADOS (CLP):")
    print("-"*70)
    print("📦 Materiales DIY:      Ver búsqueda arriba")
    print("🏪 Rack tienda:         Ver búsqueda arriba")
    print("🔧 Kit para armar:      Ver búsqueda arriba")
    print("👷 Carpintero a medida: Ver búsqueda arriba")
    print()

    print("="*70)
    print("✅ Búsqueda completada con Gemini Flash (gratuito)")
    print("="*70)

    return results

if __name__ == "__main__":
    results = search_furniture_prices()
