#include <iostream>
#include <random>
#include <vector>
#include <string>
#include <iomanip>

/**
 * @brief Versión interactiva del simulador de decisión de auto
 * 
 * Esta versión te permite personalizar los parámetros según tu situación:
 * - Tu presupuesto específico
 * - Tus prioridades (costo vs satisfacción vs confiabilidad)
 * - Km que manejas por año
 * - Años que planeas tener el auto
 * - Tu tolerancia al riesgo
 */

class SimuladorAutoPersonalizado {
private:
    struct PerfilUsuario {
        double presupuesto_maximo;
        double km_anuales;
        int años_propiedad;
        double precio_gasolina;
        
        // Pesos para decisión (deben sumar 1.0)
        double peso_costo;        // Qué tan importante es el costo
        double peso_satisfaccion; // Qué tan importante es la satisfacción
        double peso_confiabilidad; // Qué tan importante es la confiabilidad
        
        double tolerancia_riesgo; // 0.0 = averso al riesgo, 1.0 = amante del riesgo
    };
    
    struct AutoSimple {
        std::string nombre;
        double precio;
        double costo_anual_mantenimiento;
        double consumo_combustible; // L/100km
        double satisfaccion; // 1-10
        double confiabilidad; // 0-1 (probabilidad de NO tener problemas)
        double depreciacion_anual; // porcentaje
    };
    
    PerfilUsuario perfil_;
    std::vector<AutoSimple> autos_;
    std::mt19937 gen_;
    
public:
    SimuladorAutoPersonalizado() : gen_(std::random_device{}()) {}
    
    void configurarPerfil() {
        std::cout << "🔧 CONFIGURACIÓN PERSONALIZADA\n";
        std::cout << "Responde las siguientes preguntas para personalizar la simulación:\n\n";
        
        std::cout << "1. ¿Cuál es tu presupuesto máximo para el auto? $";
        std::cin >> perfil_.presupuesto_maximo;
        
        std::cout << "2. ¿Aproximadamente cuántos km manejas por año? ";
        std::cin >> perfil_.km_anuales;
        
        std::cout << "3. ¿Por cuántos años planeas tener el auto? ";
        std::cin >> perfil_.años_propiedad;
        
        std::cout << "4. ¿Cuánto cuesta la gasolina por litro en tu área? $";
        std::cin >> perfil_.precio_gasolina;
        
        std::cout << "\n🎯 PRIORIDADES (del 1 al 10, donde 10 es muy importante):\n";
        double costo_raw, satisfaccion_raw, confiabilidad_raw;
        
        std::cout << "5. ¿Qué tan importante es el COSTO TOTAL para ti? (1-10): ";
        std::cin >> costo_raw;
        
        std::cout << "6. ¿Qué tan importante es la SATISFACCIÓN/LUJO para ti? (1-10): ";
        std::cin >> satisfaccion_raw;
        
        std::cout << "7. ¿Qué tan importante es la CONFIABILIDAD para ti? (1-10): ";
        std::cin >> confiabilidad_raw;
        
        // Normalizar pesos
        double total = costo_raw + satisfaccion_raw + confiabilidad_raw;
        perfil_.peso_costo = costo_raw / total;
        perfil_.peso_satisfaccion = satisfaccion_raw / total;
        perfil_.peso_confiabilidad = confiabilidad_raw / total;
        
        std::cout << "8. ¿Cuál es tu tolerancia al riesgo? (0=conservador, 10=arriesgado): ";
        double tolerancia_raw;
        std::cin >> tolerancia_raw;
        perfil_.tolerancia_riesgo = tolerancia_raw / 10.0;
        
        std::cout << "\n✅ Perfil configurado!\n\n";
    }
    
    void mostrarPerfil() {
        std::cout << "👤 TU PERFIL:\n";
        std::cout << "• Presupuesto máximo: $" << std::fixed << std::setprecision(0) 
                  << perfil_.presupuesto_maximo << "\n";
        std::cout << "• Km anuales: " << perfil_.km_anuales << "\n";
        std::cout << "• Años de propiedad: " << perfil_.años_propiedad << "\n";
        std::cout << "• Precio gasolina: $" << std::setprecision(2) << perfil_.precio_gasolina << "/L\n";
        std::cout << "• Prioridad costo: " << std::setprecision(1) << perfil_.peso_costo * 100 << "%\n";
        std::cout << "• Prioridad satisfacción: " << perfil_.peso_satisfaccion * 100 << "%\n";
        std::cout << "• Prioridad confiabilidad: " << perfil_.peso_confiabilidad * 100 << "%\n";
        std::cout << "• Tolerancia al riesgo: " << perfil_.tolerancia_riesgo * 100 << "%\n\n";
    }
    
