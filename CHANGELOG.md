---
aliases: [Changelog, Historial de Cambios]
tags: [changelog, lumina, quant, project-management]
id: ROOT-CHANGELOG
title: "Decision Maker Changelog"
type: changelog
category: project-management
status: active
related: ["[[docs/kanban|kanban]]", "[[docs/index|index]]", "[[docs/adr/001-use-rust-for-math-engine|adr-001]]"]
created: 2026-08-10
updated: 2026-10-01
---

# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

Desde v3.1 (2026-08-23). Commits del 2026-09-28 en adelante más el árbol de trabajo del 2026-10-01.

### 🐛 Fixed
- **Fuga de `factor_stats` entre opciones** (`41c33a3`, 2026-09-29): el segundo lazo de `MonteCarloEngine.run()` reusaba `factor_stats` y `raw_factor_data` de la **última** opción para todas. Introducido en `c343bf9` (2026-08-23). Afectaba a los consumidores de esos campos: `sensitivity` (modo `standard`), `genetic`, `ml_surrogate`, `reporting`, `explainability`, `antifragile`, `information_theory` y `what_if`. `mean_score`, percentiles y ranking no estaban afectados. Los resultados en `results/` generados entre 2026-08-23 y 2026-09-29 tienen esos campos por opción corruptos; ver [[docs/results-catalog|results-catalog]].
- **Penalización de cola con puntajes negativos**: ahora resta `|s|*(1-p)` en vez de multiplicar por `p`. Con `normalize=False` y puntajes negativos, multiplicar acercaba la cola a cero y la **mejoraba**. Con `normalize=True` (el default) las dos fórmulas coinciden.
- **CI no corría en push**: el trigger tenía `branches: [master]` y `master` se renombró/borró el 2026-09-28, así que ningún push corrió CI desde entonces (`41c33a3` nunca pasó por CI). Ahora push sin filtro de rama, `workflow_dispatch` y `concurrency`.
- **Puntos ciegos de los checkers**: `check_docs_links.py` revisa imágenes y definiciones `[ref]:`, falla con un fence sin cerrar, con rutas que escapan del repo y con exenciones `KNOWN_BROKEN` que ya no hacen falta (anclas `#...` y `<a href>` quedan fuera a propósito); `check_obsidian_fidelity.py` falla con un fence sin cerrar y resuelve literales `dir/archivo.py` como rutas; `check_docs_scope.py` falla si `docs/` falta o está vacío; `dev_agents_linter.py` falla con algo que no es directorio y cubre `async def`. Parser de fences compartido en `scripts/_fences.py`.
- **`jira_manager.py`**: sin credenciales por defecto (se exigen por entorno), con timeout y códigos de salida.
- `uvicorn` importado a nivel de módulo dejaba el server inimportable sin el extra (`231bada`).
- El linter de dev-agents estaba rojo desde `74d116e`: 2 defectos y un ratchet (`6d4dac5`).
- `ruff` limpio en todo el repo: 115 hallazgos, 2 de ellos bugs — un `open()` sin context manager y `zip()` sin `strict=` (`161d7d9`).
- `mkdocs.yml` nunca fue YAML válido, y 3 cards del kanban describían defectos falsos (`4586f6c`).
- Test de ergodicidad tautológico: afirmaba `ruin_probability >= 0.0`, que no puede fallar porque es `count/len`; ahora exige el rango medido para N(0,10).

### ✨ Added
- **Análisis `diagnostico_remoto_linea_base_decision.py`** (v1.2): sobre qué línea de sw-diagnosticoremoto seguir construyendo. Gana E (una línea de producto VHF+UHF, `development` como laboratorio): MC 0.752, TOPSIS 0.836; D segundo con 0.719. Ver [[docs/sw-diagnosticoremoto/README|sw-diagnosticoremoto]].
- **Tests de regresión**: la fuga de `factor_stats` entre opciones, y la penalización de cola con puntajes negativos.
- Los 5 checkers documentales se ejecutan desde pytest, no sólo como pasos de CI (`6fdba0b`).
- Ratchets sobre las cifras que declaran las notas: tests, análisis, motores, piso de Python (`18cb0ae`).
- Vault de Obsidian consolidado en `docs/`, auditoría estructural y 4 checkers en CI (`81582b5`), con [[docs/database-hub|database-hub]] (centro de base de datos relacional), [[docs/kanban|kanban]] (tablero del proyecto) y [[docs/note-schema|note-schema]] (esquema canónico de notas).

