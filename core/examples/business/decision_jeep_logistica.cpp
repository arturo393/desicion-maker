// SIMULACIÓN MONTE CARLO: Decisión logística Jeep Compass
// Arturo vive en Santiago con familia (niños), trabaja en Con Con Lun-Mie
// Sale lunes 5:30am, regresa miércoles tarde
// Auto es CRÍTICO: familia lo usa para llevar niños al colegio
// Sin auto: viaja domingo tarde (pierde tiempo familiar) + duerme en casa suegros
// Opciones: Risky Run, Correct Fix, Tow, Commuter, Esperar
// 
// INCERTIDUMBRES SIMULADAS:
// - ¿Jefe aprueba permiso? (probabilidad)
// - ¿Correa se sale en viaje? (probabilidad)
// - ¿Compresor listo a tiempo? (probabilidad)
// - Tiempo extra perdido (variabilidad)

#include <iostream>
#include <vector>
#include <string>
#include <iomanip>
#include <random>
#include <algorithm>
#include <numeric>

// Resultado de UNA simulación de una opción
struct ResultadoSimulacion {
    bool exito;                 // ¿Funcionó la opción?
    double costo_total;         // Costo real final (puede variar)
    double costo_total_4semanas; // Costo proyectado a 4 semanas
    double tiempo_perdido;      // Horas perdidas reales por semana
    double tiempo_total_4semanas; // Tiempo perdido proyectado a 4 semanas
    double estres_final;        // Nivel de estrés experimentado
    bool conflicto_laboral;     // ¿Hubo problema con jefe?
    bool problema_mecanico;     // ¿Hubo falla mecánica?
    bool emergencia_familiar;   // ¿Suzuki Alto falló?
    double carga_mental;        // Costo cognitivo de estar pendiente
    double puntuacion;          // Score final de esta simulación
    double puntuacion_4semanas; // Score ajustado por tiempo
};

// Parámetros de incertidumbre para cada opción
struct OpcionIncertidumbre {
    std::string nombre;
    std::string descripcion;
    
    // Probabilidades de eventos
    double prob_jefe_rechaza;      // Probabilidad que jefe diga NO
    double prob_falla_mecanica;    // Probabilidad de problema en ruta/reparación
    double prob_retraso;           // Probabilidad de retrasos
    double prob_emergencia_familiar; // Probabilidad que Suzuki Alto falle (POR SEMANA)
    
    // Costos (pueden variar)
    double costo_base;
    double costo_std;              // Desviación estándar
    bool costo_recurrente;         // ¿Se repite semanalmente?
    int semanas_duracion;          // Cuántas semanas dura esta opción
    
    // Tiempo (puede variar)
    double tiempo_base;
    double tiempo_std;
    bool tiempo_recurrente;        // ¿Se repite semanalmente?
    
    // Carga mental
    double carga_mental_base;      // Estrés cognitivo de estar pendiente
    
    // Valores fijos
    double seguridad_base;
    double logistica_familiar;
    double comodidad;
};

