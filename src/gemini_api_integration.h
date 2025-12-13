/**
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
 *   - GEMINI_API_KEY en variable de entorno o pasado al constructor
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
    // NO hardcodear API keys en código. Usar variables de entorno.
    
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
                throw std::runtime_error(
                    "GEMINI_API_KEY no encontrado.\n"
                    "Soluciones:\n"
                    "1. Copia .env.gemini.template a .env.gemini\n"
                    "2. Agrega tu API key en .env.gemini\n"
                    "3. O establece GEMINI_API_KEY como variable de entorno\n"
                    "4. O pasa la API key en el constructor"
                );
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