### 🗑️ Removed
- `mkdocs.yml` y el extra `docs` de `pyproject.toml` (`a1a8eae`): nunca se usó y no puede leer los wikilinks del vault.
- `ndarray` de `rust_core/Cargo.toml`, declarado y sin un solo uso (`95829fa`).
- `test_engine_runs_without_rust_module`: parcheaba un módulo que `monte_carlo.py` nunca importa, así que no podía fallar.

### 🔧 Changed
- `uv.lock` versionado; CI usa `uv sync --frozen`, que falla si el lock no corresponde a `pyproject.toml` (`7e5e650`).
- El conteo de motores se deriva del código: 19 motores ruteables en `ENGINE_UNIVERSE` (`core/adaptive_router.py`), no los 24 que repetían tres notas (`b5600ad`).

## [v3.1] - 2026-08-23

Rediseño arquitectónico cuantitativo (trabajo de las incidencias ID-1846 y continuación 19–23 Ago).

### 🦀 Núcleo Rust
- **`rust_core/`** — crate `decision_maker_core` (pyo3 + rayon + ndarray) que expone la normalización Min-Max global del Monte Carlo.
- **`MonteCarloEngine.run(normalize=True)`** ahora usa los mismos bounds globales que el núcleo Rust, alineando Python y Rust.
- Fallback a motor Python puro si el módulo nativo no está instalado.

### 🧠 Aprendizaje y Meta-Aprendizaje
- **Learning System** — `outcome_tracker` (seguimiento de resultados), `calibration` (calibración de confianza), `decision_journal` (diario), `adaptive_router` (enrutamiento adaptivo de motores).
- **Meta-Learning** — `action_threshold` (umbral de acción), `reasoning_trace` (traza de razonamiento), `unknown_scanner` (detección de incógnitas), `meta_calibration`.

### 🚦 Compuertas de Decisión con Veto
- **`decision_gates`** con poder de veto real: ergodicidad (`ergodicity`), ruina (`ruin_probabilities` cableado desde Monte Carlo), DAG causal (`causal_dag`), compromiso (`decision_commitment`).

### 📉 Ergonomía y Riesgo
- **Ergodicity analyzer** — crecimiento promedio-tiempo vs ensamble, probabilidad de ruina.
- **Kelly criterion** — dimensionamiento óptimo de apuesta bajo incertidumbre (umbral de campo, no degenerado).
- Correlación de Cholesky entre factores en Monte Carlo.

### 🔀 Motor Difuso
- Lógica difusa migrada a **`FuzzyWeightedSum`** (antes embebida); integrado en `analyses/decision_concon.py`.

### 🧹 Auditoría Infinita
- 10 rondas de auditoría que eliminaron código muerto, inconsistencias y brechas críticas.
- Des-normalización de consumidores de escala rotos por el cableado Rust: Kelly, `via_negativa`, `success_rate`, `confidence_weighted_winner`, matriz de decisión.

### 🧪 Test Suite
- **495 tests passing** en todos los motores (era 322 en v3.0).

## [v3.0] - 2026-06-02

### 🧠 10 New Decision Engines
- **Antifragile** — Taleb-inspired barbell strategy, convexity/optionality, fragility indexing, and via negativa analysis.
- **Group Decision** — Multi-stakeholder weight aggregation into consensus rankings using statistical methods.
- **Information Theory** — Mutual information analysis to quantify non-linear influence of each factor on scores.
- **Portfolio Optimization** — Mean-variance resource allocation across options with efficient frontier.
- **What-If Analysis** — Interactive engine to tweak weights/directions and see scores recomputed in real time (includes REPL).
- **Weight Derivation** — Swing weighting, AHP pairwise comparison, and PAPRIKA to derive weights from human judgment.
- **Explainability** — Factor-contribution waterfalls, counterfactuals, and narrative generation for human-readable decision reports.
- **Topological Data Analysis** — MDS/Isomap embedding, clustering, and ranking stability analysis.
- **Visualization Engine** — Matplotlib/seaborn plots (Pareto frontier, tornado, distributions) with dark theme.
- **Decision Registry** — SQLite-backed persistent store for querying, comparing, and tracking outcomes across analyses.

