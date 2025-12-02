/**
 * @file advanced_decision_tools.h
 * @brief Herramientas avanzadas para toma de decisiones
 * 
 * CARACTERÍSTICAS PODEROSAS:
 * 1. Bayesian Network: Actualizar probabilidades con nueva información
 * 2. Regret Analysis: Minimizar arrepentimiento (minimax regret)
 * 3. Real Options Analysis: Valor de flexibilidad futura
 * 4. Multi-Armed Bandit: Exploración vs explotación
 * 5. Portfolio Optimization: Diversificación óptima
 * 6. Risk Analysis: VaR, CVaR, probabilidad de ruina
 * 7. Scenario Planning: Futuros alternativos
 * 8. Correlation Analysis: Detectar dependencias entre factores
 * 
 * @author Arturo
 * @date 2025-12
 */

#pragma once

#include "unified_decision_framework.h"
#include <queue>
#include <set>

namespace DecisionFramework {

// ============================================================================
// 1. BAYESIAN NETWORK - Actualizar con nueva información
// ============================================================================

/**
 * @brief Red Bayesiana para actualizar probabilidades
 * 
 * VENTAJA vs Monte Carlo estático:
 * - Adapta decisión cuando llega NUEVA información
 * - Ejemplo: "Encontré MacBook usado $800 → recalcular"
 */
class BayesianUpdater {
private:
    struct Node {
        std::string name;
        double prior_prob;
        double posterior_prob;
        std::map<std::string, double> conditional_probs;  // P(this | parent)
    };
    
    std::map<std::string, Node> nodes_;
    
public:
    void addNode(const std::string& name, double prior) {
        nodes_[name] = {name, prior, prior, {}};
    }
    
    void addConditional(const std::string& node, 
                       const std::string& parent, 
                       double prob) {
        nodes_[node].conditional_probs[parent] = prob;
    }
    
    /**
     * @brief Actualiza probabilidad posterior con nueva evidencia
     * 
     * Teorema de Bayes: P(A|B) = P(B|A) * P(A) / P(B)
     */
    void updateBelief(const std::string& node, 
                     const std::string& evidence, 
                     bool evidence_true) {
        auto& n = nodes_[node];
        auto& e = nodes_[evidence];
        
        double likelihood = evidence_true ? 
            n.conditional_probs[evidence] : 
            (1.0 - n.conditional_probs[evidence]);
        
        double marginal = evidence_true ? e.prior_prob : (1.0 - e.prior_prob);
        
        // Bayes' theorem
        n.posterior_prob = (likelihood * n.prior_prob) / marginal;
    }
    
    double getPosterior(const std::string& node) const {
        return nodes_.at(node).posterior_prob;
    }
    
    /**
     * @brief Ejemplo de uso:
     * 
     * BayesianUpdater bn;
     * bn.addNode("laptop_falla", 0.15);  // Prior: 15% falla
     * bn.addNode("encontre_barato", 0.30);
     * bn.addConditional("laptop_falla", "encontre_barato", 0.60);
     * 
     * // Nueva evidencia: encontré laptop barato
     * bn.updateBelief("laptop_falla", "encontre_barato", true);
     * // Posterior prob aumenta (laptops baratos fallan más)
     */
};

// ============================================================================
// 2. REGRET ANALYSIS - Minimizar arrepentimiento
// ============================================================================

/**
 * @brief Análisis de arrepentimiento (minimax regret)
 * 
 * VENTAJA vs Monte Carlo:
 * - Enfoque psicológico: "¿Qué decisión lamentaré MENOS?"
 * - Útil para personas con aversión a arrepentimiento
 */
class RegretAnalyzer {
public:
    struct Outcome {
        std::string option;
        std::string scenario;
        double payoff;
    };
    
