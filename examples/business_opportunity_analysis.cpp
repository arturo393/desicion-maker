#include <iostream>
#include <random>
#include <vector>
#include <string>
#include <iomanip>
#include <algorithm>
#include <map>

/**
 * @brief Simulación Monte Carlo: ¿Qué oportunidad de negocio automatizado elegir?
 * 
 * Escenario: Comparar 4 ideas de negocio automatizado considerando:
 * - Inversión inicial (tiempo y capital)
 * - Potencial de ingresos mensuales
 * - Tiempo de setup (hasta generar primer ingreso)
 * - Nivel de automatización real (% de tiempo libre después)
 * - Escalabilidad (crecimiento potencial)
 * - Riesgo de fracaso
 * - Satisfacción personal (alineación con intereses)
 * - Costos operativos mensuales
 */

struct OportunidadNegocio {
    std::string nombre;
    
    // Inversión inicial
    double capital_inicial_usd;          // Capital en dólares
    double horas_setup_inicial;          // Horas de trabajo para MVP
    
    // Ingresos potenciales (distribución incierta)
    double ingreso_mensual_medio;        // Ingreso promedio esperado/mes
    double ingreso_mensual_std;          // Desviación estándar
    double ingreso_mensual_min;          // Piso realista
    double ingreso_mensual_max;          // Techo optimista
    
    // Tiempo hasta primer ingreso
    double meses_hasta_primer_ingreso_media;
    double meses_hasta_primer_ingreso_std;
    
    // Nivel de automatización (0-1, donde 1 = 100% automático)
    double nivel_automatizacion_inicial;  // Al inicio
    double nivel_automatizacion_6_meses;  // Después de 6 meses
    double nivel_automatizacion_12_meses; // Después de 1 año
    
    // Escalabilidad (factor de crecimiento mensual)
    double factor_crecimiento_mensual;    // Ej: 1.05 = 5% crecimiento/mes
    double variabilidad_crecimiento;      // Incertidumbre en crecimiento
    
    // Riesgos
    double probabilidad_fracaso_total;    // % de que no funcione
    double probabilidad_pivote;           // % de necesitar cambio grande
    
    // Costos operativos
    double costo_mensual_medio;           // Hosting, APIs, etc.
    double costo_mensual_std;
    
    // Satisfacción personal (1-10)
    double satisfaccion_inicial;          // Alineación con intereses
    double factor_burnout;                // Qué tan rápido decrece si no automatiza
    
    // Uso de GitHub Copilot (acelera desarrollo)
    double factor_aceleracion_copilot;    // Ej: 1.5 = 50% más rápido
};

struct ResultadoSimulacion {
    std::string nombre_negocio;
    
    // Métricas financieras (12 meses)
    double ingreso_total_12_meses;
    double costo_total_12_meses;
    double ganancia_neta_12_meses;
    double roi_12_meses;                  // Return on Investment
    
    // Métricas de tiempo
    double horas_trabajadas_total;
    double horas_libres_generadas;        // Tiempo automatizado
    double meses_hasta_breakeven;         // Recuperar inversión
    
    // Métricas de éxito
    bool negocio_exitoso;                 // ¿Llegó a ser rentable?
    bool requirio_pivote;                 // ¿Necesitó cambio de estrategia?
    double nivel_automatizacion_final;    // % automatización a 12 meses
    
    // Satisfacción
    double satisfaccion_promedio;
    
    // Puntuación combinada (normalizada)
    double puntuacion_total;
};

class SimuladorDecisionNegocio {
private:
    std::vector<OportunidadNegocio> oportunidades_;
    std::mt19937 gen_;
    const int meses_analisis_ = 12;       // Analizar primer año
    const double horas_semana_disponibles_ = 20;  // Tiempo disponible
    
public:
    SimuladorDecisionNegocio() : gen_(std::random_device{}()) {}
    
    void agregarOportunidad(const OportunidadNegocio& oportunidad) {
        oportunidades_.push_back(oportunidad);
    }
    
