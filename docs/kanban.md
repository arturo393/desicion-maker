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
- [x] 🦀 **Quitar `ndarray` de `rust_core/Cargo.toml`**: hecho. Se quitó la dependencia, el `Cargo.lock` la perdió (y con ella `num-complex`, `num-integer` y `rawpointer`), y los tres anuncios del stack que la nombraban. `cargo check` verificado con el Python del venv #rust #p3
- [x] 🗑️ **mkdocs retirado**: existía un `mkdocs.yml` en la raíz desde el commit `3279d14` (31-Jul-2026, la fase "God-Mode"), un template genérico que nunca se usó. Ningún session-log lo mencionaba, no estaba en CI ni instalado, y **nunca funcionó**: la línea 27 tenía un `:` sin comillas, así que `mkdocs build` abortaba en el YAML. Arreglado y medido, el veredicto fue retirarlo: no puede leer los 512 `[[wikilinks]]` del vault sin plugin, es ciego fuera de `docs_dir` (41 de sus warnings), su nav cubría 4 de 54 notas, y el repo ya es un vault de Obsidian con cuatro checkers encima. Se borraron `mkdocs.yml`, el extra `docs` de `pyproject.toml` y su ratchet. Si algún día hace falta sitio web, se genera desde el vault, no se mantiene un segundo árbol #docs #p3
- [x] 🧪 **Correr los checkers documentales en el harness**: antes sólo se ejecutaban en CI, así que una suite 100% verde no decía nada de si un checker funcionaba. Ahora `test_checkers_run.py` los corre como subprocesos y verifica su código de salida. Medido: 10 tests pasan, y con una sonda `sys.exit(3)` en `check_docs_links.py` el test falla nombrando el checker y su salida #qa #p2
- [x] 🧾 **Piso de Python alineado**: `AGENTS.md` decía Python 3.12+ y `pyproject.toml` exige `>=3.11`; canónico el declarado, porque es lo que la CI prueba en su celda más baja. `AGENTS.md` ahora dice 3.11+, y un test compara ambos #docs #p3
- [x] 🔗 **Enlaces rotos preexistentes**: eran 13 y quedaban etiquetados en bloque como "no existen en ningún lado". Al medir uno por uno, dos eran falsos: `./docs/architecture.md` y `./docs/index.md` desde `docs/reorganization/` tienen destino real un nivel arriba, así que se corregieron a `../`. Los 9 que quedan sí son del plan nunca ejecutado y ahora cada uno tiene la razón que le corresponde, con `./python/scripts/` separado del resto porque es un directorio inexistente y no un documento del árbol fantasma #docs #p3
- [x] 🔒 **Versionar `uv.lock` y alinear el install de CI con el local**: las 20 dependencias tenían cota inferior y ninguna superior, y local usaba `uv` contra CI `pip`, sin fuente de verdad común — los pins existían (623 KB) y el repo los descartaba. Resuelto: `uv.lock` versionado, el extra `dev` referencia a `test` en vez de copiar sus 6 líneas, y CI usa `uv sync --frozen --extra dev`, que falla si el lock no corresponde a `pyproject.toml`. Los 7 comandos de CI verificados en local #deps #p1
- [x] 🔢 **Hacer derivable el conteo de motores**: la premisa de esta card era falsa — decía que no existía registro en el código, y `AdaptiveRouter` ya particionaba los motores en tres niveles. Lo que sí era cierto es que las tres listas vivían escritas a mano, así que el número no derivaba de nada: el docstring decía 24, tres notas decían 24, y las rutas sumaban 19. Hoy las tres notas dicen 19 motores ruteables y el test lo lee de `ENGINE_UNIVERSE` en vez de comparar las tres entre sí. Ahora `ENGINE_UNIVERSE` y `ROUTES` son la fuente única, `_simple/_moderate/_advanced_engines()` leen de ahí y `all_engines()` devuelve el número. Ruteo verificado idéntico contra la versión previa, salida included. La tabla `### Engines` de `architecture.md` ya no se presenta como el conteo: faltaban tres motores ruteables en ella (GameTheory, ROA, MLSurrogate) y 18 de sus filas son módulos de análisis o presentación que el router nunca despacha. Siguen abiertos: `Genetic` está en el universo y en ninguna ruta recomendada, ni en `advanced`, cuyo propio texto dice "Full suite needed" — si es deliberado o un olvido es una decisión de producto, no de código #docs #p2

