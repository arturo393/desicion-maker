# 🎯 Decision Maker Framework

> Sistema profesional de análisis de decisiones con implementación dual (C++ y Python) + Integración Gemini Deep Research

[![C++17](https://img.shields.io/badge/C++-17-blue.svg)](https://en.cppreference.com/w/cpp/17)
[![Python](https://img.shields.io/badge/Python-3.9+-green.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 🚀 Quick Start

### Python Framework (AI-Powered) - RECOMENDADO ⭐
```bash
cd python

# Con UV (más rápido)
uv run python core/deep_research_decision_agent.py

# O tradicional
source .venv/bin/activate
python core/deep_research_decision_agent.py
```

**Configurado con**:
- ✅ UV 0.9.17 (10-100x más rápido que pip)
- ✅ Gemini Flash (GRATIS)
- ✅ 13 metodologías + IA
- ✅ 39 paquetes instalados

### C++ Framework (Performance-Critical)
```bash
cd core
cmake -B build && cmake --build build
./build/examples/basic/sillon_decision
```

---

## 📁 Estructura del Proyecto

```
desicion-maker/
├── core/                   # C++ Framework (3,971 líneas)
│   ├── src/                # Código fuente
│   │   ├── framework/      # Framework base
│   │   ├── methodologies/  # 5 metodologías (ML, Bayesian, VaR, etc)
│   │   ├── integrations/   # API Gemini
│   │   ├── advanced/       # Herramientas avanzadas
│   │   ├── core/           # Tipos y estructuras
│   │   ├── distributions/  # 7 distribuciones estocásticas
│   │   ├── scenarios/      # Escenarios de negocio
│   │   └── utils/          # Utilidades
│   ├── examples/           # 24 ejemplos compilables
│   │   ├── basic/          # Ejemplos básicos
│   │   ├── business/       # Análisis de negocios
│   │   ├── personal/       # Decisiones personales
│   │   ├── advanced/       # Análisis avanzados
│   │   └── templates/      # Templates para nuevos casos
│   ├── docs/               # Documentación técnica C++
│   ├── CMakeLists.txt      # Build system
│   └── Makefile            # Alternative build
│
├── python/                 # Python Framework (731 líneas)
│   ├── core/               # Motor de decisiones
│   │   ├── deep_research_decision_agent.py  # 13 metodologías + Gemini
│   │   └── mining_career_analyzer.py        # Análisis minería
│   ├── tests/              # Tests organizados
│   │   ├── test_gemini_flash.py
│   │   ├── test_structure.py
│   │   └── test_framework.py
│   ├── scripts/            # Scripts de utilidad
│   │   ├── gemini_query.py
│   │   ├── validate_logic.py
│   │   └── ...más scripts
│   ├── config.py           # Sistema de modelos Gemini
│   ├── meta_decision.py    # Meta-análisis del framework
│   ├── requirements.txt    # Dependencias
│   ├── README.md           # Guía Python
│   └── .venv/              # Virtual environment (UV)
│
├── cases/                  # Casos de análisis reales
│   ├── career/             # Análisis de carrera profesional
│   ├── mining/             # Plan minería 2026 ($4.5M meta)
│   ├── decisions/          # Decisiones personales (sillón, PC)
│   └── business/           # Análisis de negocios (DeFi Monitor)
│
├── results/                # Resultados de análisis
│   ├── sillon/             # JSONs de análisis sillón
│   ├── mining/             # Resultados minería
│   └── research/           # Research Gemini
│
├── docs/                   # Documentación
│   ├── UV_SETUP.md            # Guía completa UV
│   ├── GEMINI_FLASH_SETUP.md  # Config modelos Gemini
│   ├── session-logs/          # Logs de reorganización
│   ├── tests-results/         # Resultados de análisis
│   ├── architecture/       # Arquitectura del sistema (futuro)
│   ├── guides/             # Guías de uso (futuro)
│   └── legacy/             # 9 READMEs antiguos
│
├── README.md               # Este archivo
├── QUICK_START.md          # Guía rápida
└── CHANGELOG.md            # Historial de cambios
```

---

## 🧠 Capacidades del Framework

### C++ Framework (Motor de Alto Rendimiento)

#### 5 Metodologías Avanzadas
1. **ML Demand Predictor** - Regresión logística entrenable
2. **Bayesian Updater** - Actualización probabilística con evidencia
3. **Value at Risk (VaR)** - VaR 90/95/99 + CVaR
4. **Real-Time Monitor** - Streaming de mercado
5. **Scenario Analysis** - Árboles de decisión complejos

#### 7 Distribuciones Estocásticas
- Normal (Gaussian)
- Uniform
- Triangular
- Bernoulli (Éxito/Fracaso)
- Exponential
- Beta
- Deterministic

#### Performance
- ⚡ 10k - 1M simulaciones Monte Carlo
- 🔧 Compilado a binario nativo
- 💾 Biblioteca estática linkeable
- 📐 Arquitectura OOP extensible

### Python Framework (AI-Powered)

#### 13 Metodologías de Decisión
1. Monte Carlo Simulation (10k iter)
2. TOPSIS Ranking
3. Pareto Optimality
4. Regret Analysis (Minimax)
5. Risk Analysis (VaR básico)
6. Scenario Planning
7. Sensitivity Analysis
8. Decision Trees
9. Multi-Criteria (AHP-like)
10. Expected Value
11. Break-even Analysis
12. Payoff Matrix
13. Analytic Hierarchy Process

#### Integración Gemini Deep Research
- 🤖 Research profundo de mercados
- 🌐 Búsqueda web automática
- 📊 Análisis de tendencias
- 🔄 Async/await nativo

#### Ventajas
- 🚀 Desarrollo rápido
- 🔌 FastAPI-ready
- 📦 Fácil deployment
- 🧪 Testing simple

---

## 📊 Comparación: Python vs C++

| Aspecto | Python | C++ |
|---------|--------|-----|
| **Líneas de código** | 731 | 3,971 |
| **Metodologías** | 13 simples | 5 avanzadas |
| **Monte Carlo** | 10k iter | 10k-1M iter |
| **Distribuciones** | 1 (uniforme) | 7 tipos |
| **ML Predictor** | ❌ | ✅ Entrenable |
| **Bayesian Update** | ❌ | ✅ Formal |
| **VaR/CVaR** | Básico | VaR 90/95/99 |
| **Gemini Integration** | ✅ Nativo | ⚠️ Via API |
| **Performance** | Moderado | Muy rápido |
| **Desarrollo** | Rápido | Complejo |
| **Mejor para** | Prototipo + AI | Producción + Escala |

**Recomendación**: Usar ambos en arquitectura híbrida (Python orquesta + C++ procesa)

---

## 🎯 Casos de Uso

### 1. Análisis de Carrera (Mining 2026)
```bash
cd python
python3 core/mining_career_analyzer.py
```
- Meta: $4.5M+ salario minería Chile
- Timeline: 12 semanas
- Probabilidad: 70-80%

### 2. Decisión Personal (Sillón)
```bash
cd core
./build/examples/personal/sillon_decision
```
- Opciones: Botar vs Restaurar vs Vender
- Metodologías: 5 análisis cruzados
- Resultado: Recomendación con confianza

### 3. Análisis de Negocio (DeFi Monitor)
```bash
cd python
python3 scripts/analyze_defi_monitor_business.py
```
- Evaluación de viabilidad
- Market sizing
- Risk assessment

---

## 🛠️ Instalación Completa

### Requisitos
- **C++**: g++ 9+ o clang 10+, CMake 3.12+
- **Python**: 3.9+, pip
- **API Keys**: Gemini API (opcional)

### Setup C++
```bash
cd core
cmake -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build -j4

# Ejecutar ejemplo
./build/examples/basic/demo_simple
```

### Setup Python
```bash
cd python
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Configurar API key
cp .env.example .env
# Editar .env y agregar: GEMINI_API_KEY=tu_clave_aqui

# Ejecutar
python3 core/deep_research_decision_agent.py
```

---

## 📖 Documentación

- **[QUICK_START.md](QUICK_START.md)** - Guía rápida de inicio
- **[core/docs/](core/docs/)** - Documentación técnica C++
- **[docs/architecture/](docs/architecture/)** - Arquitectura del sistema
- **[cases/](cases/)** - Ejemplos de casos reales

---

## 🧪 Testing

### C++ Tests
```bash
cd core
cmake -B build -DENABLE_TESTING=ON
cmake --build build
ctest --test-dir build
```

### Python Tests
```bash
cd python
pytest tests/
```

---

## 🤝 Contribuir

1. Fork el repositorio
2. Crea una rama: `git checkout -b feature/nueva-metodologia`
3. Commit: `git commit -am 'Add nueva metodología'`
4. Push: `git push origin feature/nueva-metodologia`
5. Abre Pull Request

---

## 📝 Changelog

Ver [CHANGELOG.md](CHANGELOG.md) para historial completo.

### v2.0.0 (Diciembre 2024)
- ✅ Reorganización completa del repositorio
- ✅ Separación C++ / Python
- ✅ Estructura profesional modular
- ✅ 13 metodologías Python
- ✅ 5 metodologías C++ avanzadas
- ✅ Integración Gemini Deep Research
- ✅ 24 ejemplos compilables
- ✅ Documentación completa

---

## 📄 Licencia

MIT License - Ver [LICENSE](LICENSE) para detalles.

---

## 🎯 Próximos Pasos

### Para Usuarios
1. Explora [cases/mining/](cases/mining/) - Plan minería 2026
2. Ejecuta ejemplo sillón: `cd core && make sillon_decision && ./sillon_decision`
3. Prueba Python + Gemini: `cd python && python3 core/deep_research_decision_agent.py`

### Para Desarrolladores
1. Lee [docs/architecture/HYBRID_ARCHITECTURE.md](docs/architecture/)
2. Crea tu primer caso con `core/examples/templates/template_new_decision.cpp`
3. Contribuye con nuevas metodologías

---

## 📬 Contacto

- Issues: [GitHub Issues](https://github.com/tu-usuario/desicion-maker/issues)
- Discussions: [GitHub Discussions](https://github.com/tu-usuario/desicion-maker/discussions)

---

**⭐ Si este proyecto te ayudó a tomar mejores decisiones, dale una estrella!**
