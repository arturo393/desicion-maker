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
updated: 2026-10-02
---

# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

Desde v3.1 (2026-08-23). Commits del 2026-09-28 en adelante más el árbol de trabajo del 2026-10-01.

### ✨ Added
- **Escenarios comunes entre opciones** (`core/scenarios.py`, `core/models.py`, `core/monte_carlo.py`): `DecisionOption.add_variable(..., driver="nombre")`. Las variables con el mismo driver, de cualquier opción, se reordenan por rangos siguiendo un vector uniforme común sembrado del run: correlación de rangos 1 (comonotonía) y marginales intactas. Se excluyen de la correlación intra-opción. Un modelo sin drivers no consume números aleatorios extra y da exactamente lo mismo que antes con la misma semilla.
- **Minimax Regret por escenario** (`core/decision_theory.py`): con el modelo totalmente compartido compara simulación por simulación; si no, por percentiles. El texto del resultado dice qué método usó.
- **Valor de la información** (`core/value_of_information.py`, clave `value_of_information` del orquestador): EVPI total, válido sólo con modelo totalmente compartido (si no, `None` con la razón), y EVPPI por driver con 20 bins por cuantiles, ordenado de mayor a menor. Sesgo hacia arriba con N chico: medido hasta 0,7 % de la media del ganador con N=1.000, nulo con N=10.000.
- **Madurez de motores** (`core/engine_maturity.py`, clave `engine_maturity` del orquestador): `validated` (coincide con una referencia externa o un cálculo independiente), `characterized` (se sabe exactamente qué calcula aunque difiera del estándar) o `experimental`. Hoy: MonteCarlo y PROMETHEE validados, TOPSIS caracterizado, 16 experimentales. Un test exige entrada para cada motor ruteable y evidencia existente para cada `validated`.

