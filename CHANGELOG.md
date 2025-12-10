# CHANGELOG - desicion-maker

Todos los cambios notables en este proyecto serán documentados en este archivo.

---

## [2.0.0] - 2025-12-09 - REORGANIZACIÓN COMPLETA

### 🏗️ Reorganización Mayor

#### Cambios Estructurales
- **Reorganización completa del repositorio**: De 82 archivos en raíz a 5 carpetas temáticas
- **Nueva estructura**:
  - `mineria-2026/` - Plan ejecutivo activo (10 documentos)
  - `carrera-analisis/` - Evaluaciones alternativas (4 documentos)
  - `decisiones/` - Framework + casos de uso (9+ documentos)
  - `negocios/` - Opciones emprendimiento (3+ documentos)
  - `docs-legacy/` - Histórico y deprecated (40+ documentos)

#### Documentación Nueva
- **README.md** completamente reescrito con guía de navegación
- **INDEX.md** creado como índice maestro detallado
- Guías de lectura por tiempo disponible (2min, 5min, 15min, 30min+)
- Referencias cruzadas entre documentos

#### Navegación Mejorada
- Plan minería destacado y accesible inmediatamente
- Documentos históricos organizados pero no molestos
- Estructura escalable para nuevas decisiones
- Índices por caso de uso (ejecutar plan, aprender framework, revisar alternativas)

#### Beneficios
- ✅ 60+ documentos organizados lógicamente
- ✅ Navegación por carpetas temáticas
- ✅ Plan activo separado del histórico
- ✅ Reducción de caos en raíz (82 → 15 archivos)
- ✅ Estructura clara para colaboradores

---

## [1.5.0] - 2025-12-09 - PLAN MINERÍA CHILE 2026

### ✨ Agregado

#### Plan Ejecutivo Minería
- **PLAN_MINERIA_MARZO_2026.md** - Plan completo 12 semanas (586 líneas)
- **GANTT_MINERIA_VISUAL.md** - Timeline visual + checklist semanal (408 líneas)
- **PRIMEROS_PASOS_HOY.md** - Acciones HOY/MAÑANA específicas (391 líneas)
- **VISUALIZACION_PLAN_MINERIA.md** - Arquitectura + números + motivación (370 líneas)
- **RESUMEN_FINAL_2MIN.md** - Resumen ejecutivo (281 líneas)
- **ONE_PAGER_PLAN_MINERIA.md** - Referencia 1 página (212 líneas)
- **QUICK_REFERENCE_APLICACIONES.md** - Links directos + templates (278 líneas)
- **CV_INTERNACIONAL_MINERIA_2025.md** - CV adaptado minería (380+ líneas)
- **READ_ME_FIRST.md** - Guía navegación principal (301 líneas)
- **INDICE_DOCUMENTOS.md** - Mapa de documentos (255 líneas)

#### Características Plan
- Timeline realista: 12 semanas, 21 horas totales
- Probabilidad éxito: 70-80% si se ejecuta
- Meta: $4.5M+ en minería antes Marzo 2026
- 5 empresas target: Codelco, BHP, Anglo, Hexagon, Sandvik
- Templates: Mensajes recruiter, follow-up, negociación salarial
- Estrategia paso-a-paso: LinkedIn → CV → Aplicaciones → Entrevistas → Oferta

### 🎨 Refinamiento Tono
- Actualización tono profesional conversacional chileno
- Eliminación de frases genéricas AI ("PERFECT", "REAL", "EXACTLY")
- Lenguaje apropiado para LinkedIn (profesional sin groserías)
- 5 documentos principales refinados
- Commits: 28f53cb, 1a415f2

---

## [1.4.0] - 2025-12-07 - ANÁLISIS CARRERA

### 📊 Agregado

#### Evaluaciones Carrera
- **CARRERA_ARTURO_DIC2025.md** - Análisis inicial v1 (602 líneas)
- **CARRERA_ARTURO_V2_REALISTA.md** - Análisis realista v2 (510 líneas)
- **VALOR_MERCADO_ARTURO_2025.md** - Evaluación valor mercado (567 líneas)
- **TRABAJO_EXTRANJERO_ANALISIS.md** - Opciones internacionales (434 líneas)

#### Análisis Incluido
- Comparación: UQOMM vs Minería vs Internacional vs Emprendimiento
- Benchmark salarial Chile: $2.6M actual → $4-5M target
- Evaluación remoto: USA, Europa, Australia, Alemania
- Plan híbrido: Minería Chile + DeFi Monitor backup

---

## [1.3.0] - 2025-12-06 - FRAMEWORK DECISIONES V4

### ✅ Agregado

#### Framework Genérico
- **DECISION_NEGOCIO_AUTOMATIZADO.md** - Framework automático (450+ líneas)
- **ANALISIS_DECISION_ARTURO.md** - Aplicado a carrera (380+ líneas)
- **ANALISIS_FINANCIERO_EXHAUSTIVO.md** - Framework financiero (520+ líneas)

#### Casos de Uso
- **Sillón**: Análisis vender/reparar sillón (4 documentos)
- **Computador**: Análisis comprar PC 32GB (4 documentos)
- **COMPARATIVA_SILLON_VS_COMPUTADOR.md** - Comparación directa

#### Mejoras Algorítmicas
- Mejora #4: Machine Learning Demand Predictor
- Mejora #5: Value at Risk Analyzer
- Integración Monte Carlo + ML + Risk Analysis

---

## [1.2.0] - 2025-12-04 - ANÁLISIS NEGOCIOS

### 💼 Agregado

#### Evaluación DeFi Monitor
- **REEVALUACION_DEFI_MONITOR_DIC2025.md** - Análisis completo Phase 2
- Evaluación viabilidad: MVP vs Full Stack
- Estrategia freemium + Pro ($15/mes)
- Plan exit: Venta API a DeBank/Zapper

#### Evaluación Técnica
- **GUI_COMPARISON.md** - Comparativa frameworks GUI
- **WHY_JAVASCRIPT.md** - Evaluación tecnologías

---

## [1.1.0] - 2025-11-28 - DOCUMENTACIÓN INICIAL

### 📚 Agregado

#### Índices y Guías
- Múltiples índices maestros (INDICE_MAESTRO_V4, INDICE_DECISIONES, etc.)
- Guías rápidas (QUICK_START, QUICK_ACTION_PLAN)
- Resúmenes ejecutivos (STATUS_FINAL, RESUMEN_EJECUTIVO)
- Documentación V1-V4

#### Estructura Original
- 82 archivos en raíz (antes de reorganización)
- Documentación framework C++
- Ejemplos y casos de uso
- Tests y validaciones

---

## [1.0.0] - 2024-12-08 - FRAMEWORK BASE

### 🎯 Lanzamiento Inicial

#### Framework C++
- Framework Monte Carlo genérico
- Simulaciones 40,000+/segundo
- Arquitectura extensible (Strategy, Builder, Template Method)
- Header-only library
- Estadísticas completas (mean, P25, P50, P75, std dev)

#### Componentes
- `src/` - Código fuente framework
- `examples/` - Casos de uso
- `tests/` - Unit tests
- `cmake/` - Build system
- `docs/` - Documentación técnica

---

## Tipos de Cambios

- **Agregado**: Nuevas características
- **Cambiado**: Cambios en funcionalidad existente
- **Deprecated**: Características que serán removidas
- **Removido**: Características eliminadas
- **Corregido**: Bug fixes
- **Seguridad**: Vulnerabilidades

---

**Nota**: Este CHANGELOG fue creado durante la reorganización v2.0.0. 
Para historial anterior, ver `docs-legacy/CHANGELOG.md`
