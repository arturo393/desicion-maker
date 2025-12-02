# 🎯 Framework Unificado de Decisiones

## Introducción

Este framework combina lo mejor de **tres arquitecturas diferentes** encontradas en los ejemplos:

1. **OOP** (`business_decision_v2_enhanced.cpp`): Extensibilidad con clases
2. **Procedural** (`decision_jeep_logistica.cpp`): Robustez en simulación
3. **Flat** (`decision_computadora_arturo.cpp`): Simplicidad y realismo

El resultado es un **header-only framework** en C++17 que soporta **5 metodologías de decisión**.

---

## 🚀 Inicio Rápido

### Instalación

```bash
# Solo copia el header en tu proyecto
cp src/unified_decision_framework.h tu_proyecto/include/
```

### Ejemplo Mínimo

```cpp
#include "unified_decision_framework.h"
using namespace DecisionFramework;

int main() {
    // 1. Crear engine
    MonteCarloEngine engine;
    engine.setNumSimulations(10000);
    
    // 2. Agregar factores
    engine.addFactor(Factor("Costo", "Económico", 0.4, false));
    engine.addFactor(Factor("Calidad", "Rendimiento", 0.6, true));
    
    // 3. Crear opción
    DecisionOption opcion("Laptop A", "Laptop económico");
    opcion.addVariable("Costo", UncertainVariable("costo", 
                       DistributionType::NORMAL, 1000, 100));
    opcion.addVariable("Calidad", UncertainVariable("calidad",
                       DistributionType::TRIANGULAR, 6, 7, 9));
    
    // 4. Definir simulador
    opcion.setSimulator([](const auto& values, std::mt19937& gen) {
        SimulationResult result;
        result.factor_values = values;
        result.success = true;
        return result;
    });
    
    // 5. Ejecutar
    engine.addOption(opcion);
    auto results = engine.run();
    
    // 6. Mostrar resultados
    printComparison(results);
    
    return 0;
}
```

**Compilar:**
```bash
g++ -std=c++17 -O2 mi_decision.cpp -o mi_decision
```

---

## 📊 Metodologías Soportadas

### 1. Monte Carlo (incertidumbre)
```cpp
MonteCarloEngine mc;
mc.setNumSimulations(10000);
// ... agregar opciones ...
auto results = mc.run();
```

**Cuándo usar:** Incertidumbre, probabilidades, riesgo

### 2. TOPSIS (determinístico)
```cpp
TOPSISAnalyzer topsis;
topsis.setOptions({"A", "B", "C"});
topsis.setFactors({"Costo", "Calidad"}, {0.4, 0.6}, {false, true});
topsis.setDecisionMatrix({{1000, 7}, {1200, 9}, {800, 5}});
auto scores = topsis.analyze();
```

**Cuándo usar:** Valores conocidos, ranking rápido

### 3. Pareto (multi-objetivo)
```cpp
ParetoAnalyzer pareto;
std::vector<Point> points = {
    {"A", {1000, 7, 0.9}, false},
    {"B", {1200, 9, 0.95}, false}
};
auto front = pareto.findParetoFront(points, {false, true, true});
```

**Cuándo usar:** Conflicto entre objetivos, no sabes pesos

### 4. Árboles de Decisión (secuencial)
```cpp
DecisionNode root("Comprar ahora", DecisionNode::Type::DECISION, 0);
auto chance = std::make_shared<DecisionNode>("Falla", 
              DecisionNode::Type::CHANCE, 0.2);
root.addChild(chance);
```

**Cuándo usar:** Decisiones en etapas

### 5. Análisis de Sensibilidad (validación)
```cpp
auto sensitivities = engine.sensitivityAnalysis("Opción A");
// Retorna impacto de cada factor
```

**Cuándo usar:** Siempre (validación de robustez)

---

## 🎓 Arquitectura

### Componentes Principales

```
unified_decision_framework.h
│
├── UncertainVariable          // Variables con incertidumbre
│   ├── DistributionType       // Normal, Uniform, Triangular, etc.
│   └── sample()               // Genera valor aleatorio
│
├── Factor                     // Criterios de decisión
│   ├── name                   // Nombre del factor
│   ├── weight                 // Importancia (0-1)
│   └── maximize               // Maximizar o minimizar
│
├── SimulationResult           // Resultado de una simulación
│   ├── factor_values          // Valores de factores
│   ├── events                 // Eventos ocurridos
│   └── total_score            // Puntaje final
│
├── Statistics                 // Estadísticas agregadas
│   ├── mean, stddev           // Media, desviación estándar
│   ├── min, max               // Rango
│   └── p5, p95                // Percentiles
│
├── DecisionOption             // Opción de decisión
│   ├── variables_             // Variables inciertas
│   ├── simulator_             // Lógica custom
│   └── simulate()             // Ejecuta una simulación
│
├── MonteCarloEngine           // Motor de simulación
│   ├── options_               // Opciones a comparar
│   ├── factors_               // Factores de decisión
│   ├── run()                  // Ejecuta simulaciones
│   └── sensitivityAnalysis()  // Análisis de sensibilidad
│
├── TOPSISAnalyzer             // Análisis determinístico
│   └── analyze()              // Calcula proximidad al ideal
│
├── ParetoAnalyzer             // Análisis multi-objetivo
│   └── findParetoFront()      // Encuentra frontera óptima
│
└── DecisionNode               // Árboles de decisión
    ├── Type (DECISION/CHANCE) // Tipo de nodo
    └── children               // Nodos hijos
```

