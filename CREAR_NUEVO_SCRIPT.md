# 🎯 Crear Nuevo Script de Decisión (Dual Framework)

Guía rápida para crear un nuevo script que analice decisiones usando **ambos frameworks** (Python + C++) y compare resultados.

---

## ⚡ Opción Más Rápida: Solo Python (Recomendado)

### Paso 1: Crear archivo Python

```bash
cd python
cp core/deep_research_decision_agent.py myscript_decision.py
```

### Paso 2: Modificar el script

```python
#!/usr/bin/env python3
"""Tu análisis de decisión aquí"""

from core.deep_research_decision_agent import (
    CareerOption,
    DecisionAnalysisEngine,
    GeminiDeepResearchAgent
)
import asyncio

# 1️⃣ DEFINIR TUS OPCIONES
opciones = [
    CareerOption(
        name="Opción A",
        salary_expected=4_000_000,
        probability_success=0.70,
        timeline_months=12,
        tech_growth=7.0,
        income_stability=8.0,
        work_life_balance=6.0,
        prestige=7.5,
        remote_flexibility=8.0,
        learning_opportunity=8.0,
        career_ceiling=9.0,
        unemployment_risk=0.1,
        burnout_risk=0.2,
        market_risk=0.15,
        description="Descripción opción A",
        pros=["Pro 1", "Pro 2"],
        cons=["Con 1", "Con 2"]
    ),
    CareerOption(
        name="Opción B",
        salary_expected=5_000_000,
        probability_success=0.60,
        timeline_months=18,
        tech_growth=8.5,
        income_stability=6.0,
        work_life_balance=7.0,
        prestige=8.5,
        remote_flexibility=7.0,
        learning_opportunity=9.0,
        career_ceiling=10.0,
        unemployment_risk=0.2,
        burnout_risk=0.3,
        market_risk=0.25,
        description="Descripción opción B",
        pros=["Pro 1", "Pro 2"],
        cons=["Con 1", "Con 2"]
    ),
]

# 2️⃣ ANALIZAR CON 13 METODOLOGÍAS
engine = DecisionAnalysisEngine()
results = engine.analyze_all_options(opciones)

# 3️⃣ DEEP RESEARCH CON GEMINI (OPCIONAL)
async def deep_research():
    agent = GeminiDeepResearchAgent()
    for option in opciones:
        research = await agent.research_option(
            option.name,
            context="Mi contexto aquí"
        )
        print(f"\n📊 Research para {option.name}:")
        print(research)

# 4️⃣ EJECUTAR
if __name__ == "__main__":
    print("=" * 80)
    print("📊 ANÁLISIS DE DECISIÓN (13 Metodologías)")
    print("=" * 80)
    
    # Mostrar resultados
    engine.print_comparison_matrix(results)
    
    # Deep research (opcional)
    asyncio.run(deep_research())
```

### Paso 3: Ejecutar

```bash
# Con UV (recomendado)
uv run myscript_decision.py

# O tradicional
python3 myscript_decision.py
```

---

## 🔥 Opción Completa: Python + C++ (Comparación)

Para comparar resultados entre ambos frameworks:

### Paso 1: Script Python

```bash
cd python
cat > compare_frameworks.py << 'EOF'
#!/usr/bin/env python3
import json
import subprocess
from core.deep_research_decision_agent import (
    CareerOption, DecisionAnalysisEngine
)

# Tus opciones
opciones = [
    CareerOption(
        name="Opción A",
        salary_expected=4_000_000,
        probability_success=0.70,
        timeline_months=12,
        tech_growth=7.0,
        income_stability=8.0,
        work_life_balance=6.0,
        prestige=7.5,
        remote_flexibility=8.0,
        learning_opportunity=8.0,
        career_ceiling=9.0,
        unemployment_risk=0.1,
        burnout_risk=0.2,
        market_risk=0.15,
    ),
]

# 1️⃣ Python Analysis
engine = DecisionAnalysisEngine()
python_results = engine.analyze_all_options(opciones)

# 2️⃣ C++ Analysis (ejecutar C++)
cpp_output = subprocess.run(
    ["../core/build/examples/basic/your_cpp_example"],
    capture_output=True,
    text=True
)
cpp_results = json.loads(cpp_output.stdout)

# 3️⃣ Comparar
print("=" * 80)
print("📊 COMPARACIÓN: Python vs C++")
print("=" * 80)
print(f"\nPython Score:  {python_results[0]['overall_score']:.2f}/10")
print(f"C++ Score:     {cpp_results[0]['overall_score']:.2f}/10")
print(f"Diferencia:    {abs(python_results[0]['overall_score'] - cpp_results[0]['overall_score']):.2f}")

# Exportar comparación
comparison = {
    "timestamp": datetime.now().isoformat(),
    "python": python_results,
    "cpp": cpp_results,
    "difference": abs(python_results[0]['overall_score'] - cpp_results[0]['overall_score'])
}

with open("framework_comparison.json", "w") as f:
    json.dump(comparison, f, indent=2)

print("\n✅ Resultados guardados en framework_comparison.json")
EOF
```

