/**
 * @file deep_research_decision_example.cpp
 * @brief Ejemplo: Decisión de Computadora con Deep Research Pro
 * 
 * Combina:
 * 1. Framework de decisiones (Monte Carlo, TOPSIS, Pareto)
 * 2. Deep Research Pro (análisis con IA Google)
 * 
 * Compile:
 *   g++ -std=c++17 -O2 deep_research_decision_example.cpp -o bin/deep_research_example
 * 
 * Execute:
 *   ./bin/deep_research_example
 */

#include "../src/unified_decision_framework.h"
#include "../src/ai_deep_research_integration.h"
#include <iostream>
#include <iomanip>

using namespace DecisionFramework;
using namespace AIIntegration;

int main() {
    std::cout << "\n" << std::string(90, '=') << "\n";
    std::cout << "🤖 DECISION MAKER + Deep Research Pro\n";
    std::cout << std::string(90, '=') << "\n\n";
    
    // ========================================================================
    // PARTE 1: Framework tradicional (rápido, 10 segundos)
    // ========================================================================
    
    std::cout << "📊 PASO 1: Análisis con Framework de Decisiones (10s)\n";
    std::cout << std::string(90, '-') << "\n\n";
    
    MonteCarloEngine mc;
    mc.setNumSimulations(5000);
    
    // Factores de decisión
    mc.addFactor(Factor("Costo Total", "Gasto en 2 años", 0.25, false));
    mc.addFactor(Factor("Portabilidad", "Movilidad", 0.20, true));
    mc.addFactor(Factor("Potencia", "Desempeño", 0.25, true));
    mc.addFactor(Factor("Durabilidad", "Años de vida", 0.15, true));
    mc.addFactor(Factor("Ecosistema", "Software/services", 0.15, true));
    
    // Opción 1: MacBook Air M2
    {
        DecisionOption opcion("MacBook Air M2", "Laptop portátil M2, 8GB, 256GB");
        opcion.addVariable("Costo Total", 
                          UncertainVariable("costo", DistributionType::TRIANGULAR, 1400, 1600, 1800));
        opcion.addVariable("Portabilidad",
                          UncertainVariable("portab", DistributionType::TRIANGULAR, 8, 9, 10));
        opcion.addVariable("Potencia",
                          UncertainVariable("potencia", DistributionType::TRIANGULAR, 7, 8, 9));
        opcion.addVariable("Durabilidad",
                          UncertainVariable("durabil", DistributionType::NORMAL, 5, 0.5));
        opcion.addVariable("Ecosistema",
                          UncertainVariable("ecosist", DistributionType::TRIANGULAR, 8, 9, 10));
        
        opcion.setSimulator([](const auto& values, std::mt19937& gen) {
            SimulationResult result;
            result.factor_values = values;
            result.success = true;
            return result;
        });
        
        mc.addOption(opcion);
    }
    
    // Opción 2: Lenovo ThinkPad X1
    {
        DecisionOption opcion("Lenovo ThinkPad X1", "Profesional, Intel i7, 16GB, 512GB");
        opcion.addVariable("Costo Total",
                          UncertainVariable("costo", DistributionType::TRIANGULAR, 1200, 1400, 1600));
        opcion.addVariable("Portabilidad",
                          UncertainVariable("portab", DistributionType::TRIANGULAR, 7, 8, 9));
        opcion.addVariable("Potencia",
                          UncertainVariable("potencia", DistributionType::TRIANGULAR, 8, 9, 10));
        opcion.addVariable("Durabilidad",
                          UncertainVariable("durabil", DistributionType::NORMAL, 5.5, 0.5));
        opcion.addVariable("Ecosistema",
                          UncertainVariable("ecosist", DistributionType::TRIANGULAR, 6, 7, 8));
        
        opcion.setSimulator([](const auto& values, std::mt19937& gen) {
            SimulationResult result;
            result.factor_values = values;
            result.success = true;
            return result;
        });
        
        mc.addOption(opcion);
    }
    
    // Opción 3: Dell XPS 13
    {
        DecisionOption opcion("Dell XPS 13", "Diseño, OLED, Intel/AMD, 16GB");
        opcion.addVariable("Costo Total",
                          UncertainVariable("costo", DistributionType::TRIANGULAR, 1300, 1500, 1700));
        opcion.addVariable("Portabilidad",
                          UncertainVariable("portab", DistributionType::TRIANGULAR, 8, 9, 10));
        opcion.addVariable("Potencia",
                          UncertainVariable("potencia", DistributionType::TRIANGULAR, 7.5, 8.5, 9.5));
        opcion.addVariable("Durabilidad",
                          UncertainVariable("durabil", DistributionType::NORMAL, 4.5, 0.7));
        opcion.addVariable("Ecosistema",
                          UncertainVariable("ecosist", DistributionType::TRIANGULAR, 6, 7, 8));
        
        opcion.setSimulator([](const auto& values, std::mt19937& gen) {
            SimulationResult result;
            result.factor_values = values;
            result.success = true;
            return result;
        });
        
        mc.addOption(opcion);
    }
    
    // Ejecutar análisis del framework
    auto results = mc.run();
    
    std::cout << "📊 Resultados Monte Carlo:\n\n";
    for (const auto& [name, stats] : results) {
        std::cout << "  " << std::left << std::setw(25) << name
                  << "Score: " << std::fixed << std::setprecision(2) 
                  << stats.mean_score << " ± " << stats.score_stddev << "\n";
    }
    
    // Análisis de sensibilidad
    std::cout << "\n📈 Factores más importantes:\n\n";
    auto sens = mc.sensitivityAnalysis("MacBook Air M2");
    for (const auto& [factor, impact] : sens) {
        std::string bar(static_cast<int>(impact * 20), '█');
        std::cout << "  " << std::left << std::setw(20) << factor
                  << bar << " " << std::fixed << std::setprecision(2) << impact << "\n";
    }
    
    // ========================================================================
    // PARTE 2: Análisis con Deep Research Pro (3-5 minutos)
    // ========================================================================
    
    std::cout << "\n\n";
    std::cout << "🔬 PASO 2: Análisis Profundo con Deep Research Pro (3-5 min)\n";
    std::cout << std::string(90, '-') << "\n\n";
    
    AIAnalyzer ai_analyzer;
    ai_analyzer.setPythonScriptPath("scripts/deep_research_analyzer.py");
    ai_analyzer.setTimeoutSeconds(600);  // 10 minutos máximo
    
    // Definir opciones y criterios
    std::map<std::string, std::string> options = {
        {"MacBook Air M2", "Portátil M2, 8GB RAM, 256GB SSD, $1,599"},
        {"Lenovo ThinkPad X1", "Profesional Intel i7, 16GB RAM, 512GB, $1,499"},
        {"Dell XPS 13", "Diseño con OLED, Intel/AMD, 16GB, $1,599"}
    };
    
    std::map<std::string, int> criteria = {
        {"Portabilidad", 8},
        {"Potencia", 7},
        {"Precio", 6},
        {"Durabilidad", 8},
        {"Ecosistema", 7}
    };
    
    // Ejecutar análisis profundo
    std::cout << "🚀 Iniciando Deep Research Pro...\n";
    std::cout << "   (Este análisis puede tomar 3-5 minutos)\n\n";
    
    auto ai_result = ai_analyzer.analyzeDecisionDeep(
        "Compra de Computadora Portátil 2025",
        options,
        criteria
    );
    
    // ========================================================================
    // PARTE 3: Mostrar resultados combinados
    // ========================================================================
    
    std::cout << "\n\n";
    std::cout << std::string(90, '=') << "\n";
    std::cout << "📋 RESULTADOS COMBINADOS\n";
    std::cout << std::string(90, '=') << "\n\n";
    
    if (ai_result.success) {
        std::cout << "✅ Análisis completado en " << ai_result.analysis_time_seconds 
                  << " segundos\n\n";
        
        std::cout << "🎯 RECOMENDACIÓN PRINCIPAL:\n";
        std::cout << "   " << ai_result.recommendation << "\n\n";
        
        std::cout << "📊 ANÁLISIS DETALLADO:\n";
        std::cout << ai_result.full_analysis << "\n";
    } else {
        std::cout << "⚠️  Análisis incompleto (posible timeout o error)\n";
        std::cout << "   Error: " << ai_result.error_message << "\n";
    }
    
    // ========================================================================
    // Recomendaciones finales
    // ========================================================================
    
    std::cout << "\n" << std::string(90, '=') << "\n";
    std::cout << "💡 CONCLUSIÓN\n";
    std::cout << std::string(90, '=') << "\n\n";
    
    // Encontrar mejor según Monte Carlo
    auto best_mc = results.begin();
    for (auto it = results.begin(); it != results.end(); ++it) {
        if (it->second.mean_score > best_mc->second.mean_score) {
            best_mc = it;
        }
    }
    
    std::cout << "Framework de Decisiones sugiere: " << best_mc->first << "\n";
    std::cout << "Deep Research Pro sugiere: (ver recomendación arriba)\n";
    std::cout << "\n✅ Próximo paso: Validar en tienda y revisar garantía\n";
    
    std::cout << "\n" << std::string(90, '=') << "\n";
    
    return 0;
}
