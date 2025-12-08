#!/usr/bin/env python3
"""
🌐 API GEMINI INTEGRATION - Búsqueda en Internet para Análisis de Decisión
Integra Google Gemini API para investigación de mercado en tiempo real

Uso:
    python3 scripts/gemini_market_research.py --api-key YOUR_KEY --query "sillón Santiago"
    O
    export GEMINI_API_KEY=your_key
    python3 scripts/gemini_market_research.py --query "sillón Santiago"
"""

import os
import sys
import json
import argparse
from datetime import datetime
from typing import Dict, List, Optional

try:
    import google.generativeai as genai
except ImportError:
    print("❌ Falta instalar google-generativeai")
    print("   pip install google-generativeai")
    sys.exit(1)


class GeminiMarketResearch:
    def __init__(self, api_key: Optional[str] = None):
        """
        Inicializar con API key de Gemini
        
        Args:
            api_key: Si no se proporciona, busca en variable de entorno GEMINI_API_KEY
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        
        if not self.api_key:
            raise ValueError(
                "❌ GEMINI_API_KEY no encontrado\n"
                "   Usa: export GEMINI_API_KEY=your_key\n"
                "   O:   python3 script.py --api-key YOUR_KEY"
            )
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel("gemini-2.5-flash")
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "queries": [],
            "market_analysis": {},
            "recommendations": []
        }
    
    def search_market_prices(self, product: str, location: str = "Santiago, Chile") -> Dict:
        """
        Buscar precios de mercado para un producto
        
        Args:
            product: Producto a buscar (ej: "sillón madera tapizado")
            location: Ubicación (ej: "Santiago, Chile")
        
        Returns:
            Dict con precios y análisis
        """
        print(f"\n🔍 Buscando precios de '{product}' en {location}...")
        
        prompt = f"""
Proporciona un análisis DETALLADO y REALISTA del mercado para {product} en {location}.

Incluye:
1. PRECIOS DE VENTA (mercado actual):
   - Nuevo: rango de precios en CLP
   - Usado en buen estado: rango de precios
   - Usado necesita arreglo: rango de precios

2. PRECIOS DE SERVICIOS:
   - Limpieza profunda: rango de precios
   - Reparación/tapicería: rango de precios
   - Transporte/recolección: rango de precios

3. DEMANDA Y PROBABILIDAD:
   - ¿Se venden bien en el mercado local?
   - Tiempo promedio de venta (en días)
   - Probabilidad de venta (%)
   - Factores que afectan la venta

4. PLATAFORMAS PRINCIPALES:
   - Dónde venderlo (OLX, Facebook, otros)
   - Tips para vender rápido

5. ANÁLISIS:
   - ¿Vale la pena invertir en arreglo?
   - Mejor estrategia

Sé ESPECÍFICO con números en CLP (pesos chilenos).
Usa datos REALES y ACTUALES del mercado.
"""
        
        try:
            response = self.model.generate_content(prompt)
            analysis = response.text
            
            print(f"\n✅ Análisis recibido ({len(analysis)} caracteres)")
            
            result = {
                "product": product,
                "location": location,
                "query_time": datetime.now().isoformat(),
                "analysis": analysis
            }
            
            self.results["queries"].append(result)
            print(f"   Guardado en results['queries'] (total: {len(self.results['queries'])})")
            return result
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return {"error": str(e), "product": product}
    
    def analyze_sillon_decision(self) -> Dict:
        """
        Análisis específico para decisión del sillón
        """
        print("\n🪑 Analizando decisión del sillón con Gemini...")
        
        prompt = """
ANÁLISIS PARA DECISIÓN: ¿Qué hacer con un sillón viejo, roto y sucio?

CONTEXTO:
- Ubicación: Santiago, La Florida
- Estado: Sillón madera tapizado, roto, sucio
- Situación financiera: Muy corto de dinero
- Plazo: 1 mes para resolver

OPCIONES A EVALUAR:
1. Botarlo (pagar ~$85,000 CLP)
2. Solo limpiarlo (invertir ~$40,000 CLP)
3. Limpiar + Reparar (invertir ~$75,000 CLP)

POR FAVOR PROPORCIONA:

1. ANÁLISIS DE MERCADO ACTUAL:
   - ¿Se venden sillones usados en Santiago?
   - Precios reales en OLX/Facebook para sillones similares
   - Cuánto tardan en vender típicamente?

2. COSTOS REALISTAS (CLP):
   - Servicio de limpieza profunda en La Florida
   - Reparación mecánica (resortes, etc.)
   - Transporte/recolección para venta
   - Botado de mueble

3. PROBABILIDAD DE ÉXITO:
   - % de sillones usados que se venden
   - Factores que determinan venta
   - Tiempo promedio para vender

4. RECOMENDACIÓN:
   - ¿Cuál opción financieramente es mejor?
   - Por qué?
   - Plan B si algo sale mal?

5. ESTRATEGIA DE VENTA:
   - Plataformas recomendadas
   - Precio sugerido
   - Descripción/fotos que funcionan
   - Cómo vender rápido

Sé ESPECÍFICO con números CLP actualizados.
Usa datos REALES del mercado Santiago actual.
"""
        
        try:
            response = self.model.generate_content(prompt)
            analysis = response.text
            
            print(f"\n✅ Análisis del sillón recibido ({len(analysis)} caracteres)")
            
            result = {
                "analysis_type": "sillon_decision",
                "analysis": analysis,
                "query_time": datetime.now().isoformat()
            }
            
            self.results["market_analysis"]["sillon"] = result
            print(f"   Guardado en results['market_analysis']['sillon']")
            return result
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return {"error": str(e)}
    
    def generate_cpp_integration(self) -> str:
        """
        Generar código C++ para integración con API Gemini
        """
        cpp_code = '''/**
 * @file gemini_api_integration.h
 * @brief Integración de Google Gemini API para búsqueda en tiempo real
 * 
 * Permite hacer queries a Gemini desde C++ para mejorar análisis de decisión
 * 
 * Compilar con:
 *   g++ -std=c++17 -lcurl -o programa programa.cpp
 * 
 * Requiere:
 *   - libcurl (para HTTP requests)
 *   - GEMINI_API_KEY en variable de entorno
 */

#pragma once

#include <string>
#include <iostream>
#include <curl/curl.h>
#include <nlohmann/json.hpp>

using json = nlohmann::json;

namespace DecisionFramework {

class GeminiAPI {
private:
    std::string api_key_;
    std::string base_url_ = "https://generativelanguage.googleapis.com/v1beta/models";
    
    // Callback para capturar respuesta HTTP
    static size_t WriteCallback(void* contents, size_t size, size_t nmemb, std::string* userp) {
        userp->append((char*)contents, size * nmemb);
        return size * nmemb;
    }

public:
    GeminiAPI(const std::string& api_key = "") {
        if (!api_key.empty()) {
            api_key_ = api_key;
        } else {
            const char* env_key = std::getenv("GEMINI_API_KEY");
            if (env_key) {
                api_key_ = env_key;
            } else {
                throw std::runtime_error("GEMINI_API_KEY no encontrado");
            }
        }
    }
    
    /**
     * @brief Hacer query a Gemini
     * @param prompt Pregunta o prompt para Gemini
     * @return Respuesta de Gemini como string
     */
    std::string query(const std::string& prompt) {
        CURL* curl = curl_easy_init();
        if (!curl) throw std::runtime_error("No se pudo inicializar CURL");
        
        // Construir JSON request
        json request = {
            {"contents", {
                {{"parts", {
                    {{"text", prompt}}
                }}}
            }}
        };
        
        std::string request_body = request.dump();
        std::string response;
        
        // URL de la API
        std::string url = base_url_ + "/gemini-pro:generateContent?key=" + api_key_;
        
        // Configurar CURL
        struct curl_slist* headers = nullptr;
        headers = curl_slist_append(headers, "Content-Type: application/json");
        
        curl_easy_setopt(curl, CURLOPT_URL, url.c_str());
        curl_easy_setopt(curl, CURLOPT_HTTPHEADER, headers);
        curl_easy_setopt(curl, CURLOPT_POSTFIELDS, request_body.c_str());
        curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, WriteCallback);
        curl_easy_setopt(curl, CURLOPT_WRITEDATA, &response);
        
        // Realizar request
        CURLcode res = curl_easy_perform(curl);
        
        // Limpiar
        curl_slist_free_all(headers);
        curl_easy_cleanup(curl);
        
        if (res != CURLE_OK) {
            throw std::runtime_error(std::string("CURL error: ") + curl_easy_strerror(res));
        }
        
        // Parsear respuesta
        try {
            json response_json = json::parse(response);
            if (response_json.contains("candidates")) {
                return response_json["candidates"][0]["content"]["parts"][0]["text"];
            }
        } catch (...) {
            throw std::runtime_error("Error parseando respuesta de Gemini");
        }
        
        return response;
    }
    
    /**
     * @brief Buscar precios de mercado
     */
    std::string search_market_prices(const std::string& product, const std::string& location) {
        std::string prompt = "¿Cuál es el precio actual de " + product + " en " + location + 
                           "? Proporciona rangos reales de mercado.";
        return query(prompt);
    }
    
    /**
     * @brief Analizar decisión del sillón
     */
    std::string analyze_sillon_decision() {
        std::string prompt = R"(
Analiza la siguiente decisión:
- Tengo un sillón viejo, roto y sucio en Santiago, La Florida
- Estoy muy corto de dinero
- Tengo 1 mes para resolver

Opciones:
1. Botarlo: $85,000 CLP
2. Solo limpiar: $40,000 CLP
3. Limpiar + reparar: $75,000 CLP

¿Cuál es la mejor opción financieramente? 
Proporciona precios REALES de mercado actual.
)";
        return query(prompt);
    }
};

} // namespace DecisionFramework
'''
        return cpp_code
    
    def save_results(self, filename: str = "gemini_results.json"):
        """Guardar resultados de búsquedas"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        print(f"\n✅ Resultados guardados en: {filename}")
    
    def print_results(self):
        """Mostrar resultados formateados"""
        print("\n" + "="*80)
        print("📊 RESULTADOS DE ANÁLISIS CON GEMINI")
        print("="*80)
        
        for query in self.results["queries"]:
            print(f"\n🔍 Búsqueda: {query['product']} en {query['location']}")
            print("-"*80)
            if "error" in query:
                print(f"❌ Error: {query['error']}")
            else:
                print(query["analysis"])
        
        if "sillon" in self.results["market_analysis"]:
            print("\n" + "="*80)
            print("🪑 ANÁLISIS DECISIÓN SILLÓN")
            print("="*80)
            sillon_analysis = self.results["market_analysis"]["sillon"]
            if "error" in sillon_analysis:
                print(f"❌ Error: {sillon_analysis['error']}")
            else:
                print(sillon_analysis["analysis"])


