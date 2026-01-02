/**
 * @file furniture_diy_analysis.cpp
 * @brief Análisis C++: ¿Hacer mueble DIY o Comprar?
 * 
 * Especificaciones:
 * - 60cm alto × 60cm ancho × 1.8m largo
 * - Uso: Mesón bebé + almacenamiento
 * - Similar: Rack TV
 * 
 * Opciones:
 * 1. DIY completo (construir desde cero)
 * 2. Comprar en tienda (Sodimac/Falabella)
 * 3. Encargar carpintero
 * 4. Kit DIY (armar)
 */

#include <iostream>
#include <iomanip>
#include <vector>
#include <string>
#include <numeric>
#include <algorithm>
#include <random>

struct FurnitureOption {
    std::string name;
    std::string description;
    
    double cost;  // En CLP
    double probability_success;
    int timeline_days;
    
    // Factores (0-10)
    double learning_opportunity;
    double quality_expected;
    double time_effort;  // Inverso: 10=poco esfuerzo, 1=mucho
    double customization;
    double satisfaction;
    double future_utility;  // Habilidad para futuro
    double safety;  // Seguridad para bebé
    
    // Riesgos (0-1)
    double risk_fail;  // Que salga mal
    double risk_cost_overrun;  // Que cueste más
    double risk_time_overrun;  // Que tarde más
};

std::vector<FurnitureOption> create_options() {
    std::vector<FurnitureOption> options;
    
    // DIY completo
    options.push_back({
        "DIY - Construir yo mismo",
        "Comprar materiales (MDF/melamina) y construir desde cero",
        150'000.0,  // Materiales
        0.60,       // 60% probabilidad éxito (sin experiencia)
        14,         // 2 semanas (fines semana)
        9.0,        // learning_opportunity ✅✅
        6.0,        // quality (puede quedar irregular)
        3.0,        // time_effort (mucho esfuerzo)
        10.0,       // customization ✅✅ (100% a medida)
        8.0,        // satisfaction (orgullo de hacerlo)
        8.0,        // future_utility (habilidad útil)
        6.0,        // safety (puede tener astillas, bordes)
        0.40,       // risk_fail (40% riesgo mal resultado)
        0.30,       // risk_cost (materiales extra, herramientas)
        0.40        // risk_time (puede tardar más)
    });
    
    // Comprar en tienda
    options.push_back({
        "Comprar - Rack tienda (Sodimac/Falabella)",
        "Comprar rack TV similar ya hecho",
        300'000.0,
        0.95,
        1,  // 1 día (comprar y listo)
        2.0,  // learning (no aprendes)
        8.0,  // quality ✅ (fabricado profesional)
        10.0, // time_effort ✅✅ (cero esfuerzo)
        5.0,  // customization (medidas estándar)
        6.0,  // satisfaction (normal)
        3.0,  // future_utility (no desarrollas habilidad)
        9.0,  // safety ✅✅ (cumple normas)
        0.05, // risk_fail (muy bajo, garantía)
        0.10, // risk_cost (precio fijo)
        0.05  // risk_time (inmediato)
    });
    
    // Carpintero a medida
    options.push_back({
        "Encargar - Carpintero profesional",
        "Diseño a medida, carpintero construye",
        400'000.0,
        0.85,
        21,  // 3 semanas
        4.0,  // learning (aprendes viendo)
        9.0,  // quality ✅✅ (profesional)
        9.0,  // time_effort ✅ (poco esfuerzo tuyo)
        9.0,  // customization ✅✅ (exacto a medida)
        8.0,  // satisfaction (profesional, personalizado)
        4.0,  // future_utility (no desarrollas mucho)
        9.5,  // safety ✅✅✅ (profesional)
        0.15, // risk_fail (depende carpintero)
        0.25, // risk_cost (puede cobrar más)
        0.20  // risk_time (puede atrasarse)
    });
    
    // Kit DIY
    options.push_back({
        "Kit DIY - Comprar kit para armar",
        "Kit tipo Ikea con instrucciones",
        200'000.0,
        0.80,
        1,  // 1 día (armar)
        6.0,  // learning (aprendes ensamblaje)
        7.5,  // quality (bueno pero estándar)
        7.0,  // time_effort (moderado)
        6.0,  // customization (limitado)
        7.0,  // satisfaction (logro moderado)
        6.0,  // future_utility (útil)
        8.5,  // safety ✅ (diseñado profesional)
        0.10, // risk_fail (instrucciones claras)
        0.15, // risk_cost (puede faltar piezas)
        0.15  // risk_time (puede tardar más si confundes)
    });
    
    return options;
}

