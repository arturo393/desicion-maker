#include "../src/core/MonteCarloEngine.h"
#include "../src/scenarios/CommonScenarios.h"
#include "../src/distributions/Distributions.h"
#include "../src/utils/Analysis.h"
#include <iostream>
#include <iomanip>

using namespace DecisionMaker;
using namespace DecisionMaker::Scenarios;
using namespace DecisionMaker::Utils;

/**
 * @brief Ejemplo completo: Decisión de inversión vs educación
 * 
 * Escenario: Una persona debe decidir entre:
 * 1. Invertir $50,000 en el mercado de valores
 * 2. Usar ese dinero para obtener una maestría que aumente su salario
 * 
 * Vamos a usar Monte Carlo para evaluar ambas opciones considerando incertidumbre.
 */

int main() {
    std::cout << "=== Decision Maker Framework - Ejemplo de Inversión vs Educación ===\n\n";
    
    try {
        // Configuración del motor Monte Carlo
        auto config = MonteCarloConfigBuilder()
            .withSimulations(50000)
            .withThreads(4)
            .withVerbose(true)
            .withConvergenceCheck(true, 0.001)
            .build();
        
        MonteCarloEngine engine(config);
        
        // === OPCIÓN 1: INVERSIÓN EN MERCADO ===
        std::cout << "Configurando escenario de inversión...\n";
        
        InvestmentScenario investment_scenario;
        investment_scenario.setInitialInvestment(50000.0);
        investment_scenario.setExpectedReturn(0.08, 0.15); // 8% anual, 15% volatilidad
        investment_scenario.setTimeHorizon(10.0); // 10 años
        investment_scenario.setTransactionCosts(0.01); // 1% costos
        
        // Callback para mostrar progreso
        auto progress_callback = [](size_t completed, size_t total) {
            if (completed % 5000 == 0) {
                double percent = (double)completed / total * 100.0;
                std::cout << "Progreso: " << std::fixed << std::setprecision(1) 
                         << percent << "% (" << completed << "/" << total << ")\n";
            }
        };
        
        std::cout << "Ejecutando simulación de inversión...\n";
        auto investment_results = engine.simulate(investment_scenario, progress_callback);
        
        // === OPCIÓN 2: EDUCACIÓN (MAESTRÍA) ===
        std::cout << "\nConfigurando escenario de carrera con maestría...\n";
        
        CareerDecisionScenario career_scenario;
        
        // Carrera actual (sin maestría)
        career_scenario.addCareerPath(
            "Actual",
            60000.0, // Salario inicial
            std::make_unique<NormalDistribution>(0.03, 0.01), // 3% crecimiento anual
            std::make_unique<UniformDistribution>(0.1, 0.2),  // 10-20% prob promoción
            std::make_unique<NormalDistribution>(7.0, 1.0),   // Satisfacción 7/10
            1.0 // Factor de demanda del mercado
        );
        
        // Carrera con maestría
        career_scenario.addCareerPath(
            "Con_Maestria",
            75000.0, // Salario inicial más alto
            std::make_unique<NormalDistribution>(0.05, 0.015), // 5% crecimiento anual
            std::make_unique<UniformDistribution>(0.2, 0.3),   // 20-30% prob promoción
            std::make_unique<NormalDistribution>(8.0, 1.0),    // Satisfacción 8/10
            1.2 // Mayor demanda del mercado
        );
        
        // Configurar parámetros
        career_scenario.getParameters().setValue("time_horizon", 10.0);
        career_scenario.getParameters().setValue("satisfaction_weight", 0.3);
        career_scenario.getParameters().setValue("salary_weight", 0.7);
        career_scenario.getParameters().setValue("education_cost", 50000.0); // Costo de la maestría
        
        std::cout << "Ejecutando simulación de carrera...\n";
        auto career_results = engine.simulate(career_scenario, progress_callback);
        
        // === ANÁLISIS COMPARATIVO ===
        std::cout << "\n=== ANÁLISIS DE RESULTADOS ===\n\n";
        
        // Comparar escenarios
        ScenarioComparator comparator;
        comparator.addScenario("Inversión en Mercado", investment_results, 0.02);
        comparator.addScenario("Educación (Maestría)", career_results, 0.02);
        comparator.rankScenarios("mean", false); // Ranking por valor esperado
        
        std::cout << comparator.generateReport() << "\n";
        
        // Análisis estadístico detallado
        std::cout << "=== ANÁLISIS ESTADÍSTICO DETALLADO ===\n\n";
        
        // Inversión
        std::cout << "INVERSIÓN EN MERCADO:\n";
        std::cout << "VaR (95%): $" << std::fixed << std::setprecision(2) 
                  << StatisticalAnalyzer::calculateVaR(investment_results, 0.95) << "\n";
        std::cout << "CVaR (95%): $" << StatisticalAnalyzer::calculateCVaR(investment_results, 0.95) << "\n";
        std::cout << "Sharpe Ratio: " << std::setprecision(3) 
                  << StatisticalAnalyzer::calculateSharpeRatio(investment_results, 0.02) << "\n";
        std::cout << "Asimetría: " << StatisticalAnalyzer::calculateSkewness(investment_results) << "\n";
        std::cout << "Curtosis: " << StatisticalAnalyzer::calculateKurtosis(investment_results) << "\n\n";
        
        // Carrera
        std::cout << "EDUCACIÓN (MAESTRÍA):\n";
        std::cout << "VaR (95%): $" << std::fixed << std::setprecision(2) 
                  << StatisticalAnalyzer::calculateVaR(career_results, 0.95) << "\n";
        std::cout << "CVaR (95%): $" << StatisticalAnalyzer::calculateCVaR(career_results, 0.95) << "\n";
        std::cout << "Sharpe Ratio: " << std::setprecision(3) 
                  << StatisticalAnalyzer::calculateSharpeRatio(career_results, 0.02) << "\n";
        std::cout << "Asimetría: " << StatisticalAnalyzer::calculateSkewness(career_results) << "\n";
        std::cout << "Curtosis: " << StatisticalAnalyzer::calculateKurtosis(career_results) << "\n\n";
        
        // Visualizaciones
        std::cout << "=== VISUALIZACIONES ===\n\n";
        
        std::cout << "Histograma - Inversión en Mercado:\n";
        std::cout << TextVisualizer::generateHistogram(investment_results, 20, 60) << "\n\n";
        
        std::cout << "Histograma - Educación (Maestría):\n";
        std::cout << TextVisualizer::generateHistogram(career_results, 20, 60) << "\n\n";
        
        // Box plots comparativos
        std::cout << "Box Plot - Inversión:\n";
        std::cout << TextVisualizer::generateBoxPlot(investment_results, 60) << "\n\n";
        
        std::cout << "Box Plot - Educación:\n";
        std::cout << TextVisualizer::generateBoxPlot(career_results, 60) << "\n\n";
        
        // === RECOMENDACIÓN FINAL ===
        std::cout << "=== RECOMENDACIÓN BASADA EN DATOS ===\n\n";
        
        double inv_mean = investment_results.getMean();
        double career_mean = career_results.getMean();
        double inv_success = investment_results.getSuccessProbability();
        double career_success = career_results.getSuccessProbability();
        
        std::cout << "Basado en " << config.num_simulations << " simulaciones Monte Carlo:\n\n";
        
        if (career_mean > inv_mean) {
            std::cout << "✅ RECOMENDACIÓN: EDUCACIÓN (MAESTRÍA)\n";
            std::cout << "Razones:\n";
            std::cout << "• Mayor valor esperado: $" << std::fixed << std::setprecision(0) 
                      << career_mean << " vs $" << inv_mean << "\n";
            std::cout << "• Diferencia: $" << (career_mean - inv_mean) << " a favor de la educación\n";
            if (career_success > inv_success) {
                std::cout << "• Mayor probabilidad de éxito: " << std::setprecision(1) 
                          << career_success * 100 << "% vs " << inv_success * 100 << "%\n";
            }
        } else {
            std::cout << "✅ RECOMENDACIÓN: INVERSIÓN EN MERCADO\n";
            std::cout << "Razones:\n";
            std::cout << "• Mayor valor esperado: $" << std::fixed << std::setprecision(0) 
                      << inv_mean << " vs $" << career_mean << "\n";
            std::cout << "• Diferencia: $" << (inv_mean - career_mean) << " a favor de la inversión\n";
            if (inv_success > career_success) {
                std::cout << "• Mayor probabilidad de éxito: " << std::setprecision(1) 
                          << inv_success * 100 << "% vs " << career_success * 100 << "%\n";
            }
        }
        
        std::cout << "\n⚠️  CONSIDERACIONES ADICIONALES:\n";
        std::cout << "• La educación proporciona beneficios intangibles (conocimiento, red de contactos)\n";
        std::cout << "• La inversión es más líquida y flexible\n";
        std::cout << "• Considere su tolerancia al riesgo personal\n";
        std::cout << "• Evalúe las condiciones específicas de su mercado laboral\n";
        
        // Generar reportes completos
        std::cout << "\n=== GENERANDO REPORTES DETALLADOS ===\n";
        
        auto investment_report = ReportGenerator::generateFullReport(
            investment_scenario, investment_results, true);
        ReportGenerator::exportReport(investment_report, "reporte_inversion.txt");
        
        auto career_report = ReportGenerator::generateFullReport(
            career_scenario, career_results, true);
        ReportGenerator::exportReport(career_report, "reporte_carrera.txt");
        
        // Exportar datos para análisis posterior
        investment_results.exportToCSV("datos_inversion.csv");
        career_results.exportToCSV("datos_carrera.csv");
        comparator.exportToCSV("comparacion_escenarios.csv");
        
        std::cout << "✅ Reportes y datos exportados exitosamente\n";
        std::cout << "📊 Archivos generados: reporte_inversion.txt, reporte_carrera.txt\n";
        std::cout << "📈 Datos CSV: datos_inversion.csv, datos_carrera.csv, comparacion_escenarios.csv\n";
        
    } catch (const std::exception& e) {
        std::cerr << "❌ Error durante la simulación: " << e.what() << std::endl;
        return 1;
    }
    
    std::cout << "\n🎉 Simulación completada exitosamente!\n";
    std::cout << "Gracias por usar Decision Maker Framework\n";
    
    return 0;
}