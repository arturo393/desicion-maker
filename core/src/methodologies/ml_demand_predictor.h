#ifndef ML_DEMAND_PREDICTOR_H
#define ML_DEMAND_PREDICTOR_H

#include <vector>
#include <string>
#include <cmath>
#include <algorithm>
#include <numeric>

namespace decision_maker {

/**
 * Histórico de ventas de un producto
 */
struct SalesHistory {
    int day;                    // Día del histórico (1-365)
    double price;               // Precio listado
    int days_listed;            // Días que llevaba listado
    bool sold;                  // ¿Se vendió?
    std::string condition;      // "nuevo", "restaurado", "gastado"
    std::string marketplace;    // "OLX", "ML", "Yapo"
    double competitor_count;    // Cantidad de competidores con precio similar
};

/**
 * Predicción de demanda
 */
struct DemandPrediction {
    double sale_probability;    // Probabilidad de venta (0-1)
    double expected_sale_days;  // Días esperados para vender
    std::string demand_level;   // "BAJA", "MEDIA", "ALTA"
    double confidence;          // Confianza en la predicción (0-1)
    std::string explanation;    // Explicación de la predicción
};

/**
 * Modelo de predicción de demanda usando Machine Learning
 * Utiliza regresión logística y análisis de tendencias
 */
class MLDemandPredictor {
public:
    MLDemandPredictor();
    
    /**
     * Entrenar el modelo con datos históricos
     */
    void train(const std::vector<SalesHistory>& training_data);
    
    /**
     * Predecir demanda para un producto dado
     */
    DemandPrediction predict(
        double price,
        int days_listed,
        const std::string& condition,
        const std::string& marketplace,
        double competitor_count
    );
    
    /**
     * Predecir con datos completos de histórico
     */
    DemandPrediction predict_with_history(
        const std::vector<SalesHistory>& recent_sales,
        double current_price,
        const std::string& condition
    );
    
    /**
     * Obtener importancia de características
     */
    struct FeatureImportance {
        std::string feature_name;
        double importance_score;  // 0-1
    };
    
    std::vector<FeatureImportance> get_feature_importance() const;
    
    /**
     * Generar reporte de modelo
     */
    std::string generate_model_report() const;
    
private:
    // Parámetros del modelo entrenado
    double weight_price;
    double weight_days_listed;
    double weight_condition;
    double weight_marketplace;
    double weight_competitors;
    double intercept;
    
    // Estadísticas de entrenamiento
    int training_samples;
    double training_accuracy;
    double avg_sale_probability;
    
    // Normalizadores (para escalar características)
    double price_mean, price_std;
    double days_mean, days_std;
    double competitors_mean, competitors_std;
    
    // Métodos privados
    double sigmoid(double x) const;
    double normalize_feature(double value, double mean, double std_dev) const;
    void calculate_weights(const std::vector<SalesHistory>& data);
    double calculate_accuracy(const std::vector<SalesHistory>& data) const;
};

} // namespace decision_maker

#endif // ML_DEMAND_PREDICTOR_H
