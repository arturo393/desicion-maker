# 🏗️ Guía de Extensión: Arquitectura Genérica para Decisiones

## 📖 Introducción

Este documento explica cómo **extender** y **reutilizar** el framework de decisiones Monte Carlo para cualquier tipo de decisión (no solo negocios).

---

## 🎯 Casos de Uso

### ✅ Este framework es útil para:

1. **Decisiones de negocio**
   - Qué producto lanzar
   - En qué mercado entrar
   - Qué tecnología adoptar

2. **Decisiones personales**
   - Dónde vivir
   - Qué carrera estudiar
   - Qué casa comprar

3. **Decisiones de inversión**
   - Qué acciones comprar
   - Diversificación de portafolio
   - Timing de entrada/salida

4. **Decisiones estratégicas**
   - Contratar o no contratar
   - Asociarse o ir solo
   - Pivotar o perseverar

---

## 🧩 Componentes del Framework

### 1️⃣ `DecisionFactor` (Factores de Decisión)

**¿Qué es?** Una característica que influencia tu decisión.

**Tipos disponibles:**

#### A) `NumericFactor` - Valor fijo
```cpp
class NumericFactor : public DecisionFactor {
protected:
    double value_;  // Valor constante (0-1)
    double weight_; // Importancia del factor
    
public:
    NumericFactor(std::string name, std::string category, 
                  double value, double weight);
};
```

**Ejemplo:** Costo de vida de una ciudad (no cambia en la simulación)
```cpp
auto cost_of_living = std::make_shared<NumericFactor>(
    "Cost of Living",  // Nombre
    "Financial",       // Categoría
    0.7,               // Score normalizado (0-1)
    1.5                // Peso (importancia alta)
);
```

---

#### B) `StochasticFactor` - Valor variable
```cpp
class StochasticFactor : public DecisionFactor {
protected:
    double mean_;      // Promedio
    double std_dev_;   // Desviación estándar
    std::mt19937* rng_; // Generador aleatorio
};
```

**Ejemplo:** Ingreso mensual con variabilidad
```cpp
auto monthly_income = std::make_shared<StochasticFactor>(
    "Monthly Income",  // Nombre
    "Financial",       // Categoría
    0.65,              // Media normalizada (0-1)
    0.20,              // Desv. estándar (volatilidad)
    1.5,               // Peso
    &rng               // RNG para Monte Carlo
);
```

**Comportamiento:** Cada simulación genera un valor diferente usando distribución normal.

---

#### C) `CompositeFactor` - Combina múltiples factores
```cpp
class CompositeFactor : public DecisionFactor {
private:
    std::vector<std::shared_ptr<DecisionFactor>> sub_factors_;
    
public:
    void addSubFactor(std::shared_ptr<DecisionFactor> factor);
    double evaluate() const override; // Promedio ponderado
};
```

**Ejemplo:** Factor "Calidad de Vida" compuesto por clima, seguridad, cultura
```cpp
auto quality_of_life = std::make_shared<CompositeFactor>(
    "Quality of Life", "Lifestyle", 1.0
);

quality_of_life->addSubFactor(
    std::make_shared<NumericFactor>("Climate", "Lifestyle", 0.8, 1.0)
);
quality_of_life->addSubFactor(
    std::make_shared<NumericFactor>("Safety", "Lifestyle", 0.9, 1.2)
);
quality_of_life->addSubFactor(
    std::make_shared<NumericFactor>("Culture", "Lifestyle", 0.7, 0.8)
);

// evaluate() retorna promedio ponderado de subfactores
```

---

### 2️⃣ `DecisionOption` (Opciones a Comparar)

**¿Qué es?** Una alternativa en tu decisión.

```cpp
struct DecisionOption {
    std::string id;                                           // Identificador único
    std::string name;                                         // Nombre legible
    std::string description;                                  // Descripción
    std::map<std::string, std::shared_ptr<DecisionFactor>> factors;  // Factores
    std::map<std::string, double> metadata;                   // Datos extra
};
```

