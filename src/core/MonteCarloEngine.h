#pragma once

#include "Scenario.h"
#include <functional>
#include <future>
#include <thread>

namespace DecisionMaker {

/**
 * @brief Configuración para el motor de Monte Carlo
 */
struct MonteCarloConfig {
    size_t num_simulations = 10000;     // Número de simulaciones
    size_t num_threads = std::thread::hardware_concurrency(); // Número de hilos
    unsigned int random_seed = std::random_device{}();        // Semilla aleatoria
    bool parallel_execution = true;      // Ejecución en paralelo
    bool verbose = false;               // Salida detallada
    
    // Criterios de convergencia
    bool enable_convergence_check = false;
    double convergence_tolerance = 0.001;
    size_t min_simulations_for_convergence = 1000;
    size_t convergence_check_interval = 100;
};

/**
 * @brief Callback para progreso de simulación
 * Parámetros: simulaciones_completadas, total_simulaciones
 */
using ProgressCallback = std::function<void(size_t, size_t)>;

/**
 * @brief Motor principal de simulaciones Monte Carlo
 * 
 * Maneja la ejecución de simulaciones de forma eficiente,
 * incluyendo procesamiento paralelo y monitoreo de progreso.
 */
class MonteCarloEngine {
private:
    MonteCarloConfig config_;
    ProgressCallback progress_callback_;
    
    /**
     * @brief Ejecuta un lote de simulaciones en un hilo
     * @param scenario Escenario a simular
     * @param num_sims Número de simulaciones en este lote
     * @param seed Semilla para el generador aleatorio
     * @return Resultados del lote
     */
    SimulationResults runBatch(const DecisionScenario& scenario, 
                              size_t num_sims, 
                              unsigned int seed) const;
    
    /**
     * @brief Verifica convergencia de los resultados
     * @param results Resultados actuales
     * @param previous_mean Media anterior
     * @return true si ha convergido
     */
    bool checkConvergence(const SimulationResults& results, double previous_mean) const;
    
public:
    /**
     * @brief Constructor con configuración personalizada
     * @param config Configuración del motor
     */
    explicit MonteCarloEngine(const MonteCarloConfig& config = MonteCarloConfig{});
    
    /**
     * @brief Constructor con número de simulaciones
     * @param num_simulations Número de simulaciones a ejecutar
     */
    explicit MonteCarloEngine(size_t num_simulations);
    
    /**
     * @brief Ejecuta la simulación Monte Carlo
     * @param scenario Escenario de decisión a simular
     * @return Resultados agregados de todas las simulaciones
     */
    SimulationResults simulate(const DecisionScenario& scenario);
    
    /**
     * @brief Ejecuta simulación con callback de progreso
     * @param scenario Escenario a simular
     * @param callback Función callback para progreso
     * @return Resultados de la simulación
     */
    SimulationResults simulate(const DecisionScenario& scenario, 
                              ProgressCallback callback);
    
    /**
     * @brief Establece callback de progreso
     * @param callback Función callback
     */
    void setProgressCallback(ProgressCallback callback) {
        progress_callback_ = std::move(callback);
    }
    
    /**
     * @brief Obtiene la configuración actual
     * @return Configuración del motor
     */
    const MonteCarloConfig& getConfig() const { return config_; }
    
    /**
     * @brief Actualiza la configuración
     * @param config Nueva configuración
     */
    void setConfig(const MonteCarloConfig& config) { config_ = config; }
    
    /**
     * @brief Estima el tiempo de ejecución
     * @param scenario Escenario a simular
     * @param sample_size Tamaño de muestra para estimación
     * @return Tiempo estimado en segundos
     */
    double estimateExecutionTime(const DecisionScenario& scenario, size_t sample_size = 100);
    
    /**
     * @brief Ejecuta análisis de sensibilidad
     * @param scenario Escenario base
     * @param parameter_name Nombre del parámetro a variar
     * @param variations Vector de valores a probar
     * @return Mapa de variación -> resultados
     */
    std::map<double, SimulationResults> sensitivityAnalysis(
        DecisionScenario& scenario,
        const std::string& parameter_name,
        const std::vector<double>& variations
    );
};

/**
 * @brief Clase helper para construir configuraciones
 */
class MonteCarloConfigBuilder {
private:
    MonteCarloConfig config_;
    
public:
    MonteCarloConfigBuilder& withSimulations(size_t num_sims) {
        config_.num_simulations = num_sims;
        return *this;
    }
    
    MonteCarloConfigBuilder& withThreads(size_t num_threads) {
        config_.num_threads = num_threads;
        return *this;
    }
    
    MonteCarloConfigBuilder& withSeed(unsigned int seed) {
        config_.random_seed = seed;
        return *this;
    }
    
    MonteCarloConfigBuilder& withParallelExecution(bool parallel) {
        config_.parallel_execution = parallel;
        return *this;
    }
    
    MonteCarloConfigBuilder& withVerbose(bool verbose) {
        config_.verbose = verbose;
        return *this;
    }
    
    MonteCarloConfigBuilder& withConvergenceCheck(bool enable, 
                                                 double tolerance = 0.001,
                                                 size_t min_sims = 1000) {
        config_.enable_convergence_check = enable;
        config_.convergence_tolerance = tolerance;
        config_.min_simulations_for_convergence = min_sims;
        return *this;
    }
    
    MonteCarloConfig build() const {
        return config_;
    }
};

} // namespace DecisionMaker