## 🚧 En Curso (In Progress)

- [ ] 🤖 **Preparación de v3.1**: prototipado de inferencia empírica automatizada #quant #p2

## 🔍 En Revisión & QA (Review)

Sin tarjetas.

## ✅ Completado (Done)

- [x] 🗄️ **Formateo de Documentación como Base de Datos**: propiedades YAML enriquecidas (`id`, `type`, `category`, `status`, `related`) para Dataview y Obsidian #database
- [x] 📊 **Creación de Centro de Base de Datos**: [[database-hub]] con consultas Dataview y tablas Markdown para navegación relacional #database
- [x] 📈 **Catálogo Exhaustivo de Resultados**: [[results-catalog]] documentando los lotes de simulación y su nomenclatura (reportes, JSON y visualizaciones) #database
- [x] 🔬 **Catálogo Completo de Análisis y Scripts**: [[decision-analyses]] integrando 36 análisis operativos, 7 scripts utilitarios y 3 ejemplos #database
- [x] 📦 **Auditoría e Indexación de Documentación Legacy y Raíz**: [[legacy-docs]] con los 10 documentos históricos de `archive/legacy/` y archivos raíz #database
- [x] 🔗 **Interconexión Total del Grafo**: enlazado bidireccional entre módulos cuantitativos, guías, arquitectura, roadmap y resultados #graph
- [x] 🔬 **Auditoría granular de fidelidad por sección**: la resolución de clases pasó a ser por sección y no por unión de la nota, con un caso de dos módulos como prueba; único dueño por módulo verificado en tres canales (heading, frontmatter y registro) #qa
- [x] 🚧 **Conflicto de proprietarios resuelto**: `robust.py` y `bootstrap.py` tenían dos notas dueñas cada uno con contenido incompatible; se movió el contenido verificado al dueño que designa el registro y el otro quedó como puntero #docs
- [x] 🗑️ **Un solo vault, sin `.obsidian` en la raíz**: había dos copias byte-idénticas de 1.1 MB, y la de la raíz convertía todo el repositorio en vault al abrirlo; se borró con respaldo y se añadió a `.gitignore` #vault
- [x] 📜 **Schema reescrito desde medición**: la tabla de campos, los cuatro ejes de tags y las cifras reales del vault, con ratchet que ata prosa, tabla y notas en las tres direcciones #docs
- [x] 🧬 **Regla de corrupción de alfabeto**: detecta cirílico o chino pegados dentro de una palabra, con dos controles negativos que además exigen **no** marcar `σ` ni `Σ`, que son notación legítima #qa
- [x] 🧹 **`ruff` limpio en todo el repo, no sólo en `src/decision_maker`**: 115 hallazgos, 96 por autofix y 19 a mano. Entre ellos dos que eran bugs: un `open()` sin context manager que perdía el archivo, y `zip()` sin `strict=` que truncaba en silencio. Las migraciones de `alembic/versions` quedan excluidas con el motivo escrito: son el registro congelado de lo que ya corrió contra una base real #qa
- [x] 🧪 **Suite de pruebas documentales**: 24 tests nuevos que hacen falla la fidelidad y el schema, en lugar de depender de que alguien ejecute los scripts a mano #qa
- [x] 🔗 **Validación de Enlaces de Grafo**: 559 enlaces verificados, 546 resueltos y 13 rotos documentados, sin ninguno nuevo, mediante `scripts/check_docs_links.py` #qa
- [x] 🌐 **Validación de Consistencia Lingüística**: 0 intrusos léxicos y 0 alfabetos foreignos pegados, verificado mediante `scripts/check_obsidian_language.py` #qa
- [x] 🎯 **Validación de Fidelidad de Código**: 54 notas, 25 módulos, 45 clases, 25 imports, 25 propietarios y 189 literales de módulo verificadas con AST mediante `scripts/check_obsidian_fidelity.py` #qa
- [x] ⚡ **Suite de Pruebas Unitarias**: validación de 539 tests pasando con `uv run pytest` #qa
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
