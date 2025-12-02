# 🎯 Guía de Metodologías para Toma de Decisiones

## Resumen Ejecutivo

Este framework unificado soporta **múltiples metodologías** para toma de decisiones, cada una óptima para diferentes escenarios:

1. **Monte Carlo** (estocástico) - incertidumbre y riesgo
2. **TOPSIS** (determinístico) - comparación rápida con valores conocidos
3. **Pareto** (multi-objetivo) - trade-offs sin asignar pesos
4. **Árboles de Decisión** (secuencial) - decisiones en etapas
5. **Análisis de Sensibilidad** (robustez) - identificar factores críticos

---

## 📊 Método 1: Monte Carlo

### ¿Cuándo usar?
✅ Hay **incertidumbre** significativa (precios variables, probabilidades)  
✅ Existen **eventos probabilísticos** (fallos, downtime, crisis)  
✅ Necesitas ver **distribuciones completas** (mejor/peor caso)  
✅ Quieres **intervalos de confianza** (5th-95th percentil)  

### ¿Cuándo NO usar?
❌ Valores son **determinísticos** (todo conocido)  
❌ Decisión es **trivial** (solo 2 opciones claras)  
❌ No hay tiempo para ejecutar simulaciones (necesitas respuesta inmediata)  

### Ejemplo de uso:
```cpp
MonteCarloEngine mc;
mc.setNumSimulations(10000);

DecisionOption option("MacBook 2019", "Laptop actual");
option.addVariable("costo", UncertainVariable("costo", 
                   DistributionType::TRIANGULAR, 800, 1200, 2000));

option.setSimulator([](const auto& values, std::mt19937& gen) {
    SimulationResult result;
    // Simular downtime crítico
    std::bernoulli_distribution downtime_dist(0.95);
    result.events["Downtime"] = downtime_dist(gen);
    return result;
});

mc.addOption(option);
auto results = mc.run();
```

### Ventajas:
✅ Maneja incertidumbre de forma realista  
✅ Muestra rangos completos (min, max, p5, p95)  
✅ Permite modelar eventos complejos  
✅ Resultados robustos con muchas iteraciones  

### Desventajas:
❌ Lento (10,000+ simulaciones)  
❌ Requiere definir distribuciones  
❌ No siempre converge rápido  

---

## 📐 Método 2: TOPSIS (Determinístico)

### ¿Cuándo usar?
✅ Valores son **conocidos** (sin probabilidades)  
✅ Necesitas **ranking rápido** de opciones  
✅ Ya conoces **pesos** de cada factor  
✅ No hay eventos probabilísticos importantes  

### ¿Cuándo NO usar?
❌ Hay mucha **incertidumbre**  
❌ No conoces los **pesos** (prueba Pareto)  
❌ Hay **eventos complejos** a modelar  

### Ejemplo de uso:
```cpp
TOPSISAnalyzer topsis;

topsis.setOptions({"MacBook Air M2", "Laptop Económico", "Mini PC"});
topsis.setFactors(
    {"Costo", "Productividad", "Satisfacción"},
    {0.3, 0.35, 0.35},         // Pesos
    {false, true, true}        // Minimizar costo, maximizar otros
);

// Matriz [opciones][factores]
std::vector<std::vector<double>> matrix = {
    {2551, 1.0, 9.3},   // MacBook Air M2
    {2403, 0.996, 6.8}, // Laptop Económico
    {858, 1.0, 5.5}     // Mini PC
};

topsis.setDecisionMatrix(matrix);
auto scores = topsis.analyze();  // Instantáneo
```

### Ventajas:
✅ **Rápido** (milisegundos vs minutos de Monte Carlo)  
✅ Fácil de entender (proximidad al ideal)  
✅ No necesita distribuciones  
✅ Resultados determinísticos (reproducibles)  

### Desventajas:
❌ No captura incertidumbre  
❌ Necesitas conocer pesos a priori  
❌ No muestra rangos (solo puntaje único)  

