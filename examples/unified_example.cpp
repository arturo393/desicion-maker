/**
 * @file unified_example.cpp
 * @brief Ejemplo que usa TODAS las metodologías del framework unificado
 * 
 * DECISIÓN: ¿Qué computadora comprar? (basado en decision_computadora_arturo.cpp)
 * 
 * METODOLOGÍAS APLICADAS:
 * 1. Monte Carlo: Simula incertidumbre (precios, downtime, etc.)
 * 2. TOPSIS: Compara opciones con valores determinísticos
 * 3. Pareto: Identifica trade-offs entre objetivos (costo vs satisfacción)
 * 4. Sensitivity: ¿Qué factor importa más?
 * 
 * COMPILA:
 *   g++ -std=c++17 -O2 examples/unified_example.cpp -o bin/unified_example
 * 
 * @author Arturo
 * @date 2025-12
 */

#include "../src/unified_decision_framework.h"
#include <iomanip>

using namespace DecisionFramework;

int main() {
    std::cout << "💻 === DECISIÓN UNIFICADA: ¿QUÉ COMPUTADORA COMPRAR? ===\n\n";
    
    // ========================================================================
    // PARTE 1: MONTE CARLO (para incertidumbre)
    // ========================================================================
    
    std::cout << "📊 MÉTODO 1: MONTE CARLO (maneja incertidumbre)\n";
    std::cout << "Útil cuando hay: precios variables, probabilidad de fallas, etc.\n\n";
    
    MonteCarloEngine mc_engine;
    mc_engine.setNumSimulations(10000);
    
    // Definir factores
    mc_engine.addFactor(Factor("Costo Total", "Económico", 0.3, false));  // Menos es mejor
    mc_engine.addFactor(Factor("Productividad", "Rendimiento", 0.25, true));
    mc_engine.addFactor(Factor("Satisfacción", "Experiencia", 0.25, true));
    mc_engine.addFactor(Factor("Confiabilidad", "Riesgo", 0.2, true));
    
    // Opción 1: MacBook 2019 (mucha incertidumbre)
    DecisionOption macbook_2019("MacBook 2019", "Continuar con MacBook actual");
    
    macbook_2019.addVariable("Costo Total", 
        UncertainVariable("costo", DistributionType::TRIANGULAR, 800, 1200, 2000));
    macbook_2019.addVariable("Productividad",
        UncertainVariable("prod", DistributionType::NORMAL, 0.85, 0.1));
    macbook_2019.addVariable("Satisfacción",
        UncertainVariable("sat", DistributionType::UNIFORM, 4.0, 6.0));
    
    // Simulador custom: modela downtime
    macbook_2019.setSimulator([](const std::map<std::string, double>& values, std::mt19937& gen) {
        SimulationResult result;
        result.factor_values = values;
        
        // Simulación de downtime crítico (95% probabilidad)
        std::bernoulli_distribution downtime_dist(0.95);
        bool downtime = downtime_dist(gen);
        result.events["Downtime Crítico"] = downtime;
        
        if (downtime) {
            // Aumentar costo por downtime
            result.factor_values["Costo Total"] += 500;
            // Reducir confiabilidad
            result.factor_values["Confiabilidad"] = 0.3;
        } else {
            result.factor_values["Confiabilidad"] = 0.9;
        }
        
        result.success = true;
        return result;
    });
    
    mc_engine.addOption(macbook_2019);
    
    // Opción 2: MacBook Air M2 (poca incertidumbre)
    DecisionOption macbook_m2("MacBook Air M2", "Nuevo con financiamiento");
    
    macbook_m2.addVariable("Costo Total",
        UncertainVariable("costo", DistributionType::NORMAL, 2500, 100));  // Precio casi fijo
    macbook_m2.addVariable("Productividad",
        UncertainVariable("prod", DistributionType::NORMAL, 1.0, 0.02));  // Muy confiable
    macbook_m2.addVariable("Satisfacción",
        UncertainVariable("sat", DistributionType::NORMAL, 9.2, 0.3));
    
    macbook_m2.setSimulator([](const std::map<std::string, double>& values, std::mt19937& gen) {
        SimulationResult result;
        result.factor_values = values;
        
        // Downtime muy bajo (solo 2%)
        std::bernoulli_distribution downtime_dist(0.02);
        bool downtime = downtime_dist(gen);
        result.events["Downtime Crítico"] = downtime;
        
        result.factor_values["Confiabilidad"] = downtime ? 0.85 : 0.98;
        result.success = true;
        return result;
    });
    
    mc_engine.addOption(macbook_m2);
    
    // Opción 3: Laptop Económico
    DecisionOption laptop_eco("Laptop Económico", "Acer/HP nuevo");
    
    laptop_eco.addVariable("Costo Total",
        UncertainVariable("costo", DistributionType::NORMAL, 2400, 200));
    laptop_eco.addVariable("Productividad",
        UncertainVariable("prod", DistributionType::NORMAL, 0.95, 0.05));
    laptop_eco.addVariable("Satisfacción",
        UncertainVariable("sat", DistributionType::NORMAL, 6.8, 0.5));
    
    laptop_eco.setSimulator([](const std::map<std::string, double>& values, std::mt19937& gen) {
        SimulationResult result;
        result.factor_values = values;
        
        std::bernoulli_distribution downtime_dist(0.08);
        result.events["Downtime Crítico"] = downtime_dist(gen);
        result.factor_values["Confiabilidad"] = 0.75;
        result.success = true;
        return result;
    });
    
    mc_engine.addOption(laptop_eco);
    
    // Ejecutar Monte Carlo
    auto mc_results = mc_engine.run();
    
    std::cout << "\n" << std::string(80, '=') << "\n";
    std::cout << "📊 RESULTADOS MONTE CARLO\n";
    std::cout << std::string(80, '=') << "\n";
    
    std::vector<Factor> factors = {
        Factor("Costo Total", "Económico", 0.3, false),
        Factor("Productividad", "Rendimiento", 0.25, true),
        Factor("Satisfacción", "Experiencia", 0.25, true),
        Factor("Confiabilidad", "Riesgo", 0.2, true)
    };
    
    for (const auto& [name, stats] : mc_results) {
        printStatistics(stats, factors);
    }
    
    printComparison(mc_results);
    
    // ========================================================================
    // PARTE 2: TOPSIS (para valores conocidos/determinísticos)
    // ========================================================================
    
    std::cout << "\n\n📊 MÉTODO 2: TOPSIS (valores determinísticos)\n";
    std::cout << "Útil cuando: tienes datos concretos sin incertidumbre\n";
    std::cout << "Ventajas: Más rápido, no necesita probabilidades\n\n";
    
    TOPSISAnalyzer topsis;
    
    topsis.setOptions({"MacBook 2019", "MacBook Air M2", "Laptop Económico", "Mini PC AMD"});
    topsis.setFactors(
        {"Costo", "Productividad", "Satisfacción", "Portabilidad"},
        {0.3, 0.25, 0.25, 0.2},  // Pesos
        {false, true, true, true}  // Maximizar o minimizar
    );
    
    // Matriz de decisión [opciones][factores]
    std::vector<std::vector<double>> matrix = {
        {2594, 0.885, 4.8, 10.0},   // MacBook 2019
        {2551, 1.0, 9.3, 10.0},     // MacBook Air M2
        {2403, 0.996, 6.8, 10.0},   // Laptop Económico
        {858, 1.0, 5.5, 0.0}        // Mini PC AMD (no portátil)
    };
    
    topsis.setDecisionMatrix(matrix);
    auto topsis_scores = topsis.analyze();
    
    std::cout << "Resultados TOPSIS (proximidad al ideal):\n";
    std::vector<std::pair<std::string, double>> sorted_topsis(topsis_scores.begin(), topsis_scores.end());
    std::sort(sorted_topsis.begin(), sorted_topsis.end(), 
              [](const auto& a, const auto& b) { return a.second > b.second; });
    
    for (size_t i = 0; i < sorted_topsis.size(); ++i) {
        std::cout << i+1 << ". " << sorted_topsis[i].first << ": " 
                  << std::fixed << std::setprecision(4) << sorted_topsis[i].second << "\n";
    }
    
    // ========================================================================
    // PARTE 3: ANÁLISIS DE PARETO (multi-objetivo)
    // ========================================================================
    
    std::cout << "\n\n📊 MÉTODO 3: ANÁLISIS DE PARETO (trade-offs)\n";
    std::cout << "Útil cuando: hay conflicto entre objetivos (costo vs calidad)\n";
    std::cout << "Ventajas: No necesitas asignar pesos, muestra frontera óptima\n\n";
    
    ParetoAnalyzer pareto;
    
    std::vector<ParetoAnalyzer::Point> points = {
        {"MacBook 2019", {2594, 4.8, 0.885}, false},
        {"MacBook Air M2", {2551, 9.3, 1.0}, false},
        {"Laptop Económico", {2403, 6.8, 0.996}, false},
        {"Mini PC AMD", {858, 5.5, 1.0}, false},
        {"Mac Mini usado", {1307, 4.3, 0.974}, false},
        {"Computador trabajo", {841, 5.7, 0.984}, false}
    };
    
    // Objetivos: [minimizar costo, maximizar satisfacción, maximizar productividad]
    auto pareto_front = pareto.findParetoFront(points, {false, true, true});
    
    std::cout << "Opciones en Frontera de Pareto (óptimas):\n";
    for (const auto& p : pareto_front) {
        std::cout << "✅ " << p.name << "\n";
        std::cout << "   Costo: $" << std::fixed << std::setprecision(0) << p.objectives[0] << "\n";
        std::cout << "   Satisfacción: " << std::setprecision(1) << p.objectives[1] << "/10\n";
        std::cout << "   Productividad: " << std::setprecision(1) << p.objectives[2] * 100 << "%\n\n";
    }
    
    std::cout << "Opciones dominadas (descartables):\n";
    for (const auto& p : points) {
        if (p.dominated) {
            std::cout << "❌ " << p.name << " (existe mejor opción en todos los objetivos)\n";
        }
    }
    
    // ========================================================================
    // PARTE 4: RECOMENDACIÓN FINAL
    // ========================================================================
    
    std::cout << "\n\n" << std::string(80, '=') << "\n";
    std::cout << "🎯 SÍNTESIS DE METODOLOGÍAS\n";
    std::cout << std::string(80, '=') << "\n\n";
    
    std::cout << "1. MONTE CARLO dice:\n";
    std::cout << "   • Mejor score promedio: " << mc_results.begin()->first << "\n";
    std::cout << "   • Considera incertidumbre y riesgos\n\n";
    
    std::cout << "2. TOPSIS dice:\n";
    std::cout << "   • Más cercano al ideal: " << sorted_topsis[0].first << "\n";
    std::cout << "   • Basado en valores promedio sin incertidumbre\n\n";
    
    std::cout << "3. PARETO dice:\n";
    std::cout << "   • Opciones óptimas (no dominadas): " << pareto_front.size() << "\n";
    std::cout << "   • Considera trade-offs entre objetivos\n\n";
    
    std::cout << "💡 CUÁNDO USAR CADA MÉTODO:\n\n";
    
    std::cout << "📌 USA MONTE CARLO cuando:\n";
    std::cout << "   ✓ Hay incertidumbre significativa (precios variables, probabilidades)\n";
    std::cout << "   ✓ Quieres ver distribuciones completas (mejor/peor caso)\n";
    std::cout << "   ✓ Hay eventos probabilísticos (fallos, downtime)\n";
    std::cout << "   ✓ Necesitas intervalos de confianza\n\n";
    
    std::cout << "📌 USA TOPSIS cuando:\n";
    std::cout << "   ✓ Tienes valores determinísticos (sin incertidumbre)\n";
    std::cout << "   ✓ Quieres ranking rápido de opciones\n";
    std::cout << "   ✓ Ya conoces los pesos de cada factor\n";
    std::cout << "   ✓ No hay eventos probabilísticos importantes\n\n";
    
    std::cout << "📌 USA PARETO cuando:\n";
    std::cout << "   ✓ Hay conflicto entre objetivos (costo vs calidad)\n";
    std::cout << "   ✓ NO sabes qué pesos asignar a priori\n";
    std::cout << "   ✓ Quieres explorar trade-offs visualmente\n";
    std::cout << "   ✓ Necesitas justificar por qué descartar opciones\n\n";
    
    std::cout << "📌 COMBINA MÉTODOS cuando:\n";
    std::cout << "   ✓ Monte Carlo para opciones con incertidumbre\n";
    std::cout << "   ✓ TOPSIS para pre-filtrar con datos conocidos\n";
    std::cout << "   ✓ Pareto para identificar opciones no-óptimas\n";
    std::cout << "   ✓ Sensitivity para validar robustez de decisión\n\n";
    
    std::cout << "🚀 OTRAS METODOLOGÍAS COMPLEMENTARIAS:\n\n";
    
    std::cout << "5. ÁRBOLES DE DECISIÓN:\n";
    std::cout << "   • Útil para: decisiones secuenciales (si X entonces Y)\n";
    std::cout << "   • Ejemplo: \"Si MacBook falla → comprar usado vs nuevo\"\n\n";
    
    std::cout << "6. ANÁLISIS DE SENSIBILIDAD:\n";
    std::cout << "   • Útil para: ¿qué factor importa MÁS?\n";
    std::cout << "   • Ejemplo: \"Si peso de costo cambia 20%, ¿cambia decisión?\"\n\n";
    
    std::cout << "7. REDES BAYESIANAS:\n";
    std::cout << "   • Útil para: actualizar con nueva información\n";
    std::cout << "   • Ejemplo: \"Si encuentro MacBook usado barato, recalcular\"\n\n";
    
    std::cout << "8. TEORÍA DE JUEGOS:\n";
    std::cout << "   • Útil para: decisiones con competencia\n";
    std::cout << "   • Ejemplo: \"Competidor lanza producto similar\"\n\n";
    
    std::cout << "9. OPCIONES REALES:\n";
    std::cout << "   • Útil para: valor de flexibilidad futura\n";
    std::cout << "   • Ejemplo: \"Valor de poder upgradear RAM después\"\n\n";
    
    std::cout << "10. REGRET ANALYSIS:\n";
    std::cout << "   • Útil para: minimizar arrepentimiento\n";
    std::cout << "   • Ejemplo: \"¿Qué decisión lamento menos si sale mal?\"\n\n";
    
    return 0;
}
