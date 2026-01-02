/**
 * @file refactoring_decision.cpp
 * @brief ¿Completar refactorización FSK/LoRa Opción B?
 * 
 * Contexto:
 * - Líder técnico con ganas de irse
 * - Cultura "salir del paso"
 * - Refactorización 60% completa (punto sin retorno)
 * - 40% pendiente: actualizar FskScanner + main.cpp
 * 
 * Decisión: ¿Vale la pena terminar?
 */

#include "../../src/core/MonteCarloEngine.h"
#include "../../src/distributions/Distributions.h"
#include "../../src/utils/Analysis.h"
#include <iostream>
#include <iomanip>

using namespace DecisionMaker;
using namespace DecisionMaker::Utils;

/**
 * @brief Escenario de decisión de refactorización
 */
class RefactoringDecisionScenario : public DecisionScenario {
public:
    RefactoringDecisionScenario() : DecisionScenario(
        "Refactorización FSK/LoRa", 
        "¿Completar Strategy Pattern o revertir?"
    ) {}
    
    SimulationResult runSimulation(std::mt19937& rng) const override {
        // Obtener parámetros
        std::string decision = parameters_.getValue<std::string>("decision");
        
        // Distribuciones de incertidumbre
        const auto* compilation_risk_dist = parameters_.getDistribution("compilation_risk");
        const auto* learning_value_dist = parameters_.getDistribution("learning_value");
        const auto* reputation_impact_dist = parameters_.getDistribution("reputation_impact");
        
        double total_value = 0.0;
        double time_invested = 0.0;
        double reputation = 0.0;
        double technical_debt = 0.0;
        bool success = true;
        
        std::uniform_real_distribution<double> uniform(0.0, 1.0);
        
        if (decision == "COMPLETE") {
            // === OPCIÓN A: COMPLETAR REFACTORIZACIÓN ===
            time_invested = 2.5; // 2-4 horas promedio
            
            // Riesgo de compilación (15%)
            double compilation_risk = compilation_risk_dist->sample(rng);
            bool compilation_fails = uniform(rng) < compilation_risk;
            
            if (compilation_fails) {
                // Compilación falla - debugging adicional
                time_invested += 1.0; // +1 hora debugging
                success = uniform(rng) < 0.90; // 90% eventual success
            }
            
            if (success) {
                // Beneficios
                double learning = learning_value_dist->sample(rng);
                reputation = reputation_impact_dist->sample(rng);
                technical_debt = -5.0; // Reduce deuda técnica
                
                total_value = (
                    learning * 7.5 +           // Aprendizaje Strategy Pattern
                    reputation * 8.0 +         // Reputación profesional
                    technical_debt * (-2.0) +  // Reducción deuda técnica
                    10.0                       // Portfolio value
                );
                
                // Penalización por tiempo
                total_value -= time_invested * 0.5;
            } else {
                // Fallo total - peor escenario
                total_value = -10.0;
                reputation = -3.0;
                technical_debt = 0.0; // No cambia
            }
            
        } else if (decision == "REVERT") {
            // === OPCIÓN B: REVERTIR (git reset) ===
            time_invested = 0.08; // 5 minutos
            
            // Siempre exitoso
            success = true;
            
            // Consecuencias
            reputation = -4.0; // Mala reputación por abandonar
            technical_debt = 5.0; // Deuda técnica permanece
            
            total_value = (
                -10.0 +                    // Pérdida trabajo previo
                reputation * 2.0 +         // Impacto reputación
                technical_debt * (-1.5)    // Costo deuda técnica
            );
            
            // Pequeño bonus por tiempo mínimo
            total_value += 2.0;
            
        } else if (decision == "PARTIAL") {
            // === OPCIÓN C: COMMIT PARCIAL + TODO ===
            time_invested = 0.5; // 30 minutos
            
            // Alta probabilidad de éxito
            success = uniform(rng) < 0.95;
            
            if (success) {
                reputation = -2.0; // Trabajo a medias
                technical_debt = 3.0; // Código roto
                
                total_value = (
                    -5.0 +                     // Valor parcial del trabajo
                    reputation * 2.0 +         // Impacto reputación moderado
                    technical_debt * (-2.0) +  // Costo código roto
                    3.0                        // Documentación +valor
                );
            } else {
                total_value = -8.0;
                reputation = -3.0;
            }
        }
        
        // Calcular utilidad final
        double utility = total_value;
        bool good_decision = utility > 0.0;
        
        SimulationResult result(utility, good_decision);
        result.metrics["time_invested"] = time_invested;
        result.metrics["reputation"] = reputation;
        result.metrics["technical_debt"] = technical_debt;
        result.metrics["success"] = success ? 1.0 : 0.0;
        
        return result;
    }
    
