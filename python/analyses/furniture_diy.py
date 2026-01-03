#!/usr/bin/env python3
"""
Título: Análisis de Decisión - DIY Furniture vs Compra
Propósito: Decidir entre construir muebles DIY, comprar nuevos o comprar usados
Fecha de Creación: 2025-12-01
Última Actualización: 2026-01-03
Versión: 1.2
Status: Activo

DESCRIPCIÓN:
🔨 Decisión sobre construcción de mesa/rack:
- Dimensiones: 60cm alto × 60cm ancho × 1.8m largo
- Uso: Para bebé (mesón) con almacenamiento debajo
- Similar a rack TV con cajones/cajas

CAMBIOS EN ESTA VERSIÓN (1.2):
- Movido a python/analyses/ directory
- Actualizado import paths
- Mantiene integración con Gemini API para búsqueda de precios

METODOLOGÍAS USADAS:
- Monte Carlo Simulation (10k iteraciones)
- TOPSIS (multi-criteria ranking)
- Pareto Analysis
- Gemini Research para precios de mercado chileno

PRÓXIMOS PASOS:
- [ ] Actualizar precios de mercado 2026
- [ ] Agregar análisis de tiempo de construcción
- [ ] Comparar con precios Amazon/MercadoLibre

NOTAS:
- Usa Gemini API para buscar precios reales en Chile
- Requiere GEMINI_API_KEY en .env
- Resultados guardados en results/furniture/
"""

import sys
from pathlib import Path
import os

sys.path.insert(0, str(Path(__file__).parent.parent / 'core'))

from deep_research_decision_agent import CareerOption, DecisionAnalysisEngine

# Primero: Configurar Gemini para búsqueda
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("⚠️  google-generativeai no instalado. Instalar: uv pip install google-generativeai")

def search_with_gemini(query: str) -> str:
    """Buscar información con Gemini"""
    if not GEMINI_AVAILABLE:
        return "Gemini no disponible - instalar google-generativeai"
    
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        return "GEMINI_API_KEY no configurada en environment"
    
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash-exp')  # Gratis
        
        response = model.generate_content(query)
        return response.text
    except Exception as e:
        return f"Error Gemini: {str(e)}"


def research_diy_furniture():
    """Investigar con Gemini sobre el mueble"""
    
    print("\n" + "="*70)
    print("   🔍 INVESTIGACIÓN CON GEMINI (gratis)")
    print("="*70 + "\n")
    
    queries = [
        {
            "name": "Precio materiales MDF/melamina Chile",
            "query": """
            ¿Cuánto cuesta en Chile (pesos chilenos) comprar materiales para construir 
            un mueble de 60cm alto × 60cm ancho × 1.8m largo?
            - Plancha MDF o melamina
            - Tornillos, bisagras
            - Ruedas o patas
            - Herramientas básicas (si no las tengo)
            
            Dame estimación realista de costos 2024.
            """
        },
        {
            "name": "Precio rack TV similar en Chile",
            "query": """
            ¿Cuánto cuesta en Chile (pesos chilenos) comprar un rack para TV o mueble similar de:
            - 60cm alto
            - 60cm ancho  
            - 1.8m largo
            - Con espacio para almacenar abajo
            
            Busca en tiendas chilenas: Falabella, Sodimac, Easy, Homecenter.
            Dame rango de precios 2024.
            """
        },
        {
            "name": "Dificultad construcción DIY",
            "query": """
            ¿Qué tan difícil es construir un mueble de melamina/MDF de 60cm×60cm×1.8m 
            para alguien con CERO experiencia en carpintería?
            
            - ¿Cuánto tiempo toma?
            - ¿Qué herramientas necesito?
            - ¿Hay tutoriales YouTube buenos?
            - Riesgos de que salga mal
            
            Sé realista sobre dificultad.
            """
        },
        {
            "name": "Servicio carpintero a medida",
            "query": """
            ¿Cuánto cobra un carpintero en Chile para hacer mueble a medida de:
            - 60cm alto × 60cm ancho × 1.8m largo
            - Melamina o MDF
            - Con espacio almacenamiento
            
            Rango de precios típico 2024 para mueble encargado.
            """
        }
    ]
    
    results = {}
    
    for q in queries:
        print(f"📡 Buscando: {q['name']}...")
        result = search_with_gemini(q['query'])
        results[q['name']] = result
        print(f"   ✅ Completado\n")
    
    return results


