---
aliases: [Database Hub, Centro de Base de Datos, Database, Base de Datos]
tags: [database, moc, lumina, quant, archive]
id: DB-HUB
title: "Centro de Base de Datos y Catálogo Relacional"
type: moc
category: governance
status: active
related: ["[[decision-maker-moc]]", "[[index]]", "[[kanban]]", "[[roadmap]]", "[[note-schema]]"]
created: 2026-09-27
updated: 2026-09-27
---

# 🗄️ Centro de Base de Datos: Decision Maker Repository

Este documento centraliza la documentación del repositorio estructurada como una **Base de Datos Relacional para Obsidian**. Cada documento del sistema posee propiedades uniformes (`id`, `title`, `type`, `category`, `status`, `related`, `tags`) permitiendo su consulta mediante tablas relacionales estáticas y consultas dinámicas con el plugin **Dataview**.

Tablero Kanban asociado: [[kanban]] | Mapa de Contenido canónico: [[decision-maker-moc]].

---

## 🧮 1. Catálogo de Motores Cuantitativos (`type: module`)

| ID | Documento / Nota | Módulo Fuente (`src/`) | Eje Temático | Estado | Relaciones Clave |
|:---|:---|:---|:---|:---|:---|
| `MOD-MONTE-CARLO` | [[monte-carlo-engine]] | `core/monte_carlo.py` | `stochastic` | `stable` | [[bayesian-inference-engine]], [[antifragile-engine]], [[topsis]] |
| `MOD-BAYESIAN` | [[bayesian-inference-engine]] | `core/bayesian.py` | `stochastic` | `stable` | [[monte-carlo-engine]], [[unified-orchestrator]] |
| `MOD-ANTIFRAGILE` | [[antifragile-engine]] | `core/antifragile.py` | `portfolio` | `stable` | [[monte-carlo-engine]], [[portfolio-optimizer]] |
| `MOD-ERGODICITY` | [[ergodicity-analyzer]] | `core/ergodicity.py` | `stochastic` | `stable` | [[monte-carlo-engine]], [[decision-gates]] |
| `MOD-GATES` | [[decision-gates]] | `core/decision_gates.py` | `infrastructure` | `stable` | [[unified-orchestrator]], [[ergodicity-analyzer]] |
| `MOD-TOPSIS` | [[topsis]] | `core/topsis.py` | `mcda` | `stable` | [[monte-carlo-engine]], [[promethee]], [[ahp]] |
| `MOD-PROMETHEE` | [[promethee]] | `core/promethee.py` | `mcda` | `stable` | [[topsis]], [[ahp]], [[unified-orchestrator]] |
| `MOD-AHP` | [[ahp]] | `core/ahp.py` | `mcda` | `stable` | [[topsis]], [[promethee]], [[unified-orchestrator]] |
| `MOD-PARETO` | [[pareto-frontier]] | `core/pareto.py` | `optimization` | `stable` | [[unified-orchestrator]], [[topsis]] |
| `MOD-DECISION-THEORY` | [[decision-theory]] | `core/decision_theory.py` | `stochastic` | `stable` | [[unified-orchestrator]], [[monte-carlo-engine]] |
| `MOD-AGGREGATOR` | [[rank-aggregator]] | `core/aggregator.py` | `mcda` | `stable` | [[unified-orchestrator]], [[topsis]] |
| `MOD-ROBUST` | [[robust-optimization]] | `core/robust.py` | `optimization` | `stable` | [[unified-orchestrator]], [[sensitivity-analysis]] |
| `MOD-SENSITIVITY` | [[sensitivity-analysis]] | `core/sensitivity.py` | `stochastic` | `stable` | [[unified-orchestrator]], [[robust-optimization]] |
| `MOD-BOOTSTRAP` | [[bootstrap-ranking]] | `core/bootstrap.py` | `stochastic` | `stable` | [[unified-orchestrator]], [[monte-carlo-engine]] |
| `MOD-WHAT-IF` | [[what-if-engine]] | `core/what_if.py` | `stochastic` | `stable` | [[unified-orchestrator]], [[sensitivity-analysis]] |
| `MOD-PORTFOLIO` | [[portfolio-optimizer]] | `core/portfolio.py` | `optimization` | `stable` | [[antifragile-engine]], [[genetic-algorithms]] |
| `MOD-GENETIC` | [[genetic-algorithms]] | `core/genetic.py` | `optimization` | `stable` | [[portfolio-optimizer]], [[unified-orchestrator]] |
| `MOD-TOPOLOGY` | [[topological-data-analysis]] | `core/topology.py` | `topology` | `stable` | [[topsis]], [[reporting-and-registry]] |
| `MOD-ORCHESTRATOR` | [[unified-orchestrator]] | `core/orchestrator.py` | `infrastructure` | `stable` | [[data-models-and-schemas]], [[monte-carlo-engine]] |
| `MOD-SCHEMAS` | [[data-models-and-schemas]] | `core/schemas.py` | `infrastructure` | `stable` | [[unified-orchestrator]], [[reporting-and-registry]] |
| `MOD-REGISTRY` | [[reporting-and-registry]] | `core/registry.py` | `infrastructure` | `stable` | [[data-models-and-schemas]], [[topological-data-analysis]] |