    bool validateConfiguration() const override {
        return parameters_.hasParameter("decision") &&
               parameters_.hasParameter("compilation_risk") &&
               parameters_.hasParameter("learning_value") &&
               parameters_.hasParameter("reputation_impact");
    }
    
    std::vector<std::string> getRequiredParameters() const override {
        return {"decision", "compilation_risk", "learning_value", "reputation_impact"};
    }
    
    std::vector<std::string> getProducedMetrics() const override {
        return {"time_invested", "reputation", "technical_debt", "success"};
    }
};

int main() {
    std::cout << "================================================================================\n";
    std::cout << "🎯 ANÁLISIS C++: ¿Completar Refactorización FSK/LoRa?\n";
    std::cout << "================================================================================\n\n";
    
    std::cout << "📋 CONTEXTO:\n";
    std::cout << "   - Líder técnico con ganas de irse\n";
    std::cout << "   - Cultura empresa: 'salir del paso'\n";
    std::cout << "   - Refactorización 60% completa (FskModem creado, Lora limpiado)\n";
    std::cout << "   - Pendiente: FskScanner + main.cpp (40%)\n";
    std::cout << "   - Tiempo estimado: 2-4 horas\n\n";
    
    try {
        std::cout << "🔬 EJECUTANDO SIMULACIONES MONTE CARLO (50,000 iteraciones)...\n\n";
        
        // Distribuciones de incertidumbre
        auto compilation_risk = std::make_unique<UniformDistribution>(0.10, 0.20); // 10-20%
        auto learning_value = std::make_unique<TriangularDistribution>(0.6, 1.0, 0.85);
        auto reputation_impact = std::make_unique<TriangularDistribution>(0.7, 1.0, 0.85);
        
        MonteCarloEngine engine(50000);
        
        // === OPCIÓN A: COMPLETAR ===
        std::cout << "📊 Opción 1: COMPLETAR REFACTORIZACIÓN...\n";
        RefactoringDecisionScenario scenario_complete;
        scenario_complete.getParameters().setValue("decision", std::string("COMPLETE"));
        scenario_complete.getParameters().setDistribution("compilation_risk", compilation_risk->clone());
        scenario_complete.getParameters().setDistribution("learning_value", learning_value->clone());
        scenario_complete.getParameters().setDistribution("reputation_impact", reputation_impact->clone());
        
        auto results_complete = engine.simulate(scenario_complete);
        
        // === OPCIÓN B: REVERTIR ===
        std::cout << "📊 Opción 2: REVERTIR (git reset)...\n";
        RefactoringDecisionScenario scenario_revert;
        scenario_revert.getParameters().setValue("decision", std::string("REVERT"));
        scenario_revert.getParameters().setDistribution("compilation_risk", compilation_risk->clone());
        scenario_revert.getParameters().setDistribution("learning_value", learning_value->clone());
        scenario_revert.getParameters().setDistribution("reputation_impact", reputation_impact->clone());
        
        auto results_revert = engine.simulate(scenario_revert);
        
        // === OPCIÓN C: COMMIT PARCIAL ===
        std::cout << "📊 Opción 3: COMMIT PARCIAL + TODO...\n\n";
        RefactoringDecisionScenario scenario_partial;
        scenario_partial.getParameters().setValue("decision", std::string("PARTIAL"));
        scenario_partial.getParameters().setDistribution("compilation_risk", compilation_risk->clone());
        scenario_partial.getParameters().setDistribution("learning_value", learning_value->clone());
        scenario_partial.getParameters().setDistribution("reputation_impact", reputation_impact->clone());
        
        auto results_partial = engine.simulate(scenario_partial);
        
        // === COMPARACIÓN ===
        std::cout << "================================================================================\n";
        std::cout << "📊 RESULTADOS DEL ANÁLISIS (Monte Carlo C++)\n";
        std::cout << "================================================================================\n\n";
        
        ScenarioComparator comparator;
        comparator.addScenario("Completar Refactorización", results_complete);
        comparator.addScenario("Revertir (git reset)", results_revert);
        comparator.addScenario("Commit Parcial + TODO", results_partial);
        comparator.rankScenarios("mean", false);
        
        std::cout << comparator.generateReport() << "\n\n";
        
        // === ANÁLISIS DETALLADO ===
        std::cout << "🏆 RANKING DE OPCIONES\n";
        std::cout << "--------------------------------------------------------------------------------\n";
        
        auto print_option = [](const std::string& name, const MonteCarloResults& res, int rank) {
            auto time_stats = res.getMetricStats("time_invested");
            auto rep_stats = res.getMetricStats("reputation");
            auto debt_stats = res.getMetricStats("technical_debt");
            auto success_stats = res.getMetricStats("success");
            
            std::cout << "#" << rank << " " << name << "\n";
            std::cout << "    Utilidad promedio: " << std::fixed << std::setprecision(2) 
                      << res.getMean() << "\n";
            std::cout << "    Probabilidad éxito: " << std::setprecision(1) 
                      << success_stats.mean * 100 << "%\n";
            std::cout << "    Tiempo invertido: " << std::setprecision(2) 
                      << time_stats.mean << " horas\n";
            std::cout << "    Impacto reputación: " << std::setprecision(2) 
                      << rep_stats.mean << "\n";
            std::cout << "    Deuda técnica: " << std::setprecision(2) 
                      << debt_stats.mean << "\n";
            
            if (res.getMean() > 10.0) {
                std::cout << "    ⭐⭐⭐ HIGHLY RECOMMENDED\n";
            } else if (res.getMean() > 5.0) {
                std::cout << "    ⭐⭐ RECOMMENDED\n";
            } else if (res.getMean() > 0.0) {
                std::cout << "    ⭐ CONSIDER\n";
            } else {
                std::cout << "    ❌ NOT RECOMMENDED\n";
            }
            std::cout << "\n";
        };
        
        // Ordenar por utilidad
        struct RankedOption {
            std::string name;
            const MonteCarloResults* results;
            double mean;
        };
        
        std::vector<RankedOption> ranked = {
            {"Completar Refactorización", &results_complete, results_complete.getMean()},
            {"Revertir (git reset)", &results_revert, results_revert.getMean()},
            {"Commit Parcial + TODO", &results_partial, results_partial.getMean()}
        };
        
        std::sort(ranked.begin(), ranked.end(), 
            [](const RankedOption& a, const RankedOption& b) { return a.mean > b.mean; });
        
        for (size_t i = 0; i < ranked.size(); ++i) {
            print_option(ranked[i].name, *ranked[i].results, i + 1);
        }
        
        // === RECOMENDACIÓN ===
        std::cout << "================================================================================\n";
        std::cout << "✅ RECOMENDACIÓN C++: " << ranked[0].name << "\n";
        std::cout << "================================================================================\n\n";
        
        if (ranked[0].name.find("Completar") != std::string::npos) {
            std::cout << "🎯 RAZONES PARA COMPLETAR:\n";
            std::cout << "   1. Mayor utilidad esperada: " << std::fixed << std::setprecision(2) 
                      << ranked[0].mean << "\n";
            std::cout << "   2. Código 60% hecho (sunk cost positivo)\n";
            std::cout << "   3. Strategy Pattern → portfolio técnico\n";
            std::cout << "   4. Reduce deuda técnica significativamente\n";
            std::cout << "   5. Mejora reputación profesional\n\n";
            
            std::cout << "⏰ PLAN DE ACCIÓN (2-4 horas):\n";
            std::cout << "   [ ] 1. Actualizar FskScanner.hpp/cpp (15 min)\n";
            std::cout << "   [ ] 2. Actualizar main.cpp FskModem instances (30 min)\n";
            std::cout << "   [ ] 3. Test compilación (15 min)\n";
            std::cout << "   [ ] 4. Fix linker errors (30 min)\n";
            std::cout << "   [ ] 5. Commit 'refactor: Strategy Pattern' (10 min)\n\n";
        } else if (ranked[0].name.find("Revertir") != std::string::npos) {
            std::cout << "⚠️ RAZONES PARA REVERTIR:\n";
            std::cout << "   1. Utilidad esperada: " << std::fixed << std::setprecision(2) 
                      << ranked[0].mean << "\n";
            std::cout << "   2. Mínimo riesgo (5 minutos)\n";
            std::cout << "   3. Código vuelve a estado funcional\n\n";
            
            std::cout << "❌ CONSECUENCIAS:\n";
            std::cout << "   - Pérdida 2-3 horas trabajo\n";
            std::cout << "   - Deuda técnica permanece\n";
            std::cout << "   - Mala reputación (abandonar)\n\n";
        }
        
        std::cout << "================================================================================\n";
        
    } catch (const std::exception& e) {
        std::cerr << "ERROR: " << e.what() << std::endl;
        return 1;
    }
    
    return 0;
}