    /**
     * @brief Calcula estrategia minimax regret
     * 
     * Regret = (Mejor payoff en escenario) - (Tu payoff en escenario)
     * Objetivo: Minimizar el MÁXIMO regret posible
     */
    std::string minimaxRegret(const std::vector<Outcome>& outcomes,
                             const std::vector<std::string>& scenarios) {
        std::map<std::string, std::map<std::string, double>> payoffs;
        std::set<std::string> options;
        
        // Organizar payoffs
        for (const auto& o : outcomes) {
            payoffs[o.option][o.scenario] = o.payoff;
            options.insert(o.option);
        }
        
        // Calcular mejor payoff por escenario
        std::map<std::string, double> best_in_scenario;
        for (const auto& scenario : scenarios) {
            double best = -std::numeric_limits<double>::infinity();
            for (const auto& option : options) {
                best = std::max(best, payoffs[option][scenario]);
            }
            best_in_scenario[scenario] = best;
        }
        
        // Calcular max regret por opción
        std::map<std::string, double> max_regret;
        for (const auto& option : options) {
            double max_r = 0;
            for (const auto& scenario : scenarios) {
                double regret = best_in_scenario[scenario] - payoffs[option][scenario];
                max_r = std::max(max_r, regret);
            }
            max_regret[option] = max_r;
        }
        
        // Elegir opción con menor max regret
        std::string best_option;
        double min_max_regret = std::numeric_limits<double>::infinity();
        for (const auto& [option, regret] : max_regret) {
            if (regret < min_max_regret) {
                min_max_regret = regret;
                best_option = option;
            }
        }
        
        return best_option;
    }
    
    /**
     * @brief Ejemplo:
     * 
     * Escenarios: [Precio sube 20%, Precio igual, Precio baja 20%]
     * 
     * MacBook ahora:   [-$200,  $0,   $300]  → max regret = $300
     * MacBook esperar: [$300,   $0,  -$200]  → max regret = $300
     * Laptop económico:[$100, -$50,  -$100]  → max regret = $200 (GANA)
     * 
     * Minimax: Laptop económico (lamentas menos en peor caso)
     */
};

// ============================================================================
// 3. REAL OPTIONS ANALYSIS - Valor de flexibilidad
// ============================================================================

/**
 * @brief Valoración de opciones reales (adaptado de finanzas)
 * 
 * VENTAJA vs Monte Carlo simple:
 * - Captura VALOR de poder cambiar decisión después
 * - Ejemplo: "Valor de poder upgradear RAM luego"
 */
class RealOptionsAnalyzer {
public:
    /**
     * @brief Calcula valor de opción de espera
     * 
     * Similar a Black-Scholes pero para decisiones operativas
     * 
     * @param current_value Valor actual de ejecutar ahora
     * @param volatility Incertidumbre del valor futuro (σ)
     * @param time_to_expiry Tiempo hasta que opción expire
     * @param risk_free_rate Tasa libre de riesgo
     * @return Valor adicional de poder esperar
     */
    double valueOfWaiting(double current_value, 
                         double volatility,
                         double time_to_expiry,
                         double risk_free_rate = 0.05) {
        // Aproximación simple de valor de opción
        // En realidad usarías Black-Scholes completo
        
        double d1 = (std::log(current_value) + 
                    (risk_free_rate + 0.5 * volatility * volatility) * time_to_expiry) /
                   (volatility * std::sqrt(time_to_expiry));
        
        // Valor adicional de flexibilidad
        double option_premium = current_value * volatility * std::sqrt(time_to_expiry) * 0.4;
        
        return option_premium;
    }
    
