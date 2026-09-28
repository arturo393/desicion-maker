---
aliases: [Kanban, Tablero Kanban, Project Kanban]
tags: [kanban, lumina, quant, project-management, archive]
kanban-plugin: basic
id: KANBAN-REPO
title: "Tablero Kanban de Decision Maker"
type: kanban
category: project-management
status: active
related: ["[[decision-maker-moc]]", "[[decision-maker-worklog]]", "[[index]]", "[[roadmap]]"]
created: 2026-09-27
updated: 2026-09-28
---

# 📋 Tablero Kanban: Decision Maker Framework

Tablero interactivo de seguimiento de tareas, hitos y desarrollo del framework cuantitativo. Compatible con el plugin **Obsidian Kanban** y estructurado como registro relacional de base de datos.

## 📋 Backlog (Hojas de Ruta / v3.1+)

- [ ] 🤖 **AI-Powered Parameter Estimation**: `add_variable("Price", DistributionType.AI_FETCH)` con integración Gemini para inferencia empírica #enhancement #p2
- [ ] ⚖️ **Interactive AHP CLI Wizard**: asistente interactivo en terminal para matrices de comparación por pares con [[ahp]] #cli #p2
- [ ] 📉 **Funciones de Utilidad Dinámica**: soporte para rendimientos decrecientes y curvas sigmoidales en [[data-models-and-schemas]] #quant #p3
- [ ] 📊 **Suite Interactiva de Visualización**: migración de gráficos estáticos a Plotly interactivo en [[reporting-and-registry]] #viz #p2
- [ ] 🐳 **Despliegue con Docker**: contenedorización para API FastAPI y dashboard Streamlit con `docker-compose` #infra #p2

## 📌 Por Hacer / En Cola (To Do)

- [ ] 📝 **Documentar módulos auxiliares restantes**: crear notas para submódulos de soporte secundario en `src/decision_maker/core/` (como `config_runner.py`, `jsonl_store.py`) #docs #p3
- [ ] 🦀 **Limpieza en Cargo.toml**: auditar dependencia `ndarray` en `rust_core/Cargo.toml` respecto a [[adr/001-use-rust-for-math-engine]] #rust #p3
- [ ] 🗺️ **Sincronización mkdocs.yml**: alinear navegación del generador estático con la estructura unificada de `docs/` #docs #p3
- [ ] 🧪 **Correr los checkers documentales en el harness**: hoy `scripts/check_docs_*.py` y `scripts/check_obsidian_*.py` se ejecutan sólo en CI, así que un test que confirme que sus nombres aparecen en la salida del pipeline no existe #qa #p2
- [ ] 🧹 **Deuda de `ruff` preexistente**: `ruff check src/decision_maker` reporta 111 hallazgos en archivos de test ajenos a la documentación; hoy impiden afirmar que CI está verde #qa #p3
- [ ] 🔗 **Resolver los 13 enlaces rotos preexistentes**: apuntan a un árbol de documentación propuesto que nunca se ejecutó, y están documentados por target exacto en `KNOWN_BROKEN` para que no se confundan con roturas nuevas #docs #p3

## 🚧 En Curso (In Progress)

- [ ] 🤖 **Preparación de v3.1**: prototipado de inferencia empírica automatizada #quant #p2

## 🔍 En Revisión & QA (Review)

Sin tarjetas.

## ✅ Completado (Done)

