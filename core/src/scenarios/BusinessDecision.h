#pragma once

#include <string>
#include <map>
#include <vector>
#include <memory>
#include <functional>
#include <random>
#include <numeric>
#include <algorithm>
#include <cmath>

namespace DecisionMaker {
namespace Business {

/**
 * @brief Factor abstracto que puede influenciar una decisión
 * 
 * Patrón Strategy: Cada factor implementa su propia lógica de evaluación
 */
class DecisionFactor {
public:
    virtual ~DecisionFactor() = default;
    
    /**
     * @brief Nombre del factor (ej. "Market Competition")
     */
    virtual std::string getName() const = 0;
    
    /**
     * @brief Evalúa el impacto del factor en un escenario
     * @return Valor entre 0-1 donde 1 es máximo impacto positivo
     */
    virtual double evaluate() const = 0;
    
    /**
     * @brief Peso del factor en la decisión final (0-1)
     */
    virtual double getWeight() const = 0;
    
    /**
     * @brief Categoría del factor (para agrupación)
     */
    virtual std::string getCategory() const = 0;
};

/**
 * @brief Factor numérico simple con valor y peso
 */
class NumericFactor : public DecisionFactor {
protected:
    std::string name_;
    std::string category_;
    double value_;      // Valor actual (0-1)
    double weight_;     // Peso en decisión (0-1)
    
public:
    NumericFactor(const std::string& name, 
                  const std::string& category,
                  double value, 
                  double weight)
        : name_(name), category_(category), value_(value), weight_(weight) {}
    
    std::string getName() const override { return name_; }
    std::string getCategory() const override { return category_; }
    double evaluate() const override { return value_; }
    double getWeight() const override { return weight_; }
    
    void setValue(double value) { value_ = value; }
    double getValue() const { return value_; }
};

/**
 * @brief Factor con distribución de probabilidad
 */
class StochasticFactor : public DecisionFactor {
protected:
    std::string name_;
    std::string category_;
    double mean_;
    double std_dev_;
    double weight_;
    mutable std::mt19937* rng_;
    
public:
    StochasticFactor(const std::string& name,
                     const std::string& category,
                     double mean,
                     double std_dev,
                     double weight,
                     std::mt19937* rng)
        : name_(name), category_(category), mean_(mean), 
          std_dev_(std_dev), weight_(weight), rng_(rng) {}
    
    std::string getName() const override { return name_; }
    std::string getCategory() const override { return category_; }
    double getWeight() const override { return weight_; }
    
    double evaluate() const override {
        std::normal_distribution<double> dist(mean_, std_dev_);
        double value = dist(*rng_);
        // Clamp entre 0 y 1
        return std::max(0.0, std::min(1.0, value));
    }
    
    void setMean(double mean) { mean_ = mean; }
    void setStdDev(double std_dev) { std_dev_ = std_dev; }
};

/**
 * @brief Factor compuesto (combina otros factores)
 */
class CompositeFactor : public DecisionFactor {
protected:
    std::string name_;
    std::string category_;
    double weight_;
    std::vector<std::shared_ptr<DecisionFactor>> sub_factors_;
    std::function<double(const std::vector<double>&)> aggregation_func_;
    
public:
    CompositeFactor(const std::string& name,
                    const std::string& category,
                    double weight,
                    std::function<double(const std::vector<double>&)> aggregator)
        : name_(name), category_(category), weight_(weight), 
          aggregation_func_(aggregator) {}
    
    std::string getName() const override { return name_; }
    std::string getCategory() const override { return category_; }
    double getWeight() const override { return weight_; }
    
    void addSubFactor(std::shared_ptr<DecisionFactor> factor) {
        sub_factors_.push_back(factor);
    }
    
    double evaluate() const override {
        std::vector<double> values;
        for (const auto& factor : sub_factors_) {
            values.push_back(factor->evaluate());
        }
        return aggregation_func_(values);
    }
};

/**
 * @brief Opciones/alternativas a evaluar
 */
struct DecisionOption {
    std::string id;
    std::string name;
    std::string description;
    