// Simular UNA ejecución de una opción con incertidumbre
ResultadoSimulacion simularOpcion(
    const OpcionIncertidumbre& opcion,
    std::mt19937& gen
) {
    ResultadoSimulacion resultado;
    
    // Distribuciones para variables aleatorias
    std::uniform_real_distribution<double> prob_dist(0.0, 1.0);
    std::normal_distribution<double> costo_dist(opcion.costo_base, opcion.costo_std);
    std::normal_distribution<double> tiempo_dist(opcion.tiempo_base, opcion.tiempo_std);
    
    // 1. ¿Jefe rechaza permiso?
    double roll_jefe = prob_dist(gen);
    resultado.conflicto_laboral = (roll_jefe < opcion.prob_jefe_rechaza);
    
    // 2. ¿Hay falla mecánica?
    double roll_mecanico = prob_dist(gen);
    resultado.problema_mecanico = (roll_mecanico < opcion.prob_falla_mecanica);
    
    // 3. Calcular costo real (con variabilidad)
    resultado.costo_total = std::max(0.0, costo_dist(gen));
    
    // 3b. Proyectar costo a 4 semanas (si es recurrente)
    if (opcion.costo_recurrente) {
        resultado.costo_total_4semanas = resultado.costo_total * opcion.semanas_duracion;
    } else {
        resultado.costo_total_4semanas = resultado.costo_total; // Costo único
    }
    
    // 4. Calcular tiempo perdido real (con variabilidad)
    resultado.tiempo_perdido = std::max(0.0, tiempo_dist(gen));
    
    // 4b. Proyectar tiempo a 4 semanas (si es recurrente)
    if (opcion.tiempo_recurrente) {
        resultado.tiempo_total_4semanas = resultado.tiempo_perdido * opcion.semanas_duracion;
    } else {
        resultado.tiempo_total_4semanas = resultado.tiempo_perdido; // Tiempo único
    }
    
    // 5. Calcular estrés (ALTO BASE: 4 años sin vacaciones, muy estresado)
    resultado.estres_final = 0.70; // Base ALTA (ya estás muy estresado)
    if (resultado.conflicto_laboral) {
        resultado.estres_final += 0.25; // Rechazo jefe dispara estrés
        // EFECTO CASCADA: Estrés alto → más probabilidad de conflictos
        if (resultado.estres_final > 0.85) {
            // Si estrés > 85%, aumenta prob de más problemas
            if (prob_dist(gen) < 0.20) {
                resultado.problema_mecanico = true; // Errores por estrés
            }
        }
    }
    if (resultado.problema_mecanico) resultado.estres_final += 0.20;
    resultado.estres_final = std::min(1.0, resultado.estres_final);
    
    // 5b. Emergencia familiar: ¿Suzuki Alto falla durante estas semanas?
    resultado.emergencia_familiar = false;
    for (int sem = 0; sem < opcion.semanas_duracion; ++sem) {
        if (prob_dist(gen) < opcion.prob_emergencia_familiar) {
            resultado.emergencia_familiar = true;
            resultado.estres_final += 0.30; // CRISIS TOTAL
            resultado.tiempo_perdido += 8.0; // +8h resolviendo emergencia
            resultado.costo_total += 50000; // Uber/taxi emergencia
            break;
        }
    }
    
    // 5c. Carga mental de estar pendiente
    resultado.carga_mental = opcion.carga_mental_base;
    if (opcion.prob_falla_mecanica > 0.20) {
        resultado.carga_mental += 0.15; // Más ansiedad si hay riesgo alto
    }
    resultado.estres_final = std::min(1.0, resultado.estres_final + resultado.carga_mental * 0.3);
    
    // 6. Determinar si la opción TUVO ÉXITO
    resultado.exito = !resultado.conflicto_laboral && 
                      !resultado.problema_mecanico && 
                      !resultado.emergencia_familiar;
    
    // 7. Calcular puntuación final (CORTO PLAZO: 1 semana)
    double score_tiempo = 1.0 - (resultado.tiempo_perdido / 20.0);
    double score_costo = resultado.costo_total / 300000.0;
    
    // AJUSTE: Riesgo laboral ahora pesa MENOS (ya quieres irte del trabajo)
    resultado.puntuacion = 
        0.25 * opcion.seguridad_base +
        0.25 * opcion.logistica_familiar +  // ↑ MÁS PESO (familia crítica)
        0.20 * score_tiempo +                // ↑ MÁS PESO (tiempo con familia)
        0.10 * opcion.comodidad +
        0.05 * (resultado.conflicto_laboral ? 0.0 : 1.0) + // ↓ MENOS PESO (ya no importa tanto)
        0.02 * (resultado.conflicto_laboral ? 0.0 : 1.0) + // ↓ MENOS PESO
        0.15 * (1.0 - resultado.estres_final) - // ↑ MÁS PESO (ya estás muy estresado)
        0.08 * score_costo -
        0.10 * resultado.carga_mental; // NUEVO: penaliza estar pendiente
    
    resultado.puntuacion = std::max(0.0, std::min(1.0, resultado.puntuacion));
    
    // Si hay falla mecánica crítica, penalizar
    if (resultado.problema_mecanico && opcion.seguridad_base < 0.5) {
        resultado.puntuacion *= 0.3;
    }
    
    // Si hay emergencia familiar (Suzuki falla), penalizar FUERTE
    if (resultado.emergencia_familiar) {
        resultado.puntuacion *= 0.4; // -60% por crisis familiar
    }
    
    // 8. Calcular puntuación LARGO PLAZO (4 semanas)
    double score_tiempo_4sem = 1.0 - (resultado.tiempo_total_4semanas / 80.0); // 80h = 20h/sem * 4
    double score_costo_4sem = resultado.costo_total_4semanas / 300000.0;
    
    resultado.puntuacion_4semanas = 
        0.25 * opcion.seguridad_base +
        0.25 * opcion.logistica_familiar +  // ↑ MÁS PESO
        0.20 * score_tiempo_4sem +          // ↑ MÁS PESO
        0.10 * opcion.comodidad +
        0.05 * (resultado.conflicto_laboral ? 0.0 : 1.0) + // ↓ MENOS PESO
        0.02 * (resultado.conflicto_laboral ? 0.0 : 1.0) + // ↓ MENOS PESO
        0.15 * (1.0 - resultado.estres_final) - // ↑ MÁS PESO
        0.08 * score_costo_4sem -
        0.10 * resultado.carga_mental; // NUEVO
    
    resultado.puntuacion_4semanas = std::max(0.0, std::min(1.0, resultado.puntuacion_4semanas));
    
    if (resultado.problema_mecanico && opcion.seguridad_base < 0.5) {
        resultado.puntuacion_4semanas *= 0.3;
    }
    
    if (resultado.emergencia_familiar) {
        resultado.puntuacion_4semanas *= 0.4; // -60% por crisis familiar
    }
    
    return resultado;
}