**Ejemplo:** Opción "Vivir en Barcelona"
```cpp
DecisionOption barcelona;
barcelona.id = "barcelona";
barcelona.name = "Barcelona, España";
barcelona.description = "Ciudad mediterránea con playa y cultura";

barcelona.factors["climate"] = std::make_shared<NumericFactor>(...);
barcelona.factors["cost_of_living"] = std::make_shared<NumericFactor>(...);
barcelona.factors["job_market"] = std::make_shared<StochasticFactor>(...);

barcelona.metadata["rent_monthly_eur"] = 1200.0;
barcelona.metadata["population"] = 1600000;
```

---

### 3️⃣ `DecisionOptionBuilder` (Constructor Fluido)

**¿Qué es?** API fluida para construir opciones fácilmente.

```cpp
DecisionOptionBuilder builder("barcelona", "Barcelona, España");
builder.setRNG(&rng)
    .setDescription("Ciudad mediterránea")
    .addNumericFactor("Climate", "Lifestyle", 0.9, 1.2)
    .addNumericFactor("Cost", "Financial", 0.6, 1.5)
    .addStochasticFactor("Salary", "Financial", 0.7, 0.15, 1.3)
    .addMetadata("rent_eur", 1200.0);

DecisionOption option = builder.build();
```

---

### 4️⃣ `DecisionEvaluator` (Estrategia de Evaluación)

**¿Qué es?** Cómo calcular el score total de una opción.

#### A) `WeightedSumEvaluator` - Suma ponderada simple
```cpp
class WeightedSumEvaluator : public DecisionEvaluator {
public:
    double evaluate(const DecisionOption& option) const override {
        double total_score = 0.0;
        double total_weight = 0.0;
        
        for (const auto& [name, factor] : option.factors) {
            total_score += factor->evaluate() * factor->getWeight();
            total_weight += factor->getWeight();
        }
        
        return total_score / total_weight;
    }
};
```

**Uso:**
```cpp
auto evaluator = std::make_shared<WeightedSumEvaluator>();
simulator.setEvaluator(evaluator);
```

---

#### B) `MultiCriteriaEvaluator` - Evaluación por categorías
```cpp
class MultiCriteriaEvaluator : public DecisionEvaluator {
private:
    std::map<std::string, double> category_weights_;
    
public:
    MultiCriteriaEvaluator(std::map<std::string, double> weights)
        : category_weights_(weights) {}
};
```

**Uso:** Dar pesos diferentes a categorías (Financial 30%, Lifestyle 20%, etc.)
```cpp
std::map<std::string, double> category_weights = {
    {"Financial", 0.30},
    {"Lifestyle", 0.20},
    {"Career", 0.25},
    {"Family", 0.15},
    {"Health", 0.10}
};

auto evaluator = std::make_shared<MultiCriteriaEvaluator>(category_weights);
simulator.setEvaluator(evaluator);
```

---

### 5️⃣ `MonteCarloSimulator` (Motor de Simulación)

**¿Qué es?** Ejecuta N simulaciones y recolecta estadísticas.

```cpp
class MonteCarloSimulator {
public:
    MonteCarloSimulator(size_t num_simulations);
    
    void addOption(const DecisionOption& option);
    void setEvaluator(std::shared_ptr<DecisionEvaluator> evaluator);
    void setSuccessThreshold(double threshold);
    
    void run();  // Ejecuta simulación
    
    // Resultados
    std::map<std::string, double> getStatistics(const std::string& option_id) const;
    const std::vector<SimulationResult>& getResults(const std::string& option_id) const;
};
```

**Uso:**
```cpp
std::mt19937 rng(std::random_device{}());
MonteCarloSimulator simulator(10000);  // 10,000 iteraciones

// Agregar opciones
simulator.addOption(barcelona_option);
simulator.addOption(berlin_option);
simulator.addOption(lisbon_option);

// Configurar evaluador
auto evaluator = std::make_shared<WeightedSumEvaluator>();
simulator.setEvaluator(evaluator);

// Ejecutar
simulator.run();

// Obtener resultados
auto stats = simulator.getStatistics("barcelona");
std::cout << "Barcelona score: " << stats["mean"] << "\n";
std::cout << "Success rate: " << stats["success_rate"] * 100 << "%\n";
```

