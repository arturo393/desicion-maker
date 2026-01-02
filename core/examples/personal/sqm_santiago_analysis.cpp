/**
 * @file sqm_santiago_analysis.cpp
 * @brief Análisis SQM Santiago con C++ Framework
 * 
 * Compara:
 * 1. SQM Santiago
 * 2. Minería Híbrida 
 * 3. Minería Faena
 * 4. UQOMM Actual
 * 5. Remoto Internacional
 * 
 * CRITERIOS DE EVALUACIÓN EXPLICADOS:
 * 
 * 1. MONTE CARLO SIMULATION (40,000 iteraciones)
 *    - Simula incertidumbre real del salario
 *    - Distribución Normal: μ=salary, σ=15% salary
 *    - Probabilidad éxito: Uniform distribution
 *    - Ajusta por burnout y WLB
 * 
 * 2. SCORE CALCULATION
 *    - Weighted average de 7 factores:
 *      * Tech Growth: 15%
 *      * Income Stability: 15%
 *      * Work-Life Balance: 20% (peso más alto)
 *      * Prestige: 10%
 *      * Remote Flexibility: 10%
 *      * Learning Opportunity: 15%
 *      * Career Ceiling: 15%
 *    
 *    - Risk Penalty (resta):
 *      * Unemployment Risk: 40%
 *      * Burnout Risk: 35% 
 *      * Market Risk: 25%
 *    
 *    - Multiplica por probabilidad éxito
 * 
 * 3. VALUE AT RISK (VaR) y CVaR
 *    - VaR95: Peor caso del 5% (downside risk)
 *    - CVaR: Expected shortfall (promedio 5% peor)
 *    - Cuantifica riesgo real financiero
 */

#include "../../src/framework/unified_decision_framework.h"
#include <iostream>
#include <iomanip>
#include <vector>
#include <string>
#include <numeric>
#include <algorithm>
#include <random>

using namespace DecisionFramework;

// Estructura para resultados Monte Carlo
struct MonteCarloResult {
    int iterations;
    double mean;
    double percentile_25;
    double percentile_50;
    double percentile_75;
    double min;
    double max;
    double std_dev;  // CVaR
};

// Estructura para opciones de carrera
struct CareerOption {
    std::string name;
    std::string description;
    
    // Financiero
    double salary;
    double probability_success;
    int timeline_months;
    
    // Factores (0-10)
    double tech_growth;
    double income_stability;
    double work_life_balance;
    double prestige;
    double remote_flexibility;
    double learning_opportunity;
    double career_ceiling;
    
    // Riesgos (0-1)
    double unemployment_risk;
    double burnout_risk;
    double market_risk;
};

std::vector<CareerOption> create_options() {
    std::vector<CareerOption> options;
    
    // SQM SANTIAGO (nueva opción)
    options.push_back({
        "SQM Santiago - Ingeniero Senior",
        "Líder mundial litio. Salario top, Santiago, híbrido, prestigio máximo",
        4'800'000.0,  // salary
        0.70,         // probability_success
        3,            // timeline_months
        8.5,          // tech_growth
        9.5,          // income_stability ✅
        8.5,          // work_life_balance ✅✅
        9.5,          // prestige ✅✅
        7.0,          // remote_flexibility ✅
        9.0,          // learning_opportunity
        9.0,          // career_ceiling
        0.05,         // unemployment_risk ✅ (muy bajo)
        0.15,         // burnout_risk ✅ (muy bajo)
        0.15          // market_risk (litio en auge)
    });
    
    // Minería Híbrida
    options.push_back({
        "Minería Híbrida - 2 años + Transición",
        "2 años faena → remoto internacional",
        4'500'000.0,
        0.75,
        3,
        8.5,
        9.0,
        6.0,
        9.0,
        4.0,
        9.0,
        9.5,
        0.10,
        0.25,
        0.15
    });
    
    // Minería Faena
    options.push_back({
        "Minería Faena - Norte Chile",
        "Turnos 7x7, Antofagasta/Calama. Alto salario, lejos familia",
        4'500'000.0,
        0.75,
        3,
        7.5,
        9.0,
        5.0,
        8.5,
        2.0,
        8.0,
        9.0,
        0.15,
        0.35,
        0.20
    });
    
    // UQOMM Actual
    options.push_back({
        "UQOMM - Actual",
        "Status quo. Seguro pero limitado",
        2'600'000.0,
        1.0,
        0,
        6.0,
        7.0,
        8.0,
        6.0,
        7.0,
        6.0,
        6.0,
        0.10,
        0.20,
        0.25
    });
    
    // Remoto Internacional
    options.push_back({
        "Remoto Internacional",
        "Tech remoto USA/Europa. Alto salario USD, 100% remoto",
        5'500'000.0,
        0.50,
        6,
        9.0,
        6.0,
        9.0,
        8.0,
        10.0,
        9.0,
        9.5,
        0.30,
        0.40,
        0.35
    });
    
    return options;
}

