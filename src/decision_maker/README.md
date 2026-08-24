# Python Decision Framework

Motor de decisiones en Python con integración Gemini Deep Research.

## 🚀 Quick Start

```bash
# Crear entorno virtual
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar API key
cp .env.example .env
# Editar .env y agregar: GEMINI_API_KEY=tu_clave_aqui

# Ejecutar análisis de ejemplo
python3 analyses/furniture_diy.py
```

## 📊 Análisis Activos

Colección de análisis de decisiones personales usando el framework:

| Análisis | Propósito | Estado | Última Actualización |
|----------|-----------|--------|---------------------|
| [furniture_diy.py](analyses/furniture_diy.py) | Compra de muebles DIY vs usados | ✅ Activo | 2026-01-03 |
| [mining_improved.py](analyses/mining_improved.py) | Decisión de carrera en minería (v2) | ✅ Activo | 2026-01-03 |
| [sqm_santiago.py](analyses/sqm_santiago.py) | Análisis proyecto SQM Santiago | ✅ Activo | 2025-12-10 |
| [refactoring_decision.py](analyses/refactoring_decision.py) | Decisión de refactorización | ✅ Completado | 2025-11-30 |
| [mining_decision.py](analyses/mining_decision.py) | Carrera minería (v1 - obsoleta) | 📦 Archivado | 2025-12-15 |

**📝 Ver detalles completos**: [analyses/metadata.json](analyses/metadata.json)

## 🆕 Crear Nuevo Análisis

1. **Copiar template**:
   ```bash
   cp analyses/_template.py analyses/mi_analisis.py
   ```

2. **Editar y configurar**:
   - Cambiar `analysis_name`
   - Definir `research_question`
   - Configurar `alternatives` y `criteria`

3. **Ejecutar**:
   ```bash
   python3 analyses/mi_analisis.py
   ```

4. **Resultados** se guardan automáticamente en `results/mi_analisis/`

## 📁 Estructura

```
src/decision_maker/
├── analyses/                          # 📊 TUS ANÁLISIS
│   ├── _template.py                  # Template para nuevo análisis
│   ├── furniture_diy.py              # Análisis muebles
│   ├── mining_improved.py            # Análisis carrera minería
│   ├── metadata.json                 # Tracking de todos los análisis
│   └── ...
├── core/                              # 🧠 Motor principal
│   ├── orchestrator.py               # UnifiedDecisionFramework
│   ├── fuzzy_weighted_sum.py         # Fuzzy weighted-sum (lingüístico)
│   └── ...                            # 30+ módulos (TOPSIS, PROMETHEE, Monte Carlo, etc.)
├── api/                               # 🌐 FastAPI
│   └── server.py
├── dashboard/                         # 📊 Streamlit
│   └── app.py
└── tests/                             # ✅ Pytest (482 tests)
```

## 🧠 13 Metodologías

1. **Monte Carlo** - 10k simulaciones
2. **TOPSIS** - Ranking multi-criterio
3. **Pareto** - Optimización
4. **Regret** - Minimax regret
5. **VaR** - Value at Risk
6. **Scenario** - Planning robusto
7. **Sensitivity** - Análisis sensibilidad
8. **Decision Trees** - Secuencias
9. **Multi-Criteria** - AHP-like
10. **Expected Value** - Valor esperado
11. **Break-even** - Punto equilibrio
12. **Payoff Matrix** - Matriz de pagos
13. **AHP** - Analytic Hierarchy

## 🤖 Gemini Integration

```python
from python.core.gemini_agent import GeminiDeepResearchAgent

agent = GeminiDeepResearchAgent()
result = await agent.research(topic="Decision analysis", context="...")
```

## 📊 Ejemplo de Uso

```python
from python.core.orchestrator import UnifiedDecisionFramework
from python.core.models import DecisionOption, DistributionType, Factor

# Definir factores y opciones
framework = UnifiedDecisionFramework()
framework.add_factor(Factor("Costo", 0.5, maximize=False))
framework.add_factor(Factor("Beneficio", 0.5, maximize=True))

opt = DecisionOption("Opción A", "Descripción")
opt.add_variable("Costo", DistributionType.NORMAL, 1000, 200)
opt.add_variable("Beneficio", DistributionType.NORMAL, 5000, 1000)
framework.add_option(opt)

import asyncio
result = asyncio.run(framework.run_analysis(mode="standard"))
```

## 🔧 Development

```bash
# Instalar en modo desarrollo
pip install -e .

# Run tests
pytest tests/

# Linting
black core/ scripts/
flake8 core/ scripts/
```

## 📖 Ver También

- [../README.md](../README.md) - Documentación principal
- [../core/](../core/) - Framework C++ (más completo)
- [../cases/](../cases/) - Casos de uso reales
