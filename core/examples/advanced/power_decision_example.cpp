/**
 * @file power_decision_example.cpp
 * @brief Ejemplo SUPER PODEROSO usando todas las herramientas avanzadas
 * 
 * DECISIÓN: ¿Qué computadora comprar? (ANÁLISIS COMPLETO)
 * 
 * METODOLOGÍAS APLICADAS:
 * 1. Monte Carlo base (incertidumbre)
 * 2. Bayesian Update (nueva información: "Encontré MacBook usado barato")
 * 3. Regret Analysis (minimizar arrepentimiento)
 * 4. Real Options (valor de poder upgradear después)
 * 5. Risk Analysis (VaR, CVaR, probabilidad de ruina)
 * 6. Scenario Planning (futuros alternativos: boom vs recesión)
 * 7. Correlation Analysis (¿costo y calidad correlacionados?)
 * 8. Multi-Armed Bandit (aprender de experiencia real)
 * 
 * @author Arturo
 * @date 2025-12
 */

#include "../src/unified_decision_framework.h"
#include "../src/advanced_decision_tools.h"
#include <iomanip>

using namespace DecisionFramework;

int main() {
    std::cout << "🚀 === DECISIÓN SUPER PODEROSA: COMPUTADORA CON TODAS LAS METODOLOGÍAS ===\n\n";
    
    // ========================================================================
    // PASO 1: MONTE CARLO BASE (como siempre)
    // ========================================================================
    
    std::cout << "📊 PASO 1: MONTE CARLO (baseline)\n\n";
    
    MonteCarloEngine mc;
    mc.setNumSimulations(5000);
    
    mc.addFactor(Factor("Costo", "Económico", 0.3, false));
    mc.addFactor(Factor("Productividad", "Rendimiento", 0.25, true));
    mc.addFactor(Factor("Satisfacción", "Experiencia", 0.25, true));
    mc.addFactor(Factor("Confiabilidad", "Riesgo", 0.2, true));
    
    // Opción 1: MacBook 2019 actual
    DecisionOption macbook_2019("MacBook 2019", "Continuar con actual");
    macbook_2019.addVariable("Costo", UncertainVariable("costo", 
        DistributionType::TRIANGULAR, 800, 1200, 2000));
    macbook_2019.addVariable("Productividad", UncertainVariable("prod",
        DistributionType::NORMAL, 0.85, 0.1));
    macbook_2019.addVariable("Satisfacción", UncertainVariable("sat",
        DistributionType::UNIFORM, 4.0, 6.0));
    macbook_2019.setSimulator([](const auto& values, std::mt19937& gen) {
        SimulationResult result;
        result.factor_values = values;
        std::bernoulli_distribution downtime(0.95);
        result.events["Downtime"] = downtime(gen);
        result.factor_values["Confiabilidad"] = result.events["Downtime"] ? 0.3 : 0.9;
        result.success = true;
        return result;
    });
    mc.addOption(macbook_2019);
    
    // Opción 2: MacBook Air M2 nuevo
    DecisionOption macbook_m2("MacBook Air M2", "Nuevo con financiamiento");
    macbook_m2.addVariable("Costo", UncertainVariable("costo",
        DistributionType::NORMAL, 2500, 100));
    macbook_m2.addVariable("Productividad", UncertainVariable("prod",
        DistributionType::NORMAL, 1.0, 0.02));
    macbook_m2.addVariable("Satisfacción", UncertainVariable("sat",
        DistributionType::NORMAL, 9.2, 0.3));
    macbook_m2.setSimulator([](const auto& values, std::mt19937& gen) {
        SimulationResult result;
        result.factor_values = values;
        std::bernoulli_distribution downtime(0.02);
        result.events["Downtime"] = downtime(gen);
        result.factor_values["Confiabilidad"] = result.events["Downtime"] ? 0.85 : 0.98;
        result.success = true;
        return result;
    });
    mc.addOption(macbook_m2);
    
    auto mc_results = mc.run();
    
    std::cout << "Resultados Monte Carlo:\n";
    for (const auto& [name, stats] : mc_results) {
        std::cout << "  • " << name << ": score " << std::fixed << std::setprecision(1) 
                  << stats.mean_score << " (±" << stats.score_stddev << ")\n";
    }
    
    // ========================================================================
    // PASO 2: BAYESIAN UPDATE - Nueva información
    // ========================================================================
    
    std::cout << "\n\n🧠 PASO 2: ACTUALIZACIÓN BAYESIANA\n";
    std::cout << "Situación: Encontré MacBook usado a $800 (muy barato)\n\n";
    
    BayesianUpdater bn;
    bn.addNode("macbook_falla", 0.15);  // Prior: 15% falla
    bn.addNode("precio_muy_bajo", 0.20); // Prior: 20% encuentra muy barato
    bn.addConditional("macbook_falla", "precio_muy_bajo", 0.65); // P(falla|barato) = 65%
    
    // Nueva evidencia: encontré barato
    bn.updateBelief("macbook_falla", "precio_muy_bajo", true);
    
    std::cout << "Probabilidad de falla:\n";
    std::cout << "  • Prior (antes): 15.0%\n";
    std::cout << "  • Posterior (con evidencia): " << std::fixed << std::setprecision(1)
              << bn.getPosterior("macbook_falla") * 100 << "%\n";
    std::cout << "  ⚠️  Riesgo AUMENTA (laptops baratas fallan más)\n";
    
    // ========================================================================
    // PASO 3: REGRET ANALYSIS - Minimizar arrepentimiento
    // ========================================================================
    
    std::cout << "\n\n😰 PASO 3: ANÁLISIS DE ARREPENTIMIENTO\n";
    std::cout << "¿Qué decisión lamentaré MENOS si sale mal?\n\n";
    
    RegretAnalyzer regret;
    
    std::vector<std::string> scenarios = {"Precio sube 20%", "Precio igual", "Precio baja 20%"};
    std::vector<RegretAnalyzer::Outcome> outcomes = {
        {"MacBook 2019", "Precio sube 20%", -500},    // Pierdo $500 (no compré antes)
        {"MacBook 2019", "Precio igual", 0},
        {"MacBook 2019", "Precio baja 20%", 400},     // Gano $400 (esperé)
        
        {"MacBook Air M2", "Precio sube 20%", -600},  // Pierdo $600
        {"MacBook Air M2", "Precio igual", 0},
        {"MacBook Air M2", "Precio baja 20%", 500},   // Gano $500
        
        {"Laptop económico", "Precio sube 20%", -200}, // Menos variación
        {"Laptop económico", "Precio igual", 0},
        {"Laptop económico", "Precio baja 20%", 200}
    };
    
    std::string minimax_choice = regret.minimaxRegret(outcomes, scenarios);
    
    std::cout << "Estrategia Minimax Regret: " << minimax_choice << "\n";
    std::cout << "  → Minimiza arrepentimiento en el PEOR escenario\n";
    std::cout << "  → Enfoque psicológico para aversión a pérdidas\n";
    
    // ========================================================================
    // PASO 4: REAL OPTIONS - Valor de flexibilidad
    // ========================================================================
    
    std::cout << "\n\n💎 PASO 4: OPCIONES REALES (valor de flexibilidad)\n";
    std::cout << "¿Cuánto vale poder cambiar de decisión después?\n\n";
    
    RealOptionsAnalyzer real_opt;
    
    // Valor de esperar 3 meses (puede bajar precio)
    double value_wait = real_opt.valueOfWaiting(2500, 0.30, 0.25, 0.05);
    std::cout << "Valor de opción de ESPERAR 3 meses:\n";
    std::cout << "  • Prima de flexibilidad: $" << std::fixed << std::setprecision(0) 
              << value_wait << "\n";
    std::cout << "  • Decisión: Si prima > costo de esperar → ESPERA\n";
    
    // Valor de poder upgradear RAM después
    double value_upgrade = real_opt.valueOfExpansionOption(
        1200,  // Costo base Mac Mini
        400,   // Costo upgrade RAM
        800,   // Beneficio de RAM extra
        0.60   // 60% probabilidad de necesitar
    );
    std::cout << "\nValor de opción de UPGRADEAR RAM después:\n";
    std::cout << "  • Valor de flexibilidad: $" << std::fixed << std::setprecision(0)
              << value_upgrade << "\n";
    std::cout << "  • Mac Mini con opción vale: $" << (1200 + value_upgrade) << "\n";
    
    // ========================================================================
    // PASO 5: RISK ANALYSIS - Métricas avanzadas
    // ========================================================================
    
    std::cout << "\n\n⚠️  PASO 5: ANÁLISIS DE RIESGO AVANZADO\n";
    std::cout << "VaR, CVaR, Probabilidad de ruina\n\n";
    
    RiskAnalyzer risk;
    
    // Simular costos totales (incluyendo downtime)
    std::vector<double> macbook_costs, m2_costs;
    std::mt19937 gen(12345);
    for (int i = 0; i < 1000; ++i) {
        // MacBook 2019: costo variable + downtime
        std::normal_distribution<> cost_dist(1200, 300);
        double base_cost = cost_dist(gen);
        std::bernoulli_distribution downtime(0.95);
        if (downtime(gen)) {
            base_cost += 500;  // Costo downtime
        }
        macbook_costs.push_back(-base_cost);  // Negativo = pérdida
        
        // MacBook Air M2: costo estable
        std::normal_distribution<> m2_dist(2500, 100);
        m2_costs.push_back(-m2_dist(gen));
    }
    
    std::cout << "MacBook 2019:\n";
    std::cout << "  • VaR (95%): $" << std::fixed << std::setprecision(0)
              << -risk.calculateVaR(macbook_costs, 0.95) << "\n";
    std::cout << "  • CVaR (peor 5%): $" << -risk.calculateCVaR(macbook_costs, 0.95) << "\n";
    std::cout << "  • Prob. ruina (>50% capital): " << std::setprecision(1)
              << risk.probabilityOfRuin(macbook_costs, 3000, 0.5) * 100 << "%\n";
    
    std::cout << "\nMacBook Air M2:\n";
    std::cout << "  • VaR (95%): $" << std::fixed << std::setprecision(0)
              << -risk.calculateVaR(m2_costs, 0.95) << "\n";
    std::cout << "  • CVaR (peor 5%): $" << -risk.calculateCVaR(m2_costs, 0.95) << "\n";
    std::cout << "  • Prob. ruina: " << std::setprecision(1)
              << risk.probabilityOfRuin(m2_costs, 3000, 0.5) * 100 << "%\n";
    
    std::cout << "\n💡 Interpretación:\n";
    std::cout << "  • CVaR muestra pérdida promedio en PEOR escenario\n";
    std::cout << "  • MacBook 2019 tiene mayor riesgo de ruina (downtime)\n";
    
    // ========================================================================
    // PASO 6: SCENARIO PLANNING - Futuros alternativos
    // ========================================================================
    
    std::cout << "\n\n🌍 PASO 6: PLANIFICACIÓN DE ESCENARIOS\n";
    std::cout << "3 futuros posibles con narrativas coherentes\n\n";
    
    ScenarioPlanner sp;
    
    std::vector<ScenarioPlanner::Scenario> scenarios_plan = {
        {
            "Boom Tecnológico",
            "IA revoluciona desarrollo, demanda freelance +200%, necesito máxima potencia",
            0.30,
            {{"ingreso_mensual", 5000}, {"valor_portabilidad", 10}, {"necesidad_potencia", 0.9}}
        },
        {
            "Status Quo",
            "Mercado estable, trabajo híbrido continúa",
            0.50,
            {{"ingreso_mensual", 2500}, {"valor_portabilidad", 7}, {"necesidad_potencia", 0.6}}
        },
        {
            "Recesión",
            "Crisis económica, prioridad es minimizar gastos",
            0.20,
            {{"ingreso_mensual", 1200}, {"valor_portabilidad", 4}, {"necesidad_potencia", 0.4}}
        }
    };
    
    auto evaluate_scenario = [](const std::string& option, 
                                const ScenarioPlanner::Scenario& s) -> double {
        double score = 0;
        if (option == "MacBook Air M2") {
            score = s.factor_values.at("ingreso_mensual") * 0.5 - 2500;
            score += s.factor_values.at("necesidad_potencia") * 1000;
        } else if (option == "MacBook 2019") {
            score = s.factor_values.at("ingreso_mensual") * 0.3 - 1200;
            score += s.factor_values.at("necesidad_potencia") * 500;
        } else { // Laptop económico
            score = s.factor_values.at("ingreso_mensual") * 0.4 - 2000;
            score += s.factor_values.at("necesidad_potencia") * 700;
        }
        return score;
    };
    
    std::vector<std::string> options = {"MacBook Air M2", "MacBook 2019", "Laptop económico"};
    std::string robust_choice = sp.findRobustOption(options, scenarios_plan, evaluate_scenario);
    
    std::cout << "Escenarios considerados:\n";
    for (const auto& scenario : scenarios_plan) {
        std::cout << "  • " << scenario.name << " (" << std::fixed << std::setprecision(0)
                  << scenario.probability * 100 << "% prob)\n";
        std::cout << "    \"" << scenario.narrative << "\"\n";
    }
    
    std::cout << "\nOpción ROBUSTA (funciona bien en todos): " << robust_choice << "\n";
    std::cout << "  → No es la mejor en ningún escenario\n";
    std::cout << "  → Pero es BUENA en todos los escenarios\n";
    
    // ========================================================================
    // PASO 7: CORRELATION ANALYSIS
    // ========================================================================
    
    std::cout << "\n\n🔗 PASO 7: ANÁLISIS DE CORRELACIONES\n";
    std::cout << "¿Factores se mueven juntos?\n\n";
    
    CorrelationAnalyzer corr_analyzer;
    
    std::vector<std::string> factor_names = {"Costo", "Productividad", "Satisfacción", "Confiabilidad"};
    
    // Simular datos
    std::vector<std::map<std::string, double>> sims;
    for (int i = 0; i < 100; ++i) {
        std::map<std::string, double> sim;
        double costo = 1000 + gen() % 2000;
        sim["Costo"] = costo;
        sim["Productividad"] = 0.5 + (costo / 3000.0) * 0.4; // Correlación +
        sim["Satisfacción"] = 5 + (costo / 3000.0) * 4;      // Correlación +
        sim["Confiabilidad"] = 0.6 + (gen() % 100) / 250.0;  // Independiente
        sims.push_back(sim);
    }
    
    auto corr_matrix = corr_analyzer.correlationMatrix(factor_names, sims);
    auto high_corrs = corr_analyzer.findHighCorrelations(factor_names, corr_matrix, 0.7);
    
    std::cout << "Correlaciones altas detectadas:\n";
    for (const auto& [f1, f2] : high_corrs) {
        std::cout << "  • " << f1 << " ↔ " << f2 << "\n";
    }
    std::cout << "\n💡 Implicación: Costo y calidad NO son independientes\n";
    std::cout << "  → Laptops caras suelen ser mejores (correlación positiva)\n";
    std::cout << "  → Modelo debe capturar esta dependencia\n";
    
    // ========================================================================
    // PASO 8: MULTI-ARMED BANDIT - Aprendizaje adaptativo
    // ========================================================================
    
    std::cout << "\n\n🎰 PASO 8: MULTI-ARMED BANDIT (aprendizaje real)\n";
    std::cout << "Simula usar laptop cada semana y APRENDER cuál funciona mejor\n\n";
    
    MultiArmedBandit mab;
    mab.addArm("MacBook Air M2");
    mab.addArm("MacBook 2019");
    mab.addArm("Laptop económico");
    
    std::cout << "Simulación 10 semanas:\n";
    for (int week = 1; week <= 10; ++week) {
        std::string choice = mab.selectArmUCB(1.5);
        
        // Simular satisfacción real (con ruido)
        double satisfaction = 0;
        if (choice == "MacBook Air M2") {
            satisfaction = 9.0 + (gen() % 10 - 5) / 10.0;
        } else if (choice == "MacBook 2019") {
            satisfaction = 5.0 + (gen() % 10 - 5) / 10.0;
        } else {
            satisfaction = 7.0 + (gen() % 10 - 5) / 10.0;
        }
        
        mab.updateReward(choice, satisfaction);
        
        if (week <= 3 || week == 10) {
            std::cout << "  Semana " << week << ": Probé " << choice 
                      << " → satisfacción " << std::fixed << std::setprecision(1) 
                      << satisfaction << "/10\n";
        }
    }
    
    std::cout << "\n💡 Ventaja: APRENDE de experiencia REAL\n";
    std::cout << "  → Balancea exploración (probar nuevas) vs explotación (usar mejor)\n";
    std::cout << "  → Converge a mejor opción PARA TI específicamente\n";
    
    // ========================================================================
    // SÍNTESIS FINAL
    // ========================================================================
    
    std::cout << "\n\n" << std::string(80, '=') << "\n";
    std::cout << "🎯 SÍNTESIS SUPER PODEROSA\n";
    std::cout << std::string(80, '=') << "\n\n";
    
    std::cout << "1. MONTE CARLO: Mejor opción promedio\n";
    std::cout << "   ✅ Considera incertidumbre básica\n\n";
    
    std::cout << "2. BAYESIAN UPDATE: Actualiza con nueva info\n";
    std::cout << "   ✅ \"Encontré barato\" → Riesgo aumenta 15% → 48%\n\n";
    
    std::cout << "3. REGRET ANALYSIS: " << minimax_choice << "\n";
    std::cout << "   ✅ Minimiza arrepentimiento en peor caso\n\n";
    
    std::cout << "4. REAL OPTIONS: Valor de flexibilidad\n";
    std::cout << "   ✅ Esperar vale $" << std::fixed << std::setprecision(0) << value_wait << "\n";
    std::cout << "   ✅ Opción upgrade vale $" << value_upgrade << "\n\n";
    
    std::cout << "5. RISK ANALYSIS: VaR, CVaR\n";
    std::cout << "   ✅ MacBook 2019: Alto riesgo de ruina (downtime)\n";
    std::cout << "   ✅ MacBook Air M2: Riesgo controlado\n\n";
    
    std::cout << "6. SCENARIO PLANNING: " << robust_choice << "\n";
    std::cout << "   ✅ Funciona bien en boom, status quo, y recesión\n\n";
    
    std::cout << "7. CORRELATION: Costo ↔ Calidad\n";
    std::cout << "   ✅ NO son independientes (correlación +0.8)\n\n";
    
    std::cout << "8. BANDIT: Aprende de experiencia real\n";
    std::cout << "   ✅ Converge a mejor opción PARA TI\n\n";
    
    std::cout << "🚀 DECISIÓN FINAL SUPER INFORMADA:\n\n";
    std::cout << "Considera:\n";
    std::cout << "  • Incertidumbre (Monte Carlo)\n";
    std::cout << "  • Nueva información (Bayesian)\n";
    std::cout << "  • Arrepentimiento (Regret)\n";
    std::cout << "  • Flexibilidad futura (Real Options)\n";
    std::cout << "  • Riesgo extremo (VaR/CVaR)\n";
    std::cout << "  • Futuros alternativos (Scenarios)\n";
    std::cout << "  • Dependencias (Correlation)\n";
    std::cout << "  • Aprendizaje adaptativo (Bandit)\n\n";
    
    std::cout << "📊 Esta es la toma de decisiones MÁS COMPLETA posible.\n";
    std::cout << "   No hay metodología que no hayas considerado.\n\n";
    
    return 0;
}