// Calcular estadísticas de N simulaciones
struct EstadisticasOpcion {
    std::string nombre;
    int total_simulaciones;
    int simulaciones_exitosas;
    double prob_exito;
    double score_promedio;
    double score_promedio_4semanas; // Score a largo plazo
    double score_p25;
    double score_p50;
    double score_p75;
    double costo_promedio;
    double costo_promedio_4semanas; // Costo acumulado
    double tiempo_perdido_promedio;
    double tiempo_perdido_4semanas; // Tiempo acumulado
};

EstadisticasOpcion calcularEstadisticas(
    const std::string& nombre,
    const std::vector<ResultadoSimulacion>& resultados
) {
    EstadisticasOpcion stats;
    stats.nombre = nombre;
    stats.total_simulaciones = resultados.size();
    stats.simulaciones_exitosas = 0;
    
    double suma_score = 0;
    double suma_score_4sem = 0;
    double suma_costo = 0;
    double suma_costo_4sem = 0;
    double suma_tiempo = 0;
    double suma_tiempo_4sem = 0;
    std::vector<double> scores;
    
    for (const auto& r : resultados) {
        if (r.exito) stats.simulaciones_exitosas++;
        suma_score += r.puntuacion;
        suma_score_4sem += r.puntuacion_4semanas;
        suma_costo += r.costo_total;
        suma_costo_4sem += r.costo_total_4semanas;
        suma_tiempo += r.tiempo_perdido;
        suma_tiempo_4sem += r.tiempo_total_4semanas;
        scores.push_back(r.puntuacion);
    }
    
    stats.prob_exito = (double)stats.simulaciones_exitosas / stats.total_simulaciones;
    stats.score_promedio = suma_score / stats.total_simulaciones;
    stats.score_promedio_4semanas = suma_score_4sem / stats.total_simulaciones;
    stats.costo_promedio = suma_costo / stats.total_simulaciones;
    stats.costo_promedio_4semanas = suma_costo_4sem / stats.total_simulaciones;
    stats.tiempo_perdido_promedio = suma_tiempo / stats.total_simulaciones;
    stats.tiempo_perdido_4semanas = suma_tiempo_4sem / stats.total_simulaciones;
    
    // Calcular percentiles
    std::sort(scores.begin(), scores.end());
    stats.score_p25 = scores[stats.total_simulaciones / 4];
    stats.score_p50 = scores[stats.total_simulaciones / 2];
    stats.score_p75 = scores[(3 * stats.total_simulaciones) / 4];
    
    return stats;
}

