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
updated: 2026-10-02
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

- [ ] 🧬 **¿`Genetic` sin ruta es deliberado?** Está en `ENGINE_UNIVERSE` y en ninguna ruta, ni en `advanced` — decisión de producto #p2
- [ ] 🧩 **`scripts/samba_performance_strategy.py` no corre**: migración a medias — construye `UnifiedDecisionFramework(debug=...)` y llama `analyze_option`, que el framework no tiene. Su propio docstring ya dice que hay que reescribirlo #analyses #p3
- [ ] 🕳️ **Punto ciego del humo: 11 análisis con motor propio** (`NO_ENGINE` en `test_analyses_smoke.py`): para los que tienen TOPSIS/MC propio en numpy, el humo sólo prueba que corren, no que distingan opciones. Migrarlos al framework o darles su propia aserción #qa #p3
- [ ] ✏️ **`samba`/`commandmessage`/varios declaran metodologías que no aplican**: se corrigió la tabla de [[decision-analyses]], pero los docstrings de varios scripts siguen prometiendo «13 metodologías» o Monte Carlo sin usarlo #docs #p3
- [ ] 📐 **Decidir qué TOPSIS queremos: hoy, con datos crisp, es una suma ponderada**: `core/topsis.py` es TOPSIS difuso a la Chen (suma distancias por criterio), y con a=b=c eso da exactamente la suma ponderada de puntajes min-max (`test_crisp_topsis_is_a_min_max_weighted_sum`). Con los datos del caza de Hwang & Yoon ordena A3>A1>A4>A2; el TOPSIS clásico (normalización vectorial, distancia euclidiana) da A1>A3>A4>A2. Con triángulos (p5, media, p95) se aparta algo, no mucho. Pasar a distancia euclidiana cambia rankings ya hechos: decisión de modelado. Dos tests `xfail(strict=True)` lo marcan #quant #p1
- [ ] 📶 **`process_utility_analysis.py` no lee la investigación que dice reinterpretar**: `json.load(f)` sin asignar; el análisis está escrito a mano. Reescribirlo sobre `power_supply_research_results.json` o declararlo como plantilla #analyses #p2
- [ ] ⚠️ **`pymcdm.methods.PROMETHEE_II` agota su generador interno de funciones de preferencia tras una corrida**: cuando se inicializa con listas de parámetros ($p$, $q$), `self.pfs` se almacena como una expresión generadora que se consume en la primera invocación. Llamar a la misma instancia por segunda vez lanza `IndexError: axis 1 is out of bounds`. Cualquier wrapper o benchmark debe instanciar un nuevo `PROMETHEE_II` por corrida o convertir `pfs` a tupla #deps #qa #p3
- [ ] 🔁 **Puntaje relativo y rank reversal**: el puntaje es min-max sobre las opciones de la corrida, así que agregar una opción puede reordenar las demás. **Confirmado y medido con `hypothesis` en `test_properties.py` (`test_rank_reversal_topsis_with_dominated_third_option`)**: con $w=[0.25, 0.75]$, $A=[1.0, 7.0]$ y $B=[2.0, 6.0]$, $A$ gana inicialmente ($0.75 > 0.25$); al introducir $C=[0.0, 0.0]$ estrictamente dominada por ambas, el rango se expande de forma no uniforme y $B$ pasa a ganar ($0.8929 > 0.8750$). Evaluar funciones de valor por criterio fijadas por el decisor para evitar distorsión relativa #quant #p2
- [ ] 📐 **EVPPI sesgado hacia arriba con N chico**: el máximo de medias por bin con ruido supera el de las medias verdaderas. Medido con un factor de riesgo que no cambia la decisión: hasta 0,7 % de la media del ganador con N=1.000 y 0 con N=10.000. Corregirlo (p. ej. restar el EVPPI de un driver permutado) o exigir N mínimo; tampoco se hizo EVSI (información muestral) #quant #p3
- [ ] 📒 **Registrar el resultado de las decisiones reales**: `OutcomeTracker`/`DecisionJournal` existen y ningún análisis los usa. Empezar por la línea base del diagnóstico remoto. Es lo que prueba si el framework decide bien #process #p1
- [ ] 📦 **Publicar en PyPI con versión etiquetada**: depende de «Versión sin fuente única» #infra #p3
- [ ] 🧮 **La compuerta de ruina decide «no aplicable» por el rango de los puntajes, no por `normalize`**: con `normalize=False` y todos los puntajes en [0, 1] también dice «no aplicable» (correcto en el resultado, ninguno puede bajar de 0, pero por inferencia). Pasarle el flag explícito #quant #p3
- [ ] 📏 **`sqm_santiago`/`furniture_diy` siguen cortando en 5.0 y 3.5**: el texto ya dice «posición relativa», pero los umbrales absolutos sobre un puntaje min-max no significan nada. Quitarlos o ranquear #analyses #p3
- [ ] 🔬 **Correr los `power_supply_*` con `agy`**: ya no necesitan API key, pero no se corrieron enteros (~25 s por consulta). Los dos `process_*` leen los datasets que ellos generan, así que van después #analyses #p2
- [ ] 📡 **Cerrar la decisión de línea base del diagnóstico remoto**: E gana, pero (a) la fecha de ID-1476 decide entre E y D (escenario S4 en empate), (b) S6 sin verificar: si los arreglos que le faltan a v4.2.0 importan en un VHF de campo, (c) S2: clientes instalados por línea. Fijar semilla para que S4 sea reproducible #analyses #p1
- [ ] ♻️ **Re-correr lo que usó datos por factor entre 2026-08-23 y 2026-09-29**: `factor_stats`/`raw_factor_data` eran los de la última opción. Sólo afecta reportes de sensibilidad, explicabilidad, antifrágil o genético; los rankings están sanos ([[results-catalog]]) #analyses #p2
- [ ] 📉 **¿La penalización de cola tiene que distinguir colas?** Hoy recorta ~5 % fijo por opción ([[monte-carlo-engine]]). Cambiar a un umbral común reordena todos los análisis ya hechos — decisión de modelado #quant #p2
- [ ] 🌿 **Rama por defecto de GitHub en `main`**: se sincronizó `improve-computer-decision` con `main` (mismo HEAD). La cuenta de `gh` (`arturoSigmadev`) tiene push pero no admin; cambiar la default branch a `main` en Settings → Default branch de GitHub cuando sea conveniente #infra #p2
- [ ] 🗂️ **`metadata.json` cubre 5 de 37 análisis** y sus `results_location` no existen: completarlo o retirarlo #docs #p3
- [ ] 🏷️ **Versión sin fuente única**: `pyproject.toml` dice 3.0.0, la doc v3.1, y no hay tags de git #infra #p3
- [ ] 🧱 **`commandmessage_*` fallan en un clon limpio**: escriben en `results/` sin crearlo. Y los `sniffertelemetry` v1–v4 comparten nombres de opción, así que sus `analysis_*.json` genéricos no se distinguen #analyses #p3
- [ ] 🔍 **Huecos que quedan en los checkers**: anclas `#...` no se verifican; `check_obsidian_language.py` detecta archivo con una ventana de 400 caracteres y no saca fences `~~~`; `dev_agents_linter.py` indexa UX-01 por nombre de función y dos métodos homónimos se pisan #qa #p3
- [ ] 📝 **Documentar módulos auxiliares restantes**: crear notas para submódulos de soporte secundario en `src/decision_maker/core/` (como `config_runner.py`, `jsonl_store.py`) #docs #p3