// Calcular score
double calculate_score(const CareerOption& opt) {
    // CRITERIO 1: Weighted factor score
    double factor_score = (
        opt.tech_growth * 0.15 +
        opt.income_stability * 0.15 +
        opt.work_life_balance * 0.20 +  // Peso más alto
        opt.prestige * 0.10 +
        opt.remote_flexibility * 0.10 +
        opt.learning_opportunity * 0.15 +
        opt.career_ceiling * 0.15
    );
    
    // CRITERIO 2: Risk penalty
    double risk_score = (
        opt.unemployment_risk * 0.4 +
        opt.burnout_risk * 0.35 +
        opt.market_risk * 0.25
    );
    
    // CRITERIO 3: Combine y normalizar (0-10)
    double base_score = (factor_score - risk_score * 5.0);
    
    // CRITERIO 4: Ajustar por probabilidad éxito
    double final_score = base_score * opt.probability_success;
    
    return final_score;
}

// Monte Carlo simulation
MonteCarloResult simulate_option(const CareerOption& opt, int iterations = 40'000) {
    std::random_device rd;
    std::mt19937 gen(rd());
    
    std::vector<double> outcomes;
    outcomes.reserve(iterations);
    
    // CRITERIO 5: Distribuciones de probabilidad
    
    // Salario: Normal distribution (realista)
    std::normal_distribution<double> salary_dist(
        opt.salary, 
        opt.salary * 0.15  // 15% std dev
    );
    
    // Éxito: Uniform distribution
    std::uniform_real_distribution<double> success_dist(0.0, 1.0);
    
    for (int i = 0; i < iterations; ++i) {
        // CRITERIO 6: Simular éxito/fracaso
        if (success_dist(gen) > opt.probability_success) {
            // No consigue: mantiene actual ($2.6M)
            outcomes.push_back(2'600'000.0);
        } else {
            // Consigue: salary con variación
            double simulated_salary = salary_dist(gen);
            
            // CRITERIO 7: Ajustar por factores psicológicos
            
            // Burnout reduce satisfacción efectiva
            double burnout_factor = 1.0 - (opt.burnout_risk * 0.5);
            
            // WLB afecta "valor percibido"
            double wlb_factor = opt.work_life_balance / 10.0;
            
            // Valor ajustado
            double adjusted_value = simulated_salary * burnout_factor * wlb_factor;
            outcomes.push_back(adjusted_value);
        }
    }
    
    // CRITERIO 8: Calcular estadísticas
    std::sort(outcomes.begin(), outcomes.end());
    
    MonteCarloResult result;
    result.iterations = iterations;
    result.mean = std::accumulate(outcomes.begin(), outcomes.end(), 0.0) / iterations;
    
    result.percentile_25 = outcomes[iterations * 0.25];
    result.percentile_50 = outcomes[iterations * 0.50];
    result.percentile_75 = outcomes[iterations * 0.75];
    
    // CRITERIO 9: VaR y CVaR (risk metrics)
    int var_index = static_cast<int>(iterations * 0.05);  // VaR 95%
    result.min = outcomes[var_index];
    result.max = outcomes[iterations - 1];
    
    // CVaR (expected shortfall - promedio del 5% peor)
    double cvar_sum = 0.0;
    for (int i = 0; i < var_index; ++i) {
        cvar_sum += outcomes[i];
    }
    result.std_dev = cvar_sum / var_index;  // Reusing field
    
    return result;
}

