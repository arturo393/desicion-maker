# 🏗️ Arquitectura - Decision Maker Framework

Descripción técnica de la estructura dual del framework (C++ + Python) y sus componentes.

---

## 📐 Visión General

**Decision Maker** es un framework profesional que combina:

- **Python Framework** 🐍: AI-powered con Gemini, rápido prototipado (10-100x más rápido con UV)
- **C++ Framework** ⚙️: Performance-critical, simulaciones complejas, 13 metodologías

Ambos frameworks comparten:
- Mismas 13 metodologías de decisión
- API compatible para facilitar comparación
- Integración profunda con Google Gemini (Deep Research + Chat)

---

## 🐍 Python Framework

### Ubicación
```
python/
├── core/
│   ├── deep_research_decision_agent.py    (732 líneas - CORE)
│   └── __init__.py
├── scripts/
│   ├── mining_career_analyzer.py
│   ├── gemini_query.py
│   ├── research_leaky_feeder.py
│   └── deep_research_analyzer.py
├── tests/
│   └── test_*.py
├── api/
│   └── [API integrations]
├── pyproject.toml
├── requirements.txt
└── .env.gemini
```

### Componentes Principales

#### 1. **deep_research_decision_agent.py** (Core)
```python
# Dataclasses
@dataclass CareerOption          # Opciones de decisión con 13 atributos
@dataclass AnalysisResult        # Resultados por metodología

# Clases Principales
class DecisionAnalysisEngine:     # Ejecuta 13 metodologías
  - analyze_all_options()        # Análisis global
  - apply_monte_carlo()          # Simulación estocástica
  - apply_topsis()               # Ranking multi-criterio
  - apply_pareto()               # Frontera eficiente
  - apply_vat()                  # Value at Risk
  - ... (13 total)
  - print_comparison_matrix()    # Output formateado

class GeminiDeepResearchAgent:   # Integración con Gemini
  - research_option()            # Análisis profundo async
  - generate_report()            # Reporte compilado
```

#### 2. **mining_career_analyzer.py** (Ejemplo Específico)
Caso de uso completo: análisis de 5 opciones minería (Codelco, BHP, SQM, etc.)
- Timeline realista por fase
- Pesos contextuales por criterio
- Integración con Deep Research Pro
- Output JSON + matriz comparativa

#### 3. **Scripts Utilitarios**
- `gemini_query.py`: Testing rápido de API Gemini
- `research_leaky_feeder.py`: Análisis específico infraestructura
- `deep_research_analyzer.py`: Wrapper Deep Research Pro + Framework

### Flujo Típico Python

```
1. Definir opciones (CareerOption dataclass)
   ↓
2. Instanciar DecisionAnalysisEngine
   ↓
3. engine.analyze_all_options(options)
   ├── Aplica 13 metodologías en paralelo
   ├── Genera matriz comparativa (100+ líneas)
   └── Retorna AnalysisResult dict
   ↓
4. [Opcional] GeminiDeepResearchAgent.research_option()
   ├── Deep Research Pro (15-30 min por opción)
   ├── 30-50 fuentes por análisis
   └── 20K+ tokens generados
   ↓
5. Print results / Save JSON
```

### Dependencias Python

```toml
# Especificadas en pyproject.toml
python = "^3.9"
google-genai = "^0.5"      # Gemini API
numpy = "^1.24"            # Cálculos
scipy = "^1.10"            # Estadística
pandas = "^2.0"            # DataFrames
```

**Package Manager**: UV 0.9.17 (recomendado)
```bash
uv sync                    # Instala todas las dependencias
uv run python core/...     # Ejecuta con env automático
```

---

## ⚙️ C++ Framework