---

## 🎯 Método 3: Análisis de Pareto (Multi-Objetivo)

### ¿Cuándo usar?
✅ Hay **conflicto** entre objetivos (costo vs calidad)  
✅ **NO sabes** qué pesos asignar  
✅ Quieres explorar **trade-offs** visualmente  
✅ Necesitas **justificar** por qué descartar opciones  

### ¿Cuándo NO usar?
❌ Solo hay un objetivo principal  
❌ Ya conoces pesos exactos (usa TOPSIS)  
❌ Necesitas un ganador único (Pareto da conjunto de opciones)  

### Ejemplo de uso:
```cpp
ParetoAnalyzer pareto;

std::vector<ParetoAnalyzer::Point> points = {
    {"MacBook Air M2", {2551, 9.3, 1.0}, false},
    {"Laptop Económico", {2403, 6.8, 0.996}, false},
    {"Mini PC AMD", {858, 5.5, 1.0}, false}
};

// Objetivos: [min costo, max satisfacción, max productividad]
auto pareto_front = pareto.findParetoFront(points, {false, true, true});

// pareto_front contiene solo opciones NO dominadas
```

### Ventajas:
✅ No necesitas asignar pesos  
✅ Muestra **todas** las opciones óptimas  
✅ Identifica opciones **dominadas** (descartables)  
✅ Visual (gráficos de frontera)  

### Desventajas:
❌ No da un "ganador" único  
❌ Requiere que elijas dentro de la frontera  
❌ Difícil con >3 objetivos (visualización)  

---

## 🌳 Método 4: Árboles de Decisión (Secuencial)

### ¿Cuándo usar?
✅ Decisiones ocurren en **etapas** (multi-step)  
✅ Elecciones futuras dependen de **resultados previos**  
✅ Necesitas visualizar **caminos alternativos**  
✅ Hay puntos de decisión con opciones claras  

### ¿Cuándo NO usar?
❌ Decisión es de un solo paso  
❌ No hay secuencialidad clara  
❌ Demasiadas ramas (explosión combinatoria)  

### Ejemplo de uso:
```cpp
DecisionNode root("Comprar ahora", DecisionNode::Type::DECISION, 0);

// Rama 1: Comprar ahora
auto buy_now = std::make_shared<DecisionNode>("Falla en 6 meses", 
                DecisionNode::Type::CHANCE, 0.15);
buy_now->addChild({"Reparar", DecisionNode::Type::DECISION, -200});
buy_now->addChild({"Reemplazar", DecisionNode::Type::DECISION, -1500});

// Rama 2: Esperar
auto wait = std::make_shared<DecisionNode>("Precio baja", 
            DecisionNode::Type::CHANCE, 0.30);

root.addChild(buy_now);
root.addChild(wait);
```

### Ventajas:
✅ **Visual** (fácil de explicar)  
✅ Captura secuencialidad  
✅ Muestra valor de información futura  
✅ Soporta **rollback** (backward induction)  

### Desventajas:
❌ Explosión combinatoria con muchas ramas  
❌ Difícil modelar incertidumbre continua  
❌ No captura interdependencias complejas  

---

## 🔬 Método 5: Análisis de Sensibilidad

### ¿Cuándo usar?
✅ **SIEMPRE** - como validación  
✅ Quieres saber **qué factor importa MÁS**  
✅ Necesitas validar **robustez** de decisión  
✅ Pesos son inciertos (¿qué pasa si cambio peso?)  

### ¿Cuándo NO usar?
❌ Ya sabes que la decisión es clara (todos los factores apuntan igual)  

### Ejemplo de uso:
```cpp
MonteCarloEngine mc;
// ... configurar opciones ...

auto results = mc.run();
auto sensitivities = mc.sensitivityAnalysis("MacBook Air M2");

// sensitivities["portabilidad"] = 0.85  (alto impacto)
// sensitivities["ecosistema"] = 0.23    (bajo impacto)
```