def create_furniture_options(gemini_results: dict):
    """Crear opciones basadas en investigación Gemini"""
    
    print("\n" + "="*70)
    print("   💡 ANÁLISIS DE RESULTADOS GEMINI")
    print("="*70 + "\n")
    
    for name, result in gemini_results.items():
        print(f"📌 {name}:")
        print("-" * 70)
        print(result[:500] + "..." if len(result) > 500 else result)
        print()
    
    # Opciones para evaluar
    # Adaptamos CareerOption para decisión de mueble
    
    print("\n" + "="*70)
    print("   🔨 OPCIONES A EVALUAR")
    print("="*70 + "\n")
    
    # Opción 1: DIY completo
    diy_full = CareerOption(
        name="DIY - Construir yo mismo",
        salary_expected=150_000,  # Costo materiales estimado
        probability_success=0.60,  # 60% sale bien (sin experiencia)
        timeline_months=1,  # 1 mes (fines de semana)
        tech_growth=7.0,  # Aprende carpintería
        income_stability=5.0,  # N/A (es gasto, no ingreso)
        work_life_balance=4.0,  # ❌ Consume tiempo fines semana
        prestige=7.0,  # Satisfacción de "lo hice yo"
        remote_flexibility=10.0,  # Total flexibilidad horario
        learning_opportunity=9.0,  # ✅ Aprendes mucho
        career_ceiling=6.0,  # Habilidad útil futuro
        unemployment_risk=0.40,  # 40% riesgo de quedar mal/no terminar
        burnout_risk=0.30,  # Puede ser frustrante
        market_risk=0.20,  # Puede costar más de lo planeado
        description="Comprar materiales y construir. Aprendes, personalizas, pero riesgo que salga mal."
    )
    
    # Opción 2: Comprar en tienda
    buy_store = CareerOption(
        name="Comprar - Rack en tienda (Sodimac/Falabella)",
        salary_expected=300_000,  # Precio estimado rack similar
        probability_success=0.95,  # 95% satisfacción (calidad conocida)
        timeline_months=0,  # Inmediato (compras y listo)
        tech_growth=2.0,  # No aprendes nada
        income_stability=8.0,  # Garantía tienda
        work_life_balance=9.0,  # ✅ Sin esfuerzo
        prestige=5.0,  # Normal, todos hacen esto
        remote_flexibility=5.0,  # Tienes que ir a tienda
        learning_opportunity=2.0,  # No aprendes
        career_ceiling=3.0,  # No desarrollas habilidad
        unemployment_risk=0.05,  # Muy bajo (garantía)
        burnout_risk=0.05,  # Sin stress
        market_risk=0.10,  # Puede ser caro pero conocido
        description="Rápido, garantizado, sin esfuerzo. Más caro pero sin riesgo."
    )
    
    # Opción 3: Encargar a carpintero
    custom_carpenter = CareerOption(
        name="Encargar - Carpintero a medida",
        salary_expected=400_000,  # Costo carpintero estimado
        probability_success=0.85,  # 85% (depende carpintero)
        timeline_months=1,  # 1 mes espera
        tech_growth=3.0,  # Aprendes poco (solo supervisar)
        income_stability=7.0,  # Depende carpintero
        work_life_balance=8.0,  # Poco esfuerzo tuyo
        prestige=8.0,  # ✅ Mueble personalizado
        remote_flexibility=6.0,  # Coordinar con carpintero
        learning_opportunity=4.0,  # Aprendes algo viendo
        career_ceiling=4.0,  # No mucho para futuro
        unemployment_risk=0.15,  # Riesgo carpintero malo
        burnout_risk=0.10,  # Puede ser estresante coordinar
        market_risk=0.25,  # Puede costar más de lo cotizado
        description="A tu medida, calidad profesional. Más caro, pero exactamente lo que quieres."
    )
    
    # Opción 4: Kit DIY (Ikea-style)
    kit_diy = CareerOption(
        name="Kit DIY - Comprar kit para armar",
        salary_expected=200_000,  # Precio kit estimado
        probability_success=0.80,  # 80% (instrucciones claras)
        timeline_months=0,  # Inmediato (armas en horas)
        tech_growth=5.0,  # Aprendes algo
        income_stability=8.0,  # Garantía kit
        work_life_balance=7.0,  # Esfuerzo moderado
        prestige=6.0,  # Armaste algo
        remote_flexibility=9.0,  # Armas cuando quieras
        learning_opportunity=6.0,  # Aprendes ensamblaje
        career_ceiling=5.0,  # Habilidad útil
        unemployment_risk=0.10,  # Bajo (instrucciones)
        burnout_risk=0.15,  # Puede ser tedioso
        market_risk=0.15,  # Precio conocido
        description="Término medio: aprendes algo, no muy caro, menos riesgo que DIY completo."
    )
    
    return [diy_full, buy_store, custom_carpenter, kit_diy]


