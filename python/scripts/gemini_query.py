#!/usr/bin/env python3
"""
Script de utilidad para consultar Google Gemini API desde decision-maker
Soporta:
  - Gemini chat simple (gemini-2.0-flash)
  - Gemini Deep Research Agent (investigación profunda)

Uso: 
  python3 gemini_query.py "Tu pregunta aquí"
  python3 gemini_query.py --research "Tu pregunta para investigación profunda"
  python3 gemini_query.py --research --async "Pregunta con ejecución asíncrona"
"""

import requests
import json
import sys
import os
import asyncio
from pathlib import Path
from typing import Optional

# Cargar variables de entorno desde .env.gemini si existe
env_file = Path(__file__).parent / ".env.gemini"
if env_file.exists():
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ[key.strip()] = value.strip()

class GeminiClient:
    """Cliente para interactuar con Google Gemini API (chat simple)"""
    
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
            
            # Gemini API v1beta retorna 'candidates' en lugar de 'contents'
            if 'candidates' in result and len(result['candidates']) > 0:
                candidate = result['candidates'][0]
                if 'content' in candidate:
                    content = candidate['content']
                    if 'parts' in content and len(content['parts']) > 0:
                        return content['parts'][0].get('text', '')
            
            # Fallback para formato antiguo
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


class GeminiDeepResearchClient:
    """
    Cliente para Google Gemini Deep Research Agent
    Requiere: pip install google-genai
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not configured")
        
        self.debug = os.getenv("GEMINI_DEBUG", "false").lower() == "true"
        
        try:
            from google import genai
            self.client = genai.Client(api_key=self.api_key)
            self.available = True
        except ImportError:
            print("⚠️  google-genai no instalado. Install: pip install google-genai")
            self.available = False
    
    async def research(self, prompt: str, background: bool = True) -> str:
        """
        Ejecuta investigación profunda usando Deep Research Agent
        
        Args:
            prompt: Pregunta/tema para investigación
            background: Si True, ejecuta asíncrona
            
        Returns:
            str: Resultado de investigación
        """
        if not self.available:
            return "❌ Deep Research no disponible (google-genai no instalado)"
        
        try:
            if self.debug:
                print(f"[DEBUG] Deep Research Agent: {prompt[:50]}...")
            
            interaction = self.client.interactions.create(
                input=prompt,
                agent="deep-research-pro-preview-12-2025",
                background=background
            )
            
            if self.debug:
                print(f"[DEBUG] Interaction ID: {interaction.name}")
            
            # Para ejecución background, esperar completación
            if background:
                return await self._wait_for_completion(interaction)
            
            return str(interaction)
        
        except Exception as e:
            return f"Error en Deep Research: {str(e)}"
    
    async def _wait_for_completion(self, interaction, max_wait: int = 300):
        """Esperar a que se complete la investigación"""
        import time
        start = time.time()
        
        while time.time() - start < max_wait:
            try:
                status = self.client.interactions.get(name=interaction.name)
                if hasattr(status, 'response') and status.response:
                    return self._extract_text(status.response)
                
                await asyncio.sleep(5)
            except:
                await asyncio.sleep(5)
        
        return "⏱️ Investigación tardó más del tiempo permitido"
    
    def _extract_text(self, response) -> str:
        """Extrae texto de respuesta Gemini"""
        if isinstance(response, str):
            return response
        
        try:
            if hasattr(response, 'candidates'):
                for candidate in response.candidates:
                    if hasattr(candidate, 'content'):
                        parts = []
                        for part in candidate.content.parts:
                            if hasattr(part, 'text'):
                                parts.append(part.text)
                        if parts:
                            return "\n".join(parts)
        except:
            pass
        
        return json.dumps(response, indent=2)



def main():
    """Función principal con soporte para chat simple y Deep Research"""
    
    # Parse arguments
    use_deep_research = "--research" in sys.argv
    use_async = "--async" in sys.argv
    
    if use_deep_research:
        sys.argv.remove("--research")
    if use_async:
        sys.argv.remove("--async")
    
    if len(sys.argv) < 2:
        print("Uso: python3 gemini_query.py [opciones] \"Tu pregunta aquí\"")
        print("\nOpciones:")
        print("  (ninguna)     - Gemini chat simple (rápido)")
        print("  --research    - Deep Research Agent (profundo, toma más tiempo)")
        print("  --async       - Ejecutar Deep Research asíncrona")
        print("\nEjemplos:")
        print("  python3 gemini_query.py \"¿Cuál es la capital de Francia?\"")
        print("  python3 gemini_query.py --research \"Analiza minería en Chile 2025\"")
        sys.exit(1)
    
    prompt = " ".join(sys.argv[1:])
    
    if use_deep_research:
        # Deep Research Agent
        print("\n" + "="*80)
        print("🔍 GEMINI DEEP RESEARCH AGENT")
        print("="*80)
        print(f"\nPrompt: {prompt}\n")
        print("-"*80)
        print("Investigando...\n")
        
        try:
            client = GeminiDeepResearchClient()
            
            if use_async:
                # Async execution
                response = asyncio.run(client.research(prompt, background=True))
            else:
                # Sync execution
                async def sync_wrapper():
                    return await client.research(prompt, background=True)
                response = asyncio.run(sync_wrapper())
            
            print("Resultados de investigación:\n")
            print(response)
        
        except Exception as e:
            print(f"❌ Error: {e}")
    
    else:
        # Simple Gemini Chat
        print("\n" + "="*80)
        print("CONSULTA GEMINI (Chat Simple)")
        print("="*80)
        print(f"\nPrompt: {prompt}\n")
        print("-"*80)
        print("Respuesta:\n")
        
        client = GeminiClient()
        response = client.query(prompt)
        print(response)
    
    print("\n" + "="*80)


if __name__ == "__main__":
    main()