    ResultadoSimulacion simularNegocio(const OportunidadNegocio& oportunidad) {
        ResultadoSimulacion resultado;
        resultado.nombre_negocio = oportunidad.nombre;
        
        // Distribuciones para modelar incertidumbre
        std::uniform_real_distribution<double> dist_uniforme(0.0, 1.0);
        
        // Verificar fracaso total (ocurre al inicio)
        if (dist_uniforme(gen_) < oportunidad.probabilidad_fracaso_total) {
            // Negocio fracasa completamente
            resultado.negocio_exitoso = false;
            resultado.ingreso_total_12_meses = 0.0;
            resultado.costo_total_12_meses = oportunidad.capital_inicial_usd;
            resultado.ganancia_neta_12_meses = -oportunidad.capital_inicial_usd;
            resultado.roi_12_meses = -100.0;
            resultado.horas_trabajadas_total = oportunidad.horas_setup_inicial;
            resultado.horas_libres_generadas = 0.0;
            resultado.meses_hasta_breakeven = 999.0;
            resultado.requirio_pivote = false;
            resultado.nivel_automatizacion_final = 0.0;
            resultado.satisfaccion_promedio = 2.0;  // Frustración
            resultado.puntuacion_total = -10000.0;
            return resultado;
        }
        
        // Setup inicial (acelerado por Copilot)
        double horas_setup_real = oportunidad.horas_setup_inicial / 
                                  oportunidad.factor_aceleracion_copilot;
        
        // Tiempo hasta primer ingreso
        std::normal_distribution<double> dist_tiempo_ingreso(
            oportunidad.meses_hasta_primer_ingreso_media,
            oportunidad.meses_hasta_primer_ingreso_std
        );
        int mes_primer_ingreso = std::max(1, (int)dist_tiempo_ingreso(gen_));
        mes_primer_ingreso = std::min(mes_primer_ingreso, 12);  // Máximo 12 meses
        
        // Verificar si requiere pivote
        bool requirio_pivote = dist_uniforme(gen_) < oportunidad.probabilidad_pivote;
        if (requirio_pivote) {
            mes_primer_ingreso += 2;  // Retraso por pivote
            horas_setup_real *= 1.3;  // 30% más trabajo
        }
        resultado.requirio_pivote = requirio_pivote;
        
        // === SIMULAR MES POR MES ===
        double ingreso_acumulado = 0.0;
        double costo_acumulado = oportunidad.capital_inicial_usd;
        double horas_trabajadas_acumuladas = horas_setup_real;
        double satisfaccion_acumulada = 0.0;
        double ingreso_mensual_actual = 0.0;
        
        for (int mes = 1; mes <= meses_analisis_; ++mes) {
            // Calcular nivel de automatización para este mes
            double nivel_auto = interpolarAutomatizacion(
                oportunidad, mes, mes_primer_ingreso
            );
            
            // Horas de trabajo necesarias este mes
            double horas_mes = horas_semana_disponibles_ * 4.0 * (1.0 - nivel_auto);
            horas_trabajadas_acumuladas += horas_mes;
            
            // Ingresos (solo después del primer ingreso)
            if (mes >= mes_primer_ingreso) {
                if (mes == mes_primer_ingreso) {
                    // Primer ingreso (más conservador)
                    std::normal_distribution<double> dist_ingreso(
                        oportunidad.ingreso_mensual_medio * 0.3,  // 30% del promedio
                        oportunidad.ingreso_mensual_std * 0.5
                    );
                    ingreso_mensual_actual = std::max(
                        oportunidad.ingreso_mensual_min,
                        std::min(oportunidad.ingreso_mensual_max * 0.3, 
                                dist_ingreso(gen_))
                    );
                } else {
                    // Crecimiento mensual con variabilidad
                    std::normal_distribution<double> dist_crecimiento(
                        oportunidad.factor_crecimiento_mensual,
                        oportunidad.variabilidad_crecimiento
                    );
                    double factor = std::max(0.9, std::min(1.3, dist_crecimiento(gen_)));
                    ingreso_mensual_actual *= factor;
                    
                    // Limitar al rango realista
                    ingreso_mensual_actual = std::max(
                        oportunidad.ingreso_mensual_min,
                        std::min(oportunidad.ingreso_mensual_max, ingreso_mensual_actual)
                    );
                }
                
                ingreso_acumulado += ingreso_mensual_actual;
            }
            
            // Costos operativos
            std::normal_distribution<double> dist_costo(
                oportunidad.costo_mensual_medio,
                oportunidad.costo_mensual_std
            );
            double costo_mes = std::max(0.0, dist_costo(gen_));
            costo_acumulado += costo_mes;
            
            // Satisfacción (decrece si no automatiza lo suficiente)
            double satisfaccion_mes = oportunidad.satisfaccion_inicial *
                (1.0 - oportunidad.factor_burnout * (1.0 - nivel_auto) * (mes / 12.0));
            satisfaccion_mes = std::max(1.0, satisfaccion_mes);
            satisfaccion_acumulada += satisfaccion_mes;
        }
        
        // === CALCULAR RESULTADOS FINALES ===
        resultado.negocio_exitoso = ingreso_acumulado > costo_acumulado;
        resultado.ingreso_total_12_meses = ingreso_acumulado;
        resultado.costo_total_12_meses = costo_acumulado;
        resultado.ganancia_neta_12_meses = ingreso_acumulado - costo_acumulado;
        
        if (oportunidad.capital_inicial_usd > 0) {
            resultado.roi_12_meses = (resultado.ganancia_neta_12_meses / 
                                     oportunidad.capital_inicial_usd) * 100.0;
        } else {
            resultado.roi_12_meses = resultado.ganancia_neta_12_meses > 0 ? 999.0 : -100.0;
        }
        
        resultado.horas_trabajadas_total = horas_trabajadas_acumuladas;
        
        // Horas libres = horas que se automatizaron
        double horas_totales_posibles = horas_semana_disponibles_ * 4.0 * meses_analisis_;
        resultado.horas_libres_generadas = horas_totales_posibles - 
                                          (horas_trabajadas_acumuladas - horas_setup_real);
        
        // Meses hasta breakeven
        resultado.meses_hasta_breakeven = calcularBreakeven(
            oportunidad, mes_primer_ingreso, ingreso_mensual_actual
        );
        
        resultado.nivel_automatizacion_final = interpolarAutomatizacion(
            oportunidad, 12, mes_primer_ingreso
        );
        
        resultado.satisfaccion_promedio = satisfaccion_acumulada / meses_analisis_;
        
        // Puntuación total (normalizada para comparar)
        // Prioriza: ganancia, automatización, satisfacción
        resultado.puntuacion_total = 
            resultado.ganancia_neta_12_meses * 0.4 +                    // 40% peso en ganancia
            resultado.nivel_automatizacion_final * 10000 * 0.3 +        // 30% peso en automatización
            resultado.satisfaccion_promedio * 1000 * 0.2 +              // 20% peso en satisfacción
            (resultado.negocio_exitoso ? 5000 : -5000) * 0.1;          // 10% peso en éxito
        
        return resultado;
    }
    