### Paso 2: Crear ejemplo C++

```bash
cd ../core/examples/basic
cat > my_decision.cpp << 'EOF'
#include "../../src/framework/decision_engine.hpp"
#include "../../src/methodologies/monte_carlo.hpp"
#include "../../src/methodologies/topsis.hpp"
#include <iostream>
#include <json/json.h>

using namespace DecisionMaker;

int main() {
    // Crear opciones
    DecisionOption opcionA{
        .name = "Opción A",
        .expectedValue = 4000000.0,
        .probability = 0.70,
        .factors = {7.0, 8.0, 6.0, 7.5, 8.0, 8.0, 9.0}
    };
    
    DecisionOption opcionB{
        .name = "Opción B",
        .expectedValue = 5000000.0,
        .probability = 0.60,
        .factors = {8.5, 6.0, 7.0, 8.5, 7.0, 9.0, 10.0}
    };
    
    // Analizar
    DecisionEngine engine;
    auto results = engine.analyzeOptions({opcionA, opcionB});
    
    // Output JSON
    Json::Value output;
    for (const auto& result : results) {
        output.append(result.toJson());
    }
    
    std::cout << output.toStyledString() << std::endl;
    return 0;
}
EOF
```

### Paso 3: Compilar y ejecutar

```bash
cd ../..
cmake -B build && cmake --build build

python3 python/compare_frameworks.py
```

---

## 📊 13 Metodologías Disponibles

| # | Metodología | Mejor para | Tiempo |
|---|---|---|---|
| 1 | **Monte Carlo** | Simulaciones probabilísticas | 2s |
| 2 | **TOPSIS** | Ranking multi-criterio | <1s |
| 3 | **Pareto** | Optimización | <1s |
| 4 | **Regret** | Minimax regret analysis | <1s |
| 5 | **VaR** | Value at Risk | <1s |
| 6 | **Scenario** | Planning robusto | 1s |
| 7 | **Sensitivity** | Análisis sensibilidad | 1s |
| 8 | **Decision Trees** | Secuencias de decisión | 1s |
| 9 | **Multi-Criteria** | AHP-style ranking | <1s |
| 10 | **Expected Value** | Valor esperado ponderado | <1s |
| 11 | **Break-even** | Punto de equilibrio | <1s |
| 12 | **Payoff Matrix** | Matriz de pagos | <1s |
| 13 | **AHP** | Hierarchy analysis | 1s |

Todas se ejecutan **automáticamente** - no necesitas elegir, obtienen todas.

---

## 🔧 Configuración Rápida

### Variables de Entorno

```bash
# .env
GEMINI_API_KEY=tu_api_key_aqui
GEMINI_MODEL=gemini-2.0-flash-exp
```

### Instalar dependencias

```bash
cd python
uv sync  # Recomendado - 10x más rápido
# o
pip install -r requirements.txt
```

---

## 📝 Template Mínimo (Copia y Pega)

```python
#!/usr/bin/env python3
from core.deep_research_decision_agent import CareerOption, DecisionAnalysisEngine

# TUS OPCIONES
opciones = [
    CareerOption(
        name="Opción 1",
        salary_expected=4_000_000,
        probability_success=0.70,
        timeline_months=12,
        tech_growth=7.0,
        income_stability=8.0,
        work_life_balance=6.0,
        prestige=7.5,
        remote_flexibility=8.0,
        learning_opportunity=8.0,
        career_ceiling=9.0,
        unemployment_risk=0.1,
        burnout_risk=0.2,
        market_risk=0.15,
    ),
]

# ANALIZAR
engine = DecisionAnalysisEngine()
results = engine.analyze_all_options(opciones)
engine.print_comparison_matrix(results)
```

Eso es todo - solo 20 líneas y obtienes **13 análisis** automáticos.

---

## 🚀 Ejemplos Reales en el Repositorio

```bash
python/core/mining_career_analyzer.py      # Análisis minería 2026
python/core/deep_research_decision_agent.py # Framework principal
core/examples/business/                     # Ejemplos C++ negocios
core/examples/personal/                     # Ejemplos C++ personales
```

---

## 💡 Tips

- **Python es más rápido** para prototipado
- **C++ es más preciso** para análisis complejos
- **Compara ambos** para decisiones críticas
- **Usa Gemini** para context y validación
- **JSON los resultados** para análisis posterior

---

## ❓ Preguntas Frecuentes

**¿Necesito ambos frameworks?**
→ No. Python solo es suficiente. C++ para análisis de alto rendimiento.

**¿Cuánto tarda?**
→ Python: 30-60s (incluye Gemini research)
→ C++: <2s (solo análisis matemático)

**¿Cómo exporto resultados?**
→ Automáticamente en JSON. Ver `results/` directorio.

**¿Puedo agregar más metodologías?**
→ Sí. Ve a `core/methodologies/` (Python o C++) y agrega.

---

**🎯 ¡Listo para crear tu primer análisis?**

```bash
cd python
uv run python/core/deep_research_decision_agent.py
```
