#include "../src/scenarios/BusinessDecision.h"
#include <iostream>
#include <iomanip>
#include <algorithm>
#include <numeric>

using namespace DecisionMaker::Business;

/**
 * @brief Simulación mejorada con 10+ factores adicionales
 * 
 * Arquitectura genérica que permite:
 * - Agregar nuevos factores sin modificar código core
 * - Reutilizar para cualquier tipo de decisión
 * - Diferentes estrategias de evaluación
 * - Escalable a miles de simulaciones
 */

// ============================================================================
// FACTORES ESPECÍFICOS PARA NEGOCIO AUTOMATIZADO
// ============================================================================

/**
 * @brief Factor de competencia de mercado
 */
class MarketCompetitionFactor : public NumericFactor {
private:
    double market_saturation_;      // 0-1 (0=virgen, 1=saturado)
    double competitive_advantage_;  // 0-1 (qué tan único)
    double barrier_to_entry_;       // 0-1 (qué tan difícil copiar)
    
public:
    MarketCompetitionFactor(double saturation, double advantage, double barrier, double weight)
        : NumericFactor("Market Competition", "Market", 0.0, weight),
          market_saturation_(saturation),
          competitive_advantage_(advantage),
          barrier_to_entry_(barrier)
    {
        // Score inverso: menos saturación y más barreras = mejor
        value_ = (1.0 - market_saturation_) * 0.4 + 
                 competitive_advantage_ * 0.3 + 
                 barrier_to_entry_ * 0.3;
    }
};

/**
 * @brief Factor de habilidades técnicas
 */
class TechnicalSkillsFactor : public NumericFactor {
private:
    double required_level_;  // 1-10
    double current_level_;   // 1-10
    double learning_curve_;  // Meses para dominar
    
public:
    TechnicalSkillsFactor(double required, double current, double learning, double weight)
        : NumericFactor("Technical Skills", "Personal", 0.0, weight),
          required_level_(required),
          current_level_(current),
          learning_curve_(learning)
    {
        // Gap de habilidades afecta el score
        double skill_gap = std::max(0.0, required_level_ - current_level_);
        double penalty = skill_gap * learning_curve_ * 0.1;  // 10% penalty por mes
        value_ = std::max(0.0, 1.0 - penalty);
    }
    
    double getSkillGap() const { return std::max(0.0, required_level_ - current_level_); }
};

/**
 * @brief Factor de dependencias externas (APIs, plataformas)
 */
class ExternalDependenciesFactor : public StochasticFactor {
private:
    double api_dependency_;          // 0-1 (qué tan dependiente)
    double price_change_risk_;       // Probabilidad que API cobre más
    double shutdown_risk_;           // Probabilidad que API cierre
    
public:
    ExternalDependenciesFactor(double dependency, double price_risk, 
                               double shutdown_risk, double weight, std::mt19937* rng)
        : StochasticFactor("External Dependencies", "Risk", 
                          1.0 - (dependency * (price_risk + shutdown_risk) * 0.5),
                          0.15, weight, rng),
          api_dependency_(dependency),
          price_change_risk_(price_risk),
          shutdown_risk_(shutdown_risk)
    {
        // Score baja con alta dependencia y riesgo
    }
};

/**
 * @brief Factor de marketing y adquisición
 */
class MarketingAcquisitionFactor : public NumericFactor {
private:
    double cac_;        // Customer Acquisition Cost
    double ltv_;        // Lifetime Value
    double virality_;   // 0-1 (potential boca a boca)
    
public:
    MarketingAcquisitionFactor(double cac, double ltv, double virality, double weight)
        : NumericFactor("Marketing & Acquisition", "Growth", 0.0, weight),
          cac_(cac), ltv_(ltv), virality_(virality)
    {
        // LTV/CAC ratio óptimo es 3:1
        double ltv_cac_ratio = cac_ > 0 ? ltv_ / cac_ : 10.0;
        double ratio_score = std::min(1.0, ltv_cac_ratio / 3.0);
        
        value_ = ratio_score * 0.7 + virality_ * 0.3;
    }
    
    double getLTVCACRatio() const { return cac_ > 0 ? ltv_ / cac_ : 999.0; }
};

/**
 * @brief Factor de burnout y salud mental
 */
