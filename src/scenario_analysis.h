#ifndef SCENARIO_ANALYSIS_H
#define SCENARIO_ANALYSIS_H

#include <string>
#include <vector>
#include <map>

namespace decision_maker {

struct ScenarioAssumptions {
    std::string name;  // "pessimistic", "realistic", "optimistic"
    double restoration_cost;
    double expected_sale_price;
    double sale_probability;
    int days_to_sale;
    std::string description;
};

struct ScenarioResult {
    std::string scenario_name;
    double expected_value;
    double best_case_value;
    double worst_case_value;
    double confidence;
    std::string recommendation;
};

class ScenarioAnalyzer {
public:
    ScenarioAnalyzer();
    
    // Define custom scenario
    void add_scenario(const ScenarioAssumptions& scenario);
    
    // Calculate scenario outcomes
    ScenarioResult analyze_scenario(
        const ScenarioAssumptions& scenario,
        double botar_cost = 5000
    );
    
    // Run all scenarios and compare
    std::vector<ScenarioResult> run_all_scenarios();
    
    // Get default scenarios (pessimistic, realistic, optimistic)
    std::vector<ScenarioAssumptions> get_default_scenarios();
    
    // Generate scenario comparison report
    std::string generate_comparison_report();
    
    // Get sensitivity analysis for key variables
    std::map<std::string, std::vector<double>> 
    sensitivity_analysis(const ScenarioAssumptions& base_scenario);
    
private:
    std::vector<ScenarioAssumptions> scenarios_;
    std::vector<ScenarioResult> results_;
    
    // Helper function to calculate expected value
    double calculate_expected_value(
        const ScenarioAssumptions& scenario,
        double botar_cost
    );
    
    // Calculate break-even price
    double calculate_breakeven_price(double sale_probability);
};

}  // namespace decision_maker

#endif  // SCENARIO_ANALYSIS_H
