# 🏔️ MINING & CAREER DECISION ANALYZER
## Guía Completa: Gemini Deep Research + Decision-Maker 13 Metodologías

**Autor**: Arturo Veras  
**Fecha**: Diciembre 2025  
**Objetivo**: Decisión de carrera minería con investigación profunda y análisis cuantitativo  

---

## 📋 Tabla de Contenidos

1. [Setup Inicial](#setup-inicial)
2. [Componentes Principales](#componentes-principales)
3. [Cómo Usar](#cómo-usar)
4. [Ejemplos Prácticos](#ejemplos-prácticos)
5. [Interpretación de Resultados](#interpretación-de-resultados)
6. [Troubleshooting](#troubleshooting)

---

## 🚀 Setup Inicial

### Paso 1: Instalar Dependencias

```bash
# Dependencia principal: google-genai para Deep Research Agent
pip install google-genai

# Otras dependencias
pip install python-dotenv requests

# Opcional (para visualización)
pip install pandas matplotlib
```

### Paso 2: Configurar API Key

El archivo `.env.gemini` ya está configurado. Verifica:

```bash
cat .env.gemini
```

Debe contener:
```
GEMINI_API_KEY=AIzaSyDIuo2lfInFZKeDAKApypziugGX8ieTRnw
GEMINI_MODEL=gemini-2.0-flash
GEMINI_DEBUG=false
```

⚠️ **IMPORTANTE**: Esta API key está en git. Debe ser revocada y reemplazada antes de usar en producción.

### Paso 3: Verificar Conexión

```bash
# Test simple
python3 gemini_query.py "¿Estás funcionando?"

# Test con Deep Research (toma 30-60 segundos)
python3 gemini_query.py --research "¿Cuál es la demanda de ingenieros IoT en minería Chile 2025?"
```

---

## 📦 Componentes Principales

### 1. **`gemini_query.py`** (Herramienta CLI)
Interfaz de línea de comandos para consultas Gemini

**Modos:**
- **Chat Simple** (Fast): Respuesta inmediata (~2s)
  ```bash
  python3 gemini_query.py "Tu pregunta"
  ```

- **Deep Research** (Thorough): Investigación profunda (~30-60s)
  ```bash
  python3 gemini_query.py --research "Tu pregunta de investigación"
  ```

**Clases:**
- `GeminiClient`: Chat simple (requests HTTP)
- `GeminiDeepResearchClient`: Deep Research Agent (google-genai)

---

### 2. **`deep_research_decision_agent.py`** (Motor de Análisis)
Sistema integrado que combina investigación + 13 metodologías

**Clases Principales:**

#### `GeminiDeepResearchAgent`
```python
agent = GeminiDeepResearchAgent(debug=True)

# Investigar una opción de carrera
result = await agent.research_option(
    option=CareerOption(...),
    context="Context adicional"
)
```

**Metodologías Implementadas (13 total):**

1. **Monte Carlo** (10,000 simulaciones)
   - Distribuye incertidumbre en factores clave
   - Retorna mean score y distribución

2. **TOPSIS** (Ranking multi-criterio)
   - Compara opción contra todas las demás
   - Retorna ranking (#1, #2, #3...)

3. **Pareto Optimality**
   - Detecta trade-offs
   - ¿Esta opción domina a otras?

4. **Regret Analysis** (Minimax Regret)
   - ¿Qué es lo peor que puede pasar?
   - Cuánto lamentarás si falla

5. **Risk Analysis** (VaR, CVaR)
   - Riesgo de desempleo + burnout + mercado
   - Score 0-1 de riesgo total

6. **Scenario Planning**
   - Robustez en: Boom, Status Quo, Recesión
   - ¿Funciona en todos los escenarios?

7-13. **Adicionales**: Bayesian, Decision Trees, Sensitivity, Correlations, Portfolio, Real Options, etc.

#### `DecisionAnalysisEngine`
```python
engine = DecisionAnalysisEngine(debug=True)

result = engine.analyze_option(
    option=CareerOption(...),
    all_options=[...],
    deep_research="Texto investigación"
)

# Resultado contiene:
result.overall_score        # 0-10
result.confidence           # 0-1
result.monte_carlo_score    # Media simulaciones
result.topsis_rank          # #1, #2, #3...
result.pareto_optimal       # True/False
result.regret_analysis      # CLP lamentados
result.risk_score           # 0-1
result.scenario_robustness  # 0-1
result.recommendation       # Texto
```

#### `CareerOption` (Data Structure)
```python
option = CareerOption(
    name="Codelco - Senior IoT Engineer",
    salary_expected=4_200_000,
    probability_success=0.70,
    timeline_months=16,
    
    # Factores 0-10
    tech_growth=8,
    income_stability=9,
    work_life_balance=5,
    prestige=9,
    remote_flexibility=2,
    learning_opportunity=7,
    career_ceiling=9,
    
    # Riesgos 0-1
    unemployment_risk=0.03,
    burnout_risk=0.35,
    market_risk=0.05
)
```

---

### 3. **`mining_career_analyzer.py`** (Análisis Específico)
Especializado en minería Chile + carrera de Arturo

**Clase Principal: `MiningCareerAnalyzer`**

```python
analyzer = MiningCareerAnalyzer(debug=True)

# Crear 5 opciones minería específicas
options = analyzer.create_mining_options()
# → Codelco, BHP, SQM, Consulting, Hybrid

# Deep research en tópicos minería
research_data = await analyzer.deep_research_mining_options(options)
# → Research de industria + empresas

# Análisis timeline (3 años a $4M)
timeline = analyzer.analyze_timeline_feasibility()
# → Fases: Prep (6w) → Apps (8w) → Interviews (8w) → Negotiation (4w)

# Matriz de comparación
matrix = analyzer.generate_comparison_matrix(options, results)
# → Tabla de 100+ líneas comparando todas opciones
```

**Base de Datos Integrada:**
```python
MINING_COMPANIES = {
    "Codelco": {stability: 9, growth: 6, prestige: 9, salary: (3.8M, 5.2M)},
    "BHP": {stability: 8, growth: 8, prestige: 9, salary: (4.2M, 5.5M)},
    ...
}

TECH_ROLES = {
    "IoT/Sensors Engineer": {salary_mult: 1.1, growth: 9, demand: "Very High"},
    "Data Engineer": {salary_mult: 1.2, growth: 10, demand: "Very High"},
    ...
}
```

---

## 🎯 Cómo Usar

### Flujo 1: Análisis Simple (5 minutos)

```bash
# 1. Chat Gemini rápido
python3 gemini_query.py "¿Cuál es salario promedio ingeniero IoT minería Chile?"

# 2. Ver resultado inmediato
# → Respuesta en ~2 segundos

# 3. Listo
```

---

### Flujo 2: Deep Research (30-60 minutos)

```bash
# 1. Investigación profunda
python3 gemini_query.py --research "Análisis completo minería Chile 2025"

# 2. Esperar (30-60 segundos)
# [DEBUG] Deep Research Agent iniciado...
# [DEBUG] Investigando empresas...
# [DEBUG] Analizando mercado...
# ✅ Research completado

# 3. Leer resultados (muy detallados)
```

---

### Flujo 3: Análisis Completo de Carrera (15-30 minutos)

```bash
# 1. Ejecutar análisis
python3 -u mining_career_analyzer.py

# 2. El script automáticamente:
#    a) Crea 5 opciones minería (Codelco, BHP, SQM, Consulting, Hybrid)
#    b) Deep research en cada una
#    c) Análisis con 13 metodologías
#    d) Genera matriz de comparación
#    e) Timeline analysis
#    f) Guarda resultados JSON

# 3. Resultados en:
#    - Terminal (resumen)
#    - mining_career_analysis_results.json (datos completos)
```

---

## 💻 Ejemplos Prácticos

### Ejemplo 1: ¿Vale la pena Codelco?

```bash
python3 gemini_query.py --research \
  "¿Es Codelco buena opción para ingeniero tech age 39 en 2025?"
```

**Respuesta esperada:** (30-60 segundos)
```
INVESTIGACIÓN PROFUNDA

En Codelco:
- Demanda muy alta para IoT engineers en operaciones minería
- Salario: $4.2M-5M típico para Senior Engineer
- Timeline: 16-20 semanas típico (reclutamiento)
- Estabilidad: 9/10 (empresa estatal)
- Beneficios: Top-tier (salud, AFP, bonos)
- Desventajas: Ubicación remota (Atacama), burocracia

Comparación con mercado:
- BHP similar salary pero más flexible
- SQM menor estabilidad pero más growth
- Tech corporativa: menos especialización
```

---

### Ejemplo 2: Timeline Realistic a $4M

```bash
python3 mining_career_analyzer.py
```

**Resultado (extracto):**
```
⏰ TIMELINE ANALYSIS
Target Date: 2026-12-13
Time Remaining: 36 months (156 weeks)

Recommended phases:

PHASE 1: Preparation (0-6 weeks)
  - LinkedIn optimization
  - CV mining-specialized
  - Company research
  - Timeline: 5-7 hours/week

PHASE 2: Applications (6-14 weeks)
  - Apply to 5-7 companies
  - First interviews expected: week 8-10
  - Timeline: 7-11 hours/week

PHASE 3: Offers (14-18 weeks)
  - Negotiate salary $4M+
  - Sign contract
  - Timeline: 2-4 hours/week

📊 REALISTIC EXPECTATION:
Contract signed by: March 2026 (12 weeks)
Start work: April 2026
Salary achievement: $4.2-4.8M ✅
```

---

### Ejemplo 3: Comparación de 5 Opciones

```bash
# Archivo se genera automáticamente con análisis completo

cat mining_career_analysis_results.json | jq '.results'
```

**Output:**
```json
{
  "Codelco - Senior IoT Engineer": {
    "score": 8.2,
    "confidence": 0.85,
    "recommendation": "⭐⭐⭐ HIGHLY RECOMMENDED",
    "salary": 4200000,
    "success_prob": 0.70
  },
  "BHP - Tech Lead": {
    "score": 8.1,
    "confidence": 0.80,
    "recommendation": "⭐⭐⭐ HIGHLY RECOMMENDED",
    "salary": 4600000,
    "success_prob": 0.55
  },
  ...
}
```

---

## 📊 Interpretación de Resultados

### Overall Score (0-10)

| Score | Interpretación |
|-------|---|
| 8-10 | ⭐⭐⭐ HIGHLY RECOMMENDED - Excelente fit |
| 6-8  | ⭐⭐ RECOMMENDED - Buena opción |
| 4-6  | ⚠️ CONSIDER - Requiere análisis más profundo |
| 0-4  | ❌ NOT RECOMMENDED - Riesgos altos |

### Confidence (0-1 = 0-100%)

- **80-100%**: Datos sólidos, recomendación fuerte
- **60-80%**: Buen análisis, algunos unknowns
- **40-60%**: Incertidumbre moderada
- **0-40%**: Muy incierto, requiere más research

### Metodologías Clave

**Monte Carlo Score**: ¿Qué tan bueno bajo incertidumbre?
- 2.0-3.0: Pobre en variabilidad
- 3.0-4.0: Aceptable
- 4.0-5.0: Bueno
- 5.0+: Excelente

**TOPSIS Rank**: ¿Ranking contra opciones?
- #1: Mejor opción según criterios
- #2-3: Alternativas viables
- #4+: Menos atractivo

**Risk Score** (0-1): ¿Qué tan riesgoso?
- 0.0-0.2: Muy seguro (estable)
- 0.2-0.4: Aceptable (normal)
- 0.4-0.6: Moderado riesgo
- 0.6+: Alto riesgo

---

## 🔧 Troubleshooting

### Problem 1: "API key not found"

```bash
# ✅ Solución
cat .env.gemini
# Debe tener GEMINI_API_KEY=...

# Si no existe:
cp .env.gemini.template .env.gemini
# Editar y agregar llave
```

### Problem 2: "google-genai no instalado"

```bash
# ✅ Solución
pip install google-genai

# O si quieres solo chat simple (sin Deep Research):
# Simplemente NO usar --research flag
```

### Problem 3: Deep Research tarda mucho (>60s)

```bash
# Normal: Deep Research toma 30-60 segundos
# Si tarda >60s:
# 1. Verificar internet
# 2. Verificar API key válida
# 3. Reducir complejidad pregunta
```

### Problem 4: "Permission denied .env.gemini"

```bash
# ✅ Solución
chmod 644 .env.gemini
```

### Problem 5: Resultados JSON no se crean

```bash
# Verificar permisos de escritura
ls -la mining_career_analysis_results.json

# Si no existe, crear manualmente:
touch mining_career_analysis_results.json
chmod 666 mining_career_analysis_results.json
```

---

## 📚 Archivos Generados

Después de correr `mining_career_analyzer.py`:

1. **`mining_career_analysis_results.json`**
   - Resultados completos en formato JSON
   - Scores de cada metodología
   - Research summaries

2. **Terminal output**
   - Matriz comparativa (100+ líneas)
   - Timeline analysis
   - Recomendaciones detalladas

3. **Logs opcionales**
   - Si `GEMINI_DEBUG=true`: archivo debug.log

---

## 🚀 Próximos Pasos

### Para Arturo (Acción Inmediata):

1. **Run full analysis**
   ```bash
   python3 mining_career_analyzer.py | tee análisis_carrera_$(date +%Y%m%d).txt
   ```

2. **Study results**
   - Revisar scores y confidence
   - Entender tradeoffs
   - Identificar bloqueadores

3. **Deep dive en top 2**
   ```bash
   python3 gemini_query.py --research "Profundizar en Codelco vs BHP para IoT engineer"
   ```

4. **Action plan**
   - Usar timeline del análisis
   - Start Phase 1 (LinkedIn + CV)
   - Contact recruiters

---

## 📞 Soporte

**Si algo no funciona:**

1. Verificar `.env.gemini` configurada
2. Correr test: `python3 gemini_query.py "¿Hola?"`
3. Check API key válida en Google Cloud Console
4. Revisar internet connection

**Debug mode:**
```bash
# Editar .env.gemini:
GEMINI_DEBUG=true

# Re-run con más información:
python3 mining_career_analyzer.py
```

---

**Made with 💙 and 13 decision methodologies**
