#ifndef REAL_TIME_MONITOR_H
#define REAL_TIME_MONITOR_H

#include <vector>
#include <map>
#include <string>
#include <chrono>
#include <memory>

namespace decision_maker {

struct MarketDataPoint {
    std::chrono::system_clock::time_point timestamp;
    std::string product_name;
    double price;
    std::string condition;  // nuevo, como_nuevo, restaurado, gastado
    int days_listed;
    std::string marketplace;  // OLX, ML, Yapo
    bool sold;  // if we can detect it sold
};

struct MarketTrend {
    double avg_price;
    double median_price;
    double price_trend;  // positive = increasing, negative = decreasing
    int total_listings;
    int sold_listings;
    double sale_velocity;  // listings sold per week
    std::string demand_level;  // ALTA, MEDIA, BAJA
    double saturation_level;  // 0-1, higher = more saturated
    std::chrono::system_clock::time_point last_updated;
};

class RealTimeMarketMonitor {
public:
    RealTimeMarketMonitor(const std::string& product_type);
    
    // Add new market data point
    void add_market_data(const MarketDataPoint& data);
    
    // Analyze current market trends
    MarketTrend analyze_market();
    
    // Get price history for trend analysis
    std::vector<double> get_price_history(
        const std::string& condition = "restaurado"
    );
    
    // Get days to sale estimate
    double estimate_days_to_sale();
    
    // Update probability based on real-time data
    double update_probability_with_market_data(
        double prior_probability
    );
    
    // Get market saturation metric
    double calculate_saturation();
    
    // Get demand assessment
    std::string assess_demand();
    
    // Generate market report
    std::string generate_report();
    
private:
    std::string product_type_;
    std::vector<MarketDataPoint> market_data_;
    std::map<std::string, std::vector<double>> price_by_condition_;
    std::map<std::string, int> marketplace_counts_;
    
    // Calculate moving average of prices
    double calculate_moving_average(const std::vector<double>& prices,
                                   int window_size = 7);
    
    // Calculate price trend (regression slope)
    double calculate_price_trend();
    
    // Estimate sale velocity from data
    double estimate_sale_velocity();
};

}  // namespace decision_maker

#endif  // REAL_TIME_MONITOR_H
