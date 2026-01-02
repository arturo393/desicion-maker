#!/usr/bin/env python3
"""
Gemini with Google Search Grounding
Busca información en tiempo real usando Google Search integrado en Gemini
"""

import os
import json
import google.generativeai as genai
from pathlib import Path

class GeminiGrounding:
    """Cliente Gemini con capacidad de búsqueda en Google"""
    
    def __init__(self, api_key=None):
        # Cargar API key
        if api_key:
            self.api_key = api_key
        else:
            # Intentar desde .env
            env_file = Path(__file__).parent.parent / ".env"
            if env_file.exists():
                with open(env_file) as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            key, value = line.split("=", 1)
                            if key.strip() == "GEMINI_API_KEY":
                                self.api_key = value.strip().strip('"').strip("'")
                                break
            
            if not hasattr(self, 'api_key') or not self.api_key:
                self.api_key = os.getenv("GEMINI_API_KEY")
        
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY no encontrada")
        
        # Configurar Gemini
        genai.configure(api_key=self.api_key)
        
        # Usar modelo gratuito más reciente
        self.model = genai.GenerativeModel('gemini-2.0-flash')
    
    def search_and_answer(self, query, context=""):
        """
        Busca en Google y genera respuesta contextualizada
        
        Args:
            query: Pregunta o búsqueda a realizar
            context: Contexto adicional (opcional)
        
        Returns:
            dict con 'answer' y 'sources' si están disponibles
        """
        try:
            full_prompt = query
            if context:
                full_prompt = f"{context}\n\n{query}"
            
            response = self.model.generate_content(full_prompt)
            
            result = {
                'answer': response.text,
                'sources': []
            }
            
            # Extraer fuentes si están disponibles
            if hasattr(response, 'grounding_metadata'):
                for chunk in response.grounding_metadata.grounding_chunks:
                    if hasattr(chunk, 'web'):
                        result['sources'].append({
                            'url': chunk.web.uri,
                            'title': chunk.web.title if hasattr(chunk.web, 'title') else ''
                        })
            
            return result
            
        except Exception as e:
            return {
                'answer': f"Error: {str(e)}",
                'sources': [],
                'error': str(e)
            }
    
    def search_prices_chile(self, item_name, condition="usado"):
        """
        Búsqueda específica de precios en Chile
        
        Args:
            item_name: Nombre del producto/servicio
            condition: "nuevo" o "usado"
        
        Returns:
            Información de precios en CLP
        """
        query = f"""
Busca precios actuales en Chile (CLP) para: {item_name}
Condición: {condition}
Incluye:
- Rango de precios típicos
- Sitios donde se vende (Yapo, Mercado Libre, Facebook Marketplace)
- Diferencia entre nuevo y usado si aplica
- Fecha de los datos

Responde en formato estructurado con precios en CLP.
"""
        return self.search_and_answer(query)


def main():
    """Ejemplo de uso"""
    import sys
    
    if len(sys.argv) < 2:
        print("Uso: python3 gemini_grounding.py 'tu pregunta'")
        print("\nEjemplos:")
        print("  python3 gemini_grounding.py 'precio muebles rack tv usados Chile'")
        print("  python3 gemini_grounding.py 'precio madera aglomerada Santiago'")
        sys.exit(1)
    
    query = " ".join(sys.argv[1:])
    
    try:
        client = GeminiGrounding()
        print("\n" + "="*80)
        print("GEMINI + GOOGLE SEARCH GROUNDING")
        print("="*80)
        print(f"\nConsulta: {query}\n")
        print("-"*80)
        
        result = client.search_and_answer(query)
        
        print("\nRESPUESTA:\n")
        print(result['answer'])
        
        if result.get('sources'):
            print("\n" + "-"*80)
            print("FUENTES:")
            for i, source in enumerate(result['sources'], 1):
                print(f"{i}. {source.get('title', 'Sin título')}")
                print(f"   {source['url']}")
        
        print("\n" + "="*80)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
