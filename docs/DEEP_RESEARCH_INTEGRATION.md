# 🤖 Deep Research Pro Integration

Integración de **Google's Deep Research Pro** con el **Decision Maker Framework**.

Combina:
- 📊 **Análisis rápido** (framework de decisiones: 10-30 segundos)
- 🔬 **Análisis profundo** (Deep Research Pro: 3-5 minutos)

---

## 🚀 Quick Start

### 1. Instalar SDK

```bash
# Deep Research Pro usa google-genai (NO google-generativeai)
pip install google-genai
# O con uv:
uv pip install google-genai
```

### 2. Configurar API Key

```bash
# Opción A: Variable de entorno
export GOOGLE_API_KEY="tu_api_key_aqui"

# Opción B: En código (archivos .env)
echo "GOOGLE_API_KEY=tu_api_key_aqui" > .env.gemini
```

### 3. Ejecutar Ejemplo

```bash
# Versión Python (standalone)
uv run scripts/deep_research_analyzer.py

# Versión C++ (con framework)
cd decision-maker
g++ -std=c++17 -O2 examples/deep_research_decision_example.cpp -o bin/deep_research_example
./bin/deep_research_example
```

---

## 📁 Archivos Agregados

### Scripts Python

```
scripts/deep_research_analyzer.py
└── Analizador con Deep Research Pro
    ├── analyze_with_deep_research() - Ejecuta investigación
    ├── analyze_decision() - Analiza opciones vs criterios
    └── Ejemplos de uso listos
```

**Uso directo:**
```bash
uv run scripts/deep_research_analyzer.py
```

**Output:**
- Análisis de Computadora (3-5 min)
- Análisis de Trabajo vs Freelance (3-5 min)
- Resultados JSON completos

### Headers C++

```
src/ai_deep_research_integration.h
└── Integración C++ con Deep Research Pro
    ├── AIAnalyzer - Clase principal
    ├── AIAnalysisResult - Resultado estructurado
    └── Métodos:
        ├── analyzeDecisionDeep() - Análisis profundo (3-5 min)
        ├── analyzeDecisionQuick() - Análisis rápido con Gemini (1-2 min)
        └── analyzeQuestion() - Pregunta libre
```

**Uso en C++:**
```cpp
#include "src/ai_deep_research_integration.h"
using namespace AIIntegration;

AIAnalyzer analyzer;
auto result = analyzer.analyzeDecisionDeep(
    "Mi Decisión",
    {{"Opción A", "Descripción"}, {"Opción B", "Descripción"}},
    {{"Criterio 1", 8}, {"Criterio 2", 6}}
);

std::cout << result.recommendation << "\n";
```

### Ejemplos

```
examples/deep_research_decision_example.cpp
└── Decisión Computadora con Framework + Deep Research
    ├── Parte 1: Monte Carlo (10s)
    ├── Parte 2: Deep Research Pro (3-5 min)
    ├── Parte 3: Resultados combinados
    └── Salida: Recomendación dual
```

**Compilar:**
```bash
g++ -std=c++17 -O2 examples/deep_research_decision_example.cpp -o bin/deep_research_example
```

---

## 🔧 Configuración Detallada

### Variables de Entorno

```bash
# API Key de Google
export GOOGLE_API_KEY="AIzaSyDIuo2lfInFZKeDAKApypziugGX8ieTRnw"

# Ruta al script Python (opcional, default: scripts/deep_research_analyzer.py)
export AI_SCRIPT_PATH="scripts/deep_research_analyzer.py"
```

### Archivos .env

```bash
# .env.gemini (ejemplo)
GOOGLE_API_KEY=AIzaSyDIuo2lfInFZKeDAKApypziugGX8ieTRnw
AI_ANALYZER_TIMEOUT=600
AI_ANALYZER_SCRIPT_PATH=scripts/deep_research_analyzer.py
```

---

## 📊 Modelos Disponibles

### Deep Research Pro (Profundo)
- **Modelo:** `deep-research-pro-preview-12-2025`
- **Tiempo:** 3-5 minutos
- **Profundidad:** Máxima
- **Tokens:** 25,000+ por respuesta
- **Mejor para:** Decisiones complejas, análisis exhaustivo
- **Costo:** Relativamente alto

```cpp
// Usar Deep Research (default)
auto result = analyzer.analyzeDecisionDeep(...);
```

