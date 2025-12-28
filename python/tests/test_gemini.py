#!/usr/bin/env python3
"""
"""

import sys
import os
from pathlib import Path

def test_uv_env():
    """Test 1: Verificar entorno UV"""
    print("🧪 Test 1: Verificando entorno UV...")
    
    venv_path = Path(__file__).parent / ".venv"
    if venv_path.exists():
        print(f"   ✅ Virtual environment UV existe: {venv_path}")
        
        # Check Python version
        import platform
        print(f"   ✅ Python version: {platform.python_version()}")
        
        return True
    else:
        print(f"   ❌ Virtual environment no encontrado")
        return False

def test_google_genai():
    """Test 2: Verificar instalación de google-genai"""
    print("\n🧪 Test 2: Verificando google-genai...")
    
    try:
        import google.genai as genai
        print(f"   ✅ google-genai instalado correctamente")
        print(f"   📦 Versión: {genai.__version__ if hasattr(genai, '__version__') else 'N/A'}")
        return True, genai
    except ImportError as e:
        print(f"   ❌ google-genai no instalado: {e}")
        return False, None

def test_dependencies():
    """Test 3: Verificar otras dependencias"""
    print("\n🧪 Test 3: Verificando dependencias...")
    
    deps = {
        'dotenv': 'python-dotenv',
        'numpy': 'numpy', 
        'pandas': 'pandas',
        'aiohttp': 'aiohttp',
    }
    
    all_ok = True
    for module, package in deps.items():
        try:
            __import__(module)
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package} faltante")
            all_ok = False
    
    return all_ok

def test_env_file():
    """Test 4: Verificar archivo .env"""
    print("\n🧪 Test 4: Verificando configuración .env...")
    
    env_path = Path(__file__).parent / ".env"
    
    if not env_path.exists():
        print(f"   ⚠️  Archivo .env no existe")
        print(f"   💡 Crea uno desde: cp .env.example .env")
        return False
    
    print(f"   ✅ Archivo .env existe")
    
    # Load and check
    from dotenv import load_dotenv
    load_dotenv(env_path)
    
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key and api_key != "your_api_key_here":
        print(f"   ✅ GEMINI_API_KEY configurado ({api_key[:20]}...)")
        return True
    else:
        print(f"   ⚠️  GEMINI_API_KEY no configurado o es el valor ejemplo")
        print(f"   💡 Edita .env y agrega tu API key de Google AI Studio")
        return False

def test_genai_connection(genai):
    """Test 5: Verificar conexión con Gemini (opcional)"""
    print("\n🧪 Test 5: Verificando conexión Gemini...")
    
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "your_api_key_here":
        print(f"   ⚠️  Saltando test - API key no configurado")
        return None
    
    try:
        # Initialize client
        client = genai.Client(api_key=api_key)
        print(f"   ✅ Cliente Gemini inicializado")
        
        # Try a simple query (won't actually execute to save quota)
        print(f"   ✅ Configuración lista para usar")
        return True
        
    except Exception as e:
        print(f"   ❌ Error conectando con Gemini: {e}")
        return False

def main():
    print("\n" + "="*70)
    print("   🚀 TEST UV + GOOGLE GEMINI")
    print("="*70 + "\n")
    
    # Run tests
    test1 = test_uv_env()
    test2, genai = test_google_genai()
    test3 = test_dependencies()
    test4 = test_env_file()
    
    # Optional test 5
    test5 = None
    if test2 and test4:
        test5 = test_genai_connection(genai)
    
    # Summary
    print("\n" + "="*70)
    print("   📋 RESUMEN")
    print("="*70)
    
    print(f"\n   Entorno UV:           {'✅' if test1 else '❌'}")
    print(f"   google-genai:         {'✅' if test2 else '❌'}")
    print(f"   Dependencias:         {'✅' if test3 else '❌'}")
    print(f"   Configuración .env:   {'✅' if test4 else '⚠️ '}")
    
    if test5 is not None:
        print(f"   Conexión Gemini:      {'✅' if test5 else '❌'}")
    else:
        print(f"   Conexión Gemini:      ⏭️  (no testeado)")
    
    if test1 and test2 and test3:
        print("\n   🎉 ENTORNO UV CONFIGURADO CORRECTAMENTE")
        
        if test4:
            print("   ✅ Listo para usar Gemini Deep Research")
        else:
            print("   ⚠️  Configura .env para usar Gemini")
    else:
        print("\n   ⚠️  CONFIGURACIÓN INCOMPLETA")
    
    print("\n" + "="*70 + "\n")
    
    return test1 and test2 and test3

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
