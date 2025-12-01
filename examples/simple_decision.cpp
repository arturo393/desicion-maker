#include "../src/core/MonteCarloEngine.h"
#include "../src/distributions/Distributions.h"
#include "../src/utils/Analysis.h"
#include <iostream>

using namespace DecisionMaker;
using namespace DecisionMaker::Utils;

/**
 * @brief Ejemplo de decisión simple: ¿Llevar paraguas o no?
 * 
 * Escenario: Tienes que decidir si llevar paraguas considerando:
 * - Probabilidad de lluvia (incierta)
 * - Costo de mojarse si llueve
 * - Incomodidad de cargar paraguas
 * - Probabilidad de olvidar el paraguas
 */

class UmbrellaDecisionScenario : public DecisionScenario {
public:
    UmbrellaDecisionScenario() : DecisionScenario("Decisión del Paraguas", 
                                                 "¿Llevar paraguas o arriesgarse?") {}
    
    SimulationResult runSimulation(std::mt19937& rng) const override {
        // Obtener parámetros
        bool carry_umbrella = parameters_.getValue<bool>("carry_umbrella");
        const auto* rain_prob_dist = parameters_.getDistribution("rain_probability");
        const auto* rain_intensity_dist = parameters_.getDistribution("rain_intensity");
        
        // Simular si llueve
        double rain_prob = rain_prob_dist->sample(rng);
        std::uniform_real_distribution<double> uniform(0.0, 1.0);
        bool rains = uniform(rng) < rain_prob;
        
        double total_cost = 0.0;
        double discomfort = 0.0;
        
        if (carry_umbrella) {
            // Costo base de cargar paraguas
            discomfort += parameters_.getValue<double>("umbrella_inconvenience");
            
            // Probabilidad de olvidar el paraguas
            double forget_prob = parameters_.getValue<double>("forget_probability");
            bool forgets_umbrella = uniform(rng) < forget_prob;
            
            if (rains) {
                if (forgets_umbrella) {
                    // Llueve y olvidó el paraguas - peor escenario
                    double rain_intensity = rain_intensity_dist->sample(rng);
                    total_cost = parameters_.getValue<double>("getting_wet_cost") * rain_intensity;
                    discomfort += total_cost * 1.5; // Extra frustración por haber traído paraguas
                } else {
                    // Llueve y tiene paraguas - éxito
                    total_cost = 0.0;
                    discomfort += 0.0; // Se siente bien por haber traído paraguas
                }
            } else {
                // No llueve pero cargó paraguas innecesariamente
                discomfort += parameters_.getValue<double>("unnecessary_burden");
            }
        } else {
            // No trae paraguas
            if (rains) {
                // Llueve y no tiene paraguas
                double rain_intensity = rain_intensity_dist->sample(rng);
                total_cost = parameters_.getValue<double>("getting_wet_cost") * rain_intensity;
                discomfort += total_cost;
            }
            // Si no llueve y no trae paraguas, perfecto (costo = 0)
        }
        
        // Calcular utilidad total (negativa porque queremos minimizar costos)
        double total_utility = -(total_cost + discomfort);
        
        // Determinar si fue una buena decisión
        bool good_decision = total_utility > -5.0; // Umbral arbitrario
        
        SimulationResult result(total_utility, good_decision);
        result.metrics["rained"] = rains ? 1.0 : 0.0;
        result.metrics["total_cost"] = total_cost;
        result.metrics["discomfort"] = discomfort;
        result.metrics["carried_umbrella"] = carry_umbrella ? 1.0 : 0.0;
        
        return result;
    }
    
    bool validateConfiguration() const override {
        return parameters_.hasParameter("carry_umbrella") && 
               parameters_.hasParameter("rain_probability") &&
               parameters_.hasParameter("rain_intensity") &&
               parameters_.hasParameter("getting_wet_cost") &&
               parameters_.hasParameter("umbrella_inconvenience");
    }
    
    std::vector<std::string> getRequiredParameters() const override {
        return {"carry_umbrella", "rain_probability", "rain_intensity", 
                "getting_wet_cost", "umbrella_inconvenience", "forget_probability", 
                "unnecessary_burden"};
    }
    
    std::vector<std::string> getProducedMetrics() const override {
        return {"rained", "total_cost", "discomfort", "carried_umbrella"};
    }
};

