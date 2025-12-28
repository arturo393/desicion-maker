#pragma once

#include "Types.h"
#include <vector>
#include <memory>

namespace DecisionMaker {

/**
 * @brief Estructura para almacenar los resultados de una simulación individual
 */
struct SimulationResult {
    double outcome;                          // Resultado principal de la simulación
    std::unordered_map<std::string, double> metrics; // Métricas adicionales
    bool success;                           // Indica si el resultado fue exitoso
    
    SimulationResult(double out = 0.0, bool succ = true) 
        : outcome(out), success(succ) {}
};

/**
 * @brief Contenedor para los resultados agregados de todas las simulaciones
 */
class SimulationResults {
private:
    std::vector<SimulationResult> results_;
    size_t total_simulations_;
    
public:
    explicit SimulationResults(size_t expected_size = 0);
    
    /**
     * @brief Agrega un resultado individual
     * @param result Resultado de la simulación
     */
    void addResult(const SimulationResult& result);
    
    /**
     * @brief Obtiene el número total de simulaciones
     * @return Número de simulaciones ejecutadas
     */
    size_t getTotalSimulations() const { return results_.size(); }
    
    /**
     * @brief Calcula la probabilidad de éxito
     * @return Probabilidad de éxito (0.0 a 1.0)
     */
    double getSuccessProbability() const;
    
    /**
     * @brief Obtiene la media de los resultados
     * @return Valor medio de los outcomes
     */
    double getMean() const;
    
    /**
     * @brief Obtiene la desviación estándar de los resultados
     * @return Desviación estándar de los outcomes
     */
    double getStandardDeviation() const;
    
    /**
     * @brief Obtiene un percentil específico
     * @param percentile Percentil deseado (0.0 a 1.0)
     * @return Valor del percentil
     */
    double getPercentile(double percentile) const;
    
    /**
     * @brief Obtiene el valor mínimo
     * @return Valor mínimo de los outcomes
     */
    double getMin() const;
    
    /**
     * @brief Obtiene el valor máximo
     * @return Valor máximo de los outcomes
     */
    double getMax() const;
    
    /**
     * @brief Obtiene todos los resultados
     * @return Vector con todos los resultados
     */
    const std::vector<SimulationResult>& getResults() const { return results_; }
    
    /**
     * @brief Obtiene estadísticas de una métrica específica
     * @param metric_name Nombre de la métrica
     * @return Estadísticas de la métrica
     */
    struct MetricStats {
        double mean;
        double stddev;
        double min;
        double max;
        size_t count;
    };
    
    MetricStats getMetricStats(const std::string& metric_name) const;
    
    /**
     * @brief Genera un resumen textual de los resultados
     * @return String con el resumen
     */
    std::string getSummary() const;
    
    /**
     * @brief Exporta los resultados a CSV
     * @param filename Nombre del archivo CSV
     */
    void exportToCSV(const std::string& filename) const;
};

/**
 * @brief Clase base abstracta para escenarios de decisión
 * 
 * Define la interfaz que deben implementar todos los escenarios
 * específicos de decisión.
 */
class DecisionScenario {
protected:
    SimulationParameters parameters_;
    std::string name_;
    std::string description_;
    
public:
    explicit DecisionScenario(const std::string& name, const std::string& description = "");
    virtual ~DecisionScenario() = default;
    
    /**
     * @brief Ejecuta una simulación individual
     * @param rng Generador de números aleatorios
     * @return Resultado de la simulación
     */
    virtual SimulationResult runSimulation(std::mt19937& rng) const = 0;
    
    /**
     * @brief Valida que los parámetros necesarios estén configurados
     * @return true si la configuración es válida
     */
    virtual bool validateConfiguration() const = 0;
    
    /**
     * @brief Obtiene los parámetros de simulación
     * @return Referencia a los parámetros
     */
    SimulationParameters& getParameters() { return parameters_; }
    const SimulationParameters& getParameters() const { return parameters_; }
    
    /**
     * @brief Obtiene el nombre del escenario
     * @return Nombre del escenario
     */
    const std::string& getName() const { return name_; }
    
    /**
     * @brief Obtiene la descripción del escenario
     * @return Descripción del escenario
     */
    const std::string& getDescription() const { return description_; }
    
    /**
     * @brief Establece la descripción del escenario
     * @param description Nueva descripción
     */
    void setDescription(const std::string& description) { description_ = description; }
    
    /**
     * @brief Obtiene información sobre los parámetros requeridos
     * @return Vector de nombres de parámetros requeridos
     */
    virtual std::vector<std::string> getRequiredParameters() const = 0;
    
    /**
     * @brief Obtiene información sobre las métricas que produce
     * @return Vector de nombres de métricas
     */
    virtual std::vector<std::string> getProducedMetrics() const { return {}; }
};

} // namespace DecisionMaker