## 🚧 En Curso (In Progress)

Sin tarjetas.

## 🔍 En Revisión & QA (Review)

Sin tarjetas.

## ✅ Completado (Done)

- [x] 🌐 **Escenarios comunes, valor de la información y madurez de motores** (2026-10-08, `agy` + revisión): `add_variable(..., driver="mercado")` acopla de forma comonótona las variables de todas las opciones que dependen del mismo factor de riesgo, conservando cada marginal (`core/scenarios.py`); sin drivers, mismos números que antes con la misma semilla. Minimax Regret vuelve a ser por escenario cuando el modelo está totalmente compartido. EVPI total (sólo con modelo totalmente compartido) y EVPPI por driver, ordenado: «qué conviene averiguar primero» (`core/value_of_information.py`). Madurez de los 19 motores en `core/engine_maturity.py` con test que impide «validated» sin evidencia: MonteCarlo y PROMETHEE validados, TOPSIS caracterizado, el resto experimental #core

- [x] ⚖️ **Comparar contra librerías establecidas** (2026-10-07, `agy` + revisión): `src/decision_maker/tests/test_reference_libraries.py`. PROMETHEE II (`PrometheeEngine`) validado contra `pymcdm.methods.PROMETHEE_II` (v1.4.0) en flujos netos y rankings con preferencia "usual" y "vshape" (con parámetros $p$) en matrices fijas y aleatorias con criterios de beneficio y costo. TOPSIS crisp verificado contra `pymcdm.methods.WSM(normalizations.minmax_normalization)` y contra suma ponderada min-max en numpy (coincidencia exacta). Divergencia metodológica entre TOPSIS Chen (suma $L_1$) y TOPSIS clásico de `pymcdm` (distancia euclidiana $L_2$) documentada con `xfail(strict=True)` #qa #core