class BurnoutRiskFactor : public StochasticFactor {
private:
    double operational_stress_;      // 1-10
    double automation_level_;        // 0-1 (más automatización = menos burnout)
    double burnout_probability_;     // Probabilidad a 6 meses
    
public:
    BurnoutRiskFactor(double stress, double automation, double burnout_prob, 
                      double weight, std::mt19937* rng)
        : StochasticFactor("Burnout Risk", "Personal", 
                          (1.0 - burnout_prob) * automation * (1.0 - stress/10.0),
                          0.12, weight, rng),
          operational_stress_(stress),
          automation_level_(automation),
          burnout_probability_(burnout_prob)
    {}
};

/**
 * @brief Factor de timing de mercado
 */
class MarketTimingFactor : public NumericFactor {
private:
    double market_trend_;            // -1 a 1 (bajando/creciendo)
    double opportunity_window_;      // Meses antes de saturación
    double current_hype_;            // 0-1 (qué tan "hot")
    
public:
    MarketTimingFactor(double trend, double window, double hype, double weight)
        : NumericFactor("Market Timing", "Market", 0.0, weight),
          market_trend_(trend),
          opportunity_window_(window),
          current_hype_(hype)
    {
        // Normaliza trend de -1,1 a 0,1
        double trend_norm = (market_trend_ + 1.0) / 2.0;
        // Penaliza ventanas muy cortas
        double window_norm = std::min(1.0, opportunity_window_ / 12.0);
        
        value_ = trend_norm * 0.5 + window_norm * 0.3 + current_hype_ * 0.2;
    }
};

/**
 * @brief Factor legal y compliance
 */
class LegalRiskFactor : public NumericFactor {
private:
    double legal_risk_;              // 0-1
    double annual_legal_cost_;       // $ en costos legales
    double regulatory_change_risk_;  // Probabilidad cambio regulatorio
    
public:
    LegalRiskFactor(double risk, double cost, double reg_risk, double weight)
        : NumericFactor("Legal Risk", "Risk", 0.0, weight),
          legal_risk_(risk),
          annual_legal_cost_(cost),
          regulatory_change_risk_(reg_risk)
    {
        // Penaliza alto riesgo y costos
        double cost_norm = 1.0 - std::min(1.0, annual_legal_cost_ / 5000.0);
        value_ = (1.0 - legal_risk_) * 0.5 + 
                 cost_norm * 0.3 + 
                 (1.0 - regulatory_change_risk_) * 0.2;
    }
};

/**
 * @brief Factor de red de contactos (network effects)
 */
class NetworkEffectsFactor : public NumericFactor {
private:
    int contacts_in_niche_;          // Número de contactos
    bool has_audience_;              // ¿Tiene audiencia previa?
    double credibility_;             // 0-1
    
public:
    NetworkEffectsFactor(int contacts, bool has_audience, double credibility, double weight)
        : NumericFactor("Network Effects", "Growth", 0.0, weight),
          contacts_in_niche_(contacts),
          has_audience_(has_audience),
          credibility_(credibility)
    {
        double contacts_score = std::min(1.0, contacts_in_niche_ / 50.0);
        double audience_bonus = has_audience_ ? 0.3 : 0.0;
        
        value_ = contacts_score * 0.4 + credibility_ * 0.3 + audience_bonus;
    }
};

/**
 * @brief Factor de escalabilidad técnica
 */
class TechnicalScalabilityFactor : public NumericFactor {
private:
    int max_users_current_arch_;     // Límite técnico
    double cost_per_user_scaling_;   // $ adicional por usuario
    bool needs_rewrite_;             // ¿Requiere reescribir código?
    
public:
    TechnicalScalabilityFactor(int max_users, double cost_per_user, 
                               bool needs_rewrite, double weight)
        : NumericFactor("Technical Scalability", "Technical", 0.0, weight),
          max_users_current_arch_(max_users),
          cost_per_user_scaling_(cost_per_user),
          needs_rewrite_(needs_rewrite)
    {
        // Penaliza arquitecturas que no escalan bien
        double capacity_score = std::min(1.0, max_users_current_arch_ / 1000.0);
        double cost_score = 1.0 - std::min(1.0, cost_per_user_scaling_ / 5.0);
        double rewrite_penalty = needs_rewrite_ ? 0.3 : 0.0;
        
        value_ = capacity_score * 0.4 + cost_score * 0.4 + (1.0 - rewrite_penalty) * 0.2;
    }
};