int main() {
    std::random_device rd;
    std::mt19937 gen(rd());
    
    const int NUM_SIMULACIONES = 10000;
    
    std::cout << "\n╔════════════════════════════════════════════════════════════════╗\n";
    std::cout << "║  SIMULACIÓN MONTE CARLO: JEEP COMPASS - CRISIS LOGÍSTICA      ║\n";
    std::cout << "╚════════════════════════════════════════════════════════════════╝\n\n";
    
    std::cout << "🎲 Ejecutando " << NUM_SIMULACIONES << " simulaciones por opción...\n\n";
    
    std::cout << "📍 CONTEXTO:\n";
    std::cout << "  • Vives en SANTIAGO con familia (niños pequeños)\n";
    std::cout << "  • Trabajas Lun-Mie en CON CON (cerca Viña)\n";
    std::cout << "  • Jeep Compass: guardado en Santiago (correa se sale)\n";
    std::cout << "  • Suzuki Alto: auto de respaldo para familia\n";
    std::cout << "  • Mauricio: mecánico de confianza para coordinar traslado\n\n";
    std::cout << "⏰ HORIZONTE DE TIEMPO:\n";
    std::cout << "  • Proyección a 4 SEMANAS (1 mes)\n";
    std::cout << "  • 'Esperar' dura SOLO 1 semana (luego coordinas con calma)\n";
    std::cout << "  • 'Commuter' asume 4 semanas sin auto (peor caso)\n\n";
    
    // Variables configurables
    const double costo_compresor = 300000;      // CLP (nuevo, original)
    const double costo_recarga_aire = 40000;    // CLP (si hay que recargar)
    const double costo_grua = 100000;           // CLP (Santiago → Viña)
    const double costo_bus_semanal = 16000;     // CLP (ida+vuelta/semana)
    const double costo_mecanico_viña = 20000;   // CLP (escolta en carretera)
    
    // Tiempo familiar perdido si usas bus
    const double horas_perdidas_domingo = 6;    // Sales 6pm domingo vs estar en casa
    const double horas_perdidas_miercoles = 3;  // Llegas 11pm vs 8pm
    
    // Tiempo extra diario en Viña usando micro vs auto
    const double tiempo_auto_viña_trabajo = 0.67;  // 40 min en auto
    const double tiempo_micro_viña_trabajo = 1.25; // 1h15min en micro (ida+vuelta = 2.5h/día)
    const double tiempo_extra_micro_dia = (tiempo_micro_viña_trabajo - tiempo_auto_viña_trabajo) * 2; // ida+vuelta
    const double dias_trabajo_semana = 3;  // Lun, Mar, Mie
    const double horas_extra_micro_semana = tiempo_extra_micro_dia * dias_trabajo_semana; // ~3.5h extra
    
    const double horas_perdidas_semana = horas_perdidas_domingo + horas_perdidas_miercoles + horas_extra_micro_semana;
    
    // === OPCIONES CON INCERTIDUMBRE ===
    std::vector<OpcionIncertidumbre> opciones = {
        {
            "Opción 1: Risky Run",
            "Mecánico Viña te escolta en carretera, repara si correa se sale",
            0.80,  // prob_jefe_rechaza: 80% (YA PASÓ TIEMPO, ya no le vas a preguntar)
            0.35,  // prob_falla_mecanica: 35% que correa falle múltiples veces
            0.10,  // prob_retraso: 10% de retraso menor
            0.05,  // prob_emergencia_familiar: 5% Suzuki falle (solo 1 día)
            costo_mecanico_viña,  // costo_base: $20k
            5000,  // costo_std: ±$5k variabilidad
            false, // costo_recurrente: NO (pago único)
            1,     // semanas_duracion: resuelve HOY
            0,     // tiempo_base: 0 horas perdidas si funciona
            1.5,   // tiempo_std: ±1.5h variabilidad
            false, // tiempo_recurrente: NO
            0.25,  // carga_mental_base: ALTA (estar pendiente en carretera)
            0.35,  // seguridad_base: RIESGO ALTO
            1.0,   // logistica_familiar: OK (tienes auto)
            1.0    // comodidad: OK (duermes en casa)
        },
        {
            "Opción 2: Correct Fix (Santiago)",
            "Instalar compresor correcto + recarga. Puede NO estar listo lunes.",
            0.95,  // prob_jefe_rechaza: 95% (ya pasó tiempo, no le vas a preguntar)
            0.40,  // prob_falla_mecanica: 40% que compresor NO llegue a tiempo
            0.30,  // prob_retraso: 30% de retraso adicional
            0.08,  // prob_emergencia_familiar: 8% Suzuki falle (1 semana sin Jeep)
            costo_compresor + costo_recarga_aire,  // costo_base: $340k
            30000, // costo_std: ±$30k variabilidad
            false, // costo_recurrente: NO (pago único)
            1,     // semanas_duracion: resuelve esta semana
            horas_perdidas_semana,  // tiempo_base: ~12.5h perdidas
            2.0,   // tiempo_std: ±2h variabilidad
            false, // tiempo_recurrente: NO (solo esta semana)
            0.20,  // carga_mental_base: ALTA (estar pendiente si llega compresor)
            0.95,  // seguridad_base: AUTO BIEN REPARADO
            0.30,  // logistica_familiar: MALO (sin auto)
            0.40   // comodidad: BAJO (casa suegros)
        },
        {
            "Opción 3: Tow (Grúa a Viña)",
            "Grúa interurbana Santiago → Viña. Reparas con mecánico Mauricio.",
            0.0,   // prob_jefe_rechaza: 0% (no necesitas permiso)
            0.05,  // prob_falla_mecanica: 5% que grúa no llegue a tiempo
            0.15,  // prob_retraso: 15% de retraso menor
            0.08,  // prob_emergencia_familiar: 8% Suzuki falle (1 semana sin Jeep)
            costo_grua,  // costo_base: $100k
            15000, // costo_std: ±$15k variabilidad cotizaciones
            false, // costo_recurrente: NO (pago único)
            1,     // semanas_duracion: resuelve esta semana
            horas_perdidas_semana,  // tiempo_base: ~12.5h perdidas
            1.5,   // tiempo_std: ±1.5h variabilidad
            false, // tiempo_recurrente: NO (solo esta semana)
            0.05,  // carga_mental_base: BAJA (solo coordinar grúa, simple)
            1.0,   // seguridad_base: PERFECTO (no circula)
            0.30,  // logistica_familiar: MALO (sin auto)
            0.40   // comodidad: BAJO (casa suegros)
        },
        {
            "Opción 4: Commuter (Bus)",
            "Viajas en bus. Auto queda guardado en casa Santiago.",
            0.0,   // prob_jefe_rechaza: 0% (no necesitas permiso)
            0.02,  // prob_falla_mecanica: 2% que bus se retrase gravemente
            0.20,  // prob_retraso: 20% de retrasos menores
            0.12,  // prob_emergencia_familiar: 12% Suzuki falle (4 semanas exposición!)
            costo_bus_semanal,  // costo_base: $16k/semana
            2000,  // costo_std: ±$2k variabilidad
            true,  // costo_recurrente: SÍ (cada semana)
            4,     // semanas_duracion: asumes 4 semanas hasta reparar
            horas_perdidas_semana,  // tiempo_base: ~12.5h perdidas
            2.0,   // tiempo_std: ±2h variabilidad horarios
            true,  // tiempo_recurrente: SÍ (cada semana)
            0.15,  // carga_mental_base: MEDIA (estar pendiente horarios bus)
            1.0,   // seguridad_base: PERFECTO
            0.70,  // logistica_familiar: OK (Suzuki Alto)
            0.30   // comodidad: BAJO (suegros + horarios)
        },
        {
            "Opción 5: Esperar y Coordinar",
            "Postergas 1 semana. Auto listo lunes, pareja maneja lento. Pides día admin.",
            0.0,   // prob_jefe_rechaza: 0% (pides día admin próxima semana, sin presión)
            0.01,  // prob_falla_mecanica: 1% (auto SÍ O SÍ listo lunes)
            0.10,  // prob_retraso: 10% de retrasos menores
            0.08,  // prob_emergencia_familiar: 8% Suzuki falle (1 semana sin Jeep)
            costo_bus_semanal,  // costo_base: $16k/semana
            2000,  // costo_std: ±$2k variabilidad
            true,  // costo_recurrente: SÍ (solo esta semana)
            1,     // semanas_duracion: SOLO 1 SEMANA (luego coordinas con jefe/Mauricio)
            horas_perdidas_semana,  // tiempo_base: ~12.5h perdidas
            1.5,   // tiempo_std: ±1.5h variabilidad
            true,  // tiempo_recurrente: SÍ (solo esta semana)
            0.02,  // carga_mental_base: MUY BAJA (todo bajo control, sin presión)
            1.0,   // seguridad_base: PERFECTO
            0.70,  // logistica_familiar: OK (Suzuki Alto)
            0.35   // comodidad: BAJO temporal
        }
    };
    
    // === SIMULACIONES MONTE CARLO ===
    std::vector<EstadisticasOpcion> todas_stats;
    
    for (const auto& opcion : opciones) {
        std::vector<ResultadoSimulacion> resultados;
        
        for (int sim = 0; sim < NUM_SIMULACIONES; ++sim) {
            resultados.push_back(simularOpcion(opcion, gen));
        }
        
        todas_stats.push_back(calcularEstadisticas(opcion.nombre, resultados));
    }
    
    // === RESULTADOS ===
    std::cout << "📊 RESULTADOS MONTE CARLO:\n";
    std::cout << std::string(80, '=') << "\n\n";
    
    // Ordenar por score a LARGO PLAZO (4 semanas)
    std::vector<EstadisticasOpcion> stats_ordenadas = todas_stats;
    std::sort(stats_ordenadas.begin(), stats_ordenadas.end(), 
              [](const EstadisticasOpcion& a, const EstadisticasOpcion& b) {
                  // Ordenar por score a 4 semanas (captura costos/tiempo acumulados)
                  return a.score_promedio_4semanas > b.score_promedio_4semanas;
              });
    
    for (const auto& stats : stats_ordenadas) {
        std::cout << stats.nombre << "\n";
        std::cout << "  🎯 Probabilidad de éxito:  " << std::fixed << std::setprecision(1) 
                  << (stats.prob_exito * 100) << "%\n";
        std::cout << "  ⭐ Score 1 semana:         " << std::setprecision(3) 
                  << stats.score_promedio << "\n";
        std::cout << "  ⭐ Score 4 semanas:        " << std::setprecision(3) 
                  << stats.score_promedio_4semanas << " ⬅️ LARGO PLAZO\n";
        std::cout << "  📊 Rango scores (P25-P75): " << std::setprecision(3) 
                  << stats.score_p25 << " - " << stats.score_p75 << "\n";
        std::cout << "  💰 Costo 1 semana:         $" << std::setprecision(0) 
                  << stats.costo_promedio << " CLP\n";
        std::cout << "  💰 Costo 4 semanas:        $" << std::setprecision(0) 
                  << stats.costo_promedio_4semanas << " CLP ⬅️ ACUMULADO\n";
        std::cout << "  ⏰ Tiempo perdido 1 semana: " << std::setprecision(1) 
                  << stats.tiempo_perdido_promedio << " horas\n";
        std::cout << "  ⏰ Tiempo perdido 4 semanas: " << std::setprecision(1) 
                  << stats.tiempo_perdido_4semanas << " horas ⬅️ ACUMULADO\n";
        std::cout << "  ✅ Simulaciones exitosas:  " << stats.simulaciones_exitosas 
                  << " / " << stats.total_simulaciones << "\n\n";
    }
    
    // === RECOMENDACIÓN FINAL ===
    std::cout << std::string(80, '=') << "\n";
    std::cout << "🎯 RECOMENDACIÓN MONTE CARLO:\n";
    std::cout << std::string(80, '=') << "\n\n";
    std::cout << "✅ MEJOR OPCIÓN: " << stats_ordenadas[0].nombre << "\n\n";
    std::cout << "Por qué:\n";
    std::cout << "  • Probabilidad de éxito: " << std::setprecision(1) 
              << (stats_ordenadas[0].prob_exito * 100) << "%\n";
    std::cout << "  • Score esperado: " << std::setprecision(3) 
              << stats_ordenadas[0].score_promedio << "\n";
    std::cout << "  • Confiabilidad: " << stats_ordenadas[0].simulaciones_exitosas 
              << " escenarios exitosos de " << NUM_SIMULACIONES << "\n\n";
    
    std::cout << "📋 ANÁLISIS COMPARATIVO:\n\n";
    
    for (size_t i = 0; i < stats_ordenadas.size(); ++i) {
        std::cout << i + 1 << ". " << stats_ordenadas[i].nombre << ":\n";
        
        if (stats_ordenadas[i].nombre.find("Risky Run") != std::string::npos) {
            std::cout << "   ⚠️  RIESGOS: 60% rechazo jefe + 35% falla mecánica\n";
            std::cout << "   ✅ VENTAJAS: Bajo costo, familia con auto, duermes en casa\n";
        } else if (stats_ordenadas[i].nombre.find("Correct Fix") != std::string::npos) {
            std::cout << "   ⚠️  RIESGOS: 80% rechazo jefe + 40% compresor no llega\n";
            std::cout << "   ✅ VENTAJAS: Reparación definitiva\n";
        } else if (stats_ordenadas[i].nombre.find("Tow") != std::string::npos) {
            std::cout << "   ⚠️  COSTOS: $100k grúa única vez, familia sin auto 1 semana\n";
            std::cout << "   ✅ VENTAJAS: 0% riesgo laboral, seguro, mecánico Mauricio\n";
        } else if (stats_ordenadas[i].nombre.find("Commuter") != std::string::npos) {
            std::cout << "   ⚠️  COSTOS: 4 semanas sin auto ($64k + 50h familia)\n";
            std::cout << "   ✅ VENTAJAS: 0% riesgo laboral, familia OK (Suzuki Alto)\n";
        } else if (stats_ordenadas[i].nombre.find("Esperar") != std::string::npos) {
            std::cout << "   ⚠️  COSTOS: Solo 1 semana sin auto ($16k + 12.5h)\n";
            std::cout << "   ✅ VENTAJAS: 0% riesgo laboral, coordinas con jefe/Mauricio con calma\n";
        }
        std::cout << "\n";
    }
    
    std::cout << "💡 FACTORES CLAVE:\n";
    std::cout << "  • Jefe Alejandro: Relación tensa, llamar sábado es incómodo\n";
    std::cout << "  • Risky Run necesita permiso lunes (60% probabilidad rechazo)\n";
    std::cout << "  • Correct Fix necesita 2-3 días (80% probabilidad rechazo)\n";
    std::cout << "  • Familia: Suzuki Alto disponible como respaldo\n";
    std::cout << "  • Sin Jeep en Viña: +12.5h/semana perdidas (bus + micro)\n\n";
    
    return 0;
}