- [x] 🎯 **Control de convergencia del Monte Carlo** (2026-10-07, `agy` + revisión): `core/monte_carlo.py`, `core/models.py`, `core/orchestrator.py`, `tests/test_monte_carlo_convergence.py`. Incorpora `Statistics.standard_error: float | None = None` calculado como $\text{std}/\sqrt{N}$. Implementa diagnóstico de convergencia comparando el gap de las dos mejores medias contra $\text{CONVERGENCE\_Z} \cdot \sqrt{\text{se}_1^2 + \text{se}_2^2}$ ($Z=2.0$, ~95% de confianza); emite `logger.warning` accionable sugiriendo $N$ necesario por la regla $1/\sqrt{N}$. Expuesto en `self.last_convergence` y `"convergence"` en el resultado de `run_analysis()`. Serializado en `REPORT_SCHEMA` y reportes JSON. Verificado con control negativo #quant #core

- [x] 🧪 **Tests por propiedades con `hypothesis`** (2026-10-07, `agy` + revisión): `src/decision_maker/tests/test_properties.py`. Verificación axiomática mediante pruebas basadas en propiedades: dominancia (opción dominante nunca queda debajo de la dominada en Monte Carlo, TOPSIS ni PROMETHEE II), invariancia ante escala positiva de pesos ($k > 0$ preserva rankings) e invariancia ante permutación de orden de inserción de opciones con variables deterministas #qa #core

- [x] 🎲 **Semilla en Bootstrap de TOPSIS** (2026-10-02): `core/bootstrap.py` incorpora `seed: int | None = None` a `confidence_intervals` y `BootstrapConfig`, usando un `default_rng(seed)` local determinista. `core/orchestrator.py` deriva `self.mc_engine.seed + BOOTSTRAP_SEED_OFFSET` (offset 1) para aislar la secuencia estocástica del remuestreo Monte Carlo sin introducir correlación espuria. Test de reproducibilidad con control negativo verificado #core #quant

- [x] 1️⃣ **`success_rate = None` con una sola opción y simetría de penalización de cola** (2026-10-02): con una sola opción no hay competidor contra el cual medir tasa de éxito (`Statistics.success_rate: float | None = None`). Consumidores actualizados para propagar None o renderizar "n/a" (`core/antifragile.py`, `core/reporting.py`, `core/report_schema.py` admitiendo null, `api/server.py`, `dashboard/app.py`, `cli.py`, `core/deep_research_decision_agent.py`). Ambos lados de la comparación de corte usan puntajes con penalización de cola. Tests y 3 controles negativos verificados #core #quant

