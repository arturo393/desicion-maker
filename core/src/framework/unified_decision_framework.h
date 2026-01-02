/**
 * @file unified_decision_framework.h
 * @brief Framework unificado para toma de decisiones con múltiples metodologías
 * 
 * ARQUITECTURA:
 * - Monte Carlo: Simulación estocástica (incertidumbre)
 * - MCDM: Multi-Criteria Decision Making (criterios ponderados)
 * - Decision Trees: Árboles de decisión (secuencias)
 * - Sensitivity Analysis: Análisis de sensibilidad (qué factores importan más)
 * - Bayesian Networks: Actualización con nueva información
 * 
 * INSPIRADO EN:
 * - business_decision_v2_enhanced.cpp (OOP, factores como clases)
 * - decision_jeep_logistica.cpp (Monte Carlo robusto)
 * - decision_computadora_arturo.cpp (simplicidad, realismo)
 * 
 * @author Arturo
 * @date 2025-12
 */

#pragma once

#include <iostream>
#include <vector>
#include <string>
#include <random>
#include <functional>
#include <memory>
#include <map>
#include <algorithm>
#include <numeric>
#include <cmath>
#include <iomanip>

namespace DecisionFramework {

// ============================================================================
// 1. TIPOS BASE
// ============================================================================

/**
 * @brief Tipo de distribución para incertidumbre
 */
enum class DistributionType {
    DETERMINISTIC,  // Sin incertidumbre (valor fijo)
    NORMAL,         // Distribución normal (μ, σ)
    UNIFORM,        // Distribución uniforme [min, max]
    TRIANGULAR,     // Distribución triangular (min, mode, max)
    BERNOULLI,      // Éxito/fracaso (probabilidad p)
    EXPONENTIAL,    // Tiempos de espera
    BETA            // Valores entre 0-1 con forma
};

/**
 * @brief Variable con incertidumbre
 */
struct UncertainVariable {
    std::string name;
    DistributionType type;
    double param1;  // μ, min, o p según tipo
    double param2;  // σ, max, o mode según tipo
    double param3;  // max (solo triangular)
    
    // Constructor por defecto (necesario para std::map)
    UncertainVariable() 
        : name(""), type(DistributionType::DETERMINISTIC), 
          param1(0), param2(0), param3(0) {}
    
    UncertainVariable(std::string n, double value)
        : name(n), type(DistributionType::DETERMINISTIC), 
          param1(value), param2(0), param3(0) {}
    
    UncertainVariable(std::string n, DistributionType t, double p1, double p2 = 0, double p3 = 0)
        : name(n), type(t), param1(p1), param2(p2), param3(p3) {}
    
    // Generar valor aleatorio según distribución
    double sample(std::mt19937& gen) const {
        switch (type) {
            case DistributionType::DETERMINISTIC:
                return param1;
            
            case DistributionType::NORMAL: {
                std::normal_distribution<> d(param1, param2);
                return d(gen);
            }
            
            case DistributionType::UNIFORM: {
                std::uniform_real_distribution<> d(param1, param2);
                return d(gen);
            }
            
            case DistributionType::TRIANGULAR: {
                // Transformación inversa para triangular
                std::uniform_real_distribution<> u(0, 1);
                double U = u(gen);
                double F_mode = (param2 - param1) / (param3 - param1);
                if (U < F_mode) {
                    return param1 + std::sqrt(U * (param3 - param1) * (param2 - param1));
                } else {
                    return param3 - std::sqrt((1 - U) * (param3 - param1) * (param3 - param2));
                }
            }
            
            case DistributionType::BERNOULLI: {
                std::bernoulli_distribution d(param1);
                return d(gen) ? 1.0 : 0.0;
            }
            
            case DistributionType::EXPONENTIAL: {
                std::exponential_distribution<> d(param1);
                return d(gen);
            }
            
            case DistributionType::BETA: {
                // Aproximación Beta usando Normal (simplificado)
                // Para producción usar boost o implementación completa
                std::gamma_distribution<> g1(param1, 1.0);
                std::gamma_distribution<> g2(param2, 1.0);
                double X = g1(gen);
                double Y = g2(gen);
                return X / (X + Y);
            }
            
            default:
                return param1;
        }
    }
};

/**
 * @brief Factor de decisión (criterio)
 */
struct Factor {
    std::string name;
    std::string category;  // "Costo", "Tiempo", "Riesgo", etc.
    double weight;         // Peso 0-1 (importancia relativa)
    bool maximize;         // true = más es mejor, false = menos es mejor
    
