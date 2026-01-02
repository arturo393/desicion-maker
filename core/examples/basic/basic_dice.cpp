#include "../src/core/MonteCarloEngine.h"
#include "../src/distributions/Distributions.h"
#include <iostream>
#include <memory>

using namespace DecisionMaker;

/**
 * @brief Ejemplo básico: Simulación de lanzamiento de dados
 * 
 * Este ejemplo muestra los conceptos fundamentales del framework:
 * - Crear distribuciones
 * - Configurar un motor Monte Carlo
 * - Ejecutar simulaciones simples
 * - Analizar resultados básicos
 */

// Escenario simple: suma de dos dados
class DiceRollScenario : public DecisionScenario {
public:
    DiceRollScenario() : DecisionScenario("Lanzamiento de Dados", 
                                         "Simula la suma de dos dados de 6 caras") {
        // Los dados son distribuciones discretas uniformes (1-6)
        std::vector<double> dice_values = {1, 2, 3, 4, 5, 6};
        std::vector<double> dice_probs = {1.0/6, 1.0/6, 1.0/6, 1.0/6, 1.0/6, 1.0/6};
        
        parameters_.setDistribution("dice1", 
            std::make_unique<DiscreteDistribution>(dice_values, dice_probs));
        parameters_.setDistribution("dice2", 
            std::make_unique<DiscreteDistribution>(dice_values, dice_probs));
    }
    
    SimulationResult runSimulation(std::mt19937& rng) const override {
        // Obtener las distribuciones
        const auto* dice1_dist = parameters_.getDistribution("dice1");
        const auto* dice2_dist = parameters_.getDistribution("dice2");
        
        // Lanzar los dados
        double roll1 = dice1_dist->sample(rng);
        double roll2 = dice2_dist->sample(rng);
        double sum = roll1 + roll2;
        
        // Crear resultado
        SimulationResult result(sum, true);
        
        // Agregar métricas adicionales
        result.metrics["dice1"] = roll1;
        result.metrics["dice2"] = roll2;
        result.metrics["is_seven"] = (sum == 7.0) ? 1.0 : 0.0;
        result.metrics["is_double"] = (roll1 == roll2) ? 1.0 : 0.0;
        
        return result;
    }
    
    bool validateConfiguration() const override {
        return parameters_.hasParameter("dice1") && 
               parameters_.hasParameter("dice2");
    }
    
    std::vector<std::string> getRequiredParameters() const override {
        return {"dice1", "dice2"};
    }
    
    std::vector<std::string> getProducedMetrics() const override {
        return {"dice1", "dice2", "is_seven", "is_double"};
    }
};

int main() {
    std::cout << "=== Decision Maker Framework - Ejemplo Básico: Dados ===\n\n";
    
    try {
        // 1. Crear el escenario
        std::cout << "📋 Creando escenario de lanzamiento de dados...\n";
        DiceRollScenario scenario;
        
        // 2. Configurar el motor Monte Carlo
        std::cout << "⚙️  Configurando motor Monte Carlo...\n";
        MonteCarloEngine engine(10000); // 10,000 simulaciones
        
        // 3. Ejecutar la simulación
        std::cout << "🎲 Ejecutando simulación...\n";
        auto results = engine.simulate(scenario);
        
        // 4. Analizar resultados básicos
        std::cout << "\n=== RESULTADOS ===\n";
        std::cout << "Simulaciones ejecutadas: " << results.getTotalSimulations() << "\n";
        std::cout << "Suma promedio: " << std::fixed << std::setprecision(2) 
                  << results.getMean() << "\n";
        std::cout << "Desviación estándar: " << results.getStandardDeviation() << "\n";
        std::cout << "Suma mínima: " << results.getMin() << "\n";
        std::cout << "Suma máxima: " << results.getMax() << "\n\n";
        
        // 5. Analizar métricas específicas
        std::cout << "=== MÉTRICAS ESPECÍFICAS ===\n";
        
        auto seven_stats = results.getMetricStats("is_seven");
        std::cout << "Probabilidad de sacar 7: " 
                  << std::setprecision(3) << seven_stats.mean * 100 << "%\n";
        
        auto double_stats = results.getMetricStats("is_double");
        std::cout << "Probabilidad de dobles: " 
                  << double_stats.mean * 100 << "%\n\n";
        
        // 6. Mostrar distribución de resultados
        std::cout << "=== DISTRIBUCIÓN DE SUMAS ===\n";
        
        // Contar frecuencias manualmente para mostrar
        std::map<int, int> frequency;
        for (const auto& result : results.getResults()) {
            int sum = static_cast<int>(result.outcome);
            frequency[sum]++;
        }
        
        for (const auto& [sum, count] : frequency) {
            double percentage = (double)count / results.getTotalSimulations() * 100;
            std::cout << "Suma " << sum << ": " << std::setw(6) << count 
                      << " veces (" << std::setprecision(2) << percentage << "%)\n";
        }
        
        // 7. Verificar teoría vs práctica
        std::cout << "\n=== VERIFICACIÓN TEÓRICA ===\n";
        std::cout << "Suma teórica esperada: 7.00 (promedio de 2 dados)\n";
        std::cout << "Suma obtenida: " << std::setprecision(2) << results.getMean() << "\n";
        std::cout << "Diferencia: " << std::abs(results.getMean() - 7.0) << "\n\n";
        
        std::cout << "Probabilidad teórica de 7: 16.67% (6 formas de hacerlo)\n";
        std::cout << "Probabilidad obtenida: " << seven_stats.mean * 100 << "%\n";
        std::cout << "Diferencia: " << std::abs(seven_stats.mean - (6.0/36.0)) * 100 << "%\n\n";
        
        std::cout << "Probabilidad teórica de dobles: 16.67% (6 dobles posibles)\n";
        std::cout << "Probabilidad obtenida: " << double_stats.mean * 100 << "%\n";
        std::cout << "Diferencia: " << std::abs(double_stats.mean - (6.0/36.0)) * 100 << "%\n\n";
        
        // 8. Generar reporte simple
        std::cout << "📄 Generando reporte...\n";
        std::cout << results.getSummary() << "\n";
        
        // 9. Exportar datos para análisis posterior
        results.exportToCSV("resultados_dados.csv");
        std::cout << "📊 Datos exportados a: resultados_dados.csv\n";
        
    } catch (const std::exception& e) {
        std::cerr << "❌ Error: " << e.what() << std::endl;
        return 1;
    }
    
    std::cout << "\n🎉 ¡Simulación completada!\n";
    std::cout << "Acabas de ver cómo funciona el framework Decision Maker.\n";
    std::cout << "Próximo paso: prueba examples/simple_decision.cpp\n";
    
    return 0;
}