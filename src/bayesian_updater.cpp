#include "bayesian_updater.h"
#include <algorithm>
#include <numeric>
#include <sstream>
#include <iomanip>
#include <cmath>

namespace decision_maker {

BayesianUpdater::BayesianUpdater()
    : prior_(0.0), posterior_(0.0), prior_source_("") {}

void BayesianUpdater::set_prior(double probability, 
                                const std::string& source) {
    prior_ = probability;
    posterior_ = probability;
    prior_source_ = source;
    
    PriorBelief belief;
    belief.probability = probability;
    belief.source = source;
    belief.timestamp = "init";
    
    belief_history_.push_back(belief);
}

void BayesianUpdater::add_evidence(const Evidence& evidence) {
    evidences_.push_back(evidence);
    update_posterior();
}

double BayesianUpdater::get_posterior() {
    return posterior_;
}

double BayesianUpdater::get_posterior_for_scenario(
    const std::string& scenario
) {
    auto it = std::find_if(
        scenarios_.begin(),
        scenarios_.end(),
        [&](const Scenario& s) { return s.name == scenario; }
    );
    
    if (it != scenarios_.end()) {
        return it->posterior;
    }
    
    return posterior_;
}

std::vector<PriorBelief> BayesianUpdater::get_belief_history() {
    return belief_history_;
}

std::string BayesianUpdater::generate_evidence_report() {
    std::ostringstream report;
    report << std::fixed << std::setprecision(4);
    
    report << "=== BAYESIAN EVIDENCE REPORT ===\n\n";
    
    report << "PRIOR BELIEF\n";
    report << "  Source: " << prior_source_ << "\n";
    report << "  Probability: " << prior_ << " (" 
           << (prior_ * 100) << "%)\n\n";
    
    report << "EVIDENCE COLLECTED (" << evidences_.size() << " items)\n";
    for (size_t i = 0; i < evidences_.size(); i++) {
        report << "  " << (i + 1) << ". " << evidences_[i].type << "\n";
        report << "     Value: " << evidences_[i].value << "\n";
        report << "     Confidence: " << evidences_[i].confidence 
               << "\n";
        report << "     Source: " << evidences_[i].source << "\n";
    }
    report << "\n";
    
    report << "POSTERIOR BELIEF\n";
    report << "  Probability: " << posterior_ << " (" 
           << (posterior_ * 100) << "%)\n";
    report << "  Change: " << (posterior_ - prior_) << " (" 
           << ((posterior_ - prior_) * 100) << "%)\n\n";
    
    if (!scenarios_.empty()) {
        report << "SCENARIO ANALYSIS (" << scenarios_.size() << " scenarios)\n";
        for (const auto& scenario : scenarios_) {
            report << "  " << scenario.name << ": " 
                   << scenario.posterior << " (" 
                   << (scenario.posterior * 100) << "%)\n";
        }
    }
    
    return report.str();
}

void BayesianUpdater::reset() {
    posterior_ = prior_;
    evidences_.clear();
}

void BayesianUpdater::add_scenario(const Scenario& scenario) {
    Scenario s = scenario;
    s.posterior = combine_evidences(s.evidences);
    scenarios_.push_back(s);
}

std::vector<BayesianUpdater::Scenario> BayesianUpdater::get_scenarios() {
    return scenarios_;
}

double BayesianUpdater::calculate_likelihood(const Evidence& evidence) {
    // P(evidence|hypothesis_true) / P(evidence|hypothesis_false)
    
    if (evidence.type == "price") {
        // If price is high, more likely to sell
        // Assuming price range: $45K-$85K
        double likelihood_ratio;
        if (evidence.value > 75000) {
            likelihood_ratio = 1.5;  // Better chance to sell
        } else if (evidence.value > 65000) {
            likelihood_ratio = 1.2;
        } else if (evidence.value > 50000) {
            likelihood_ratio = 0.9;
        } else {
            likelihood_ratio = 0.7;  // Low price, unlikely to sell
        }
        return likelihood_ratio;
        
    } else if (evidence.type == "demand") {
        // ALTA=0.2, MEDIA=0.5, BAJA=0.1 (normalized)
        if (evidence.value > 0.6) {  // ALTA
            return 1.8;  // High demand increases sale probability
        } else if (evidence.value > 0.3) {  // MEDIA
            return 1.0;  // Neutral
        } else {
            return 0.4;  // Low demand decreases probability
        }
        
    } else if (evidence.type == "saturation") {
        // Higher saturation = lower probability to sell
        double likelihood_ratio = 1.0 - evidence.value;  // 0-1 range
        return likelihood_ratio;
        
    } else if (evidence.type == "days_listed") {
        // If item has been listed many days, might still be for sale
        // Or it could have sold and wasn't updated
        // Treat as neutral evidence
        return 1.0;
        
    } else if (evidence.type == "competition") {
        // Number of similar items available
        // Higher competition = lower probability
        double likelihood_ratio = 1.0 / (1.0 + evidence.value / 100.0);
        return likelihood_ratio;
    }
    
    return 1.0;  // Unknown evidence type = neutral
}

void BayesianUpdater::update_posterior() {
    posterior_ = combine_evidences(evidences_);
}

double BayesianUpdater::combine_evidences(
    const std::vector<Evidence>& evidences
) {
    if (evidences.empty()) {
        return prior_;
    }
    
    // Start with prior
    double posterior = prior_;
    
    // Apply each evidence sequentially
    for (const auto& evidence : evidences) {
        double likelihood = calculate_likelihood(evidence);
        
        // Apply confidence weighting
        double weighted_likelihood = 1.0 + 
            (likelihood - 1.0) * evidence.confidence;
        
        // Bayes update: 
        // P(H|E) = P(E|H) * P(H) / P(E)
        // Simplified as: P(H|E) ∝ P(E|H) * P(H)
        posterior = posterior * weighted_likelihood;
        
        // Normalize to keep probability in [0, 1]
        // Use logistic function for stability
        double log_odds = std::log(posterior / (1.0 - posterior + 1e-10));
        posterior = 1.0 / (1.0 + std::exp(-log_odds));
    }
    
    return std::min(1.0, std::max(0.0, posterior));
}

}  // namespace decision_maker