    Factor(std::string n, std::string cat, double w, bool max = true)
        : name(n), category(cat), weight(w), maximize(max) {}
};

/**
 * @brief Resultado de UNA simulación
 */
struct SimulationResult {
    std::map<std::string, double> factor_values;  // Valor de cada factor
    std::map<std::string, bool> events;           // Eventos que ocurrieron
    double total_score;                           // Score ponderado final
    bool success;                                 // ¿Fue exitoso?
    std::string failure_reason;                   // Razón de fallo (si aplica)
};

/**
 * @brief Estadísticas de múltiples simulaciones
 */
struct Statistics {
    std::string option_name;
    size_t num_simulations;
    
    // Por cada factor
    std::map<std::string, double> mean;
    std::map<std::string, double> stddev;
    std::map<std::string, double> min;
    std::map<std::string, double> max;
    std::map<std::string, double> percentile_5;
    std::map<std::string, double> percentile_95;
    
    // Métricas generales
    double success_rate;
    double mean_score;
    double score_stddev;
    double score_min;
    double score_max;
    
    // Eventos
    std::map<std::string, double> event_probabilities;
};

// ============================================================================
// 2. OPCIÓN DE DECISIÓN
// ============================================================================

/**
 * @brief Opción de decisión con incertidumbre
 */
class DecisionOption {
private:
    std::string name_;
    std::string description_;
    std::map<std::string, UncertainVariable> variables_;
    std::function<SimulationResult(const std::map<std::string, double>&, std::mt19937&)> simulator_;
    
public:
    DecisionOption(std::string name, std::string desc)
        : name_(name), description_(desc) {}
    
    // Agregar variable con incertidumbre
    void addVariable(const std::string& factor_name, const UncertainVariable& var) {
        variables_[factor_name] = var;
    }
    
    // Definir función de simulación custom
    void setSimulator(std::function<SimulationResult(const std::map<std::string, double>&, std::mt19937&)> sim) {
        simulator_ = sim;
    }
    
    // Ejecutar UNA simulación
    SimulationResult simulate(std::mt19937& gen, const std::vector<Factor>& factors) {
        // 1. Samplear todas las variables
        std::map<std::string, double> sampled_values;
        for (const auto& [name, var] : variables_) {
            sampled_values[name] = var.sample(gen);
        }
        
        // 2. Ejecutar simulador custom (si existe)
        SimulationResult result;
        if (simulator_) {
            result = simulator_(sampled_values, gen);
        } else {
            // Simulador por defecto: solo copiar valores
            result.factor_values = sampled_values;
            result.success = true;
        }
        
        // 3. Calcular score ponderado
        result.total_score = 0;
        for (const auto& factor : factors) {
            auto it = result.factor_values.find(factor.name);
            if (it != result.factor_values.end()) {
                double normalized = it->second;
                if (!factor.maximize) {
                    normalized = -normalized;  // Invertir si menor es mejor
                }
                result.total_score += normalized * factor.weight;
            }
        }
        
        return result;
    }
    
    std::string getName() const { return name_; }
    std::string getDescription() const { return description_; }
};

// ============================================================================
// 3. MOTOR DE SIMULACIÓN MONTE CARLO
// ============================================================================

class MonteCarloEngine {
private:
    std::vector<DecisionOption> options_;
    std::vector<Factor> factors_;
    std::mt19937 gen_;
    size_t num_simulations_;
    
public:
    MonteCarloEngine(size_t seed = std::random_device{}())
        : gen_(seed), num_simulations_(10000) {}
    
    void setNumSimulations(size_t n) { num_simulations_ = n; }
    
    void addFactor(const Factor& factor) {
        factors_.push_back(factor);
    }
    
    void addOption(const DecisionOption& option) {
        options_.push_back(option);
    }
    
