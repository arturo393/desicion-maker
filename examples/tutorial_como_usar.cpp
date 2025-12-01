#include <iostream>
#include <random>
#include <vector>
#include <string>
#include <iomanip>

/**
 * EJEMPLO PRÁCTICO: ¿Qué laptop comprar?
 * 
 * Te enseño PASO A PASO cómo usar Monte Carlo para cualquier decisión
 */

struct Laptop {
    std::string nombre;
    double precio_inicial;
    double duracion_promedio_años;      // Cuánto esperamos que dure
    double variabilidad_duracion;       // Incertidumbre en la duración
    double costo_reparacion_anual;      // Costo esperado de reparaciones
    double satisfaccion_inicial;        // Del 1 al 10
    double depreciacion_anual;          // % que pierde valor cada año
};

// Función que simula UN escenario (ej: un futuro posible)
struct ResultadoLaptop {
    double costo_total_propiedad;      // Precio + reparaciones - valor residual
    double años_de_uso;                // Cuánto duró realmente
    double satisfaccion_promedio;      // Qué tan feliz estuviste
    bool necesito_reemplazo_temprano;  // ¿Se descompuso antes de tiempo?
};

ResultadoLaptop simular_laptop(const Laptop& laptop, std::mt19937& gen) {
    // 1. SIMULAR DURACIÓN (con incertidumbre)
    std::normal_distribution<double> dist_duracion(
        laptop.duracion_promedio_años, 
        laptop.variabilidad_duracion
    );
    double años_uso = std::max(1.0, dist_duracion(gen)); // Mínimo 1 año
    años_uso = std::min(8.0, años_uso); // Máximo 8 años
    
    // 2. SIMULAR COSTOS DE REPARACIÓN (cada año puede variar)
    std::exponential_distribution<double> dist_reparacion(1.0 / laptop.costo_reparacion_anual);
    double costos_reparacion_total = 0;
    
    for (int año = 1; año <= (int)años_uso; ++año) {
        // Probabilidad de reparación aumenta con la edad
        double probabilidad_reparacion = 0.1 + (año - 1) * 0.05; // 10% primer año, +5% cada año
        std::uniform_real_distribution<double> prob_dist(0.0, 1.0);
        
        if (prob_dist(gen) < probabilidad_reparacion) {
            costos_reparacion_total += dist_reparacion(gen);
        }
    }
    
    // 3. CALCULAR VALOR RESIDUAL (depreciación)
    double valor_residual = laptop.precio_inicial;
    for (int año = 1; año <= (int)años_uso; ++año) {
        valor_residual *= (1.0 - laptop.depreciacion_anual);
    }
    
    // 4. SIMULAR SATISFACCIÓN (puede cambiar con el tiempo)
    std::normal_distribution<double> dist_satisfaccion(laptop.satisfaccion_inicial, 1.0);
    double satisfaccion_promedio = std::max(1.0, dist_satisfaccion(gen));
    satisfaccion_promedio = std::min(10.0, satisfaccion_promedio);
    
    // 5. CALCULAR COSTO TOTAL DE PROPIEDAD
    double costo_total = laptop.precio_inicial + costos_reparacion_total - valor_residual;
    
    // 6. ¿NECESITÉ REEMPLAZARLO TEMPRANO?
    bool reemplazo_temprano = años_uso < (laptop.duracion_promedio_años * 0.8);
    
    return {costo_total, años_uso, satisfaccion_promedio, reemplazo_temprano};
}

void explicar_proceso() {
    std::cout << "🎓 CÓMO FUNCIONA MONTE CARLO PARA TOMAR DECISIONES:\n\n";
    
    std::cout << "1️⃣ DEFINES TU PROBLEMA:\n";
    std::cout << "   Tienes que elegir entre varias opciones (laptops, autos, trabajos, etc.)\n\n";
    
    std::cout << "2️⃣ IDENTIFICAS LAS INCERTIDUMBRES:\n";
    std::cout << "   ✓ ¿Cuánto durará cada opción?\n";
    std::cout << "   ✓ ¿Qué costos extras tendré?\n";
    std::cout << "   ✓ ¿Qué tan satisfecho estaré?\n";
    std::cout << "   ✓ ¿Cuánto valdrá después?\n\n";
    
    std::cout << "3️⃣ EJECUTAS SIMULACIONES:\n";
    std::cout << "   El programa simula 10,000 futuros posibles para cada opción\n";
    std::cout << "   En cada simulación, las variables cambian aleatoriamente\n\n";
    
    std::cout << "4️⃣ ANALIZAS RESULTADOS:\n";
    std::cout << "   ✓ ¿Cuál tiene menor costo promedio?\n";
    std::cout << "   ✓ ¿Cuál es más confiable?\n";
    std::cout << "   ✓ ¿Cuál da más satisfacción?\n\n";
    
    std::cout << "5️⃣ TOMAS LA DECISIÓN:\n";
    std::cout << "   Basada en DATOS y PROBABILIDADES, no en corazonadas\n\n";
    
    std::cout << std::string(60, '=') << "\n\n";
}