### 🐛 Fixed
- **Semilla en Bootstrap de TOPSIS** (`core/bootstrap.py`, `core/orchestrator.py`): incorpora `seed: int | None = None` a `confidence_intervals` y `BootstrapConfig`, creando un `np.random.default_rng(seed)` local determinista en lugar de llamar a `np.random.normal` global. En `orchestrator.py` deriva `bootstrap_seed = (self.mc_engine.seed + BOOTSTRAP_SEED_OFFSET)` para aislar la secuencia de perturbación del remuestreo Monte Carlo sin correlación espuria.
- **`success_rate` nulo con una sola opción y simetría de penalización de cola** (`core/monte_carlo.py`, `core/models.py`, `core/report_schema.py`, `core/antifragile.py`, `api/server.py`, `dashboard/app.py`, `cli.py`, `core/deep_research_decision_agent.py`): reporta `success_rate = None` cuando sólo existe una opción evaluada (evitando un 100% ficticio por falta de competidores). Además unifica la comparación de `total_scores` contra `cross_option_mean` aplicando a ambos lados los puntajes con penalización de cola por ruina. Se actualizó el schema de reporte para admitir `["number", "null"]` y los consumidores para representar `"n/a"`.
- **Normalización y validación en TOPSIS** (`core/topsis.py`): normaliza criterios de beneficio mediante escala min-max lineal `(x - min) / (max - min)` con guarda ante división por cero, corrigiendo la inversión de rankings con valores negativos. Lanza `ValueError` explícito si `len(weights)` o `len(maximize)` no coinciden con la cantidad de factores, eliminando el truncamiento silencioso y subsiguiente `IndexError`.
- **Compuertas de decisión y ruina** (`core/decision_gates.py`, `core/ergodicity.py`): la compuerta de ruina reporta explícitamente "no aplicable" (`value=None`) sobre puntajes normalizados en `[0, 1]` (donde `RUIN_THRESHOLD=0.0` no puede activarse por definición), y evalúa veto correctamente sobre datos no normalizados con mayoría de puntajes negativos. Se actualizó la documentación en `README.md` y docstrings para precisar que la compuerta de ergodicidad es informativa en puntajes aditivos.
- **Exclusión temprana de opciones vetadas** (`core/orchestrator.py`): las compuertas de decisión se evalúan antes de invocar a los motores de ranking (TOPSIS, PROMETHEE, Borda), excluyendo de inmediato a las opciones vetadas para que no aparezcan clasificadas en los resultados subsiguientes.
- **Acuerdo de ganador multicriterio** (`core/orchestrator.py`, `docs/architecture.md`): incorpora al resultado el diccionario `winner_agreement` (`topsis`, `promethee`, `borda`) que mide la concordancia del ganador de Monte Carlo con el líder de cada método, documentando la regla en la arquitectura.
- **Semilla y reproducibilidad Monte Carlo** (`core/monte_carlo.py`, `core/models.py`, `core/uncertainty.py`): `MonteCarloEngine` admite `seed: int | None = None` y genera un `np.random.Generator` determinista (derivando entropía si es `None`), almacenando la semilla en el motor y en la traza `DM_MC_TRACE`. Pasa el generador a `UncertainVariable.sample(n, rng)` manteniendo compatibilidad, y deriva la semilla en `ranking_confidence`.
- **Minimax Regret con estados cuantílicos comonótonos** (`core/decision_theory.py`): evalúa regret sobre estados discretos definidos por la tupla constante `REGRET_STATE_PERCENTILES = (5.0, 25.0, 50.0, 75.0, 95.0)`, documentando la hipótesis de comonotonía y evitando el emparejamiento ficticio de iteraciones Monte Carlo independientes.
- **Orden invariante en números difusos perturbados** (`core/bootstrap.py`): ordena el triplete `(a, b, c)` tras la adición de ruido normal independiente para asegurar la restricción estructural $a \le b \le c$.
- **Persistencia de peor puntaje bajo shock de pesos** (`core/robust.py`): almacena `worst_score` en `results["weight_shock_worst"][opt_name]`.
- **Validación estricta de variables inciertas** (`core/models.py`): lanza `ValueError` claro ante parámetros `NaN` o `Inf` en vez de sustituirlos silenciosamente por valores por defecto, y lanza `ValueError` ante fallos de muestreo en lugar de retornar ceros.
- **Acotación de robustez y consistencia de recomendación** (`core/deep_research_decision_agent.py`): acota `scenario_robustness` en `[0.0, 1.0]` y hace converger la opción marcada como `"Recommended"` con el ganador de `overall_score` (Monte Carlo).
- **Normalización de PROMETHEE crisp en modo avanzado** (`core/orchestrator.py`): normaliza el DataFrame determinista antes de computar flujos netos, garantizando paridad metodológica con el cálculo estocástico.
- **Puntaje Borda para opciones no clasificadas** (`core/aggregator.py`): asigna a las alternativas omitidas por un método el promedio algebraico de los puntos no asignados `(n - k - 1) / 2.0`.
- **Interpretación relativa de puntajes en análisis SQM y DIY** (`analyses/sqm_santiago.py`, `analyses/furniture_diy.py`): actualiza los mensajes en terminal para explicitar que los puntajes corresponden a una posición relativa dentro del conjunto de alternativas comparadas en la corrida.
- **Fuga de `factor_stats` entre opciones** (`41c33a3`, 2026-09-29): el segundo lazo de `MonteCarloEngine.run()` reusaba `factor_stats` y `raw_factor_data` de la **última** opción para todas. Introducido en `c343bf9` (2026-08-23). Afectaba a los consumidores de esos campos: `sensitivity` (modo `standard`), `genetic`, `ml_surrogate`, `reporting`, `explainability`, `antifragile`, `information_theory` y `what_if`. `mean_score`, percentiles y ranking no estaban afectados. Los resultados en `results/` generados entre 2026-08-23 y 2026-09-29 tienen esos campos por opción corruptos; ver [[docs/results-catalog|results-catalog]].
- **Penalización de cola con puntajes negativos**: ahora resta `|s|*(1-p)` en vez de multiplicar por `p`. Con `normalize=False` y puntajes negativos, multiplicar acercaba la cola a cero y la **mejoraba**. Con `normalize=True` (el default) las dos fórmulas coinciden.
- **CI no corría en push**: el trigger tenía `branches: [master]` y `master` se renombró/borró el 2026-09-28, así que ningún push corrió CI desde entonces (`41c33a3` nunca pasó por CI). Ahora push sin filtro de rama, `workflow_dispatch` y `concurrency`.
- **Puntos ciegos de los checkers**: `check_docs_links.py` revisa imágenes y definiciones `[ref]:`, falla con un fence sin cerrar, con rutas que escapan del repo y con exenciones `KNOWN_BROKEN` que ya no hacen falta (anclas `#...` y `<a href>` quedan fuera a propósito); `check_obsidian_fidelity.py` falla con un fence sin cerrar y resuelve literales `dir/archivo.py` como rutas; `check_docs_scope.py` falla si `docs/` falta o está vacío; `dev_agents_linter.py` falla con algo que no es directorio y cubre `async def`. Parser de fences compartido en `scripts/_fences.py`.
- **`jira_manager.py`**: sin credenciales por defecto (se exigen por entorno), con timeout y códigos de salida.
- `uvicorn` importado a nivel de módulo dejaba el server inimportable sin el extra (`231bada`).
- El linter de dev-agents estaba rojo desde `74d116e`: 2 defectos y un ratchet (`6d4dac5`).
- `ruff` limpio en todo el repo: 115 hallazgos, 2 de ellos bugs — un `open()` sin context manager y `zip()` sin `strict=` (`161d7d9`).
- `mkdocs.yml` nunca fue YAML válido, y 3 cards del kanban describían defectos falsos (`4586f6c`).
- **`fsk_protocol_evaluation.py` y `fsk_scanner_integration.py` (v2)**: se caían al importar y su Monte Carlo no registraba factores. Reescritos sobre su propia tabla de puntajes y pesos, con test de humo.
- **El motor ya no puntúa en silencio un modelo vacío o incompleto**: `MonteCarloEngine.run()` lanza `ValueError` si no hay opciones, si no hay factores, o si a una opción le falta la variable de un factor. Antes devolvía `{}` en los dos primeros casos y en el tercero sumaba 0 a esa opción, que es el peor puntaje posible, sin aviso. Los 8 tests que fijaban ese comportamiento como contrato se invirtieron.
- **`DecisionAnalysisEngine` (capa legacy) vuelve a cumplir su contrato original**: el shim del 19-Jul (`8361a5a`) no registraba ni las opciones que recibe `analyze_option(option, all_options)` ni ningún factor, así que `mining_decision`, `mining_improved`, `furniture_diy`, `refactoring_decision`, `sqm_santiago` e `ip_config_strategy` comparaban 0.0 contra 0.0 y ganaba la primera al ordenar. Ahora registra las opciones y, sin `add_factor`, puntúa con `CAREER_FACTORS`: los pesos del motor original (`eed6522~1`) y su ±15 % de salario. `overall_score` vuelve a la escala 0..10 que esos scripts imprimen; una opción desconocida lanza `KeyError` en vez de devolver ceros; `CareerOption` recupera `pros`/`cons`, que el shim había perdido (`ip_config_strategy` se caía al construirla). Resultados de esos análisis anteriores al 2026-10-02: nulos.
- **Cadena `power_supply`**: los tres productores escribían junto a su código en `src/` (y uno, `power_supply_gemini_research.json`, no lo cubría el `.gitignore`), y guardaban un archivo aunque todas las consultas hubieran fallado. Ahora escriben en `results/power_supply/` y salen con 1 si fallan todas. `process_research_results.py` escribía por defecto en el repo `sw-diagnosticoremoto`; ahora en `results/`, y publicar allá es opt-in con `POWER_SUPPLY_OUTPUT_DIR`.
- **El ratchet del conteo de tests se saltaba siempre** con el nuevo `addopts = -m "not smoke"`: trataba el `-m` por defecto como una corrida parcial. Ahora lo reconoce, y un test exige que su copia del filtro coincida con `pyproject.toml`.
- **`decision-analyses.md` atribuía métodos que los scripts no usan**: 11 análisis no llaman al motor del framework y su columna nombraba `[[monte-carlo-engine]]`, AHP, PROMETHEE, Pareto, antifrágil u optimización robusta; varios ni mencionan el método. Reescritas con lo que cada uno hace.
- Test de ergodicidad tautológico: afirmaba `ruin_probability >= 0.0`, que no puede fallar porque es `count/len`; ahora exige el rango medido para N(0,10).