    // Ejecutar simulaciones para todas las opciones
    std::map<std::string, Statistics> run() {
        std::map<std::string, Statistics> results;
        
        std::cout << "🎲 Ejecutando " << num_simulations_ << " simulaciones para "
                  << options_.size() << " opciones...\n\n";
        
        for (auto& option : options_) {
            std::cout << "Analizando: " << option.getName() << "...\n";
            
            Statistics stats;
            stats.option_name = option.getName();
            stats.num_simulations = num_simulations_;
            
            // Almacenar todos los resultados
            std::vector<SimulationResult> all_results;
            std::map<std::string, std::vector<double>> factor_samples;
            std::vector<double> scores;
            
            size_t successes = 0;
            
            // Ejecutar simulaciones
            for (size_t i = 0; i < num_simulations_; ++i) {
                SimulationResult result = option.simulate(gen_, factors_);
                all_results.push_back(result);
                
                if (result.success) successes++;
                scores.push_back(result.total_score);
                
                // Recolectar valores de factores
                for (const auto& [factor_name, value] : result.factor_values) {
                    factor_samples[factor_name].push_back(value);
                }
                
                // Recolectar eventos
                for (const auto& [event_name, occurred] : result.events) {
                    if (occurred) {
                        stats.event_probabilities[event_name] += 1.0;
                    }
                }
            }
            
            // Calcular estadísticas
            stats.success_rate = (double)successes / num_simulations_;
            
            // Estadísticas de score
            stats.mean_score = std::accumulate(scores.begin(), scores.end(), 0.0) / scores.size();
            
            double sq_sum = std::inner_product(scores.begin(), scores.end(), scores.begin(), 0.0);
            stats.score_stddev = std::sqrt(sq_sum / scores.size() - stats.mean_score * stats.mean_score);
            
            stats.score_min = *std::min_element(scores.begin(), scores.end());
            stats.score_max = *std::max_element(scores.begin(), scores.end());
            
            // Estadísticas por factor
            for (const auto& [factor_name, values] : factor_samples) {
                stats.mean[factor_name] = std::accumulate(values.begin(), values.end(), 0.0) / values.size();
                
                double sq_sum_factor = std::inner_product(values.begin(), values.end(), values.begin(), 0.0);
                stats.stddev[factor_name] = std::sqrt(sq_sum_factor / values.size() - 
                                                      stats.mean[factor_name] * stats.mean[factor_name]);
                
                auto sorted = values;
                std::sort(sorted.begin(), sorted.end());
                stats.min[factor_name] = sorted.front();
                stats.max[factor_name] = sorted.back();
                stats.percentile_5[factor_name] = sorted[sorted.size() * 0.05];
                stats.percentile_95[factor_name] = sorted[sorted.size() * 0.95];
            }
            
            // Normalizar probabilidades de eventos
            for (auto& [event_name, count] : stats.event_probabilities) {
                count /= num_simulations_;
            }
            
            results[option.getName()] = stats;
        }
        
        return results;
    }
    
    // Análisis de sensibilidad: ¿qué factor importa más?
    std::map<std::string, double> sensitivityAnalysis(const std::string& option_name) {
        std::map<std::string, double> sensitivities;
        
        // Para cada factor, variar su peso y medir impacto
        auto original_factors = factors_;
        
        for (size_t i = 0; i < factors_.size(); ++i) {
            double original_weight = factors_[i].weight;
            
            // Probar con peso +20%
            factors_[i].weight *= 1.2;
            auto results_high = run();
            
            // Probar con peso -20%
            factors_[i].weight = original_weight * 0.8;
            auto results_low = run();
            
            // Restaurar peso
            factors_[i].weight = original_weight;
            
            // Calcular sensibilidad
            double score_high = results_high[option_name].mean_score;
            double score_low = results_low[option_name].mean_score;
            sensitivities[factors_[i].name] = std::abs(score_high - score_low);
        }
        
        factors_ = original_factors;
        return sensitivities;
    }
};

// ============================================================================
// 4. MÉTODOS COMPLEMENTARIOS (NO MONTE CARLO)
// ============================================================================

/**
 * @brief TOPSIS (Technique for Order Preference by Similarity to Ideal Solution)
 * 
 * Ventajas vs Monte Carlo:
 * - NO requiere distribuciones de probabilidad
 * - Más rápido (determinístico)
 * - Útil cuando hay CERTEZA en los valores
 * - Ideal para comparar opciones existentes
 */
class TOPSISAnalyzer {
private:
    std::vector<std::vector<double>> decision_matrix_;  // [opciones][factores]
    std::vector<double> weights_;
    std::vector<bool> maximize_;  // true si mayor es mejor
    std::vector<std::string> option_names_;
    std::vector<std::string> factor_names_;
    
public:
    void setOptions(const std::vector<std::string>& names) {
        option_names_ = names;
    }
    