/**
 * @brief Factor de experiencia previa
 */
class PriorExperienceFactor : public NumericFactor {
private:
    bool has_similar_project_;       // ¿Hizo algo similar?
    double code_reuse_;              // % código reutilizable
    int beta_users_available_;       // Usuarios listos para probar
    
public:
    PriorExperienceFactor(bool has_project, double reuse, int beta_users, double weight)
        : NumericFactor("Prior Experience", "Personal", 0.0, weight),
          has_similar_project_(has_project),
          code_reuse_(reuse),
          beta_users_available_(beta_users)
    {
        double project_bonus = has_similar_project_ ? 0.4 : 0.0;
        double beta_score = std::min(1.0, beta_users_available_ / 10.0) * 0.3;
        
        value_ = project_bonus + code_reuse_ * 0.3 + beta_score;
    }
};

// ============================================================================
// CONFIGURACIÓN DE OPCIONES CON TODOS LOS FACTORES
// ============================================================================

void setupBusinessOptions(MonteCarloSimulator& simulator, std::mt19937& rng) {
    // Categorías con pesos (para evaluador multi-criterio)
    std::map<std::string, double> category_weights = {
        {"Market", 0.20},      // 20% peso en factores de mercado
        {"Financial", 0.25},   // 25% peso en factores financieros
        {"Risk", 0.20},        // 20% peso en riesgos
        {"Personal", 0.15},    // 15% peso en factores personales
        {"Growth", 0.10},      // 10% peso en crecimiento
        {"Technical", 0.10}    // 10% peso en factores técnicos
    };
    
    auto evaluator = std::make_shared<MultiCriteriaEvaluator>(category_weights);
    simulator.setEvaluator(evaluator);
    
    // ========================================================================
    // OPCIÓN 1: BOT DE ARBITRAJE CRIPTO
    // ========================================================================
    {
        DecisionOptionBuilder builder("arbitrage_bot", "Bot Arbitraje Cripto");
        builder.setRNG(&rng)
            .setDescription("Bot automatizado para arbitraje en exchanges de cripto")
            
            // Factores originales (financieros)
            .addNumericFactor("Initial Investment", "Financial", 0.8, 1.0)  // $200
            .addStochasticFactor("Monthly Income", "Financial", 0.65, 0.20, 1.5)  // $300±$150
            .addNumericFactor("Automation Level", "Technical", 0.85, 1.2)  // 85% automatizado
            .addNumericFactor("ROI", "Financial", 0.75, 1.0)  // 389% ROI
            
            // NUEVOS FACTORES
            .addMetadata("initial_capital_usd", 200.0)
            .addMetadata("monthly_income_mean", 300.0);
        
        auto option = builder.build();
        
        // Agregar factores complejos manualmente
        option.factors["market_competition"] = std::make_shared<MarketCompetitionFactor>(
            0.7,    // Alta saturación (muchos bots)
            0.6,    // Ventaja competitiva media (velocidad)
            0.8,    // Alta barrera entrada (capital + skills)
            1.0     // Peso normal
        );
        
        option.factors["technical_skills"] = std::make_shared<TechnicalSkillsFactor>(
            8.0,    // Nivel requerido 8/10 (APIs complejas, latencia)
            6.0,    // Tu nivel actual estimado 6/10
            2.0,    // 2 meses para dominar
            1.2     // Peso alto (crítico)
        );
        
        option.factors["external_dependencies"] = std::make_shared<ExternalDependenciesFactor>(
            0.9,    // Altísima dependencia (exchanges)
            0.3,    // 30% riesgo cambio pricing
            0.15,   // 15% riesgo cierre
            1.3,    // Peso muy alto (crítico)
            &rng
        );
        
        option.factors["marketing_acquisition"] = std::make_shared<MarketingAcquisitionFactor>(
            50.0,   // CAC medio $50 (demostrar resultados)
            300.0,  // LTV bajo $300 (uso personal mayormente)
            0.3,    // Baja viralidad (no se comparte fácilmente)
            0.8     // Peso medio-bajo
        );
        
        option.factors["burnout_risk"] = std::make_shared<BurnoutRiskFactor>(
            7.5,    // Alto estrés (monitoreo 24/7, volatilidad)
            0.85,   // Alta automatización
            0.35,   // 35% probabilidad burnout a 6 meses
            1.2,    // Peso alto
            &rng
        );
        
        option.factors["market_timing"] = std::make_shared<MarketTimingFactor>(
            0.3,    // Tendencia positiva moderada (ciclo cripto)
            18.0,   // 18 meses ventana (hasta próximo bear market)
            0.6,    // Hype medio
            0.9     // Peso medio
        );
        
        option.factors["legal_risk"] = std::make_shared<LegalRiskFactor>(
            0.6,    // Alto riesgo legal (regulación cripto)
            1000.0, // $1000/año en compliance
            0.5,    // 50% riesgo cambio regulatorio
            1.1     // Peso alto
        );
        
        option.factors["network_effects"] = std::make_shared<NetworkEffectsFactor>(
            5,      // Pocos contactos en trading algorítmico
            false,  // Sin audiencia previa
            0.3,    // Baja credibilidad inicial
            0.7     // Peso medio-bajo
        );
        
        option.factors["technical_scalability"] = std::make_shared<TechnicalScalabilityFactor>(
            10000,  // Escala muy bien (más capital = más ganancias)
            0.0,    // No hay costo por "usuario" (es personal)
            false,  // No necesita reescribir
            0.8     // Peso medio
        );
        
        option.factors["prior_experience"] = std::make_shared<PriorExperienceFactor>(
            false,  // No hiciste bots de arbitraje antes
            0.2,    // 20% código reutilizable (API wrappers genéricos)
            0,      // No hay beta users (uso personal)
            0.9     // Peso medio
        );
        
        simulator.addOption(option);
    }
    
    // ========================================================================
    // OPCIÓN 2: ALERTAS DE TRADING
    // ========================================================================
    {
        DecisionOptionBuilder builder("trading_alerts", "Alertas Trading (Suscripción)");
        builder.setRNG(&rng)
            .setDescription("Sistema de alertas automatizadas para traders")
            
            .addNumericFactor("Initial Investment", "Financial", 0.95, 1.0)  // $70 (bajo)
            .addStochasticFactor("Monthly Income", "Financial", 0.40, 0.15, 1.5)  // $150±$80
            .addNumericFactor("Automation Level", "Technical", 0.90, 1.3)  // 90% automatizado
            .addNumericFactor("ROI", "Financial", 0.85, 1.0)  // 542% ROI
            
            .addMetadata("initial_capital_usd", 70.0)
            .addMetadata("monthly_income_mean", 150.0);
        
        auto option = builder.build();
        
        option.factors["market_competition"] = std::make_shared<MarketCompetitionFactor>(
            0.8,    // Alta saturación (TradingView, TrendSpider existen)
            0.5,    // Ventaja competitiva media-baja
            0.4,    // Baja barrera entrada (fácil copiar)
            1.1     // Peso alto
        );
        
        option.factors["technical_skills"] = std::make_shared<TechnicalSkillsFactor>(
            5.0,    // Nivel requerido 5/10 (APIs básicas)
            6.0,    // Tu nivel actual 6/10
            0.5,    // 0.5 meses para dominar
            0.8     // Peso medio
        );
        
        option.factors["external_dependencies"] = std::make_shared<ExternalDependenciesFactor>(
            0.8,    // Alta dependencia (Twilio para SMS)
            0.4,    // 40% riesgo cambio pricing (Twilio puede subir)
            0.05,   // 5% riesgo cierre (Twilio es estable)
            1.2,    // Peso alto
            &rng
        );
        
        option.factors["marketing_acquisition"] = std::make_shared<MarketingAcquisitionFactor>(
            15.0,   // CAC bajo $15 (comunidades gratis)
            120.0,  // LTV alto $120 (suscripción recurrente)
            0.6,    // Viralidad buena (traders comparten)
            1.0     // Peso normal
        );
        
        option.factors["burnout_risk"] = std::make_shared<BurnoutRiskFactor>(
            3.0,    // Bajo estrés (una vez configurado, corre solo)
            0.90,   // Muy alta automatización
            0.15,   // 15% probabilidad burnout
            0.9,    // Peso medio
            &rng
        );
        
        option.factors["market_timing"] = std::make_shared<MarketTimingFactor>(
            0.0,    // Tendencia neutral (siempre hay traders)
            999.0,  // Ventana ilimitada (mercado maduro)
            0.4,    // Hype bajo-medio
            0.7     // Peso medio-bajo
        );
        
        option.factors["legal_risk"] = std::make_shared<LegalRiskFactor>(
            0.4,    // Riesgo medio (necesita disclaimers)
            500.0,  // $500/año en legal (T&C, disclaimers)
            0.2,    // 20% riesgo cambio regulatorio
            0.9     // Peso medio
        );
        
        option.factors["network_effects"] = std::make_shared<NetworkEffectsFactor>(
            10,     // Algunos contactos en trading
            false,  // Sin audiencia previa
            0.4,    // Credibilidad media-baja
            0.8     // Peso medio
        );
        
        option.factors["technical_scalability"] = std::make_shared<TechnicalScalabilityFactor>(
            100,    // Límite 100 usuarios (SMS caro)
            2.5,    // $2.5 por usuario (Twilio SMS)
            true,   // Necesita reescribir a 100+ usuarios
            1.0     // Peso normal
        );
        
        option.factors["prior_experience"] = std::make_shared<PriorExperienceFactor>(
            false,  // No hiciste sistemas de alertas antes
            0.3,    // 30% código reutilizable
            3,      // 3 beta users disponibles
            0.8     // Peso medio
        );
        
        simulator.addOption(option);
    }
    
    // ========================================================================
    // OPCIÓN 3: MONITOR YIELD FARMING DEFI
    // ========================================================================
    {
        DecisionOptionBuilder builder("yield_farming", "Monitor Yield Farming DeFi");
        builder.setRNG(&rng)
            .setDescription("Dashboard automatizado para monitorear yields en DeFi")
            
            .addNumericFactor("Initial Investment", "Financial", 0.98, 1.0)  // $30 (muy bajo)
            .addStochasticFactor("Monthly Income", "Financial", 0.50, 0.18, 1.5)  // $180±$90
            .addNumericFactor("Automation Level", "Technical", 0.78, 1.1)  // 78% automatizado
            .addNumericFactor("ROI", "Financial", 0.95, 1.0)  // 1890% ROI
            
            .addMetadata("initial_capital_usd", 30.0)
            .addMetadata("monthly_income_mean", 180.0);
        
        auto option = builder.build();
        
        option.factors["market_competition"] = std::make_shared<MarketCompetitionFactor>(
            0.4,    // Baja saturación (nicho emergente)
            0.7,    // Alta ventaja competitiva (especialización)
            0.6,    // Media barrera entrada (necesitas saber DeFi)
            1.2     // Peso alto
        );
        
        option.factors["technical_skills"] = std::make_shared<TechnicalSkillsFactor>(
            7.0,    // Nivel requerido 7/10 (Web3, blockchain)
            5.0,    // Tu nivel actual 5/10 (necesitas aprender)
            3.0,    // 3 meses para dominar Web3
            1.1     // Peso alto
        );
        
        option.factors["external_dependencies"] = std::make_shared<ExternalDependenciesFactor>(
            0.6,    // Media dependencia (DeFi Llama API gratis)
            0.2,    // 20% riesgo cambio pricing
            0.1,    // 10% riesgo cierre
            0.9,    // Peso medio
            &rng
        );
        
        option.factors["marketing_acquisition"] = std::make_shared<MarketingAcquisitionFactor>(
            25.0,   // CAC medio $25 (comunidad DeFi activa)
            180.0,  // LTV medio $180
            0.5,    // Viralidad media (nicho pero activo)
            1.0     // Peso normal
        );
        
        option.factors["burnout_risk"] = std::make_shared<BurnoutRiskFactor>(
            5.0,    // Estrés medio (necesitas actualizar protocolos)
            0.78,   // Media-alta automatización
            0.25,   // 25% probabilidad burnout
            1.0,    // Peso normal
            &rng
        );
        
        option.factors["market_timing"] = std::make_shared<MarketTimingFactor>(
            0.7,    // Tendencia muy positiva (DeFi en crecimiento)
            24.0,   // 24 meses ventana (DeFi sigue siendo nuevo)
            0.8,    // Hype alto (post-2024 DeFi boom)
            1.2     // Peso alto (timing crítico)
        );
        
        option.factors["legal_risk"] = std::make_shared<LegalRiskFactor>(
            0.2,    // Bajo riesgo (solo informativo)
            200.0,  // $200/año en legal
            0.3,    // 30% riesgo cambio regulatorio (DeFi regulándose)
            0.8     // Peso medio
        );
        
        option.factors["network_effects"] = std::make_shared<NetworkEffectsFactor>(
            20,     // Buenos contactos en DeFi (newsletter existente)
            true,   // TIENES AUDIENCIA (DeFi newsletter!)
            0.6,    // Credibilidad media-alta (ya en nicho)
            1.3     // Peso muy alto (SINERGIA con newsletter)
        );
        
        option.factors["technical_scalability"] = std::make_shared<TechnicalScalabilityFactor>(
            1000,   // Escala bien (API calls baratas)
            0.1,    // $0.10 por usuario
            false,  // No necesita reescribir
            0.9     // Peso medio
        );
        
        option.factors["prior_experience"] = std::make_shared<PriorExperienceFactor>(
            true,   // SÍ (ya tienes newsletter DeFi, sabes el nicho)
            0.5,    // 50% código reutilizable (scripts de newsletter)
            10,     // 10 beta users (suscriptores newsletter)
            1.3     // Peso muy alto (EXPERIENCIA PREVIA)
        );
        
        simulator.addOption(option);
    }
    
    // ========================================================================
    // OPCIÓN 4: SAAS ANÁLISIS DE DATOS
    // ========================================================================
    {
        DecisionOptionBuilder builder("market_analysis", "Análisis Datos Mercado (SaaS)");
        builder.setRNG(&rng)
            .setDescription("Plataforma SaaS para análisis de datos de mercado")
            
            .addNumericFactor("Initial Investment", "Financial", 0.93, 1.0)  // $50
            .addStochasticFactor("Monthly Income", "Financial", 0.45, 0.20, 1.5)  // $200±$100
            .addNumericFactor("Automation Level", "Technical", 0.72, 1.0)  // 72% automatizado
            .addNumericFactor("ROI", "Financial", 0.80, 1.0)  // 1111% ROI
            
            .addMetadata("initial_capital_usd", 50.0)
            .addMetadata("monthly_income_mean", 200.0);
        
        auto option = builder.build();
        
        option.factors["market_competition"] = std::make_shared<MarketCompetitionFactor>(
            0.9,    // Muy alta saturación (muchos SaaS de análisis)
            0.4,    // Baja ventaja competitiva
            0.3,    // Baja barrera entrada
            1.2     // Peso alto
        );
        
        option.factors["technical_skills"] = std::make_shared<TechnicalSkillsFactor>(
            6.0,    // Nivel requerido 6/10 (scraping, backend)
            6.0,    // Tu nivel actual 6/10
            1.0,    // 1 mes para dominar
            0.9     // Peso medio
        );
        
        option.factors["external_dependencies"] = std::make_shared<ExternalDependenciesFactor>(
            0.5,    // Media dependencia (scraping de datos públicos)
            0.3,    // 30% riesgo cambio (sitios bloquean scraping)
            0.1,    // 10% riesgo cierre
            1.0,    // Peso normal
            &rng
        );
        
        option.factors["marketing_acquisition"] = std::make_shared<MarketingAcquisitionFactor>(
            80.0,   // CAC alto $80 (mercado competido)
            200.0,  // LTV medio $200
            0.3,    // Baja viralidad
            1.1     // Peso alto (crítico para SaaS)
        );
        
        option.factors["burnout_risk"] = std::make_shared<BurnoutRiskFactor>(
            7.0,    // Alto estrés (soporte usuarios, bugs, scraping rompiéndose)
            0.72,   // Media automatización
            0.40,   // 40% probabilidad burnout
            1.2,    // Peso alto
            &rng
        );
        
        option.factors["market_timing"] = std::make_shared<MarketTimingFactor>(
            0.0,    // Tendencia neutral (demanda constante)
            999.0,  // Ventana ilimitada (mercado maduro)
            0.3,    // Hype bajo
            0.7     // Peso medio-bajo
        );
        
        option.factors["legal_risk"] = std::make_shared<LegalRiskFactor>(
            0.3,    // Riesgo medio-bajo
            300.0,  // $300/año en legal
            0.1,    // 10% riesgo cambio regulatorio
            0.8     // Peso medio
        );
        
        option.factors["network_effects"] = std::make_shared<NetworkEffectsFactor>(
            5,      // Pocos contactos
            false,  // Sin audiencia
            0.3,    // Baja credibilidad
            0.8     // Peso medio
        );
        
        option.factors["technical_scalability"] = std::make_shared<TechnicalScalabilityFactor>(
            500,    // Escala medio (scraping puede saturarse)
            0.5,    // $0.50 por usuario
            false,  // No necesita reescribir inicialmente
            0.9     // Peso medio
        );
        
        option.factors["prior_experience"] = std::make_shared<PriorExperienceFactor>(
            false,  // No hiciste SaaS antes
            0.25,   // 25% código reutilizable
            0,      // No hay beta users
            0.8     // Peso medio
        );
        
        simulator.addOption(option);
    }
}