### Gemini 2.5 Pro (Rápido)
- **Modelo:** `gemini-2.5-pro`
- **Tiempo:** 1-2 minutos
- **Profundidad:** Alta
- **Tokens:** 10,000 por respuesta
- **Mejor para:** Decisiones simples, prototipado
- **Costo:** Bajo

```cpp
// Usar Gemini rápido
auto result = analyzer.analyzeDecisionQuick(...);
```

---

## 🎯 Flujo de Uso Recomendado

### Para Decisiones Simples

```
1. TOPSIS (framework)         → 100ms  → Ranking rápido
2. Gemini 2.5 Pro (AI)        → 90s   → Validación
3. Decisión Final             → 5s    → Acción
```

**Tiempo total:** ~2 minutos

### Para Decisiones Complejas

```
1. Monte Carlo (framework)    → 10s   → Simulación
2. Pareto (framework)         → 5s    → Trade-offs
3. Deep Research Pro (AI)     → 4min  → Investigación profunda
4. Sensibilidad (framework)   → 10s   → Validación
5. Decisión Final             → 5s    → Acción
```

**Tiempo total:** ~5 minutos

### Para Decisiones Críticas

```
1. Todos los métodos arriba (framework)     → 30s
2. Deep Research Pro (análisis 1)           → 4min
3. Deep Research Pro (perspectiva 2)        → 4min
4. Análisis de riesgo (framework)           → 10s
5. Escenarios (framework)                   → 15s
6. Decisión Final                           → 10s
```

**Tiempo total:** ~9 minutos

---

## 📊 Ejemplo: Decisión de Computadora

### Input

```cpp
AIAnalyzer analyzer;

auto result = analyzer.analyzeDecisionDeep(
    "Compra de Computadora Portátil 2025",
    {
        {"MacBook Air M2", "Portátil M2, 8GB RAM, $1,599"},
        {"Lenovo ThinkPad X1", "Profesional Intel i7, 16GB, $1,499"},
        {"Dell XPS 13", "Diseño OLED, Intel/AMD, $1,599"}
    },
    {
        {"Portabilidad", 8},
        {"Potencia", 7},
        {"Precio", 6},
        {"Durabilidad", 8},
        {"Ecosistema", 7}
    }
);
```

### Output (Ejemplo)

```
✅ Análisis completado en 287 segundos

🎯 RECOMENDACIÓN PRINCIPAL:
   Lenovo ThinkPad X1 con 75% probabilidad (mejor relación precio-features)

📊 ANÁLISIS DETALLADO:

1. MATRIZ DE DECISIÓN
   
   Portabilidad (8/10):
   - MacBook Air M2: 9/10 (excelente, 1.24 kg)
   - Lenovo ThinkPad: 7/10 (buena, 1.38 kg)
   - Dell XPS 13: 9/10 (excelente, 1.20 kg)
   
   Potencia (7/10):
   - MacBook Air M2: 8/10 (M2 es muy capaz)
   - Lenovo ThinkPad: 9/10 (Intel i7-12 es superior)
   - Dell XPS 13: 8/10 (Intel i7-13 comparable)
   
   [... resto de criterios ...]

2. ANÁLISIS COMPARATIVO
   
   ✅ Fortalezas MacBook Air M2:
      - Mejor portabilidad relativa
      - Ecosistema cerrado = menos virus
      - Batería excepcional (15 horas real)
   
   ⚠️ Debilidades:
      - Menor potencia computacional
      - RAM no upgradeable
      - Precio más alto
   
   [... análisis de otras opciones ...]

3. EVALUACIÓN DE RIESGO
   
   MacBook Air M2:
   - Riesgo obsolescencia: 30% (ARM custom, cambios rápidos)
   - Riego dependencia Apple: 20% (costly repairs)
   - Riesgo general: MODERADO
   
   Lenovo ThinkPad X1:
   - Riesgo de driver issues: 15% (enterprise, soporte bueno)
   - Riesgo repuestos: 10% (mercado grande)
   - Riego general: BAJO
   
   Dell XPS 13:
   - Riesgo térmica: 25% (diseño compacto)
   - Riesgo pantalla OLED: 20% (burn-in posible)
   - Riego general: MODERADO-ALTO

4. RECOMENDACIÓN FINAL
   
   GANADOR: Lenovo ThinkPad X1 (75% confianza)
   
   Justificación:
   - Mejor relación precio/potencia
   - Menor riesgo técnico
   - Reparaciones más económicas
   - Mercado de repuestos amplio
   
   CUANDO CAMBIAR:
   - Si trabajas > 8h/día en movimiento → MacBook Air M2
   - Si necesitas pantalla ultraportátil → Dell XPS 13
   - Si presupuesto < $1,200 → Buscar alternativa
   
   PRÓXIMOS PASOS:
   1. Validar en tienda (touch, teclado)
   2. Revisar garantía (ThinkPlus vs AppleCare)
   3. Comprar en Black Friday (ahorro 15-20%)
```