    std::map<std::string, std::vector<ResultadoSimulacion>> ejecutarSimulacion(int num_simulaciones) {
        std::map<std::string, std::vector<ResultadoSimulacion>> resultados;
        
        std::cout << "🚀 Ejecutando " << num_simulaciones << " simulaciones para " 
                  << oportunidades_.size() << " oportunidades de negocio...\n\n";
        
        for (const auto& oportunidad : oportunidades_) {
            std::cout << "   Simulando: " << oportunidad.nombre << "..." << std::flush;
            
            std::vector<ResultadoSimulacion> resultados_negocio;
            resultados_negocio.reserve(num_simulaciones);
            
            for (int i = 0; i < num_simulaciones; ++i) {
                resultados_negocio.push_back(simularNegocio(oportunidad));
            }
            
            resultados[oportunidad.nombre] = std::move(resultados_negocio);
            std::cout << " ✅\n";
        }
        
        return resultados;
    }
    
private:
    double interpolarAutomatizacion(const OportunidadNegocio& opp, 
                                    int mes_actual, 
                                    int mes_primer_ingreso) const {
        if (mes_actual < mes_primer_ingreso) {
            return opp.nivel_automatizacion_inicial;
        } else if (mes_actual < 6) {
            // Interpolar entre inicial y 6 meses
            double t = (mes_actual - mes_primer_ingreso) / (6.0 - mes_primer_ingreso);
            return opp.nivel_automatizacion_inicial + 
                   t * (opp.nivel_automatizacion_6_meses - opp.nivel_automatizacion_inicial);
        } else if (mes_actual < 12) {
            // Interpolar entre 6 y 12 meses
            double t = (mes_actual - 6) / 6.0;
            return opp.nivel_automatizacion_6_meses + 
                   t * (opp.nivel_automatizacion_12_meses - opp.nivel_automatizacion_6_meses);
        } else {
            return opp.nivel_automatizacion_12_meses;
        }
    }
    