def main():
    parser = argparse.ArgumentParser(
        description="🌐 Investigación de mercado con Gemini API"
    )
    parser.add_argument(
        "--api-key",
        help="Google Gemini API Key (o usa GEMINI_API_KEY env var)",
        default=None
    )
    parser.add_argument(
        "--query",
        help="Query de búsqueda (ej: 'sillón Santiago')",
        default="sillón madera tapizado Santiago"
    )
    parser.add_argument(
        "--sillon",
        action="store_true",
        help="Ejecutar análisis específico del sillón"
    )
    parser.add_argument(
        "--output",
        help="Archivo de salida (default: gemini_results.json)",
        default="gemini_results.json"
    )
    
    args = parser.parse_args()
    
    try:
        # Inicializar
        researcher = GeminiMarketResearch(api_key=args.api_key)
        
        print("\n🌐 Iniciando búsqueda con Gemini API...")
        
        # Query general
        if args.query:
            result = researcher.search_market_prices(args.query)
            if "error" not in result:
                print(f"\n✅ Búsqueda completada")
        
        # Análisis del sillón
        if args.sillon:
            result = researcher.analyze_sillon_decision()
            if "error" not in result:
                print(f"\n✅ Análisis completado")
        
        # Mostrar y guardar resultados
        researcher.print_results()
        researcher.save_results(args.output)
        
        # Generar código C++
        cpp_code = researcher.generate_cpp_integration()
        with open("src/gemini_api_integration.h", "w") as f:
            f.write(cpp_code)
        print(f"\n✅ Código C++ generado en: src/gemini_api_integration.h")
        
    except ValueError as e:
        print(f"❌ Error de configuración: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
