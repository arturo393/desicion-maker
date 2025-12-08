/**
 * @file template_new_decision.cpp
 * @brief PLANTILLA para agregar nuevas decisiones al framework
 * 
 * Esta es una plantilla que muestra cómo usar DecisionFramework
 * para CUALQUIER tipo de decisión (Sillón, Computador, Inversión, etc)
 * 
 * INSTRUCCIONES:
 * 1. Copiar este archivo y renombrarlo: 3_mi_decision.cpp
 * 2. Cambiar los datos según tu decisión
 * 3. Compilar: cd build && make
 * 4. Ejecutar: ./mi_decision
 */

#include "decision_framework.h"
#include "real_time_monitor.h"
#include "bayesian_updater.h"
#include "scenario_analysis.h"
#include "ml_demand_predictor.h"
#include "value_at_risk.h"

#include <iostream>
#include <iomanip>

using namespace decision;

// ============================================================================
// ADAPTADORES: Convertir metodologías existentes al framework genérico
// ============================================================================

/**
 * @class RealTimeMonitorAdapter
 * Adapta RealTimeMonitor al framework genérico
 */
class RealTimeMonitorAdapter : public Methodology {
public:
    std::string get_name() const override {
        return "Real-Time Market Monitor";
    }
    
    std::string get_description() const override {
        return "Analiza datos en tiempo real del mercado";
    }
    
    AnalysisResult analyze(const std::vector<Option>& options) override {
        AnalysisResult result(get_name());
        
        // TODO: Implementar análisis real-time
        // Por ahora, dummy data
        result.recommended_option = options.empty() ? "N/A" : options[0].name;
        result.confidence = 0.85;
        result.reasoning = "Basado en análisis de mercado en tiempo real";
        
        return result;
    }
};

/**
 * @class BayesianUpdaterAdapter
 * Adapta BayesianUpdater al framework genérico
 */
class BayesianUpdaterAdapter : public Methodology {
public:
    std::string get_name() const override {
        return "Bayesian Probability Updater";
    }
    
    std::string get_description() const override {
        return "Actualiza probabilidades con evidencia";
    }
    
    AnalysisResult analyze(const std::vector<Option>& options) override {
        AnalysisResult result(get_name());
        
        // TODO: Implementar actualización Bayesiana
        result.recommended_option = options.empty() ? "N/A" : options[0].name;
        result.confidence = 0.80;
        result.reasoning = "Basado en actualización de probabilidades";
        
        return result;
    }
};

/**
 * @class MLPredictorAdapter
 * Adapta ML Demand Predictor al framework genérico
 */
class MLPredictorAdapter : public Methodology {
public:
    std::string get_name() const override {
        return "Machine Learning Predictor";
    }
    
    std::string get_description() const override {
        return "Predice usando regresión logística";
    }
    
    AnalysisResult analyze(const std::vector<Option>& options) override {
        AnalysisResult result(get_name());
        
        // TODO: Implementar predicción ML
        result.recommended_option = options.empty() ? "N/A" : options[0].name;
        result.confidence = 0.75;
        result.reasoning = "Basado en modelo ML entrenado";
        
        return result;
    }
};

// ============================================================================
// MAIN: EJEMPLO DE USO
// ============================================================================