// ============================================================================
// ANÁLISIS Y REPORTE DE RESULTADOS
// ============================================================================

void printDetailedResults(const MonteCarloSimulator& simulator) {
    std::cout << "\n" << std::string(100, '=') << "\n";
    std::cout << "📊 ANÁLISIS COMPLETO CON 10+ FACTORES ADICIONALES\n";
    std::cout << std::string(100, '=') << "\n\n";
    
    struct OptionStats {
        std::string id;
        std::string name;
        double mean_score;
        double success_rate;
        double p25, p50, p75;
        std::map<std::string, double> factor_averages;
    };
    
    std::vector<OptionStats> all_stats;
    
    for (const auto& [option_id, results] : simulator.getResults()) {
        OptionStats stats;
        stats.id = option_id;
        
        // Encontrar nombre de opción
        // (En producción, guardaríamos referencia)
        if (option_id == "arbitrage_bot") stats.name = "Bot Arbitraje Cripto";
        else if (option_id == "trading_alerts") stats.name = "Alertas Trading";
        else if (option_id == "yield_farming") stats.name = "Monitor Yield Farming DeFi";
        else if (option_id == "market_analysis") stats.name = "Análisis Datos Mercado";
        
        // Calcular estadísticas
        auto sim_stats = simulator.getStatistics(option_id);
        stats.mean_score = sim_stats["mean"];
        stats.success_rate = sim_stats["success_rate"];
        stats.p25 = sim_stats["p25"];
        stats.p50 = sim_stats["p50"];
        stats.p75 = sim_stats["p75"];
        
        // Promediar factores
        std::map<std::string, std::vector<double>> factor_values;
        for (const auto& result : results) {
            for (const auto& [factor_name, score] : result.factor_scores) {
                factor_values[factor_name].push_back(score);
            }
        }
        
        for (const auto& [factor_name, values] : factor_values) {
            double sum = std::accumulate(values.begin(), values.end(), 0.0);
            stats.factor_averages[factor_name] = sum / values.size();
        }
        
        all_stats.push_back(stats);
    }
    
    // Ordenar por score medio
    std::sort(all_stats.begin(), all_stats.end(),
              [](const OptionStats& a, const OptionStats& b) {
                  return a.mean_score > b.mean_score;
              });
    
    // Imprimir resultados detallados
    for (size_t i = 0; i < all_stats.size(); ++i) {
        const auto& stats = all_stats[i];
        
        std::cout << "🏆 POSICIÓN #" << (i + 1) << ": " << stats.name << "\n";
        std::cout << "   📊 Score Promedio: " << std::fixed << std::setprecision(3) 
                  << stats.mean_score << "\n";
        std::cout << "   📈 Rango (P25-P75): " << std::setprecision(3) 
                  << stats.p25 << " - " << stats.p75 << "\n";
        std::cout << "   ✅ Tasa de Éxito: " << std::setprecision(1) 
                  << stats.success_rate * 100 << "%\n";
        
        std::cout << "\n   🔍 Scores por Factor:\n";
        
        // Agrupar por categoría
        std::map<std::string, std::vector<std::pair<std::string, double>>> by_category;
        for (const auto& [factor_name, avg_score] : stats.factor_averages) {
            // Inferir categoría del nombre (en producción, guardar metadata)
            std::string category = "Other";
            if (factor_name.find("Market") != std::string::npos) category = "Market";
            else if (factor_name.find("Financial") != std::string::npos || 
                     factor_name.find("ROI") != std::string::npos ||
                     factor_name.find("Investment") != std::string::npos ||
                     factor_name.find("Income") != std::string::npos) category = "Financial";
            else if (factor_name.find("Risk") != std::string::npos || 
                     factor_name.find("Legal") != std::string::npos ||
                     factor_name.find("Dependencies") != std::string::npos) category = "Risk";
            else if (factor_name.find("Personal") != std::string::npos ||
                     factor_name.find("Skills") != std::string::npos ||
                     factor_name.find("Experience") != std::string::npos ||
                     factor_name.find("Burnout") != std::string::npos) category = "Personal";
            else if (factor_name.find("Marketing") != std::string::npos ||
                     factor_name.find("Network") != std::string::npos) category = "Growth";
            else if (factor_name.find("Technical") != std::string::npos ||
                     factor_name.find("Automation") != std::string::npos ||
                     factor_name.find("Scalability") != std::string::npos) category = "Technical";
            
            by_category[category].push_back({factor_name, avg_score});
        }
        
        for (const auto& [category, factors] : by_category) {
            std::cout << "      " << category << ":\n";
            for (const auto& [name, score] : factors) {
                std::cout << "        • " << std::left << std::setw(35) << name 
                          << std::right << std::setw(6) << std::setprecision(3) << score << "\n";
            }
        }
        
        std::cout << "\n";
    }
    
    // Recomendación final
    std::cout << "🎯 RECOMENDACIÓN FINAL (CON FACTORES MEJORADOS):\n";
    std::cout << "✅ MEJOR OPCIÓN: " << all_stats[0].name << "\n\n";
    
    std::cout << "💡 ANÁLISIS COMPARATIVO:\n";
    std::cout << "• Mayor score general: " << all_stats[0].name << "\n";
    
    auto max_success = std::max_element(all_stats.begin(), all_stats.end(),
        [](const OptionStats& a, const OptionStats& b) {
            return a.success_rate < b.success_rate;
        });
    std::cout << "• Mayor tasa de éxito: " << max_success->name << " (" 
              << std::setprecision(1) << max_success->success_rate * 100 << "%)\n";
    
    std::cout << "\n";
}

