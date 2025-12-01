#include <iostream>
#include <random>
#include <vector>
#include <string>
#include <iomanip>
#include <algorithm>
#include <map>

/**
 * @brief Simulación Monte Carlo: ¿Qué auto comprar?
 * 
 * Escenario realista: Comparar diferentes opciones de automóviles considerando:
 * - Precio inicial y financiamiento
 * - Depreciación variable
 * - Costos de mantenimiento inciertos
 * - Consumo de combustible
 * - Probabilidad de averías mayores
 * - Valor de reventa
 * - Satisfacción personal
 */

struct Auto {
    std::string marca_modelo;
    double precio_inicial;
    double enganche_requerido;
    double tasa_interes_financiamiento;
    int meses_financiamiento;
    
    // Parámetros de incertidumbre (se modelarán con distribuciones)
    double depreciacion_anual_media;
    double depreciacion_variabilidad;
    double costo_mantenimiento_anual_base;
    double variabilidad_mantenimiento;
    double consumo_litros_por_100km;
    double variabilidad_consumo;
    double probabilidad_averia_mayor_anual;
    double costo_averia_mayor_promedio;
    
    // Factores subjetivos
    double satisfaccion_inicial;  // 1-10
    double factor_depreciacion_satisfaccion;  // Cómo afecta el tiempo
};

struct ResultadoSimulacion {
    std::string auto_elegido;
    double costo_total_5_años;
    double valor_residual;
    double costo_neto;
    double satisfaccion_promedio;
    double costo_por_km;
    bool tuvo_averia_mayor;
    double puntuacion_total;  // Métrica combinada
};

class SimuladorDecisionAuto {
private:
    std::vector<Auto> opciones_;
    std::mt19937 gen_;
    const int años_analisis_ = 5;
    const double km_por_año_ = 15000;  // Promedio de manejo anual
    const double precio_gasolina_por_litro_ = 24.0;  // Pesos mexicanos
    
public:
    SimuladorDecisionAuto() : gen_(std::random_device{}()) {}
    
    void agregarOpcion(const Auto& auto_opcion) {
        opciones_.push_back(auto_opcion);
    }
    
    ResultadoSimulacion simularAuto(const Auto& auto_opcion) {
        ResultadoSimulacion resultado;
        resultado.auto_elegido = auto_opcion.marca_modelo;
        
        // Distribuciones para modelar incertidumbre
        std::normal_distribution<double> dist_depreciacion(
            auto_opcion.depreciacion_anual_media, 
            auto_opcion.depreciacion_variabilidad
        );
        
        std::normal_distribution<double> dist_mantenimiento(
            auto_opcion.costo_mantenimiento_anual_base,
            auto_opcion.variabilidad_mantenimiento
        );
        
        std::normal_distribution<double> dist_consumo(
            auto_opcion.consumo_litros_por_100km,
            auto_opcion.variabilidad_consumo
        );
        
        std::uniform_real_distribution<double> dist_uniforme(0.0, 1.0);
        std::exponential_distribution<double> dist_averia(1.0 / auto_opcion.costo_averia_mayor_promedio);
        
        // === CALCULAR COSTOS INICIALES ===
        double monto_financiado = auto_opcion.precio_inicial - auto_opcion.enganche_requerido;
        double pago_mensual = calcularPagoMensual(
            monto_financiado, 
            auto_opcion.tasa_interes_financiamiento / 12.0, 
            auto_opcion.meses_financiamiento
        );
        
        double costo_financiamiento_total = pago_mensual * auto_opcion.meses_financiamiento;
        
        // === SIMULAR AÑO POR AÑO ===
        double valor_actual = auto_opcion.precio_inicial;
        double costo_mantenimiento_total = 0.0;
        double costo_combustible_total = 0.0;
        double satisfaccion_acumulada = 0.0;
        bool tuvo_averia_mayor = false;
        double costo_averias_total = 0.0;
        
        for (int año = 1; año <= años_analisis_; ++año) {
            // Depreciación anual (con variabilidad)
            double tasa_depreciacion = std::max(0.05, dist_depreciacion(gen_));  // Mínimo 5%
            tasa_depreciacion = std::min(0.30, tasa_depreciacion);  // Máximo 30%
            valor_actual *= (1.0 - tasa_depreciacion);
            
            // Costos de mantenimiento (incrementan con la edad del auto)
            double factor_edad = 1.0 + (año - 1) * 0.1;  // 10% más cada año
            double costo_mantenimiento_año = std::max(0.0, 
                dist_mantenimiento(gen_) * factor_edad);
            costo_mantenimiento_total += costo_mantenimiento_año;
            
            // Consumo de combustible
            double consumo_año = std::max(5.0, dist_consumo(gen_));  // Mínimo 5L/100km
            double litros_año = (km_por_año_ / 100.0) * consumo_año;
            double costo_combustible_año = litros_año * precio_gasolina_por_litro_;
            costo_combustible_total += costo_combustible_año;
            
            // Probabilidad de avería mayor
            if (dist_uniforme(gen_) < auto_opcion.probabilidad_averia_mayor_anual) {
                tuvo_averia_mayor = true;
                double costo_averia = dist_averia(gen_);
                costo_averias_total += costo_averia;
            }
            
            // Satisfacción (decrece con el tiempo pero varía por auto)
            double satisfaccion_año = auto_opcion.satisfaccion_inicial * 
                (1.0 - auto_opcion.factor_depreciacion_satisfaccion * (año - 1));
            satisfaccion_año = std::max(1.0, satisfaccion_año);  // Mínimo 1
            satisfaccion_acumulada += satisfaccion_año;
        }
        
        // === CALCULAR RESULTADOS FINALES ===
        resultado.valor_residual = valor_actual;
        resultado.costo_total_5_años = auto_opcion.enganche_requerido + 
                                      costo_financiamiento_total +
                                      costo_mantenimiento_total +
                                      costo_combustible_total +
                                      costo_averias_total;
        
        resultado.costo_neto = resultado.costo_total_5_años - resultado.valor_residual;
        resultado.satisfaccion_promedio = satisfaccion_acumulada / años_analisis_;
        resultado.costo_por_km = resultado.costo_neto / (km_por_año_ * años_analisis_);
        resultado.tuvo_averia_mayor = tuvo_averia_mayor;
        
        // Puntuación combinada (menor es mejor para costo, mayor para satisfacción)
        // Normalizar para que sea comparable entre autos
        resultado.puntuacion_total = resultado.satisfaccion_promedio * 10000 - resultado.costo_neto;
        
        return resultado;
    }
    