void print_criteria() {
    std::cout << "\n" << std::string(70, '=') << "\n";
    std::cout << "   📋 CRITERIOS DE EVALUACIÓN C++ FRAMEWORK\n";
    std::cout << std::string(70, '=') << "\n\n";
    
    std::cout << "1️⃣ FACTORES EVALUADOS (0-10 scale)\n";
    std::cout << "   ─────────────────────────────────\n";
    std::cout << "   • Tech Growth:           15% peso\n";
    std::cout << "   • Income Stability:      15% peso\n";
    std::cout << "   • Work-Life Balance:     20% peso ⭐ (más importante)\n";
    std::cout << "   • Prestige:              10% peso\n";
    std::cout << "   • Remote Flexibility:    10% peso\n";
    std::cout << "   • Learning Opportunity:  15% peso\n";
    std::cout << "   • Career Ceiling:        15% peso\n\n";
    
    std::cout << "2️⃣ RIESGOS EVALUADOS (0-1 scale)\n";
    std::cout << "   ─────────────────────────────\n";
    std::cout << "   • Unemployment Risk:     40% peso (desempleo)\n";
    std::cout << "   • Burnout Risk:          35% peso (agotamiento)\n";
    std::cout << "   • Market Risk:           25% peso (mercado)\n";
    std::cout << "   → Penalizan el score final\n\n";
    
    std::cout << "3️⃣ MONTE CARLO SIMULATION (40,000 iteraciones)\n";
    std::cout << "   ───────────────────────────────────────────\n";
    std::cout << "   • Distribución Normal: Salario ± 15% std dev\n";
    std::cout << "   • Distribución Uniform: Probabilidad éxito\n";
    std::cout << "   • Ajuste Burnout: reduce valor 0-50%\n";
    std::cout << "   • Ajuste WLB: reduce valor según balance\n";
    std::cout << "   → Simula incertidumbre REAL\n\n";
    
    std::cout << "4️⃣ MÉTRICAS DE RIESGO\n";
    std::cout << "   ───────────────────\n";
    std::cout << "   • VaR 95%: Worst case 5% (downside risk)\n";
    std::cout << "   • CVaR: Expected shortfall (promedio 5% peor)\n";
    std::cout << "   • P25, P50, P75: Percentiles outcomes\n";
    std::cout << "   → Cuantifica riesgo financiero real\n\n";
    
    std::cout << "5️⃣ SCORE CALCULATION\n";
    std::cout << "   ──────────────────\n";
    std::cout << "   Score = (Factores ponderados - Risk penalty) × Prob. éxito\n";
    std::cout << "   \n";
    std::cout << "   Escala interpretación:\n";
    std::cout << "   • 7.0+ = Excelente (raro)\n";
    std::cout << "   • 5.0-7.0 = Bueno, recomendado ⭐\n";
    std::cout << "   • 3.0-5.0 = Viable, considerar\n";
    std::cout << "   • <3.0 = Revisar trade-offs\n\n";
    
    std::cout << std::string(70, '=') << "\n\n";
}

void print_header() {
    std::cout << "\n" << std::string(70, '=') << "\n";
    std::cout << "   🏢 ANÁLISIS C++: SQM Santiago + Comparación\n";
    std::cout << std::string(70, '=') << "\n";
}

void print_options(const std::vector<CareerOption>& options) {
    std::cout << "\n📋 Opciones a evaluar:\n\n";
    
    for (size_t i = 0; i < options.size(); ++i) {
        const auto& opt = options[i];
        std::cout << (i + 1) << ". " << opt.name << "\n";
        std::cout << "   💰 $" << std::fixed << std::setprecision(0) 
                  << opt.salary << " | 🎯 " << (int)(opt.probability_success * 100) << "%\n";
        std::cout << "   ⚖️  WLB: " << opt.work_life_balance << "/10"
                  << " | 🏠 Remote: " << opt.remote_flexibility << "/10"
                  << " | 🏆 Prestige: " << opt.prestige << "/10\n";
        std::cout << "   ⚠️  Burnout: " << (int)(opt.burnout_risk * 100) << "%"
                  << " | Unemployment: " << (int)(opt.unemployment_risk * 100) << "%\n";
        std::cout << "   📝 " << opt.description << "\n\n";
    }
}

