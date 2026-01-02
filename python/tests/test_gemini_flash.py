#!/usr/bin/env python3
"""
🧪 Test simple con Gemini Flash (modelo más barato)
"""

import sys
import os
from pathlib import Path

# Add to path
sys.path.insert(0, str(Path(__file__).parent))

from config import GeminiConfig
from dotenv import load_dotenv

load_dotenv()

def test_simple_query():
    """Test simple sin usar el framework completo"""
    print("\n" + "="*70)
    print("   🧪 TEST SIMPLE GEMINI FLASH")
    print("="*70 + "\n")
    
    # Mostrar config
    config = GeminiConfig()
    config.print_config()
    
    # Import Gemini
    try:
        from google import genai
    except ImportError:
        print("❌ google-genai no instalado")
        return False
    
    # Initialize client
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY no configurado")
        return False
    
    try:
        client = genai.Client(api_key=api_key)
        print("✅ Cliente Gemini inicializado\n")
        
        # Test query simple
        print("📤 Enviando query de prueba...")
        print("   Pregunta: '¿Cuál es la capital de Chile?'\n")
        
        response = client.models.generate_content(
            model=config.get_model_name(),
            contents="¿Cuál es la capital de Chile? Responde en una sola palabra."
        )
        
        # Extract response
        if hasattr(response, 'text'):
            answer = response.text.strip()
        elif hasattr(response, 'candidates') and response.candidates:
            parts = response.candidates[0].content.parts
            answer = "".join([part.text for part in parts if hasattr(part, 'text')])
        else:
            answer = str(response)
        
        print("📥 Respuesta recibida:")
        print(f"   {answer}\n")
        
        # Estimate cost
        input_tokens = 20  # Aproximado
        output_tokens = 10  # Aproximado
        cost = config.estimate_cost(input_tokens, output_tokens)
        
        print("💰 Estimación de costo:")
        print(f"   Input: ~{input_tokens} tokens")
        print(f"   Output: ~{output_tokens} tokens")
        print(f"   Costo: ${cost:.6f}")
        
        if cost == 0:
            print("   🎉 ¡GRATIS con Flash!")
        
        print("\n" + "="*70)
        print("   ✅ TEST EXITOSO")
        print("="*70 + "\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        import traceback
        traceback.print_exc()
        return False

def test_decision_analysis():
    """Test de análisis de decisión simple"""
    print("\n" + "="*70)
    print("   🧪 TEST ANÁLISIS DE DECISIÓN CON GEMINI FLASH")
    print("="*70 + "\n")
    
    try:
        from google import genai
        from config import GeminiConfig
        
        config = GeminiConfig()
        api_key = os.getenv("GEMINI_API_KEY")
        client = genai.Client(api_key=api_key)
        
        # Pregunta de decisión simple
        decision_query = """
Tengo que decidir entre 2 opciones:

Opción A: Comprar laptop usada
- Precio: $500
- RAM: 16GB
- Procesador: i5 gen 8
- Estado: Bueno

Opción B: Comprar laptop nueva
- Precio: $1200
- RAM: 16GB  
- Procesador: i5 gen 13
- Estado: Nueva con garantía

¿Cuál recomiendas y por qué? Responde en máximo 3 líneas.
"""
        
        print("📤 Enviando análisis de decisión...")
        print("   Escenario: Compra de laptop\n")
        
        response = client.models.generate_content(
            model=config.get_model_name(),
            contents=decision_query
        )
        
        # Extract response
        if hasattr(response, 'text'):
            answer = response.text.strip()
        elif hasattr(response, 'candidates') and response.candidates:
            parts = response.candidates[0].content.parts
            answer = "".join([part.text for part in parts if hasattr(part, 'text')])
        else:
            answer = str(response)
        
        print("📥 Recomendación de Gemini:")
        print(f"\n{answer}\n")
        
        # Cost estimate
        input_tokens = 100
        output_tokens = 50
        cost = config.estimate_cost(input_tokens, output_tokens)
        
        print("💰 Costo estimado:")
        print(f"   ${cost:.6f} {'🎉 ¡GRATIS!' if cost == 0 else ''}\n")
        
        print("="*70)
        print("   ✅ ANÁLISIS COMPLETADO")
        print("="*70 + "\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    import sys
    
    # Test 1: Query simple
    test1 = test_simple_query()
    
    if not test1:
        print("\n⚠️  Test 1 falló, abortando test 2")
        sys.exit(1)
    
    # Test 2: Análisis de decisión
    test2 = test_decision_analysis()
    
    if test1 and test2:
        print("\n🎉 Ambos tests exitosos!")
        print("✅ Gemini Flash configurado y funcionando")
        sys.exit(0)
    else:
        print("\n⚠️  Algunos tests fallaron")
        sys.exit(1)