    std::map<std::string, std::vector<ResultadoSimulacion>> ejecutarSimulacion(int num_simulaciones) {
        std::map<std::string, std::vector<ResultadoSimulacion>> resultados;
        
        std::cout << "🚗 Ejecutando " << num_simulaciones << " simulaciones para " 
                  << opciones_.size() << " opciones de auto...\n\n";
        
        for (const auto& auto_opcion : opciones_) {
            std::cout << "   Simulando: " << auto_opcion.marca_modelo << "..." << std::flush;
            
            std::vector<ResultadoSimulacion> resultados_auto;
            resultados_auto.reserve(num_simulaciones);
            
            for (int i = 0; i < num_simulaciones; ++i) {
                resultados_auto.push_back(simularAuto(auto_opcion));
            }
            
            resultados[auto_opcion.marca_modelo] = std::move(resultados_auto);
            std::cout << " ✅\n";
        }
        
        return resultados;
    }
    
private:
    double calcularPagoMensual(double principal, double tasa_mensual, int meses) {
        if (tasa_mensual == 0) return principal / meses;
        
        double factor = std::pow(1 + tasa_mensual, meses);
        return principal * (tasa_mensual * factor) / (factor - 1);
    }
};

// Función para analizar y comparar resultados
void analizarResultados(const std::map<std::string, std::vector<ResultadoSimulacion>>& resultados) {
    std::cout << "\n" << std::string(80, '=') << "\n";
    std::cout << "📊 ANÁLISIS COMPARATIVO DE RESULTADOS\n";
    std::cout << std::string(80, '=') << "\n\n";
    
    struct EstadisticasAuto {
        std::string nombre;
        double costo_neto_promedio;
        double costo_neto_min;
        double costo_neto_max;
        double satisfaccion_promedio;
        double probabilidad_averia;
        double costo_por_km_promedio;
        double valor_residual_promedio;
        double puntuacion_promedio;
    };
    
    std::vector<EstadisticasAuto> estadisticas;
    
    for (const auto& [nombre_auto, sims] : resultados) {
        EstadisticasAuto stats;
        stats.nombre = nombre_auto;
        
        double suma_costo_neto = 0, suma_satisfaccion = 0, suma_costo_km = 0;
        double suma_valor_residual = 0, suma_puntuacion = 0;
        int count_averias = 0;
        double min_costo = std::numeric_limits<double>::max();
        double max_costo = std::numeric_limits<double>::min();
        
        for (const auto& sim : sims) {
            suma_costo_neto += sim.costo_neto;
            suma_satisfaccion += sim.satisfaccion_promedio;
            suma_costo_km += sim.costo_por_km;
            suma_valor_residual += sim.valor_residual;
            suma_puntuacion += sim.puntuacion_total;
            
            if (sim.tuvo_averia_mayor) count_averias++;
            
            min_costo = std::min(min_costo, sim.costo_neto);
            max_costo = std::max(max_costo, sim.costo_neto);
        }
        
        stats.costo_neto_promedio = suma_costo_neto / sims.size();
        stats.costo_neto_min = min_costo;
        stats.costo_neto_max = max_costo;
        stats.satisfaccion_promedio = suma_satisfaccion / sims.size();
        stats.probabilidad_averia = (double)count_averias / sims.size();
        stats.costo_por_km_promedio = suma_costo_km / sims.size();
        stats.valor_residual_promedio = suma_valor_residual / sims.size();
        stats.puntuacion_promedio = suma_puntuacion / sims.size();
        
        estadisticas.push_back(stats);
    }
    
    // Ordenar por puntuación total (mejor primero)
    std::sort(estadisticas.begin(), estadisticas.end(),
              [](const EstadisticasAuto& a, const EstadisticasAuto& b) {
                  return a.puntuacion_promedio > b.puntuacion_promedio;
              });
    
    // Mostrar resultados detallados
    for (size_t i = 0; i < estadisticas.size(); ++i) {
        const auto& stats = estadisticas[i];
        
        std::cout << "🏆 POSICIÓN #" << (i + 1) << ": " << stats.nombre << "\n";
        std::cout << "   💰 Costo neto promedio: $" << std::fixed << std::setprecision(0) 
                  << stats.costo_neto_promedio << "\n";
        std::cout << "   📊 Rango de costos: $" << stats.costo_neto_min 
                  << " - $" << stats.costo_neto_max << "\n";
        std::cout << "   😊 Satisfacción promedio: " << std::setprecision(1) 
                  << stats.satisfaccion_promedio << "/10\n";
        std::cout << "   🔧 Probabilidad avería mayor: " << std::setprecision(1) 
                  << stats.probabilidad_averia * 100 << "%\n";
        std::cout << "   🛣️  Costo por km: $" << std::setprecision(2) 
                  << stats.costo_por_km_promedio << "\n";
        std::cout << "   💎 Valor residual promedio: $" << std::setprecision(0) 
                  << stats.valor_residual_promedio << "\n";
        std::cout << "   ⭐ Puntuación total: " << std::setprecision(0) 
                  << stats.puntuacion_promedio << "\n\n";
    }
    
    // Recomendación final
    std::cout << "🎯 RECOMENDACIÓN FINAL:\n";
    std::cout << "✅ MEJOR OPCIÓN: " << estadisticas[0].nombre << "\n\n";
    
    std::cout << "📋 CRITERIOS DE DECISIÓN:\n";
    std::cout << "• Si priorizas MENOR COSTO: ";
    auto min_costo_it = std::min_element(estadisticas.begin(), estadisticas.end(),
                                        [](const EstadisticasAuto& a, const EstadisticasAuto& b) {
                                            return a.costo_neto_promedio < b.costo_neto_promedio;
                                        });
    std::cout << min_costo_it->nombre << "\n";
    
    std::cout << "• Si priorizas MAYOR SATISFACCIÓN: ";
    auto max_satisfaccion_it = std::max_element(estadisticas.begin(), estadisticas.end(),
                                               [](const EstadisticasAuto& a, const EstadisticasAuto& b) {
                                                   return a.satisfaccion_promedio < b.satisfaccion_promedio;
                                               });
    std::cout << max_satisfaccion_it->nombre << "\n";
    
    std::cout << "• Si priorizas MENOR RIESGO: ";
    auto min_riesgo_it = std::min_element(estadisticas.begin(), estadisticas.end(),
                                         [](const EstadisticasAuto& a, const EstadisticasAuto& b) {
                                             return a.probabilidad_averia < b.probabilidad_averia;
                                         });
    std::cout << min_riesgo_it->nombre << "\n";
}