    void setFactors(const std::vector<std::string>& names, 
                    const std::vector<double>& weights,
                    const std::vector<bool>& maximize) {
        factor_names_ = names;
        weights_ = weights;
        maximize_ = maximize;
    }
    
    void setDecisionMatrix(const std::vector<std::vector<double>>& matrix) {
        decision_matrix_ = matrix;
    }
    
    std::map<std::string, double> analyze() {
        size_t n_options = decision_matrix_.size();
        size_t n_factors = decision_matrix_[0].size();
        
        // 1. Normalizar matriz
        std::vector<std::vector<double>> normalized(n_options, std::vector<double>(n_factors));
        for (size_t j = 0; j < n_factors; ++j) {
            double sum_sq = 0;
            for (size_t i = 0; i < n_options; ++i) {
                sum_sq += decision_matrix_[i][j] * decision_matrix_[i][j];
            }
            double norm = std::sqrt(sum_sq);
            
            for (size_t i = 0; i < n_options; ++i) {
                normalized[i][j] = decision_matrix_[i][j] / norm;
            }
        }
        
        // 2. Aplicar pesos
        for (size_t i = 0; i < n_options; ++i) {
            for (size_t j = 0; j < n_factors; ++j) {
                normalized[i][j] *= weights_[j];
            }
        }
        
        // 3. Determinar ideal positivo y negativo
        std::vector<double> ideal_pos(n_factors);
        std::vector<double> ideal_neg(n_factors);
        
        for (size_t j = 0; j < n_factors; ++j) {
            std::vector<double> column;
            for (size_t i = 0; i < n_options; ++i) {
                column.push_back(normalized[i][j]);
            }
            
            if (maximize_[j]) {
                ideal_pos[j] = *std::max_element(column.begin(), column.end());
                ideal_neg[j] = *std::min_element(column.begin(), column.end());
            } else {
                ideal_pos[j] = *std::min_element(column.begin(), column.end());
                ideal_neg[j] = *std::max_element(column.begin(), column.end());
            }
        }
        
        // 4. Calcular distancias
        std::map<std::string, double> scores;
        for (size_t i = 0; i < n_options; ++i) {
            double dist_pos = 0, dist_neg = 0;
            for (size_t j = 0; j < n_factors; ++j) {
                dist_pos += std::pow(normalized[i][j] - ideal_pos[j], 2);
                dist_neg += std::pow(normalized[i][j] - ideal_neg[j], 2);
            }
            dist_pos = std::sqrt(dist_pos);
            dist_neg = std::sqrt(dist_neg);
            
            // Proximidad relativa
            scores[option_names_[i]] = dist_neg / (dist_pos + dist_neg);
        }
        
        return scores;
    }
};

/**
 * @brief Análisis de Árbol de Decisión
 * 
 * Ventajas vs Monte Carlo:
 * - Modela SECUENCIAS de decisiones
 * - Visualizable (diagrama)
 * - Muestra rutas alternativas claramente
 * - Útil para decisiones multi-etapa
 */
struct DecisionNode {
    std::string description;
    bool is_decision;  // true = eliges, false = chance node
    std::vector<std::pair<std::string, double>> branches;  // [descripción, probabilidad o valor]
    std::vector<std::shared_ptr<DecisionNode>> children;
};

/**
 * @brief Análisis de Pareto (Multi-Objetivo)
 * 
 * Ventajas vs Monte Carlo:
 * - Identifica trade-offs entre objetivos
 * - No requiere asignar pesos a priori
 * - Muestra frontera de Pareto (opciones óptimas)
 * - Útil cuando hay conflicto entre objetivos
 */
class ParetoAnalyzer {
public:
    struct Point {
        std::string name;
        std::vector<double> objectives;  // [obj1, obj2, ...]
        bool dominated;
    };
    