    /**
     * @brief Valor de opción de expansión
     * 
     * Ejemplo: Compro Mac Mini ahora, pero puedo upgradear a MacBook después
     */
    double valueOfExpansionOption(double base_cost,
                                  double expansion_cost,
                                  double expansion_benefit,
                                  double prob_need_expansion) {
        // Valor esperado de tener la opción
        double option_value = prob_need_expansion * 
                             std::max(0.0, expansion_benefit - expansion_cost);
        
        return option_value;
    }
};

// ============================================================================
// 4. MULTI-ARMED BANDIT - Exploración vs Explotación
// ============================================================================

/**
 * @brief Bandit para decisiones secuenciales con aprendizaje
 * 
 * VENTAJA vs Monte Carlo:
 * - APRENDE de resultados reales
 * - Balancea exploración (probar nuevas opciones) vs explotación (usar mejor)
 */
class MultiArmedBandit {
private:
    struct Arm {
        std::string name;
        double mean_reward;
        int pulls;
        double confidence_bound;
    };
    
    std::vector<Arm> arms_;
    int total_pulls_;
    
public:
    void addArm(const std::string& name) {
        arms_.push_back({name, 0.0, 0, std::numeric_limits<double>::infinity()});
        total_pulls_ = 0;
    }
    
    /**
     * @brief Upper Confidence Bound (UCB1) algorithm
     * 
     * Selecciona brazo balanceando:
     * - Reward promedio (explotación)
     * - Incertidumbre (exploración)
     */
    std::string selectArmUCB(double exploration_param = 2.0) {
        // Actualizar confidence bounds
        for (auto& arm : arms_) {
            if (arm.pulls == 0) {
                arm.confidence_bound = std::numeric_limits<double>::infinity();
            } else {
                arm.confidence_bound = arm.mean_reward + 
                    exploration_param * std::sqrt(std::log(total_pulls_) / arm.pulls);
            }
        }
        
        // Seleccionar brazo con mayor UCB
        auto best = std::max_element(arms_.begin(), arms_.end(),
            [](const Arm& a, const Arm& b) {
                return a.confidence_bound < b.confidence_bound;
            });
        
        return best->name;
    }
    
    /**
     * @brief Actualiza recompensa observada
     */
    void updateReward(const std::string& arm_name, double reward) {
        for (auto& arm : arms_) {
            if (arm.name == arm_name) {
                // Actualizar promedio incremental
                arm.mean_reward = (arm.mean_reward * arm.pulls + reward) / (arm.pulls + 1);
                arm.pulls++;
                total_pulls_++;
                break;
            }
        }
    }
    
    /**
     * @brief Ejemplo:
     * 
     * MultiArmedBandit mab;
     * mab.addArm("MacBook Air M2");
     * mab.addArm("Laptop económico");
     * 
     * // Cada semana pruebas una opción
     * for (int week = 0; week < 10; ++week) {
     *     std::string choice = mab.selectArmUCB();
     *     double satisfaction = usarLaptop(choice);  // Real
     *     mab.updateReward(choice, satisfaction);
     * }
     * 
     * // Aprende cuál laptop funciona mejor PARA TI
     */
};

// ============================================================================
// 5. PORTFOLIO OPTIMIZATION - Diversificación
// ============================================================================

/**
 * @brief Optimización de portfolio (Markowitz)
 * 
 * VENTAJA vs elegir UNA opción:
 * - Combina opciones para reducir riesgo
 * - Ejemplo: "60% trabajo remoto + 40% oficina"
 */
class PortfolioOptimizer {
public:
    /**
     * @brief Calcula frontera eficiente
     * 
     * @param expected_returns Returns esperados de cada opción
     * @param covariance_matrix Matriz de covarianza (riesgos correlacionados)
     * @return Pesos óptimos para cada opción
     */
    std::vector<double> optimizePortfolio(
        const std::vector<double>& expected_returns,
        const std::vector<std::vector<double>>& covariance_matrix,
        double target_return) {
        
        // Simplificación: Equal risk contribution
        size_t n = expected_returns.size();
        std::vector<double> weights(n, 1.0 / n);
        
        // En implementación completa usarías optimización cuadrática
        // Aquí solo mostramos la idea
        
        return weights;
    }
    