void print_results(const std::vector<CareerOption>& options,
                   const std::vector<MonteCarloResult>& mc_results,
                   const std::vector<double>& scores) {
    
    std::cout << "\n" << std::string(70, '=') << "\n";
    std::cout << "   📊 RESULTADOS C++ FRAMEWORK\n";
    std::cout << std::string(70, '=') << "\n\n";
    
    // Crear ranking
    std::vector<size_t> indices(options.size());
    std::iota(indices.begin(), indices.end(), 0);
    std::sort(indices.begin(), indices.end(), [&](size_t a, size_t b) {
        return scores[a] > scores[b];
    });
    
    for (size_t rank = 0; rank < indices.size(); ++rank) {
        size_t idx = indices[rank];
        const auto& opt = options[idx];
        const auto& mc = mc_results[idx];
        
        std::string emoji = rank == 0 ? "🥇" : rank == 1 ? "🥈" : rank == 2 ? "🥉" : "  ";
        
        std::cout << emoji << " RANK " << (rank + 1) << ": " << opt.name << "\n";
        std::cout << "   📊 Score C++: " << std::fixed << std::setprecision(2) 
                  << scores[idx] << "/10";
        
        if (scores[idx] >= 7.0) {
            std::cout << " ✅✅ EXCELENTE";
        } else if (scores[idx] >= 5.0) {
            std::cout << " ✅ RECOMENDADO";
        } else if (scores[idx] >= 3.0) {
            std::cout << " ⚠️ VIABLE";
        }
        std::cout << "\n";
        
        std::cout << "   💰 Salario: $" << std::setprecision(0) << opt.salary << "\n";
        
        std::cout << "   📈 Monte Carlo (40,000 sims):\n";
        std::cout << "      Mean:  $" << (int)mc.mean << "\n";
        std::cout << "      P50:   $" << (int)mc.percentile_50 << "\n";
        std::cout << "      VaR95: $" << (int)mc.min << " (worst 5%)\n";
        std::cout << "      CVaR:  $" << (int)mc.std_dev << " (expected shortfall)\n";
        
        std::cout << "   ⚖️  Factores:\n";
        std::cout << "      WLB: " << opt.work_life_balance << "/10"
                  << " | Remote: " << opt.remote_flexibility << "/10"
                  << " | Prestige: " << opt.prestige << "/10\n";
        std::cout << "      Stability: " << opt.income_stability << "/10"
                  << " | Tech: " << opt.tech_growth << "/10\n";
        
        std::cout << "   ⚠️  Riesgos:\n";
        std::cout << "      Burnout " << (int)(opt.burnout_risk * 100) << "%"
                  << " | Unemployment " << (int)(opt.unemployment_risk * 100) << "%"
                  << " | Market " << (int)(opt.market_risk * 100) << "%\n\n";
    }
}

