#include <iostream>
#include <random>
#include <vector>
#include <string>
#include <iomanip>
#include <algorithm>

/**
 * 🎯 DECISIÓN ESPECÍFICA PARA ARTURO:
 * ¿Qué hacer con mi setup de desarrollo?
 * 
 * SITUACIÓN:
 * - MacBook 2019 funciona pero se queda corto de RAM
 * - Presupuesto: ~$300 USD
 * - Soy desarrollador, me gusta Ubuntu/Linux
 * - Quiero el mejor valor por mi dinero
 */

struct OpcionComputadora {
    std::string nombre;
    std::string descripcion;
    double costo_inicial;
    double probabilidad_encontrar_buen_precio;  // % de encontrar buen deal
    double rendimiento_desarrollo;              // 1-10 para desarrollo
    double ram_gb;                             // RAM disponible
    double duracion_esperada_años;             // Cuánto durará
    double costo_upgrades_año;                 // Upgrades/mantenimiento por año
    double compatibilidad_linux;              // 1-10 qué tan bien funciona Linux
    double probabilidad_problemas_hardware;   // % chance de problemas
    double valor_reventa_después_2años;       // Valor de reventa
    bool requiere_pantalla_externa;           // ¿Necesito comprar pantalla?
    double costo_pantalla_si_necesaria;       // Costo de pantalla si la necesito
    
    // NUEVOS FACTORES CRÍTICOS
    double portabilidad;                      // 0-10: laptop portátil vs desktop inmóvil
    double facilidad_upgrade_ram;             // 0-10: qué tan fácil/barato upgradear RAM
    double costo_upgrade_ram_16_a_32gb;       // Costo específico upgrade RAM (si aplica)
    double ecosistema_docker_compiladores;    // 0-10: qué tan bien funciona Docker/compiladores
    double prob_downtime_laboral;             // % probabilidad downtime durante trabajo freelance
    double costo_oportunidad_hora_perdida;    // $/hora perdida en freelance (promedio)
    double estres_base;                       // 0-1: ansiedad base con esta opción
    double familiaridad_sistema;              // 0-10: qué tan familiar es el sistema para ti
    double gasto_extra_movil_semana;          // $/semana en café/comida adicional por trabajar fuera (cafés)
};

struct ResultadoSimulacion {
    double costo_total_2años;
    double productividad_promedio;     // Qué tan productivo seré
    double satisfaccion_desarrollo;    // Qué tan feliz trabajando
    bool necesite_upgrade_temprano;    // ¿Tuve que upgradear antes?
    double tiempo_perdido_problemas;   // Horas perdidas por problemas técnicos
    bool encontre_buen_deal;           // ¿Conseguí buen precio inicial?
    
    // NUEVOS RESULTADOS
    double dinero_perdido_downtime;    // $ perdidos por downtime freelance
    double estres_acumulado;           // Estrés total durante 2 años
    bool tuvo_downtime_critico;        // ¿Downtime durante proyecto importante?
    bool upgrade_ram_necesario;        // ¿Necesité upgrade RAM?
    double costo_upgrade_ram_real;     // Costo real si upgradeé RAM
    double penalizacion_portabilidad;  // Penalización por no poder trabajar móvil
    double gasto_comida_total;         // Gasto acumulado en café/comida extra por trabajo móvil
};