---

## 🚀 Ejemplo Completo: Decisión "Dónde Vivir"

### Paso 1: Definir factores personalizados

```cpp
// Factor: Clima (temperatura, sol, lluvia)
class ClimateFactor : public NumericFactor {
private:
    double avg_temp_c_;
    int sunny_days_per_year_;
    int rainy_days_per_year_;
    
public:
    ClimateFactor(double temp, int sunny, int rainy, double weight)
        : NumericFactor("Climate", "Lifestyle", 0.0, weight),
          avg_temp_c_(temp),
          sunny_days_per_year_(sunny),
          rainy_days_per_year_(rainy)
    {
        // Preferencia: 20-25°C óptimo, >250 días sol
        double temp_score = 1.0 - std::abs(temp - 22.5) / 10.0;
        double sunny_score = std::min(1.0, sunny / 250.0);
        
        value_ = temp_score * 0.6 + sunny_score * 0.4;
    }
};

// Factor: Costo de vida
class CostOfLivingFactor : public NumericFactor {
private:
    double rent_monthly_;
    double groceries_monthly_;
    double utilities_monthly_;
    
public:
    CostOfLivingFactor(double rent, double groceries, double utilities, double weight)
        : NumericFactor("Cost of Living", "Financial", 0.0, weight),
          rent_monthly_(rent),
          groceries_monthly_(groceries),
          utilities_monthly_(utilities)
    {
        double total_cost = rent + groceries + utilities;
        // Score inverso: menos costo = mejor
        // Normalizado a 2000 EUR/mes como "caro"
        value_ = 1.0 - std::min(1.0, total_cost / 2000.0);
    }
};

// Factor: Mercado laboral
class JobMarketFactor : public StochasticFactor {
private:
    int job_openings_;
    double avg_salary_;
    
public:
    JobMarketFactor(int openings, double salary, double weight, std::mt19937* rng)
        : StochasticFactor("Job Market", "Career", 0.0, 0.12, weight, rng),
          job_openings_(openings),
          avg_salary_(salary)
    {
        // Normalizar: 100 jobs = 0.5, 500 jobs = 1.0
        double openings_norm = std::min(1.0, openings / 500.0);
        // Normalizar: 50k EUR = 0.5, 100k EUR = 1.0
        double salary_norm = std::min(1.0, (avg_salary - 30000) / 70000.0);
        
        mean_ = openings_norm * 0.6 + salary_norm * 0.4;
    }
};
```

---

### Paso 2: Configurar opciones

```cpp
void setupCityOptions(MonteCarloSimulator& simulator, std::mt19937& rng) {
    // ======== BARCELONA ========
    {
        DecisionOptionBuilder builder("barcelona", "Barcelona, España");
        builder.setRNG(&rng)
            .setDescription("Ciudad mediterránea con playa")
            .addMetadata("rent_eur", 1200.0)
            .addMetadata("population", 1600000);
        
        auto option = builder.build();
        
        option.factors["climate"] = std::make_shared<ClimateFactor>(
            18.5,  // Temperatura media
            300,   // 300 días soleados
            50,    // 50 días lluvia
            1.2    // Peso alto (importante)
        );
        
        option.factors["cost_of_living"] = std::make_shared<CostOfLivingFactor>(
            1200.0,  // Renta
            400.0,   // Comida
            150.0,   // Utilidades
            1.5      // Peso muy alto
        );
        
        option.factors["job_market"] = std::make_shared<JobMarketFactor>(
            200,     // 200 ofertas tech
            55000.0, // Salario promedio
            1.3,     // Peso alto
            &rng
        );
        
        simulator.addOption(option);
    }
    
    // ======== BERLÍN ========
    {
        DecisionOptionBuilder builder("berlin", "Berlín, Alemania");
        builder.setRNG(&rng)
            .setDescription("Hub tecnológico europeo")
            .addMetadata("rent_eur", 1000.0)
            .addMetadata("population", 3600000);
        
        auto option = builder.build();
        
        option.factors["climate"] = std::make_shared<ClimateFactor>(
            10.0,  // Frío
            150,   // Poco sol
            120,   // Mucha lluvia
            1.2
        );
        
        option.factors["cost_of_living"] = std::make_shared<CostOfLivingFactor>(
            1000.0,  // Renta más barata que Barcelona
            350.0,
            120.0,
            1.5
        );
        
        option.factors["job_market"] = std::make_shared<JobMarketFactor>(
            500,     // Muchas ofertas (hub tech)
            70000.0, // Salarios más altos
            1.3,
            &rng
        );
        
        simulator.addOption(option);
    }
    
    // ======== LISBOA ========
    {
        DecisionOptionBuilder builder("lisbon", "Lisboa, Portugal");
        builder.setRNG(&rng)
            .setDescription("Ciudad costera con buen clima")
            .addMetadata("rent_eur", 900.0)
            .addMetadata("population", 500000);
        
        auto option = builder.build();
        
        option.factors["climate"] = std::make_shared<ClimateFactor>(
            19.0,  // Clima similar a Barcelona
            290,
            80,
            1.2
        );
        
        option.factors["cost_of_living"] = std::make_shared<CostOfLivingFactor>(
            900.0,   // Más barato
            300.0,
            100.0,
            1.5
        );
        
        option.factors["job_market"] = std::make_shared<JobMarketFactor>(
            80,      // Menos ofertas (mercado pequeño)
            45000.0, // Salarios más bajos
            1.3,
            &rng
        );
        
        simulator.addOption(option);
    }
}
```

