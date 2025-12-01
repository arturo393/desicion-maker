#pragma once

#include "../core/Scenario.h"
#include <vector>
#include <string>
#include <map>

namespace DecisionMaker {
namespace Utils {

/**
 * @brief Clase para análisis estadístico avanzado de resultados
 */
class StatisticalAnalyzer {
public:
    /**
     * @brief Calcula el Value at Risk (VaR)
     * @param results Resultados de la simulación
     * @param confidence_level Nivel de confianza (ej: 0.95)
     * @return Valor en riesgo
     */
    static double calculateVaR(const SimulationResults& results, double confidence_level);
    
    /**
     * @brief Calcula el Conditional Value at Risk (CVaR)
     * @param results Resultados de la simulación
     * @param confidence_level Nivel de confianza
     * @return Valor condicional en riesgo
     */
    static double calculateCVaR(const SimulationResults& results, double confidence_level);
    
    /**
     * @brief Calcula el coeficiente de Sharpe
     * @param results Resultados de la simulación
     * @param risk_free_rate Tasa libre de riesgo
     * @return Ratio de Sharpe
     */
    static double calculateSharpeRatio(const SimulationResults& results, double risk_free_rate);
    
    /**
     * @brief Calcula la curtosis de los resultados
     * @param results Resultados de la simulación
     * @return Curtosis
     */
    static double calculateKurtosis(const SimulationResults& results);
    
    /**
     * @brief Calcula la asimetría (skewness) de los resultados
     * @param results Resultados de la simulación
     * @return Asimetría
     */
    static double calculateSkewness(const SimulationResults& results);
    
    /**
     * @brief Realiza test de normalidad Jarque-Bera
     * @param results Resultados de la simulación
     * @return p-value del test
     */
    static double jarqueBeraTest(const SimulationResults& results);
    
    /**
     * @brief Calcula intervalos de confianza
     * @param results Resultados de la simulación
     * @param confidence_level Nivel de confianza
     * @return Par (límite_inferior, límite_superior)
     */
    static std::pair<double, double> calculateConfidenceInterval(
        const SimulationResults& results, double confidence_level);
};

/**
 * @brief Clase para comparar múltiples escenarios
 */
class ScenarioComparator {
public:
    struct ComparisonResult {
        std::string scenario_name;
        double mean;
        double stddev;
        double var_95;
        double success_probability;
        double sharpe_ratio;
        int ranking;
    };
    
private:
    std::vector<ComparisonResult> results_;
    
public:
    /**
     * @brief Agrega un escenario para comparación
     * @param name Nombre del escenario
     * @param results Resultados de la simulación
     * @param risk_free_rate Tasa libre de riesgo para Sharpe ratio
     */
    void addScenario(const std::string& name, 
                    const SimulationResults& results, 
                    double risk_free_rate = 0.0);
    
    /**
     * @brief Rankea los escenarios según criterio
     * @param criteria Criterio de ranking ("mean", "sharpe", "success_prob", "var")
     * @param ascending Orden ascendente si es true
     */
    void rankScenarios(const std::string& criteria, bool ascending = false);
    
    /**
     * @brief Obtiene la comparación completa
     * @return Vector de resultados comparativos
     */
    const std::vector<ComparisonResult>& getComparison() const { return results_; }
    
    /**
     * @brief Genera reporte de comparación
     * @return String con el reporte
     */
    std::string generateReport() const;
    
    /**
     * @brief Exporta comparación a CSV
     * @param filename Nombre del archivo
     */
    void exportToCSV(const std::string& filename) const;
};

/**
 * @brief Generador de visualizaciones simples en texto
 */
class TextVisualizer {
public:
    /**
     * @brief Genera histograma en texto
     * @param results Resultados de la simulación
     * @param bins Número de bins
     * @param width Ancho del histograma
     * @return String con el histograma
     */
    static std::string generateHistogram(const SimulationResults& results, 
                                       int bins = 20, int width = 60);
    
    /**
     * @brief Genera gráfico de línea simple
     * @param values Vector de valores
     * @param labels Vector de etiquetas
     * @param width Ancho del gráfico
     * @return String con el gráfico
     */
    static std::string generateLineChart(const std::vector<double>& values,
                                       const std::vector<std::string>& labels,
                                       int width = 60);
    
    /**
     * @brief Genera gráfico de barras
     * @param values Mapa de etiqueta -> valor
     * @param width Ancho del gráfico
     * @return String con el gráfico
     */
    static std::string generateBarChart(const std::map<std::string, double>& values,
                                      int width = 60);
    
    /**
     * @brief Genera box plot simple
     * @param results Resultados de la simulación
     * @param width Ancho del gráfico
     * @return String con el box plot
     */
    static std::string generateBoxPlot(const SimulationResults& results, int width = 60);
};

/**
 * @brief Generador de reportes completos
 */
class ReportGenerator {
public:
    /**
     * @brief Genera reporte completo de simulación
     * @param scenario Escenario simulado
     * @param results Resultados de la simulación
     * @param include_charts Incluir gráficos de texto
     * @return String con el reporte completo
     */
    static std::string generateFullReport(const DecisionScenario& scenario,
                                        const SimulationResults& results,
                                        bool include_charts = true);
    
    /**
     * @brief Genera reporte ejecutivo resumido
     * @param scenario Escenario simulado
     * @param results Resultados de la simulación
     * @return String con el resumen ejecutivo
     */
    static std::string generateExecutiveSummary(const DecisionScenario& scenario,
                                               const SimulationResults& results);
    
    /**
     * @brief Genera reporte de análisis de riesgo
     * @param scenario Escenario simulado
     * @param results Resultados de la simulación
     * @param risk_free_rate Tasa libre de riesgo
     * @return String con el análisis de riesgo
     */
    static std::string generateRiskAnalysis(const DecisionScenario& scenario,
                                           const SimulationResults& results,
                                           double risk_free_rate = 0.0);
    
    /**
     * @brief Exporta reporte a archivo
     * @param content Contenido del reporte
     * @param filename Nombre del archivo
     * @param format Formato ("txt", "md", "html")
     */
    static void exportReport(const std::string& content,
                           const std::string& filename,
                           const std::string& format = "txt");
};

/**
 * @brief Utilidades para optimización de parámetros
 */
class ParameterOptimizer {
public:
    struct OptimizationResult {
        double best_value;
        std::map<std::string, double> best_parameters;
        std::vector<std::pair<std::map<std::string, double>, double>> all_results;
    };
    
    /**
     * @brief Optimiza parámetros usando grid search
     * @param scenario Escenario base
     * @param engine Motor de Monte Carlo
     * @param parameter_ranges Rangos de parámetros a explorar
     * @param objective_function Función objetivo a optimizar
     * @return Resultado de la optimización
     */
    static OptimizationResult gridSearch(
        DecisionScenario& scenario,
        MonteCarloEngine& engine,
        const std::map<std::string, std::vector<double>>& parameter_ranges,
        std::function<double(const SimulationResults&)> objective_function
    );
    
    /**
     * @brief Optimiza usando búsqueda aleatoria
     * @param scenario Escenario base
     * @param engine Motor de Monte Carlo
     * @param parameter_ranges Rangos de parámetros
     * @param objective_function Función objetivo
     * @param num_iterations Número de iteraciones
     * @return Resultado de la optimización
     */
    static OptimizationResult randomSearch(
        DecisionScenario& scenario,
        MonteCarloEngine& engine,
        const std::map<std::string, std::pair<double, double>>& parameter_ranges,
        std::function<double(const SimulationResults&)> objective_function,
        int num_iterations = 100
    );
};

} // namespace Utils
} // namespace DecisionMaker