double calculate_score(const FurnitureOption& opt) {
    // Criterios ponderados para decisión mueble
    double factor_score = (
        opt.learning_opportunity * 0.10 +   // Aprender es bueno pero no crítico
        opt.quality_expected * 0.25 +       // ⭐ Calidad muy importante
        opt.time_effort * 0.15 +            // Esfuerzo importa
        opt.customization * 0.10 +          // Personalización
        opt.satisfaction * 0.15 +           // Satisfacción
        opt.future_utility * 0.05 +         // Utilidad futura
        opt.safety * 0.20                   // ⭐ Seguridad bebé MUY importante
    );
    
    // Penalización riesgo
    double risk_score = (
        opt.risk_fail * 0.50 +              // Que salga mal es crítico
        opt.risk_cost_overrun * 0.30 +      // Sobrecosto
        opt.risk_time_overrun * 0.20        // Retraso
    );
    
    // Ajuste por costo (normalizar 100k-500k a 0-10, inverso)
    double cost_factor = 1.0 - ((opt.cost - 100'000) / 400'000);
    cost_factor = std::max(0.5, std::min(1.0, cost_factor));  // Clamp 0.5-1.0
    
    double base_score = (factor_score - risk_score * 5.0) * cost_factor;
    double final_score = base_score * opt.probability_success;
    
    return final_score;
}

struct MonteCarloResult {
    double mean_cost;
    double worst_cost;  // VaR95
    double best_cost;
    double mean_days;
    double worst_days;
};

MonteCarloResult simulate_option(const FurnitureOption& opt, int iterations = 40'000) {
    std::random_device rd;
    std::mt19937 gen(rd());
    
    std::vector<double> costs;
    std::vector<double> days;
    costs.reserve(iterations);
    days.reserve(iterations);
    
    std::normal_distribution<double> cost_dist(opt.cost, opt.cost * 0.20);
    std::normal_distribution<double> days_dist(opt.timeline_days, opt.timeline_days * 0.30);
    std::uniform_real_distribution<double> success_dist(0.0, 1.0);
    
    for (int i = 0; i < iterations; ++i) {
        if (success_dist(gen) > opt.probability_success) {
            // Falla: costo aumenta (rehacer o comprar alternativa)
            costs.push_back(opt.cost * 1.5);
            days.push_back(opt.timeline_days * 2.0);
        } else {
            double sim_cost = cost_dist(gen);
            double sim_days = days_dist(gen);
            
            // Ajuste por riesgos
            sim_cost *= (1.0 + opt.risk_cost_overrun * 0.5);
            sim_days *= (1.0 + opt.risk_time_overrun * 0.5);
            
            costs.push_back(std::max(opt.cost * 0.7, sim_cost));
            days.push_back(std::max(1.0, sim_days));
        }
    }
    
    std::sort(costs.begin(), costs.end());
    std::sort(days.begin(), days.end());
    
    MonteCarloResult result;
    result.mean_cost = std::accumulate(costs.begin(), costs.end(), 0.0) / iterations;
    result.worst_cost = costs[static_cast<int>(iterations * 0.95)];
    result.best_cost = costs[static_cast<int>(iterations * 0.05)];
    
    result.mean_days = std::accumulate(days.begin(), days.end(), 0.0) / iterations;
    result.worst_days = days[static_cast<int>(iterations * 0.95)];
    
    return result;
}

void print_header() {
    std::cout << "\n" << std::string(70, '=') << "\n";
    std::cout << "   🔨 ANÁLISIS C++: Mueble DIY vs Comprar\n";
    std::cout << std::string(70, '=') << "\n\n";
    
    std::cout << "📋 Especificaciones:\n";
    std::cout << "   • Tamaño: 60cm alto × 60cm ancho × 1.8m largo\n";
    std::cout << "   • Uso: Mesón bebé + almacenamiento\n";
    std::cout << "   • Similar: Rack TV\n\n";
}

void print_criteria() {
    std::cout << std::string(70, '=') << "\n";
    std::cout << "   📊 CRITERIOS C++ FRAMEWORK\n";
    std::cout << std::string(70, '=') << "\n\n";
    
    std::cout << "1️⃣ FACTORES (0-10):\n";
    std::cout << "   • Quality Expected:      25% ⭐ (muy importante)\n";
    std::cout << "   • Safety (bebé):         20% ⭐ (crítico)\n";
    std::cout << "   • Time/Effort:           15%\n";
    std::cout << "   • Satisfaction:          15%\n";
    std::cout << "   • Learning:              10%\n";
    std::cout << "   • Customization:         10%\n";
    std::cout << "   • Future Utility:         5%\n\n";
    
    std::cout << "2️⃣ RIESGOS (0-1):\n";
    std::cout << "   • Risk Fail:             50% (que salga mal)\n";
    std::cout << "   • Risk Cost Overrun:     30% (que cueste más)\n";
    std::cout << "   • Risk Time Overrun:     20% (que tarde más)\n\n";
    
    std::cout << "3️⃣ COSTO: Ajuste inverso (más barato = mejor)\n\n";
    
    std::cout << "4️⃣ MONTE CARLO: 40,000 sims costo y tiempo\n\n";
    
    std::cout << std::string(70, '=') << "\n\n";
}

int main() {
    print_header();
    print_criteria();
    
    auto options = create_options();
    
    std::cout << "📋 Opciones a evaluar:\n\n";
    for (size_t i = 0; i < options.size(); ++i) {
        const auto& opt = options[i];
        std::cout << (i + 1) << ". " << opt.name << "\n";
        std::cout << "   💰 $" << std::fixed << std::setprecision(0) << opt.cost;
        std::cout << " | 🎯 " << (int)(opt.probability_success * 100) << "% éxito";
        std::cout << " | ⏱️ " << opt.timeline_days << " días\n";
        std::cout << "   📝 " << opt.description << "\n\n";
    }
    
    std::cout << "🔄 Ejecutando análisis C++...\n";
    std::cout << "   • Monte Carlo: 40,000 iteraciones\n";
    std::cout << "   • Simulando costos y tiempo reales\n\n";
    
    std::vector<MonteCarloResult> mc_results;
    std::vector<double> scores;
    
    for (const auto& opt : options) {
        std::cout << "   ▶ " << opt.name << "...\n";
        auto mc = simulate_option(opt, 40'000);
        mc_results.push_back(mc);
        scores.push_back(calculate_score(opt));
    }
    
    // Ranking
    std::vector<size_t> indices(options.size());
    std::iota(indices.begin(), indices.end(), 0);
    std::sort(indices.begin(), indices.end(), [&](size_t a, size_t b) {
        return scores[a] > scores[b];
    });
    
    std::cout << "\n" << std::string(70, '=') << "\n";
    std::cout << "   📊 RESULTADOS C++\n";
    std::cout << std::string(70, '=') << "\n\n";
    
    for (size_t rank = 0; rank < indices.size(); ++rank) {
        size_t idx = indices[rank];
        const auto& opt = options[idx];
        const auto& mc = mc_results[idx];
        
        std::string emoji = rank == 0 ? "🥇" : rank == 1 ? "🥈" : rank == 2 ? "🥉" : "  ";
        
        std::cout << emoji << " RANK " << (rank + 1) << ": " << opt.name << "\n";
        std::cout << "   📊 Score C++: " << std::fixed << std::setprecision(2) << scores[idx] << "/10";
        
        if (scores[idx] >= 7.0) std::cout << " ✅✅ EXCELENTE";
        else if (scores[idx] >= 5.0) std::cout << " ✅ RECOMENDADO";
        else if (scores[idx] >= 3.0) std::cout << " ⚠️ VIABLE";
        
        std::cout << "\n";
        std::cout << "   💰 Costo base: $" << std::setprecision(0) << opt.cost << "\n";
        std::cout << "   📈 Monte Carlo:\n";
        std::cout << "      Costo mean: $" << (int)mc.mean_cost << "\n";
        std::cout << "      Costo worst (VaR95): $" << (int)mc.worst_cost << "\n";
        std::cout << "      Días mean: " << (int)mc.mean_days << " días\n";
        std::cout << "      Días worst: " << (int)mc.worst_days << " días\n";
        
        std::cout << "   ⚖️ Factores clave:\n";
        std::cout << "      Quality: " << opt.quality_expected << "/10";
        std::cout << " | Safety: " << opt.safety << "/10";
        std::cout << " | Learning: " << opt.learning_opportunity << "/10\n";
        
        std::cout << "   ⚠️ Riesgos:\n";
        std::cout << "      Fail " << (int)(opt.risk_fail * 100) << "%";
        std::cout << " | Cost+ " << (int)(opt.risk_cost_overrun * 100) << "%";
        std::cout << " | Time+ " << (int)(opt.risk_time_overrun * 100) << "%\n\n";
    }
    
    // Análisis ganador
    size_t winner_idx = indices[0];
    const auto& winner = options[winner_idx];
    const auto& winner_mc = mc_results[winner_idx];
    
    std::cout << std::string(70, '=') << "\n";
    std::cout << "   🏆 GANADOR C++\n";
    std::cout << std::string(70, '=') << "\n\n";
    
    std::cout << "   " << winner.name << "\n";
    std::cout << "   Score: " << std::setprecision(2) << scores[winner_idx] << "/10\n\n";
    
    std::cout << "   ✅ Por qué gana:\n";
    std::cout << "      • Quality: " << winner.quality_expected << "/10\n";
    std::cout << "      • Safety: " << winner.safety << "/10 (bebé)\n";
    std::cout << "      • Costo esperado: $" << std::setprecision(0) << (int)winner_mc.mean_cost << "\n";
    std::cout << "      • Tiempo: " << (int)winner_mc.mean_days << " días\n";
    std::cout << "      • Riesgo falla: " << (int)(winner.risk_fail * 100) << "%\n\n";
    
    std::cout << std::string(70, '=') << "\n\n";
    
    std::cout << "✨ Análisis C++ completado\n\n";
    
    return 0;
}
