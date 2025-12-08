#ifndef DECISION_FRAMEWORK_H
#define DECISION_FRAMEWORK_H

#include <string>
#include <vector>
#include <map>
#include <memory>

/**
 * @file decision_framework.h
 * @brief Framework genérico para tomar decisiones con validación cruzada
 * 
 * Este framework proporciona una estructura reutilizable para:
 * - Definir opciones de decisión
 * - Aplicar múltiples metodologías
 * - Validar resultados de forma cruzada
 * - Reportar con confianza cuantificada
 * 
 * Caso de uso: Sillón La Florida, Compra/Venta Computador, etc.
 */

namespace decision {

// ============================================================================
// TIPOS DE DATOS GENÉRICOS
// ============================================================================

/**
 * @struct Option
 * @brief Representa una opción de decisión
 */
struct Option {
    std::string name;           // "BOTAR", "RESTAURAR", etc
    std::string description;    // Descripción detallada
    double estimated_cost;      // Costo en dinero
    double estimated_benefit;   // Beneficio esperado
    int time_days;             // Tiempo en días
    
    Option() : estimated_cost(0), estimated_benefit(0), time_days(0) {}
    Option(const std::string& n, const std::string& d = "")
        : name(n), description(d), estimated_cost(0), estimated_benefit(0), time_days(0) {}
};

/**
 * @struct AnalysisResult
 * @brief Resultado de una metodología individual
 */
struct AnalysisResult {
    std::string methodology_name;    // "Real-Time Monitor", "ML Predictor", etc
    std::string recommended_option;  // Opción recomendada
    double confidence;              // 0.0 a 1.0 (0% a 100%)
    std::string reasoning;          // Explicación del resultado
    std::map<std::string, double> scores;  // Puntuaciones por opción
    
    AnalysisResult() : confidence(0.0) {}
    AnalysisResult(const std::string& m) 
        : methodology_name(m), confidence(0.0) {}
};

/**
 * @struct DecisionReport
 * @brief Reporte final de decisión
 */
struct DecisionReport {
    std::string decision_title;                          // "Sillón La Florida", etc
    std::string final_recommendation;                    // Opción ganadora
    double final_confidence;                             // Confianza 0-1
    int methodologies_count;                             // Cuántos concordaron
    std::vector<AnalysisResult> all_results;             // Todos los análisis
    std::map<std::string, double> option_confidence;     // Confianza por opción
    std::string executive_summary;                       // Resumen ejecutivo
    
    DecisionReport() : final_confidence(0.0), methodologies_count(0) {}
};

// ============================================================================
// CLASE BASE: METODOLOGÍA
// ============================================================================

/**
 * @class Methodology
 * @brief Interfaz base para cualquier metodología de análisis
 * 
 * Ejemplo de implementación:
 * - RealTimeMonitor
 * - BayesianUpdater
 * - ScenarioAnalysis
 * - MLDemandPredictor
 * - ValueAtRiskAnalyzer
 */
class Methodology {
public:
    virtual ~Methodology() = default;
    
    /**
     * @brief Realiza el análisis
     * @param options Opciones a evaluar
     * @return Resultado del análisis
     */
    virtual AnalysisResult analyze(const std::vector<Option>& options) = 0;
    
    /**
     * @brief Nombre de la metodología
     */
    virtual std::string get_name() const = 0;
    
    /**
     * @brief Descripción breve
     */
    virtual std::string get_description() const = 0;
    
    /**
     * @brief Confianza base de esta metodología (0-1)
     */
    virtual double get_base_confidence() const { return 0.85; }
};

// ============================================================================
// FRAMEWORK PRINCIPAL
// ============================================================================

/**
 * @class DecisionFramework
 * @brief Framework para decisiones con validación cruzada
 * 
 * Uso:
 * @code
 * DecisionFramework framework("Sillón La Florida");
 * 
 * // Agregar opciones
 * framework.add_option(Option("BOTAR", "Desechar", 7500, 0, 5));
 * framework.add_option(Option("RESTAURAR", "Restaurar", 175000, 45000, 84));
 * 
 * // Agregar metodologías
 * framework.add_methodology(std::make_unique<RealTimeMonitor>());
 * framework.add_methodology(std::make_unique<BayesianUpdater>());
 * framework.add_methodology(std::make_unique<MLDemandPredictor>());
 * 
 * // Ejecutar análisis
 * auto report = framework.analyze();
 * 
 * // Mostrar resultado
 * std::cout << report.final_recommendation << " (Confianza: " 
 *           << report.final_confidence * 100 << "%)\n";
 * @endcode
 */
class DecisionFramework {
private:
    std::string decision_title_;
    std::vector<Option> options_;
    std::vector<std::unique_ptr<Methodology>> methodologies_;
    
public:
    /**
     * @brief Constructor
     * @param title Título de la decisión (ej: "Sillón La Florida")
     */
    explicit DecisionFramework(const std::string& title);
    
    /**
     * @brief Agregar opción a evaluar
     */
    void add_option(const Option& option);
    
    /**
     * @brief Agregar metodología de análisis
     */
    void add_methodology(std::unique_ptr<Methodology> methodology);
    
    /**
     * @brief Ejecutar análisis completo con validación cruzada
     * @return Reporte final con recomendación
     */
    DecisionReport analyze();
    
    /**
     * @brief Obtener opciones registradas
     */
    const std::vector<Option>& get_options() const { return options_; }
    
    /**
     * @brief Obtener cantidad de metodologías
     */
    size_t get_methodology_count() const { return methodologies_.size(); }
    
    /**
     * @brief Generar reporte en formato markdown
     */
    std::string generate_markdown_report(const DecisionReport& report) const;
    
    /**
     * @brief Generar reporte en formato texto simple
     */
    std::string generate_text_report(const DecisionReport& report) const;
};

// ============================================================================
// UTILIDADES
// ============================================================================

/**
 * @brief Calcular confianza final basada en consenso
 * @param results Todos los resultados de análisis
 * @param recommended_option Opción recomendada
 * @return Confianza 0-1
 */
double calculate_consensus_confidence(
    const std::vector<AnalysisResult>& results,
    const std::string& recommended_option
);

/**
 * @brief Encontrar opción más recomendada
 * @param results Todos los resultados
 * @return Nombre de opción con más votos
 */
std::string find_consensus_option(const std::vector<AnalysisResult>& results);

/**
 * @brief Convertir confianza a porcentaje
 */
inline int confidence_to_percentage(double confidence) {
    return static_cast<int>(confidence * 100);
}

} // namespace decision

#endif // DECISION_FRAMEWORK_H
