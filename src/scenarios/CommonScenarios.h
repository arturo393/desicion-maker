#pragma once

#include "../core/Scenario.h"
#include "../distributions/Distributions.h"

namespace DecisionMaker {
namespace Scenarios {

/**
 * @brief Escenario genérico de inversión
 * 
 * Modela una decisión de inversión considerando:
 * - Retorno esperado (con incertidumbre)
 * - Riesgo de pérdida
 * - Costos de transacción
 * - Horizonte temporal
 */
class InvestmentScenario : public DecisionScenario {
public:
    InvestmentScenario();
    
    SimulationResult runSimulation(std::mt19937& rng) const override;
    bool validateConfiguration() const override;
    
    std::vector<std::string> getRequiredParameters() const override {
        return {"initial_investment", "expected_return", "volatility", "time_horizon"};
    }
    
    std::vector<std::string> getProducedMetrics() const override {
        return {"final_value", "total_return", "annualized_return", "max_drawdown"};
    }
    
    // Métodos específicos para configuración
    void setInitialInvestment(double amount);
    void setExpectedReturn(double annual_return, double volatility);
    void setTimeHorizon(double years);
    void setTransactionCosts(double percentage);
};

/**
 * @brief Escenario de planificación de proyectos
 * 
 * Modela la finalización de un proyecto considerando:
 * - Duración de tareas individuales
 * - Dependencias entre tareas
 * - Recursos disponibles
 * - Riesgos e interrupciones
 */
class ProjectPlanningScenario : public DecisionScenario {
public:
    struct Task {
        std::string name;
        std::unique_ptr<Distribution> duration;
        std::vector<std::string> dependencies;
        double resource_requirement;
        double failure_probability;
    };
    
private:
    std::vector<Task> tasks_;
    
public:
    ProjectPlanningScenario();
    
    void addTask(const std::string& name, 
                std::unique_ptr<Distribution> duration,
                const std::vector<std::string>& dependencies = {},
                double resource_requirement = 1.0,
                double failure_probability = 0.0);
    
    SimulationResult runSimulation(std::mt19937& rng) const override;
    bool validateConfiguration() const override;
    
    std::vector<std::string> getRequiredParameters() const override {
        return {"available_resources", "daily_cost"};
    }
    
    std::vector<std::string> getProducedMetrics() const override {
        return {"total_duration", "total_cost", "critical_path_duration", "resource_utilization"};
    }
};

/**
 * @brief Escenario de gestión de inventarios
 * 
 * Modela decisiones de inventario considerando:
 * - Demanda variable
 * - Costos de almacenamiento
 * - Costos de faltantes
 * - Tiempos de reposición variables
 */
class InventoryManagementScenario : public DecisionScenario {
public:
    InventoryManagementScenario();
    
    SimulationResult runSimulation(std::mt19937& rng) const override;
    bool validateConfiguration() const override;
    
    std::vector<std::string> getRequiredParameters() const override {
        return {"demand_distribution", "holding_cost", "shortage_cost", 
                "lead_time_distribution", "order_cost"};
    }
    
    std::vector<std::string> getProducedMetrics() const override {
        return {"total_cost", "service_level", "average_inventory", "stockout_frequency"};
    }
    
    // Configuración específica
    void setDemandDistribution(std::unique_ptr<Distribution> demand);
    void setLeadTimeDistribution(std::unique_ptr<Distribution> lead_time);
    void setCosts(double holding_cost, double shortage_cost, double order_cost);
    void setPolicy(double reorder_point, double order_quantity);
};

/**
 * @brief Escenario de decisiones de carrera profesional
 * 
 * Modela decisiones profesionales considerando:
 * - Crecimiento salarial en diferentes trayectorias
 * - Probabilidades de promoción
 * - Satisfacción laboral
 * - Oportunidades de mercado
 */
class CareerDecisionScenario : public DecisionScenario {
public:
    struct CareerPath {
        std::string name;
        double initial_salary;
        std::unique_ptr<Distribution> salary_growth;
        std::unique_ptr<Distribution> promotion_probability;
        std::unique_ptr<Distribution> satisfaction_score;
        double market_demand_factor;
    };
    
private:
    std::vector<CareerPath> career_paths_;
    
public:
    CareerDecisionScenario();
    
    void addCareerPath(const std::string& name,
                      double initial_salary,
                      std::unique_ptr<Distribution> salary_growth,
                      std::unique_ptr<Distribution> promotion_prob,
                      std::unique_ptr<Distribution> satisfaction,
                      double market_demand = 1.0);
    
    SimulationResult runSimulation(std::mt19937& rng) const override;
    bool validateConfiguration() const override;
    
    std::vector<std::string> getRequiredParameters() const override {
        return {"time_horizon", "satisfaction_weight", "salary_weight"};
    }
    
    std::vector<std::string> getProducedMetrics() const override {
        return {"lifetime_earnings", "average_satisfaction", "promotion_count", "composite_score"};
    }
};

/**
 * @brief Escenario de optimización de rutas
 * 
 * Modela decisiones de transporte considerando:
 * - Tiempos de viaje variables
 * - Costos de combustible
 * - Probabilidades de congestión
 * - Condiciones climáticas
 */
class RouteOptimizationScenario : public DecisionScenario {
public:
    struct Route {
        std::string name;
        double base_distance;
        std::unique_ptr<Distribution> travel_time;
        std::unique_ptr<Distribution> fuel_cost;
        double congestion_probability;
        double weather_delay_factor;
    };
    
private:
    std::vector<Route> routes_;
    
public:
    RouteOptimizationScenario();
    
    void addRoute(const std::string& name,
                 double distance,
                 std::unique_ptr<Distribution> travel_time,
                 std::unique_ptr<Distribution> fuel_cost,
                 double congestion_prob = 0.1,
                 double weather_factor = 1.0);
    
    SimulationResult runSimulation(std::mt19937& rng) const override;
    bool validateConfiguration() const override;
    
    std::vector<std::string> getRequiredParameters() const override {
        return {"time_value", "fuel_price", "weather_conditions"};
    }
    
    std::vector<std::string> getProducedMetrics() const override {
        return {"total_cost", "travel_time", "fuel_consumption", "delay_probability"};
    }
};

/**
 * @brief Escenario de análisis de riesgos de seguridad
 * 
 * Modela riesgos de seguridad considerando:
 * - Probabilidades de diferentes tipos de amenazas
 * - Impacto de cada amenaza
 * - Efectividad de medidas de seguridad
 * - Costos de implementación
 */
class SecurityRiskScenario : public DecisionScenario {
public:
    struct ThreatModel {
        std::string name;
        std::unique_ptr<Distribution> probability;
        std::unique_ptr<Distribution> impact;
        double mitigation_effectiveness;
        double mitigation_cost;
    };
    
private:
    std::vector<ThreatModel> threats_;
    
public:
    SecurityRiskScenario();
    
    void addThreat(const std::string& name,
                  std::unique_ptr<Distribution> probability,
                  std::unique_ptr<Distribution> impact,
                  double mitigation_effectiveness = 0.0,
                  double mitigation_cost = 0.0);
    
    SimulationResult runSimulation(std::mt19937& rng) const override;
    bool validateConfiguration() const override;
    
    std::vector<std::string> getRequiredParameters() const override {
        return {"security_budget", "risk_tolerance"};
    }
    
    std::vector<std::string> getProducedMetrics() const override {
        return {"total_risk", "mitigation_cost", "residual_risk", "cost_benefit_ratio"};
    }
};

} // namespace Scenarios
} // namespace DecisionMaker