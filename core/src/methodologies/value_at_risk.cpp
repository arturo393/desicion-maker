#include "value_at_risk.h"
#include <random>
#include <numeric>
#include <sstream>
#include <iomanip>
#include <cmath>

namespace decision_maker {

ValueAtRiskAnalyzer::ValueAtRiskAnalyzer()
    : random_seed(42) {}

double ValueAtRiskAnalyzer::normal_random(double mean, double std_dev) {
    static std::mt19937 generator(random_seed++);
    std::normal_distribution<double> distribution(mean, std_dev);
    return distribution(generator);
}

double ValueAtRiskAnalyzer::percentile(
    const std::vector<double>& sorted_data, double percentile) const {
    
    if (sorted_data.empty()) return 0.0;
    if (percentile <= 0.0) return sorted_data.front();
    if (percentile >= 1.0) return sorted_data.back();
    
    double index = percentile * (sorted_data.size() - 1);
    int lower = static_cast<int>(index);
    int upper = lower + 1;
    double weight = index - lower;
    
    if (upper >= static_cast<int>(sorted_data.size())) {
        return sorted_data.back();
    }
    
    return sorted_data[lower] * (1.0 - weight) + sorted_data[upper] * weight;
}

OutcomeDistribution ValueAtRiskAnalyzer::create_outcome_distribution(
    double expected_value,
    double std_dev,
    int num_simulations) {
    
    OutcomeDistribution dist;
    dist.outcomes.reserve(num_simulations);
    
    // Generar simulaciones con distribución normal
    for (int i = 0; i < num_simulations; i++) {
        double outcome = normal_random(expected_value, std_dev);
        dist.outcomes.push_back(outcome);
    }
    
    // Ordenar para cálculo de percentiles
    std::sort(dist.outcomes.begin(), dist.outcomes.end());
    
    // Calcular estadísticas
    dist.min_value = dist.outcomes.front();
    dist.max_value = dist.outcomes.back();
    
    dist.mean = std::accumulate(dist.outcomes.begin(), dist.outcomes.end(), 0.0)
                / dist.outcomes.size();
    
    dist.median = percentile(dist.outcomes, 0.5);
    
    // Desviación estándar
    double variance = 0.0;
    for (const auto& outcome : dist.outcomes) {
        variance += (outcome - dist.mean) * (outcome - dist.mean);
    }
    dist.std_dev = std::sqrt(variance / dist.outcomes.size());
    
    return dist;
}

ValueAtRiskResult ValueAtRiskAnalyzer::analyze_risk(
    const OutcomeDistribution& distribution,
    double confidence_level) {
    
    // VaR es el percentil inverso de la confianza
    // Para 95% confianza, buscamos el peor 5%
    double percentile_loss = 1.0 - confidence_level;
    
    double var_95 = percentile(distribution.outcomes, 0.05);
    double var_90 = percentile(distribution.outcomes, 0.10);
    double var_99 = percentile(distribution.outcomes, 0.01);
    
    // Expected Shortfall (CVaR): promedio de los peores outcomes
    int num_tail = std::max(1, static_cast<int>(distribution.outcomes.size() * percentile_loss));
    double shortfall = 0.0;
    for (int i = 0; i < num_tail; i++) {
        shortfall += distribution.outcomes[i];
    }
    double expected_shortfall = shortfall / num_tail;
    
    // Probabilidad de pérdida y ganancia
    int loss_count = 0;
    int gain_count = 0;
    for (const auto& outcome : distribution.outcomes) {
        if (outcome < 0) loss_count++;
        else if (outcome > 0) gain_count++;
    }
    
    double probability_loss = static_cast<double>(loss_count) / distribution.outcomes.size();
    double probability_gain = static_cast<double>(gain_count) / distribution.outcomes.size();
    
    // Clasificar nivel de riesgo
    std::string risk_level = classify_risk_level(var_95);
    
    // Generar recomendación
    std::string recommendation;
    if (probability_loss > 0.95) {
        recommendation = "⚠️ CRÍTICO: Pérdida casi segura. NO PROCEDER.";
    } else if (probability_loss > 0.80) {
        recommendation = "🔴 ALTO RIESGO: 80%+ probabilidad de pérdida. RECONSIDERAR.";
    } else if (probability_loss > 0.50) {
        recommendation = "🟠 RIESGO MODERADO: Más probable perder que ganar. CON PRECAUCIÓN.";
    } else if (probability_loss > 0.20) {
        recommendation = "🟡 RIESGO BAJO-MODERADO: Posible pérdida pero ganancia más probable.";
    } else {
        recommendation = "🟢 BAJO RIESGO: Ganancia muy probable. PROCEDER.";
    }
    
    return ValueAtRiskResult{
        var_95,
        var_90,
        var_99,
        expected_shortfall,
        probability_loss,
        probability_gain,
        risk_level,
        recommendation
    };
}

std::string ValueAtRiskAnalyzer::classify_risk_level(double var_95) const {
    // Clasificar según magnitud de pérdida potencial
    if (var_95 < -100000) {
        return "CRÍTICO";
    } else if (var_95 < -50000) {
        return "ALTO";
    } else if (var_95 < -10000) {
        return "MEDIO";
    } else {
        return "BAJO";
    }
}

std::vector<ValueAtRiskAnalyzer::RiskComparison> 
ValueAtRiskAnalyzer::compare_scenarios(
    const std::vector<std::pair<std::string, OutcomeDistribution>>& scenarios) {
    
    std::vector<RiskComparison> comparisons;
    
    double max_var = -1e9;
    for (const auto& scenario : scenarios) {
        auto var_result = analyze_risk(scenario.second);
        
        // Calcular risk score (0-1)
        double risk_score = 0.5;  // Base neutral
        
        // Factor 1: Probabilidad de pérdida
        risk_score += var_result.probability_loss * 0.4;
        
        // Factor 2: Magnitud de pérdida (normalizada)
        if (var_result.var_95 < -100000) {
            risk_score += 0.4;
        } else if (var_result.var_95 < -50000) {
            risk_score += 0.25;
        } else if (var_result.var_95 < 0) {
            risk_score += 0.1;
        }
        
        // Factor 3: Expected Shortfall
        risk_score -= (var_result.expected_shortfall / 100000) * 0.2;  // Limitar impacto
        
        risk_score = std::max(0.0, std::min(1.0, risk_score));
        
        comparisons.push_back({
            scenario.first,
            var_result,
            risk_score
        });
    }
    
    // Ordenar por risk_score (mayor riesgo primero)
    std::sort(comparisons.begin(), comparisons.end(),
              [](const RiskComparison& a, const RiskComparison& b) {
                  return a.risk_score > b.risk_score;
              });
    
    return comparisons;
}

ValueAtRiskAnalyzer::RiskTolerance ValueAtRiskAnalyzer::check_risk_tolerance(
    const ValueAtRiskResult& var_result,
    double max_acceptable_loss) {
    
    bool is_acceptable = var_result.var_95 >= max_acceptable_loss;
    
    std::stringstream ss;
    ss << "Pérdida máxima (95% confianza): $" << std::fixed << std::setprecision(0)
       << var_result.var_95 << "\n";
    ss << "Tolerancia máxima: $" << max_acceptable_loss << "\n";
    
    if (is_acceptable) {
        ss << "✅ DENTRO DE TOLERANCIA: El riesgo es aceptable.";
    } else {
        double excess = max_acceptable_loss - var_result.var_95;
        ss << "❌ FUERA DE TOLERANCIA: Excede por $" << (-excess);
    }
    
    return RiskTolerance{
        max_acceptable_loss,
        is_acceptable,
        ss.str()
    };
}

std::string ValueAtRiskAnalyzer::generate_var_report(
    const ValueAtRiskResult& var_result,
    const OutcomeDistribution& distribution) const {
    
    std::stringstream ss;
    
    ss << "╔════════════════════════════════════════════╗\n";
    ss << "║        VALUE AT RISK (VaR) ANALYSIS        ║\n";
    ss << "╚════════════════════════════════════════════╝\n\n";
    
    ss << "📊 VALUE AT RISK METRICS\n";
    ss << std::string(45, '-') << "\n";
    ss << "VaR @ 95% confianza: $" << std::fixed << std::setprecision(0) 
       << var_result.var_95 << "\n";
    ss << "VaR @ 90% confianza: $" << var_result.var_90 << "\n";
    ss << "VaR @ 99% confianza: $" << var_result.var_99 << "\n";
    ss << "Expected Shortfall (CVaR): $" << var_result.expected_shortfall << "\n\n";
    
    ss << "📈 PROBABILITY ANALYSIS\n";
    ss << std::string(45, '-') << "\n";
    ss << "Probabilidad de pérdida: " << std::setprecision(2) 
       << (var_result.probability_loss * 100) << "%\n";
    ss << "Probabilidad de ganancia: " 
       << (var_result.probability_gain * 100) << "%\n";
    ss << "Riesgo: " << var_result.risk_level << "\n\n";
    
    ss << "📋 DISTRIBUTION STATISTICS\n";
    ss << std::string(45, '-') << "\n";
    ss << "Valor mínimo: $" << std::setprecision(0) 
       << distribution.min_value << "\n";
    ss << "Valor máximo: $" << distribution.max_value << "\n";
    ss << "Valor medio: $" << std::setprecision(0) 
       << distribution.mean << "\n";
    ss << "Valor mediano: $" << distribution.median << "\n";
    ss << "Desviación estándar: $" << distribution.std_dev << "\n\n";
    
    ss << "💡 RECOMMENDATION\n";
    ss << std::string(45, '-') << "\n";
    ss << var_result.recommendation << "\n";
    
    return ss.str();
}

} // namespace decision_maker
