# 📋 Plan de Reorganización - Decision Maker Framework

**Estado**: Propuesta para ejecución  
**Fecha**: 2 Enero 2026  
**Objetivo**: Consolidar documentación duplicada y mejorar navegación del proyecto

---

## 📊 Análisis Actual de Problemas

### 1. **Documentación Duplicada en Raíz**

| Archivo | Tamaño | Contenido | Acción |
|---------|--------|----------|--------|
| `README.md` | 9.8 KB | **Principal** - Estructura dual framework, quick start | MANTENER |
| `README_NEW.md` | 0 KB | **VACÍO** | ELIMINAR |
| `QUICK_START.md` | 7.5 KB | 3 pasos básicos, rutas MacOS | CONSOLIDAR en README.md |
| `CREAR_NUEVO_SCRIPT.md` | 8.9 KB | Plantilla de scripts Python+C++ | MOVER a `docs/` |
| `INTEGRATION_SUMMARY.md` | 6.4 KB | Deep Research integration | MOVER a `docs/` |
| `CHANGELOG.md` | 8.1 KB | Historial de versiones | MOVER a `docs/` |

### 2. **Archivos .env Duplicados**

```
.env.example              ← Template genérico
.env.gemini              ← Archivo actual
.env.gemini.template     ← Duplicado innecesario
```

**Acción**: Consolidar en `.env.example`

### 3. **Scripts Sueltos en Raíz**

```
gemini_query.py                    ← Herramienta de testing
research_leaky_feeder_monitoring.py ← Análisis específico
```

**Acción**: Mover a `scripts/` (ya existe)

### 4. **Carpetas Dormidas/Inconsistentes**

```
examples/               ← Solo 1 archivo (diy_furniture_secondhand.py)
                        ← Debería tener más ejemplos generados
docs/                  ← 4 archivos (DEEP_RESEARCH, GEMINI, UV, search)
stochastic-decision-architect/ ← Proyecto legacy sin documentación
results/               ← Carpeta de resultados (dinámica)
build/                 ← Carpeta de compilación (dinámica)
```

---

## 🎯 Estructura Propuesta

```
desicion-maker/
│
├── 📖 DOCUMENTACIÓN EN RAÍZ (Esencial)
│   ├── README.md                 ← Principal (CONSOLIDADO)
│   ├── CHANGELOG.md              ← Versionado
│   ├── .gitignore
│   ├── .env.example              ← Único template ENV
│   ├── package.json (si aplica)
│   └── CMakeLists.txt
│
├── 📚 docs/                      ← TODA la documentación técnica
│   ├── QUICK_START.md            ← Migrado (rutas actualizadas a Unix)
│   ├── CREAR_NUEVO_SCRIPT.md     ← Migrado
│   ├── INTEGRATION_SUMMARY.md    ← Migrado
│   ├── DEEP_RESEARCH_INTEGRATION.md
│   ├── GEMINI_FLASH_SETUP.md
│   ├── UV_SETUP.md
│   ├── search_alternatives_comparison.md
│   └── ARCHITECTURE.md           ← Nuevo: Overview técnico
│
├── 🐍 python/                    ← Framework Python (AI-powered)
│   ├── core/
│   │   ├── deep_research_decision_agent.py    ← Core
│   │   └── __init__.py
│   ├── scripts/
│   │   ├── mining_career_analyzer.py
│   │   ├── gemini_query.py              ← MIGRADO
│   │   ├── research_leaky_feeder.py     ← MIGRADO
│   │   └── deep_research_analyzer.py
│   ├── tests/
│   ├── api/
│   ├── pyproject.toml
│   ├── requirements.txt
│   └── .env.gemini                 ← MIGRADO
│
├── ⚙️ core/                       ← Framework C++ (Performance)
│   ├── src/
│   │   ├── framework/
│   │   ├── methodologies/
│   │   ├── integrations/
│   │   ├── advanced/
│   │   ├── core/
│   │   ├── distributions/
│   │   ├── scenarios/
│   │   └── utils/
│   ├── examples/
│   │   ├── basic/
│   │   ├── business/
│   │   ├── personal/
│   │   ├── advanced/
│   │   ├── templates/
│   │   └── deep_research_decision_example.cpp
│   ├── tests/
│   ├── CMakeLists.txt
│   └── cmake/
│
├── 📋 examples/                   ← Ejemplos ejecutables (Python)
│   ├── diy_furniture_secondhand.py
│   ├── career_decision.py          ← Generado
│   ├── business_analysis.py        ← Generado
│   └── README.md                   ← Índice de ejemplos
│
├── 📊 results/                    ← Generado dinámicamente
│   └── .gitkeep
│
├── 🔧 scripts/                    ← Herramientas y utilidades
│   ├── setup.sh
│   ├── build.sh
│   └── validate.py
│
├── 📦 build/                      ← Generado por CMake (en .gitignore)
│
└── 🗂️ LEGACY (Opcional)
    ├── stochastic-decision-architect/
    └── README.md → "Ver archivos históricos en branch legacy-projects"
```

---

## 🔄 Plan de Migración Paso a Paso