    // Factores específicos de esta opción
    std::map<std::string, std::shared_ptr<DecisionFactor>> factors;
    
    // Metadatos adicionales
    std::map<std::string, double> metadata;
    
    DecisionOption(const std::string& id, const std::string& name)
        : id(id), name(name) {}
};

/**
 * @brief Resultado de evaluar una opción en una simulación
 */
struct SimulationResult {
    std::string option_id;
    
    // Métricas agregadas
    double total_score;
    std::map<std::string, double> factor_scores;  // Score por factor
    std::map<std::string, double> category_scores; // Score por categoría
    
    // Estadísticas
    bool is_successful;
    double confidence_level;
    
    // Métricas personalizadas
    std::map<std::string, double> custom_metrics;
};

/**
 * @brief Evaluador de decisiones (Patrón Strategy para diferentes criterios)
 */
class DecisionEvaluator {
public:
    virtual ~DecisionEvaluator() = default;
    
    /**
     * @brief Evalúa una opción y retorna un score
     */
    virtual double evaluate(const DecisionOption& option) const = 0;
    
    /**
     * @brief Nombre del criterio de evaluación
     */
    virtual std::string getCriterionName() const = 0;
};

/**
 * @brief Evaluador ponderado (suma de factores * pesos)
 */
class WeightedSumEvaluator : public DecisionEvaluator {
public:
    double evaluate(const DecisionOption& option) const override {
        double total_score = 0.0;
        double total_weight = 0.0;
        
        for (const auto& [name, factor] : option.factors) {
            double factor_score = factor->evaluate();
            double weight = factor->getWeight();
            total_score += factor_score * weight;
            total_weight += weight;
        }
        
        return total_weight > 0 ? total_score / total_weight : 0.0;
    }
    
    std::string getCriterionName() const override {
        return "Weighted Sum";
    }
};

/**
 * @brief Evaluador multi-criterio (considera categorías)
 */
class MultiCriteriaEvaluator : public DecisionEvaluator {
private:
    std::map<std::string, double> category_weights_;
    
public:
    MultiCriteriaEvaluator(const std::map<std::string, double>& weights)
        : category_weights_(weights) {}
    
    double evaluate(const DecisionOption& option) const override {
        // Agrupa factores por categoría
        std::map<std::string, std::vector<double>> category_values;
        
        for (const auto& [name, factor] : option.factors) {
            std::string category = factor->getCategory();
            category_values[category].push_back(
                factor->evaluate() * factor->getWeight()
            );
        }
        
        // Calcula score por categoría
        double total_score = 0.0;
        double total_weight = 0.0;
        
        for (const auto& [category, values] : category_values) {
            double category_avg = 0.0;
            for (double v : values) category_avg += v;
            category_avg /= values.size();
            
            double weight = category_weights_.count(category) 
                ? category_weights_.at(category) : 1.0;
            
            total_score += category_avg * weight;
            total_weight += weight;
        }
        
        return total_weight > 0 ? total_score / total_weight : 0.0;
    }
    
    std::string getCriterionName() const override {
        return "Multi-Criteria";
    }
};

/**
 * @brief Motor de simulación Monte Carlo genérico
 * 
 * Patrón Template Method: Define el flujo, las subclases personalizan pasos
 */
class MonteCarloSimulator {
protected:
    std::vector<DecisionOption> options_;
    std::shared_ptr<DecisionEvaluator> evaluator_;
    std::mt19937 rng_;
    size_t num_simulations_;
    
    // Resultados
    std::map<std::string, std::vector<SimulationResult>> results_;
    
public:
    MonteCarloSimulator(size_t num_simulations, unsigned int seed = 0)
        : num_simulations_(num_simulations) {
        if (seed == 0) {
            std::random_device rd;
            rng_.seed(rd());
        } else {
            rng_.seed(seed);
        }
    }
    
    void addOption(const DecisionOption& option) {
        options_.push_back(option);
    }
    
    void setEvaluator(std::shared_ptr<DecisionEvaluator> evaluator) {
        evaluator_ = evaluator;
    }
    