    std::vector<Point> findParetoFront(std::vector<Point>& points, 
                                      const std::vector<bool>& maximize) {
        // Marcar puntos dominados
        for (size_t i = 0; i < points.size(); ++i) {
            points[i].dominated = false;
            for (size_t j = 0; j < points.size(); ++j) {
                if (i == j) continue;
                
                bool dominates = true;
                bool strictly_better = false;
                
                for (size_t k = 0; k < points[i].objectives.size(); ++k) {
                    double val_i = points[i].objectives[k];
                    double val_j = points[j].objectives[k];
                    
                    if (maximize[k]) {
                        if (val_j < val_i) strictly_better = true;
                        if (val_j > val_i) { dominates = false; break; }
                    } else {
                        if (val_j > val_i) strictly_better = true;
                        if (val_j < val_i) { dominates = false; break; }
                    }
                }
                
                if (dominates && strictly_better) {
                    points[i].dominated = true;
                    break;
                }
            }
        }
        
        // Retornar frontera de Pareto
        std::vector<Point> pareto_front;
        for (const auto& p : points) {
            if (!p.dominated) {
                pareto_front.push_back(p);
            }
        }
        
        return pareto_front;
    }
};

// ============================================================================
// 5. UTILIDADES DE VISUALIZACIÓN
// ============================================================================

void printStatistics(const Statistics& stats, const std::vector<Factor>& factors) {
    std::cout << "\n🖥️  " << stats.option_name << "\n";
    std::cout << "   ✅ Tasa de éxito: " << std::fixed << std::setprecision(1) 
              << stats.success_rate * 100 << "%\n";
    std::cout << "   📊 Score promedio: " << std::setprecision(2) 
              << stats.mean_score << " (±" << stats.score_stddev << ")\n";
    std::cout << "   📈 Rango score: [" << stats.score_min << ", " << stats.score_max << "]\n\n";
    
    std::cout << "   Factores:\n";
    for (const auto& factor : factors) {
        auto it = stats.mean.find(factor.name);
        if (it != stats.mean.end()) {
            std::cout << "   • " << factor.name << ": " << std::setprecision(1)
                      << it->second << " (±" << stats.stddev.at(factor.name) << ")\n";
            std::cout << "      5%-95%: [" << stats.percentile_5.at(factor.name) 
                      << ", " << stats.percentile_95.at(factor.name) << "]\n";
        }
    }
    
    if (!stats.event_probabilities.empty()) {
        std::cout << "\n   Eventos:\n";
        for (const auto& [event, prob] : stats.event_probabilities) {
            std::cout << "   ⚠️  " << event << ": " << std::setprecision(1) 
                      << prob * 100 << "%\n";
        }
    }
}

void printComparison(const std::map<std::string, Statistics>& all_stats) {
    std::cout << "\n" << std::string(80, '=') << "\n";
    std::cout << "🏆 COMPARACIÓN FINAL\n";
    std::cout << std::string(80, '=') << "\n\n";
    
    // Encontrar mejor por score
    std::string best_score;
    double max_score = -std::numeric_limits<double>::infinity();
    for (const auto& [name, stats] : all_stats) {
        if (stats.mean_score > max_score) {
            max_score = stats.mean_score;
            best_score = name;
        }
    }
    
    std::cout << "✅ Mayor score promedio: " << best_score 
              << " (" << std::fixed << std::setprecision(2) << max_score << ")\n";
    
    // Encontrar más confiable
    std::string most_reliable;
    double max_success = 0;
    for (const auto& [name, stats] : all_stats) {
        if (stats.success_rate > max_success) {
            max_success = stats.success_rate;
            most_reliable = name;
        }
    }
    
    std::cout << "🎯 Más confiable: " << most_reliable 
              << " (" << std::setprecision(1) << max_success * 100 << "% éxito)\n";
}

} // namespace DecisionFramework
