/**
 * @file ai_deep_research_integration.h
 * @brief Integración de Google's Deep Research Pro con el Framework de Decisiones
 * 
 * Permite usar Google's Deep Research Pro (análisis profundo con IA) en combinación
 * con las metodologías de decisión del framework.
 * 
 * Requisitos:
 * - SDK: google-genai (no google-generativeai)
 * - Python 3.9+ con script deep_research_analyzer.py
 * - API Key: GOOGLE_API_KEY
 * 
 * Uso básico:
 * @code
 * AIAnalyzer analyzer;
 * auto result = analyzer.analyzeDecision(
 *     "Compra de Computadora",
 *     {{"MacBook Air", "Portátil M2"}, {"Dell XPS", "Profesional"}},
 *     {{"Precio", 7}, {"Potencia", 8}}
 * );
 * std::cout << result.recommendation << "\n";
 * @endcode
 */

#pragma once

#include <string>
#include <vector>
#include <map>
#include <memory>
#include <cstdlib>
#include <fstream>
#include <sstream>
#include <iostream>
#include <chrono>

namespace AIIntegration {

/**
 * @struct AIAnalysisResult
 * @brief Resultado del análisis con Deep Research Pro
 */
struct AIAnalysisResult {
    bool success = false;                    ///< ¿Análisis completó exitosamente?
    std::string recommendation;              ///< Recomendación principal
    std::string full_analysis;               ///< Análisis completo
    std::map<std::string, double> scores;    ///< Puntuaciones por opción
    std::string error_message;               ///< Mensaje de error (si aplica)
    int analysis_time_seconds = 0;           ///< Tiempo que tardó (segundos)
};

/**
 * @class AIAnalyzer
 * @brief Analizador usando Google's Deep Research Pro
 * 
 * Integra Google's Deep Research Pro para proporcionar análisis profundos
 * de decisiones, complementando las metodologías del framework.
 */
class AIAnalyzer {
public:
    /// Constructor
    AIAnalyzer() 
        : python_script_path_("scripts/deep_research_analyzer.py"),
          timeout_seconds_(600) {}
    
    /**
     * @brief Configura la ruta del script Python
     * 
     * @param path Ruta relativa al script deep_research_analyzer.py
     * 
     * @code
     * analyzer.setPythonScriptPath("../scripts/deep_research_analyzer.py");
     * @endcode
     */
    void setPythonScriptPath(const std::string& path) {
        python_script_path_ = path;
    }
    
    /**
     * @brief Configura timeout máximo
     * 
     * @param seconds Máximo de segundos a esperar (default: 600 = 10 min)
     * 
     * Deep Research Pro típicamente tarda 3-5 minutos
     */
    void setTimeoutSeconds(int seconds) {
        timeout_seconds_ = seconds;
    }
    
    /**
     * @brief Analiza una decisión usando Deep Research Pro
     * 
     * @param decision_name Nombre de la decisión (ej: "Comprar Laptop")
     * @param options Map de {nombre_opcion: descripcion}
     * @param criteria Map de {criterio: importancia_0_a_10}
     * @param use_fast_model Si es true, usa gemini-2.5-pro (rápido); 
     *                       si es false, usa deep-research-pro (profundo)
     * 
     * @return AIAnalysisResult con recomendación y análisis
     * 
     * @code
     * AIAnalyzer analyzer;
     * auto result = analyzer.analyzeDecision(
     *     "Compra de Computadora",
     *     {
     *         {"MacBook Air M2", "Portátil, M2, 256GB"},
     *         {"Dell XPS 13", "Profesional, OLED"}
     *     },
     *     {
     *         {"Portabilidad", 8},
     *         {"Potencia", 7},
     *         {"Precio", 6}
     *     },
     *     false  // Usar Deep Research (no rápido)
     * );
     * 
     * if (result.success) {
     *     std::cout << result.recommendation << "\n";
     * }
     * @endcode
     */
    AIAnalysisResult analyzeDecision(
        const std::string& decision_name,
        const std::map<std::string, std::string>& options,
        const std::map<std::string, int>& criteria,
        bool use_fast_model = false
    ) {
        auto start_time = std::chrono::steady_clock::now();
        
        // Crear archivo JSON con la solicitud
        std::string json_request = buildJsonRequest(
            decision_name, 
            options, 
            criteria,
            use_fast_model
        );
        
        // Ejecutar script Python
        std::string result_text = executePythonScript(json_request);
        
        auto end_time = std::chrono::steady_clock::now();
        int elapsed_seconds = std::chrono::duration_cast<std::chrono::seconds>(
            end_time - start_time
        ).count();
        
        // Parsear resultado
        AIAnalysisResult result;
        result.analysis_time_seconds = elapsed_seconds;
        result.full_analysis = result_text;
        result.success = !result_text.empty() && 
                        result_text.find("Error") == std::string::npos;
        
        if (!result.success) {
            result.error_message = result_text;
        } else {
            // Extraer recomendación (primera línea después de "RECOMENDACIÓN")
            size_t rec_pos = result_text.find("RECOMENDACIÓN");
            if (rec_pos != std::string::npos) {
                size_t start = result_text.find('\n', rec_pos) + 1;
                size_t end = result_text.find('\n', start);
                result.recommendation = result_text.substr(start, end - start);
            }
        }
        
        return result;
    }
    
