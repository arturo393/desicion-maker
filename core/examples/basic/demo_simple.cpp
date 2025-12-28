#include <iostream>
#include <random>
#include <vector>
#include <iomanip>

/**
 * @brief Ejemplo ultrabasico de Monte Carlo sin el framework completo
 * 
 * Este ejemplo demuestra los conceptos fundamentales:
 * - Generación de números aleatorios
 * - Simulación repetitiva 
 * - Análisis estadístico básico
 * - Toma de decisiones basada en probabilidades
 * 
 * Escenario: Decidir si comprar un paraguas basado en predicción del clima
 */

struct Resultado {
    double costo_total;
    bool decision_correcta;
    bool llovio;
    bool llevo_paraguas;
};

// Función que simula un día y retorna el resultado
Resultado simular_dia(bool llevar_paraguas, std::mt19937& gen) {
    // Distribuciones de probabilidad
    std::uniform_real_distribution<double> prob_lluvia(0.0, 1.0);
    std::uniform_real_distribution<double> intensidad_lluvia(0.1, 1.0);
    
    // Parámetros del escenario
    const double probabilidad_lluvia = 0.3;  // 30% de que llueva
    const double costo_mojarse = 10.0;       // Costo de mojarse
    const double molestia_paraguas = 1.0;    // Molestia de cargar paraguas
    
    // ¿Llueve hoy?
    bool llueve = prob_lluvia(gen) < probabilidad_lluvia;
    
    // Calcular costos
    double costo = 0.0;
    bool decision_correcta = false;
    
    if (llevar_paraguas) {
        costo += molestia_paraguas;  // Siempre hay molestia
        
        if (llueve) {
            // Llevé paraguas y llovió: ¡decisión correcta!
            decision_correcta = true;
            // No me mojo, solo la molestia del paraguas
        } else {
            // Llevé paraguas y no llovió: molestia innecesaria
            decision_correcta = false;
        }
    } else {
        // No llevé paraguas
        if (llueve) {
            // No llevé paraguas y llovió: ¡me mojo!
            double intensidad = intensidad_lluvia(gen);
            costo += costo_mojarse * intensidad;
            decision_correcta = false;
        } else {
            // No llevé paraguas y no llovió: ¡perfecto!
            decision_correcta = true;
        }
    }
    
    return {costo, decision_correcta, llueve, llevar_paraguas};
}

int main() {
    std::cout << "=== Simulación Monte Carlo: ¿Llevar Paraguas? ===\n\n";
    
    // Configuración
    const int num_simulaciones = 10000;
    std::random_device rd;
    std::mt19937 gen(rd());
    
    // Contenedores para resultados
    std::vector<Resultado> resultados_con_paraguas;
    std::vector<Resultado> resultados_sin_paraguas;
    
    resultados_con_paraguas.reserve(num_simulaciones);
    resultados_sin_paraguas.reserve(num_simulaciones);
    
    // Ejecutar simulaciones
    std::cout << "🎲 Ejecutando " << num_simulaciones << " simulaciones para cada estrategia...\n";
    
    for (int i = 0; i < num_simulaciones; ++i) {
        // Simular llevando paraguas
        resultados_con_paraguas.push_back(simular_dia(true, gen));
        
        // Simular sin llevar paraguas  
        resultados_sin_paraguas.push_back(simular_dia(false, gen));
    }
    
    // Análisis de resultados
    auto analizar_resultados = [](const std::vector<Resultado>& resultados, const std::string& estrategia) {
        double costo_promedio = 0.0;
        int decisiones_correctas = 0;
        int dias_lluvia = 0;
        
        for (const auto& r : resultados) {
            costo_promedio += r.costo_total;
            if (r.decision_correcta) decisiones_correctas++;
            if (r.llovio) dias_lluvia++;
        }
        
        costo_promedio /= resultados.size();
        double tasa_acierto = (double)decisiones_correctas / resultados.size();
        double probabilidad_lluvia_observada = (double)dias_lluvia / resultados.size();
        
        std::cout << "\n📊 ESTRATEGIA: " << estrategia << "\n";
        std::cout << "   Costo promedio: " << std::fixed << std::setprecision(2) << costo_promedio << "\n";
        std::cout << "   Tasa de acierto: " << std::setprecision(1) << tasa_acierto * 100 << "%\n";
        std::cout << "   Días con lluvia observados: " << probabilidad_lluvia_observada * 100 << "%\n";
        
        return std::make_pair(costo_promedio, tasa_acierto);
    };
    
    // Analizar ambas estrategias
    auto [costo_con, acierto_con] = analizar_resultados(resultados_con_paraguas, "LLEVAR PARAGUAS");
    auto [costo_sin, acierto_sin] = analizar_resultados(resultados_sin_paraguas, "NO LLEVAR PARAGUAS");
    
    // Recomendación
    std::cout << "\n🤔 RECOMENDACIÓN BASADA EN DATOS:\n";
    
    if (costo_con < costo_sin) {
        std::cout << "✅ LLEVAR PARAGUAS\n";
        std::cout << "   Razón: Menor costo esperado (" << std::setprecision(2) 
                  << costo_con << " vs " << costo_sin << ")\n";
        std::cout << "   Ahorro esperado: " << (costo_sin - costo_con) << " por día\n";
    } else {
        std::cout << "✅ NO LLEVAR PARAGUAS\n";
        std::cout << "   Razón: Menor costo esperado (" << std::setprecision(2) 
                  << costo_sin << " vs " << costo_con << ")\n";
        std::cout << "   Ahorro esperado: " << (costo_con - costo_sin) << " por día\n";
    }
    
    // Análisis adicional
    std::cout << "\n📈 ANÁLISIS ADICIONAL:\n";
    
    // Buscar el peor caso para cada estrategia
    auto peor_con = *std::max_element(resultados_con_paraguas.begin(), 
                                     resultados_con_paraguas.end(),
                                     [](const Resultado& a, const Resultado& b) {
                                         return a.costo_total < b.costo_total;
                                     });
    
    auto peor_sin = *std::max_element(resultados_sin_paraguas.begin(), 
                                     resultados_sin_paraguas.end(),
                                     [](const Resultado& a, const Resultado& b) {
                                         return a.costo_total < b.costo_total;
                                     });
    
    std::cout << "   Peor caso con paraguas: " << peor_con.costo_total << "\n";
    std::cout << "   Peor caso sin paraguas: " << peor_sin.costo_total << "\n";
    
    // Percentil 95 (Value at Risk básico)
    auto calcular_percentil_95 = [](std::vector<Resultado> resultados) {
        std::sort(resultados.begin(), resultados.end(), 
                  [](const Resultado& a, const Resultado& b) {
                      return a.costo_total < b.costo_total;
                  });
        size_t index_95 = (size_t)(resultados.size() * 0.95);
        return resultados[index_95].costo_total;
    };
    
    double var_95_con = calcular_percentil_95(resultados_con_paraguas);
    double var_95_sin = calcular_percentil_95(resultados_sin_paraguas);
    
    std::cout << "   VaR 95% con paraguas: " << var_95_con << "\n";
    std::cout << "   VaR 95% sin paraguas: " << var_95_sin << "\n";
    
    std::cout << "\n💡 CONCLUSIÓN:\n";
    std::cout << "Este es un ejemplo básico de cómo Monte Carlo te ayuda a tomar\n";
    std::cout << "mejores decisiones considerando incertidumbre. El framework completo\n";
    std::cout << "te permite hacer esto para cualquier tipo de decisión!\n";
    
    return 0;
}