### Ubicación
```
core/
├── src/
│   ├── framework/          # Base del framework
│   │   ├── decision_framework.h
│   │   ├── option.h
│   │   └── metrics.h
│   ├── methodologies/      # Implementaciones de decisión
│   │   ├── monte_carlo.h
│   │   ├── topsis.h
│   │   ├── pareto.h
│   │   ├── vat.h
│   │   └── [9 más]
│   ├── distributions/      # Distribuciones probabilísticas
│   │   ├── normal.h
│   │   ├── triangular.h
│   │   ├── uniform.h
│   │   └── [4 más]
│   ├── integrations/       # APIs externas
│   │   └── gemini_integration.h
│   ├── advanced/           # Herramientas avanzadas
│   │   ├── decision_tree.h
│   │   ├── sensitivity_analysis.h
│   │   └── scenario_planner.h
│   ├── core/               # Tipos base
│   │   ├── types.h
│   │   └── config.h
│   └── utils/              # Utilidades
├── examples/
│   ├── basic/
│   │   └── sillon_decision.cpp
│   ├── business/
│   │   └── [ejemplos negocio]
│   ├── personal/
│   │   └── [ejemplos personales]
│   ├── advanced/
│   │   └── [ejemplos avanzados]
│   ├── templates/
│   │   └── [plantillas]
│   └── deep_research_decision_example.cpp
├── tests/
│   └── test_*.cpp
├── CMakeLists.txt          # Build configuration
└── cmake/
    └── [módulos cmake]
```

### Componentes Principales

#### 1. **framework/** (Base)
```cpp
class DecisionOption {
  - name: string
  - criteria: map<string, float>
  - alternatives: vector<string>
  - constraints: vector<Constraint>
};

class DecisionFramework {
  - addOption(option)
  - analyze()               // Ejecuta análisis
  - getResults()            // Retorna AnalysisResult
  - compareOptions()        // Matriz comparativa
};
```

#### 2. **methodologies/** (13 Algoritmos)
Cada metodología como header separado:
- `monte_carlo.h`: Simulación estocástica (10K iteraciones)
- `topsis.h`: Technique for Order Preference (ranking)
- `pareto.h`: Frontera eficiente (Pareto)
- `bayesian.h`: Probabilidad bayesiana
- `vat.h`: Value at Risk (downside risk)
- Y 8 más...

Estructura común:
```cpp
template<typename T>
class MethodologyName {
  public:
    AnalysisResult analyze(const vector<DecisionOption>& options);
};
```

#### 3. **distributions/** (Estocástica)
7 distribuciones para Monte Carlo:
- Normal (Gaussian)
- Triangular
- Uniform
- Beta
- Exponential
- Lognormal
- Custom

#### 4. **integrations/** (Gemini)
```cpp
class AIAnalyzer {
  - analyzeDecisionDeep(decision, options, criteria)
  - generateReport()
  - callGeminiAPI()
};
```

### Flujo Típico C++

```
1. Definir opciones como DecisionOption
   ↓
2. Instanciar DecisionFramework
   ↓
3. framework.addOption(option1, option2, ...)
   ↓
4. framework.analyze()
   ├── Compila todas las metodologías en paralelo
   ├── Ejecuta simulaciones (Monte Carlo ~1000ms)
   └── Genera matriz comparativa
   ↓
5. auto results = framework.getResults()
   ├── scores: map<string, float>
   ├── ranking: vector<string>
   └── confidence: float
   ↓
6. framework.compareOptions()  → Output formateado
```

### Build System (CMake)

```cmake
# Compilar todas las metodologías
cmake -B build -DENABLE_DEEP_RESEARCH=ON
cmake --build build -j4

# Ejecutar ejemplo
./build/examples/basic/sillon_decision

# Con opciones
cmake -DCMAKE_BUILD_TYPE=Release -DENABLE_OPTIMIZATION=ON
```

### Performance

| Metodología | Tiempo | Iteraciones |
|-------------|--------|------------|
| TOPSIS | ~5ms | 1 pass |
| Monte Carlo | ~500ms | 10K |
| Pareto | ~50ms | completo |
| Bayesian | ~100ms | iterativo |
| Sensitivity | ~200ms | 1K+ |
| **Total (todas)** | **~2s** | paralelo |

---

## 🔗 Integración Dual

### Comparación Python vs C++