### 🌐 API & Dashboard
- **REST API** (`src/decision_maker/api/server.py`) — FastAPI server exposing the full decision framework via Pydantic-schematized endpoints.
- **Web Dashboard** (`src/decision_maker/dashboard/app.py`) — Interactive frontend for running analyses and visualizing results.

### 🖥️ CLI Overhaul
- **`decision-maker` CLI** — Typer-based entry point with subcommands for running configs and distribution listing.
- **`run` command** — Execute decision configs from YAML/JSON files, with `--what-if` flag for interactive REPL mode.
- **`list-distributions` command** — Show all available probability distributions and their parameters.

### ⚙️ Core Improvements
- Removed legacy `unified_decision_framework.py` — logic fully migrated into `orchestrator.py`.
- Cleaned up old test artifacts (`old_framework.py`, `old_gemini.py`, `old_gemini_flash.py`, `old_structure.py`, `test_integration_bdd.py`).
- Updated reporting engine with enhanced HTML templates.
- Improved Monte Carlo and robust optimization internals.
- Enhanced genetic optimizer convergence logic.

### 🧪 Test Suite
- **322 tests passing** across all 24 engines.
- New test suites for: antifragile, explainability, group_decision, information_theory, portfolio, registry, topology, visualization, weight_derivation, what_if.
- Updated existing test suites for genetic, monte_carlo, robust, and unified workflows.

### 📦 Dependencies
- Added `matplotlib`, `seaborn`, `scikit-learn`, `aiohttp`, `pydantic`, `typer`, `jinja2`.
- Added optional `google-genai` dependency for AI-powered research.

## [v2.2] - 2026-05-12

### 🔌 Full Engine Integration
-   **PROMETHEE with uncertainty** (`_promethee_with_uncertainty`) now runs in `standard` mode (previously only `advanced`), averaging PROMETHEE net flows across p5/mean/p95 percentiles.
-   **Robust Optimizer** now runs in `standard` mode, computing worst-case scores under weight shocks.
-   **Rank Aggregation (Borda)** now runs in both `standard` and `advanced` modes. `standard` aggregates 3 methods (TOPSIS, MC, PROMETHEE uncertainty); `advanced` aggregates 4 (adds crisp PROMETHEE).
-   **Scale mismatch detection** (`_check_scale_mismatch`) warns when factor scales differ by >10x.
-   Weights and max/min bools are computed once and reused across all engines.

### 🧪 Test Suite
-   Updated `test_orchestrator.py` and `test_integration_bdd.py` to verify new standard-mode engines.
-   **199 tests passing** across all 18 engines.

### 📊 Comparison Script
-   Added `examples/mac_upgrade_comparison.py` to run the Mac upgrade case in all 3 modes (express/standard/advanced) and compare results side-by-side.

## [v2.1] - 2026-02-17

### 🚀 Major Improvements
-   **Pivot to Generic Python Library**: The project is no longer a specific Mac Upgrade app but a generic decision support framework.
-   **New Generic Template**: Added `generic_template.py` as the primary entry point for users to model *any* decision.
-   **Refactored Examples**: Moved `cases/mac_upgrade_decision.py` to `examples/mac_upgrade_example.py`.

### 🗑️ Removals
-   **Removed Web UI (`app.py`)**: Streamlit Dashboard removed to focus on a pure Python library experience.
-   **Removed `cases/` directory**: Replaced by `examples/`.

### ✨ New Features
-   **Interactive AHP (CLI)**: Although the Web UI was removed, the `AHPHelper` class remains available for programmatic weight calculation.
-   **Frankenstein Logic**: `GeneticOptimizer` now calculates the theoretical maximum score based on the best traits of all options.

## [v2.0] - 2026-02-13

### Added
-   **Unified Decision Framework**: Consolidated 18 methodologies into a single Python class.
-   **Advanced Methodologies**: Added Pareto Analysis, Sensitivity Analysis, and Future Horizons (Bayesian, ROA, MDP, Genetic).
-   **AI Integration**: Added support for Google Gemini to provide qualitative insights.