---

## 🏛️ 2. Arquitectura, Gobernanza y Decisiones Técnicas

| ID | Documento / Nota | Tipo | Categoría | Estado | Propósito y Alcance |
|:---|:---|:---|:---|:---|:---|
| `DOC-INDEX` | [[index]] | `narrative` | `governance` | `stable` | Portal de bienvenida, mapa conceptual y vista general del repositorio |
| `DOC-ARCH` | [[architecture]] | `architecture` | `governance` | `stable` | Arquitectura interna, flujo de datos estocásticos y compuertas de decisión |
| `DOC-GUIDE` | [[guide]] | `guide` | `governance` | `stable` | Guía de modelado de decisiones paso a paso y configuración YAML |
| `ADR-001` | [[adr/001-use-rust-for-math-engine]] | `adr` | `architecture` | `active` | Justificación técnica del motor nativo en Rust y fallback a Python |
| `TOOL-DEV` | [[dev-tools]] | `meta` | `infrastructure` | `active` | Herramientas de automatización, linters AST y validación de calidad en `scripts/` |
| `DOC-SCHEMA` | [[note-schema]] | `meta` | `governance` | `stable` | Esquema canónico de notas, taxonomía de tags y reglas de idioma del vault |
| `MOC-CORE` | [[decision-maker-moc]] | `moc` | `governance` | `stable` | Mapa de Contenido estructurado para navegación estándar en Obsidian |

---

## 📋 3. Gestión de Proyecto, Tareas y Análisis Aplicados

| ID | Documento / Nota | Tipo | Categoría | Estado | Propósito y Alcance |
|:---|:---|:---|:---|:---|:---|
| `DB-ANALYSES` | [[decision-analyses]] | `moc` | `analyses` | `active` | Catálogo de decisiones reales modeladas en `src/decision_maker/analyses/` |
| `DB-RESULTS` | [[results-catalog]] | `moc` | `analyses` | `active` | Catálogo de reportes, trazas JSON y gráficos en `results/` |
| `DOC-LEGACY-HUB` | [[legacy-docs]] | `moc` | `legacy` | `archive` | Catálogo de documentación histórica en `archive/legacy/` |
| `KANBAN-REPO` | [[kanban]] | `kanban` | `project-management` | `active` | Tablero interactivo Kanban para Obsidian con backlog, tareas y estado actual |
| `WORKLOG-DM` | [[decision-maker-worklog]] | `worklog` | `project-management` | `active` | Bitácora detallada de trabajo realizado, refactorizaciones y auditorías |
| `DOC-ROADMAP` | [[roadmap]] | `roadmap` | `project-management` | `active` | Hito v3.0 completado y roadmap de funcionalidades planificadas v3.1+ |
| `DOC-CHANGELOG` | [[changelog]] | `changelog` | `project-management` | `active` | Historial de versiones y evolución arquitectónica del framework |

---

## 📡 4. Dominio de Aplicación: Diagnóstico Remoto (`sw-diagnosticoremoto`)

