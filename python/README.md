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
python/
├── analyses/                          # 📊 TUS ANÁLISIS
│   ├── _template.py                  # Template para nuevo análisis
│   ├── furniture_diy.py              # Análisis muebles
│   ├── mining_improved.py            # Análisis carrera minería
│   ├── metadata.json                 # Tracking de todos los análisis
│   └── ...
├── core/                              # 🧠 Motor principal
│   ├── deep_research_decision_agent.py  # 13 metodologías + Gemini
│   └── mining_career_analyzer.py     # Analizador especializado
├── scripts/                           # 🛠️ Utilidades
│   ├── gemini_query.py
│   ├── validate_logic.py
│   └── ...
├── api/                               # 🌐 FastAPI (futuro)
├── requirements.txt                   # Dependencias
└── .env.example                       # Template de configuración
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
from core.deep_research_decision_agent import GeminiDeepResearchAgent

agent = GeminiDeepResearchAgent()
result = await agent.research_option(option, context="Mining Chile")
```

## 📊 Ejemplo de Uso

```python
from core.deep_research_decision_agent import CareerOption, DecisionAnalysisEngine

# Definir opción
option = CareerOption(
    name="Mining Engineer Chile",
    salary_expected=4_500_000,
    probability_success=0.75,
    tech_growth=6.5,
    income_stability=8.0,
    # ... más campos
)

# Analizar
engine = DecisionAnalysisEngine()
result = engine.analyze_option(option, all_options=[option])

print(f"Score: {result.overall_score}/10")
print(f"Confidence: {result.confidence*100}%")
print(result.recommendation)
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
