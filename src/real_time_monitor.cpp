#include "real_time_monitor.h"
#include <algorithm>
#include <numeric>
#include <cmath>
#include <sstream>
#include <iomanip>

namespace decision_maker {

RealTimeMarketMonitor::RealTimeMarketMonitor(
    const std::string& product_type
) : product_type_(product_type) {}

void RealTimeMarketMonitor::add_market_data(
    const MarketDataPoint& data
) {
    market_data_.push_back(data);
    
    // Track prices by condition
    price_by_condition_[data.condition].push_back(data.price);
    
    // Track marketplace distribution
    marketplace_counts_[data.marketplace]++;
}

MarketTrend RealTimeMarketMonitor::analyze_market() {
    MarketTrend trend;
    
    if (market_data_.empty()) {
        return trend;  // Return default/empty trend
    }
    
    // Calculate statistics for restored items
    auto& restored_prices = price_by_condition_["restaurado"];
    if (!restored_prices.empty()) {
        std::sort(restored_prices.begin(), restored_prices.end());
        
        trend.avg_price = std::accumulate(
            restored_prices.begin(),
            restored_prices.end(),
            0.0
        ) / restored_prices.size();
        
        int mid = restored_prices.size() / 2;
        trend.median_price = restored_prices[mid];
    }
    
    trend.total_listings = market_data_.size();
    trend.sold_listings = std::count_if(
        market_data_.begin(),
        market_data_.end(),
        [](const MarketDataPoint& p) { return p.sold; }
    );
    
    trend.price_trend = calculate_price_trend();
    trend.sale_velocity = estimate_sale_velocity();
    trend.demand_level = assess_demand();
    trend.saturation_level = calculate_saturation();
    trend.last_updated = std::chrono::system_clock::now();
    
    return trend;
}

std::vector<double> RealTimeMarketMonitor::get_price_history(
    const std::string& condition
) {
    auto it = price_by_condition_.find(condition);
    if (it != price_by_condition_.end()) {
        return it->second;
    }
    return std::vector<double>();
}

double RealTimeMarketMonitor::estimate_days_to_sale() {
    // Based on demand level and saturation
    std::string demand = assess_demand();
    double saturation = calculate_saturation();
    
    if (demand == "ALTA") {
        return 7.0 + (saturation * 14.0);  // 7-21 days
    } else if (demand == "MEDIA") {
        return 30.0 + (saturation * 60.0);  // 30-90 days
    } else {
        return 180.0 + (saturation * 90.0);  // 180-270 days
    }
}

double RealTimeMarketMonitor::update_probability_with_market_data(
    double prior_probability
) {
    // Bayesian update: P(sale|market) = P(market|sale) * P(sale) / P(market)
    
    std::string demand = assess_demand();
    double saturation = calculate_saturation();
    
    // Likelihood: P(market|sale happens)
    double p_market_given_sale;
    if (demand == "ALTA") {
        p_market_given_sale = 0.8;  // High demand helps sales
    } else if (demand == "MEDIA") {
        p_market_given_sale = 0.5;
    } else {
        p_market_given_sale = 0.2;  // Low demand hurts sales
    }
    
    // Adjust for saturation
    p_market_given_sale *= (1.0 - saturation * 0.5);
    
    // Evidence: P(market) - marginal probability
    double p_market;
    if (demand == "ALTA") {
        p_market = 0.4;
    } else if (demand == "MEDIA") {
        p_market = 0.4;
    } else {
        p_market = 0.2;
    }
    
    // Bayesian posterior
    double posterior = (p_market_given_sale * prior_probability) / p_market;
    
    // Cap between 0 and 1
    return std::min(1.0, std::max(0.0, posterior));
}

double RealTimeMarketMonitor::calculate_saturation() {
    int listings = market_data_.size();
    
    if (listings > 500) {
        return 1.0;  // Completely saturated
    } else if (listings > 200) {
        return 0.7;  // Highly saturated
    } else if (listings > 50) {
        return 0.5;  // Moderately saturated
    } else {
        return 0.2;  // Low saturation
    }
}

std::string RealTimeMarketMonitor::assess_demand() {
    double saturation = calculate_saturation();
    
    if (saturation > 0.7) {
        return "BAJA";  // High saturation = low relative demand
    } else if (saturation > 0.3) {
        return "MEDIA";
    } else {
        return "ALTA";  // Low saturation = high relative demand
    }
}

std::string RealTimeMarketMonitor::generate_report() {
    MarketTrend trend = analyze_market();
    
    std::ostringstream report;
    report << std::fixed << std::setprecision(2);
    
    report << "=== MARKET MONITORING REPORT ===\n";
    report << "Product: " << product_type_ << "\n";
    report << "Last Updated: " 
           << std::chrono::system_clock::now().time_since_epoch().count() 
           << "\n\n";
    
    report << "PRICE ANALYSIS\n";
    report << "  Average Price: $" << trend.avg_price << "\n";
    report << "  Median Price: $" << trend.median_price << "\n";
    report << "  Price Trend: " << trend.price_trend << "%\n\n";
    
    report << "MARKET STATUS\n";
    report << "  Total Listings: " << trend.total_listings << "\n";
    report << "  Sold Listings: " << trend.sold_listings << "\n";
    report << "  Sale Velocity: " << trend.sale_velocity 
           << " items/week\n";
    report << "  Saturation: " << (trend.saturation_level * 100) << "%\n";
    report << "  Demand Level: " << trend.demand_level << "\n\n";
    
    report << "SALE ESTIMATE\n";
    report << "  Est. Days to Sale: " << estimate_days_to_sale() << "\n";
    
    return report.str();
}

double RealTimeMarketMonitor::calculate_moving_average(
    const std::vector<double>& prices,
    int window_size
) {
    if (prices.empty() || window_size <= 0) {
        return 0.0;
    }
    
    int actual_window = std::min(window_size, (int)prices.size());
    double sum = 0.0;
    for (int i = 0; i < actual_window; i++) {
        sum += prices[prices.size() - 1 - i];
    }
    
    return sum / actual_window;
}

double RealTimeMarketMonitor::calculate_price_trend() {
    // Linear regression of prices over time
    auto& prices = price_by_condition_["restaurado"];
    
    if (prices.size() < 2) {
        return 0.0;  // No trend with < 2 points
    }
    
    int n = prices.size();
    double sum_x = 0, sum_y = 0, sum_xy = 0, sum_x2 = 0;
    
    for (int i = 0; i < n; i++) {
        sum_x += i;
        sum_y += prices[i];
        sum_xy += i * prices[i];
        sum_x2 += i * i;
    }
    
    double numerator = n * sum_xy - sum_x * sum_y;
    double denominator = n * sum_x2 - sum_x * sum_x;
    
    if (denominator == 0) {
        return 0.0;
    }
    
    double slope = numerator / denominator;
    
    // Return percentage change per data point
    double avg_price = sum_y / n;
    if (avg_price == 0) {
        return 0.0;
    }
    
    return (slope / avg_price) * 100.0;
}

double RealTimeMarketMonitor::estimate_sale_velocity() {
    if (market_data_.empty()) {
        return 0.0;
    }
    
    int sold = std::count_if(
        market_data_.begin(),
        market_data_.end(),
        [](const MarketDataPoint& p) { return p.sold; }
    );
    
    // Calculate average days listed
    double total_days = 0;
    int listed_count = 0;
    
    for (const auto& data : market_data_) {
        total_days += data.days_listed;
        listed_count++;
    }
    
    if (listed_count == 0) {
        return 0.0;
    }
    
    double avg_days = total_days / listed_count;
    
    // Items per week = 7 / avg_days_to_sell
    if (avg_days == 0) {
        return 0.0;
    }
    
    return 7.0 / avg_days;
}

}  // namespace decision_maker
