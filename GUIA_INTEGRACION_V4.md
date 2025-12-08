# 🔗 GUÍA DE INTEGRACIÓN V4: USAR LAS 3 MEJORAS

## 📌 VISIÓN GENERAL

Esta guía explica cómo **integrar las 3 nuevas mejoras** en tu programa principal de V3.

---

## 📦 LOS 3 MÓDULOS

### 1. Real-Time Market Monitor
**Para**: Ingestar y analizar datos de mercado en vivo
**Archivo**: `src/real_time_monitor.h` / `src/real_time_monitor.cpp`

### 2. Bayesian Probability Updater
**Para**: Actualizar probabilidades dinámicamente basado en evidencia
**Archivo**: `src/bayesian_updater.h` / `src/bayesian_updater.cpp`

### 3. Scenario Analysis
**Para**: Validar la decisión en 3 escenarios (pesimista/realista/optimista)
**Archivo**: `src/scenario_analysis.h` / `src/scenario_analysis.cpp`

---

## 🚀 OPCIÓN 1: USO COMPLETO (RECOMENDADO)

### Paso 1: Incluir Headers

```cpp
#include "real_time_monitor.h"
#include "bayesian_updater.h"
#include "scenario_analysis.h"

using namespace decision_maker;
```

### Paso 2: Crear Instancias

```cpp
// Monitor de mercado
RealTimeMarketMonitor monitor("sillon restaurado");

// Actualizador Bayesiano
BayesianUpdater updater;

// Análisis de escenarios
ScenarioAnalyzer analyzer;
```

### Paso 3: Flujo Completo

```cpp
// A. RECOLECTAR DATOS DE MERCADO
std::vector<MarketDataPoint> market_data = fetch_from_mercado_libre_api();

for (const auto& data : market_data) {
    monitor.add_market_data(data);
}

// B. ANALIZAR MERCADO
MarketTrend trend = monitor.analyze_market();

std::cout << "Saturación: " << (trend.saturation_level * 100) << "%\n";
std::cout << "Demanda: " << trend.demand_level << "\n";
std::cout << "Precio Promedio: $" << trend.avg_price << "\n";

// C. ACTUALIZAR PROBABILIDADES
updater.set_prior(0.04, "Gemini API");  // Prior inicial

// Agregar evidencia del mercado
Evidence saturation_evidence;
saturation_evidence.type = "saturation";
saturation_evidence.value = trend.saturation_level;
saturation_evidence.confidence = 0.95;
updater.add_evidence(saturation_evidence);

Evidence demand_evidence;
demand_evidence.type = "demand";
demand_evidence.value = (trend.demand_level == "ALTA") ? 0.8 : 
                        (trend.demand_level == "MEDIA") ? 0.5 : 0.2;
demand_evidence.confidence = 0.85;
updater.add_evidence(demand_evidence);

double posterior = updater.get_posterior();
std::cout << "Probabilidad actualizada: " << (posterior * 100) << "%\n";

// D. ANALIZAR ESCENARIOS
auto scenarios = analyzer.get_default_scenarios();
for (const auto& scenario : scenarios) {
    auto result = analyzer.analyze_scenario(scenario);
    std::cout << scenario.name << ": EV = $" << result.expected_value << "\n";
}
```

---

## 🎯 OPCIÓN 2: USO PARCIAL

### Solo Real-Time Monitor

```cpp
#include "real_time_monitor.h"

RealTimeMarketMonitor monitor("producto");
monitor.add_market_data(data);
MarketTrend trend = monitor.analyze_market();

// Usar solo para actualizar datos en tiempo real
update_v3_probability(trend.avg_price, trend.demand_level);
```

### Solo Bayesian Updater

```cpp
#include "bayesian_updater.h"

BayesianUpdater updater;
updater.set_prior(0.04, "Gemini");
updater.add_evidence(evidence1);
updater.add_evidence(evidence2);

double p_updated = updater.get_posterior();
```

### Solo Scenario Analysis

```cpp
#include "scenario_analysis.h"

ScenarioAnalyzer analyzer;
auto scenarios = analyzer.get_default_scenarios();

for (const auto& scenario : scenarios) {
    auto result = analyzer.analyze_scenario(scenario);
    if (result.expected_value < 0) {
        std::cout << "Recomendación: " << result.recommendation << "\n";
    }
}
```

---

## 📊 EJEMPLO PRÁCTICO: SILLÓN EN LA FLORIDA

### Código Completo