### **Fase 1: Preparación y Backup**

```bash
# 1. Crear rama para reorganización
git checkout -b refactor/reorganize-structure

# 2. Crear backup de archivos críticos
cp README.md README.md.backup
cp QUICK_START.md QUICK_START.md.backup
```

### **Fase 2: Consolidar Documentación**

#### 2a. Actualizar README.md

```bash
# README.md debe incluir:
# - Descripción del framework (desde README actual)
# - Quick start básico (desde QUICK_START.md, rutas Unix)
# - Estructura clara del proyecto
# - Links a docs/ para documentación detallada
```

#### 2b. Mover archivos a docs/

```bash
# Archivos que se mueven (sin cambios):
mv QUICK_START.md docs/QUICK_START.md
mv CREAR_NUEVO_SCRIPT.md docs/
mv INTEGRATION_SUMMARY.md docs/
mv CHANGELOG.md docs/CHANGELOG.md

# Crear docs/ARCHITECTURE.md (nuevo - overview técnico)
# Incluir: Componentes, flujos, dependencias
```

#### 2c. Limpiar archivos .env

```bash
# Consolidar en único .env.example:
cat .env.example > .env.example.new
cat .env.gemini.template >> .env.example.new

# Eliminar duplicados:
rm .env.gemini.template
rm .env.example
mv .env.example.new .env.example

# Mantener solo:
# - .env.example (plantilla)
# - .env.gemini (actual, en .gitignore)
```

### **Fase 3: Organizar Scripts**

```bash
# Mover scripts a python/scripts/
mv gemini_query.py python/scripts/
mv research_leaky_feeder_monitoring.py python/scripts/research_leaky_feeder.py

# Actualizar imports en scripts si es necesario
# (cambiar from core. a from ..core.)
```

### **Fase 4: Limpiar y Validar**

```bash
# Eliminar archivos innecesarios:
rm README_NEW.md
rm -rf stochastic-decision-architect/  (O: crear branch legacy-projects)

# Crear .gitignore actualizado:
# - build/ (cmake)
# - __pycache__/
# - *.pyc
# - .env (no .env.example)
# - .venv/
# - .vscode/
```

### **Fase 5: Actualizar Referencias**

```bash
# 1. Actualizar paths en docs/QUICK_START.md
#    MacOS: /Users/arturo/... → relativo: ./python/scripts/
#    Windows: c:\Users\artur\... → relativo: .\python\scripts\

# 2. Actualizar paths en docs/CREAR_NUEVO_SCRIPT.md
#    Cambiar: cd python → cd ./python
#    Cambiar: cp core/... → cp ../python/core/...

# 3. Crear links en README.md
#    - [Quick Start](docs/QUICK_START.md)
#    - [Nueva Decisión](docs/CREAR_NUEVO_SCRIPT.md)
#    - [Arquitectura](docs/ARCHITECTURE.md)
```

### **Fase 6: Commit y Push**

```bash
git add -A
git commit -m "refactor: reorganizar estructura del proyecto

- Consolidar documentación duplicada en docs/
- Mover scripts a python/scripts/
- Limpiar archivos .env duplicados
- Actualizar referencias de paths (Unix/Windows)
- Crear docs/ARCHITECTURE.md

Estructura final:
✅ Raíz: Solo documentación esencial
✅ docs/: Toda documentación técnica
✅ python/: Scripts y core Python
✅ core/: Framework C++
✅ examples/: Ejemplos ejecutables
"

git push origin refactor/reorganize-structure
```

---

## ✅ Checklist de Validación

Después de cada fase:

- [ ] Fase 1: Rama creada, backups listos
- [ ] Fase 2: README consolidado, docs/ completo
- [ ] Fase 3: Scripts movidos con imports correctos
- [ ] Fase 4: Archivos innecesarios eliminados
- [ ] Fase 5: Todos los paths actualizados
- [ ] Fase 6: Commit message claro, push exitoso
- [ ] Final: `python/scripts/gemini_query.py` ejecuta correctamente
- [ ] Final: `docs/QUICK_START.md` tiene paths correctos
- [ ] Final: `examples/` tiene al menos 2-3 ejemplos

---

## 📈 Beneficios de Esta Reorganización

| Área | Antes | Después |
|------|-------|---------|
| **Documentación** | Fragmentada en raíz | Centralizada en docs/ |
| **Navegación** | 6 archivos .md en raíz | 1 README + links a docs/ |
| **Scripts** | Sueltos en raíz | Organizados en python/scripts/ |
| **Onboarding** | Confuso (¿por dónde empiezo?) | Claro (README → docs/QUICK_START) |
| **Mantenimiento** | Duplicado (.env x3) | Único .env.example |
| **Git History** | Archivos obsoletos visibles | Limpios, solo lo relevante |

---

## 🚀 Siguiente: Ejecución

Para comenzar la reorganización:

```bash
cd c:\Users\artur\development\desicion-maker
git checkout -b refactor/reorganize-structure
# ... ejecutar fases según plan ...
```

¿Procedo con la ejecución? 👉 [EJECUTAR PLAN](./REORGANIZATION_PLAN.md#ejecución)