int main() {
    std::cout << "💻 === EJEMPLO: ¿QUÉ LAPTOP COMPRAR? ===\n\n";
    
    explicar_proceso();
    
    // DEFINIR LAS OPCIONES (aquí pones TUS opciones reales)
    std::vector<Laptop> opciones = {
        {
            "MacBook Pro M3", 
            30000,    // precio inicial
            5.5,      // dura ~5.5 años en promedio
            1.0,      // variabilidad: entre 4.5 y 6.5 años
            800,      // reparaciones: ~$800/año
            9.0,      // satisfacción inicial alta
            0.15      // 15% depreciación anual
        },
        {
            "Dell XPS 13",
            15000,    // precio inicial
            4.0,      // dura ~4 años en promedio
            0.8,      // menos variabilidad
            1200,     // reparaciones más caras (Windows)
            7.5,      // satisfacción media-alta
            0.20      // 20% depreciación anual
        },
        {
            "HP Pavilion",
            12000,    // precio inicial
            3.0,      // dura ~3 años
            0.5,      // duración más predecible
            1500,     // reparaciones frecuentes
            6.5,      // satisfacción media
            0.25      // 25% depreciación anual
        }
    };
    
    const int num_simulaciones = 10000;
    std::random_device rd;
    std::mt19937 gen(rd());
    
    std::cout << "🎲 Ejecutando " << num_simulaciones << " simulaciones para cada laptop...\n\n";
    
    // EJECUTAR SIMULACIONES PARA CADA OPCIÓN
    for (const auto& laptop : opciones) {
        std::cout << "Analizando: " << laptop.nombre << "...\n";
        
        std::vector<double> costos_totales;
        std::vector<double> duraciones;
        std::vector<double> satisfacciones;
        int reemplazos_tempranos = 0;
        
        // Ejecutar muchas simulaciones
        for (int i = 0; i < num_simulaciones; ++i) {
            auto resultado = simular_laptop(laptop, gen);
            
            costos_totales.push_back(resultado.costo_total_propiedad);
            duraciones.push_back(resultado.años_de_uso);
            satisfacciones.push_back(resultado.satisfaccion_promedio);
            
            if (resultado.necesito_reemplazo_temprano) {
                reemplazos_tempranos++;
            }
        }
        
        // CALCULAR ESTADÍSTICAS
        double costo_promedio = 0, duracion_promedio = 0, satisfaccion_promedio = 0;
        for (size_t i = 0; i < costos_totales.size(); ++i) {
            costo_promedio += costos_totales[i];
            duracion_promedio += duraciones[i];
            satisfaccion_promedio += satisfacciones[i];
        }
        costo_promedio /= num_simulaciones;
        duracion_promedio /= num_simulaciones;
        satisfaccion_promedio /= num_simulaciones;
        
        // CALCULAR RIESGO (desviación estándar del costo)
        double suma_cuadrados = 0;
        for (double costo : costos_totales) {
            double diff = costo - costo_promedio;
            suma_cuadrados += diff * diff;
        }
        double riesgo_financiero = std::sqrt(suma_cuadrados / num_simulaciones);
        
        // MOSTRAR RESULTADOS
        std::cout << "\n📊 RESULTADOS PARA " << laptop.nombre << ":\n";
        std::cout << "   💰 Costo total promedio: $" << std::fixed << std::setprecision(0) << costo_promedio << "\n";
        std::cout << "   📅 Duración promedio: " << std::setprecision(1) << duracion_promedio << " años\n";
        std::cout << "   😊 Satisfacción promedio: " << satisfaccion_promedio << "/10\n";
        std::cout << "   ⚠️  Riesgo financiero: ±$" << std::setprecision(0) << riesgo_financiero << "\n";
        std::cout << "   🔧 Prob. reemplazo temprano: " << std::setprecision(1) 
                  << (double)reemplazos_tempranos / num_simulaciones * 100 << "%\n";
        std::cout << "   💵 Costo por año de uso: $" << std::setprecision(0) 
                  << costo_promedio / duracion_promedio << "\n\n";
    }
    
    std::cout << "🎯 ¿CÓMO INTERPRETAR LOS RESULTADOS?\n\n";
    
    std::cout << "✅ MENOR COSTO TOTAL = Opción más económica\n";
    std::cout << "✅ MENOR RIESGO = Opción más predecible\n";
    std::cout << "✅ MAYOR SATISFACCIÓN = Opción que más te gustará\n";
    std::cout << "✅ MENOR COSTO/AÑO = Mejor valor a largo plazo\n\n";
    
    std::cout << "🔧 PARA USAR CON TUS DECISIONES:\n\n";
    std::cout << "1. Cambia las opciones en el código (línea ~65)\n";
    std::cout << "2. Ajusta los parámetros según tu situación\n";
    std::cout << "3. Ejecuta de nuevo: g++ laptop_decision.cpp -o laptop && ./laptop\n";
    std::cout << "4. ¡Toma tu decisión basada en datos!\n\n";
    
    std::cout << "💡 EJEMPLOS DE OTRAS DECISIONES:\n";
    std::cout << "• ¿Qué trabajo aceptar? (salario, crecimiento, satisfacción)\n";
    std::cout << "• ¿Dónde vivir? (renta, tiempo traslado, calidad de vida)\n";
    std::cout << "• ¿Qué carrera estudiar? (costo, salario futuro, demanda)\n";
    std::cout << "• ¿Qué inversión hacer? (retorno, riesgo, liquidez)\n\n";
    
    return 0;
}