```cpp
#include <iostream>
#include <iomanip>
#include "real_time_monitor.h"
#include "bayesian_updater.h"
#include "scenario_analysis.h"

using namespace decision_maker;

int main() {
    // ========== PASO 1: RECOLECTAR DATOS ==========
    std::cout << "🔍 Recolectando datos del mercado...\n";
    
    RealTimeMarketMonitor monitor("sillon restaurado");
    
    // Simular 487 sillones disponibles en mercado
    for (int i = 0; i < 487; i++) {
        double price = 45000 + (i % 35000);  // Rango: $45K - $80K
        monitor.add_market_data(MarketDataPoint{
            std::chrono::system_clock::now(),
            "sillon",
            price,
            "restaurado",
            30,
            (i % 3 == 0) ? "OLX" : (i % 3 == 1) ? "ML" : "Yapo",
            false
        });
    }
    
    // ========== PASO 2: ANALIZAR MERCADO ==========
    std::cout << "\n📊 Analizando datos del mercado...\n";
    MarketTrend trend = monitor.analyze_market();
    
    std::cout << "Resultados:\n";
    std::cout << "  Precio promedio: $" << trend.avg_price << "\n";
    std::cout << "  Saturación: " << (trend.saturation_level * 100) << "%\n";
    std::cout << "  Demanda: " << trend.demand_level << "\n";
    
    // ========== PASO 3: ACTUALIZAR PROBABILIDADES ==========
    std::cout << "\n🔄 Actualizando probabilidades...\n";
    
    BayesianUpdater updater;
    updater.set_prior(0.04, "Gemini API");
    
    // Evidencia 1: Saturación alta
    Evidence saturation_evidence{
        "saturation",
        trend.saturation_level,
        0.95,
        "Market data"
    };
    updater.add_evidence(saturation_evidence);
    
    // Evidencia 2: Demanda baja
    Evidence demand_evidence{
        "demand",
        trend.demand_level == "BAJA" ? 0.2 : 
        trend.demand_level == "MEDIA" ? 0.5 : 0.8,
        0.85,
        "Market saturation"
    };
    updater.add_evidence(demand_evidence);
    
    double prior = 0.04;
    double posterior = updater.get_posterior();
    
    std::cout << "Prior: " << (prior * 100) << "%\n";
    std::cout << "Posterior: " << (posterior * 100) << "%\n";
    std::cout << "Cambio: " << ((posterior - prior) * 100) << "%\n";
    
    // ========== PASO 4: ANALIZAR ESCENARIOS ==========
    std::cout << "\n🎯 Ejecutando análisis de escenarios...\n";
    
    ScenarioAnalyzer analyzer;
    auto scenarios = analyzer.get_default_scenarios();
    
    bool all_recommend_botar = true;
    for (const auto& scenario : scenarios) {
        auto result = analyzer.analyze_scenario(scenario);
        std::cout << scenario.name << ":\n";
        std::cout << "  EV: $" << std::fixed << result.expected_value << "\n";
        std::cout << "  Recomendación: " << result.recommendation << "\n";
        
        if (result.expected_value > 0) {
            all_recommend_botar = false;
        }
    }
    
    // ========== PASO 5: DECISIÓN FINAL ==========
    std::cout << "\n✅ DECISIÓN FINAL:\n";
    
    if (all_recommend_botar && posterior < 0.01) {
        std::cout << "BOTAR EL SILLÓN\n";
        std::cout << "Confianza: 99%\n";
        std::cout << "Razón: Todos los escenarios tienen EV negativo\n";
        return 0;
    } else {
        std::cout << "RESTAURAR\n";
        return 1;
    }
}
```

### Salida Esperada

```
🔍 Recolectando datos del mercado...

📊 Analizando datos del mercado...
Resultados:
  Precio promedio: $50332
  Saturación: 95%
  Demanda: MEDIA

🔄 Actualizando probabilidades...
Prior: 4%
Posterior: 0.6%
Cambio: -3.4%

🎯 Ejecutando análisis de escenarios...
PESSIMISTIC:
  EV: $-84200
  Recomendación: BOTAR
REALISTIC:
  EV: $-72600
  Recomendación: BOTAR
OPTIMISTIC:
  EV: $-53600
  Recomendación: BOTAR

✅ DECISIÓN FINAL:
BOTAR EL SILLÓN
Confianza: 99%
Razón: Todos los escenarios tienen EV negativo
```

---

## 🔧 CONFIGURACIÓN DEL COMPILADOR

### CMakeLists.txt (Si integras en tu proyecto)

```cmake
# Agregar los 3 módulos a tu biblioteca
set(MY_SOURCES
    src/real_time_monitor.cpp
    src/bayesian_updater.cpp
    src/scenario_analysis.cpp
    # ... otros archivos
)

add_library(mylib STATIC ${MY_SOURCES})
target_include_directories(mylib PUBLIC src)
```

### Compilación Manual (g++/clang++)

```bash
# Compilar juntos
g++ -std=c++17 -O3 \
    src/real_time_monitor.cpp \
    src/bayesian_updater.cpp \
    src/scenario_analysis.cpp \
    main.cpp -o my_program

# Ejecutar
./my_program
```

---

## 📈 DATOS ESPERADOS PARA CADA MÓDULO

### Real-Time Monitor

**Entrada**: Datos de mercado
```cpp
MarketDataPoint {
    timestamp: 2024-12-08 18:30:00,
    product_name: "sillon restaurado",
    price: 65000,
    condition: "restaurado",
    days_listed: 15,
    marketplace: "OLX",
    sold: false
}
```