### Tipos de Distribuciones

```cpp
enum class DistributionType {
    DETERMINISTIC,  // Valor fijo (sin incertidumbre)
    NORMAL,         // Gaussiana: μ ± σ
    UNIFORM,        // Uniforme: [min, max]
    TRIANGULAR,     // Triangular: (min, mode, max)
    BERNOULLI,      // Binaria: probabilidad p
    EXPONENTIAL,    // Exponencial: eventos raros
    BETA            // Beta: valores 0-1 con forma
};
```

**¿Cuál usar?**

- **Normal:** Cuando conoces media y desviación (precios, tiempos)
- **Uniform:** Sin sesgo, cualquier valor igualmente probable
- **Triangular:** Más realista (min, más probable, max)
- **Bernoulli:** Eventos sí/no (fallas, éxito/fracaso)
- **Exponential:** Tiempos de espera, eventos raros
- **Beta:** Proporciones, porcentajes (0-1)

---

## 📚 Ejemplos Completos

### Ejemplo 1: Decisión de Computadora
```bash
g++ -std=c++17 -O2 examples/unified_example.cpp -o bin/unified_example
./bin/unified_example
```

Muestra:
- ✅ Monte Carlo con incertidumbre
- ✅ TOPSIS para ranking rápido
- ✅ Pareto para trade-offs
- ✅ Recomendaciones por metodología

### Ejemplo 2: Migrar Ejemplo Existente

**Antes** (`decision_computadora_arturo.cpp`):
```cpp
struct OpcionComputadora {
    double costo_base;
    double prob_downtime;
    // ... 20 campos más ...
};

ResultadoSimulacion simular_opcion(OpcionComputadora opt, /* ... */) {
    // 150 líneas de lógica custom
}
```

**Después** (framework unificado):
```cpp
DecisionOption opcion("MacBook 2019", "Laptop actual");

opcion.addVariable("costo", UncertainVariable("costo",
                   DistributionType::TRIANGULAR, 800, 1200, 2000));

opcion.setSimulator([](const auto& values, std::mt19937& gen) {
    SimulationResult result;
    result.factor_values = values;
    
    // Tu lógica custom aquí (más concisa)
    std::bernoulli_distribution downtime_dist(0.95);
    result.events["Downtime"] = downtime_dist(gen);
    
    return result;
});
```

**Beneficios:**
- 📉 60% menos líneas de código
- 🔄 Reutilización de componentes
- 📊 Soporte de múltiples metodologías (no solo Monte Carlo)
- 🎯 Separación clara: datos vs lógica vs presentación

---

## 🔬 Análisis de Sensibilidad

### ¿Para qué sirve?

Identifica **qué factores importan más** en tu decisión.

### Ejemplo:

```cpp
MonteCarloEngine mc;
// ... configurar opciones ...

auto results = mc.run();
auto sens = mc.sensitivityAnalysis("Opción A");

// Salida:
// portabilidad: 0.85 (muy importante)
// costo: 0.62 (importante)
// ecosistema: 0.23 (poco importante)
```

**Interpretación:**
- **0.8-1.0:** Factor crítico (cambios pequeños afectan mucho)
- **0.4-0.8:** Factor importante (vale la pena optimizar)
- **0.0-0.4:** Factor secundario (no afecta decisión significativamente)

**Acción:**
- Enfoca esfuerzo en factores críticos (0.8+)
- Ignora factores secundarios (<0.4)

---

## 🎯 Estrategia Combinada (Recomendada)

Para decisiones complejas:

```cpp
// PASO 1: TOPSIS (pre-filtrado rápido)
TOPSISAnalyzer topsis;
// ... configurar ...
auto topsis_scores = topsis.analyze();
// → Descartar opciones con score < 0.3

// PASO 2: PARETO (identificar trade-offs)
ParetoAnalyzer pareto;
// ... configurar solo opciones filtradas ...
auto pareto_front = pareto.findParetoFront(points, {false, true, true});
// → Reducir a frontera óptima (3-5 opciones)

// PASO 3: MONTE CARLO (análisis detallado)
MonteCarloEngine mc;
// ... configurar solo opciones de frontera Pareto ...
auto mc_results = mc.run();
// → Simular incertidumbre con 10,000 iteraciones

// PASO 4: SENSIBILIDAD (validación)
auto sens = mc.sensitivityAnalysis("Mejor opción");
// → Verificar que decisión es robusta

// DECISIÓN FINAL
std::cout << "Ganador: " << mc_results.begin()->first << "\n";
std::cout << "Factores críticos: ";
for (const auto& [factor, impact] : sens) {
    if (impact > 0.7) std::cout << factor << " ";
}
```