- [x] 📚 **Validar los motores contra la literatura** (2026-10-04, `agy` + revisión): `tests/test_published_examples.py`. AHP contra el autovector principal calculado en el test (el motor aproxima por media de filas: ±0.004); PROMETHEE II contra un cálculo a mano de Brans & Vincke; TOPSIS contra TOPSIS clásico calculado en el test sobre los datos del caza de Hwang & Yoon. **Ningún valor es citado de una tabla**: agy había atribuido a Saaty 1990 y a Hwang & Yoon p. 101 valores que no pudo respaldar, y el «ranking publicado» de TOPSIS no era el que da el método — se reemplazaron por cálculos independientes #qa

- [x] 🧭 **Corrección del núcleo (2026-10-02, hecho con `agy` y revisado)**: TOPSIS ya no invierte con criterios negativos; el veto se aplica antes de rankear; ruina «no aplicable» en vez de 0 medido; `seed` en `MonteCarloEngine` (cada `run()` parte de ella y queda en la traza); Minimax Regret por percentiles; bootstrap ordena (a,b,c); `weight_shock_worst`; NaN/Inf y fallos de muestreo lanzan; Borda promedia lo no rankeado; PROMETHEE crisp normalizado; `winner_agreement` en el resultado. 15 tests nuevos, todos con control negativo #core

- [x] 💨 **Humo de los 37 análisis** (2026-10-02): `uv run pytest -m smoke`, paso propio en CI. Lee la traza del motor (`DM_MC_TRACE`): cada análisis tiene que haberlo corrido, puntuado al menos una opción y distinguido entre ellas. Su primera versión miraba los JSON de reporte y el control negativo la dejó en verde; la segunda falla exactamente en los cinco análisis rotos #qa

- [x] 🚨 **Modelo vacío o incompleto ya no puntúa en silencio** (2026-10-02): `MonteCarloEngine` lanza sin opciones, sin factores o con un factor sin variable. La capa legacy `DecisionAnalysisEngine` registra las opciones y puntúa con los pesos del motor original (`CAREER_FACTORS`); los cinco análisis y `ip_config_strategy`, que comparaban 0.0 contra 0.0, dan ahora puntajes distintos. Resultados anteriores de esos seis: nulos #bug

- [x] 🤖 **Backend `agy` para la IA** (2026-10-01): sin `GEMINI_API_KEY` responde el CLI de Antigravity, en modo plan y sandbox. `DM_LLM_BACKEND=auto|api|agy`; la suite nunca llega a un LLM real ([[guide]]) #enhancement
- [x] 📶 **FSK v2** (2026-10-01): los dos análisis se caían al importar y su Monte Carlo no registraba factores. Reescritos sobre su propia tabla de puntajes; el ganador del MC coincide con la suma ponderada y un test lo exige ([[decision-analyses]]) #analyses
- [x] 🛰️ **CI vuelve a correr en push** (2026-10-01): filtraba por `master`, que ya no existe #infra
- [x] 🧷 **Fuga de `factor_stats` con test de regresión** y penalización de cola que ya no premia puntajes negativos (2026-10-01) #quant