void analyze_sqm_specific(const CareerOption& sqm, 
                           const MonteCarloResult& sqm_mc,
                           double sqm_score) {
    
    std::cout << std::string(70, '=') << "\n";
    std::cout << "   🎯 ANÁLISIS DETALLADO: SQM SANTIAGO\n";
    std::cout << std::string(70, '=') << "\n\n";
    
    std::cout << "   📊 Score C++: " << std::fixed << std::setprecision(2) 
              << sqm_score << "/10\n\n";
    
    std::cout << "   💎 POR QUÉ ESTE SCORE:\n";
    std::cout << "   ─────────────────────\n\n";
    
    // Factor score breakdown
    double factor_score = (
        sqm.tech_growth * 0.15 +
        sqm.income_stability * 0.15 +
        sqm.work_life_balance * 0.20 +
        sqm.prestige * 0.10 +
        sqm.remote_flexibility * 0.10 +
        sqm.learning_opportunity * 0.15 +
        sqm.career_ceiling * 0.15
    );
    
    double risk_penalty = (
        sqm.unemployment_risk * 0.4 +
        sqm.burnout_risk * 0.35 +
        sqm.market_risk * 0.25
    ) * 5.0;
    
    std::cout << "   1. Factor Score (weighted): " << factor_score << "/10\n";
    std::cout << "      • Tech Growth: " << sqm.tech_growth << " × 15% = " 
              << (sqm.tech_growth * 0.15) << "\n";
    std::cout << "      • Stability: " << sqm.income_stability << " × 15% = " 
              << (sqm.income_stability * 0.15) << "\n";
    std::cout << "      • WLB: " << sqm.work_life_balance << " × 20% = " 
              << (sqm.work_life_balance * 0.20) << " ⭐\n";
    std::cout << "      • Prestige: " << sqm.prestige << " × 10% = " 
              << (sqm.prestige * 0.10) << "\n";
    std::cout << "      • Remote: " << sqm.remote_flexibility << " × 10% = " 
              << (sqm.remote_flexibility * 0.10) << "\n";
    std::cout << "      • Learning: " << sqm.learning_opportunity << " × 15% = " 
              << (sqm.learning_opportunity * 0.15) << "\n";
    std::cout << "      • Ceiling: " << sqm.career_ceiling << " × 15% = " 
              << (sqm.career_ceiling * 0.15) << "\n\n";
    
    std::cout << "   2. Risk Penalty: -" << std::setprecision(2) << risk_penalty << "\n";
    std::cout << "      • Unemployment: " << (sqm.unemployment_risk * 100) << "% ✅ (muy bajo)\n";
    std::cout << "      • Burnout: " << (sqm.burnout_risk * 100) << "% ✅ (muy bajo)\n";
    std::cout << "      • Market: " << (sqm.market_risk * 100) << "% ✅ (bajo)\n\n";
    
    std::cout << "   3. Base Score: " << (factor_score - risk_penalty) << "/10\n\n";
    
    std::cout << "   4. Ajuste probabilidad: × " << (sqm.probability_success * 100) << "%\n";
    std::cout << "      = " << sqm_score << "/10 (final)\n\n";
    
    std::cout << "   💰 ROI Esperado (vs UQOMM $2.6M):\n";
    std::cout << "   ──────────────────────────────────\n";
    std::cout << "   • Incremento: +$" << std::setprecision(0) 
              << (sqm.salary - 2'600'000) << "/mes (+85%)\n";
    std::cout << "   • Anual: +$" << ((sqm.salary - 2'600'000) * 12) << "\n";
    std::cout << "   • 3 años: +$" << ((sqm.salary - 2'600'000) * 36) << "\n\n";
    
    std::cout << "   📈 Monte Carlo Outcomes:\n";
    std::cout << "   ─────────────────────────\n";
    std::cout << "   • Mean: $" << (int)sqm_mc.mean 
              << " (valor esperado ajustado)\n";
    std::cout << "   • VaR95: $" << (int)sqm_mc.min 
              << " (peor 5% casos)\n";
    std::cout << "   • CVaR: $" << (int)sqm_mc.std_dev 
              << " (expected shortfall)\n\n";
    
    std::cout << std::string(70, '=') << "\n\n";
}

int main() {
    print_header();
    print_criteria();
    
    auto options = create_options();
    print_options(options);
    
    std::cout << "🔄 Ejecutando análisis C++...\n";
    std::cout << "   • Monte Carlo: 40,000 iteraciones\n";
    std::cout << "   • Criterios: 9 factores + VaR/CVaR\n\n";
    
    std::vector<MonteCarloResult> mc_results;
    std::vector<double> scores;
    
    for (const auto& opt : options) {
        std::cout << "   ▶ " << opt.name << "...\n";
        auto mc_result = simulate_option(opt, 40'000);
        mc_results.push_back(mc_result);
        
        double score = calculate_score(opt);
        scores.push_back(score);
    }
    
    print_results(options, mc_results, scores);
    
    // Análisis específico SQM
    analyze_sqm_specific(options[0], mc_results[0], scores[0]);
    
    std::cout << "✨ Análisis C++ completado\n\n";
    std::cout << "📊 Comparación con Python:\n";
    std::cout << "   Python SQM: 2.96/10 (conservador)\n";
    std::cout << "   C++ SQM:    " << std::fixed << std::setprecision(2) 
              << scores[0] << "/10 (realista)\n\n";
    
    return 0;
}
