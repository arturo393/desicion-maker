#include "decision_framework.h"
#include <algorithm>
#include <sstream>
#include <iomanip>
#include <numeric>

namespace decision {

// ============================================================================
// DECISION FRAMEWORK - IMPLEMENTACIÓN
// ============================================================================

DecisionFramework::DecisionFramework(const std::string& title)
    : decision_title_(title) {}

void DecisionFramework::add_option(const Option& option) {
    options_.push_back(option);
}

void DecisionFramework::add_methodology(std::unique_ptr<Methodology> methodology) {
    methodologies_.push_back(std::move(methodology));
}

DecisionReport DecisionFramework::analyze() {
    DecisionReport report;
    report.decision_title = decision_title_;
    report.methodologies_count = methodologies_.size();
    
    // Ejecutar cada metodología
    for (auto& methodology : methodologies_) {
        auto result = methodology->analyze(options_);
        report.all_results.push_back(result);
    }
    
    // Encontrar opción con mayor consenso
    report.final_recommendation = find_consensus_option(report.all_results);
    
    // Calcular confianza final
    report.final_confidence = calculate_consensus_confidence(
        report.all_results,
        report.final_recommendation
    );
    
    // Calcular confianza por opción
    for (const auto& option : options_) {
        double option_confidence = 0.0;
        int votes = 0;
        
        for (const auto& result : report.all_results) {
            if (result.recommended_option == option.name) {
                option_confidence += result.confidence;
                votes++;
            }
        }
        
        if (votes > 0) {
            option_confidence /= votes;
        }
        
        report.option_confidence[option.name] = option_confidence;
    }
    
    // Generar resumen ejecutivo
    std::ostringstream summary;
    summary << "Decision: " << report.final_recommendation << "\n";
    summary << "Confidence: " << confidence_to_percentage(report.final_confidence) << "%\n";
    summary << "Methodologies: " << report.methodologies_count << "\n";
    summary << "Consensus: " << find_consensus_option(report.all_results);
    
    report.executive_summary = summary.str();
    
    return report;
}

std::string DecisionFramework::generate_markdown_report(const DecisionReport& report) const {
    std::ostringstream oss;
    
    oss << "# Reporte de Decisión: " << decision_title_ << "\n\n";
    
    oss << "## Decisión Final\n";
    oss << "**Recomendación:** " << report.final_recommendation << "\n";
    oss << "**Confianza:** " << confidence_to_percentage(report.final_confidence) << "%\n";
    oss << "**Metodologías:** " << report.methodologies_count << "\n\n";
    
    oss << "## Resultados por Metodología\n\n";
    for (const auto& result : report.all_results) {
        oss << "### " << result.methodology_name << "\n";
        oss << "- **Recomendación:** " << result.recommended_option << "\n";
        oss << "- **Confianza:** " << confidence_to_percentage(result.confidence) << "%\n";
        oss << "- **Razonamiento:** " << result.reasoning << "\n\n";
    }
    
    oss << "## Confianza por Opción\n";
    oss << "| Opción | Confianza |\n";
    oss << "|--------|----------|\n";
    for (const auto& [option, conf] : report.option_confidence) {
        oss << "| " << option << " | " << confidence_to_percentage(conf) << "% |\n";
    }
    oss << "\n";
    
    oss << "## Resumen Ejecutivo\n";
    oss << "```\n" << report.executive_summary << "\n```\n";
    
    return oss.str();
}

std::string DecisionFramework::generate_text_report(const DecisionReport& report) const {
    std::ostringstream oss;
    
    oss << "════════════════════════════════════════════════════════════\n";
    oss << "REPORTE DE DECISIÓN: " << decision_title_ << "\n";
    oss << "════════════════════════════════════════════════════════════\n\n";
    
    oss << "DECISIÓN FINAL: " << report.final_recommendation << "\n";
    oss << "CONFIANZA: " << confidence_to_percentage(report.final_confidence) << "%\n";
    oss << "METODOLOGÍAS: " << report.methodologies_count << "\n\n";
    
    oss << "────────────────────────────────────────────────────────────\n";
    oss << "ANÁLISIS POR METODOLOGÍA\n";
    oss << "────────────────────────────────────────────────────────────\n\n";
    
    for (size_t i = 0; i < report.all_results.size(); ++i) {
        const auto& result = report.all_results[i];
        oss << (i + 1) << ". " << result.methodology_name << "\n";
        oss << "   Recomienda: " << result.recommended_option << "\n";
        oss << "   Confianza: " << confidence_to_percentage(result.confidence) << "%\n";
        oss << "   Razonamiento: " << result.reasoning << "\n\n";
    }
    
    oss << "────────────────────────────────────────────────────────────\n";
    oss << "CONFIANZA POR OPCIÓN\n";
    oss << "────────────────────────────────────────────────────────────\n\n";
    for (const auto& [option, conf] : report.option_confidence) {
        oss << option << ": " << confidence_to_percentage(conf) << "%\n";
    }
    
    return oss.str();
}

// ============================================================================
// FUNCIONES UTILIDAD
// ============================================================================

double calculate_consensus_confidence(
    const std::vector<AnalysisResult>& results,
    const std::string& recommended_option) {
    
    if (results.empty()) return 0.0;
    
    // Contar votos para la opción recomendada
    int votes = 0;
    double total_confidence = 0.0;
    
    for (const auto& result : results) {
        if (result.recommended_option == recommended_option) {
            votes++;
            total_confidence += result.confidence;
        }
    }
    
    if (votes == 0) return 0.0;
    
    // Calcular confianza promedio
    double avg_confidence = total_confidence / votes;
    
    // Boost por consenso: si todos concuerdan, confianza más alta
    double consensus_boost = static_cast<double>(votes) / results.size();
    
    // Fórmula: (confianza promedio) * (factor de consenso)
    // Con todos de acuerdo = 1.0 (boost máximo)
    // Con mitad de acuerdo = 0.5 (medio boost)
    double final_confidence = avg_confidence * (0.5 + 0.5 * consensus_boost);
    
    return std::min(1.0, final_confidence);  // Máximo 1.0 (100%)
}

std::string find_consensus_option(const std::vector<AnalysisResult>& results) {
    if (results.empty()) return "";
    
    // Contar votos por opción
    std::map<std::string, int> vote_count;
    for (const auto& result : results) {
        vote_count[result.recommended_option]++;
    }
    
    // Encontrar opción con más votos
    auto max_it = std::max_element(
        vote_count.begin(),
        vote_count.end(),
        [](const auto& a, const auto& b) { return a.second < b.second; }
    );
    
    return max_it->first;
}

} // namespace decision
