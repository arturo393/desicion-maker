---
aliases: [Database Hub, Centro de Base de Datos, Database, Base de Datos]
tags: [database, moc, lumina, quant, archive]
id: DB-HUB
title: "Centro de Base de Datos y Catálogo Relacional"
type: moc
category: governance
status: active
related: ["[[decision-maker-moc]]", "[[index]]", "[[Tablero]]", "[[roadmap]]", "[[note-schema]]"]
created: 2026-09-27
updated: 2026-09-27
---

# 🗄️ Centro de Base de Datos: Decision Maker Repository

Este documento centraliza la documentación del repositorio estructurada como una **Base de Datos Relacional para Obsidian**. Cada documento del sistema posee propiedades uniformes (`id`, `title`, `type`, `category`, `status`, `related`, `tags`) permitiendo su consulta mediante tablas relacionales estáticas y consultas dinámicas con el plugin **Dataview**.

Tablero Kanban asociado: [[Tablero]] | Mapa de Contenido canónico: [[decision-maker-moc]].

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
| `MOD-WEIGHT-ROBUSTNESS` | [[weight-robustness]] | `core/weight_robustness.py` | `mcda` | `stable` | [[monte-carlo-engine]], [[sensitivity-analysis]] |
| `MOD-DECISION-LEDGER` | [[decision-ledger]] | `core/decision_commitment.py` | `learning` | `stable` | [[unified-orchestrator]], [[guide]] |

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
| `DB-ANALYSES` | [[decision-analyses]] | `moc` | `analyses` | `active` | Catálogo de decisiones reales modeladas en `analyses/` |
| `DB-RESULTS` | [[results-catalog]] | `moc` | `analyses` | `active` | Catálogo de reportes, trazas JSON y gráficos en `results/` |
| `DOC-LEGACY-HUB` | [[legacy-docs]] | `moc` | `legacy` | `archive` | Qué documentación histórica se retiró y cómo recuperarla de git |
| `KANBAN-REPO` | [[Tablero]] | `kanban` | `project-management` | `active` | Tablero interactivo Kanban para Obsidian con backlog, tareas y estado actual |
| `WORKLOG-DM` | [[bitacora]] | `worklog` | `project-management` | `active` | Bitácora detallada de trabajo realizado, refactorizaciones y auditorías |
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

---

## 🗂️ 6. Documentación Externa al Vault (Raíz, Paquete y Legacy)

Documentos que residen fuera de `docs/` indexados para acceso directo:

| ID | Documento | Ubicación | Tipo | Descripción |
|:---|:---|:---|:---|:---|
| `ROOT-README` | [README.md](../README.md) | Raíz | `narrative` | Portada principal del framework en GitHub |
| `ROOT-CHANGELOG` | [CHANGELOG.md](../CHANGELOG.md) | Raíz | `changelog` | Historial completo de versiones |
| `GOV-AGENTS` | [AGENTS.md](../AGENTS.md) | Raíz | `governance` | Guía de agentes de IA y mapa del dominio Lumina |
| `CASE-POWER-SUPPLY` | [[sw-diagnosticoremoto/05-power-supply/analisis-decision]] | `docs/sw-diagnosticoremoto/05-power-supply/` | `analysis` | Análisis formal de decisión para fuente de poder |
| `DOC-PKG-README` | [README.md](../src/decision_maker/README.md) | `src/decision_maker/` | `narrative` | Documentación técnica del paquete Python |
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