---

### Paso 3: Ejecutar simulación

```cpp
int main() {
    std::mt19937 rng(std::random_device{}());
    MonteCarloSimulator simulator(10000);  // 10k simulaciones
    
    // Configurar opciones
    setupCityOptions(simulator, rng);
    
    // Configurar evaluador
    std::map<std::string, double> category_weights = {
        {"Financial", 0.35},   // 35% peso en finanzas
        {"Lifestyle", 0.30},   // 30% en estilo de vida
        {"Career", 0.25},      // 25% en carrera
        {"Family", 0.10}       // 10% en familia
    };
    auto evaluator = std::make_shared<MultiCriteriaEvaluator>(category_weights);
    simulator.setEvaluator(evaluator);
    
    // Ejecutar
    simulator.run();
    
    // Imprimir resultados
    for (const auto& city : {"barcelona", "berlin", "lisbon"}) {
        auto stats = simulator.getStatistics(city);
        std::cout << "\n=== " << city << " ===\n";
        std::cout << "Score: " << stats["mean"] << "\n";
        std::cout << "Success rate: " << stats["success_rate"] * 100 << "%\n";
        std::cout << "P25-P75: " << stats["p25"] << " - " << stats["p75"] << "\n";
    }
    
    return 0;
}
```

---

## 🎨 Personalizando el Evaluador

### Ejemplo: Evaluador con penalizaciones

```cpp
class PenaltyEvaluator : public DecisionEvaluator {
private:
    double penalty_threshold_;
    std::string penalty_factor_;
    
public:
    PenaltyEvaluator(double threshold, std::string factor)
        : penalty_threshold_(threshold),
          penalty_factor_(factor) {}
    
    double evaluate(const DecisionOption& option) const override {
        // Calcular score base
        double base_score = 0.0;
        double total_weight = 0.0;
        
        for (const auto& [name, factor] : option.factors) {
            double score = factor->evaluate();
            double weight = factor->getWeight();
            
            // Aplicar penalización si factor cae bajo threshold
            if (name == penalty_factor_ && score < penalty_threshold_) {
                double penalty = (penalty_threshold_ - score) * 2.0;
                score = std::max(0.0, score - penalty);
            }
            
            base_score += score * weight;
            total_weight += weight;
        }
        
        return base_score / total_weight;
    }
};

// Uso: Penalizar ciudades con job_market < 0.5
auto evaluator = std::make_shared<PenaltyEvaluator>(0.5, "Job Market");
simulator.setEvaluator(evaluator);
```

---

## 🧪 Testing y Validación

### Unit test para factor personalizado

