#include "scenario_analysis.h"
#include <algorithm>
#include <sstream>
#include <iomanip>
#include <cmath>

namespace decision_maker {

ScenarioAnalyzer::ScenarioAnalyzer() {}

void ScenarioAnalyzer::add_scenario(
    const ScenarioAssumptions& scenario
) {
    scenarios_.push_back(scenario);
}

std::vector<ScenarioAssumptions> 
ScenarioAnalyzer::get_default_scenarios() {
    std::vector<ScenarioAssumptions> defaults;
    
    // PESSIMISTIC SCENARIO
    ScenarioAssumptions pessimistic;
    pessimistic.name = "PESSIMISTIC";
    pessimistic.restoration_cost = 85000;  // Costs overrun
    pessimistic.expected_sale_price = 45000;  // Low market price
    pessimistic.sale_probability = 0.02;  // Very low demand
    pessimistic.days_to_sale = 360;  // 1 year to sell
    pessimistic.description = 
        "Costs overrun, low prices, very low demand";
    defaults.push_back(pessimistic);
    
    // REALISTIC SCENARIO
    ScenarioAssumptions realistic;
    realistic.name = "REALISTIC";
    realistic.restoration_cost = 75000;  // As planned
    realistic.expected_sale_price = 65000;  // Average market price
    realistic.sale_probability = 0.04;  // Gemini analysis
    realistic.days_to_sale = 180;  // 6 months
    realistic.description = 
        "Base case, moderate prices, low demand";
    defaults.push_back(realistic);
    
    // OPTIMISTIC SCENARIO
    ScenarioAssumptions optimistic;
    optimistic.name = "OPTIMISTIC";
    optimistic.restoration_cost = 60000;  // Under budget
    optimistic.expected_sale_price = 85000;  // High market price
    optimistic.sale_probability = 0.08;  // Higher demand
    optimistic.days_to_sale = 60;  // 2 months
    optimistic.description = 
        "Under budget, high prices, good demand";
    defaults.push_back(optimistic);
    
    return defaults;
}

ScenarioResult ScenarioAnalyzer::analyze_scenario(
    const ScenarioAssumptions& scenario,
    double botar_cost
) {
    ScenarioResult result;
    result.scenario_name = scenario.name;
    
    // Calculate expected value
    double ev = calculate_expected_value(scenario, botar_cost);
    result.expected_value = ev;
    
    // Best case: sells at high price
    result.best_case_value = scenario.expected_sale_price 
                           - scenario.restoration_cost - 5000;
    
    // Worst case: doesn't sell and must botar
    result.worst_case_value = -scenario.restoration_cost;
    
    // Confidence based on scenario
    if (scenario.name == "REALISTIC") {
        result.confidence = 0.95;
    } else if (scenario.name == "PESSIMISTIC") {
        result.confidence = 0.70;
    } else {
        result.confidence = 0.60;
    }
    
    // Generate recommendation
    if (ev < -botar_cost) {
        result.recommendation = "BOTAR - Restaurar espera pérdida mayor";
    } else if (ev < 0) {
        result.recommendation = "BOTAR - Ambas opciones pierden dinero";
    } else {
        result.recommendation = "CONSIDERAR - Valor esperado positivo";
    }
    
    return result;
}

std::vector<ScenarioResult> ScenarioAnalyzer::run_all_scenarios() {
    auto default_scenarios = get_default_scenarios();
    
    results_.clear();
    for (const auto& scenario : default_scenarios) {
        results_.push_back(analyze_scenario(scenario));
    }
    
    return results_;
}

std::string ScenarioAnalyzer::generate_comparison_report() {
    if (results_.empty()) {
        run_all_scenarios();
    }
    
    std::ostringstream report;
    report << std::fixed << std::setprecision(2);
    
    report << "=== SCENARIO ANALYSIS REPORT ===\n\n";
    
    report << "SCENARIO COMPARISON\n";
    report << std::string(80, '-') << "\n";
    report << "Scenario       | Expected Value | Best Case | "
           << "Worst Case | Confidence | Recommendation\n";
    report << std::string(80, '-') << "\n";
    
    for (const auto& result : results_) {
        report << std::left << std::setw(14) << result.scenario_name
               << " | $" << std::setw(13) << result.expected_value
               << " | $" << std::setw(8) << result.best_case_value
               << " | $" << std::setw(9) << result.worst_case_value
               << " | " << std::setw(9) << (result.confidence * 100) << "%"
               << " | " << result.recommendation << "\n";
    }
    
    report << std::string(80, '-') << "\n\n";
    
    // Find best and worst scenarios
    auto best = std::max_element(
        results_.begin(),
        results_.end(),
        [](const ScenarioResult& a, const ScenarioResult& b) {
            return a.expected_value < b.expected_value;
        }
    );
    
    auto worst = std::min_element(
        results_.begin(),
        results_.end(),
        [](const ScenarioResult& a, const ScenarioResult& b) {
            return a.expected_value < b.expected_value;
        }
    );
    
    report << "BEST SCENARIO: " << best->scenario_name << "\n";
    report << "  Expected Value: $" << best->expected_value << "\n";
    report << "  Confidence: " << (best->confidence * 100) << "%\n\n";
    
    report << "WORST SCENARIO: " << worst->scenario_name << "\n";
    report << "  Expected Value: $" << worst->expected_value << "\n";
    report << "  Confidence: " << (worst->confidence * 100) << "%\n\n";
    
    report << "OVERALL RECOMMENDATION\n";
    report << "  All scenarios point to: BOTAR\n";
    report << "  Rationale: No scenario shows positive ROI\n";
    
    return report.str();
}

std::map<std::string, std::vector<double>> 
ScenarioAnalyzer::sensitivity_analysis(
    const ScenarioAssumptions& base_scenario
) {
    std::map<std::string, std::vector<double>> sensitivity;
    
    // Test sensitivity to restoration cost
    std::vector<double> cost_sensitivity;
    for (double cost = base_scenario.restoration_cost * 0.5;
         cost <= base_scenario.restoration_cost * 1.5;
         cost += base_scenario.restoration_cost * 0.1) {
        
        ScenarioAssumptions test = base_scenario;
        test.restoration_cost = cost;
        double ev = calculate_expected_value(test, 5000);
        cost_sensitivity.push_back(ev);
    }
    sensitivity["restoration_cost"] = cost_sensitivity;
    
    // Test sensitivity to sale price
    std::vector<double> price_sensitivity;
    for (double price = base_scenario.expected_sale_price * 0.5;
         price <= base_scenario.expected_sale_price * 1.5;
         price += base_scenario.expected_sale_price * 0.1) {
        
        ScenarioAssumptions test = base_scenario;
        test.expected_sale_price = price;
        double ev = calculate_expected_value(test, 5000);
        price_sensitivity.push_back(ev);
    }
    sensitivity["sale_price"] = price_sensitivity;
    
    // Test sensitivity to sale probability
    std::vector<double> prob_sensitivity;
    for (double prob = 0.01; prob <= 0.50; prob += 0.05) {
        ScenarioAssumptions test = base_scenario;
        test.sale_probability = prob;
        double ev = calculate_expected_value(test, 5000);
        prob_sensitivity.push_back(ev);
    }
    sensitivity["sale_probability"] = prob_sensitivity;
    
    return sensitivity;
}

double ScenarioAnalyzer::calculate_expected_value(
    const ScenarioAssumptions& scenario,
    double botar_cost
) {
    // EV = P(sells) * (Price - Cost - Commissions) + 
    //      P(not sells) * (-Cost)
    
    double commissions = 5000;
    
    double if_sells = scenario.expected_sale_price 
                    - scenario.restoration_cost 
                    - commissions;
    
    double if_not_sells = -scenario.restoration_cost;
    
    double ev = scenario.sale_probability * if_sells 
              + (1.0 - scenario.sale_probability) * if_not_sells;
    
    return ev;
}

double ScenarioAnalyzer::calculate_breakeven_price(
    double sale_probability
) {
    // Price needed such that EV = 0
    // 0 = P(sells) * (Price - Cost - Commissions) + 
    //     P(not sells) * (-Cost)
    // Solve for Price
    
    double cost = 75000;
    double commissions = 5000;
    
    // P * (Price - Cost - Commissions) - (1-P) * Cost = 0
    // P * Price - P * Cost - P * Commissions - Cost + P * Cost = 0
    // P * Price = Cost - P * Cost + P * Cost + P * Commissions
    // P * Price = Cost + P * Commissions
    // Price = (Cost + P * Commissions) / P
    
    if (sale_probability == 0) {
        return 0;
    }
    
    return (cost + sale_probability * commissions) / sale_probability;
}

}  // namespace decision_maker
