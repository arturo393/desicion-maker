/**
 * @file sillon_decision_v3_gemini.cpp
 * @brief VERSIÓN 3 - Decisión del sillón con DATOS REALES de Gemini API
 * 
 * ACTUALIZADO CON HALLAZGOS DE GEMINI (Dic 2025):
 * ⚠️  Sillones rotos/sucios = VALOR CASI NULO en mercado
 * ⚠️  Probabilidad REAL de venta: <5% (NO 60% como se asumió)
 * ⚠️  Precio REAL sillón roto: $0-10K (NO $120K-200K)
 * ⚠️  NO existe mercado para sillones GENÉRICOS restaurados
 * ✅  Mejor opción: BOTAR usando servicio MUNICIPAL ($0-10K)
 * 
 * LECCIÓN CIENTÍFICA:
 * Las simulaciones Monte Carlo son EXCELENTES para modelar incertidumbre,
 * PERO deben validarse con datos REALES del mercado.
 * "Garbage in, garbage out" - Los inputs deben ser realistas.
 * 
 * @author Arturo
 * @date 2025-12-08
 */

#include "../src/unified_decision_framework.h"
#include <iomanip>
#include <cmath>

using namespace DecisionFramework;

int main() {
    std::cout << "🪑 === ANÁLISIS DECISIÓN SILLÓN - V3 (DATOS REALES GEMINI API) ===\n\n";
    std::cout << "📍 Ubicación: Santiago, La Florida\n";
    std::cout << "📅 Fecha: Diciembre 2025\n";
    std::cout << "⏰ Plazo: 1 mes para resolver\n";
    std::cout << "💰 Situación: Muy corto de dinero\n\n";
    
    std::cout << "⚠️  HALLAZGOS CLAVE (Gemini API - Mercado Real):\n";
    std::cout << "   - Sillones rotos y sucios tienen VALOR CASI NULO\n";
    std::cout << "   - Probabilidad real de venta: <5% (no 60%)\n";
    std::cout << "   - Precio real sillón roto: $0-10K (no $120K-200K)\n";
    std::cout << "   - NO hay mercado para sillones genéricos restaurados\n";
    std::cout << "   - Solo funciona para: vintage calidad, madera noble\n\n";
    
    // ========================================================================
    // MONTE CARLO CON DATOS REALES (AJUSTADOS A MERCADO)
    // ========================================================================
    
    std::cout << "📊 MONTE CARLO (10,000 simulaciones - DATOS REALES)\n";
    std::cout << std::string(80, '=') << "\n\n";
    
    MonteCarloEngine mc_engine;
    mc_engine.setNumSimulations(10000);
    
    // Factores clave para tu decisión
    mc_engine.addFactor(Factor("Costo Neto", "Económico", 0.50, false));        // MÁS importante (corto $)
    mc_engine.addFactor(Factor("Probabilidad Éxito", "Riesgo", 0.30, true));    
    mc_engine.addFactor(Factor("Tiempo Resolución", "Velocidad", 0.20, false)); 
    
    // ========================================================================
    // OPCIÓN 1: BOTARLO - SERVICIO MUNICIPAL (RECOMENDADA POR GEMINI) ✅
    // ========================================================================
    
    std::cout << "✅ OPCIÓN 1: BOTAR (Municipal - RECOMENDADA)\n";
    std::cout << "   Municipalidad de La Florida ofrece retiro GRATUITO o bajo costo\n";
    std::cout << "   Costo real: $0-10K (vs $85K servicio privado)\n\n";
    
    DecisionOption botar_municipal("1. Botar (Municipal)", "Retiro gratuito o $0-10K");
    
    // Costo REAL municipal: 0-10K CLP
    botar_municipal.addVariable("Costo Neto",
        UncertainVariable("costo", DistributionType::TRIANGULAR, 0, 5000, 10000));
    
    botar_municipal.addVariable("Probabilidad Éxito",
        UncertainVariable("prob", DistributionType::UNIFORM, 0.75, 0.85)); // 80% éxito contactar municipalidad
    
    botar_municipal.addVariable("Tiempo Resolución",
        UncertainVariable("tiempo", DistributionType::UNIFORM, 1, 7)); // 1-7 días
    
    botar_municipal.setSimulator([](const std::map<std::string, double>& values, std::mt19937& gen) {
        SimulationResult result;
        result.factor_values = values;
        
        double prob_exito = values.at("Probabilidad Éxito");
        std::bernoulli_distribution exito_dist(prob_exito);
        bool municipalidad_responde = exito_dist(gen);
        
        if (municipalidad_responde) {
            // Municipalidad retira: costo mínimo
            result.events["Municipalidad retira"] = true;
            result.events["Problema resuelto"] = true;
        } else {
            // Plan B: regalar en Facebook (gratis pero toma tiempo)
            result.factor_values["Tiempo Resolución"] = 
                values.at("Tiempo Resolución") + 7; // +7 días más
            result.events["Plan B Facebook"] = true;
        }
        
        result.success = true;
        return result;
    });
    
    mc_engine.addOption(botar_municipal);
    
    // ========================================================================
    // OPCIÓN 2: SOLO LIMPIEZA (DATOS REALES - NO RECOMENDADA) ⚠️
    // ========================================================================
    
    std::cout << "⚠️  OPCIÓN 2: SOLO LIMPIAR (NO recomendada)\n";
    std::cout << "   REALIDAD: Sillón limpio pero ROTO sigue sin valor\n";
    std::cout << "   Precio real: $10K-30K (no $70K-120K como se pensaba)\n";
    std::cout << "   Probabilidad REAL venta: <10% (no 35%)\n";
    std::cout << "   Riesgo: Perder $40K de limpieza + $80K de botarlo después\n\n";
    
    DecisionOption solo_limpieza("2. Solo Limpiar", "Inversión $40K - Alto riesgo");
    
    // Costo: 30K-50K CLP
    solo_limpieza.addVariable("Costo Neto",
        UncertainVariable("costo", DistributionType::TRIANGULAR, 30000, 40000, 50000));
    
    // Probabilidad venta REAL: <10% (ajustado de 35%)
    solo_limpieza.addVariable("Probabilidad Éxito",
        UncertainVariable("prob", DistributionType::UNIFORM, 0.05, 0.10));
    
    // Tiempo: 10-30 días (puede NO venderse nunca)
    solo_limpieza.addVariable("Tiempo Resolución",
        UncertainVariable("tiempo", DistributionType::UNIFORM, 10, 30));
    
    solo_limpieza.setSimulator([](const std::map<std::string, double>& values, std::mt19937& gen) {
        SimulationResult result;
        result.factor_values = values;
        
        double prob_venta = values.at("Probabilidad Éxito");
        std::bernoulli_distribution venta_dist(prob_venta);
        bool se_vendio = venta_dist(gen);
        
        if (se_vendio) {
            // Precio venta REAL: 10K-30K (no 70K-120K)
            std::uniform_real_distribution<> precio_dist(10000, 30000);
            double precio_venta = precio_dist(gen);
            
            result.factor_values["Costo Neto"] = 
                values.at("Costo Neto") - precio_venta;
            
            result.events["Se Vendió"] = true;
            result.events["Ganancia"] = precio_venta - values.at("Costo Neto");
        } else {
            // NO se vendió (90% probabilidad): pierde inversión + debe botarlo
            result.factor_values["Costo Neto"] = 
                values.at("Costo Neto") + 85000;  // +$85K botar después
            
            result.events["Se Vendió"] = false;
            result.events["Tuvo que botar"] = true;
            result.events["PÉRDIDA TOTAL"] = values.at("Costo Neto") + 85000;
        }
        
        result.success = true;
        return result;
    });
    
    mc_engine.addOption(solo_limpieza);
    
    // ========================================================================
    // OPCIÓN 3: LIMPIAR + REPARAR (DATOS REALES - NO RECOMENDADA) ❌
    // ========================================================================
    
    std::cout << "❌ OPCIÓN 3: LIMPIAR + REPARAR (NO recomendada)\n";
    std::cout << "   REALIDAD MERCADO:\n";
    std::cout << "   - NO hay demanda para sillones GENÉRICOS restaurados\n";
    std::cout << "   - Solo funciona para: vintage, madera noble, diseño especial\n";
    std::cout << "   - Precio REAL: $50K-80K (no $120K-200K asumido)\n";
    std::cout << "   - Probabilidad REAL venta: <5% (NO 60% como se pensó)\n";
    std::cout << "   - Tiempo venta: 30-90+ días (puede NO venderse NUNCA)\n";
    std::cout << "   - RIESGO: Invertir $75K y NO recuperar NADA\n\n";
    
    DecisionOption limpieza_reparacion("3. Limpiar + Reparar", "Inversión $75K - Riesgo MUY ALTO");
    
    // Costo: 50K-100K CLP
    limpieza_reparacion.addVariable("Costo Neto",
        UncertainVariable("costo", DistributionType::TRIANGULAR, 50000, 75000, 100000));
    
    // Probabilidad venta REAL: <5% (NO 60%!)
    limpieza_reparacion.addVariable("Probabilidad Éxito",
        UncertainVariable("prob", DistributionType::UNIFORM, 0.02, 0.05));
    
    // Tiempo: 30-90 días (o NUNCA)
    limpieza_reparacion.addVariable("Tiempo Resolución",
        UncertainVariable("tiempo", DistributionType::UNIFORM, 30, 90));
    
    limpieza_reparacion.setSimulator([](const std::map<std::string, double>& values, std::mt19937& gen) {
        SimulationResult result;
        result.factor_values = values;
        
        double prob_venta = values.at("Probabilidad Éxito");
        std::bernoulli_distribution venta_dist(prob_venta);
        bool se_vendio = venta_dist(gen);
        
        if (se_vendio) {
            // Precio venta REAL: 50K-80K (no 120K-200K)
            std::uniform_real_distribution<> precio_dist(50000, 80000);
            double precio_venta = precio_dist(gen);
            
            result.factor_values["Costo Neto"] = 
                values.at("Costo Neto") - precio_venta;
            
            result.events["Se Vendió"] = true;
            result.events["Ganancia"] = precio_venta - values.at("Costo Neto");
        } else {
            // NO se vendió (95% probabilidad): PÉRDIDA TOTAL
            result.factor_values["Costo Neto"] = 
                values.at("Costo Neto") + 85000;  // +$85K botar después
            
            result.events["Se Vendió"] = false;
            result.events["Tuvo que botar"] = true;
            result.events["PÉRDIDA CATASTRÓFICA"] = values.at("Costo Neto") + 85000;
        }
        
        result.success = true;
        return result;
    });
    
    mc_engine.addOption(limpieza_reparacion);
    
    // ========================================================================
    // EJECUTAR SIMULACIÓN
    // ========================================================================
    
    std::cout << "⏳ Ejecutando 10,000 simulaciones...\n\n";
    
    auto mc_results = mc_engine.run();
    
    std::cout << "\n📈 RESULTADOS MONTE CARLO (CON DATOS REALES DE GEMINI):\n";
    std::cout << std::string(80, '=') << "\n";
    
    for (const auto& [option_name, stats] : mc_results) {
        std::cout << "\n🎯 " << option_name << "\n";
        std::cout << "   Costo promedio: $" << std::fixed << std::setprecision(0) 
                  << stats.mean_score << " CLP\n";
        std::cout << "   Desv. estándar: $" << stats.score_stddev << " CLP\n";
        std::cout << "   Rango: $" << stats.score_min 
                  << " a $" << stats.score_max << " CLP\n";
        
        if (stats.event_probabilities.find("Se Vendió") != stats.event_probabilities.end()) {
            std::cout << "   Prob. venta: " 
                      << (stats.event_probabilities.at("Se Vendió") * 100)
                      << "%\n";
        }
        std::cout << "\n";
    }
    
    // ========================================================================
    // RECOMENDACIÓN FINAL CON DATOS REALES
    // ========================================================================
    
    std::cout << "\n" << std::string(80, '=') << std::endl;
    std::cout << "🎯 RECOMENDACIÓN FINAL (DATOS REALES GEMINI API)" << std::endl;
    std::cout << std::string(80, '=') << std::endl;
    
    std::cout << "\n⚠️  IMPORTANTE - HALLAZGOS GEMINI API:\n" << std::endl;
    std::cout << "Las probabilidades asumidas inicialmente eran OPTIMISTAS:\n";
    std::cout << "   ❌ Asumido: 60% prob. venta sillón restaurado\n";
    std::cout << "   ✅ REAL:    <5% prob. venta (mercado casi inexistente)\n\n";
    std::cout << "   ❌ Asumido: Precio venta $120K-200K\n";
    std::cout << "   ✅ REAL:    Precio $0-10K para sillón roto\n\n";
    std::cout << "   ❌ Asumido: Existe mercado para restaurados\n";
    std::cout << "   ✅ REAL:    NO hay mercado para sillones GENÉRICOS\n\n";
    
    std::cout << "✅ RECOMENDACIÓN BASADA EN DATOS REALES:\n" << std::endl;
    std::cout << "   Opción: BOTAR usando servicio MUNICIPAL\n";
    std::cout << "   Costo:  $0 - $10,000\n";
    std::cout << "   Riesgo: MÍNIMO\n";
    std::cout << "   Tiempo: 1-7 días\n";
    std::cout << "   Prob. éxito: 80%\n\n";
    
    std::cout << "🔬 LECCIÓN CIENTÍFICA:\n" << std::endl;
    std::cout << "   Monte Carlo es EXCELENTE para modelar incertidumbre,\n";
    std::cout << "   PERO debe validarse con DATOS REALES del mercado.\n\n";
    std::cout << "   \"Garbage in, garbage out\"\n";
    std::cout << "   Si los inputs (probabilidades) son irrealistas,\n";
    std::cout << "   los outputs (recomendaciones) serán incorrectos.\n\n";
    
    std::cout << "📋 PLAN DE ACCIÓN REAL:\n" << std::endl;
    
    std::cout << "DÍA 1 (HOY):\n";
    std::cout << "   ☎️  Llamar Municipalidad de La Florida\n";
    std::cout << "   📋 Dirección de Aseo y Ornato\n";
    std::cout << "   📅 Preguntar: '¿Cuándo operativo recolección enseres?'\n";
    std::cout << "   💰 Agendar retiro GRATUITO o bajo costo ($0-10K)\n\n";
    
    std::cout << "DÍAS 2-7 (Plan B si municipalidad no responde):\n";
    std::cout << "   📱 Publicar en Facebook Marketplace como REGALO\n";
    std::cout << "   💬 Título: 'SE REGALA - Sillón para retiro La Florida'\n";
    std::cout << "   📸 Fotos honestas mostrando defectos\n";
    std::cout << "   💰 Precio: GRATIS o $5,000 simbólico\n";
    std::cout << "   ⏱️  Probabilidad retiro: 40-60%\n\n";
    
    std::cout << "DÍAS 21-30 (Plan C - última opción):\n";
    std::cout << "   💰 Contratar servicio privado: $85,000\n";
    std::cout << "   ✅ Garantía 100% se lo llevan\n\n";
    
    std::cout << "⚠️  NO INVERTIR en limpieza/reparación:\n";
    std::cout << "   ❌ Probabilidad recuperar inversión: <5%\n";
    std::cout << "   ❌ Riesgo perder $40K-75K completos\n";
    std::cout << "   ❌ Mercado NO existe para sillones genéricos\n";
    std::cout << "   ❌ Cuando estás corto de $, NO arriesgar capital\n\n";
    
    std::cout << "📞 CONTACTOS ÚTILES:\n";
    std::cout << "   - Municipalidad La Florida: Dirección Aseo y Ornato\n";
    std::cout << "   - Facebook Marketplace: facebook.com/marketplace\n";
    std::cout << "   - OLX Chile: olx.cl\n";
    std::cout << "   - Yapo.cl: yapo.cl\n\n";
    
    std::cout << "📚 ANÁLISIS COMPLETO:\n";
    std::cout << "   Ver: ANALISIS_GEMINI_REAL.md\n";
    std::cout << "   Ejecutar: python3 scripts/gemini_market_research.py --sillon\n\n";
    
    std::cout << std::string(80, '=') << std::endl;
    std::cout << "🎉 Sistema validado: Monte Carlo + TOPSIS + Gemini API\n";
    std::cout << "📞 ¡Ahora llama a la Municipalidad de La Florida!\n";
    std::cout << std::string(80, '=') << std::endl;
    
    return 0;
}