    void configurarAutos() {
        // Filtrar autos que estén dentro del presupuesto
        std::vector<AutoSimple> todos_los_autos = {
            {"Nissan Versa 2024", 280000, 8000, 7.5, 7.0, 0.90, 0.15},
            {"Toyota Corolla 2024", 320000, 7000, 6.8, 7.5, 0.95, 0.12},
            {"Honda Civic 2024", 420000, 10000, 6.8, 8.2, 0.93, 0.12},
            {"Mazda 3 2024", 380000, 9000, 7.2, 8.0, 0.91, 0.13},
            {"Volkswagen Jetta 2024", 390000, 12000, 7.0, 7.8, 0.88, 0.14},
            {"BMW Serie 3 2024", 850000, 25000, 8.5, 9.1, 0.96, 0.18},
            {"Mercedes C-Class 2024", 900000, 28000, 8.8, 9.2, 0.95, 0.19},
            {"Audi A4 2024", 820000, 24000, 8.2, 8.9, 0.94, 0.17},
            {"Toyota Corolla 2020 (Usado)", 220000, 10000, 7.0, 7.2, 0.89, 0.10},
            {"Honda Civic 2019 (Usado)", 280000, 12000, 7.5, 7.8, 0.85, 0.11},
            {"Nissan Sentra 2024", 290000, 8500, 7.2, 7.2, 0.89, 0.14}
        };
        
        for (const auto& auto_opcion : todos_los_autos) {
            if (auto_opcion.precio <= perfil_.presupuesto_maximo) {
                autos_.push_back(auto_opcion);
            }
        }
        
        std::cout << "🚗 AUTOS DENTRO DE TU PRESUPUESTO:\n";
        for (size_t i = 0; i < autos_.size(); ++i) {
            std::cout << "   " << (i + 1) << ". " << autos_[i].nombre 
                      << " - $" << std::fixed << std::setprecision(0) << autos_[i].precio << "\n";
        }
        std::cout << "\n";
    }
    
    struct ResultadoPersonalizado {
        std::string nombre;
        double costo_total;
        double valor_residual;
        double costo_neto;
        double puntuacion_personalizada;
        double riesgo_financiero;
    };
    
    std::vector<ResultadoPersonalizado> simular(int num_simulaciones = 10000) {
        std::vector<ResultadoPersonalizado> resultados;
        
        std::cout << "🎲 Ejecutando " << num_simulaciones << " simulaciones personalizadas...\n\n";
        
        for (const auto& auto_opcion : autos_) {
            ResultadoPersonalizado resultado;
            resultado.nombre = auto_opcion.nombre;
            
            double suma_costo_neto = 0;
            double suma_puntuacion = 0;
            std::vector<double> costos_netos;
            
            for (int i = 0; i < num_simulaciones; ++i) {
                // Simular un escenario
                double costo_total = simularCostoTotal(auto_opcion);
                double valor_residual = simularValorResidual(auto_opcion);
                double costo_neto = costo_total - valor_residual;
                
                suma_costo_neto += costo_neto;
                costos_netos.push_back(costo_neto);
                
                // Calcular puntuación personalizada
                double puntuacion = calcularPuntuacionPersonalizada(auto_opcion, costo_neto);
                suma_puntuacion += puntuacion;
            }
            
            resultado.costo_neto = suma_costo_neto / num_simulaciones;
            resultado.puntuacion_personalizada = suma_puntuacion / num_simulaciones;
            
            // Calcular riesgo (desviación estándar de costos)
            double suma_cuadrados = 0;
            for (double costo : costos_netos) {
                double diff = costo - resultado.costo_neto;
                suma_cuadrados += diff * diff;
            }
            resultado.riesgo_financiero = std::sqrt(suma_cuadrados / num_simulaciones);
            
            resultados.push_back(resultado);
        }
        
        return resultados;
    }
    
private:
    double simularCostoTotal(const AutoSimple& auto_opcion) {
        std::normal_distribution<double> dist_mantenimiento(
            auto_opcion.costo_anual_mantenimiento, auto_opcion.costo_anual_mantenimiento * 0.3);
        
        std::normal_distribution<double> dist_consumo(
            auto_opcion.consumo_combustible, auto_opcion.consumo_combustible * 0.1);
        
        double costo_inicial = auto_opcion.precio;
        double costo_mantenimiento_total = 0;
        double costo_combustible_total = 0;
        
        for (int año = 1; año <= perfil_.años_propiedad; ++año) {
            // Mantenimiento (incrementa con los años)
            double factor_edad = 1.0 + (año - 1) * 0.1;
            double costo_mantenimiento_año = std::max(0.0, dist_mantenimiento(gen_) * factor_edad);
            costo_mantenimiento_total += costo_mantenimiento_año;
            
            // Combustible
            double consumo = std::max(5.0, dist_consumo(gen_));
            double litros_año = (perfil_.km_anuales / 100.0) * consumo;
            double costo_combustible_año = litros_año * perfil_.precio_gasolina;
            costo_combustible_total += costo_combustible_año;
        }
        
        return costo_inicial + costo_mantenimiento_total + costo_combustible_total;
    }
    