- [x] 🗄️ **Formateo de Documentación como Base de Datos**: propiedades YAML enriquecidas (`id`, `type`, `category`, `status`, `related`) para Dataview y Obsidian #database
- [x] 📊 **Creación de Centro de Base de Datos**: [[database-hub]] con consultas Dataview y tablas Markdown para navegación relacional #database
- [x] 📈 **Catálogo Exhaustivo de Resultados**: [[results-catalog]] indexando los 295 artefactos en `results/` (reportes, JSON y visualizaciones) #database
- [x] 🔬 **Catálogo Completo de Análisis y Scripts**: [[decision-analyses]] integrando 36 análisis operativos, 7 scripts utilitarios y 3 ejemplos #database
- [x] 📦 **Auditoría e Indexación de Documentación Legacy y Raíz**: [[legacy-docs]] con los 10 documentos históricos de `archive/legacy/` y archivos raíz #database
- [x] 🔗 **Interconexión Total del Grafo**: enlazado bidireccional entre módulos cuantitativos, guías, arquitectura, roadmap y resultados #graph
- [x] 🔬 **Auditoría granular de fidelidad por sección**: la resolución de clases pasó a ser por sección y no por unión de la nota, con un caso de dos módulos como prueba; único dueño por módulo verificado en tres canales (heading, frontmatter y registro) #qa
- [x] 🚧 **Conflicto de proprietarios resuelto**: `robust.py` y `bootstrap.py` tenían dos notas dueñas cada uno con contenido incompatible; se movió el contenido verificado al dueño que designa el registro y el otro quedó como puntero #docs
- [x] 🗑️ **Un solo vault, sin `.obsidian` en la raíz**: había dos copias byte-idénticas de 1.1 MB, y la de la raíz convertía todo el repositorio en vault al abrirlo; se borró con respaldo y se añadió a `.gitignore` #vault
- [x] 📜 **Schema reescrito desde medición**: la tabla de campos, los cuatro ejes de tags y las cifras reales del vault, con ratchet que ata prosa, tabla y notas en las tres direcciones #docs
- [x] 🧬 **Regla de corrupción de alfabeto**: detecta cirílico o chino pegados dentro de una palabra, con dos controles negativos que además exigen **no** marcar `σ` ni `Σ`, que son notación legítima #qa
- [x] 🧪 **Suite de pruebas documentales**: 23 tests nuevos que hacen falla la fidelidad y el schema, en lugar de depender de que alguien ejecute los scripts a mano #qa
- [x] 🔗 **Validación de Enlaces de Grafo**: 559 enlaces verificados, 546 resueltos y 13 rotos documentados, sin ninguno nuevo, mediante `scripts/check_docs_links.py` #qa
- [x] 🌐 **Validación de Consistencia Lingüística**: 0 intrusos léxicos y 0 alfabetos foreignos pegados, verificado mediante `scripts/check_obsidian_language.py` #qa
- [x] 🎯 **Validación de Fidelidad de Código**: 54 notas, 25 módulos, 45 clases, 25 imports, 25 propietarios y 189 literales de módulo verificadas con AST mediante `scripts/check_obsidian_fidelity.py` #qa
- [x] ⚡ **Suite de Pruebas Unitarias**: validación de 519 tests pasando con `uv run pytest` #qa
- [x] 🏗️ **Unificación del Vault**: raíz de Obsidian consolidada en `docs/`, con la configuración del vault bajo control de versiones y el plugin `obsidian-kanban` #vault
- [x] 🏷️ **Normalización de Nombres**: convención uniforme `lowercase-with-hyphens` y 100% de aliases resueltos #naming
- [x] 🚀 **24 Motores Cuantitativos**: implementación de Monte Carlo, Fuzzy TOPSIS, PROMETHEE, Barbell/Antifragile, Bayesian, etc. #core
- [x] 📝 **Documentar Motores Clave del Pipeline**: fichas creadas para [[pareto-frontier]], [[decision-theory]], [[sensitivity-analysis]], [[robust-optimization]], [[bootstrap-ranking]], [[rank-aggregator]], [[ergodicity-analyzer]], [[decision-gates]], [[what-if-engine]] #docs
- [x] 🔌 **Interfaces de Usuario**: API REST FastAPI (`api/server.py`) y Dashboard interactivo Streamlit (`dashboard/app.py`) #api
- [x] 🦀 **Extensión Nativa Rust**: desarrollo de `rust_core` y documentación de arquitectura en [[adr/001-use-rust-for-math-engine]] #rust
- [x] 🛡️ **Compuertas de Decisión y Veto**: implementación de compuertas de ergodicidad, riesgo de ruina y DAG causal #core

%% kanban:settings
```json
{
  "kanban-plugin": "basic",
  "tag-sort": []
}
```
%%