### ⚠️ Known Issues
- **TOPSISEngine colapsa a suma ponderada (SAW) en datos crisp**: en `core/topsis.py` la distancia a los ideales se evalúa como la suma $L_1$ de distancias unidimensionales (`sum(fuzzy_distance(...))`) en lugar de la norma euclidiana $L_2$ multidimensional. Para datos crisp acotados en $[0, 1]$, $d^+ + d^- = 1.0$ constante, por lo que $C_i = d_i^- / (d_i^+ + d_i^-) = \sum w_j x_{ij}$ (idéntico a SAW), perdiendo la penalización cuadrática sobre extremos que caracteriza a TOPSIS y difiriendo del orden de Hwang & Yoon (1981).
- `process_utility_analysis.py` carga la investigación sólo para exigir que exista (descarta el resultado de `json.load`); su análisis está escrito a mano.
- La penalización de cola no distingue colas (recorte fijo de ~5 % por opción): decisión de modelado abierta.

### ✨ Added
- **Comparación contra pymcdm** (`tests/test_reference_libraries.py`): validación cruzada de motores multicriterio contra la biblioteca externa `pymcdm` (v1.4.0). PROMETHEE II (`PrometheeEngine`) evaluado en flujos netos y ranking contra `pymcdm.methods.PROMETHEE_II` con funciones de preferencia "usual" y "vshape" (con parámetros $p$) en matrices fijas y pseudoaleatorias con criterios mixtos de beneficio y costo (coincidencia exacta). TOPSIS crisp verificado contra `pymcdm.methods.WSM(minmax_normalization)` y contra suma ponderada min-max manual en NumPy (coincidencia exacta); divergencia con el TOPSIS euclidiano clásico de `pymcdm` documentada y marcada con `xfail(strict=True)`.
- **Control de convergencia del Monte Carlo y error estándar** (`core/monte_carlo.py`, `core/models.py`, `core/orchestrator.py`, `core/report_schema.py`, `core/reporting.py`, `tests/test_monte_carlo_convergence.py`): incorpora `standard_error: float | None = None` a `Statistics` ($\text{std} / \sqrt{N}$); implementa diagnóstico de convergencia que compara el gap de las dos mejores medias contra $\text{CONVERGENCE\_Z} \cdot \sqrt{\text{se}_1^2 + \text{se}_2^2}$ ($Z=2.0$, ~95% de confianza) y emite un warning con recomendación de $N$ usando la regla $1/\sqrt{N}$; expuesto en `engine.last_convergence` y bajo la clave `"convergence"` en `run_analysis`; serializado en reportes JSON y validado con control negativo.
- **Tests por propiedades con hypothesis** (`tests/test_properties.py`): verificación axiomática mediante pruebas generativas: dominancia (MC, TOPSIS, PROMETHEE II), invariancia ante escala positiva de pesos ($k > 0$ preserva rankings) e invariancia ante permutación de orden de opciones con variables deterministas. Hallazgo de inversión de rango (rank reversal) en TOPSIS al agregar una tercera opción dominada confirmado empíricamente por hypothesis (`xfail(strict=True)` con contraejemplo mínimo).
- **Rigor de verificación y ratchets documentales** (`docs/kanban.md`, `docs/architecture.md`, `docs/index.md`, `README.md`): ratchets actualizados a 599 tests unitarios; tarjetas de librerías de referencia, convergencia MC y tests por propiedades movidas a Done en el Kanban; confirmación y contraejemplo mínimo de rank reversal incorporados a la tarjeta de puntaje relativo.
- **Validación de motores contra la literatura** (`tests/test_published_examples.py`): AHP contra el autovector principal, PROMETHEE II contra un cálculo a mano según Brans & Vincke (1985), y TOPSIS contra el TOPSIS clásico calculado en el test sobre los datos del caza de Hwang & Yoon (1981). Todos los valores esperados se calculan en el test; ninguno se cita de una tabla. Dos `xfail(strict=True)` documentan que el TOPSIS del motor no es el clásico.
- **Humo de todos los análisis** (`tests/test_analyses_smoke.py`, `uv run pytest -m smoke`, paso propio en CI): corre cada `analyses/*.py` como subproceso, sin LLM. Exige exit 0 sin traceback, que los que necesitan LLM o datos fallen con un motivo, y —leyendo la traza del propio motor (`DM_MC_TRACE`), no la salida del script— que cada análisis haya corrido `MonteCarloEngine` puntuando al menos una opción y distinguiendo entre ellas. Control negativo: con el motor y el shim viejos puestos de vuelta, falla exactamente en los cinco análisis que comparaban 0.0 contra 0.0. Un análisis nuevo entra solo por el glob. 11 análisis declarados `NO_ENGINE` (TOPSIS/MC propios, calculadoras): para ellos sólo se verifica que corran.
- `DM_MC_TRACE=<archivo>`: una línea JSON por corrida del motor con la media de cada opción. Apagado por defecto.
- **Análisis `diagnostico_remoto_linea_base_decision.py`** (v1.2): sobre qué línea de sw-diagnosticoremoto seguir construyendo. Gana E (una línea de producto VHF+UHF, `development` como laboratorio): MC 0.752, TOPSIS 0.836; D segundo con 0.719. Ver [[docs/sw-diagnosticoremoto/README|sw-diagnosticoremoto]].
- **Tests de regresión**: la fuga de `factor_stats` entre opciones, y la penalización de cola con puntajes negativos.
- **Backend `agy`** (`core/agy_backend.py`): sin `GEMINI_API_KEY`, las llamadas a IA se responden con el CLI de Antigravity (`agy -p` en modo plan y sandbox). `DM_LLM_BACKEND=auto|api|agy`; `gemini_helper.ask_llm` lanza en vez de devolver el error como texto. Los tres `power_supply_*` que importaban `google.generativeai` directo pasan por él.
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