int main() {
    try {
        std::cout << "\n";
        std::cout << "╔════════════════════════════════════════════════════════════════╗\n";
        std::cout << "║                                                                ║\n";
        std::cout << "║         PLANTILLA: USAR FRAMEWORK PARA NUEVA DECISIÓN          ║\n";
        std::cout << "║                                                                ║\n";
        std::cout << "╚════════════════════════════════════════════════════════════════╝\n";
        std::cout << "\n";
        
        // ────────────────────────────────────────────────────────────────────────
        // PASO 1: CREAR FRAMEWORK PARA TU DECISIÓN
        // ────────────────────────────────────────────────────────────────────────
        
        // TODO: Cambiar título según tu decisión
        DecisionFramework framework("MI NUEVA DECISIÓN");  // ← CAMBIAR AQUÍ
        
        // ────────────────────────────────────────────────────────────────────────
        // PASO 2: AGREGAR OPCIONES A EVALUAR
        // ────────────────────────────────────────────────────────────────────────
        
        // TODO: Definir opciones según tu decisión
        
        // Opción A
        Option option_a("OPCIÓN_A", "Primera alternativa");
        option_a.estimated_cost = 1000;      // Costo esperado
        option_a.estimated_benefit = 5000;   // Beneficio esperado
        option_a.time_days = 30;             // Tiempo en días
        framework.add_option(option_a);
        
        // Opción B
        Option option_b("OPCIÓN_B", "Segunda alternativa");
        option_b.estimated_cost = 5000;
        option_b.estimated_benefit = 2000;
        option_b.time_days = 90;
        framework.add_option(option_b);
        
        // Opción C (opcional)
        Option option_c("OPCIÓN_C", "Tercera alternativa");
        option_c.estimated_cost = 0;
        option_c.estimated_benefit = 0;
        option_c.time_days = 0;
        framework.add_option(option_c);
        
        // ────────────────────────────────────────────────────────────────────────
        // PASO 3: AGREGAR METODOLOGÍAS
        // ────────────────────────────────────────────────────────────────────────
        
        // Puedes usar adaptadores o metodologías custom
        framework.add_methodology(std::make_unique<RealTimeMonitorAdapter>());
        framework.add_methodology(std::make_unique<BayesianUpdaterAdapter>());
        framework.add_methodology(std::make_unique<MLPredictorAdapter>());
        
        // ────────────────────────────────────────────────────────────────────────
        // PASO 4: EJECUTAR ANÁLISIS
        // ────────────────────────────────────────────────────────────────────────
        
        std::cout << "🔍 Ejecutando análisis con " << framework.get_methodology_count() 
                  << " metodologías...\n\n";
        
        auto report = framework.analyze();
        
        // ────────────────────────────────────────────────────────────────────────
        // PASO 5: MOSTRAR RESULTADOS
        // ────────────────────────────────────────────────────────────────────────
        
        std::cout << "════════════════════════════════════════════════════════════════\n";
        std::cout << "📊 RESULTADO FINAL\n";
        std::cout << "════════════════════════════════════════════════════════════════\n\n";
        
        std::cout << "Decisión: " << std::setw(20) << report.final_recommendation << "\n";
        std::cout << "Confianza: " << std::setw(18) << report.final_confidence * 100 
                  << "%\n";
        std::cout << "Metodologías concordando: " << report.methodologies_count << "\n\n";
        
        std::cout << "────────────────────────────────────────────────────────────────\n";
        std::cout << "Resultados por Opción:\n";
        std::cout << "────────────────────────────────────────────────────────────────\n\n";
        
        for (const auto& [option, confidence] : report.option_confidence) {
            std::cout << "  " << option << ": " << std::setw(3) 
                      << static_cast<int>(confidence * 100) << "%\n";
        }
        
        std::cout << "\n";
        std::cout << "────────────────────────────────────────────────────────────────\n";
        std::cout << "Análisis Detallado por Metodología:\n";
        std::cout << "────────────────────────────────────────────────────────────────\n\n";
        
        for (size_t i = 0; i < report.all_results.size(); ++i) {
            const auto& result = report.all_results[i];
            std::cout << (i + 1) << ". " << result.methodology_name << "\n";
            std::cout << "   → Recomienda: " << result.recommended_option << "\n";
            std::cout << "   → Confianza: " << static_cast<int>(result.confidence * 100) 
                      << "%\n";
            std::cout << "   → Razón: " << result.reasoning << "\n\n";
        }
        
        // Opcional: Generar reporte markdown
        std::cout << "════════════════════════════════════════════════════════════════\n";
        std::cout << "\n✅ ANÁLISIS COMPLETADO\n\n";
        std::cout << "Próximos pasos:\n";
        std::cout << "1. Personalizar las opciones con tus datos reales\n";
        std::cout << "2. Implementar metodologías específicas para tu caso\n";
        std::cout << "3. Ajustar pesos de confianza según experiencia\n";
        std::cout << "4. Repetir el análisis con nuevos datos\n\n";
        
    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << "\n";
        return 1;
    }
    
    return 0;
}

/*
═══════════════════════════════════════════════════════════════════════════════
INSTRUCCIONES DE ADAPTACIÓN

Para usar este template con TU DECISIÓN:

1. CAMBIAR TÍTULO
   DecisionFramework framework("MI NUEVA DECISIÓN");
   
2. DEFINIR OPCIONES
   - Opción A: Primera alternativa
   - Opción B: Segunda alternativa
   - Opción C: (opcional)
   
3. ASIGNAR COSTOS Y BENEFICIOS
   option.estimated_cost = valor;      // Cuánto cuesta
   option.estimated_benefit = valor;   // Cuánto beneficia
   option.time_days = valor;           // Cuánto tiempo toma

4. ELEGIR METODOLOGÍAS
   framework.add_methodology(std::make_unique<MiMetodología>());
   
5. COMPILAR Y EJECUTAR
   cd build && make
   ./template_new_decision

═══════════════════════════════════════════════════════════════════════════════
EJEMPLOS DE DECISIONES QUE SE PUEDEN ANALIZAR:

• Comprar/vender computador
• Invertir en criptomonedas
• Cambiar de trabajo
• Mudarse a otra ciudad
• Iniciar startup
• Comprar vs arrendar casa
• Usar cloud vs servidor local
• Cualquier decisión con múltiples opciones y criterios

═══════════════════════════════════════════════════════════════════════════════
*/
