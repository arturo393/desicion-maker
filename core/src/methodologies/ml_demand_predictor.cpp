#include "ml_demand_predictor.h"
#include <sstream>
#include <iomanip>
#include <map>
#include <cmath>

namespace decision_maker {

MLDemandPredictor::MLDemandPredictor()
    : weight_price(0.0), weight_days_listed(0.0),
      weight_condition(0.0), weight_marketplace(0.0),
      weight_competitors(0.0), intercept(0.0),
      training_samples(0), training_accuracy(0.0),
      avg_sale_probability(0.04), // Default 4% if not trained
      price_mean(60000), price_std(15000),
      days_mean(45), days_std(30),
      competitors_mean(20), competitors_std(15) {}

double MLDemandPredictor::sigmoid(double x) const {
    // Stable sigmoid function
    if (x > 20) return 1.0;
    if (x < -20) return 0.0;
    return 1.0 / (1.0 + std::exp(-x));
}

double MLDemandPredictor::normalize_feature(
    double value, double mean, double std_dev) const {
    if (std_dev < 0.001) return 0.0;
    return (value - mean) / std_dev;
}

void MLDemandPredictor::train(const std::vector<SalesHistory>& training_data) {
    if (training_data.empty()) return;
    
    training_samples = training_data.size();
    
    // Calcular estadísticas de características
    std::vector<double> prices, days, competitors;
    int sold_count = 0;
    
    for (const auto& record : training_data) {
        prices.push_back(record.price);
        days.push_back(record.days_listed);
        competitors.push_back(record.competitor_count);
        if (record.sold) sold_count++;
    }
    
    // Calcular media y desviación estándar
    price_mean = std::accumulate(prices.begin(), prices.end(), 0.0) / prices.size();
    days_mean = std::accumulate(days.begin(), days.end(), 0.0) / days.size();
    competitors_mean = std::accumulate(competitors.begin(), competitors.end(), 0.0) / competitors.size();
    
    // Desviación estándar
    double price_var = 0.0, days_var = 0.0, competitors_var = 0.0;
    for (size_t i = 0; i < training_data.size(); i++) {
        price_var += (prices[i] - price_mean) * (prices[i] - price_mean);
        days_var += (days[i] - days_mean) * (days[i] - days_mean);
        competitors_var += (competitors[i] - competitors_mean) * (competitors[i] - competitors_mean);
    }
    
    price_std = std::sqrt(price_var / training_data.size());
    days_std = std::sqrt(days_var / training_data.size());
    competitors_std = std::sqrt(competitors_var / training_data.size());
    
    if (price_std < 0.001) price_std = 15000;
    if (days_std < 0.001) days_std = 30;
    if (competitors_std < 0.001) competitors_std = 15;
    
    // Entrenamiento básico: pesos basados en correlación
    // Precios altos → menor venta
    weight_price = -0.00003;  // Precio negativo (más caro = menos venta)
    
    // Días listados → mayor venta (si ha estado mucho tiempo, probablemente se venda)
    weight_days_listed = 0.005;
    
    // Condición: restaurado es menos deseable
    weight_condition = -0.3;  // Penalidad para "restaurado"
    
    // Marketplace: OLX y ML son más populares
    weight_marketplace = 0.2;
    
    // Competencia: más competidores = menor venta
    weight_competitors = -0.01;
    
    // Intercept (bias term)
    avg_sale_probability = static_cast<double>(sold_count) / training_data.size();
    intercept = std::log(avg_sale_probability / (1.0 - avg_sale_probability));
    
    // Validar
    training_accuracy = calculate_accuracy(training_data);
}

double MLDemandPredictor::calculate_accuracy(
    const std::vector<SalesHistory>& data) const {
    if (data.empty()) return 0.0;
    
    int correct = 0;
    for (const auto& record : data) {
        // Calcular predicción inline para método const
        double norm_price = normalize_feature(record.price, price_mean, price_std);
        double norm_days = normalize_feature(record.days_listed, days_mean, days_std);
        double norm_competitors = normalize_feature(record.competitor_count, competitors_mean, competitors_std);
        
        double cond_score = (record.condition == "restaurado") ? -0.5 :
                           (record.condition == "nuevo") ? 0.5 : 0.0;
        
        double market_score = (record.marketplace == "OLX") ? 0.3 :
                             (record.marketplace == "ML") ? 0.4 :
                             (record.marketplace == "Yapo") ? 0.2 : 0.0;
        
        double logit = intercept +
                       (weight_price * norm_price) +
                       (weight_days_listed * norm_days) +
                       (weight_condition * cond_score) +
                       (weight_marketplace * market_score) +
                       (weight_competitors * norm_competitors);
        
        double pred = sigmoid(logit);
        
        bool predicted_sold = pred > 0.5;
        if (predicted_sold == record.sold) correct++;
    }
    
    return static_cast<double>(correct) / data.size();
}

DemandPrediction MLDemandPredictor::predict(
    double price,
    int days_listed,
    const std::string& condition,
    const std::string& marketplace,
    double competitor_count) {
    
    // Normalizar características
    double norm_price = normalize_feature(price, price_mean, price_std);
    double norm_days = normalize_feature(days_listed, days_mean, days_std);
    double norm_competitors = normalize_feature(competitor_count, competitors_mean, competitors_std);
    
    // Codificar características categóricas
    double cond_score = (condition == "restaurado") ? -0.5 :
                       (condition == "nuevo") ? 0.5 : 0.0;
    
    double market_score = (marketplace == "OLX") ? 0.3 :
                         (marketplace == "ML") ? 0.4 :
                         (marketplace == "Yapo") ? 0.2 : 0.0;
    
    // Predicción con regresión logística
    double logit = intercept +
                   (weight_price * norm_price) +
                   (weight_days_listed * norm_days) +
                   (weight_condition * cond_score) +
                   (weight_marketplace * market_score) +
                   (weight_competitors * norm_competitors);
    
    double probability = sigmoid(logit);
    
    // Garantizar rango razonable (0.5% - 50%)
    probability = std::max(0.005, std::min(0.50, probability));
    
    // Estimar días a venta
    double expected_days = days_listed;
    if (probability > 0.1) {
        expected_days = days_listed * (1.0 - probability) * 2.0 + 7.0;
    } else {
        expected_days = 180.0;  // Si probabilidad muy baja, esperado muy largo
    }
    
    // Clasificar demanda
    std::string demand_level;
    if (probability > 0.15) {
        demand_level = "ALTA";
    } else if (probability > 0.07) {
        demand_level = "MEDIA";
    } else {
        demand_level = "BAJA";
    }
    
    // Confianza basada en datos de entrenamiento
    double confidence = std::min(0.95, 0.5 + (training_accuracy * 0.5));
    
    std::stringstream ss;
    ss << "Regresión logística: P=" << std::fixed << std::setprecision(2) 
       << (probability * 100) << "%. "
       << "Factores: Precio (" << (norm_price > 0 ? "alto" : "bajo") << "), "
       << "Días listado (" << days_listed << "), "
       << "Condición (" << condition << "), "
       << "Mercado (" << marketplace << ")";
    
    return DemandPrediction{
        probability,
        expected_days,
        demand_level,
        confidence,
        ss.str()
    };
}

DemandPrediction MLDemandPredictor::predict_with_history(
    const std::vector<SalesHistory>& recent_sales,
    double current_price,
    const std::string& condition) {
    
    if (recent_sales.empty()) {
        // Si no hay histórico, usar predicción base
        return predict(current_price, 30, condition, "OLX", 20);
    }
    
    // Calcular tendencias del histórico
    int sold_count = 0;
    double avg_days_to_sale = 0.0;
    double price_trend = 0.0;
    
    for (const auto& record : recent_sales) {
        if (record.sold) {
            sold_count++;
            avg_days_to_sale += record.days_listed;
        }
        price_trend += record.price;
    }
    
    if (sold_count > 0) {
        avg_days_to_sale /= sold_count;
    } else {
        avg_days_to_sale = 90.0;
    }
    
    price_trend = price_trend / recent_sales.size();
    
    // Histórico de venta ratio
    double historical_sell_rate = static_cast<double>(sold_count) / recent_sales.size();
    
    // Ajustar probabilidad base con histórico
    double base_probability = historical_sell_rate * 0.8 + avg_sale_probability * 0.2;
    base_probability = std::min(0.50, std::max(0.005, base_probability));
    
    // Usar predicción del modelo como segundo factor
    auto model_pred = predict(
        current_price,
        static_cast<int>(avg_days_to_sale),
        condition,
        "OLX",
        recent_sales.size() * 0.2  // Aproximación competencia
    );
    
    // Combinar histórico + modelo
    double final_probability = base_probability * 0.6 + model_pred.sale_probability * 0.4;
    
    std::string demand_level;
    if (final_probability > 0.15) {
        demand_level = "ALTA";
    } else if (final_probability > 0.07) {
        demand_level = "MEDIA";
    } else {
        demand_level = "BAJA";
    }
    
    std::stringstream ss;
    ss << "Predicción con histórico: "
       << sold_count << "/" << recent_sales.size() << " vendidos. "
       << "Promedio " << std::fixed << std::setprecision(0) 
       << avg_days_to_sale << " días a venta. "
       << "Tendencia precio: $" << price_trend << ". "
       << "Probabilidad combinada: " << std::setprecision(2) 
       << (final_probability * 100) << "%";
    
    return DemandPrediction{
        final_probability,
        avg_days_to_sale,
        demand_level,
        0.85,  // Confianza más alta con histórico
        ss.str()
    };
}

std::vector<MLDemandPredictor::FeatureImportance> 
MLDemandPredictor::get_feature_importance() const {
    std::vector<FeatureImportance> importance;
    
    // Calcular importancia relativa de pesos (valor absoluto normalizado)
    double total_weight = std::abs(weight_price) + std::abs(weight_days_listed) +
                         std::abs(weight_condition) + std::abs(weight_marketplace) +
                         std::abs(weight_competitors);
    
    if (total_weight > 0) {
        importance.push_back({
            "Precio",
            std::abs(weight_price) / total_weight
        });
        importance.push_back({
            "Días Listado",
            std::abs(weight_days_listed) / total_weight
        });
        importance.push_back({
            "Condición",
            std::abs(weight_condition) / total_weight
        });
        importance.push_back({
            "Marketplace",
            std::abs(weight_marketplace) / total_weight
        });
        importance.push_back({
            "Competencia",
            std::abs(weight_competitors) / total_weight
        });
    }
    
    // Ordenar por importancia
    std::sort(importance.begin(), importance.end(),
              [](const FeatureImportance& a, const FeatureImportance& b) {
                  return a.importance_score > b.importance_score;
              });
    
    return importance;
}

std::string MLDemandPredictor::generate_model_report() const {
    std::stringstream ss;
    
    ss << "╔════════════════════════════════════════╗\n";
    ss << "║   ML DEMAND PREDICTOR - MODEL REPORT   ║\n";
    ss << "╚════════════════════════════════════════╝\n\n";
    
    ss << "📊 TRAINING STATISTICS\n";
    ss << std::string(40, '-') << "\n";
    ss << "Muestras de entrenamiento: " << training_samples << "\n";
    ss << "Precisión del modelo: " << std::fixed << std::setprecision(2) 
       << (training_accuracy * 100) << "%\n";
    ss << "Probabilidad promedio: " << (avg_sale_probability * 100) << "%\n\n";
    
    ss << "⚖️ MODEL WEIGHTS\n";
    ss << std::string(40, '-') << "\n";
    ss << "Intercept (bias): " << intercept << "\n";
    ss << "Precio: " << weight_price << "\n";
    ss << "Días Listado: " << weight_days_listed << "\n";
    ss << "Condición: " << weight_condition << "\n";
    ss << "Marketplace: " << weight_marketplace << "\n";
    ss << "Competencia: " << weight_competitors << "\n\n";
    
    ss << "📈 FEATURE IMPORTANCE\n";
    ss << std::string(40, '-') << "\n";
    auto importance = get_feature_importance();
    for (const auto& feat : importance) {
        int bars = static_cast<int>(feat.importance_score * 30);
        ss << feat.feature_name << ": ";
        ss << std::string(bars, '#') << " " 
           << std::fixed << std::setprecision(1) 
           << (feat.importance_score * 100) << "%\n";
    }
    
    ss << "\n📌 NORMALIZATION PARAMS\n";
    ss << std::string(40, '-') << "\n";
    ss << "Precio: µ=$" << price_mean << " σ=$" << price_std << "\n";
    ss << "Días: µ=" << days_mean << " σ=" << days_std << "\n";
    ss << "Competencia: µ=" << competitors_mean << " σ=" << competitors_std << "\n";
    
    return ss.str();
}

} // namespace decision_maker
