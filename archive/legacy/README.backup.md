# 🎯 desicion-maker: Framework Decisiones + Plan Minería 2026

> Repositorio integrado: Framework de decisiones automático (C++) + Plan ejecutivo carrera minería + análisis alternativas

[![C++17](https://img.shields.io/badge/C%2B%2B-17-blue.svg)](https://en.cppreference.com/w/cpp/17)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Status: Active](https://img.shields.io/badge/Status-Active%202025-brightgreen.svg)]()
[![Plan: Minería Chile](https://img.shields.io/badge/Plan-Minería%20Chile%202026-blue.svg)](./mineria-2026/)

---

## 🚀 Características

- **🎯 Genérico**: Funciona para cualquier tipo de decisión (negocios, inversiones, personal, etc.)
- **🔌 Extensible**: Arquitectura basada en patrones de diseño (Strategy, Builder, Template Method)
- **⚡ Eficiente**: 40,000+ simulaciones/segundo en hardware moderno
- **📊 Completo**: Estadísticas (mean, P25, P50, P75, success rate, std dev)
- **🧩 Modular**: Componentes desacoplados (factores, evaluadores, simuladores)
- **📝 Header-only**: Fácil integración (`#include "BusinessDecision.h"`)

---

## 📖 Casos de Uso

### ✅ Decisiones de Negocio
- Qué producto lanzar
- En qué mercado entrar
- Qué tecnología adoptar
- [**Ejemplo completo**](examples/business_decision_v2_enhanced.cpp)

### 💰 Inversiones y Finanzas
- Diversificación de portafolio
- Timing de entrada/salida
- Análisis de riesgo/retorno

### 🏡 Decisiones Personales
- Dónde vivir (clima, costo, carrera)
- Qué carrera estudiar
- Comprar vs rentar casa

### 🏢 Estrategia Corporativa
- Contratar vs outsource
- Asociarse vs ir solo
- Pivotar vs perseverar

---

## 🏗️ Arquitectura

```
decision-maker/
├── src/
│   └── scenarios/
│       └── BusinessDecision.h       # Framework genérico (header-only)
├── examples/
│   ├── business_opportunity_analysis.cpp     # Original (4 factores)
│   └── business_decision_v2_enhanced.cpp     # Mejorado (14 factores)
├── bin/                             # Binarios compilados
├── DECISION_NEGOCIO_AUTOMATIZADO.md # Análisis básico
├── ENHANCED_COMPARISON.md           # Comparación y arquitectura
├── EXTENSION_GUIDE.md               # Guía de extensión
└── README.md                        # Este archivo
```

---

## 🎨 Patrones de Diseño Implementados

### 1️⃣ **Strategy Pattern** (Factores de Decisión)

```cpp
class DecisionFactor {
public:
    virtual double evaluate() const = 0;  // Interfaz común
};

class NumericFactor : public DecisionFactor {
    // Valor fijo
};

class StochasticFactor : public DecisionFactor {
    // Valor con variabilidad (distribución normal)
};

class CompositeFactor : public DecisionFactor {
    // Combina múltiples subfactores
};
```

### 2️⃣ **Builder Pattern** (Construcción Fluida)

```cpp
DecisionOptionBuilder builder("yield_farming", "Monitor DeFi");
builder.setRNG(&rng)
    .setDescription("Dashboard para yields")
    .addNumericFactor("Investment", "Financial", 0.98, 1.0)
    .addStochasticFactor("Income", "Financial", 0.50, 0.18, 1.5)
    .addMetadata("capital", 30.0);

auto option = builder.build();
```

### 3️⃣ **Template Method** (Simulación)

```cpp
class MonteCarloSimulator {
public:
    void run() {  // Template method (fijo)
        for (size_t i = 0; i < num_simulations_; ++i) {
            auto result = simulateOnce(option);  // Hook (customizable)
            storeResult(result);
        }
    }
    
protected:
    virtual SimulationResult simulateOnce(DecisionOption& option);
};
```

### 4️⃣ **Strategy Pattern** (Evaluadores)

```cpp
class DecisionEvaluator {
public:
    virtual double evaluate(const DecisionOption& option) const = 0;
};

class WeightedSumEvaluator : public DecisionEvaluator {
    // Suma ponderada simple
};

class MultiCriteriaEvaluator : public DecisionEvaluator {
    // Evaluación por categorías (Financial 30%, Lifestyle 20%, etc.)
};
```

---

## 🛠️ Compilación y Uso

### Requisitos

- **Compilador:** C++17 (GCC 7+, Clang 5+, MSVC 2017+)
- **Dependencias:** STL (ninguna librería externa)

### Compilar ejemplos

```bash
# Crear directorio de binarios
mkdir -p bin

# Compilar ejemplo básico (4 factores)
g++ -std=c++17 -O2 -o bin/business examples/business_opportunity_analysis.cpp

# Compilar ejemplo mejorado (14 factores)
g++ -std=c++17 -O2 -o bin/business_v2 examples/business_decision_v2_enhanced.cpp
```

### Ejecutar

```bash
# Ejemplo básico
./bin/business

# Ejemplo mejorado (10,000 simulaciones por opción)
./bin/business_v2
```

**Salida esperada:**
```
🚀 === SIMULACIÓN MEJORADA: DECISIÓN DE NEGOCIO AUTOMATIZADO === 🚀
Arquitectura Genérica con 10+ Factores Adicionales

🔧 Configurando opciones con factores extendidos...
⚙️  Ejecutando 10000 simulaciones por opción...

====================================================================================================
📊 ANÁLISIS COMPLETO CON 10+ FACTORES ADICIONALES
====================================================================================================

🏆 POSICIÓN #1: Monitor Yield Farming DeFi
   📊 Score Promedio: 0.815
   📈 Rango (P25-P75): 0.798 - 0.832
   ✅ Tasa de Éxito: 100.0%
   ...
```

---

## 📚 Documentación

### 📄 Archivos de Documentación

| Archivo | Descripción |
|---------|-------------|
| [ENHANCED_COMPARISON.md](ENHANCED_COMPARISON.md) | **Análisis comparativo** básico vs mejorado + arquitectura completa |
| [EXTENSION_GUIDE.md](EXTENSION_GUIDE.md) | **Guía de extensión** con ejemplos paso a paso |
| [DECISION_NEGOCIO_AUTOMATIZADO.md](DECISION_NEGOCIO_AUTOMATIZADO.md) | Análisis original (4 factores básicos) |

### 🎓 Ejemplos de Código

#### Ejemplo 1: Factor Personalizado

```cpp
class MarketCompetitionFactor : public NumericFactor {
private:
    double market_saturation_;      // 0-1
    double competitive_advantage_;  // 0-1
    double barrier_to_entry_;       // 0-1
    
public:
    MarketCompetitionFactor(double saturation, double advantage, 
                            double barrier, double weight)
        : NumericFactor("Market Competition", "Market", 0.0, weight)
    {
        // Score: menos saturación + más barreras = mejor
        value_ = (1.0 - market_saturation_) * 0.4 + 
                 competitive_advantage_ * 0.3 + 
                 barrier_to_entry_ * 0.3;
    }
};
```

#### Ejemplo 2: Simulación Completa

```cpp
#include "src/scenarios/BusinessDecision.h"
#include <iostream>

int main() {
    std::mt19937 rng(std::random_device{}());
    MonteCarloSimulator simulator(10000);  // 10k iteraciones
    
    // Configurar opciones
    DecisionOptionBuilder builder("option_a", "Opción A");
    builder.setRNG(&rng)
        .addNumericFactor("Cost", "Financial", 0.8, 1.5)
        .addStochasticFactor("Revenue", "Financial", 0.6, 0.15, 1.8);
    
    simulator.addOption(builder.build());
    
    // Configurar evaluador
    auto evaluator = std::make_shared<WeightedSumEvaluator>();
    simulator.setEvaluator(evaluator);
    
    // Ejecutar
    simulator.run();
    
    // Resultados
    auto stats = simulator.getStatistics("option_a");
    std::cout << "Score medio: " << stats["mean"] << "\n";
    std::cout << "Tasa de éxito: " << stats["success_rate"] * 100 << "%\n";
    
    return 0;
}
```

---

## 📊 Caso de Estudio: Negocio Automatizado

### Problema Original

Elegir entre 4 negocios automatizados:
1. Bot de Arbitraje Cripto
2. Alertas de Trading (Suscripción)
3. Monitor Yield Farming DeFi
4. SaaS Análisis de Datos

### Simulación Básica (4 factores)

**Ganador:** Alertas Trading (score 0.787, éxito 78.6%)

### Simulación Mejorada (14 factores)

**Ganador:** Monitor DeFi (score 0.815, éxito 100%) 🔥

**Factores adicionales que cambiaron el resultado:**
- 🌐 Network Effects (audiencia DeFi existente)
- 💼 Prior Experience (newsletter DeFi ya funcionando)
- ⏱️ Market Timing (DeFi en crecimiento)
- 📊 Technical Scalability (escala muy bien)

**Lección:** Los factores contextuales (experiencia, red, timing) pueden cambiar radicalmente la decisión.

📖 [Ver análisis completo](ENHANCED_COMPARISON.md)

---

## 🎯 Extensibilidad

### Agregar Nuevo Factor (3 pasos)

```cpp
// 1. Heredar de DecisionFactor
class MyCustomFactor : public NumericFactor {
private:
    double my_parameter_;
    
public:
    MyCustomFactor(double param, double weight)
        : NumericFactor("My Factor", "MyCategory", 0.0, weight),
          my_parameter_(param)
    {
        // Tu lógica de evaluación (normalizar a 0-1)
        value_ = calculateScore(param);
    }
    
private:
    double calculateScore(double param) {
        // Implementa tu fórmula aquí
        return std::min(1.0, param / 100.0);
    }
};

// 2. Usar en configuración
option.factors["my_factor"] = std::make_shared<MyCustomFactor>(
    42.0,  // Tu parámetro
    1.0    // Peso
);

// 3. ¡Listo! La simulación lo usará automáticamente
```

📖 [Ver guía completa de extensión](EXTENSION_GUIDE.md)

---

## 🤝 Contribuciones

¡Las contribuciones son bienvenidas!

### Áreas de Mejora

- [ ] Paralelización (OpenMP/TBB)
- [ ] Exportar a JSON/CSV
- [ ] Visualizaciones (Python bindings)
- [ ] Tests unitarios (Google Test)
- [ ] Más ejemplos (inversiones, logística, etc.)
- [ ] Optimización (SIMD, cache-friendly)

### Cómo Contribuir

1. Fork el repositorio
2. Crea tu rama (`git checkout -b feature/amazing-feature`)
3. Commit tus cambios (`git commit -m 'feat: Add amazing feature'`)
4. Push a la rama (`git push origin feature/amazing-feature`)
5. Abre un Pull Request

---

## 📝 Licencia

Este proyecto está bajo la licencia MIT. Ver [LICENSE](LICENSE) para más detalles.

---

## 🙏 Agradecimientos

- Inspirado por [Multi-Criteria Decision Analysis](https://en.wikipedia.org/wiki/Multiple-criteria_decision_analysis)
- Patrones de diseño de [Design Patterns: Elements of Reusable Object-Oriented Software](https://en.wikipedia.org/wiki/Design_Patterns)
- Algoritmos Monte Carlo de [Numerical Recipes](http://numerical.recipes/)

---

## 📧 Contacto

¿Preguntas? ¿Sugerencias? ¡Abre un issue!

---

**🎉 ¡Feliz toma de decisiones basada en datos!** 🎲