    double simularValorResidual(const AutoSimple& auto_opcion) {
        std::normal_distribution<double> dist_depreciacion(
            auto_opcion.depreciacion_anual, auto_opcion.depreciacion_anual * 0.2);
        
        double valor_actual = auto_opcion.precio;
        
        for (int año = 1; año <= perfil_.años_propiedad; ++año) {
            double tasa_depreciacion = std::max(0.05, dist_depreciacion(gen_));
            tasa_depreciacion = std::min(0.30, tasa_depreciacion);
            valor_actual *= (1.0 - tasa_depreciacion);
        }
        
        return valor_actual;
    }
    
    double calcularPuntuacionPersonalizada(const AutoSimple& auto_opcion, double costo_neto) {
        // Normalizar costo (menor es mejor)
        double factor_costo = 1.0 / (1.0 + costo_neto / 100000.0);
        
        // Factor satisfacción (mayor es mejor)
        double factor_satisfaccion = auto_opcion.satisfaccion / 10.0;
        
        // Factor confiabilidad (mayor es mejor)
        double factor_confiabilidad = auto_opcion.confiabilidad;
        
        // Combinar según las prioridades del usuario
        return perfil_.peso_costo * factor_costo +
               perfil_.peso_satisfaccion * factor_satisfaccion +
               perfil_.peso_confiabilidad * factor_confiabilidad;
    }
    
public:
    void mostrarResultados(const std::vector<ResultadoPersonalizado>& resultados) {
        // Ordenar por puntuación personalizada
        auto resultados_ordenados = resultados;
        std::sort(resultados_ordenados.begin(), resultados_ordenados.end(),
                  [](const ResultadoPersonalizado& a, const ResultadoPersonalizado& b) {
                      return a.puntuacion_personalizada > b.puntuacion_personalizada;
                  });
        
        std::cout << "🎯 RESULTADOS PERSONALIZADOS PARA TU PERFIL:\n";
        std::cout << std::string(60, '=') << "\n\n";
        
        for (size_t i = 0; i < resultados_ordenados.size(); ++i) {
            const auto& r = resultados_ordenados[i];
            
            std::cout << "🏆 #" << (i + 1) << ": " << r.nombre << "\n";
            std::cout << "   💰 Costo neto promedio: $" << std::fixed << std::setprecision(0) 
                      << r.costo_neto << " (" << r.costo_neto / perfil_.años_propiedad << "/año)\n";
            std::cout << "   📊 Puntuación personalizada: " << std::setprecision(3) 
                      << r.puntuacion_personalizada << "\n";
            std::cout << "   ⚠️  Riesgo financiero: ±$" << std::setprecision(0) 
                      << r.riesgo_financiero << "\n";
            
            // Ajustar recomendación basada en tolerancia al riesgo
            if (r.riesgo_financiero > 50000 && perfil_.tolerancia_riesgo < 0.5) {
                std::cout << "   🔴 ALTO RIESGO para tu perfil conservador\n";
            } else if (r.riesgo_financiero < 30000 && perfil_.tolerancia_riesgo > 0.7) {
                std::cout << "   🟡 Quizás demasiado conservador para tu perfil\n";
            } else {
                std::cout << "   🟢 Riesgo adecuado para tu perfil\n";
            }
            std::cout << "\n";
        }
        
        std::cout << "✅ RECOMENDACIÓN FINAL PERSONALIZADA: " << resultados_ordenados[0].nombre << "\n\n";
    }
};

int main() {
    std::cout << "🚗 === SIMULADOR PERSONALIZADO DE DECISIÓN DE AUTO === 🚗\n\n";
    
    SimuladorAutoPersonalizado simulador;
    
    // Configurar perfil del usuario
    simulador.configurarPerfil();
    simulador.mostrarPerfil();
    
    // Configurar autos disponibles según presupuesto
    simulador.configurarAutos();
    
    // Ejecutar simulación
    auto resultados = simulador.simular(5000);
    
    // Mostrar resultados personalizados
    simulador.mostrarResultados(resultados);
    
    std::cout << "💡 RECUERDA:\n";
    std::cout << "• Esta simulación está personalizada para TU situación específica\n";
    std::cout << "• Considera también factores emocionales y prácticos no cuantificables\n";
    std::cout << "• Siempre prueba el auto antes de comprarlo\n";
    std::cout << "• Verifica el historial si es usado\n\n";
    
    std::cout << "🎉 ¡Toma tu decisión con confianza basada en datos!\n";
    
    return 0;
}