```
OPCIÓN A: Python Solo (RECOMENDADO)
├── Setup: 2 min (UV sync)
├── Ejecución: 30s (13 metodologías)
├── Deep Research: +15-30 min (opcional)
└── Total: 30s → 30+ min

OPCIÓN B: Python + C++
├── Setup: 5 min (compilar C++)
├── Ejecución: 2s C++ + 30s Python
├── Comparación: Resultados lado a lado
└── Total: 2s + 30s
```

### Llamar C++ desde Python

```python
import subprocess
import json

# Compilar si es necesario
subprocess.run(["cmake", "--build", "core/build"])

# Ejecutar C++ con argumentos JSON
result = subprocess.run([
    "core/build/examples/decision_analysis",
    "--options", json.dumps(options),
    "--format", "json"
], capture_output=True)

# Comparar con Python
cpp_results = json.loads(result.stdout)
python_results = engine.analyze_all_options(options)

# Matriz comparativa
compare_results(cpp_results, python_results)
```

---

## 📦 Gestión de Dependencias

### Python

```bash
# Instalación (recomendado: UV)
cd python
uv sync              # Crea .venv y instala todo

# O tradicional
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Ejecutar
uv run python core/deep_research_decision_agent.py
```

### C++

```bash
# Requisitos: CMake 3.15+, C++17 compiler

# Windows (MSVC)
cmake -G "Visual Studio 16 2019" -B build
cmake --build build

# MacOS/Linux (GCC/Clang)
cmake -B build
cmake --build build -j$(nproc)
```

---

## 🗂️ Separación de Responsabilidades

| Carpeta | Propósito | Lenguaje | Cuándo Usar |
|---------|----------|----------|------------|
| `python/core/` | Motores de decisión IA | Python | Siempre (principal) |
| `python/scripts/` | Tools y análisis específicos | Python | Casos de uso |
| `core/src/` | Framework performante | C++ | Análisis heavy |
| `core/examples/` | Ejemplos compilables | C++ | Learning |
| `examples/` | Notebooks y scripts Python | Python | Prototipos |
| `docs/` | Documentación técnica | Markdown | Referencia |

---

## 🔄 Ciclo de Desarrollo

```
Idea → Python Prototype (30s) → Test → C++ Optimization (si necesario)
        ↓
     Gemini Deep Research (15-30 min, opcional)
        ↓
     Matriz Comparativa (2-5 min)
        ↓
     Reporte Final + JSON
```

---

## 🚀 Quick Start por Rol

### Para Data Scientists
```bash
cd python
uv run python core/deep_research_decision_agent.py
# Editar opciones, ejecutar, iterar rápidamente
```

### Para C++ Developers
```bash
cd core
cmake -B build && cmake --build build
./build/examples/basic/sillon_decision
# Editar metodologías, recompilar, benchmarks
```

### Para DevOps/Productionización
```bash
# Python wrapper que llama C++ si es necesario
python examples/hybrid_analysis.py --mode=both
# Genera reportes, auditoría, métricas
```

---

## 📊 Estructura de Datos Compartida

Ambos frameworks usan estructura similar:

```
Option {
  name: string
  criteria: {
    salary: 0.85,
    growth: 0.72,
    balance: 0.65,
    ...
  }
  constraints: [...]
  timeline: int_months
}

Result {
  option_name: string
  methodology: string
  score: float
  confidence: float
  rank: int
}

AnalysisResult {
  options: [Option]
  results: [Result]
  winner: string
  comparison_matrix: [[float]]
  timestamp: datetime
}
```

---

## ✅ Validación de Setup

```bash
# Python
cd python && uv run python -c "from core.deep_research_decision_agent import *; print('✅ Python OK')"

# C++
cd core && cmake -B build && cmake --build build && echo "✅ C++ OK"

# Gemini
python scripts/gemini_query.py "test"

# Full
python examples/hybrid_analysis.py  # Ejecuta Python + C++ + Gemini
```

---

## 🔗 Versioning

- **Framework Version**: 2.0.0 (en CMakeLists.txt + pyproject.toml)
- **Python**: 3.9+
- **C++**: C++17
- **Gemini**: Flash (free tier)

Ver [CHANGELOG.md](./CHANGELOG.md) para historial completo.

