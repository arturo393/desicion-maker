#include "../src/unified_decision_framework.h"
#include "../src/advanced_decision_tools.h"
#include <iomanip>

using namespace DecisionFramework;

/*
 Evaluación de negocio: DeFi Monitor
 Opciones comparadas:
 1) Construir DeFi Monitor (SaaS $15/mes)
 2) Open Source + Sponsorships + Consultoría
 3) Newsletter Premium DeFi (pivot)
 4) Enfocarse en Freelance (no producto ahora)

 Factores (ponderaciones):
 - Ganancia 12m (35%)         -> beneficio
 - Tiempo semanal (15%)       -> costo
 - Riesgo (15%)               -> costo
 - Crecimiento usuarios (15%) -> beneficio
 - Diferenciación (10%)       -> beneficio
 - Satisfacción personal (10%)-> beneficio

 Notas:
 - Números iniciales basados en docs/MONETIZATION.md y ROADMAP.md del repo defi-monitor.
 - Ajustaremos con preguntas al final para refinar.
*/

int main() {
    std::cout << "💼 === Evaluación de Negocio: DeFi Monitor ===\n\n";

    MonteCarloEngine mc;
    mc.setNumSimulations(20000);

    std::vector<Factor> factores = {
        Factor("Ganancia 12m", "Economía", 0.35, true),
        Factor("Tiempo semanal", "Esfuerzo", 0.15, false),
        Factor("Riesgo", "Riesgo", 0.15, false),
        Factor("Crecimiento usuarios", "Mercado", 0.15, true),
        Factor("Diferenciación", "Estrategia", 0.10, true),
        Factor("Satisfacción", "Personal", 0.10, true)
    };
    for (const auto& f : factores) mc.addFactor(f);

    // =============================
    // 1) DeFi Monitor (SaaS)
    // =============================
    DecisionOption saas("DeFi Monitor (SaaS)", "Producto $15/mes");

    // Supuestos base (triangulares según docs)
    saas.addVariable("subs_final_12m", UncertainVariable("subs_final_12m", DistributionType::TRIANGULAR, 20, 60, 120));
    saas.addVariable("costo_mensual", UncertainVariable("costo_mensual", DistributionType::TRIANGULAR, 35, 45, 65)); // hosting+email+sms
    saas.addVariable("horas_semana", UncertainVariable("horas_semana", DistributionType::TRIANGULAR, 8, 12, 18));
    saas.addVariable("riesgo_base", UncertainVariable("riesgo_base", DistributionType::TRIANGULAR, 0.25, 0.35, 0.55)); // competencia, regula, dependencia API
    saas.addVariable("diferenciacion", UncertainVariable("dif", DistributionType::TRIANGULAR, 0.45, 0.6, 0.8));
    saas.addVariable("satisfaccion", UncertainVariable("sat", DistributionType::TRIANGULAR, 0.6, 0.8, 0.95));

    saas.setSimulator([](const std::map<std::string,double>& v, std::mt19937& gen){
        SimulationResult r; r.factor_values = {};
        double S = v.at("subs_final_12m");
        double cost_m = v.at("costo_mensual");
        double h_week = v.at("horas_semana");
        double risk0 = v.at("riesgo_base");
        double dif = v.at("diferenciacion");
        double sat = v.at("satisfaccion");

        // Eventos de riesgo: competencia fuerte o API cambia → reduce subs finales 30%
        std::bernoulli_distribution comp_event(0.30);
        bool comp = comp_event(gen);
        if (comp) S *= 0.7; // impacto competitivo

        // Ingresos 12m ~ crecimiento lineal 0→S, precio 15
        double revenue = (S/2.0) * 12.0 * 15.0;
        double cost = cost_m * 12.0;
        double profit = revenue - cost;

        // Riesgo efectivo aumenta si hay evento competitivo
        double risk = std::min(1.0, risk0 + (comp ? 0.1 : 0.0));

        // Factores
        r.factor_values["Ganancia 12m"] = profit;
        r.factor_values["Tiempo semanal"] = h_week;
        r.factor_values["Riesgo"] = risk;
        r.factor_values["Crecimiento usuarios"] = S; // proxy de tracción
        r.factor_values["Diferenciación"] = dif;
        r.factor_values["Satisfacción"] = sat;
        r.success = true; return r;
    });
    mc.addOption(saas);

    // ==============================================
    // 2) Open Source + Sponsorships + Consultoría
    // ==============================================
    DecisionOption oss("Open Source + Sponsors", "Sponsorships + consultoría ocasional");
    oss.addVariable("sponsorship_mensual", UncertainVariable("spon_m", DistributionType::TRIANGULAR, 50, 150, 400));
    oss.addVariable("prob_consulting_mes", UncertainVariable("p_c", DistributionType::TRIANGULAR, 0.10, 0.20, 0.40));
    oss.addVariable("ticket_consulting", UncertainVariable("t_c", DistributionType::TRIANGULAR, 500, 1000, 2000));
    oss.addVariable("horas_semana", UncertainVariable("h", DistributionType::TRIANGULAR, 4, 6, 10));
    oss.addVariable("riesgo_base", UncertainVariable("rb", DistributionType::TRIANGULAR, 0.10, 0.20, 0.35));
    oss.addVariable("diferenciacion", UncertainVariable("dif", DistributionType::TRIANGULAR, 0.55, 0.7, 0.9));
    oss.addVariable("satisfaccion", UncertainVariable("sat", DistributionType::TRIANGULAR, 0.7, 0.85, 0.98));

    oss.setSimulator([](const std::map<std::string,double>& v, std::mt19937& gen){
        SimulationResult r; r.factor_values = {};
        double spon_m = v.at("sponsorship_mensual");
        double p_cons = v.at("prob_consulting_mes");
        double ticket = v.at("ticket_consulting");
        double h_week = v.at("horas_semana");
        double risk0 = v.at("riesgo_base");
        double dif = v.at("diferenciacion");
        double sat = v.at("satisfaccion");

        // Simulación 12 meses
        std::bernoulli_distribution consult(p_cons);
        double revenue = 0.0;
        for (int m=0; m<12; ++m) {
            revenue += spon_m;
            if (consult(gen)) revenue += ticket;
        }
        double profit = revenue; // costos casi nulos
        double risk = risk0;
        double S = spon_m/10.0 + p_cons*100.0; // proxy de tracción/comunidad

        r.factor_values["Ganancia 12m"] = profit;
        r.factor_values["Tiempo semanal"] = h_week;
        r.factor_values["Riesgo"] = risk;
        r.factor_values["Crecimiento usuarios"] = S;
        r.factor_values["Diferenciación"] = dif;
        r.factor_values["Satisfacción"] = sat;
        r.success = true; return r;
    });
    mc.addOption(oss);

    // ================================
    // 3) Newsletter Premium DeFi
    // ================================
    DecisionOption news("Newsletter Premium", "Pivot a newsletter $10/mes");
    news.addVariable("subs_final_12m", UncertainVariable("S", DistributionType::TRIANGULAR, 50, 150, 400));
    news.addVariable("horas_semana", UncertainVariable("H", DistributionType::TRIANGULAR, 8, 10, 14));
    news.addVariable("riesgo_base", UncertainVariable("R", DistributionType::TRIANGULAR, 0.20, 0.30, 0.50));
    news.addVariable("diferenciacion", UncertainVariable("D", DistributionType::TRIANGULAR, 0.40, 0.55, 0.75));
    news.addVariable("satisfaccion", UncertainVariable("Sa", DistributionType::TRIANGULAR, 0.55, 0.75, 0.9));

    news.setSimulator([](const std::map<std::string,double>& v, std::mt19937& gen){
        SimulationResult r; r.factor_values = {};
        double S = v.at("subs_final_12m");
        double h = v.at("horas_semana");
        double risk0 = v.at("riesgo_base");
        double dif = v.at("diferenciacion");
        double sat = v.at("satisfaccion");

        // Newsletter $10: revenue anual ~ (S/2)*12*10 (crecimiento lineal)
        double revenue = (S/2.0)*12.0*10.0;
        // Costos mínimos ($10/mes tools)
        double cost = 10.0*12.0;
        double profit = revenue - cost;

        // Eventos: churn alto en newsletters reduce S 20% con 30% prob
        std::bernoulli_distribution churn(0.30);
        if (churn(gen)) { profit *= 0.8; risk0 += 0.05; }

        r.factor_values["Ganancia 12m"] = profit;
        r.factor_values["Tiempo semanal"] = h;
        r.factor_values["Riesgo"] = std::min(1.0, risk0);
        r.factor_values["Crecimiento usuarios"] = S;
        r.factor_values["Diferenciación"] = dif;
        r.factor_values["Satisfacción"] = sat;
        r.success = true; return r;
    });
    mc.addOption(news);

    // ==================================
    // 4) Enfocarse en Freelance ahora
    // ==================================
    DecisionOption free("Focus Freelance", "Pausar producto 12m");
    free.addVariable("horas_libres_semana", UncertainVariable("Hf", DistributionType::TRIANGULAR, 8, 10, 15));
    free.addVariable("tarifa", UncertainVariable("T", DistributionType::TRIANGULAR, 22, 25, 35));
    free.addVariable("riesgo_base", UncertainVariable("R", DistributionType::TRIANGULAR, 0.05, 0.10, 0.20));
    free.addVariable("diferenciacion", UncertainVariable("D", DistributionType::TRIANGULAR, 0.30, 0.45, 0.60));
    free.addVariable("satisfaccion", UncertainVariable("S", DistributionType::TRIANGULAR, 0.45, 0.65, 0.85));

    free.setSimulator([](const std::map<std::string,double>& v, std::mt19937& gen){
        SimulationResult r; r.factor_values = {};
        double hf = v.at("horas_libres_semana");
        double rate = v.at("tarifa");
        double risk0 = v.at("riesgo_base");
        double dif = v.at("diferenciacion");
        double sat = v.at("satisfaccion");

        double revenue = hf * rate * 52.0; // ingresos freelance añadidos
        double profit = revenue; // sin costos

        r.factor_values["Ganancia 12m"] = profit;
        r.factor_values["Tiempo semanal"] = 0.5; // overhead mínimo en producto
        r.factor_values["Riesgo"] = risk0;
        r.factor_values["Crecimiento usuarios"] = 0.0; // no crea base usuarios
        r.factor_values["Diferenciación"] = dif;
        r.factor_values["Satisfacción"] = sat;
        r.success = true; return r;
    });
    mc.addOption(free);

    // ========================
    // Ejecutar Monte Carlo
    // ========================
    std::cout << "📊 Monte Carlo (20,000 simulaciones)\n\n";
    auto results = mc.run();

    std::vector<std::pair<std::string,double>> ranking;
    for (const auto& [name, stats] : results) {
        ranking.push_back({name, stats.mean_score});
        std::cout << " • " << name
                  << " | Score: " << std::fixed << std::setprecision(2) << stats.mean_score
                  << " | Ganancia12m: $" << std::setprecision(0) << stats.mean.at("Ganancia 12m")
                  << " | Tiempo semanal: " << std::setprecision(1) << stats.mean.at("Tiempo semanal")
                  << " | Riesgo: " << std::setprecision(2) << stats.mean.at("Riesgo")
                  << "\n";
    }

    std::sort(ranking.begin(), ranking.end(), [](auto&a, auto&b){return a.second>b.second;});

    std::cout << "\n🏆 Ranking (Score ponderado):\n";
    for (size_t i=0;i<ranking.size();++i) {
        std::cout << i+1 << ". " << ranking[i].first << "\n";
    }

    // Sensibilidad de la mejor opción
    std::string best = ranking[0].first;
    std::cout << "\n🔬 Sensibilidad (" << best << ")\n";
    auto sens = mc.sensitivityAnalysis(best);
    std::vector<std::pair<std::string,double>> sensv;
    for (auto &kv : sens) sensv.push_back(kv);
    std::sort(sensv.begin(), sensv.end(), [](auto&a,auto&b){return a.second>b.second;});
    for (auto &kv : sensv) {
        std::cout << "  - " << kv.first << ": " << std::fixed << std::setprecision(2) << kv.second << "\n";
    }

    // Riesgo (VaR/CVaR) sobre Ganancias de cada opción (aprox con normal a partir de media/desvio si disponible)
    RiskAnalyzer risk;
    std::cout << "\n⚠️  Nota: Ajustaremos parámetros con tus datos para mayor precisión.\n";

    // Preguntas para refinar (imprime checklist)
    std::cout << "\n📋 Info faltante sugerida para refinar modelo:\n";
    std::cout << " - Tu tiempo disponible semanal dedicado al producto (hrs/semana)\n";
    std::cout << " - Audiencia actual: seguidores, newsletter, lista de email (tamaño)\n";
    std::cout << " - Canal principal de adquisición (Twitter, Reddit, SEO, Ads)\n";
    std::cout << " - Conversión esperada de visitantes a suscriptores (%)\n";
    std::cout << " - Churn mensual esperado (%)\n";
    std::cout << " - Presupuesto de marketing mensual ($)\n";
    std::cout << " - Diferenciadores clave vs DeFi Llama u otros competidores\n";
    std::cout << " - Preferencia personal (0-1) por cada opción\n";

    return 0;
}