| ID | Documento / Nota | Categoría | Estado | Descripción |
|:---|:---|:---|:---|:---|
| `SW-README` | [[sw-diagnosticoremoto/README]] | `remote-diagnostics` | `active` | Portal del subproyecto de diagnóstico remoto industrial |
| `SW-MINA` | [[sw-diagnosticoremoto/monitoreo-mina/propuesta-arquitectura]] | `remote-diagnostics` | `archive` | Propuesta de arquitectura para monitoreo de fuentes y leaky feeder en mina |
| `SW-VISTAS` | [[sw-diagnosticoremoto/05-power-supply/investigacion/analisis-vistas]] | `remote-diagnostics` | `archive` | Análisis de pantallas y vistas de monitoreo para fuentes de poder |
| `SW-ARTE` | [[sw-diagnosticoremoto/05-power-supply/investigacion/estado-del-arte]] | `remote-diagnostics` | `archive` | Estado del arte en monitoreo de sistemas críticos de alimentación |
| `SW-PLAN` | [[sw-diagnosticoremoto/05-power-supply/investigacion/planificacion-desarrollo]] | `remote-diagnostics` | `archive` | Planificación de desarrollo del módulo de diagnóstico |
| `SW-TECNICAS` | [[sw-diagnosticoremoto/05-power-supply/investigacion/recomendaciones-tecnicas]] | `remote-diagnostics` | `archive` | Recomendaciones técnicas de ingeniería para la fuente de poder |

---

## 📦 5. Archivo Histórico de Sesiones y Reorganización (`archive`)

| ID | Documento / Nota | Eje | Descripción |
|:---|:---|:---|:---|
| `ARCH-REORG-README` | [[reorganization/README]] | `reorganization` | Portal del proceso de reorganización histórica |
| `ARCH-REORG-PLAN` | [[reorganization/plan]] | `reorganization` | Plan de migración y estructura original |
| `ARCH-REORG-ANALYSIS` | [[reorganization/analysis]] | `reorganization` | Análisis comparativo y diagnóstico estructural previo |
| `ARCH-REORG-SUMMARY` | [[reorganization/summary]] | `reorganization` | Resumen ejecutivo del ordenamiento de scripts |
| `ARCH-REORG-DELIV` | [[reorganization/deliverables]] | `reorganization` | Entregables y estado de artefactos |
| `ARCH-REORG-IMPROV` | [[reorganization/improvement-analysis]] | `reorganization` | Análisis de oportunidades de mejora |
| `ARCH-REORG-PIP` | [[reorganization/personal-improvement-plan]] | `reorganization` | Plan individual de optimización y métricas |
| `ARCH-REORG-COMPLETE` | [[reorganization/complete]] | `reorganization` | Cierre del proceso de reestructuración |
| `ARCH-SESS-SUMMARY` | [[session-logs/reorganization-summary]] | `session-logs` | Minuta de la sesión de reorganización |
| `ARCH-SESS-TESTS` | [[session-logs/test-results]] | `session-logs` | Registro histórico de ejecución de pruebas |
| `ARCH-SESS-VERIF` | [[session-logs/verification-report]] | `session-logs` | Reporte de verificación y análisis de consistencia |
| `ARCH-META-RESULT` | [[tests-results/meta-decision-result]] | `tests-results` | Resultados de meta-decisión automatizada |

---

## 🗂️ 6. Documentación Externa al Vault (Raíz, Paquete y Legacy)

Documentos que residen fuera de `docs/` indexados para acceso directo:

| ID | Documento | Ubicación | Tipo | Descripción |
|:---|:---|:---|:---|:---|
| `ROOT-README` | [README.md](../README.md) | Raíz | `narrative` | Portada principal del framework en GitHub |
| `ROOT-ROADMAP` | [ROADMAP_v3.0.md](../ROADMAP_v3.0.md) | Raíz | `roadmap` | Hoja de ruta completa v3.0 y v3.1+ |
| `ROOT-CHANGELOG` | [CHANGELOG.md](../CHANGELOG.md) | Raíz | `changelog` | Historial completo de versiones |
| `GOV-AGENTS` | [AGENTS.md](../AGENTS.md) | Raíz | `governance` | Guía de agentes de IA y mapa del dominio Lumina |
| `CASE-POWER-SUPPLY` | [README_POWER_SUPPLY_DECISION.md](../README_POWER_SUPPLY_DECISION.md) | Raíz | `analysis` | Análisis formal de decisión para fuente de poder |
| `JIRA-ID-1846` | [DM-25.md](../jira/DM-25.md) | `jira/` | `task` | Tracking ejecutivo de refactorización cuantitativa |
| `DOC-PKG-README` | [README.md](../src/decision_maker/README.md) | `src/decision_maker/` | `narrative` | Documentación técnica del paquete Python |
| `COMP-DASHBOARD` | [README.md](../dashboard/README.md) | `dashboard/` | `narrative` | Frontend web Vite + React |
| `ARCH-MINING-GUIDE` | [MINING_CAREER_GUIDE.md](../archive/legacy/MINING_CAREER_GUIDE.md) | `archive/legacy/` | `legacy` | Guía de carrera en minería con 13 métodos |
| `ARCH-ENHANCED-COMP` | [ENHANCED_COMPARISON.md](../archive/legacy/ENHANCED_COMPARISON.md) | `archive/legacy/` | `legacy` | Comparativa estocástica de negocios (10 factores) |
| `ARCH-UNIFIED-FRAMEWORK` | [README_UNIFIED_FRAMEWORK.md](../archive/legacy/README_UNIFIED_FRAMEWORK.md) | `archive/legacy/` | `legacy` | Especificación de arquitectura unificada previa |
| `ARCH-SUPER-POWERED` | [README_SUPER_POWERED.md](../archive/legacy/README_SUPER_POWERED.md) | `archive/legacy/` | `legacy` | Algoritmos multicriterio avanzados (AHP/TOPSIS/PROMETHEE) |
| `ARCH-SYSTEM-COMPLETION` | [SYSTEM_COMPLETION_SUMMARY.md](../archive/legacy/SYSTEM_COMPLETION_SUMMARY.md) | `archive/legacy/` | `legacy` | Métricas de completitud y auditoría |
| `ARCH-INTEG-SYSTEM` | [INTEGRATED_SYSTEM_README.md](../archive/legacy/INTEGRATED_SYSTEM_README.md) | `archive/legacy/` | `legacy` | Arquitectura de sistema integrado estocástico |
| `ARCH-INTEG-SUMMARY` | [INTEGRATION_SUMMARY.md](../archive/legacy/INTEGRATION_SUMMARY.md) | `archive/legacy/` | `legacy` | Resumen de primera fase de integración de motores |
| `ARCH-LEGACY-INDEX` | [INDEX.md](../archive/legacy/INDEX.md) | `archive/legacy/` | `legacy` | Índice temático histórico del repositorio |
| `ARCH-LEGACY-OLD` | [README_OLD.md](../archive/legacy/README_OLD.md) | `archive/legacy/` | `legacy` | Portada original previa a v3.0 |
| `ARCH-LEGACY-BACKUP` | [README.backup.md](../archive/legacy/README.backup.md) | `archive/legacy/` | `legacy` | Respaldo anterior a la modularización |
| `ARCH-STOCHASTIC-ARCH` | [README.md](../archive/stochastic-decision-architect/README.md) | `archive/stochastic-decision-architect/` | `legacy` | Prototipo web React + TypeScript con Gemini |
| `DB-MIGRATIONS` | [README.md](../alembic/README.md) | `alembic/` | `meta` | Historial de versiones y migraciones de esquema con Alembic |

---

## ⚡ 7. Consultas Dinámicas para Obsidian Dataview

Si el plugin **Dataview** está activo en Obsidian, las siguientes consultas generan vistas automáticas en tiempo real:

### Todos los Motores Cuantitativos Activos
```dataview
TABLE id, category, status, module, related
FROM ""
WHERE type = "module"
SORT id ASC
```

### Registros de Gobernanza y Arquitectura
```dataview
TABLE id, type, category, status
FROM ""
WHERE type = "architecture" OR type = "adr" OR type = "narrative" OR type = "meta"
SORT id ASC
```

### Documentos del Repositorio con Tareas Pendientes
```dataview
TABLE id, type, status, updated
FROM ""
WHERE type = "kanban" OR type = "worklog" OR type = "roadmap"
SORT updated DESC
```