int main() {
    std::cout << "=== Decision Maker Framework - Decisión Simple: Paraguas ===\n\n";
    
    try {
        // Configurar parámetros del entorno
        std::cout << "🌤️  Configurando condiciones del clima...\n";
        
        // Crear distribuciones para modelar incertidumbre
        auto rain_probability = std::make_unique<UniformDistribution>(0.2, 0.6); // 20-60% prob lluvia
        auto rain_intensity = std::make_unique<TriangularDistribution>(0.1, 1.0, 0.3); // Intensidad variable
        
        // Costos y utilidades
        double getting_wet_cost = 10.0;     // Costo de mojarse (escala 0-20)
        double umbrella_inconvenience = 1.0; // Incomodidad de cargar paraguas
        double forget_probability = 0.1;     // 10% probabilidad de olvidar
        double unnecessary_burden = 0.5;     // Costo de cargar paraguas innecesariamente
        
        MonteCarloEngine engine(25000); // Más simulaciones para mayor precisión
        
        // === ESCENARIO 1: LLEVAR PARAGUAS ===
        std::cout << "🌂 Simulando: LLEVAR PARAGUAS...\n";
        
        UmbrellaDecisionScenario scenario_with_umbrella;
        scenario_with_umbrella.getParameters().setValue("carry_umbrella", true);
        scenario_with_umbrella.getParameters().setDistribution("rain_probability", 
            rain_probability->clone());
        scenario_with_umbrella.getParameters().setDistribution("rain_intensity", 
            rain_intensity->clone());
        scenario_with_umbrella.getParameters().setValue("getting_wet_cost", getting_wet_cost);
        scenario_with_umbrella.getParameters().setValue("umbrella_inconvenience", umbrella_inconvenience);
        scenario_with_umbrella.getParameters().setValue("forget_probability", forget_probability);
        scenario_with_umbrella.getParameters().setValue("unnecessary_burden", unnecessary_burden);
        
        auto results_with = engine.simulate(scenario_with_umbrella);
        
        // === ESCENARIO 2: NO LLEVAR PARAGUAS ===
        std::cout << "☀️ Simulando: NO LLEVAR PARAGUAS...\n";
        
        UmbrellaDecisionScenario scenario_without_umbrella;
        scenario_without_umbrella.getParameters().setValue("carry_umbrella", false);
        scenario_without_umbrella.getParameters().setDistribution("rain_probability", 
            rain_probability->clone());
        scenario_without_umbrella.getParameters().setDistribution("rain_intensity", 
            rain_intensity->clone());
        scenario_without_umbrella.getParameters().setValue("getting_wet_cost", getting_wet_cost);
        scenario_without_umbrella.getParameters().setValue("umbrella_inconvenience", umbrella_inconvenience);
        scenario_without_umbrella.getParameters().setValue("forget_probability", forget_probability);
        scenario_without_umbrella.getParameters().setValue("unnecessary_burden", unnecessary_burden);
        
        auto results_without = engine.simulate(scenario_without_umbrella);
        
        // === COMPARACIÓN DE RESULTADOS ===
        std::cout << "\n=== COMPARACIÓN DE ESTRATEGIAS ===\n\n";
        
        ScenarioComparator comparator;
        comparator.addScenario("Con Paraguas", results_with);
        comparator.addScenario("Sin Paraguas", results_without);
        comparator.rankScenarios("mean", false); // Mayor utilidad es mejor
        
        std::cout << comparator.generateReport() << "\n";
        
        // === ANÁLISIS DETALLADO ===
        std::cout << "=== ANÁLISIS DETALLADO ===\n\n";
        
        // Con paraguas
        std::cout << "CON PARAGUAS:\n";
        std::cout << "• Utilidad promedio: " << std::fixed << std::setprecision(2) 
                  << results_with.getMean() << "\n";
        std::cout << "• Probabilidad decisión exitosa: " 
                  << std::setprecision(1) << results_with.getSuccessProbability() * 100 << "%\n";
        std::cout << "• Desviación estándar: " << std::setprecision(2) 
                  << results_with.getStandardDeviation() << "\n";
        
        auto rain_stats_with = results_with.getMetricStats("rained");
        std::cout << "• Días que llovió: " << std::setprecision(1) 
                  << rain_stats_with.mean * 100 << "%\n";
        
        auto cost_stats_with = results_with.getMetricStats("total_cost");
        std::cout << "• Costo promedio: " << std::setprecision(2) 
                  << cost_stats_with.mean << "\n\n";
        
        // Sin paraguas
        std::cout << "SIN PARAGUAS:\n";
        std::cout << "• Utilidad promedio: " << std::fixed << std::setprecision(2) 
                  << results_without.getMean() << "\n";
        std::cout << "• Probabilidad decisión exitosa: " 
                  << std::setprecision(1) << results_without.getSuccessProbability() * 100 << "%\n";
        std::cout << "• Desviación estándar: " << std::setprecision(2) 
                  << results_without.getStandardDeviation() << "\n";
        
        auto rain_stats_without = results_without.getMetricStats("rained");
        std::cout << "• Días que llovió: " << std::setprecision(1) 
                  << rain_stats_without.mean * 100 << "%\n";
        
        auto cost_stats_without = results_without.getMetricStats("total_cost");
        std::cout << "• Costo promedio: " << std::setprecision(2) 
                  << cost_stats_without.mean << "\n\n";
        
        // === RECOMENDACIÓN ===
        std::cout << "=== RECOMENDACIÓN ===\n";
        
        if (results_with.getMean() > results_without.getMean()) {
            double advantage = results_with.getMean() - results_without.getMean();
            std::cout << "✅ RECOMENDACIÓN: LLEVAR PARAGUAS\n";
            std::cout << "• Ventaja en utilidad: " << std::setprecision(2) << advantage << "\n";
            std::cout << "• Menor variabilidad en resultados\n";
            std::cout << "• Protección contra escenarios adversos\n";
        } else {
            double advantage = results_without.getMean() - results_with.getMean();
            std::cout << "✅ RECOMENDACIÓN: NO LLEVAR PARAGUAS\n";
            std::cout << "• Ventaja en utilidad: " << std::setprecision(2) << advantage << "\n";
            std::cout << "• Menor molestia cuando no llueve\n";
            std::cout << "• Mayor libertad de movimiento\n";
        }
        
        // === ANÁLISIS DE SENSIBILIDAD ===
        std::cout << "\n=== ANÁLISIS DE SENSIBILIDAD ===\n";
        std::cout << "¿Cómo cambia la decisión si cambian los parámetros?\n\n";
        
        // Probar diferentes costos de mojarse
        std::vector<double> wet_costs = {5.0, 10.0, 15.0, 20.0};
        std::cout << "Costo de mojarse vs Mejor estrategia:\n";
        
        for (double cost : wet_costs) {
            // Simular rápidamente con menos iteraciones
            MonteCarloEngine quick_engine(1000);
            
            // Con paraguas
            UmbrellaDecisionScenario test_with;
            test_with.getParameters().setValue("carry_umbrella", true);
            test_with.getParameters().setDistribution("rain_probability", 
                rain_probability->clone());
            test_with.getParameters().setDistribution("rain_intensity", 
                rain_intensity->clone());
            test_with.getParameters().setValue("getting_wet_cost", cost);
            test_with.getParameters().setValue("umbrella_inconvenience", umbrella_inconvenience);
            test_with.getParameters().setValue("forget_probability", forget_probability);
            test_with.getParameters().setValue("unnecessary_burden", unnecessary_burden);
            
            auto test_results_with = quick_engine.simulate(test_with);
            
            // Sin paraguas
            UmbrellaDecisionScenario test_without;
            test_without.getParameters().setValue("carry_umbrella", false);
            test_without.getParameters().setDistribution("rain_probability", 
                rain_probability->clone());
            test_without.getParameters().setDistribution("rain_intensity", 
                rain_intensity->clone());
            test_without.getParameters().setValue("getting_wet_cost", cost);
            test_without.getParameters().setValue("umbrella_inconvenience", umbrella_inconvenience);
            test_without.getParameters().setValue("forget_probability", forget_probability);
            test_without.getParameters().setValue("unnecessary_burden", unnecessary_burden);
            
            auto test_results_without = quick_engine.simulate(test_without);
            
            std::string better = (test_results_with.getMean() > test_results_without.getMean()) ? 
                               "Con paraguas" : "Sin paraguas";
            
            std::cout << "• Costo $" << cost << " → " << better << "\n";
        }
        
        // Exportar resultados
        std::cout << "\n📊 Exportando resultados...\n";
        results_with.exportToCSV("paraguas_con.csv");
        results_without.exportToCSV("paraguas_sin.csv");
        comparator.exportToCSV("comparacion_paraguas.csv");
        
    } catch (const std::exception& e) {
        std::cerr << "❌ Error: " << e.what() << std::endl;
        return 1;
    }
    
    std::cout << "\n🎉 ¡Análisis completado!\n";
    std::cout << "Has visto cómo usar Monte Carlo para decisiones cotidianas.\n";
    std::cout << "El framework puede aplicarse a cualquier decisión con incertidumbre.\n";
    
    return 0;
}