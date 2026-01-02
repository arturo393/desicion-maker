#pragma once

#include "../core/Types.h"
#include <random>
#include <cmath>

namespace DecisionMaker {

/**
 * @brief Distribución normal (gaussiana)
 */
class NormalDistribution : public Distribution {
private:
    double mean_;
    double stddev_;
    mutable std::normal_distribution<double> dist_;
    
public:
    NormalDistribution(double mean, double stddev);
    
    double sample(std::mt19937& rng) const override;
    double mean() const override { return mean_; }
    double stddev() const override { return stddev_; }
    std::unique_ptr<Distribution> clone() const override;
    std::string name() const override { return "Normal"; }
    
    // Métodos específicos
    double pdf(double x) const; // Función de densidad de probabilidad
    double cdf(double x) const; // Función de distribución acumulativa
};

/**
 * @brief Distribución uniforme
 */
class UniformDistribution : public Distribution {
private:
    double min_;
    double max_;
    mutable std::uniform_real_distribution<double> dist_;
    
public:
    UniformDistribution(double min, double max);
    
    double sample(std::mt19937& rng) const override;
    double mean() const override { return (min_ + max_) / 2.0; }
    double stddev() const override { return (max_ - min_) / std::sqrt(12.0); }
    std::unique_ptr<Distribution> clone() const override;
    std::string name() const override { return "Uniform"; }
    
    double getMin() const { return min_; }
    double getMax() const { return max_; }
};

/**
 * @brief Distribución exponencial
 */
class ExponentialDistribution : public Distribution {
private:
    double lambda_;
    mutable std::exponential_distribution<double> dist_;
    
public:
    explicit ExponentialDistribution(double lambda);
    
    double sample(std::mt19937& rng) const override;
    double mean() const override { return 1.0 / lambda_; }
    double stddev() const override { return 1.0 / lambda_; }
    std::unique_ptr<Distribution> clone() const override;
    std::string name() const override { return "Exponential"; }
    
    double getLambda() const { return lambda_; }
};

/**
 * @brief Distribución log-normal
 */
class LogNormalDistribution : public Distribution {
private:
    double mu_;
    double sigma_;
    mutable std::lognormal_distribution<double> dist_;
    
public:
    LogNormalDistribution(double mu, double sigma);
    
    double sample(std::mt19937& rng) const override;
    double mean() const override { return std::exp(mu_ + sigma_ * sigma_ / 2.0); }
    double stddev() const override;
    std::unique_ptr<Distribution> clone() const override;
    std::string name() const override { return "LogNormal"; }
    
    double getMu() const { return mu_; }
    double getSigma() const { return sigma_; }
};

/**
 * @brief Distribución triangular
 */
class TriangularDistribution : public Distribution {
private:
    double min_;
    double max_;
    double mode_;
    
public:
    TriangularDistribution(double min, double max, double mode);
    
    double sample(std::mt19937& rng) const override;
    double mean() const override { return (min_ + max_ + mode_) / 3.0; }
    double stddev() const override;
    std::unique_ptr<Distribution> clone() const override;
    std::string name() const override { return "Triangular"; }
    
    double getMin() const { return min_; }
    double getMax() const { return max_; }
    double getMode() const { return mode_; }
};

/**
 * @brief Distribución beta
 */
class BetaDistribution : public Distribution {
private:
    double alpha_;
    double beta_;
    double min_;
    double max_;
    
public:
    BetaDistribution(double alpha, double beta, double min = 0.0, double max = 1.0);
    
    double sample(std::mt19937& rng) const override;
    double mean() const override;
    double stddev() const override;
    std::unique_ptr<Distribution> clone() const override;
    std::string name() const override { return "Beta"; }
    
    double getAlpha() const { return alpha_; }
    double getBeta() const { return beta_; }
    double getMin() const { return min_; }
    double getMax() const { return max_; }
};

/**
 * @brief Distribución gamma
 */
class GammaDistribution : public Distribution {
private:
    double shape_;
    double scale_;
    mutable std::gamma_distribution<double> dist_;
    
public:
    GammaDistribution(double shape, double scale);
    
    double sample(std::mt19937& rng) const override;
    double mean() const override { return shape_ * scale_; }
    double stddev() const override { return std::sqrt(shape_) * scale_; }
    std::unique_ptr<Distribution> clone() const override;
    std::string name() const override { return "Gamma"; }
    
    double getShape() const { return shape_; }
    double getScale() const { return scale_; }
};

/**
 * @brief Distribución discreta personalizada
 */
class DiscreteDistribution : public Distribution {
private:
    std::vector<double> values_;
    std::vector<double> probabilities_;
    mutable std::discrete_distribution<int> dist_;
    
public:
    DiscreteDistribution(const std::vector<double>& values, 
                        const std::vector<double>& probabilities);
    
    double sample(std::mt19937& rng) const override;
    double mean() const override;
    double stddev() const override;
    std::unique_ptr<Distribution> clone() const override;
    std::string name() const override { return "Discrete"; }
    
    const std::vector<double>& getValues() const { return values_; }
    const std::vector<double>& getProbabilities() const { return probabilities_; }
};

/**
 * @brief Factory para crear distribuciones desde strings
 */
class DistributionFactory {
public:
    /**
     * @brief Crea una distribución desde una descripción textual
     * @param description Descripción (ej: "normal(0,1)", "uniform(0,10)")
     * @return Puntero único a la distribución
     */
    static std::unique_ptr<Distribution> create(const std::string& description);
    
    /**
     * @brief Lista todas las distribuciones disponibles
     * @return Vector con nombres de distribuciones
     */
    static std::vector<std::string> getAvailableDistributions();
    
    /**
     * @brief Obtiene ayuda sobre una distribución específica
     * @param name Nombre de la distribución
     * @return String con la ayuda
     */
    static std::string getHelp(const std::string& name);
};

} // namespace DecisionMaker