---

## 📊 Comparación de Métodos

| Característica | Monte Carlo | TOPSIS | Pareto | Árboles | Sensibilidad |
|----------------|-------------|--------|--------|---------|--------------|
| **Velocidad** | 🐢 Lento (min) | ⚡ Rápido (ms) | 🏃 Medio (seg) | 🏃 Medio | ⚡ Rápido |
| **Incertidumbre** | ✅ Sí | ❌ No | ❌ No | ⚠️ Limitado | ✅ Valida |
| **Requiere pesos** | ✅ Sí | ✅ Sí | ❌ No | ❌ No | ✅ Sí |
| **Múltiples objetivos** | ⚠️ Con pesos | ⚠️ Con pesos | ✅ Nativo | ❌ No | ❌ No |
| **Secuencialidad** | ❌ No | ❌ No | ❌ No | ✅ Sí | ❌ No |
| **Salida** | Distribución | Ranking | Frontera | Árbol | Impactos |

**Recomendación general:**
- **Simple:** TOPSIS (1 método)
- **Medio:** Monte Carlo + Sensibilidad (2 métodos)
- **Completo:** TOPSIS → Pareto → Monte Carlo → Sensibilidad (4 métodos)

---

## 🛠️ API Completa

### MonteCarloEngine

```cpp
MonteCarloEngine mc;

// Configuración
mc.setNumSimulations(10000);  // Default: 10000
mc.addFactor(Factor(...));    // Agregar criterio
mc.addOption(DecisionOption(...)); // Agregar opción

// Ejecución
auto results = mc.run();      // Retorna map<string, Statistics>

// Análisis
auto sens = mc.sensitivityAnalysis("Opción A");
```

### DecisionOption

```cpp
DecisionOption opt("ID", "Descripción");

// Variables inciertas
opt.addVariable("costo", UncertainVariable(...));
opt.addVariable("tiempo", UncertainVariable(...));

// Simulador custom
opt.setSimulator([](const auto& values, std::mt19937& gen) {
    SimulationResult result;
    // Tu lógica aquí
    return result;
});

// Ejecutar una simulación
auto result = opt.simulate(gen, factors);
```

### UncertainVariable

```cpp
UncertainVariable var("nombre", DistributionType::NORMAL, mean, stddev);

// Generar valor aleatorio
double value = var.sample(gen);
```

### TOPSISAnalyzer

```cpp
TOPSISAnalyzer topsis;

topsis.setOptions({"A", "B", "C"});
topsis.setFactors({"Costo", "Calidad"}, {0.4, 0.6}, {false, true});
topsis.setDecisionMatrix({{1000, 7}, {1200, 9}});

auto scores = topsis.analyze();  // map<string, double>
```

### ParetoAnalyzer

```cpp
ParetoAnalyzer pareto;

std::vector<Point> points = {
    {"A", {costo_A, calidad_A, prod_A}, false},
    // ...
};

auto front = pareto.findParetoFront(points, 
                                    {false, true, true}); // min, max, max
```

---

## 📖 Documentación Adicional

- **[Guía de Metodologías](docs/METODOLOGIAS_ALTERNATIVAS.md)** - Cuándo usar cada método
- **[Ejemplos Completos](examples/)** - Casos de uso reales
- **[Migración desde Código Antiguo](docs/MIGRATION_GUIDE.md)** - Cómo refactorizar

---

## 🤝 Contribuir

1. Fork del proyecto
2. Crear rama de feature (`git checkout -b feature/nueva-metodologia`)
3. Commit cambios (`git commit -am 'Agrega Bayesiano'`)
4. Push a rama (`git push origin feature/nueva-metodologia`)
5. Crear Pull Request

---

## 📝 Licencia

MIT License - ve [LICENSE](LICENSE) para detalles

---

## 🙏 Agradecimientos

Este framework combina ideas de:
- Monte Carlo: Metropolis & Ulam (1949)
- TOPSIS: Hwang & Yoon (1981)
- Pareto: Vilfredo Pareto (1896)
- Decision Trees: Howard Raiffa (1968)

Ejemplos originales:
- `business_decision_v2_enhanced.cpp` (OOP)
- `decision_jeep_logistica.cpp` (Procedural)
- `decision_computadora_arturo.cpp` (Flat)

---

**Versión:** 1.0  
**Autor:** Arturo  
**Fecha:** Diciembre 2025  
**Repositorio:** https://github.com/usuario/decision-maker
