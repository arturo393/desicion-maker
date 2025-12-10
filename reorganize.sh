#!/bin/bash

# Crear estructura de carpetas
mkdir -p mineria-2026/{planning,templates,cv,references}
mkdir -p carrera-analisis/{evaluaciones,comparativas}
mkdir -p decisiones/{sillon,computador,framework}
mkdir -p negocios/{defi-monitor,emprendimiento}
mkdir -p docs-legacy/{versiones,indices,deprecated}

# CARPETA 1: MINERIA-2026 (PLAN ACTIVO)
echo "🔄 Moviendo documentos MINERÍA-2026..."
mv PLAN_MINERIA_MARZO_2026.md mineria-2026/planning/
mv GANTT_MINERIA_VISUAL.md mineria-2026/planning/
mv PRIMEROS_PASOS_HOY.md mineria-2026/planning/
mv VISUALIZACION_PLAN_MINERIA.md mineria-2026/planning/
mv RESUMEN_FINAL_2MIN.md mineria-2026/planning/
mv READ_ME_FIRST.md mineria-2026/
mv QUICK_REFERENCE_APLICACIONES.md mineria-2026/references/
mv CV_INTERNACIONAL_MINERIA_2025.md mineria-2026/cv/
mv ONE_PAGER_PLAN_MINERIA.md mineria-2026/planning/
mv INDICE_DOCUMENTOS.md mineria-2026/

# CARPETA 2: CARRERA-ANALISIS
echo "🔄 Moviendo documentos CARRERA-ANALISIS..."
mv CARRERA_ARTURO_DIC2025.md carrera-analisis/evaluaciones/
mv CARRERA_ARTURO_V2_REALISTA.md carrera-analisis/evaluaciones/
mv VALOR_MERCADO_ARTURO_2025.md carrera-analisis/evaluaciones/
mv TRABAJO_EXTRANJERO_ANALISIS.md carrera-analisis/evaluaciones/

# CARPETA 3: DECISIONES
echo "🔄 Moviendo documentos DECISIONES..."
# Sillón
mv SILLON_ANALYSIS.md decisiones/sillon/
mv SILLON_README.md decisiones/sillon/
mv SILLON_INDEX.md decisiones/sillon/
mv DECISION_SILLON_RESUMEN.txt decisiones/sillon/

# Computador
mv COMPUTADOR_ANALISIS_REVISADO_32GB.md decisiones/computador/
mv COMPUTADOR_REEVALUACION_32GB.md decisiones/computador/
mv COMPUTADOR_RESUMEN_EJECUTIVO.md decisiones/computador/
mv EVALUACION_COMPUTADOR.md decisiones/computador/
mv COMPARATIVA_SILLON_VS_COMPUTADOR.md decisiones/

# Framework general
mv DECISION_NEGOCIO_AUTOMATIZADO.md decisiones/framework/
mv DECISION_VISUAL_FINAL_V4.md decisiones/framework/
mv ANALISIS_DECISION_ARTURO.md decisiones/framework/
mv ANALISIS_FINANCIERO_EXHAUSTIVO.md decisiones/framework/

# CARPETA 4: NEGOCIOS
echo "🔄 Moviendo documentos NEGOCIOS..."
mv REEVALUACION_DEFI_MONITOR_DIC2025.md negocios/defi-monitor/
mv GUI_COMPARISON.md negocios/
mv WHY_JAVASCRIPT.md negocios/

# CARPETA 5: DOCS-LEGACY (Versiones, índices antiguos, documentos deprecated)
echo "🔄 Moviendo documentos LEGACY..."
# Índices antiguos
mv INDICE_DOCUMENTACION_COMPLETA.md docs-legacy/indices/
mv INDICE_MAESTRO_SILLON.md docs-legacy/indices/
mv INDICE_MAESTRO_V4_COMPLETO.md docs-legacy/indices/
mv INDICE_DECISIONES.md docs-legacy/indices/

# Versiones y estados
mv STATUS_FINAL_PROYECTO.md docs-legacy/versiones/
mv STATUS_FINAL_V4.md docs-legacy/versiones/
mv PROYECTO_COMPLETADO_RESUMEN_FINAL.md docs-legacy/versiones/
mv FINAL_SUMMARY.md docs-legacy/versiones/
mv FINAL_SUMMARY.txt docs-legacy/versiones/
mv RESUMEN_FINAL.md docs-legacy/versiones/
mv RESUMEN_INTEGRADO_FINAL.md docs-legacy/versiones/
mv RESUMEN_EJECUTIVO_FINAL.md docs-legacy/versiones/
mv RESUMEN_EJECUTIVO_V4_FINAL.md docs-legacy/versiones/

# Documentos consolidación/estructura
mv CONSOLIDACION_PLAN.md docs-legacy/deprecated/
mv ESTRUCTURA_CONSOLIDADA.md docs-legacy/deprecated/
mv EXTENSION_GUIDE.md docs-legacy/deprecated/
mv FELICIDADES.md docs-legacy/deprecated/
mv ANALISIS_GEMINI_REAL.md docs-legacy/deprecated/
mv COMPARACION_V2_VS_V3_GEMINI.md docs-legacy/deprecated/
mv METODOLOGIA_VALIDACION_GEMINI.md docs-legacy/deprecated/
mv GUIA_INTEGRACION_V4.md docs-legacy/deprecated/
mv GUIA_RAPIDA_V4.md docs-legacy/deprecated/
mv INTEGRACION_COMPLETA.md docs-legacy/deprecated/
mv V4_IMPLEMENTACION_COMPLETADA.md docs-legacy/deprecated/
mv VALIDACION_V2_VS_V3_VS_V4.md docs-legacy/deprecated/
mv LEE_ESTO_PRIMERO.md docs-legacy/deprecated/

# Archivos antiguos de inicio rápido
mv QUICK_ACTION_PLAN.md docs-legacy/deprecated/
mv QUICK_START.md docs-legacy/deprecated/
mv QUICK_START_15_MINUTOS.md docs-legacy/deprecated/
mv START_HERE.txt docs-legacy/deprecated/
mv START_HERE_GEMINI.txt docs-legacy/deprecated/
mv INICIO_RAPIDO.txt docs-legacy/deprecated/

# Documentos de configuración/setup
mv GEMINI_SETUP.md docs-legacy/deprecated/
mv TUTORIAL_CPP.md docs-legacy/deprecated/
mv EXTENSION_GUIDE.md docs-legacy/deprecated/ 2>/dev/null || true
mv COMIC_V4.md docs-legacy/deprecated/
mv gui_options.md docs-legacy/deprecated/

# Documentos históricos
mv CHANGELOG.md docs-legacy/
mv VERSION_HISTORY.md docs-legacy/
mv MEJORAS_4_5_DOCUMENTACION.md docs-legacy/
mv MEJORAS_ALGORITMO_Y_TECNICAS.md docs-legacy/
mv FASE1_VALIDACION_INTERACTIVA.md docs-legacy/deprecated/
mv VISUALIZACION_COMPARATIVA.md docs-legacy/deprecated/
mv RESUMEN_FINAL_VISUAL.txt docs-legacy/deprecated/
mv DECISION_VISUAL_FINAL_V4.md docs-legacy/deprecated/ 2>/dev/null || true

echo "✅ Reorganización completada"
ls -la | grep -E "^d" | awk '{print $NF}' | grep -E "mineria|carrera|decisiones|negocios|docs-legacy"
