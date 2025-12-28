#ifndef VALUE_AT_RISK_H
#define VALUE_AT_RISK_H

#include <vector>
#include <string>
#include <cmath>
#include <algorithm>

namespace decision_maker {

/**
 * Distribución de posibles resultados
 */
struct OutcomeDistribution {
    std::vector<double> outcomes;  // Resultados ordenados
    double min_value;
    double max_value;
    double mean;
    double median;
    double std_dev;
};

/**
 * Análisis Value at Risk
 */
struct ValueAtRiskResult {
    double var_95;              // Máxima pérdida al 95% confianza
    double var_90;              // Máxima pérdida al 90% confianza
    double var_99;              // Máxima pérdida al 99% confianza
    double expected_shortfall;  // Pérdida esperada condicionada (CVaR)
    double probability_loss;    // Probabilidad de pérdida
    double probability_gain;    // Probabilidad de ganancia
    std::string risk_level;     // BAJO, MEDIO, ALTO, CRÍTICO
    std::string recommendation; // Recomendación basada en riesgo
};

/**
 * Simulador de distribución usando Monte Carlo
 */
class ValueAtRiskAnalyzer {
public:
    ValueAtRiskAnalyzer();
    
    /**
     * Crear distribución de outcomes a partir de parámetros
     */
    OutcomeDistribution create_outcome_distribution(
        double expected_value,
        double std_dev,
        int num_simulations = 10000
    );
    
    /**
     * Analizar riesgo de un portafolio/decisión
     */
    ValueAtRiskResult analyze_risk(
        const OutcomeDistribution& distribution,
        double confidence_level = 0.95
    );
    
    /**
     * Comparar riesgo entre múltiples escenarios
     */
    struct RiskComparison {
        std::string scenario_name;
        ValueAtRiskResult var_result;
        double risk_score;  // 0-1, donde 1 es máximo riesgo
    };
    
    std::vector<RiskComparison> compare_scenarios(
        const std::vector<std::pair<std::string, OutcomeDistribution>>& scenarios
    );
    
    /**
     * Análisis de tolerancia al riesgo
     */
    struct RiskTolerance {
        double maximum_acceptable_loss;
        bool is_acceptable;
        std::string explanation;
    };
    
    RiskTolerance check_risk_tolerance(
        const ValueAtRiskResult& var_result,
        double max_acceptable_loss
    );
    
    /**
     * Generar reporte completo
     */
    std::string generate_var_report(
        const ValueAtRiskResult& var_result,
        const OutcomeDistribution& distribution
    ) const;
    
private:
    // Semilla para generador de números aleatorios
    unsigned int random_seed;
    
    // Métodos privados
    double normal_random(double mean, double std_dev);
    double percentile(const std::vector<double>& sorted_data, double percentile) const;
    std::string classify_risk_level(double var_95) const;
};

} // namespace decision_maker

#endif // VALUE_AT_RISK_H