- [x] 🏷️ **v3.1 publicada (2026-08-23)**: la card «Preparación de v3.1» seguía en curso después del release. La inferencia empírica automatizada que nombraba no entró en v3.1; vive en el Backlog como **AI-Powered Parameter Estimation** #quant
- [x] 🦀 **Quitar `ndarray` de `rust_core/Cargo.toml`**: hecho. Se quitó la dependencia, el `Cargo.lock` la perdió (y con ella `num-complex`, `num-integer` y `rawpointer`), y los tres anuncios del stack que la nombraban. `cargo check` verificado con el Python del venv #rust #p3
- [x] 🗑️ **mkdocs retirado**: existía un `mkdocs.yml` en la raíz desde el commit `3279d14` (31-Jul-2026, la fase "God-Mode"), un template genérico que nunca se usó. Ningún session-log lo mencionaba, no estaba en CI ni instalado, y **nunca funcionó**: la línea 27 tenía un `:` sin comillas, así que `mkdocs build` abortaba en el YAML. Arreglado y medido, el veredicto fue retirarlo: no puede leer los 512 `[[wikilinks]]` del vault sin plugin, es ciego fuera de `docs_dir` (41 de sus warnings), su nav cubría 4 de 54 notas, y el repo ya es un vault de Obsidian con cuatro checkers encima. Se borraron `mkdocs.yml`, el extra `docs` de `pyproject.toml` y su ratchet. Si algún día hace falta sitio web, se genera desde el vault, no se mantiene un segundo árbol #docs #p3
- [x] 🧪 **Correr los checkers documentales en el harness**: antes sólo se ejecutaban en CI, así que una suite 100% verde no decía nada de si un checker funcionaba. Ahora `test_checkers_run.py` los corre como subprocesos y verifica su código de salida. Medido: 10 tests pasan, y con una sonda `sys.exit(3)` en `check_docs_links.py` el test falla nombrando el checker y su salida #qa #p2
- [x] 🧾 **Piso de Python alineado**: `AGENTS.md` decía Python 3.12+ y `pyproject.toml` exige `>=3.11`; canónico el declarado, porque es lo que la CI prueba en su celda más baja. `AGENTS.md` ahora dice 3.11+, y un test compara ambos #docs #p3
- [x] 🔗 **Enlaces rotos preexistentes**: eran 13 y quedaban etiquetados en bloque como "no existen en ningún lado". Al medir uno por uno, dos eran falsos: `./docs/architecture.md` y `./docs/index.md` desde `docs/reorganization/` tienen destino real un nivel arriba, así que se corregieron a `../`. Los 9 que quedan sí son del plan nunca ejecutado y ahora cada uno tiene la razón que le corresponde, con `./python/scripts/` separado del resto porque es un directorio inexistente y no un documento del árbol fantasma #docs #p3
- [x] 🔒 **Versionar `uv.lock` y alinear el install de CI con el local**: las 20 dependencias tenían cota inferior y ninguna superior, y local usaba `uv` contra CI `pip`, sin fuente de verdad común — los pins existían (623 KB) y el repo los descartaba. Resuelto: `uv.lock` versionado, el extra `dev` referencia a `test` en vez de copiar sus 6 líneas, y CI usa `uv sync --frozen --extra dev`, que falla si el lock no corresponde a `pyproject.toml`. Los 7 comandos de CI verificados en local #deps #p1
- [x] 🔢 **Hacer derivable el conteo de motores**: la premisa de esta card era falsa — decía que no existía registro en el código, y `AdaptiveRouter` ya particionaba los motores en tres niveles. Lo que sí era cierto es que las tres listas vivían escritas a mano, así que el número no derivaba de nada: el docstring decía 24, tres notas decían 24, y las rutas sumaban 19. Hoy las tres notas dicen 19 motores ruteables y el test lo lee de `ENGINE_UNIVERSE` en vez de comparar las tres entre sí. Ahora `ENGINE_UNIVERSE` y `ROUTES` son la fuente única, `_simple/_moderate/_advanced_engines()` leen de ahí y `all_engines()` devuelve el número. Ruteo verificado idéntico contra la versión previa, salida incluida. La tabla `### Engines` de `architecture.md` ya no se presenta como el conteo: faltaban tres motores ruteables en ella (GameTheory, ROA, MLSurrogate) y 18 de sus filas son módulos de análisis o presentación que el router nunca despacha. La pregunta sobre `Genetic` quedó en su propia card en Por Hacer #docs #p2
- [x] 🗄️ **Formateo de Documentación como Base de Datos**: propiedades YAML enriquecidas (`id`, `type`, `category`, `status`, `related`) para Dataview y Obsidian #database
- [x] 📊 **Creación de Centro de Base de Datos**: [[database-hub]] con consultas Dataview y tablas Markdown para navegación relacional #database
- [x] 📈 **Catálogo Exhaustivo de Resultados**: [[results-catalog]] documentando los lotes de simulación y su nomenclatura (reportes, JSON y visualizaciones) #database
- [x] 🔬 **Catálogo Completo de Análisis y Scripts**: [[decision-analyses]] integrando 37 análisis operativos, 7 scripts utilitarios y 3 ejemplos #database
- [x] 📦 **Auditoría e Indexación de Documentación Legacy y Raíz**: [[legacy-docs]] con los 10 documentos históricos de `archive/legacy/` y archivos raíz #database
- [x] 🔗 **Interconexión Total del Grafo**: enlazado bidireccional entre módulos cuantitativos, guías, arquitectura, roadmap y resultados #graph
- [x] 🔬 **Auditoría granular de fidelidad por sección**: la resolución de clases pasó a ser por sección y no por unión de la nota, con un caso de dos módulos como prueba; único dueño por módulo verificado en tres canales (heading, frontmatter y registro) #qa
- [x] 🚧 **Conflicto de proprietarios resuelto**: `robust.py` y `bootstrap.py` tenían dos notas dueñas cada uno con contenido incompatible; se movió el contenido verificado al dueño que designa el registro y el otro quedó como puntero #docs
- [x] 🗑️ **Un solo vault, sin `.obsidian` en la raíz**: había dos copias byte-idénticas de 1.1 MB, y la de la raíz convertía todo el repositorio en vault al abrirlo; se borró con respaldo y se añadió a `.gitignore` #vault
- [x] 📜 **Schema reescrito desde medición**: la tabla de campos, los cuatro ejes de tags y las cifras reales del vault, con ratchet que ata prosa, tabla y notas en las tres direcciones #docs
- [x] 🧬 **Regla de corrupción de alfabeto**: detecta cirílico o chino pegados dentro de una palabra, con dos controles negativos que además exigen **no** marcar `σ` ni `Σ`, que son notación legítima #qa
- [x] 🧹 **`ruff` limpio en todo el repo, no sólo en `src/decision_maker`**: 115 hallazgos, 96 por autofix y 19 a mano. Entre ellos dos que eran bugs: un `open()` sin context manager que perdía el archivo, y `zip()` sin `strict=` que truncaba en silencio. Las migraciones de `alembic/versions` quedan excluidas con el motivo escrito: son el registro congelado de lo que ya corrió contra una base real #qa
- [x] 🧪 **Suite de pruebas documentales**: 24 tests nuevos que hacen fallar la fidelidad y el schema, en lugar de depender de que alguien ejecute los scripts a mano #qa
- [x] 🔗 **Validación de Enlaces de Grafo**: 587 enlaces vivos, 578 resueltos y 9 rotos documentados como preexistentes, sin ninguno nuevo (medido 2026-10-01), mediante `scripts/check_docs_links.py` #qa
- [x] 🌐 **Validación de Consistencia Lingüística**: 0 intrusos léxicos y 0 alfabetos foráneos pegados, verificado mediante `scripts/check_obsidian_language.py` #qa
- [x] 🎯 **Validación de Fidelidad de Código**: 54 notas, 25 módulos, 45 clases, 25 imports, 25 propietarios y 219 literales `.py` verificados (medido 2026-10-01) con AST mediante `scripts/check_obsidian_fidelity.py` #qa
- [x] ⚡ **Suite de Pruebas Unitarias**: validación de 617 tests pasando con `uv run pytest`, más el humo de todos los análisis con `uv run pytest -m smoke` #qa
- [x] 🏗️ **Unificación del Vault**: raíz de Obsidian consolidada en `docs/`, con la configuración del vault bajo control de versiones y el plugin `obsidian-kanban` #vault
- [x] 🏷️ **Normalización de Nombres**: convención uniforme `lowercase-with-hyphens` y 100% de aliases resueltos #naming
- [x] 🚀 **19 Motores Ruteables** (fuente: `ENGINE_UNIVERSE` en `core/adaptive_router.py`): implementación de Monte Carlo, Fuzzy TOPSIS, PROMETHEE, Barbell/Antifragile, Bayesian, etc. #core
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