```cpp
#include <cassert>

void testClimateFactor() {
    // Test: Clima perfecto
    ClimateFactor perfect(22.5, 300, 50, 1.0);
    assert(perfect.evaluate() > 0.9);
    
    // Test: Clima frío
    ClimateFactor cold(5.0, 150, 150, 1.0);
    assert(cold.evaluate() < 0.5);
    
    // Test: Clima tropical
    ClimateFactor tropical(35.0, 350, 10, 1.0);
    assert(tropical.evaluate() < 0.6);
    
    std::cout << "✅ ClimateFactor tests passed\n";
}

int main() {
    testClimateFactor();
    return 0;
}
```

---

## 📊 Exportar Resultados a JSON

```cpp
#include <fstream>
#include <nlohmann/json.hpp>  // Requiere JSON library

void exportToJSON(const MonteCarloSimulator& simulator, 
                  const std::vector<std::string>& option_ids) {
    nlohmann::json output;
    
    for (const auto& id : option_ids) {
        auto stats = simulator.getStatistics(id);
        
        output[id] = {
            {"mean_score", stats["mean"]},
            {"success_rate", stats["success_rate"]},
            {"std_dev", stats["std_dev"]},
            {"min", stats["min"]},
            {"max", stats["max"]},
            {"p25", stats["p25"]},
            {"p50", stats["p50"]},
            {"p75", stats["p75"]}
        };
    }
    
    std::ofstream file("simulation_results.json");
    file << output.dump(2);  // Pretty print con 2 espacios
}
```

---

## 🎯 Mejores Prácticas

### ✅ DO's

1. **Normalizar factores a 0-1**
   - Facilita comparación y ponderación
   - Evita problemas de escala

2. **Usar categorías consistentes**
   - Financial, Lifestyle, Career, Risk, etc.
   - Permite evaluador multi-criterio

3. **Documentar asunciones**
   - Comentarios en código explicando scores
   - Ejemplo: `// 100 jobs = 0.5, 500 jobs = 1.0`

4. **Inyectar RNG**
   - Facilita reproducibilidad
   - Permite testing determinístico

5. **Validar con simulaciones pequeñas primero**
   - 100 iteraciones para debug
   - 10,000+ para producción

---

### ❌ DON'Ts

1. **No hardcodear pesos**
   - Usa parámetros o config files
   - Permite sensibilidad de análisis

2. **No mezclar escalas**
   - Factor A: 0-100, Factor B: 0-1 ❌
   - Normaliza todo a 0-1 ✅

3. **No ignorar outliers**
   - Revisa P25, P50, P75 (no solo mean)
   - Outliers pueden indicar problemas

4. **No sobreoptimizar**
   - 10k iteraciones suele ser suficiente
   - 100k+ solo si necesitas alta precisión

---

## 🚀 Recursos Adicionales

### Archivos de referencia

- **Framework:** `src/scenarios/BusinessDecision.h`
- **Ejemplo negocios:** `examples/business_decision_v2_enhanced.cpp`
- **Comparación:** `ENHANCED_COMPARISON.md`
- **Esta guía:** `EXTENSION_GUIDE.md`

### Lecturas recomendadas

- [Monte Carlo Simulation](https://en.wikipedia.org/wiki/Monte_Carlo_method)
- [Strategy Pattern](https://refactoring.guru/design-patterns/strategy)
- [Builder Pattern](https://refactoring.guru/design-patterns/builder)
- [Multi-Criteria Decision Analysis](https://en.wikipedia.org/wiki/Multiple-criteria_decision_analysis)

---

## 🤝 Contribuyendo

### Cómo agregar tu propio factor al framework

1. Fork el repositorio
2. Crea clase heredando de `DecisionFactor`
3. Implementa `evaluate()`, `getName()`, `getCategory()`
4. Documenta asunciones y normalización
5. Agrega tests unitarios
6. Submit pull request

---

## 📝 Changelog

- **v2.0** (Enero 2025): Arquitectura genérica con 10+ factores
- **v1.0** (Diciembre 2024): Versión inicial con 4 factores básicos

---

**🎉 ¡Feliz toma de decisiones basada en datos!** 🎲
