#!/usr/bin/env python3
"""
Script de utilidad para consultar Google Gemini API desde decision-maker
Uso: python3 gemini_query.py "Tu pregunta aquí"
"""

import requests
import json
import sys
import os
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Cargar variables de entorno desde .env.gemini si existe
env_file = Path(__file__).parent.parent / ".env.gemini"
if env_file.exists():
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ[key.strip()] = value.strip()

class GeminiClient:
    """Cliente para interactuar con Google Gemini API"""
    
    def __init__(self, api_key=None):
        # Prioridad: parámetro > variable de entorno > .env.gemini > error
        if api_key:
            self.api_key = api_key
        else:
            self.api_key = os.getenv("GEMINI_API_KEY")
            if not self.api_key:
                raise ValueError(
                    "❌ API key de Gemini no encontrada.\n"
                    "Soluciones:\n"
                    "1. Copia .env.gemini.template a .env.gemini\n"
                    "2. Agrega tu API key en .env.gemini\n"
                    "3. O establece GEMINI_API_KEY como variable de entorno\n"
                    "4. O pasa la API key directamente al constructor"
                )
        
        self.model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
        self.endpoint = os.getenv("GEMINI_API_ENDPOINT", "https://generativelanguage.googleapis.com/v1beta/models")
        self.timeout = int(os.getenv("GEMINI_TIMEOUT", "30"))
        self.debug = os.getenv("GEMINI_DEBUG", "false").lower() == "true"
        
        if self.debug:
            print(f"[DEBUG] Usando modelo: {self.model}")
            print(f"[DEBUG] API Key configurada: {bool(self.api_key)}")
    
    def query(self, prompt):
        """
        Envía un prompt a Gemini y retorna la respuesta
        
        Args:
            prompt (str): El prompt/pregunta para Gemini
            
        Returns:
            str: Respuesta de Gemini
        """
        url = f"{self.endpoint}/{self.model}:generateContent?key={self.api_key}"
        
        headers = {
            "Content-Type": "application/json"
        }
        
        body = {
            "contents": [{
                "parts": [{
                    "text": prompt
                }]
            }]
        }
        
        try:
            if self.debug:
                print(f"[DEBUG] POST a {url}")
                print(f"[DEBUG] Payload: {json.dumps(body, indent=2)}")
            
            response = requests.post(
                url, 
                json=body, 
                headers=headers, 
                timeout=self.timeout
            )
            response.raise_for_status()
            
            result = response.json()
            
            if self.debug:
                print(f"[DEBUG] Respuesta: {json.dumps(result, indent=2)}")
            
            if 'contents' in result and len(result['contents']) > 0:
                content = result['contents'][0]
                if 'parts' in content and len(content['parts']) > 0:
                    return content['parts'][0].get('text', '')
            
            return "Sin respuesta de Gemini"
            
        except requests.exceptions.Timeout:
            return f"Error: Timeout después de {self.timeout} segundos"
        except requests.exceptions.RequestException as e:
            return f"Error en la solicitud: {str(e)}"
        except json.JSONDecodeError:
            return f"Error: Respuesta inválida de Gemini"
        except Exception as e:
            return f"Error inesperado: {str(e)}"


def main():
    """Función principal"""
    if len(sys.argv) < 2:
        print("Uso: python3 gemini_query.py \"Tu pregunta aquí\"")
        print("\nEjemplos:")
        print("  python3 gemini_query.py \"¿Cuál es la capital de Francia?\"")
        print("  python3 gemini_query.py \"Analiza este código: print('hola')\"")
        sys.exit(1)
    
    prompt = " ".join(sys.argv[1:])
    
    client = GeminiClient()
    print("\n" + "="*80)
    print("CONSULTA GEMINI")
    print("="*80)
    print(f"\nPrompt: {prompt}\n")
    print("-"*80)
    print("Respuesta:\n")
    
    response = client.query(prompt)
    print(response)
    print("\n" + "="*80)


if __name__ == "__main__":
    main()