### Ventajas:
✅ Identifica **factores críticos**  
✅ Valida si decisión es **robusta**  
✅ Guía dónde enfocar esfuerzo (mejorar factores críticos)  

### Desventajas:
❌ No cambia la decisión (solo valida)  
❌ Asume variaciones lineales  

---

## 🔄 Metodologías Complementarias Avanzadas

### 6. Redes Bayesianas
**Cuándo:** Actualizar probabilidades con nueva información  
**Ejemplo:** "Si encuentro MacBook usado barato, recalcular"  
**Ventaja:** Adapta decisión dinámicamente  

### 7. Teoría de Juegos
**Cuándo:** Hay competencia o conflicto con otros agentes  
**Ejemplo:** "Competidor lanza producto similar"  
**Ventaja:** Considera movimientos estratégicos  

### 8. Opciones Reales
**Cuándo:** Valoras flexibilidad futura (option value)  
**Ejemplo:** "Valor de poder upgradear RAM después"  
**Ventaja:** Captura valor de esperar o cambiar  

### 9. Regret Analysis
**Cuándo:** Quieres minimizar arrepentimiento  
**Ejemplo:** "¿Qué decisión lamento menos si sale mal?"  
**Ventaja:** Considera psicología de pérdida  

### 10. Análisis de Escenarios
**Cuándo:** Futuros alternativos muy diferentes  
**Ejemplo:** "Optimista, Base, Pesimista"  
**Ventaja:** Prepara para múltiples futuros  

---

## 🚀 Estrategia Combinada (Recomendada)

Para decisiones complejas, usa **varios métodos en secuencia**:

```
PASO 1: TOPSIS (pre-filtrado rápido)
   ↓ Descartar opciones claramente inferiores

PASO 2: PARETO (identificar trade-offs)
   ↓ Reducir a frontera óptima

PASO 3: MONTE CARLO (análisis detallado)
   ↓ Simular incertidumbre en opciones finalistas

PASO 4: SENSIBILIDAD (validación)
   ↓ Verificar robustez de decisión

DECISIÓN FINAL: Informada por múltiples perspectivas
```

---

## 📋 Tabla Comparativa Rápida

| Método | Velocidad | Incertidumbre | Pesos | Mejor para |
|--------|-----------|---------------|-------|------------|
| **Monte Carlo** | 🐢 Lento | ✅ Maneja | Sí | Riesgo, probabilidades |
| **TOPSIS** | ⚡ Rápido | ❌ No | Sí | Ranking determinístico |
| **Pareto** | 🏃 Medio | ❌ No | No | Trade-offs, exploración |
| **Árboles** | 🏃 Medio | ⚠️ Limitado | No | Decisiones secuenciales |
| **Sensibilidad** | ⚡ Rápido | ✅ Valida | Sí | Validación robustez |

---

## 🎓 Reglas de Oro

1. **Incertidumbre significativa** → Monte Carlo
2. **Valores conocidos** → TOPSIS
3. **No sabes pesos** → Pareto
4. **Decisiones en etapas** → Árboles
5. **Validar robustez** → Sensibilidad (siempre)
6. **Actualizar con info nueva** → Bayesiano
7. **Minimizar arrepentimiento** → Regret Analysis

**Combinación ganadora:**
```
TOPSIS (rápido) → Pareto (trade-offs) → Monte Carlo (detalle) → Sensibilidad (validación)
```

---

## 📚 Referencias

- **Monte Carlo:** Metropolis & Ulam (1949)
- **TOPSIS:** Hwang & Yoon (1981)
- **Pareto:** Vilfredo Pareto (1896)
- **Árboles:** Raiffa (1968)
- **Opciones Reales:** Black-Scholes adaptado por Dixit & Pindyck (1994)

---

**Versión:** 1.0  
**Autor:** Arturo  
**Fecha:** Diciembre 2025