// ============================================================================
// MAIN
// ============================================================================

int main() {
    std::cout << "🚀 === SIMULACIÓN MEJORADA: DECISIÓN DE NEGOCIO AUTOMATIZADO === 🚀\n";
    std::cout << "Arquitectura Genérica con 10+ Factores Adicionales\n\n";
    
    // Crear simulador
    const size_t NUM_SIMULATIONS = 10000;
    std::mt19937 rng(std::random_device{}());
    MonteCarloSimulator simulator(NUM_SIMULATIONS);
    
    // Configurar opciones con todos los factores
    std::cout << "🔧 Configurando opciones con factores extendidos...\n";
    setupBusinessOptions(simulator, rng);
    
    // Ejecutar simulación
    std::cout << "⚙️  Ejecutando " << NUM_SIMULATIONS << " simulaciones por opción...\n\n";
    simulator.run();
    
    // Mostrar resultados
    printDetailedResults(simulator);
    
    std::cout << "📚 FACTORES CONSIDERADOS:\n";
    std::cout << "   Originales (4): Inversión, Ingresos, Automatización, ROI\n";
    std::cout << "   Nuevos (10):\n";
    std::cout << "   1. Competencia de Mercado (saturación, ventaja competitiva)\n";
    std::cout << "   2. Habilidades Técnicas (gap, curva aprendizaje)\n";
    std::cout << "   3. Dependencias Externas (APIs, riesgo cambio)\n";
    std::cout << "   4. Marketing/Adquisición (CAC, LTV, viralidad)\n";
    std::cout << "   5. Riesgo Burnout (estrés, automatización)\n";
    std::cout << "   6. Timing de Mercado (tendencia, ventana oportunidad)\n";
    std::cout << "   7. Riesgo Legal (compliance, costos legales)\n";
    std::cout << "   8. Efectos de Red (contactos, audiencia)\n";
    std::cout << "   9. Escalabilidad Técnica (límite usuarios, costo escalar)\n";
    std::cout << "   10. Experiencia Previa (proyectos similares, código reutilizable)\n\n";
    
    std::cout << "🎉 ¡Análisis completado con arquitectura genérica y extensible!\n";
    
    return 0;
}