    /**
     * @brief Ejecuta las simulaciones
     */
    virtual void run() {
        results_.clear();
        
        for (const auto& option : options_) {
            std::vector<SimulationResult> option_results;
            option_results.reserve(num_simulations_);
            
            for (size_t i = 0; i < num_simulations_; ++i) {
                SimulationResult result = simulateOnce(option);
                option_results.push_back(result);
            }
            
            results_[option.id] = std::move(option_results);
        }
    }
    
    /**
     * @brief Simula una vez (puede ser sobrescrito)
     */
    virtual SimulationResult simulateOnce(const DecisionOption& option) {
        SimulationResult result;
        result.option_id = option.id;
        
        // Evaluar cada factor
        for (const auto& [name, factor] : option.factors) {
            double score = factor->evaluate();
            result.factor_scores[name] = score;
            
            // Agregar a categoría
            std::string category = factor->getCategory();
            if (result.category_scores.find(category) == result.category_scores.end()) {
                result.category_scores[category] = 0.0;
            }
            result.category_scores[category] += score * factor->getWeight();
        }
        
        // Score total usando evaluador
        result.total_score = evaluator_->evaluate(option);
        
        // Determinar éxito (puede personalizarse)
        result.is_successful = result.total_score > 0.6;
        result.confidence_level = result.total_score;
        
        return result;
    }
    
    /**
     * @brief Obtiene resultados
     */
    const std::map<std::string, std::vector<SimulationResult>>& getResults() const {
        return results_;
    }
    
    /**
     * @brief Obtiene estadísticas agregadas
     */
    std::map<std::string, double> getStatistics(const std::string& option_id) const {
        std::map<std::string, double> stats;
        
        if (results_.find(option_id) == results_.end()) {
            return stats;
        }
        
        const auto& results = results_.at(option_id);
        
        // Calcular estadísticas
        double sum_score = 0.0;
        double min_score = std::numeric_limits<double>::max();
        double max_score = std::numeric_limits<double>::min();
        int success_count = 0;
        
        std::vector<double> scores;
        for (const auto& result : results) {
            double score = result.total_score;
            scores.push_back(score);
            sum_score += score;
            min_score = std::min(min_score, score);
            max_score = std::max(max_score, score);
            if (result.is_successful) success_count++;
        }
        
        stats["mean"] = sum_score / results.size();
        stats["min"] = min_score;
        stats["max"] = max_score;
        stats["success_rate"] = static_cast<double>(success_count) / results.size();
        
        // Percentiles
        std::sort(scores.begin(), scores.end());
        stats["p25"] = scores[scores.size() / 4];
        stats["p50"] = scores[scores.size() / 2];
        stats["p75"] = scores[(scores.size() * 3) / 4];
        
        return stats;
    }
};

/**
 * @brief Builder para construir opciones de decisión fácilmente
 */
class DecisionOptionBuilder {
private:
    DecisionOption option_;
    std::mt19937* rng_;
    
public:
    DecisionOptionBuilder(const std::string& id, const std::string& name)
        : option_(id, name), rng_(nullptr) {}
    
    DecisionOptionBuilder& setDescription(const std::string& desc) {
        option_.description = desc;
        return *this;
    }
    
    DecisionOptionBuilder& setRNG(std::mt19937* rng) {
        rng_ = rng;
        return *this;
    }
    
    DecisionOptionBuilder& addNumericFactor(
        const std::string& name,
        const std::string& category,
        double value,
        double weight = 1.0)
    {
        auto factor = std::make_shared<NumericFactor>(name, category, value, weight);
        option_.factors[name] = factor;
        return *this;
    }
    
    DecisionOptionBuilder& addStochasticFactor(
        const std::string& name,
        const std::string& category,
        double mean,
        double std_dev,
        double weight = 1.0)
    {
        auto factor = std::make_shared<StochasticFactor>(
            name, category, mean, std_dev, weight, rng_
        );
        option_.factors[name] = factor;
        return *this;
    }
    
    DecisionOptionBuilder& addMetadata(const std::string& key, double value) {
        option_.metadata[key] = value;
        return *this;
    }
    
    DecisionOption build() {
        return option_;
    }
};

} // namespace Business
} // namespace DecisionMaker
