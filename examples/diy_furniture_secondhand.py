#!/usr/bin/env python3
"""
Análisis: ¿Hacer mueble DIY vs Comprar usado vs Comprar nuevo?
Usando Gemini API (gemini-pro gratuito) para buscar precios en Chile
"""

import os
import sys

GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY', '')
if not GOOGLE_API_KEY:
    print("Error: Set GOOGLE_API_KEY environment variable")
    sys.exit(1)

try:
    import google.generativeai as genai
    genai.configure(api_key=GOOGLE_API_KEY)
except ImportError:
    print("Error: Instalar google-generativeai")
    print("Ejecutar: uv pip install google-generativeai")
    sys.exit(1)

# Usar gemini-pro (modelo gratuito disponible)
model = genai.GenerativeModel('gemini-pro')

print("=" * 80)
print("ANÁLISIS: Mueble para bebé - DIY vs Comprar Usado vs Comprar Nuevo")
print("=" * 80)
print("\nEspecificaciones: 180cm largo x 60cm ancho x 60cm alto")
print("Uso: Mesa/mueble para bebé con almacenamiento debajo\n")

print("🔍 Consultando Gemini Pro sobre precios en Chile...\n")

prompt = """
Necesito información sobre precios en Chile (CLP) para el año 2024-2025:

1. Precio aproximado de muebles USADOS tipo rack/mesa de TV de 180cm en:
   - Yapo.cl
   - Marketplace Facebook
   - Mercado Libre Chile
   
2. Precio de muebles NUEVOS similares en Sodimac, Easy, Falabella

3. Costo de MATERIALES DIY en Chile para mueble de 180x60x60cm:
   - Madera MDF o terciado
   - Tornillos y herrajes
   - Barniz o pintura

Dame rangos de precios en CLP.
"""

try:
    response = model.generate_content(prompt)
    print("📊 Información de Gemini:\n")
    print(response.text)
    print("\n" + "=" * 80)
except Exception as e:
    print(f"❌ Error: {e}\n")
    print("Usando estimaciones locales...\n")

print("\n" + "=" * 80)
print("ANÁLISIS COMPARATIVO EN CLP (Pesos Chilenos)")
print("=" * 80)

print("""

   💰 Materiales: 25,000-45,000 CLP
   🔧 Herramientas (si no tienes): 0-30,000 CLP
   ⏱️ Tiempo: 1-2 días trabajo
   ✅ Pros: Medidas exactas, personalizable, satisfacción
   ❌ Contras: Requiere habilidad, tiempo, herramientas

   💰 Mueble: 15,000-50,000 CLP
   🚚 Transporte: 5,000-15,000 CLP
   ⏱️ Tiempo búsqueda: 1-7 días
   ✅ Pros: MÁS ECONÓMICO, inmediato, sin trabajo
   ❌ Contras: Desgaste, medidas no exactas

   💰 Mueble: 80,000-200,000 CLP
   🚚 Despacho: 0-20,000 CLP
   ⏱️ Disponibilidad: Inmediata
   ✅ Pros: Garantía, nuevo/limpio, sin trabajo
   ❌ Contras: MÁS CARO, medidas estándar
""")

print("=" * 80)
print("💡 RECOMENDACIÓN FINAL")
print("=" * 80)
print("""

RAZONES:
 Ahorro: 20,000-50,000 CLP vs 80,000-200,000 CLP nuevo
 Sin tiempo de construcción
 Disponible rápidamente
 Ecológico (reutilización)

1. Yapo.cl (mayor variedad usados)
2. Facebook Marketplace (buenos precios)
3. Mercado Libre Chile (con envío)


 VERIFICAR:
- Estado general (fotos reales)
- Estabilidad (importante para bebé)
- Dimensiones exactas
- Incluye transporte en presupuesto

SCORE ESTIMADO: 7.5/10
(Mejor relación costo-beneficio-tiempo)
""")

print("=" * 80)
print("Modelo usado: Gemini Pro (gratuito)")
print("=" * 80)
