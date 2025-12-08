#!/usr/bin/env python3
"""
🔍 Buscar y cargar GEMINI_API_KEY desde git bash
"""

import os
import subprocess
import json
from pathlib import Path


def find_gemini_key():
    """Buscar GEMINI_API_KEY en múltiples ubicaciones"""
    
    locations = [
        # Archivos shell
        Path.home() / ".bashrc",
        Path.home() / ".zshrc",
        Path.home() / ".bash_profile",
        Path.home() / ".profile",
        
        # Archivos especiales
        Path.home() / ".gemini",
        Path.home() / ".gemini_key",
        Path.home() / ".gemini_api_key",
        
        # Directorios config
        Path.home() / ".config" / "gemini",
        Path.home() / ".config" / ".gemini",
        Path.home() / ".config" / "gemini_key",
        
        # Git bash específico (Windows path)
        Path.home() / "AppData" / "Local" / "Programs" / "Git" / ".bashrc",
        Path.home() / ".gitconfig",
    ]
    
    print("🔍 Buscando GEMINI_API_KEY en múltiples ubicaciones...\n")
    
    # 1. Buscar en archivos
    for location in locations:
        if location.exists():
            try:
                with open(location, 'r') as f:
                    content = f.read()
                    if 'GEMINI' in content.upper() or 'GOOGLE' in content:
                        print(f"✅ Encontrado en: {location}")
                        # Mostrar líneas relevantes (sin exponer la key completa)
                        for i, line in enumerate(content.split('\n'), 1):
                            if 'GEMINI' in line.upper() or 'GOOGLE' in line.upper():
                                # Ocultar valor
                                if '=' in line:
                                    key_name = line.split('=')[0]
                                    print(f"   Línea {i}: {key_name}=***HIDDEN***")
                                else:
                                    print(f"   Línea {i}: {line[:50]}...")
            except Exception as e:
                pass
    
    # 2. Buscar en variables de entorno
    print("\n🔐 Variables de entorno relacionadas:")
    for var in os.environ:
        if 'GEMINI' in var.upper() or 'GOOGLE' in var.upper():
            value = os.environ[var]
            masked = value[:10] + "***" + value[-5:] if len(value) > 15 else "***"
            print(f"   {var}={masked}")
    
    # 3. Ejecutar comando en bash si está disponible
    print("\n💡 Intentando leer desde bash...")
    try:
        result = subprocess.run(
            "source ~/.bashrc 2>/dev/null && env | grep -i gemini",
            shell=True,
            capture_output=True,
            text=True
        )
        if result.stdout:
            print(f"✅ Encontrado en bash environment:")
            for line in result.stdout.strip().split('\n'):
                if line:
                    key_name = line.split('=')[0]
                    print(f"   {key_name}=***HIDDEN***")
    except Exception as e:
        print(f"   (No se pudo ejecutar bash)")
    
    # 4. Si todo falla, mostrar instrucciones
    print("\n" + "="*80)
    print("📝 ¿NO LA ENCUENTRO?")
    print("="*80)
    print("""
Si la tienes en git bash pero no aparece aquí, haz esto:

1. Abre git bash manualmente
2. Ejecuta: echo $GEMINI_API_KEY
3. Si aparece, cópiala

4. Luego en tu terminal actual:
   export GEMINI_API_KEY="<pega_aqui>"

5. Verifica:
   echo $GEMINI_API_KEY

6. Ejecuta el script:
   python3 scripts/gemini_market_research.py --sillon
""")


if __name__ == "__main__":
    find_gemini_key()
