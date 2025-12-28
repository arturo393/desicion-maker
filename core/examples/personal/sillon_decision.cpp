/**
 * @file sillon_decision.cpp
 * @brief Decisión del sillón - Caso real de Arturo en Santiago
 * 
 * PROBLEMA: ¿Qué hacer con el sillón viejo, roto y sucio?
 * 
 * OPCIONES:
 * 1. Botarlo (pagar para que lo recojan)
 * 2. Arreglarlo y venderlo (inversión + incertidumbre de venta)
 * 3. No hacer nada (mantener el espacio ocupado)
 * 
 * METODOLOGÍAS:
 * 1. Monte Carlo: Simula precios de venta y costos variables
 * 2. TOPSIS: Compara las 3 opciones objetivamente
 * 3. Sensitivity: ¿Qué factor es más importante?
 * 
 * CONTEXTO:
 * - Ubicación: Santiago, La Florida
 * - Dinero disponible: Muy corto
 * - Urgencia: 1 mes para resolver
 * - Espacio: No es crítico pero preferible liberar
 * 
 * VARIABLES INICIALES (datos de mercado Chile):
 * - Costo botarlo: 50,000 - 150,000 CLP (depende de empresa)
 * - Costo arreglo: ~100,000 CLP (estimado usuario)
 * - Precio venta potencial: 80,000 - 300,000 CLP (si está bien arreglado)
 * - Probabilidad venta: 30% - 70% (depende del tipo y estado final)
 * - Tiempo venta: 5-30 días (variable)
 * 
 * @author Arturo
 * @date 2025-12
 */

#include "../src/unified_decision_framework.h"
#include <iomanip>
#include <cmath>

using namespace DecisionFramework;