ResultadoSimulacion simular_opcion(const OpcionComputadora& opcion, std::mt19937& gen) {
    std::uniform_real_distribution<double> prob_dist(0.0, 1.0);
    std::normal_distribution<double> normal_dist(0.0, 1.0);
    
    ResultadoSimulacion resultado = {};
    
    // 1. ¿ENCUENTRO BUEN PRECIO?
    resultado.encontre_buen_deal = prob_dist(gen) < opcion.probabilidad_encontrar_buen_precio;
    double precio_real = opcion.costo_inicial;
    if (resultado.encontre_buen_deal) {
        // Si encuentro buen deal, 10-25% más barato
        std::uniform_real_distribution<double> descuento_dist(0.10, 0.25);
        precio_real *= (1.0 - descuento_dist(gen));
    }
    
    // 2. ¿NECESITO PANTALLA?
    double costo_pantalla = 0;
    if (opcion.requiere_pantalla_externa) {
        // Probabilidad de que ya tenga pantalla o encuentre barata
        if (prob_dist(gen) > 0.3) { // 70% chance necesite comprar pantalla
            costo_pantalla = opcion.costo_pantalla_si_necesaria;
        }
    }
    
    // 3. COSTOS DE UPGRADES/MANTENIMIENTO
    std::exponential_distribution<double> costo_upgrade_dist(1.0 / opcion.costo_upgrades_año);
    double costos_upgrades_2años = 0;
    
    for (int año = 1; año <= 2; ++año) {
        // Probabilidad aumenta si la RAM es insuficiente
        double prob_upgrade = 0.2; // base 20%
        if (opcion.ram_gb < 16) {
            prob_upgrade += 0.3; // +30% si RAM < 16GB
        }
        if (opcion.ram_gb < 8) {
            prob_upgrade += 0.4; // +40% más si RAM < 8GB
        }
        
        if (prob_dist(gen) < prob_upgrade) {
            costos_upgrades_2años += costo_upgrade_dist(gen);
        }
    }
    
    // ===== NUEVOS FACTORES CRÍTICOS =====
    
    // 4. UPGRADE RAM (NUEVO - FACTOR CRÍTICO)
    resultado.upgrade_ram_necesario = false;
    resultado.costo_upgrade_ram_real = 0;
    
    if (opcion.ram_gb < 16) {
        // Si RAM < 16GB, muy probable que necesite upgrade
        if (prob_dist(gen) < 0.8) { // 80% probabilidad
            resultado.upgrade_ram_necesario = true;
            resultado.costo_upgrade_ram_real = opcion.costo_upgrade_ram_16_a_32gb;
            costos_upgrades_2años += resultado.costo_upgrade_ram_real;
        }
    } else if (opcion.ram_gb == 16) {
        // Con 16GB, menor probabilidad pero posible
        if (prob_dist(gen) < 0.25) { // 25% probabilidad upgrade a 32GB
            resultado.upgrade_ram_necesario = true;
            resultado.costo_upgrade_ram_real = opcion.costo_upgrade_ram_16_a_32gb;
            costos_upgrades_2años += resultado.costo_upgrade_ram_real;
        }
    }
    
    // 5. PORTABILIDAD (NUEVO - FACTOR CRÍTICO)
    // Trabajas en cualquier lugar → laptop es crítico
    resultado.penalizacion_portabilidad = 0;
    if (opcion.portabilidad < 7.0) {
        // Desktop/Mini PC → pierdes oportunidades de trabajo móvil
        // Estimas ~2 horas/semana que no puedes trabajar óptimamente
        double horas_perdidas_portabilidad = 2.0 * 52 * 2; // 2h/semana × 52 semanas × 2 años = 208h
        resultado.penalizacion_portabilidad = horas_perdidas_portabilidad;
        resultado.dinero_perdido_downtime += horas_perdidas_portabilidad * opcion.costo_oportunidad_hora_perdida;
    }

    // 5.b GASTO EXTRA DE COMIDA / CAFÉ (nuevo)
    // Si la opción permite portabilidad alta, asumimos que trabajas X veces fuera y gastas extra.
    // Modelo: gasto semanal × factor portabilidad relativa × 104 semanas.
    resultado.gasto_comida_total = 0;
    if (opcion.portabilidad >= 7.0 && opcion.gasto_extra_movil_semana > 0) {
        // Ajuste por portabilidad (más portátil → más uso fuera → más gasto)
        double factor_porta = (opcion.portabilidad / 10.0); // 0-1
        resultado.gasto_comida_total = opcion.gasto_extra_movil_semana * 104.0 * factor_porta; // 2 años
    }
    
    // 6. DOWNTIME CRÍTICO (NUEVO - FREELANCE)
    resultado.tuvo_downtime_critico = false;
    resultado.dinero_perdido_downtime = 0;
    
    for (int mes = 1; mes <= 24; ++mes) { // 2 años = 24 meses
        if (prob_dist(gen) < opcion.prob_downtime_laboral) {
            // Downtime ocurrió este mes
            resultado.tuvo_downtime_critico = true;
            
            // Horas perdidas: entre 4-24 horas dependiendo severidad
            std::uniform_real_distribution<double> horas_perdidas_dist(4.0, 24.0);
            double horas_perdidas = horas_perdidas_dist(gen);
            
            resultado.tiempo_perdido_problemas += horas_perdidas;
            resultado.dinero_perdido_downtime += horas_perdidas * opcion.costo_oportunidad_hora_perdida;
        }
    }
    
    // 7. ESTRÉS ACUMULADO (NUEVO - COMO EN JEEP)
    resultado.estres_acumulado = opcion.estres_base; // Estrés base
    
    // Estrés aumenta si hay problemas
    bool hubo_problemas = prob_dist(gen) < opcion.probabilidad_problemas_hardware;
    if (hubo_problemas) {
        resultado.estres_acumulado += 0.25; // +25% estrés
        
        if (!resultado.tiempo_perdido_problemas) {
            resultado.tiempo_perdido_problemas = 8 + normal_dist(gen) * 3; // 8±3 horas
            resultado.tiempo_perdido_problemas = std::max(0.0, resultado.tiempo_perdido_problemas);
        }
    }
    
    // Estrés por downtime crítico durante proyecto importante
    if (resultado.tuvo_downtime_critico) {
        resultado.estres_acumulado += 0.30; // +30% estrés
    }
    
    // Estrés reducido por familiaridad con sistema
    double reduccion_estres_familiaridad = (opcion.familiaridad_sistema / 10.0) * 0.15;
    resultado.estres_acumulado = std::max(0.0, resultado.estres_acumulado - reduccion_estres_familiaridad);
    
    // 8. PRODUCTIVIDAD BASADA EN MÚLTIPLES FACTORES
    double productividad_base = opcion.rendimiento_desarrollo / 10.0; // Normalizar a 0-1
    
    // Penalizar por problemas de hardware
    if (hubo_problemas) {
        productividad_base *= 0.85; // 15% menos productivo
    }
    
    // Bonus por ecosistema Docker/compiladores (crítico para desarrollo)
    double bonus_ecosistema = (opcion.ecosistema_docker_compiladores / 10.0) * 0.25; // hasta 25% bonus
    productividad_base += bonus_ecosistema;
    
    // Bonus por compatibilidad con Linux (importante para desarrollador)
    double bonus_linux = (opcion.compatibilidad_linux / 10.0) * 0.15; // hasta 15% bonus
    productividad_base += bonus_linux;
    
    // Penalizar por falta de portabilidad (no puedes trabajar óptimamente en cafés/viajes)
    if (opcion.portabilidad < 7.0) {
        productividad_base *= 0.90; // -10% productividad
    }
    
    // Penalizar por RAM insuficiente
    if (opcion.ram_gb < 16 && !resultado.upgrade_ram_necesario) {
        productividad_base *= 0.75; // -25% productividad con RAM insuficiente
    }
    
    resultado.productividad_promedio = std::min(1.0, productividad_base);
    
    // 9. SATISFACCIÓN (REBALANCEADA CON NUEVOS FACTORES)
    resultado.satisfaccion_desarrollo = 
        (opcion.rendimiento_desarrollo * 0.25) +                              // 25% rendimiento
        (opcion.ecosistema_docker_compiladores * 0.20) +                     // 20% ecosistema
        (opcion.portabilidad * 0.20) +                                       // 20% portabilidad (CRÍTICO)
        (opcion.familiaridad_sistema * 0.15) +                               // 15% familiaridad
        ((10.0 - opcion.probabilidad_problemas_hardware * 10) * 0.10) +      // 10% confiabilidad
        ((10.0 - resultado.estres_acumulado * 10) * 0.10);                   // 10% bajo estrés
    
    // Bonus si encontré buen precio
    if (resultado.encontre_buen_deal) {
        resultado.satisfaccion_desarrollo += 0.5;
    }
    
    // Penalizar fuertemente si necesité upgrade RAM muy caro
    if (resultado.upgrade_ram_necesario && resultado.costo_upgrade_ram_real > 300) {
        resultado.satisfaccion_desarrollo -= 2.0; // -2 puntos si upgrade RAM > $300
    }
    
    // Penalizar si hubo downtime crítico
    if (resultado.tuvo_downtime_critico) {
        resultado.satisfaccion_desarrollo -= 1.5;
    }
    
    // Penalizar si necesité upgrades tempranos
    resultado.necesite_upgrade_temprano = costos_upgrades_2años > (opcion.costo_upgrades_año * 1.5);
    if (resultado.necesite_upgrade_temprano) {
        resultado.satisfaccion_desarrollo -= 1.0;
    }
    
    // 10. COSTO TOTAL (INCLUYE COSTOS OPORTUNIDAD + PORTABILIDAD)
    resultado.costo_total_2años = precio_real + 
                                  costo_pantalla + 
                                  costos_upgrades_2años + 
                                  resultado.dinero_perdido_downtime +     // Costo oportunidad downtime
                                  resultado.penalizacion_portabilidad -   // Costo oportunidad portabilidad ⚠️
                                  opcion.valor_reventa_después_2años +
                                  resultado.gasto_comida_total;           // Gasto café/comida móvil
    
    return resultado;
}