---

## 🔧 Troubleshooting

### Error: `ImportError: cannot import name 'genai'`

**Problema:** SDK incorrecto instalado

**Solución:**
```bash
# Desinstalar sdk antiguo
pip uninstall google-generativeai

# Instalar correcto
pip install google-genai
```

### Error: `Timeout waiting for analysis`

**Problema:** Deep Research Pro tardó > 10 minutos

**Solución:**
```cpp
// Aumentar timeout
analyzer.setTimeoutSeconds(1200);  // 20 minutos
```

### Error: `No API key found`

**Problema:** GOOGLE_API_KEY no configurada

**Solución:**
```bash
export GOOGLE_API_KEY="tu_key_aqui"
# O en código:
export GOOGLE_API_KEY="AIzaSyDIuo2lfInFZKeDAKApypziugGX8ieTRnw"
```

### Estado: `in_progress` por mucho tiempo

**Problema:** Deep Research Pro está investigando (normal)

**Solución:**
- Esperar 3-5 minutos (es normal)
- No interrumpir
- Ver progreso con `interaction.status`

---

## 📚 Referencias

### Google AI Docs
- [Deep Research API](https://ai.google.dev/docs/deep-research)
- [Interactions API](https://ai.google.dev/docs/interactions)
- [google-genai SDK](https://github.com/googleapis/python-genai)

### Decision Framework
- Análisis de decisiones: [`README_UNIFIED_FRAMEWORK.md`](../README_UNIFIED_FRAMEWORK.md)
- Metodologías: [`docs/METODOLOGIAS_ALTERNATIVAS.md`](../docs/METODOLOGIAS_ALTERNATIVAS.md)

### Ejemplos
- Decisión simple: [`examples/unified_example.cpp`](../examples/unified_example.cpp)
- Decisión completa: [`examples/deep_research_decision_example.cpp`](../examples/deep_research_decision_example.cpp)
- Python: [`scripts/deep_research_analyzer.py`](../scripts/deep_research_analyzer.py)

---

## 🎓 Mejores Prácticas

### 1. Validar Resultados

```cpp
// No aceptes AI como verdad absoluta
auto result = analyzer.analyzeDecisionDeep(...);

// Verifica contra:
// - Tu intuición
// - Datos históricos
// - Segunda opinión
```

### 2. Usar Combinación de Métodos

```cpp
// Framework + AI = mejor decisión

// Paso 1: Framework (rápido, determinístico)
auto mc_result = engine.run();

// Paso 2: AI (profundo, contextual)
auto ai_result = analyzer.analyzeDecisionDeep(...);

// Paso 3: Combinar conclusiones
```

### 3. Documentar Decisión

```cpp
// Guardar análisis para referencia futura
std::ofstream log("decision_log.txt");
log << "Decisión: " << decision_name << "\n";
log << "Framework recomienda: " << mc_result.begin()->first << "\n";
log << "AI recomienda: " << ai_result.recommendation << "\n";
log << "Decisión final: " << your_choice << "\n";
```

---

## 🚀 Roadmap

### Ya Implementado ✅
- [x] Integración Deep Research Pro
- [x] Integración Gemini 2.5 Pro
- [x] AIAnalyzer (clase C++)
- [x] Python script (standalone)
- [x] Ejemplo completo (C++ + Python)

### Próximo 🔮
- [ ] Caché de resultados (evitar llamadas duplicadas)
- [ ] Integración REST API (servir resultados como API)
- [ ] Dashboard web (visualizar decisiones)
- [ ] Multi-idioma (español, inglés, portugués)
- [ ] Soporte para más modelos (Claude, Llama)

---

**Versión:** 1.0  
**Última actualización:** Diciembre 12, 2025  
**Autor:** Arturo + Google AI Team  
**SDK:** google-genai (≥ 0.5.0)