    double calcularBreakeven(const OportunidadNegocio& opp,
                            int mes_primer_ingreso,
                            double ingreso_mensual_final) const {
        double costo_total = opp.capital_inicial_usd;
        double ingreso_acumulado = 0.0;
        
        if (ingreso_mensual_final <= opp.costo_mensual_medio) {
            return 999.0;  // Nunca alcanza breakeven
        }
        
        // Estimación simplificada
        double ingreso_neto_mensual = ingreso_mensual_final - opp.costo_mensual_medio;
        double meses = mes_primer_ingreso + (costo_total / ingreso_neto_mensual);
        
        return std::min(999.0, meses);
    }
};

// Función para analizar y comparar resultados
void analizarResultados(const std::map<std::string, std::vector<ResultadoSimulacion>>& resultados) {
    std::cout << "\n" << std::string(90, '=') << "\n";
    std::cout << "📊 ANÁLISIS COMPARATIVO: ¿QUÉ OPORTUNIDAD DE NEGOCIO ELEGIR?\n";
    std::cout << std::string(90, '=') << "\n\n";
    
    struct EstadisticasNegocio {
        std::string nombre;
        double ganancia_neta_promedio;
        double ganancia_neta_percentil_25;
        double ganancia_neta_percentil_75;
        double roi_promedio;
        double probabilidad_exito;
        double nivel_automatizacion_promedio;
        double satisfaccion_promedio;
        double meses_breakeven_promedio;
        double horas_libres_promedio;
        double puntuacion_promedio;
    };
    
    std::vector<EstadisticasNegocio> estadisticas;
    
    for (const auto& [nombre_negocio, sims] : resultados) {
        EstadisticasNegocio stats;
        stats.nombre = nombre_negocio;
        
        std::vector<double> ganancias;
        double suma_roi = 0, suma_auto = 0, suma_satisfaccion = 0;
        double suma_breakeven = 0, suma_horas_libres = 0, suma_puntuacion = 0;
        int count_exito = 0;
        
        for (const auto& sim : sims) {
            ganancias.push_back(sim.ganancia_neta_12_meses);
            suma_roi += sim.roi_12_meses;
            suma_auto += sim.nivel_automatizacion_final;
            suma_satisfaccion += sim.satisfaccion_promedio;
            suma_breakeven += sim.meses_hasta_breakeven;
            suma_horas_libres += sim.horas_libres_generadas;
            suma_puntuacion += sim.puntuacion_total;
            
            if (sim.negocio_exitoso) count_exito++;
        }
        
        // Calcular percentiles
        std::sort(ganancias.begin(), ganancias.end());
        size_t idx_25 = ganancias.size() / 4;
        size_t idx_75 = (ganancias.size() * 3) / 4;
        
        stats.ganancia_neta_promedio = std::accumulate(ganancias.begin(), ganancias.end(), 0.0) / ganancias.size();
        stats.ganancia_neta_percentil_25 = ganancias[idx_25];
        stats.ganancia_neta_percentil_75 = ganancias[idx_75];
        stats.roi_promedio = suma_roi / sims.size();
        stats.probabilidad_exito = (double)count_exito / sims.size();
        stats.nivel_automatizacion_promedio = suma_auto / sims.size();
        stats.satisfaccion_promedio = suma_satisfaccion / sims.size();
        stats.meses_breakeven_promedio = suma_breakeven / sims.size();
        stats.horas_libres_promedio = suma_horas_libres / sims.size();
        stats.puntuacion_promedio = suma_puntuacion / sims.size();
        
        estadisticas.push_back(stats);
    }
    
    // Ordenar por puntuación total
    std::sort(estadisticas.begin(), estadisticas.end(),
              [](const EstadisticasNegocio& a, const EstadisticasNegocio& b) {
                  return a.puntuacion_promedio > b.puntuacion_promedio;
              });
    
    // Mostrar resultados detallados
    for (size_t i = 0; i < estadisticas.size(); ++i) {
        const auto& stats = estadisticas[i];
        
        std::cout << "🏆 POSICIÓN #" << (i + 1) << ": " << stats.nombre << "\n";
        std::cout << "   💰 Ganancia neta promedio (12 meses): $" << std::fixed << std::setprecision(0) 
                  << stats.ganancia_neta_promedio << " USD\n";
        std::cout << "   📊 Rango de ganancias (P25-P75): $" << stats.ganancia_neta_percentil_25
                  << " - $" << stats.ganancia_neta_percentil_75 << " USD\n";
        std::cout << "   📈 ROI promedio: " << std::setprecision(1) << stats.roi_promedio << "%\n";
        std::cout << "   ✅ Probabilidad de éxito: " << std::setprecision(1) 
                  << stats.probabilidad_exito * 100 << "%\n";
        std::cout << "   🤖 Nivel de automatización: " << std::setprecision(1) 
                  << stats.nivel_automatizacion_promedio * 100 << "%\n";
        std::cout << "   😊 Satisfacción promedio: " << std::setprecision(1) 
                  << stats.satisfaccion_promedio << "/10\n";
        std::cout << "   ⏰ Meses hasta breakeven: " << std::setprecision(1) 
                  << stats.meses_breakeven_promedio << " meses\n";
        std::cout << "   🆓 Horas libres generadas: " << std::setprecision(0) 
                  << stats.horas_libres_promedio << " horas/año\n";
        std::cout << "   ⭐ Puntuación total: " << std::setprecision(0) 
                  << stats.puntuacion_promedio << "\n\n";
    }
    
    // Recomendación final
    std::cout << "🎯 RECOMENDACIÓN FINAL BASADA EN DATOS:\n";
    std::cout << "✅ MEJOR OPCIÓN GENERAL: " << estadisticas[0].nombre << "\n\n";
    
    std::cout << "📋 ANÁLISIS POR CRITERIO:\n";
    
    auto max_ganancia = std::max_element(estadisticas.begin(), estadisticas.end(),
        [](const EstadisticasNegocio& a, const EstadisticasNegocio& b) {
            return a.ganancia_neta_promedio < b.ganancia_neta_promedio;
        });
    std::cout << "• Mayor ganancia potencial: " << max_ganancia->nombre << "\n";
    
    auto max_auto = std::max_element(estadisticas.begin(), estadisticas.end(),
        [](const EstadisticasNegocio& a, const EstadisticasNegocio& b) {
            return a.nivel_automatizacion_promedio < b.nivel_automatizacion_promedio;
        });
    std::cout << "• Mayor automatización: " << max_auto->nombre << "\n";
    
    auto max_satisfaccion = std::max_element(estadisticas.begin(), estadisticas.end(),
        [](const EstadisticasNegocio& a, const EstadisticasNegocio& b) {
            return a.satisfaccion_promedio < b.satisfaccion_promedio;
        });
    std::cout << "• Mayor satisfacción: " << max_satisfaccion->nombre << "\n";
    
    auto min_riesgo = std::max_element(estadisticas.begin(), estadisticas.end(),
        [](const EstadisticasNegocio& a, const EstadisticasNegocio& b) {
            return a.probabilidad_exito < b.probabilidad_exito;
        });
    std::cout << "• Menor riesgo: " << min_riesgo->nombre << "\n";
}

