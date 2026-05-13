#!/usr/bin/env python3
"""
"""

import sys
from pathlib import Path

def test_file_structure():
    """Verificar que los archivos están en su lugar"""
    print("🧪 Test 1: Verificando estructura de archivos...")
    
    base = Path(__file__).parent
    
    files_to_check = {
        "core/deep_research_decision_agent.py": "Motor principal de decisiones",
        "core/mining_career_analyzer.py": "Analizador de carrera minería",
        "scripts/gemini_query.py": "Query Gemini",
        "scripts/validate_logic.py": "Validación de lógica",
        "requirements.txt": "Dependencias Python",
        "README.md": "Documentación Python",
    }
    
    all_exist = True
    for file, description in files_to_check.items():
        file_path = base / file
        exists = file_path.exists()
        status = "✅" if exists else "❌"
        print(f"   {status} {file:<45} {description}")
        if not exists:
            all_exist = False
    
    return all_exist

def test_code_syntax():
    """Verificar que el código Python es sintácticamente correcto"""
    print("\n🧪 Test 2: Verificando sintaxis de código...")
    
    base = Path(__file__).parent
    
    files_to_compile = [
        "core/deep_research_decision_agent.py",
        "core/mining_career_analyzer.py",
        "scripts/gemini_query.py",
        "scripts/validate_logic.py",
    ]
    
    all_valid = True
    for file in files_to_compile:
        file_path = base / file
        if not file_path.exists():
            continue
            
        try:
            with open(file_path, 'r') as f:
                code = f.read()
            compile(code, str(file_path), 'exec')
            print(f"   ✅ {file:<45} Sintaxis OK")
        except SyntaxError as e:
            print(f"   ❌ {file:<45} Error: {e}")
            all_valid = False
    
    return all_valid

def test_imports_availability():
    """Verificar qué imports están disponibles"""
    print("\n🧪 Test 3: Verificando módulos Python estándar...")
    
    standard_modules = [
        ("os", "Sistema operativo"),
        ("sys", "Sistema"),
        ("json", "JSON parsing"),
        ("datetime", "Fecha y hora"),
        ("pathlib", "Rutas de archivos"),
        ("typing", "Type hints"),
        ("dataclasses", "Data classes"),
        ("asyncio", "Async/await"),
        ("random", "Números aleatorios"),
        ("statistics", "Estadísticas"),
    ]
    
    all_available = True
    for module, description in standard_modules:
        try:
            __import__(module)
            print(f"   ✅ {module:<20} {description}")
        except ImportError:
            print(f"   ❌ {module:<20} NO disponible")
            all_available = False
    
    return all_available

def test_external_dependencies():
    """Verificar dependencias externas (sin fallar si no están)"""
    print("\n🧪 Test 4: Verificando dependencias externas (opcional)...")
    
    external_modules = [
        ("google.genai", "Gemini AI"),
        ("dotenv", "Environment variables"),
        ("numpy", "NumPy"),
        ("pandas", "Pandas"),
    ]
    
    available = []
    missing = []
    
    for module, description in external_modules:
        try:
            __import__(module)
            print(f"   ✅ {module:<20} {description}")
            available.append(module)
        except ImportError:
            print(f"   ⚠️  {module:<20} No instalado (pip install {module.split('.')[0]})")
            missing.append(module)
    
    if missing:
        print(f"\n   ℹ️  Instalar con: pip install -r requirements.txt")
    
    return available, missing

def count_lines_of_code():
    """Contar líneas de código"""
    print("\n📊 Estadísticas de código:")
    
    base = Path(__file__).parent
    
    files = [
        "core/deep_research_decision_agent.py",
        "core/mining_career_analyzer.py",
    ]
    
    total_lines = 0
    for file in files:
        file_path = base / file
        if file_path.exists():
            with open(file_path, 'r') as f:
                lines = len(f.readlines())
            total_lines += lines
            print(f"   📄 {file:<45} {lines:>5} líneas")
    
    print(f"\n   📦 Total Python Framework: {total_lines:>5} líneas")
    return total_lines

def main():
    print("\n" + "="*70)
    print("   🚀 TEST DE ESTRUCTURA - FRAMEWORK REORGANIZADO")
    print("="*70 + "\n")
    
    # Run tests
    test1 = test_file_structure()
    test2 = test_code_syntax()
    test3 = test_imports_availability()
    available, missing = test_external_dependencies()
    total_lines = count_lines_of_code()
    
    # Summary
    print("\n" + "="*70)
    print("   📋 RESUMEN")
    print("="*70)
    
    tests_passed = sum([test1, test2, test3])
    tests_total = 3
    
    print(f"\n   Tests pasados: {tests_passed}/{tests_total}")
    
    if test1:
        print("   ✅ Estructura de archivos: OK")
    else:
        print("   ❌ Estructura de archivos: FALTAN ARCHIVOS")
    
    if test2:
        print("   ✅ Sintaxis de código: OK")
    else:
        print("   ❌ Sintaxis de código: ERRORES")
    
    if test3:
        print("   ✅ Módulos estándar: OK")
    else:
        print("   ⚠️  Módulos estándar: ALGUNOS FALTAN")
    
    if missing:
        print(f"\n   ⚠️  Dependencias faltantes: {len(missing)}")
        print(f"   💡 Instalar con: pip install -r requirements.txt")
    else:
        print(f"\n   ✅ Todas las dependencias instaladas")
    
    if test1 and test2:
        print("\n   🎉 Estructura reorganizada: OPERACIONAL")
        print("   📁 Archivos en su lugar y sintaxis correcta")
    else:
        print("\n   ⚠️  Revisar estructura o sintaxis")
    
    print("\n" + "="*70 + "\n")
    
    return test1 and test2

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
