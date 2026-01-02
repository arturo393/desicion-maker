# 📖 Índice de Documentación

Guía centralizada de toda la documentación del Decision Maker Framework.

---

## 🚀 Empezar Rápido

| Documento | Tiempo | Nivel | Descripción |
|-----------|--------|-------|------------|
| [QUICK_START.md](./QUICK_START.md) | 5 min | Principiante | 3 pasos para ejecutar el sistema |
| [CREAR_NUEVO_SCRIPT.md](./CREAR_NUEVO_SCRIPT.md) | 10 min | Intermedio | Crear tu primer análisis de decisión |
| [ARCHITECTURE.md](./ARCHITECTURE.md) | 15 min | Avanzado | Entender la estructura dual (Python+C++) |

---

## 🔧 Configuración

| Documento | Tema | Para |
|-----------|------|------|
| [GEMINI_FLASH_SETUP.md](./GEMINI_FLASH_SETUP.md) | Configurar API Gemini | Primero la primera vez |
| [UV_SETUP.md](./UV_SETUP.md) | Instalar UV (package manager) | Si prefieres velocidad |
| [INTEGRATION_SUMMARY.md](./INTEGRATION_SUMMARY.md) | Deep Research Pro | Análisis profundos (15-30 min) |

---

## 📊 Análisis Técnicos

| Documento | Contenido | Ref |
|-----------|----------|-----|
| `search_alternatives_comparison.md` | Comparación de motores búsqueda | Investigación |
| `DEEP_RESEARCH_INTEGRATION.md` | Integración Deep Research en C++ | Avanzado |

---

## 📋 Desarrollo

### Workflow Recomendado

1. **Leer**: [QUICK_START.md](./QUICK_START.md) (5 min)
2. **Ejecutar**: Script de ejemplo
3. **Aprender**: [ARCHITECTURE.md](./ARCHITECTURE.md) (15 min)
4. **Crear**: Tu análisis usando [CREAR_NUEVO_SCRIPT.md](./CREAR_NUEVO_SCRIPT.md)

### Para Contribuidores

- Mantener 13 metodologías sincronizadas (Python ↔ C++)
- Tests en `python/tests/` antes de commit
- Actualizar `CHANGELOG.md` con cambios

---

## 🐍 Python Framework

**Ubicación**: `../python/`

### Scripts Principales
- `core/deep_research_decision_agent.py` - Motor core (13 metodologías)
- `scripts/gemini_query.py` - Testing rápido de Gemini
- `scripts/mining_career_analyzer.py` - Ejemplo completo

### Setup
```bash
cd ../python
uv sync                    # Instalar deps
uv run python core/...     # Ejecutar
```

### Métodos Disponibles
- `DecisionAnalysisEngine.analyze_all_options()`
- `GeminiDeepResearchAgent.research_option()`
- 13 metodologías individuales (Monte Carlo, TOPSIS, Pareto, etc)

---

## ⚙️ C++ Framework

**Ubicación**: `../core/`

### Headers
- `src/framework/` - Base framework
- `src/methodologies/` - 13 algoritmos
- `src/distributions/` - 7 distribuciones probabilísticas

### Compilar
```bash
cd ../core
cmake -B build && cmake --build build
./build/examples/basic/sillon_decision
```

### Ejemplos Disponibles
- `examples/basic/` - Introducción
- `examples/business/` - Casos negocio
- `examples/advanced/` - Análisis complejos
- `examples/templates/` - Plantillas reutilizables

---

## 🔗 Quick Links

### Configuración Inicial
1. Clone el repo
2. Lee [GEMINI_FLASH_SETUP.md](./GEMINI_FLASH_SETUP.md)
3. Sigue [QUICK_START.md](./QUICK_START.md)

### Mi Primer Análisis
1. Copia template de [CREAR_NUEVO_SCRIPT.md](./CREAR_NUEVO_SCRIPT.md)
2. Define tus opciones (CareerOption dataclass)
3. Ejecuta análisis
4. Revisa matriz comparativa

### Análisis Profundo (Gemini Deep Research)
1. Asegúrate API key en `.env.gemini`
2. Sigue [INTEGRATION_SUMMARY.md](./INTEGRATION_SUMMARY.md)
3. Permite 15-30 min para análisis Deep Research Pro

### Optimización de Performance
1. Lee [ARCHITECTURE.md](./ARCHITECTURE.md) sección "Performance"
2. Considera usar C++ para 10K+ simulaciones
3. Benchmark: `python examples/benchmark.py`

---

## 🎯 Por Caso de Uso

### "Quiero analizar mi carrera profesional"
→ Sigue [CREAR_NUEVO_SCRIPT.md](./CREAR_NUEVO_SCRIPT.md), usa CareerOption

### "Tengo datos de mercado, necesito decisión en 30 seg"
→ Python + [QUICK_START.md](./QUICK_START.md) (sin Deep Research)

### "Necesito análisis profundo con 50+ fuentes"
→ [INTEGRATION_SUMMARY.md](./INTEGRATION_SUMMARY.md) + Gemini Deep Research

### "Voy a compilar 100K decisiones / simulaciones"
→ C++ Framework + [ARCHITECTURE.md](./ARCHITECTURE.md) sección C++

### "Quiero entender cómo funciona todo internamente"
→ [ARCHITECTURE.md](./ARCHITECTURE.md) completo + código fuente

---

## 📞 Troubleshooting

### "No me ejecuta Python"
→ [UV_SETUP.md](./UV_SETUP.md) paso 1-2

### "Error de Gemini API"
→ [GEMINI_FLASH_SETUP.md](./GEMINI_FLASH_SETUP.md) sección troubleshooting

### "¿Dónde pongo mi código?"
→ [CREAR_NUEVO_SCRIPT.md](./CREAR_NUEVO_SCRIPT.md)

### "¿Cómo compilar C++?"
→ [ARCHITECTURE.md](./ARCHITECTURE.md) sección C++ Framework

---

## 📊 Estadísticas del Framework

| Métrica | Valor |
|---------|-------|
| Metodologías implementadas | 13 |
| Líneas código Python | 732+ |
| Líneas código C++ | 3,971+ |
| Distribuciones estocásticas | 7 |
| Ejemplos incluidos | 24+ |
| Tiempo setup rápido | 5 min |
| Tiempo análisis simple | 30 seg |
| Tiempo análisis profundo | 15-30 min (con Gemini) |

---

## 🔄 Organización de Documentación

**Nota**: Toda la documentación está centralizada en este directorio (`docs/`).
Antes estaba dispersa en la raíz. El archivo [REORGANIZATION_PLAN.md](../REORGANIZATION_PLAN.md) en raíz documenta la migración.

---

## 📝 Notas de Mantenimiento

- Versión actual: 2.0.0
- Python: 3.9+
- C++: C++17
- Gemini: Flash (free tier)
- Package manager Python: UV 0.9.17

**Última actualización**: 2 Enero 2026

