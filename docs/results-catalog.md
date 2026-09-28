---
aliases: [Results Catalog, Catálogo de Resultados, Simulación Resultados]
tags: [results, simulations, reports, lumina, archive]
id: DB-RESULTS
title: "Catálogo de Resultados de Simulación y Análisis"
type: moc
category: analyses
status: active
related: ["[[database-hub]]", "[[decision-analyses]]", "[[unified-orchestrator]]", "[[reporting-and-registry]]"]
created: 2026-09-28
updated: 2026-09-28
---

# 📈 Catálogo de Resultados de Simulación y Análisis (`results/`)

Este documento indexa y categoriza los artefactos generados por las simulaciones cuantitativas del framework almacenados en el directorio `results/`. El sistema genera automáticamente reportes Markdown, dashboards interactivos HTML, registros JSON estructurados de estados y gráficos de auditoría visual para cada ejecución.

Hub general de base de datos: [[database-hub]] | Catálogo de decisiones aplicadas: [[decision-analyses]].

---

## 📂 1. Taxonomía de Artefactos de Salida

Cada ejecución del motor unificado (`UnifiedDecisionFramework.run_analysis()`) o de los scripts de análisis genera artefactos estandarizados identificados por marca temporal (`YYYYMMDD_HHMMSS`):

| Tipo de Artefacto | Patrón de Nombre | Formato | Propósito y Contenido |
|:---|:---|:---|:---|
| **Reporte Ejecutivo Markdown** | `report_*.md` | Markdown | Resumen ejecutivo, consenso algorítmico, tabla comparativa MC/TOPSIS y recomendaciones estratégicas. |
| **Reporte Interactivo Web** | `report_*.html` | HTML / CSS | Reporte auto-contenido con estilos visuales, gráficos integrados y tablas interactivas. |
| **Volcado de Simulación** | `analysis_*.json` | JSON | Diccionario completo de resultados: percentiles, intervalos de confianza, ranking MCDA y métricas de convergencia. |
| **Perfil de Riesgo** | `risk_profiles_*.png` | PNG (300 DPI) | Distribuciones de densidad acumulada, VaR (Value at Risk) y CVaR (Conditional VaR) por alternativa. |
| **Importancia de Factores** | `factor_importance_*.png` | PNG (300 DPI) | Diagrama de tornado de coeficientes de correlación y análisis de sensibilidad global. |
| **Auditoría de Robustez** | `robustness_audit_*.png` | PNG (300 DPI) | Gráficos de estabilidad de rango y dispersión ante perturbaciones en los pesos de los criterios. |

---

## 📦 2. Datasets Especializados y Trazas de Auditoría

Dentro de `results/` residen artefactos especializados utilizados en la validación de protocolos y refactorizaciones críticas:

| Archivo Fuente | Formato | Descripción Técnica | Módulo Relacionado |
|:---|:---|:---|:---|
| `results/reasoning_traces.jsonl` | JSON Lines | Trazas completas del flujo de razonamiento y meta-decisión automatizada ejecutadas por agentes cuantitativos. | [[tests-results/meta-decision-result]] |
| `results/exportador_nms_protocolo_v5.json` | JSON | Datos estructurados de simulación y evaluación de protocolos de exportación hacia software de monitoreo de red (NMS). | [[decision-analyses]] |
| `results/commandmessage_refactor_llm_20260823.json` | JSON | Registro de prompting y evaluación comparativa asistida por LLM para la reescritura del protocolo CommandMessage. | [[decision-analyses]] |
| `results/sophos_xg115_decision_20260810_135741.json` | JSON | Dataset de evaluación multicriterio estocástica para la decisión de reemplazo vs licenciamiento de hardware perimetral Sophos. | [[decision-analyses]] |

---

## 🗓️ 3. Lotes Históricos de Simulación

El repositorio registra 295 archivos en `results/`, organizados cronológicamente por lotes operativos:

### Lote 1: Inicialización y Caso Sophos (2026-08-10)
- **Foco:** Primera corrida formal de simulación estocástica aplicada al firewall perimetral de red industrial.
- **Artefactos Clave:** `sophos_xg115_decision_20260810_135741.json`.

### Lote 2: Simulaciones Intensivas y Calibración (2026-08-13 al 2026-08-20)
- **Foco:** Calibración de distribuciones Monte Carlo con $N \ge 10{,}000$ iteraciones, ajuste de algoritmos TOPSIS difuso y matrices de correlación de factores.
- **Artefactos Clave:** Reportes `report_20260813_*` a `report_20260820_*`, gráficos de perfiles de riesgo y auditorías de robustez.

### Lote 3: Infraestructura Minera, FSK y Refactorizaciones (2026-08-23 al 2026-08-28)
- **Foco:** Evaluación de protocolos FSK en leaky feeder Becker Varis, telemetría de sniffer y refactorización de CommandMessage.
- **Artefactos Clave:** Reportes `report_20260823_*` hasta `report_20260828_*`, dataset `commandmessage_refactor_llm_20260823.json`.

### Lote 4: Auditoría Cuantitativa v3.0 / v3.1 (2026-09-27)
- **Foco:** Verificación de consistencia matemática entre módulos, exportación de reportes estandarizados y validación de compuertas de decisión.
- **Artefactos Clave:** Lote `report_20260927_195727` a `report_20260927_215247`.

---

## 🔍 4. Integración y Acceso desde Obsidian

Para consultar los resultados desde Obsidian:
1. **Visualización de Reportes:** Los archivos Markdown en `results/` pueden previsualizarse o abrirse directamente con enlaces relativos `[Reporte](file:///.../results/report_XYZ.md)`.
2. **Visualización de Gráficos:** Cualquier gráfico generado en `results/` puede incrustarse en notas de decisión con la sintaxis `![[risk_profiles_YYYYMMDD_HHMMSS.png]]` configurando la ruta de adjuntos del vault.
3. **Registro Histórico SQLite:** Los metadatos de cada ejecución son indexados en la base de datos local gestionada por [[reporting-and-registry]].