int main() {
    std::cout << "💻 === DECISIÓN DE ARTURO: ¿QUÉ COMPUTADORA COMPRAR? ===\n\n";
    
    std::cout << "🎯 TU SITUACIÓN:\n";
    std::cout << "   • MacBook 2019 funciona pero se queda corto de RAM\n";
    std::cout << "   • Desarrollador freelance ($25/hora)\n";
    std::cout << "   • Trabajas desde cualquier lugar (portabilidad crítica)\n";
    std::cout << "   • Quieres mejor valor a largo plazo (sin límite presupuesto)\n\n";
    
    // DEFINIR TUS OPCIONES REALES
    std::vector<OpcionComputadora> opciones = {
        {
            "Seguir con MacBook 2019",
            "Upgrade RAM si es posible, optimizar software",
            50,      // Solo costo de optimización/limpieza
            0.9,     // 90% probabilidad de hacer esto barato
            6.5,     // Rendimiento limitado por RAM
            8,       // RAM actual (estimada)
            2.0,     // Durará ~2 años más
            75,      // $75/año en mantenimiento/optimización
            7,       // macOS decente para desarrollo
            0.1,     // 10% chance problemas (ya funciona)
            100,     // Valor residual después de 2 años
            false,   // Ya tienes pantalla
            0,       // No necesitas pantalla
            
            // NUEVOS FACTORES
            10.0,    // Portabilidad: PERFECTA (laptop, ya lo usas así)
            2.0,     // Facilidad upgrade RAM: MUY DIFÍCIL (soldada en muchos modelos)
            400,     // Costo upgrade 16→32GB: $400 USD (MUY CARO)
            7.5,     // Ecosistema Docker/compiladores: decente en macOS
            0.12,    // Prob downtime: 12% (funciona bien pero RAM limita)
            25,      // Costo oportunidad: $25/hora freelance
            0.15,    // Estrés base: BAJO (funciona súper bien, confiable)
            10.0,    // Familiaridad: MÁXIMA (ya lo usas, conoces todo)
            12       // Gasto extra móvil semanal (café/comida trabajando fuera)
        },
        {
            "Mac Mini usado (2018-2020)",
            "Mac Mini usado con 16GB RAM, compatible con tus workflows",
            280,     // Precio objetivo
            0.4,     // 40% chance de encontrar buen deal
            8.0,     // Buen rendimiento para desarrollo
            16,      // 16GB RAM
            3.5,     // Durará ~3.5 años
            50,      // $50/año mantenimiento
            7.5,     // macOS bueno para desarrollo
            0.15,    // 15% chance problemas (usado)
            180,     // Valor residual bueno (Mac)
            true,    // Necesitas pantalla
            80,      // Pantalla 1080p decente $80
            
            // NUEVOS FACTORES
            1.0,     // Portabilidad: CERO (desktop, no portátil) ⚠️ CRÍTICO
            3.0,     // Facilidad upgrade RAM: DIFÍCIL (algunos modelos soldados)
            400,     // Costo upgrade 16→32GB: $400 USD (MUY CARO)
            7.5,     // Ecosistema Docker/compiladores: decente en macOS
            0.10,    // Prob downtime: 10% (más estable que MacBook viejo)
            25,      // Costo oportunidad: $25/hora
            0.30,    // Estrés base: MEDIO (usado + no portátil = ansiedad)
            8.5,     // Familiaridad: ALTA (macOS conocido, pero desktop nuevo)
            0        // Gasto extra móvil semanal (no portátil → no café adicional)
        },
        {
            "Mini PC AMD (nuevo)",
            "Beelink/ASUS mini PC AMD Ryzen 5, 16GB RAM",
            290,     // Precio típico
            0.7,     // 70% chance encontrar buen precio (más disponibles)
            8.5,     // Excelente rendimiento
            16,      // 16GB RAM
            4.0,     // Durará ~4 años
            30,      // $30/año mantenimiento
            9.5,     // Excelente para Linux
            0.05,    // 5% chance problemas (nuevo)
            120,     // Depreciación más rápida
            true,    // Necesitas pantalla
            80,      // Pantalla 1080p $80
            
            // NUEVOS FACTORES
            1.0,     // Portabilidad: CERO (desktop, no portátil) ⚠️ CRÍTICO
            8.0,     // Facilidad upgrade RAM: FÁCIL (SO-DIMM estándar, barato)
            80,      // Costo upgrade 16→32GB: $80 USD (barato)
            10.0,    // Ecosistema Docker/compiladores: PERFECTO en Linux
            0.05,    // Prob downtime: 5% (nuevo, confiable)
            25,      // Costo oportunidad: $25/hora
            0.35,    // Estrés base: MEDIO-ALTO (no portátil + sistema nuevo)
            5.0,     // Familiaridad: MEDIA (Linux conocido, pero HW nuevo)
            0        // Gasto extra móvil semanal (desktop)
        },
        {
            "Laptop nuevo económico",
            "Acer/HP con AMD Ryzen 5, 16GB RAM",
            300,     // En el límite del presupuesto
            0.8,     // 80% chance encontrar en presupuesto
            7.0,     // Rendimiento decente
            16,      // 16GB RAM
            3.5,     // Durará ~3.5 años
            40,      // $40/año mantenimiento
            8.5,     // Muy bueno para Linux
            0.08,    // 8% chance problemas (nuevo)
            130,     // Depreciación moderada
            false,   // Pantalla incluida
            0,       // No necesitas pantalla
            
            // NUEVOS FACTORES
            10.0,    // Portabilidad: PERFECTA (laptop) ✅
            6.0,     // Facilidad upgrade RAM: MODERADA (algunos modelos soldados)
            100,     // Costo upgrade 16→32GB: $100 USD (moderado)
            9.0,     // Ecosistema Docker/compiladores: EXCELENTE en Linux
            0.08,    // Prob downtime: 8% (nuevo, garantía)
            25,      // Costo oportunidad: $25/hora
            0.20,    // Estrés base: BAJO-MEDIO (nuevo = confianza, pero marca desconocida)
            6.0,     // Familiaridad: MEDIA (Linux conocido, HW nuevo genérico)
            15       // Gasto extra móvil semanal (trabajo frecuente fuera)
        },
        {
            "Computador del trabajo",
            "Laptop empresa (gratis, sin restricciones explícitas)",
            0,       // GRATIS ✅
            1.0,     // 100% chance (ya disponible)
            7.5,     // Rendimiento: probablemente decente (laptop corporativo)
            16,      // 16GB RAM asumido (estándar corporativo)
            2.0,     // Duración: mientras sigas empleado (incertidumbre)
            0,       // $0 mantenimiento (empresa mantiene)
            6.0,     // Linux: puede tener restricciones IT corporativas
            0.05,    // 5% problemas (soporte IT disponible)
            0,       // Valor reventa: NO ES TUYO
            false,   // Laptop incluida
            0,
            
            // NUEVOS FACTORES
            10.0,    // Portabilidad: PERFECTA (laptop) ✅
            0.0,     // Facilidad upgrade RAM: IMPOSIBLE (no es tuyo)
            0,       // Costo upgrade: N/A
            6.0,     // Ecosistema: LIMITADO (políticas corporativas, posible Windows)
            0.10,    // Prob downtime: 10% (si pierdes trabajo = crisis total)
            25,      // Costo oportunidad: $25/hora
            0.60,    // Estrés base: ALTO (dependencia laboral crítica) ⚠️
            3.0      // Familiaridad: BAJA (OS/HW desconocido, posible Windows)
        },
        {
            "MacBook Pro 2020 usado",
            "MacBook Pro 13\" 2020, i5-1038NG7, 16GB RAM, 512GB SSD",
            320,     // Precio promedio eBay Nov 2025
            0.6,     // 60% chance buen precio
            8.5,     // Muy buen rendimiento
            16,      // 16GB RAM (upgrade completo)
            3.5,     // Durará ~3.5 años (usado pero reciente)
            80,      // $80/año mantenimiento
            7.5,     // macOS decente para dev
            0.15,    // 15% problemas (usado, 4 años)
            200,     // Mac retiene valor
            false,   // Laptop incluida
            0,
            
            // NUEVOS FACTORES
            10.0,    // Portabilidad: PERFECTA ✅
            0.0,     // Facilidad upgrade RAM: IMPOSIBLE (soldado)
            0,       // Costo upgrade: N/A (soldado)
            8.0,     // Ecosistema: BUENO (macOS buen dev, Docker OK)
            0.12,    // Prob downtime: 12% (usado, pero Mac confiable)
            25,      // Costo oportunidad: $25/hora
            0.20,    // Estrés base: BAJO (muy similar a actual, confiable)
            9.0      // Familiaridad: PERFECTA (usas Mac ahora, mismo OS)
        },
        {
            "Mini PC chino barato",
            "GMKtec/BOSGAME Ryzen 5 3500U, 16GB RAM, 512GB SSD",
            260,     // Precio Amazon Nov 2025
            0.75,    // 75% chance (amplia disponibilidad)
            8.0,     // Buen rendimiento (Ryzen 5)
            16,      // 16GB RAM
            3.5,     // Durará ~3.5 años
            35,      // $35/año mantenimiento
            9.0,     // Excelente para Linux
            0.08,    // 8% problemas (nuevo, pero marca china)
            100,     // Depreciación rápida
            true,    // REQUIERE pantalla externa
            80,      // $80 pantalla básica
            
            // NUEVOS FACTORES
            0.0,     // Portabilidad: CERO (desktop) ❌ CRÍTICO
            8.0,     // Facilidad upgrade RAM: FÁCIL (SO-DIMM upgradeable)
            50,      // Costo upgrade 16→32GB: $50
            9.0,     // Ecosistema: EXCELENTE (Linux perfecto)
            0.08,    // Prob downtime: 8%
            25,      // Costo oportunidad: $25/hora
            0.50,    // Estrés base: ALTO (desktop = no movilidad = ansiedad) ⚠️
            4.0      // Familiaridad: MEDIA-BAJA (Linux conocido, HW chino desconocido)
        },
        {
            "MSI Bravo 15 usado",
            "MSI Bravo 15.6\" Ryzen 7, 16GB RAM, RX 6550M (gaming)",
            400,     // Precio eBay Nov 2025 (SOBRE PRESUPUESTO)
            0.5,     // 50% chance buen deal
            9.0,     // Excelente rendimiento (gaming spec)
            16,      // 16GB RAM
            3.0,     // Durará ~3 años (gaming laptops degastan más)
            70,      // $70/año mantenimiento
            8.5,     // Muy bueno para Linux
            0.18,    // 18% problemas (usado, gaming = alta temperatura)
            180,     // Depreciación moderada
            false,   // Laptop incluida
            0,
            
            // NUEVOS FACTORES
            10.0,    // Portabilidad: PERFECTA (laptop) ✅
            7.0,     // Facilidad upgrade RAM: BUENA (gaming laptops upgradeable)
            70,      // Costo upgrade 16→32GB: $70
            9.0,     // Ecosistema: EXCELENTE (Linux perfecto en AMD)
            0.15,    // Prob downtime: 15% (usado gaming = riesgo térmico)
            25,      // Costo oportunidad: $25/hora
            0.30,    // Estrés base: MEDIO (usado gaming = ansiedad térmica, pero potente)
            6.0,     // Familiaridad: MEDIA (Linux conocido, HW gaming desconocido)
            18       // Gasto extra móvil semanal (más uso en cafés para potencia)
        },
        {
            "MacBook Air M2 nuevo a cuotas",
            "MacBook Air M2 2024, 16GB RAM, 512GB SSD (financiamiento 12-24 meses)",
            1200,    // Precio total a pagar (con intereses ~10-15%)
            1.0,     // 100% chance (disponible en tiendas oficiales)
            9.5,     // Excelente rendimiento (M2 muy eficiente)
            16,      // 16GB RAM (configuración ideal)
            5.0,     // Durará ~5 años (nuevo, Apple Silicon duradero)
            30,      // $30/año mantenimiento (bajo, nuevo con garantía)
            7.5,     // macOS decente para dev
            0.02,    // 2% problemas (nuevo, garantía Apple)
            700,     // Retiene 58% valor después 2 años
            false,   // Laptop incluida
            0,
            
            // NUEVOS FACTORES
            10.0,    // Portabilidad: PERFECTA ✅
            0.0,     // Facilidad upgrade RAM: IMPOSIBLE (soldado)
            0,       // Costo upgrade: N/A
            8.5,     // Ecosistema: MUY BUENO (macOS excelente dev, Docker OK)
            0.02,    // Prob downtime: 2% (nuevo, garantía 1 año)
            25,      // Costo oportunidad: $25/hora
            0.10,    // Estrés base: MUY BAJO (nuevo, confiable, garantía) ⭐
            10.0,    // Familiaridad: PERFECTA (mismo OS actual, mejor HW)
            20       // Gasto extra móvil semanal (mayor comodidad → más cafés)
        },
        {
            "MacBook Pro M3 nuevo a cuotas",
            "MacBook Pro 14\" M3 2024, 16GB RAM, 512GB SSD (financiamiento 12-24 meses)",
            1800,    // Precio total con intereses (~10-15%)
            1.0,     // 100% chance (disponible tiendas oficiales)
            10.0,    // Rendimiento MÁXIMO (M3 top tier)
            16,      // 16GB RAM
            6.0,     // Durará ~6 años (nuevo, Pro quality)
            30,      // $30/año mantenimiento
            8.0,     // macOS muy bueno para dev
            0.01,    // 1% problemas (nuevo, Pro build quality)
            1100,    // Retiene 61% valor después 2 años (Pro models)
            false,   // Laptop incluida
            0,
            
            // NUEVOS FACTORES
            10.0,    // Portabilidad: PERFECTA ✅
            0.0,     // Facilidad upgrade RAM: IMPOSIBLE (soldado)
            0,       // Costo upgrade: N/A
            9.0,     // Ecosistema: EXCELENTE (macOS mejor dev experience)
            0.01,    // Prob downtime: 1% (nuevo, Pro quality)
            25,      // Costo oportunidad: $25/hora
            0.05,    // Estrés base: MÍNIMO (mejor laptop mercado, garantía) ⭐⭐
            10.0,    // Familiaridad: PERFECTA (mismo OS, hardware premium)
            22       // Gasto extra móvil semanal (más uso externo profesional)
        }
    };
    
    const int num_simulaciones = 15000;
    std::random_device rd;
    std::mt19937 gen(rd());
    
    std::cout << "🎲 Ejecutando " << num_simulaciones << " simulaciones para cada opción...\n";
    std::cout << "   (Considerando precios del mercado, disponibilidad, problemas, etc.)\n\n";
    
    struct EstadisticasOpcion {
        std::string nombre;
        double costo_promedio;
        double productividad_promedio;
        double satisfaccion_promedio;
        double tiempo_perdido_promedio;
        double probabilidad_upgrade_temprano;
        double probabilidad_buen_deal;
        double costo_minimo;
        double costo_maximo;
        
        // NUEVAS ESTADÍSTICAS
        double dinero_perdido_downtime_promedio;
        double probabilidad_downtime_critico;
        double estres_promedio;
        double probabilidad_upgrade_ram;
        double costo_upgrade_ram_promedio;
        double penalizacion_portabilidad_promedio;
        double gasto_comida_promedio;
        std::vector<double> gasto_comida_vec;
    };
    
    std::vector<EstadisticasOpcion> resultados;
    
    for (const auto& opcion : opciones) {
        std::cout << "Analizando: " << opcion.nombre << "...\n";
        
        std::vector<double> costos;
        std::vector<double> productividades;
        std::vector<double> satisfacciones;
        std::vector<double> tiempos_perdidos;
        std::vector<double> dinero_perdido_downtime_vec;
        std::vector<double> estres_vec;
        std::vector<double> costo_upgrade_ram_vec;
        std::vector<double> penalizacion_portabilidad_vec;
        std::vector<double> gasto_comida_vec;
        
        int upgrades_tempranos = 0;
        int buenos_deals = 0;
        int downtimes_criticos = 0;
        int upgrades_ram = 0;
        
        for (int i = 0; i < num_simulaciones; ++i) {
            auto resultado = simular_opcion(opcion, gen);
            
            costos.push_back(resultado.costo_total_2años);
            productividades.push_back(resultado.productividad_promedio);
            satisfacciones.push_back(resultado.satisfaccion_desarrollo);
            tiempos_perdidos.push_back(resultado.tiempo_perdido_problemas);
            dinero_perdido_downtime_vec.push_back(resultado.dinero_perdido_downtime);
            estres_vec.push_back(resultado.estres_acumulado);
            costo_upgrade_ram_vec.push_back(resultado.costo_upgrade_ram_real);
            penalizacion_portabilidad_vec.push_back(resultado.penalizacion_portabilidad);
            gasto_comida_vec.push_back(resultado.gasto_comida_total);
            
            if (resultado.necesite_upgrade_temprano) upgrades_tempranos++;
            if (resultado.encontre_buen_deal) buenos_deals++;
            if (resultado.tuvo_downtime_critico) downtimes_criticos++;
            if (resultado.upgrade_ram_necesario) upgrades_ram++;
        }
        
        // Calcular estadísticas
        EstadisticasOpcion stats;
        stats.nombre = opcion.nombre;
        
        stats.costo_promedio = 0;
        stats.productividad_promedio = 0;
        stats.satisfaccion_promedio = 0;
        stats.tiempo_perdido_promedio = 0;
        stats.dinero_perdido_downtime_promedio = 0;
        stats.estres_promedio = 0;
        stats.costo_upgrade_ram_promedio = 0;
        stats.penalizacion_portabilidad_promedio = 0;
        stats.gasto_comida_promedio = 0;
        
        for (size_t i = 0; i < costos.size(); ++i) {
            stats.costo_promedio += costos[i];
            stats.productividad_promedio += productividades[i];
            stats.satisfaccion_promedio += satisfacciones[i];
            stats.tiempo_perdido_promedio += tiempos_perdidos[i];
            stats.dinero_perdido_downtime_promedio += dinero_perdido_downtime_vec[i];
            stats.estres_promedio += estres_vec[i];
            stats.costo_upgrade_ram_promedio += costo_upgrade_ram_vec[i];
            stats.penalizacion_portabilidad_promedio += penalizacion_portabilidad_vec[i];
            stats.gasto_comida_promedio += gasto_comida_vec[i];
        }
        
        stats.costo_promedio /= num_simulaciones;
        stats.productividad_promedio /= num_simulaciones;
        stats.satisfaccion_promedio /= num_simulaciones;
        stats.tiempo_perdido_promedio /= num_simulaciones;
        stats.dinero_perdido_downtime_promedio /= num_simulaciones;
        stats.estres_promedio /= num_simulaciones;
        stats.costo_upgrade_ram_promedio /= num_simulaciones;
        stats.penalizacion_portabilidad_promedio /= num_simulaciones;
        stats.gasto_comida_promedio /= num_simulaciones;
        
        stats.probabilidad_upgrade_temprano = (double)upgrades_tempranos / num_simulaciones;
        stats.probabilidad_buen_deal = (double)buenos_deals / num_simulaciones;
        stats.probabilidad_downtime_critico = (double)downtimes_criticos / num_simulaciones;
        stats.probabilidad_upgrade_ram = (double)upgrades_ram / num_simulaciones;
        
        stats.costo_minimo = *std::min_element(costos.begin(), costos.end());
        stats.costo_maximo = *std::max_element(costos.begin(), costos.end());
        
        resultados.push_back(stats);
    }
    
    // MOSTRAR RESULTADOS
    std::cout << "\n" << std::string(80, '=') << "\n";
    std::cout << "📊 RESULTADOS DE LA SIMULACIÓN (próximos 2 años):\n";
    std::cout << std::string(80, '=') << "\n\n";
    
    for (const auto& stats : resultados) {
        std::cout << "🖥️  " << stats.nombre << "\n";
        std::cout << "   💰 Costo total promedio: $" << std::fixed << std::setprecision(0) 
                  << stats.costo_promedio << " (rango: $" << stats.costo_minimo 
                  << " - $" << stats.costo_maximo << ")\n";
        std::cout << "   🚀 Productividad promedio: " << std::setprecision(1) 
                  << stats.productividad_promedio * 100 << "%\n";
        std::cout << "   😊 Satisfacción desarrollo: " << stats.satisfaccion_promedio << "/10\n";
        std::cout << "   ⏰ Tiempo perdido por problemas: " << std::setprecision(1) 
                  << stats.tiempo_perdido_promedio << " horas\n";
        
        // NUEVOS FACTORES CRÍTICOS
        std::cout << "   💸 Dinero perdido downtime: $" << std::setprecision(0) 
                  << stats.dinero_perdido_downtime_promedio << "\n";
        std::cout << "   😰 Estrés promedio: " << std::setprecision(1) 
                  << stats.estres_promedio * 100 << "%\n";
        std::cout << "   🔧 Probabilidad upgrade RAM: " << std::setprecision(1) 
                  << stats.probabilidad_upgrade_ram * 100 << "% (costo: $" 
                  << std::setprecision(0) << stats.costo_upgrade_ram_promedio << ")\n";
        std::cout << "   🚶 Penalización portabilidad: " << std::setprecision(0) 
                  << stats.penalizacion_portabilidad_promedio << " horas\n";
        std::cout << "   ⚠️  Probabilidad downtime crítico: " << std::setprecision(1) 
                  << stats.probabilidad_downtime_critico * 100 << "%\n";
        std::cout << "   ☕ Gasto café/comida (2 años): $" << std::setprecision(0)
              << stats.gasto_comida_promedio << "\n";
        
        std::cout << "   📈 Probabilidad upgrade temprano: " << std::setprecision(1) 
                  << stats.probabilidad_upgrade_temprano * 100 << "%\n";
        std::cout << "   🎯 Probabilidad buen precio: " << stats.probabilidad_buen_deal * 100 << "%\n";
        std::cout << "   💵 Costo por punto de productividad: $" << std::setprecision(0) 
                  << stats.costo_promedio / (stats.productividad_promedio * 100) << "\n\n";
    }
    
    // ENCONTRAR LA MEJOR OPCIÓN
    std::cout << "🏆 ANÁLISIS DE RECOMENDACIÓN:\n\n";
    
    // Mejor valor (costo/productividad)
    auto mejor_valor = *std::min_element(resultados.begin(), resultados.end(),
        [](const EstadisticasOpcion& a, const EstadisticasOpcion& b) {
            return (a.costo_promedio / a.productividad_promedio) < 
                   (b.costo_promedio / b.productividad_promedio);
        });
    
    std::cout << "✅ MEJOR VALOR: " << mejor_valor.nombre << "\n";
    std::cout << "   Razón: Mejor relación costo/productividad\n\n";
    
    // Menor costo
    auto menor_costo = *std::min_element(resultados.begin(), resultados.end(),
        [](const EstadisticasOpcion& a, const EstadisticasOpcion& b) {
            return a.costo_promedio < b.costo_promedio;
        });
    
    std::cout << "💰 MÁS ECONÓMICO: " << menor_costo.nombre << "\n";
    std::cout << "   Costo promedio: $" << std::setprecision(0) << menor_costo.costo_promedio << "\n\n";
    
    // Mayor satisfacción
    auto mayor_satisfaccion = *std::max_element(resultados.begin(), resultados.end(),
        [](const EstadisticasOpcion& a, const EstadisticasOpcion& b) {
            return a.satisfaccion_promedio < b.satisfaccion_promedio;
        });
    
    std::cout << "😊 MAYOR SATISFACCIÓN: " << mayor_satisfaccion.nombre << "\n";
    std::cout << "   Satisfacción: " << std::setprecision(1) << mayor_satisfaccion.satisfaccion_promedio << "/10\n\n";
    
    std::cout << "🎯 MI RECOMENDACIÓN PERSONALIZADA:\n\n";
    std::cout << "Basado en tu perfil (desarrollador, presupuesto limitado, Linux):\n\n";
    
    if (mejor_valor.nombre.find("AMD") != std::string::npos) {
        std::cout << "🥇 " << mejor_valor.nombre << " es tu mejor opción porque:\n";
        std::cout << "   ✓ Excelente para desarrollo con Linux\n";
        std::cout << "   ✓ 16GB RAM resolverán tu problema actual\n";
        std::cout << "   ✓ Nuevo = menos problemas\n";
        std::cout << "   ✓ Buena disponibilidad en tu presupuesto\n";
    } else if (mejor_valor.nombre.find("ThinkPad") != std::string::npos) {
        std::cout << "🥇 " << mejor_valor.nombre << " es tu mejor opción porque:\n";
        std::cout << "   ✓ Legendaria compatibilidad con Linux\n";
        std::cout << "   ✓ Todo incluido (no necesitas pantalla)\n";
        std::cout << "   ✓ Portabilidad para trabajar donde quieras\n";
        std::cout << "   ✓ 16GB RAM resolverán tu problema\n";
    } else {
        std::cout << "🥇 " << mejor_valor.nombre << " según la simulación\n";
    }
    
    std::cout << "\n💡 FACTORES CLAVE PARA TU DECISIÓN:\n";
    std::cout << "   • Portabilidad: CRÍTICA (trabajas desde cualquier lugar)\n";
    std::cout << "   • Downtime: Cuesta $25/hora (freelance)\n";
    std::cout << "   • Estrés: Confiabilidad > precio inicial\n";
    std::cout << "   • Cuotas: Puedes generar dinero suficiente → opciones premium viables\n";
    std::cout << "   • ROI: Considera valor total a 2 años (no solo precio inicial)\n\n";
    
    std::cout << "🔧 PRÓXIMOS PASOS:\n";
    std::cout << "1. Buscar ofertas específicas de tu opción favorita\n";
    std::cout << "2. Verificar disponibilidad local o envío\n";
    std::cout << "3. Considerar garantías y return policy\n";
    std::cout << "4. ¡Ejecutar la decisión!\n\n";
    
    return 0;
}