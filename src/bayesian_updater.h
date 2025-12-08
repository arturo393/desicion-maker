#ifndef BAYESIAN_UPDATER_H
#define BAYESIAN_UPDATER_H

#include <vector>
#include <map>
#include <string>
#include <memory>

namespace decision_maker {

struct PriorBelief {
    double probability;
    std::string source;  // "gemini", "theoretical", "market_data"
    std::string timestamp;
};

struct Evidence {
    std::string type;  // "price", "demand", "saturation", "sales"
    double value;
    double confidence;  // 0-1, how confident is this evidence
    std::string source;
};

class BayesianUpdater {
public:
    BayesianUpdater();
    
    // Initialize with prior belief
    void set_prior(double probability, const std::string& source);
    
    // Add evidence to update belief
    void add_evidence(const Evidence& evidence);
    
    // Get current posterior probability
    double get_posterior();
    
    // Get posterior with specific scenario
    double get_posterior_for_scenario(const std::string& scenario);
    
    // Get belief history
    std::vector<PriorBelief> get_belief_history();
    
    // Get evidence summary
    std::string generate_evidence_report();
    
    // Reset to prior
    void reset();
    
    // Scenario-based analysis
    struct Scenario {
        std::string name;
        std::vector<Evidence> evidences;
        double posterior;
    };
    
    void add_scenario(const Scenario& scenario);
    std::vector<Scenario> get_scenarios();
    
private:
    double prior_;
    double posterior_;
    std::string prior_source_;
    std::vector<PriorBelief> belief_history_;
    std::vector<Evidence> evidences_;
    std::vector<Scenario> scenarios_;
    
    // Calculate likelihood for specific evidence type
    double calculate_likelihood(const Evidence& evidence);
    
    // Update posterior using Bayes rule
    void update_posterior();
    
    // Combine multiple evidences
    double combine_evidences(const std::vector<Evidence>& evidences);
};

}  // namespace decision_maker

#endif  // BAYESIAN_UPDATER_H