    /**
     * @brief Ejemplo:
     * 
     * PortfolioOptimizer po;
     * 
     * std::vector<double> returns = {0.15, 0.10, 0.20};  // MacBook, Laptop, Mini PC
     * std::vector<std::vector<double>> cov = {
     *     {0.04, 0.02, 0.01},
     *     {0.02, 0.09, 0.03},
     *     {0.01, 0.03, 0.16}
     * };
     * 
     * auto weights = po.optimizePortfolio(returns, cov, 0.13);
     * // Resultado: [0.5, 0.3, 0.2] → Diversifica entre opciones
     */
};

// ============================================================================
// 6. RISK ANALYSIS - Métricas avanzadas de riesgo
// ============================================================================

/**
 * @brief Análisis avanzado de riesgo financiero
 * 
 * VENTAJA vs stddev simple:
 * - VaR: "Perderé máximo $X con 95% confianza"
 * - CVaR: "En el peor 5%, promedio de pérdida es $Y"
 * - Prob. ruina: "¿Probabilidad de perder todo?"
 */
class RiskAnalyzer {
public:
    /**
     * @brief Value at Risk (VaR)
     * 
     * @param outcomes Distribución de resultados
     * @param confidence Nivel de confianza (ej: 0.95)
     * @return Pérdida máxima esperada con ese nivel de confianza
     */
    double calculateVaR(const std::vector<double>& outcomes, double confidence = 0.95) {
        std::vector<double> sorted = outcomes;
        std::sort(sorted.begin(), sorted.end());
        
        size_t index = static_cast<size_t>((1.0 - confidence) * sorted.size());
        return sorted[index];
    }
    
    /**
     * @brief Conditional Value at Risk (CVaR) / Expected Shortfall
     * 
     * Promedio de pérdidas en el peor percentil
     */
    double calculateCVaR(const std::vector<double>& outcomes, double confidence = 0.95) {
        double var = calculateVaR(outcomes, confidence);
        
        // Promedio de outcomes peores que VaR
        double sum = 0;
        int count = 0;
        for (double outcome : outcomes) {
            if (outcome <= var) {
                sum += outcome;
                count++;
            }
        }
        
        return count > 0 ? sum / count : var;
    }
    
    /**
     * @brief Probabilidad de ruina
     * 
     * ¿Probabilidad de perder más de X% del capital?
     */
    double probabilityOfRuin(const std::vector<double>& outcomes, 
                            double initial_capital,
                            double ruin_threshold = 0.5) {
        int ruined = 0;
        for (double outcome : outcomes) {
            if (outcome < -initial_capital * ruin_threshold) {
                ruined++;
            }
        }
        return static_cast<double>(ruined) / outcomes.size();
    }
    
    /**
     * @brief Sharpe Ratio (return ajustado por riesgo)
     */
    double sharpeRatio(const std::vector<double>& outcomes, 
                      double risk_free_rate = 0.05) {
        double mean = std::accumulate(outcomes.begin(), outcomes.end(), 0.0) / outcomes.size();
        
        double variance = 0;
        for (double x : outcomes) {
            variance += (x - mean) * (x - mean);
        }
        double stddev = std::sqrt(variance / outcomes.size());
        
        return (mean - risk_free_rate) / stddev;
    }
};

// ============================================================================
// 7. SCENARIO PLANNING - Futuros alternativos
// ============================================================================

/**
 * @brief Planificación de escenarios (Shell method)
 * 
 * VENTAJA vs Monte Carlo:
 * - Crea NARRATIVAS coherentes de futuros posibles
 * - Útil cuando incertidumbre es estructural (no solo ruido)
 */
class ScenarioPlanner {
public:
    struct Scenario {
        std::string name;
        std::string narrative;  // Historia del futuro
        double probability;
        std::map<std::string, double> factor_values;
    };
    