int main() {
    std::cout << "🚗 === SIMULACIÓN MONTE CARLO: ¿QUÉ AUTO COMPRAR? === 🚗\n\n";
    
    SimuladorDecisionAuto simulador;
    
    // === DEFINIR OPCIONES DE AUTOS ===
    
    // Opción 1: Auto económico (Nissan Versa)
    Auto versa = {
        "Nissan Versa 2024",
        280000,    // precio inicial
        56000,     // enganche 20%
        0.12,      // tasa de interés anual
        60,        // meses de financiamiento
        0.15,      // depreciación anual media 15%
        0.03,      // variabilidad depreciación
        8000,      // mantenimiento anual base
        2000,      // variabilidad mantenimiento
        7.5,       // consumo L/100km
        1.0,       // variabilidad consumo
        0.08,      // probabilidad avería mayor anual
        15000,     // costo avería mayor promedio
        7.0,       // satisfacción inicial
        0.05       // factor depreciación satisfacción
    };
    
    // Opción 2: Auto intermedio (Honda Civic)
    Auto civic = {
        "Honda Civic 2024",
        420000,    // precio inicial
        84000,     // enganche 20%
        0.10,      // tasa de interés anual (mejor crédito)
        60,        // meses
        0.12,      // depreciación anual media 12%
        0.025,     // variabilidad depreciación
        10000,     // mantenimiento anual base
        2500,      // variabilidad mantenimiento
        6.8,       // consumo L/100km
        0.8,       // variabilidad consumo
        0.05,      // probabilidad avería mayor anual
        20000,     // costo avería mayor promedio
        8.2,       // satisfacción inicial
        0.03       // factor depreciación satisfacción
    };
    
    // Opción 3: Auto premium (BMW Serie 3)
    Auto bmw = {
        "BMW Serie 3 2024",
        850000,    // precio inicial
        170000,    // enganche 20%
        0.08,      // tasa de interés anual (crédito premium)
        60,        // meses
        0.18,      // depreciación anual media 18% (lujo deprecia más)
        0.04,      // variabilidad depreciación
        25000,     // mantenimiento anual base (más caro)
        8000,      // variabilidad mantenimiento (más variable)
        8.5,       // consumo L/100km (motor más potente)
        1.2,       // variabilidad consumo
        0.04,      // probabilidad avería mayor anual (mejor calidad)
        45000,     // costo avería mayor promedio (partes caras)
        9.1,       // satisfacción inicial (alta)
        0.02       // factor depreciación satisfacción (mantiene valor emocional)
    };
    
    // Opción 4: Auto usado confiable (Toyota Corolla 2021)
    Auto corolla_usado = {
        "Toyota Corolla 2021 (Usado)",
        240000,    // precio inicial
        48000,     // enganche 20%
        0.15,      // tasa de interés anual (usado = mayor tasa)
        48,        // meses (menos tiempo)
        0.10,      // depreciación anual media 10% (ya depreció lo fuerte)
        0.02,      // variabilidad depreciación (más predecible)
        12000,     // mantenimiento anual base (3 años de edad)
        3000,      // variabilidad mantenimiento
        6.5,       // consumo L/100km
        0.5,       // variabilidad consumo (motor conocido)
        0.12,      // probabilidad avería mayor anual (mayor edad)
        18000,     // costo avería mayor promedio
        7.5,       // satisfacción inicial
        0.04       // factor depreciación satisfacción
    };
    
    // Agregar todas las opciones
    simulador.agregarOpcion(versa);
    simulador.agregarOpcion(civic);
    simulador.agregarOpcion(bmw);
    simulador.agregarOpcion(corolla_usado);
    
    // === EJECUTAR SIMULACIÓN ===
    const int num_simulaciones = 15000;  // Más simulaciones para mayor precisión
    auto resultados = simulador.ejecutarSimulacion(num_simulaciones);
    
    // === ANALIZAR Y MOSTRAR RESULTADOS ===
    analizarResultados(resultados);
    
    std::cout << "\n💡 CONSIDERACIONES ADICIONALES:\n";
    std::cout << "• Esta simulación considera 5 años de propiedad\n";
    std::cout << "• Incluye incertidumbre en depreciación, mantenimiento y averías\n";
    std::cout << "• Los costos están en pesos mexicanos\n";
    std::cout << "• La satisfacción es subjetiva y puede variar por persona\n";
    std::cout << "• Considera tu situación financiera personal antes de decidir\n\n";
    
    std::cout << "🎉 ¡Simulación completada! Usa estos datos para tomar una decisión informada.\n";
    
    return 0;
}