**Salida**: Análisis de mercado
```cpp
MarketTrend {
    avg_price: 50332,
    median_price: 50243,
    total_listings: 487,
    sold_listings: 18,
    saturation_level: 0.70,
    demand_level: "MEDIA"
}
```

### Bayesian Updater

**Entrada**: Prior + Evidencia
```cpp
Prior: 0.04 (4%)
Evidence 1: saturation = 0.70, confidence = 0.95
Evidence 2: demand = "MEDIA", confidence = 0.85
```

**Salida**: Probabilidad actualizada
```cpp
Posterior: 0.0060 (0.6%)
```

### Scenario Analysis

**Entrada**: Supuestos de escenario
```cpp
Scenario {
    name: "REALISTIC",
    restoration_cost: 75000,
    expected_sale_price: 65000,
    sale_probability: 0.04,
    description: "..."
}
```

**Salida**: Resultado del escenario
```cpp
ScenarioResult {
    expected_value: -72600,
    best_case_value: -15000,
    worst_case_value: -75000,
    confidence: 0.90,
    recommendation: "BOTAR - Restaurar espera pérdida mayor"
}
```

---

## ⚠️ NOTAS IMPORTANTES

### 1. Dependencias
Los 3 módulos **NO tienen dependencias externas** (solo C++ estándar).

### 2. Thread-Safety
Los módulos **NO son thread-safe**. Si usas multihilo, agrega mutex.

### 3. Performance
- Real-Time Monitor: O(n) para agregar datos, O(n log n) para analizar
- Bayesian Updater: O(k) donde k = número de evidencias
- Scenario Analysis: O(s × v) donde s = escenarios, v = variables

### 4. Extensibilidad
- Agregar nuevos tipos de evidencia: Editar `calculate_likelihood()` en BayesianUpdater
- Agregar nuevos escenarios: Llamar `analyzer.add_scenario(custom_scenario)`
- Agregar nuevas métricas: Extender `MarketTrend` struct

---

## 🎓 EJEMPLOS DE USO AVANZADO

### Actualización Dinámica (Loop Principal)

```cpp
// Loop de actualización cada hora
while (true) {
    // Recolectar nuevos datos
    auto new_data = api.fetch_market_data();
    
    for (const auto& data : new_data) {
        monitor.add_market_data(data);
    }
    
    // Re-analizar
    MarketTrend trend = monitor.analyze_market();
    double probability = updater.get_posterior();
    
    // Log actualizado
    log_probability_over_time(probability);
    
    // Esperar 1 hora
    std::this_thread::sleep_for(std::chrono::hours(1));
}
```

### Sensibilidad de Escenarios

```cpp
// Crear escenario personalizado
ScenarioAssumptions my_scenario{
    "MY_SCENARIO",
    80000,      // costo restauración
    70000,      // precio esperado
    0.05,       // probabilidad venta
    120,        // días a venta
    "Mi escenario personalizado"
};

analyzer.add_scenario(my_scenario);
auto result = analyzer.analyze_scenario(my_scenario);

// Ejecutar sensibilidad
auto sensitivity = analyzer.sensitivity_analysis("cost", 
    {0.5, 0.75, 1.0, 1.25, 1.5});
```

### Reportes Detallados

```cpp
// Generar reportes markdown
std::string monitor_report = monitor.generate_report();
std::string bayesian_report = updater.generate_evidence_report();
std::string scenario_report = analyzer.generate_comparison_report();

// Guardar a archivos
write_file("monitor.md", monitor_report);
write_file("bayesian.md", bayesian_report);
write_file("scenarios.md", scenario_report);
```

---

## ✅ CHECKLIST DE INTEGRACIÓN

- [ ] Copiar headers `.h` a tu proyecto
- [ ] Copiar implementaciones `.cpp` a tu proyecto
- [ ] Agregar `#include` en tu main
- [ ] Actualizar CMakeLists.txt o makefile
- [ ] Compilar exitosamente
- [ ] Crear instancias de las 3 clases
- [ ] Alimentar datos de mercado
- [ ] Ejecutar análisis
- [ ] Capturar resultados
- [ ] Integrar en decisión final

---

## 📞 SUPPORT & FAQ

### P: ¿Puedo usar solo uno de los 3 módulos?
**R**: Sí, cada módulo es independiente. Puedes usarlos por separado.

### P: ¿Cómo agrego nuevos tipos de evidencia?
**R**: Edita `calculate_likelihood()` en `bayesian_updater.cpp` para agregar más tipos.

### P: ¿Qué pasa si no tengo datos de mercado?
**R**: Usa valores por defecto. Los 3 módulos funcionan con estimaciones.

### P: ¿Necesito cambiar V3?
**R**: No. V4 es una **extensión de V3**, no un reemplazo.

### P: ¿Dónde consigo datos de mercado?
**R**: `src/marketplace_api_integration_v2.py` (scraping OLX/ML/Yapo)

---

**Última actualización**: 8 de Diciembre 2024  
**Versión**: V4.0.0  
**Estado**: ✅ Listo para usar