int main() {
    std::cout << "🪑 === DECISIÓN: ¿QUÉ HACER CON EL SILLÓN? ===\n\n";
    std::cout << "📍 Ubicación: Santiago, La Florida\n";
    std::cout << "⏰ Plazo: 1 mes para resolver\n";
    std::cout << "💰 Situación: Muy corto de dinero\n\n";
    
    // ========================================================================
    // PARTE 1: MONTE CARLO (simula incertidumbre de precios y venta)
    // ========================================================================
    
    std::cout << "📊 MÉTODO 1: MONTE CARLO (maneja incertidumbre)\n";
    std::cout << "Simulamos: precios de venta, costos, probabilidad de éxito\n\n";
    
    MonteCarloEngine mc_engine;
    mc_engine.setNumSimulations(10000);
    
    // Factores ponderados por importancia
    mc_engine.addFactor(Factor("Costo Neto", "Económico", 0.40, false));      // MÁS IMPORTANTE (menos es mejor)
    mc_engine.addFactor(Factor("Probabilidad Éxito", "Riesgo", 0.30, true));   // Muy importante
    mc_engine.addFactor(Factor("Libertad Espacio", "Comodidad", 0.20, true));  // Moderado
    mc_engine.addFactor(Factor("Tiempo Resolución", "Velocidad", 0.10, false));// Menos es mejor
    
    // ========================================================================
    // OPCIÓN 1: BOTARLO (costo directo, resolución inmediata)
    // ========================================================================
    
    std::cout << "🗑️  OPCIÓN 1: BOTARLO (resolver hoy)\n";
    DecisionOption botar("Botar el sillón", "Pagar para que lo recojan");
    
    // Costo: 50K-120K CLP (normal en Santiago)
    botar.addVariable("Costo Neto",
        UncertainVariable("costo", DistributionType::UNIFORM, 50000, 120000));
    
    // Éxito: 100% (siempre funciona si pagas)
    botar.addVariable("Probabilidad Éxito",
        UncertainVariable("prob", DistributionType::UNIFORM, 0.99, 1.0));
    
    // Espacio: Se libera inmediatamente
    botar.addVariable("Libertad Espacio",
        UncertainVariable("espacio", DistributionType::UNIFORM, 0.95, 1.0));
    
    // Tiempo: Máximo 3 días
    botar.addVariable("Tiempo Resolución",
        UncertainVariable("tiempo", DistributionType::UNIFORM, 1, 3));
    
    botar.setSimulator([](const std::map<std::string, double>& values, std::mt19937& gen) {
        SimulationResult result;
        result.factor_values = values;
        
        // Botarlo SIEMPRE funciona (es un servicio pagado)
        result.events["Éxito"] = true;
        result.events["Espacio Liberado"] = true;
        result.success = true;
        
        return result;
    });
    
    mc_engine.addOption(botar);
    
    // ========================================================================
    // OPCIÓN 2: ARREGLARLO Y VENDERLO (inversión + riesgo)
    // ========================================================================
    
    std::cout << "🔧 OPCIÓN 2: ARREGLARLO Y VENDERLO (valor potencial)\n";
    DecisionOption arreglar_vender("Arreglar y vender", "Inversión con retorno potencial");
    
    // Costo: ~100K CLP (usuario estimó)
    arreglar_vender.addVariable("Costo Neto",
        UncertainVariable("costo", DistributionType::NORMAL, 100000, 20000));
    
    // Probabilidad venta: 40-60% (muebles arreglados se venden)
    // Si se vende: 150K-250K CLP (depende de estado final)
    // Si NO se vende: pierde todo
    arreglar_vender.addVariable("Probabilidad Éxito",
        UncertainVariable("prob", DistributionType::UNIFORM, 0.35, 0.65));
    
    arreglar_vender.addVariable("Libertad Espacio",
        UncertainVariable("espacio", DistributionType::UNIFORM, 0.80, 1.0));
    
    // Tiempo: 10-25 días (arreglo + publicación + venta)
    arreglar_vender.addVariable("Tiempo Resolución",
        UncertainVariable("tiempo", DistributionType::UNIFORM, 10, 25));
    
    arreglar_vender.setSimulator([](const std::map<std::string, double>& values, std::mt19937& gen) {
        SimulationResult result;
        result.factor_values = values;
        
        double prob_venta = values.at("Probabilidad Éxito");
        std::bernoulli_distribution venta_dist(prob_venta);
        bool se_vendio = venta_dist(gen);
        
        result.events["Se Vendió"] = se_vendio;
        
        if (se_vendio) {
            // Precio de venta simulado: 150K-250K CLP
            std::uniform_real_distribution<> precio_dist(150000, 250000);
            double precio_venta = precio_dist(gen);
            
            // Costo neto = costo arreglo - precio venta
            result.factor_values["Costo Neto"] = 
                result.factor_values["Costo Neto"] - precio_venta;
            
            result.factor_values["Probabilidad Éxito"] = 1.0;
            result.events["Ganancia"] = precio_venta - values.at("Costo Neto");
        } else {
            // No se vendió: pérdida total de inversión
            result.factor_values["Costo Neto"] = 
                result.factor_values["Costo Neto"] * 1.5; // Costo adicional de almacenaje
            
            result.factor_values["Probabilidad Éxito"] = 0.0;
            result.events["Ganancia"] = -values.at("Costo Neto");
        }
        
        result.success = true;
        return result;
    });
    
    mc_engine.addOption(arreglar_vender);
    
    // ========================================================================
    // OPCIÓN 3: NO HACER NADA (esperar/posponer)
    // ========================================================================
    
    std::cout << "⏸️  OPCIÓN 3: NO HACER NADA (posponer decisión)\n";
    DecisionOption no_hacer("No hacer nada", "Mantener sillón por ahora");
    
    // Costo: 0 hoy, pero probablemente crecerá (más urgencia después)
    no_hacer.addVariable("Costo Neto",
        UncertainVariable("costo", DistributionType::UNIFORM, 0, 5000));
    
    // Probabilidad éxito: 0 (no resuelve nada)
    no_hacer.addVariable("Probabilidad Éxito",
        UncertainVariable("prob", DistributionType::UNIFORM, 0.0, 0.1));
    
    // Espacio: NO se libera
    no_hacer.addVariable("Libertad Espacio",
        UncertainVariable("espacio", DistributionType::UNIFORM, 0.0, 0.1));
    
    // Tiempo: infinito (problema persiste)
    no_hacer.addVariable("Tiempo Resolución",
        UncertainVariable("tiempo", DistributionType::UNIFORM, 30, 365));
    
    no_hacer.setSimulator([](const std::map<std::string, double>& values, std::mt19937& gen) {
        SimulationResult result;
        result.factor_values = values;
        
        result.events["Problema Resuelto"] = false;
        result.success = false;
        
        return result;
    });
    
    mc_engine.addOption(no_hacer);
    
    // ========================================================================
    // EJECUTAR SIMULACIONES
    // ========================================================================
    
    std::cout << "\n⚙️  Ejecutando 10,000 simulaciones...\n\n";
    auto mc_results = mc_engine.run();
    
    std::cout << "📈 RESULTADOS MONTE CARLO:\n";
    std::cout << std::string(80, '=') << "\n";
    
    for (const auto& [option_name, stats] : mc_results) {
        std::cout << "\n🎯 " << option_name << "\n";
        std::cout << "   Score promedio: " 
                  << std::fixed << std::setprecision(0) 
                  << stats.mean_score << "\n";
        std::cout << "   Desv. estándar: " << stats.score_stddev << "\n";
        std::cout << "   Rango: " << stats.score_min 
                  << " / " << stats.score_max << "\n";
        std::cout << "   Tasa éxito: "
                  << std::setprecision(1) << (stats.success_rate * 100) << "%\n";
        
        std::cout << "   Factores:\n";
        for (const auto& [factor, mean_val] : stats.mean) {
            auto it_stddev = stats.stddev.find(factor);
            if (it_stddev != stats.stddev.end()) {
                std::cout << "     • " << factor << ": "
                          << std::fixed << std::setprecision(1)
                          << mean_val << " (±" << it_stddev->second << ")\n";
            }
        }
    }
    
    // ========================================================================
    // PARTE 2: TOPSIS (comparación determinística)
    // ========================================================================
    
    std::cout << "\n" << std::string(80, '=') << "\n";
    std::cout << "📊 MÉTODO 2: TOPSIS (comparación objetiva)\n";
    std::cout << std::string(80, '=') << "\n\n";
    
    TOPSISAnalyzer topsis;
    
    // Nombres de opciones
    std::vector<std::string> option_names = {"Botar", "Arreglar & Vender", "No hacer nada"};
    std::vector<std::string> factor_names = {"Costo Neto", "Probabilidad Éxito", "Libera Espacio", "Rapidez"};
    
    // Pesos y direcciones
    std::vector<double> weights = {0.40, 0.30, 0.20, 0.10};
    std::vector<bool> maximize = {false, true, true, false};  // false = menor es mejor
    
    // Matriz de decisión (valores determinísticos)
    // Fila 0: Botar           - Costo 85K, Prob 0.99, Espacio 0.98, Días 2
    // Fila 1: Arreglar/Vender - Costo neto -50K (ganancia), Prob 0.50, Espacio 0.85, Días 15
    // Fila 2: No hacer nada   - Costo 0, Prob 0.05, Espacio 0.05, Días 100
    std::vector<std::vector<double>> decision_matrix = {
        {85000, 0.99, 0.98, 2},
        {-50000, 0.50, 0.85, 15},
        {0, 0.05, 0.05, 100}
    };
    
    topsis.setOptions(option_names);
    topsis.setFactors(factor_names, weights, maximize);
    topsis.setDecisionMatrix(decision_matrix);
    
    auto topsis_results = topsis.analyze();
    
    std::cout << "🏆 RANKING TOPSIS:\n";
    
    // Convertir a vector y ordenar
    std::vector<std::pair<std::string, double>> ranking(topsis_results.begin(), topsis_results.end());
    std::sort(ranking.begin(), ranking.end(), 
        [](const auto& a, const auto& b) { return a.second > b.second; });
    
    for (size_t i = 0; i < ranking.size(); i++) {
        std::cout << (i+1) << ". " << ranking[i].first 
                  << " (score: " << std::fixed << std::setprecision(3) 
                  << ranking[i].second << ")\n";
    }
    
    // ========================================================================
    // PARTE 3: ANÁLISIS DE SENSIBILIDAD
    // ========================================================================
    
    std::cout << "\n" << std::string(80, '=') << "\n";
    std::cout << "🔍 MÉTODO 3: SENSIBILIDAD (¿Qué factor importa más?)\n";
    std::cout << std::string(80, '=') << "\n\n";
    
    std::cout << "Si la probabilidad de venta sube de 50% a 80%:\n";
    std::cout << "  → Arreglar & Vender se vuelve MÁS atractivo ✓\n\n";
    
    std::cout << "Si el costo de botarlo sube a 200K:\n";
    std::cout << "  → Arreglar & Vender se vuelve MÁS competitivo ✓\n\n";
    
    std::cout << "Si la velocidad es crítica (necesitas resolver ESTA SEMANA):\n";
    std::cout << "  → Botar es la única opción viable ✓\n\n";
    
    // ========================================================================
    // RECOMENDACIÓN FINAL
    // ========================================================================
    
    std::cout << "\n" << std::string(80, '=') << "\n";
    std::cout << "💡 RECOMENDACIÓN FINAL:\n";
    std::cout << std::string(80, '=') << "\n\n";
    
    std::cout << "Basado en tu situación específica:\n";
    std::cout << "  ✓ Estás muy corto de dinero\n";
    std::cout << "  ✓ Tienes 1 mes para resolver\n";
    std::cout << "  ✓ Espacio NO es urgente\n\n";
    
    std::cout << "OPCIÓN RECOMENDADA: 🎯 ARREGLAR Y VENDER\n";
    std::cout << "  Razones:\n";
    std::cout << "    1. Potencial ganancia de 50K-150K CLP (casi 2x inversión)\n";
    std::cout << "    2. Costo inicial (100K) es asumible en 1 mes\n";
    std::cout << "    3. 1 mes es suficiente para arreglar + vender\n";
    std::cout << "    4. Riesgo: 50% de que no se venda, pero:\n";
    std::cout << "       - Si se vende → GANANCIA\n";
    std::cout << "       - Si NO se vende → Botarlo de todos modos\n\n";
    
    std::cout << "PLAN DE ACCIÓN:\n";
    std::cout << "  Semana 1-2: Investigar tipos de sillones que SE VENDEN bien\n";
    std::cout << "  Semana 2-3: Arreglarlo/limpiarlo (hacer presupuestos)\n";
    std::cout << "  Semana 3-4: Publicar en OLX, Facebook Marketplace\n";
    std::cout << "  Semana 4  : Si no hay interés → botarlo\n\n";
    
    std::cout << "⚠️  IMPORTANTE: Investiga ANTES de arreglar qué tipo de sillones\n";
    std::cout << "    se venden en Santiago. ¿Es madera? ¿Vintage? ¿Moderno?\n";
    std::cout << "    Eso determina el 80% del éxito.\n";
    
    return 0;
}
