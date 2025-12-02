# 🚀 Decision Maker - El Framework MÁS COMPLETO de Toma de Decisiones

[![C++17](https://img.shields.io/badge/C%2B%2B-17-blue.svg)](https://en.cppreference.com/w/cpp/17)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Status: Super Powered](https://img.shields.io/badge/Status-Super%20Powered-brightgreen.svg)]()

## 🎯 ¿Qué es esto?

El **sistema de toma de decisiones más poderoso y completo** jamás construido en C++. 

Combina **13 metodologías** diferentes para analizar decisiones desde TODAS las perspectivas posibles:
- ✅ Incertidumbre (Monte Carlo)
- ✅ Aprendizaje adaptativo (Bayesian, Bandit)
- ✅ Psicología (Regret Analysis)
- ✅ Flexibilidad (Real Options)
- ✅ Riesgo extremo (VaR, CVaR)
- ✅ Futuros alternativos (Scenarios)
- ✅ Dependencias (Correlation)
- ✅ ... y 6 metodologías más

---

## ⚡ Quick Start (5 minutos)

```bash
# Clonar
git clone https://github.com/usuario/decision-maker.git
cd decision-maker

# Compilar ejemplo simple
g++ -std=c++17 -O2 examples/unified_example.cpp -o bin/unified_example

# Ejecutar
./bin/unified_example
```

**Resultado:** Comparación de 3 laptops usando Monte Carlo + TOPSIS + Pareto

---

## 📊 Las 13 Metodologías

### 🎲 Básicas (Incertidumbre)
1. **Monte Carlo** - Simulación estocástica (10,000+ iteraciones)
2. **TOPSIS** - Ranking determinístico multi-criterio
3. **Pareto** - Trade-offs entre objetivos conflictivos
4. **Decision Trees** - Decisiones secuenciales multi-etapa
5. **Sensitivity** - ¿Qué factores importan MÁS?

### 🧠 Avanzadas (Aprendizaje & Adaptación)
6. **Bayesian Networks** - Actualiza con nueva información
7. **Multi-Armed Bandit** - Aprende de experiencia real (UCB1)

### 💎 Valoración (Flexibilidad)
8. **Real Options** - Valor de esperar/cambiar después

### 😰 Psicológicas (Comportamiento humano)
9. **Regret Analysis** - Minimiza arrepentimiento (minimax)

### ⚠️ Riesgo (Extremos & Colas)
10. **Risk Analysis** - VaR, CVaR, probabilidad de ruina

### 🌍 Estratégicas (Múltiples futuros)
11. **Scenario Planning** - Futuros alternativos coherentes

### 📈 Optimización (Combinación)
12. **Portfolio Optimization** - Diversificación (Markowitz)

### 🔗 Validación (Asunciones)
13. **Correlation Analysis** - Detecta dependencias (Pearson)

---

## 🎯 Ejemplo: ¿Qué Computadora Comprar?

### Opción 1: Análisis Simple (3 metodologías)
```cpp
#include "unified_decision_framework.h"

MonteCarloEngine mc;
mc.setNumSimulations(10000);
// ... configurar opciones ...
auto results = mc.run();  // Monte Carlo

TOPSISAnalyzer topsis;
// ... configurar ...
auto scores = topsis.analyze();  // TOPSIS

ParetoAnalyzer pareto;
// ... configurar ...
auto front = pareto.findParetoFront(points);  // Pareto
```

**Output:**
```
Monte Carlo: MacBook 2019 (mejor score: -539)
TOPSIS: MacBook Air M2 (más cercano al ideal: 0.555)
Pareto: 2 opciones óptimas (trade-offs)
```

### Opción 2: Análisis SUPER PODEROSO (13 metodologías)
```cpp
#include "unified_decision_framework.h"
#include "advanced_decision_tools.h"

// 1. Monte Carlo (baseline)
MonteCarloEngine mc;
auto mc_results = mc.run();

// 2. Bayesian (nueva info: "encontré barato")
BayesianUpdater bn;
bn.updateBelief("laptop_falla", "precio_bajo", true);
// Riesgo: 15% → 48.8% ⚠️

// 3. Regret (minimizar arrepentimiento)
RegretAnalyzer regret;
auto minimax = regret.minimaxRegret(outcomes, scenarios);

// 4. Real Options (valor de flexibilidad)
RealOptionsAnalyzer ro;
double value_wait = ro.valueOfWaiting(2500, 0.30, 0.25);
// Esperar vale $150

// 5. Risk (riesgo extremo)
RiskAnalyzer risk;
double var = risk.calculateVaR(outcomes, 0.95);
double cvar = risk.calculateCVaR(outcomes, 0.95);
// MacBook 2019: 71% probabilidad de ruina ⚠️

// 6. Scenarios (futuros alternativos)
ScenarioPlanner sp;
auto robust = sp.findRobustOption(options, scenarios);
// MacBook 2019 funciona en boom, status quo, Y recesión

// 7. Correlation (dependencias)
CorrelationAnalyzer ca;
auto corr = ca.correlationMatrix(factors, sims);
// Costo ↔ Calidad: +0.85 (alta correlación)

// 8. Bandit (aprender en el tiempo)
MultiArmedBandit mab;
for (int week = 0; week < 10; ++week) {
    std::string choice = mab.selectArmUCB();
    double satisfaction = usar_laptop(choice);
    mab.updateReward(choice, satisfaction);
}
// Converge a MacBook Air M2 (mejor PARA TI)
```

**Output Completo:**
```
🚀 DECISIÓN SUPER INFORMADA:

✅ Monte Carlo: MacBook 2019 (score -400)
✅ Bayesian: Riesgo aumenta 15% → 48% con nueva info
✅ Regret: Laptop económico (minimax)
✅ Real Options: Esperar = $150, Upgrade = $240
✅ Risk: MacBook 2019 = 71% prob. ruina
✅ Scenarios: MacBook 2019 robusto en todos
✅ Correlation: Costo ↔ Calidad (+0.85)
✅ Bandit: Converge a MacBook Air M2

📊 Esta es la decisión MÁS COMPLETA posible.
```

---

## 📁 Estructura del Proyecto

```
desicion-maker/
├── src/
│   ├── unified_decision_framework.h    # 5 metodologías básicas (620 líneas)
│   └── advanced_decision_tools.h       # 8 metodologías avanzadas (800+ líneas)
│
├── examples/
│   ├── unified_example.cpp             # Demo 3 metodologías
│   ├── power_decision_example.cpp      # Demo 8 metodologías avanzadas
│   └── decision_computadora_arturo.cpp # Caso real con 10 opciones
│
├── docs/
│   ├── METODOLOGIAS_ALTERNATIVAS.md    # Cuándo usar cada método
│   ├── SUPER_POWERED_GUIDE.md          # Guía completa con ejemplos
│   └── ROADMAP.md
│
└── README_UNIFIED_FRAMEWORK.md         # API completa
```

---

## 🎓 Cuándo Usar Cada Metodología

| Situación | Metodología | Ventaja Clave |
|-----------|-------------|---------------|
| Hay incertidumbre | **Monte Carlo** | Distribuciones completas |
| Valores conocidos | **TOPSIS** | Rápido (ms vs min) |
| Objetivos conflictivos | **Pareto** | No necesita pesos |
| Decisiones secuenciales | **Decision Trees** | Visualizable |
| ¿Qué importa más? | **Sensitivity** | Identifica factores críticos |
| Nueva información | **Bayesian** | Actualiza probabilidades |
| Temes arrepentirte | **Regret** | Minimiza lamento |
| Puedes cambiar después | **Real Options** | Valor de flexibilidad |
| Aprendes con el tiempo | **Bandit** | Adaptativo |
| Riesgo catastrófico | **Risk VaR/CVaR** | Pérdida máxima |
| Futuros muy diferentes | **Scenarios** | Opción robusta |
| ¿Son independientes? | **Correlation** | Detecta dependencias |
| Combinar opciones | **Portfolio** | Diversificación |

---

## 🔥 Características Destacadas

### ✅ Header-Only
```cpp
#include "unified_decision_framework.h"
#include "advanced_decision_tools.h"
// ¡Ya está! No necesitas compilar bibliotecas
```

### ✅ Simuladores Custom
```cpp
option.setSimulator([](const auto& values, std::mt19937& gen) {
    SimulationResult result;
    // TU lógica personalizada aquí
    std::bernoulli_distribution downtime(0.95);
    result.events["Downtime"] = downtime(gen);
    return result;
});
```

### ✅ 6 Tipos de Distribuciones
```cpp
DistributionType::NORMAL       // Gaussiana (μ, σ)
DistributionType::UNIFORM      // Uniforme [min, max]
DistributionType::TRIANGULAR   // (min, mode, max) - más realista
DistributionType::BERNOULLI    // Éxito/fracaso (p)
DistributionType::EXPONENTIAL  // Tiempos de espera
DistributionType::BETA         // Valores 0-1 con forma
```

### ✅ Estadísticas Completas
```cpp
Statistics stats = results["MacBook Air M2"];
std::cout << "Mean: " << stats.mean_score << "\n";
std::cout << "StdDev: " << stats.score_stddev << "\n";
std::cout << "5th-95th: [" << stats.percentile_5["Costo"] 
          << ", " << stats.percentile_95["Costo"] << "]\n";
std::cout << "Success rate: " << stats.success_rate << "\n";
```

---

## 📊 Resultados Reales

### Decisión de Computadora (10 opciones, 19 factores)

| Opción | Costo Total | Score | Riesgo |
|--------|-------------|-------|--------|
| **Computador trabajo** | **$841** | Mejor valor | 84% estrés (dependencia) |
| Mini PC AMD | $858 | Segundo | Desktop (no portátil) |
| MacBook Pro 2020 | $1,131 | Balance | 60% estrés |
| **MacBook 2019** | **$2,594** | Actual | 95% downtime ⚠️ |
| MacBook Air M2 | $2,551 | Mejor satisfacción | $2,080 café (2 años) |

**Insights:**
- Laptops agregan **$1,200-2,300** en café/comida (2 años de trabajo remoto)
- Desktops = $0 café (trabajas en casa)
- MacBook 2019: 95% probabilidad de downtime crítico
- Trabajo gratis: Mejor valor pero 84% estrés (dependencia empresa)

---

## 🚀 Casos de Uso

### 💻 Tecnología
- ✅ ¿Qué computadora comprar?
- ✅ ¿Stack tecnológico para proyecto?
- ✅ ¿Cloud provider óptimo?

### 💰 Finanzas
- ✅ ¿Dónde invertir?
- ✅ Portfolio optimization
- ✅ Risk management (VaR/CVaR)

### 👔 Carrera
- ✅ ¿Qué trabajo aceptar?
- ✅ ¿Estudiar más o trabajar?
- ✅ ¿Cambiar de industria?

### 🏢 Negocios
- ✅ ¿Qué producto lanzar?
- ✅ ¿Expandir o consolidar?
- ✅ ¿Precio óptimo?

### 🏠 Vida Personal
- ✅ ¿Comprar vs rentar?
- ✅ ¿Qué auto comprar?
- ✅ ¿Dónde vivir?

---

## 📚 Documentación Completa

| Documento | Descripción |
|-----------|-------------|
| [README_UNIFIED_FRAMEWORK.md](README_UNIFIED_FRAMEWORK.md) | API completa + Quick start |
| [METODOLOGIAS_ALTERNATIVAS.md](docs/METODOLOGIAS_ALTERNATIVAS.md) | Cuándo usar cada método |
| [SUPER_POWERED_GUIDE.md](docs/SUPER_POWERED_GUIDE.md) | Guía de 13 metodologías |
| [examples/](examples/) | Ejemplos ejecutables |

---

## 🎯 Roadmap Futuro

### Ya Implementado ✅
- [x] Monte Carlo (10,000+ sim)
- [x] TOPSIS (determinístico)
- [x] Pareto (multi-objetivo)
- [x] Decision Trees
- [x] Sensitivity Analysis
- [x] Bayesian Networks
- [x] Regret Analysis
- [x] Real Options
- [x] Multi-Armed Bandit
- [x] Risk VaR/CVaR
- [x] Scenario Planning
- [x] Correlation Analysis
- [x] Portfolio Optimization

### Futuro 🔮
- [ ] Visualización gráfica (exportar a Python/matplotlib)
- [ ] Interfaz web (WASM)
- [ ] Machine Learning integration
- [ ] API REST (servidor C++)
- [ ] Soporte GPU (CUDA para Monte Carlo)

---

## 🤝 Contribuir

```bash
# Fork del proyecto
git clone https://github.com/tu-usuario/decision-maker.git

# Crear rama
git checkout -b feature/nueva-metodologia

# Commit
git commit -am "feat: Agrega teoría de juegos"

# Push
git push origin feature/nueva-metodologia

# Pull Request
```

---

## 📝 Licencia

MIT License - ve [LICENSE](LICENSE)

---

## 🙏 Referencias & Créditos

### Papers & Libros
- **Monte Carlo**: Metropolis & Ulam (1949)
- **TOPSIS**: Hwang & Yoon (1981)
- **Pareto**: Vilfredo Pareto (1896)
- **Bayesian**: Pearl (1988) - "Probabilistic Reasoning"
- **Regret**: Savage (1951) - "The Theory of Statistical Decision"
- **Real Options**: Black-Scholes (1973), Dixit & Pindyck (1994)
- **Bandit**: Auer et al. (2002) - UCB1 algorithm
- **Risk VaR**: Artzner et al. (1999)
- **Scenarios**: Shell Oil (1970s), Schwartz (1991)

### Inspiración
- `business_decision_v2_enhanced.cpp` (OOP)
- `decision_jeep_logistica.cpp` (Procedural)
- `decision_computadora_arturo.cpp` (Flat)

---

## 📧 Contacto

**Autor:** Arturo  
**Email:** [tu-email]  
**GitHub:** [tu-usuario]  

---

## ⭐ Si te gusta, dale una estrella!

```
git clone https://github.com/usuario/decision-maker.git
cd decision-maker
g++ -std=c++17 -O2 examples/power_decision_example.cpp -o bin/power_decision
./bin/power_decision

🚀 Disfruta del framework de decisiones MÁS COMPLETO del mundo
```

---

**Made with 💙 and 13 methodologies**