    /**
     * @brief Evalúa robustez de decisión entre escenarios
     * 
     * @return Opción que funciona BIEN en más escenarios
     */
    std::string findRobustOption(
        const std::vector<std::string>& options,
        const std::vector<Scenario>& scenarios,
        std::function<double(const std::string&, const Scenario&)> evaluate) {
        
        std::map<std::string, double> scores;
        
        for (const auto& option : options) {
            double weighted_score = 0;
            for (const auto& scenario : scenarios) {
                double score = evaluate(option, scenario);
                weighted_score += score * scenario.probability;
            }
            scores[option] = weighted_score;
        }
        
        return std::max_element(scores.begin(), scores.end(),
            [](const auto& a, const auto& b) { return a.second < b.second; })->first;
    }
    
    /**
     * @brief Ejemplo:
     * 
     * ScenarioPlanner sp;
     * 
     * Scenario boom = {
     *     "Boom Tecnológico",
     *     "IA revoluciona desarrollo, demanda freelance +200%",
     *     0.30,
     *     {{"ingreso_mensual", 5000}, {"costo_laptop", 2000}}
     * };
     * 
     * Scenario recession = {
     *     "Recesión Global",
     *     "Empresas recortan, freelance -50%",
     *     0.20,
     *     {{"ingreso_mensual", 1000}, {"costo_laptop", 1500}}
     * };
     * 
     * // ¿Qué laptop funciona en AMBOS escenarios?
     */
};

// ============================================================================
// 8. CORRELATION ANALYSIS - Detectar dependencias
// ============================================================================

/**
 * @brief Análisis de correlaciones entre factores
 * 
 * VENTAJA vs asumir independencia:
 * - Detecta cuando factores se mueven juntos
 * - Ejemplo: "Precio alto → Mayor calidad" (correlación +0.8)
 */
class CorrelationAnalyzer {
public:
    /**
     * @brief Calcula matriz de correlación
     */
    std::vector<std::vector<double>> correlationMatrix(
        const std::vector<std::string>& factor_names,
        const std::vector<std::map<std::string, double>>& simulations) {
        
        size_t n = factor_names.size();
        std::vector<std::vector<double>> corr(n, std::vector<double>(n, 0.0));
        
        for (size_t i = 0; i < n; ++i) {
            for (size_t j = 0; j < n; ++j) {
                if (i == j) {
                    corr[i][j] = 1.0;
                    continue;
                }
                
                // Calcular correlación de Pearson
                std::vector<double> x, y;
                for (const auto& sim : simulations) {
                    x.push_back(sim.at(factor_names[i]));
                    y.push_back(sim.at(factor_names[j]));
                }
                
                corr[i][j] = pearsonCorrelation(x, y);
            }
        }
        
        return corr;
    }
    
    /**
     * @brief Identifica factores altamente correlacionados
     * 
     * Útil para simplificar modelo (eliminar redundancia)
     */
    std::vector<std::pair<std::string, std::string>> findHighCorrelations(
        const std::vector<std::string>& factor_names,
        const std::vector<std::vector<double>>& corr_matrix,
        double threshold = 0.7) {
        
        std::vector<std::pair<std::string, std::string>> high_corr;
        
        for (size_t i = 0; i < factor_names.size(); ++i) {
            for (size_t j = i + 1; j < factor_names.size(); ++j) {
                if (std::abs(corr_matrix[i][j]) > threshold) {
                    high_corr.push_back({factor_names[i], factor_names[j]});
                }
            }
        }
        
        return high_corr;
    }
    
private:
    double pearsonCorrelation(const std::vector<double>& x, 
                             const std::vector<double>& y) {
        double mean_x = std::accumulate(x.begin(), x.end(), 0.0) / x.size();
        double mean_y = std::accumulate(y.begin(), y.end(), 0.0) / y.size();
        
        double cov = 0, var_x = 0, var_y = 0;
        for (size_t i = 0; i < x.size(); ++i) {
            double dx = x[i] - mean_x;
            double dy = y[i] - mean_y;
            cov += dx * dy;
            var_x += dx * dx;
            var_y += dy * dy;
        }
        
        return cov / std::sqrt(var_x * var_y);
    }
};

} // namespace DecisionFramework