    /**
     * @brief Analiza rápidamente con Gemini 2.5 Pro (1-2 minutos)
     * 
     * Para decisiones que no requieren investigación profunda.
     * Usa gemini-2.5-pro en lugar de deep-research-pro.
     */
    AIAnalysisResult analyzeDecisionQuick(
        const std::string& decision_name,
        const std::map<std::string, std::string>& options,
        const std::map<std::string, int>& criteria
    ) {
        return analyzeDecision(decision_name, options, criteria, true);
    }
    
    /**
     * @brief Analiza profundamente con Deep Research Pro (3-5 minutos)
     * 
     * Para decisiones complejas que requieren investigación exhaustiva.
     * Retorna análisis mucho más detallado que versión rápida.
     */
    AIAnalysisResult analyzeDecisionDeep(
        const std::string& decision_name,
        const std::map<std::string, std::string>& options,
        const std::map<std::string, int>& criteria
    ) {
        return analyzeDecision(decision_name, options, criteria, false);
    }
    
    /**
     * @brief Analiza una pregunta libre con Deep Research Pro
     * 
     * Para preguntas que no encajan en el patrón de decisión estándar.
     * 
     * @param question Pregunta a investigar
     * @return Resultado de la investigación
     */
    AIAnalysisResult analyzeQuestion(const std::string& question) {
        auto start_time = std::chrono::steady_clock::now();
        
        std::string result_text = executeCustomQuestion(question);
        
        auto end_time = std::chrono::steady_clock::now();
        int elapsed_seconds = std::chrono::duration_cast<std::chrono::seconds>(
            end_time - start_time
        ).count();
        
        AIAnalysisResult result;
        result.analysis_time_seconds = elapsed_seconds;
        result.full_analysis = result_text;
        result.success = !result_text.empty();
        
        return result;
    }

private:
    std::string python_script_path_;
    int timeout_seconds_;
    
    /**
     * @brief Construye JSON con la solicitud de análisis
     */
    std::string buildJsonRequest(
        const std::string& decision_name,
        const std::map<std::string, std::string>& options,
        const std::map<std::string, int>& criteria,
        bool use_fast_model
    ) {
        std::ostringstream json;
        json << "{\n";
        json << "  \"decision_name\": \"" << escapeJson(decision_name) << "\",\n";
        json << "  \"model\": \"" << (use_fast_model ? "gemini-2.5-pro" : "deep-research-pro-preview-12-2025") << "\",\n";
        json << "  \"options\": {\n";
        
        bool first = true;
        for (const auto& [name, desc] : options) {
            if (!first) json << ",\n";
            json << "    \"" << escapeJson(name) << "\": \"" << escapeJson(desc) << "\"";
            first = false;
        }
        
        json << "\n  },\n";
        json << "  \"criteria\": {\n";
        
        first = true;
        for (const auto& [crit, importance] : criteria) {
            if (!first) json << ",\n";
            json << "    \"" << escapeJson(crit) << "\": " << importance;
            first = false;
        }
        
        json << "\n  }\n";
        json << "}\n";
        
        return json.str();
    }
    
    /**
     * @brief Ejecuta el script Python con JSON request
     */
    std::string executePythonScript(const std::string& json_request) {
        // Guardar JSON en archivo temporal
        std::string temp_file = "tmp_decision_request.json";
        {
            std::ofstream file(temp_file);
            file << json_request;
        }
        
        // Ejecutar: uv run script.py < temp_file
        std::string cmd = "uv run " + python_script_path_ + " < " + temp_file + " 2>&1";
        
        std::string result;
        FILE* pipe = popen(cmd.c_str(), "r");
        if (!pipe) {
            return "Error: Could not execute Python script";
        }
        
        char buffer[1024];
        while (fgets(buffer, sizeof(buffer), pipe)) {
            result += buffer;
        }
        
        pclose(pipe);
        
        // Limpiar archivo temporal
        std::remove(temp_file.c_str());
        
        return result;
    }
    
    /**
     * @brief Ejecuta pregunta libre con Deep Research Pro
     */
    std::string executeCustomQuestion(const std::string& question) {
        // Usar script Python para ejecutar pregunta directa
        std::string cmd = "python -c \"" + escapeShell(question) + "\" 2>&1";
        
        std::string result;
        FILE* pipe = popen(cmd.c_str(), "r");
        if (!pipe) {
            return "Error: Could not execute query";
        }
        
        char buffer[1024];
        while (fgets(buffer, sizeof(buffer), pipe)) {
            result += buffer;
        }
        
        pclose(pipe);
        return result;
    }
    
    /**
     * @brief Escapa caracteres especiales para JSON
     */
    std::string escapeJson(const std::string& str) {
        std::ostringstream escaped;
        for (char c : str) {
            switch (c) {
                case '"': escaped << "\\\""; break;
                case '\\': escaped << "\\\\"; break;
                case '\b': escaped << "\\b"; break;
                case '\f': escaped << "\\f"; break;
                case '\n': escaped << "\\n"; break;
                case '\r': escaped << "\\r"; break;
                case '\t': escaped << "\\t"; break;
                default:
                    if (static_cast<unsigned char>(c) < 0x20) {
                        escaped << "\\u" << std::hex << std::setw(4) 
                               << std::setfill('0') << static_cast<int>(c);
                    } else {
                        escaped << c;
                    }
            }
        }
        return escaped.str();
    }
    
    /**
     * @brief Escapa caracteres especiales para shell
     */
    std::string escapeShell(const std::string& str) {
        std::ostringstream escaped;
        for (char c : str) {
            if (c == '"' || c == '\\' || c == '$' || c == '`') {
                escaped << '\\';
            }
            escaped << c;
        }
        return escaped.str();
    }
};

} // namespace AIIntegration