def main():
    print("\n" + "="*70)
    print("   🔨 DECISIÓN: ¿Hacer mueble DIY o Comprar?")
    print("="*70)
    print("\n📋 Especificaciones:")
    print("   • 60cm alto × 60cm ancho × 1.8m largo")
    print("   • Uso: Mesón para bebé + almacenamiento")
    print("   • Similar a: Rack TV\n")
    
    # Paso 1: Investigar con Gemini
    if GEMINI_AVAILABLE and os.environ.get('GEMINI_API_KEY'):
        print("🔍 Paso 1: Investigando con Gemini (gratuito)...\n")
        gemini_results = research_diy_furniture()
    else:
        print("⚠️  Gemini no disponible. Usando estimaciones.\n")
        gemini_results = {
            "Precio materiales": "Estimación: $100-200k CLP",
            "Precio tienda": "Estimación: $250-400k CLP",
            "Dificultad DIY": "Medio-Alto para principiantes",
            "Precio carpintero": "Estimación: $350-500k CLP"
        }
    
    # Paso 2: Crear opciones
    options = create_furniture_options(gemini_results)
    
    print("📋 Opciones creadas:\n")
    for i, opt in enumerate(options, 1):
        print(f"{i}. {opt.name}")
        print(f"   💰 ${opt.salary_expected:,.0f} | 🎯 {opt.probability_success*100:.0f}% éxito")
        print(f"   ⏱️  {opt.timeline_months} {'mes' if opt.timeline_months == 1 else 'meses'}")
        print(f"   📝 {opt.description}")
        print()
    
    # Paso 3: Analizar con Python Framework
    print("="*70)
    print("   🐍 ANÁLISIS PYTHON FRAMEWORK (13 metodologías)")
    print("="*70 + "\n")
    
    engine = DecisionAnalysisEngine(debug=False)
    
    results = []
    for option in options:
        print(f"   ▶ {option.name}...")
        result = engine.analyze_option(option, options)
        results.append(result)
    
    # Mostrar resultados Python
    print("\n" + "="*70)
    print("   📊 RESULTADOS PYTHON")
    print("="*70 + "\n")
    
    sorted_results = sorted(zip(options, results), 
                           key=lambda x: x[1].overall_score, 
                           reverse=True)
    
    for rank, (option, result) in enumerate(sorted_results, 1):
        emoji = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else "  "
        print(f"{emoji} RANK {rank}: {option.name}")
        print(f"   📊 Score: {result.overall_score:.2f}/10")
        print(f"   💰 Costo: ${option.salary_expected:,.0f}")
        print(f"   🎯 Éxito: {option.probability_success*100:.0f}%")
        print(f"   ⏱️  Timeline: {option.timeline_months} {'mes' if option.timeline_months == 1 else 'meses'}")
        
        if result.overall_score >= 5.0:
            print(f"   ✅ RECOMENDADO")
        elif result.overall_score >= 3.5:
            print(f"   ⚠️  VIABLE")
        else:
            print(f"   ❌ {result.recommendation}")
        print()
    
    # Análisis del ganador
    winner_opt, winner_res = sorted_results[0]
    
    print("="*70)
    print("   🏆 GANADOR PYTHON")
    print("="*70 + "\n")
    print(f"   {winner_opt.name}")
    print(f"   Score: {winner_res.overall_score:.2f}/10\n")
    print(f"   ✅ Ventajas:")
    print(f"      • Costo: ${winner_opt.salary_expected:,.0f}")
    print(f"      • Probabilidad éxito: {winner_opt.probability_success*100:.0f}%")
    print(f"      • Timeline: {winner_opt.timeline_months} {'mes' if winner_opt.timeline_months == 1 else 'meses'}")
    print(f"      • Learning: {winner_opt.learning_opportunity}/10")
    print(f"      • WLB: {winner_opt.work_life_balance}/10\n")
    
    print("="*70 + "\n")
    
    print("💡 SIGUIENTE: Ejecutar análisis C++ para comparar")
    print("   Comando: cd core && ./furniture_analysis\n")
    
    return winner_opt.name, winner_res.overall_score


if __name__ == "__main__":
    winner, score = main()
    print(f"✨ Mejor opción (Python): {winner} ({score:.2f}/10)\n")