int main() {
    std::cout << "🚀 === ANÁLISIS MONTE CARLO: OPORTUNIDADES DE NEGOCIO AUTOMATIZADO === 🚀\n\n";
    
    SimuladorDecisionNegocio simulador;
    
    // === DEFINIR LAS 4 OPORTUNIDADES DE NEGOCIO ===
    
    // Idea 1: Bot de Arbitraje Cripto
    OportunidadNegocio bot_arbitraje = {
        "Bot Arbitraje Cripto",
        200,        // $200 capital inicial (para pruebas en exchanges)
        40,         // 40 horas setup (script + testing)
        300,        // $300/mes ingreso medio
        150,        // $150 desviación estándar
        50,         // $50 mínimo
        1000,       // $1000 máximo (con más capital)
        2.5,        // 2.5 meses hasta primer ingreso
        0.8,        // Desviación 0.8 meses
        0.70,       // 70% automatizado inicial
        0.85,       // 85% a los 6 meses
        0.95,       // 95% al año (casi totalmente automático)
        1.08,       // 8% crecimiento mensual (con reinversión)
        0.03,       // 3% variabilidad
        0.25,       // 25% probabilidad fracaso (mercado volátil)
        0.15,       // 15% probabilidad pivote
        30,         // $30/mes costos (cloud, APIs)
        10,         // $10 std
        8.5,        // 8.5/10 satisfacción (trading + coding)
        0.15,       // Factor burnout medio
        1.6         // Copilot acelera 60%
    };
    
    // Idea 2: Servicio de Análisis de Datos de Mercado
    OportunidadNegocio analisis_datos = {
        "Análisis Datos Mercado (SaaS)",
        50,         // $50 capital inicial (hosting)
        60,         // 60 horas setup (scraping + dashboard)
        200,        // $200/mes ingreso medio
        100,        // $100 std
        20,         // $20 mínimo
        800,        // $800 máximo
        3.5,        // 3.5 meses hasta primer ingreso
        1.0,        // 1 mes desviación
        0.60,       // 60% automatizado inicial
        0.75,       // 75% a 6 meses
        0.85,       // 85% al año
        1.12,       // 12% crecimiento mensual (marketing boca a boca)
        0.05,       // 5% variabilidad
        0.30,       // 30% probabilidad fracaso
        0.20,       // 20% probabilidad pivote
        20,         // $20/mes costos
        5,          // $5 std
        7.5,        // 7.5/10 satisfacción (investigación + tech)
        0.20,       // Factor burnout medio-alto
        1.7         // Copilot acelera 70%
    };
    
    // Idea 3: Generador de Alertas de Trading
    OportunidadNegocio alertas_trading = {
        "Alertas Trading (Suscripción)",
        70,         // $70 capital inicial (Twilio + APIs)
        30,         // 30 horas setup (más simple)
        150,        // $150/mes ingreso medio
        80,         // $80 std
        30,         // $30 mínimo
        500,        // $500 máximo
        2.0,        // 2 meses hasta primer ingreso (más rápido)
        0.5,        // 0.5 mes desviación
        0.80,       // 80% automatizado inicial (muy automático)
        0.90,       // 90% a 6 meses
        0.95,       // 95% al año
        1.06,       // 6% crecimiento mensual
        0.04,       // 4% variabilidad
        0.20,       // 20% probabilidad fracaso (nicho validado)
        0.10,       // 10% probabilidad pivote
        25,         // $25/mes costos (SMS + APIs)
        8,          // $8 std
        8.0,        // 8/10 satisfacción (trading directo)
        0.10,       // Factor burnout bajo
        1.5         // Copilot acelera 50%
    };
    
    // Idea 4: Monitor de Yield Farming DeFi
    OportunidadNegocio yield_farming = {
        "Monitor Yield Farming DeFi",
        30,         // $30 capital inicial (hosting cloud)
        50,         // 50 horas setup
        180,        // $180/mes ingreso medio
        90,         // $90 std
        25,         // $25 mínimo
        600,        // $600 máximo
        3.0,        // 3 meses hasta primer ingreso
        0.8,        // 0.8 mes desviación
        0.65,       // 65% automatizado inicial
        0.80,       // 80% a 6 meses
        0.90,       // 90% al año
        1.10,       // 10% crecimiento mensual (nicho DeFi crece)
        0.06,       // 6% variabilidad
        0.28,       // 28% probabilidad fracaso
        0.18,       // 18% probabilidad pivote
        15,         // $15/mes costos (APIs gratis)
        5,          // $5 std
        9.0,        // 9/10 satisfacción (DeFi + research)
        0.12,       // Factor burnout bajo-medio
        1.8         // Copilot acelera 80% (blockchain complejo)
    };
    
    // Agregar todas las oportunidades
    simulador.agregarOportunidad(bot_arbitraje);
    simulador.agregarOportunidad(analisis_datos);
    simulador.agregarOportunidad(alertas_trading);
    simulador.agregarOportunidad(yield_farming);
    
    // === EJECUTAR SIMULACIÓN ===
    const int num_simulaciones = 10000;
    auto resultados = simulador.ejecutarSimulacion(num_simulaciones);
    
    // === ANALIZAR Y MOSTRAR RESULTADOS ===
    analizarResultados(resultados);
    
    std::cout << "\n💡 CONSIDERACIONES FINALES:\n";
    std::cout << "• Esta simulación considera 12 meses de operación\n";
    std::cout << "• Incluye incertidumbre en ingresos, costos y tiempo\n";
    std::cout << "• El factor GitHub Copilot ($10/mes) acelera el desarrollo\n";
    std::cout << "• Prioriza automatización para mínima intervención\n";
    std::cout << "• Considera tu capital disponible y tolerancia al riesgo\n\n";
    
    std::cout << "🎯 PRÓXIMOS PASOS SUGERIDOS:\n";
    std::cout << "1. Valida la idea ganadora con un landing page\n";
    std::cout << "2. Habla con 5-10 usuarios potenciales\n";
    std::cout << "3. Construye un MVP en 2-3 semanas\n";
    std::cout << "4. Lanza en comunidades de trading/DeFi\n";
    std::cout << "5. Itera basado en feedback real\n\n";
    
    std::cout << "🎉 ¡Decisión basada en 10,000 escenarios simulados!\n";
    
    return 0;
}
