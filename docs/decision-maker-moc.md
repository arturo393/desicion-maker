---
aliases: [Decision Maker MOC, Motor Cuantitativo, Decision_Maker_MOC]
tags: [moc, lumina, quant, architecture]
id: MOC-CORE
title: "Lumina Decision Maker MOC"
type: moc
category: governance
status: stable
related: ["[[index]]", "[[database-hub]]", "[[kanban]]", "[[architecture]]", "[[guide]]", "[[results-catalog]]"]
created: 2026-08-10
updated: 2026-09-28
---

# 🧠 Lumina Decision Maker (MOC)

Este es el Mapa de Contenido (MOC) del motor cuantitativo de decisiones estocásticas.

Es el **índice principal de navegación** de este vault, conectado con el [[database-hub]] y el tablero [[kanban]].

## 📊 1. Motores Core (Generación y Simulación)

- [[monte-carlo-engine]]
- [[bayesian-inference-engine]]
- [[antifragile-engine]]
- [[ergodicity-analyzer]]
- [[decision-gates]]
- [[unified-orchestrator]]

## ⚖️ 2. Análisis Multicriterio (MCDA) y Decisión

- [[topsis]]
- [[promethee]]
- [[ahp]]
- [[pareto-frontier]]
- [[decision-theory]]
- [[rank-aggregator]]

## 🌐 3. Topología, Optimización y Escenarios

- [[topological-data-analysis]]
- [[portfolio-optimizer]]
- [[genetic-algorithms]]
- [[robust-optimization]]
- [[sensitivity-analysis]]
- [[bootstrap-ranking]]
- [[what-if-engine]]

## 🛠️ 4. Infraestructura, Almacenamiento y Análisis Aplicados

- [[reporting-and-registry]]
- [[data-models-and-schemas]]
- [[decision-analyses]] — catálogo de decisiones y casos reales
- [[results-catalog]] — catálogo de resultados, trazas de razonamiento y gráficos en results/

## 🗂️ 5. Gobernanza del Vault y Base de Datos

- [[database-hub]] — centro de base de datos relacional y consultas Dataview
- [[kanban]] — tablero Kanban oficial del repositorio
- [[dev-tools]] — herramientas de desarrollo, linters y scripts de QA
- [[legacy-docs]] — catálogo de documentación histórica y legacy
- [[roadmap]] — hoja de ruta de desarrollo cuantitativo
- [[changelog]] — registro histórico de versiones y cambios
- [[note-schema]] — esqueleto canónico, vocabulario de tags, regla de idioma
- [[decision-maker-worklog]] — bitácora y registro de tareas del trabajo en curso
- [[reorganization/README|Reorganización]] — archivo histórico de la reorganización de 2026
- [[sw-diagnosticoremoto/README|sw-diagnosticoremoto]] — diagnóstico remoto: fuente de poder y monitoreo mina

## 📚 6. Capa Narrativa

Este MOC indexa los módulos. La capa narrativa —que explica cómo se usa el framework, no
qué clase hay— se entra por acá y no por el archivo suelto:

- [[index]] — puerta de entrada y mapa del repositorio
- [[guide]] — cómo modelar y correr una decisión, paso a paso
- [[architecture]] — bloques constructivos, flujo de runtime, tabla de motores
- [[adr/001-use-rust-for-math-engine]] — por qué Rust, y qué se terminó integrando

## Principios Arquitectónicos

- Basado en los filtros de **Nassim Taleb** (Convexidad, Riesgo de Ruina).
- Inferencia basada en **E.T. Jaynes** (Actualización empírica).
- Testing rigoroso (XDD, PBT) siguiendo la **Dev-Agents Foundation**.

> Las tres referencias de arriba son *atribuciones*, no notas: son personas y una fundación externa a este vault, y no tienen ficha propia. Los nombres viven como tags (`taleb`, `jaynes`) en las notas que los usan — ver la regla de ejes en [[note-schema]]. Delatar una diferencia: `Dev-Agents Foundation` es un directorio **fuera del repositorio**, así que ningún wikilink podría resolverlo.

## Cobertura

El vault documenta de forma exhaustiva los motores clave del pipeline cuantitativo (`monte_carlo.py`, `bayesian.py`, `antifragile.py`, `ergodicity.py`, `decision_gates.py`, `topsis.py`, `promethee.py`, `ahp.py`, `pareto.py`, `decision_theory.py`, `aggregator.py`, `topology.py`, `portfolio.py`, `genetic.py`, `robust.py`, `sensitivity.py`, `bootstrap.py`, `what_if.py`, `schemas.py`, `registry.py`, `reporting.py`, `orchestrator.py`). Módulos auxiliares o de soporte interno se gestionan en [[decision-maker-worklog]] y [[kanban]].
