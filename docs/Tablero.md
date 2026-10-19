---
aliases: [Tablero, Kanban, kanban, Tablero Kanban, Project Kanban]
tags: [kanban, lumina, quant, project-management, archive]
kanban-plugin: basic
proyecto_gestion: []
id: KANBAN-REPO
title: "Tablero Kanban de Decision Maker"
type: kanban
category: project-management
status: active
related: ["[[decision-maker-moc]]", "[[bitacora]]", "[[index]]", "[[roadmap]]"]
created: 2026-09-27
updated: 2026-10-18
---

# 📋 Tablero Kanban: Decision Maker Framework

Qué falta, en el plugin **Obsidian Kanban**. El porqué de lo hecho va en la [[bitacora]], un archivo por día. Mismo nombre y lugar (`docs/Tablero.md`) que en los demás repositorios; `proyecto_gestion` queda vacío hasta que este repo tenga proyecto en el Sistema de Gestión I+D.

Criterios para priorizar desde el 18-Oct-2026: **simplicidad** (menos motores, mejor validados), **escalabilidad** (vectorizado, sin estado oculto) y **conectividad** (formatos planos con esquema que otros repos y plataformas puedan leer).

## 🤔 Por Decidir

Sin decisiones abiertas: las cuatro del 18-Oct se resolvieron con el criterio «profesional y simple» que pidió el dueño (ver Completado).


## 📋 Backlog (Hojas de Ruta / v3.1+)

- [ ] 🤖 **AI-Powered Parameter Estimation**: `add_variable("Price", DistributionType.AI_FETCH)` con integración Gemini para inferencia empírica #enhancement #p2
- [ ] ⚖️ **Interactive AHP CLI Wizard**: asistente interactivo en terminal para matrices de comparación por pares con [[ahp]] #cli #p2
- [ ] 📉 **Funciones de Utilidad Dinámica**: soporte para rendimientos decrecientes y curvas sigmoidales en [[data-models-and-schemas]] #quant #p3
- [ ] 📊 **Suite Interactiva de Visualización**: migración de gráficos estáticos a Plotly interactivo en [[reporting-and-registry]] #viz #p2
- [ ] 🐳 **Despliegue con Docker**: contenedorización para API FastAPI y dashboard Streamlit con `docker-compose` #infra #p2

## 📌 Por Hacer / En Cola (To Do)

- [ ] 🗄️ **Cuatro almacenes**: `registry.py` (SQLite directo), SQLModel + Alembic (API), JSONL en `results/` y el ledger. Unificar con migración; es el último porque toca datos guardados #process #p3
- [ ] 🧪 **11 análisis con motor casero** (`NO_ENGINE` en `test_analyses_smoke.py`): migrarlos al motor común o archivarlos; hoy el humo sólo prueba que corren #analyses #p2
- [ ] 🦀 **`rust_core/` se compila en cada CI sin usarse**: el ADR 001 lo conserva, pero el build backend `maturin` obliga al toolchain de Rust para instalar el paquete. Opción: backend puro Python y el crate como extra opcional. Toca el ADR #infra #p3
- [ ] ⚖️ **Ponderación por recorrido en los análisis existentes**: la plantilla ya pregunta por recorrido (`swing_weights`) y la corrida avisa cuando una diferencia menor al 5 % recibe el peso entero; los 43 análisis viejos siguen con pesos tipeados. Revisarlos uno por uno cuando se reabran #analyses #p2
- [ ] 📒 **Registrar las primeras decisiones reales en el ledger**: el mecanismo existe desde el 18-Oct (`decision-maker decide/review/close/calibration`); faltan los datos. Empezar por la línea base del diagnóstico remoto y el piloto Nexa. Con ~20 decisiones cerradas el Brier empieza a decir algo #process #p1
- [ ] 📈 **Funciones de valor por criterio (MAVT)**: el modelo sigue siendo aditivo y lineal en el valor normalizado. Una función por criterio —saturación, umbral, aversión al riesgo— fijada por el decisor quita además el rank reversal del min-max. Antes de implementarlo, spec aprobada #quant #p1
- [ ] 🎯 **Elicitación p10/p90 con chequeo de sobreconfianza**: hoy los rangos se tipean a mano. Pedir p10/p90, ajustar PERT o lognormal, y mostrar cuánto se ensancha si el experto es tan sobreconfiado como la media #quant #p2
- [ ] 🖼️ **Mostrar `weight_robustness` en el reporte HTML y en el dashboard Streamlit**: hoy sólo está en el resultado y en la plantilla #viz #p2
- [ ] 📝 **Notas de módulo para `config_runner.py` y el resto sin dueño**: falta nota dueña (`module:`) para 38 de los 59 módulos de `core/` (medido 2026-10-01). De los de primera clase en el pipeline `standard` sólo falta `config_runner.py` #docs #p3
- [ ] 🧩 **`analyses/research/samba_performance_strategy.py` no corre**: migración a medias — construye `UnifiedDecisionFramework(debug=...)` y llama `analyze_option`, que el framework no tiene. Su propio docstring ya dice que hay que reescribirlo #analyses #p3
- [ ] 🕳️ **Punto ciego del humo: 11 análisis con motor propio** (`NO_ENGINE` en `test_analyses_smoke.py`): para los que tienen TOPSIS/MC propio en numpy, el humo sólo prueba que corren, no que distingan opciones. Migrarlos al framework o darles su propia aserción #qa #p3
- [ ] ✏️ **`samba`/`commandmessage`/varios declaran metodologías que no aplican**: se corrigió la tabla de [[decision-analyses]], pero los docstrings de varios scripts siguen prometiendo «13 metodologías» o Monte Carlo sin usarlo #docs #p3
- [ ] 📶 **`process_utility_analysis.py` no lee la investigación que dice reinterpretar**: `json.load(f)` sin asignar; el análisis está escrito a mano. Reescribirlo sobre `power_supply_research_results.json` o declararlo como plantilla #analyses #p2
- [ ] ⚠️ **`pymcdm.methods.PROMETHEE_II` agota su generador interno de funciones de preferencia tras una corrida**: cuando se inicializa con listas de parámetros ($p$, $q$), `self.pfs` se almacena como una expresión generadora que se consume en la primera invocación. Llamar a la misma instancia por segunda vez lanza `IndexError: axis 1 is out of bounds`. Cualquier wrapper o benchmark debe instanciar un nuevo `PROMETHEE_II` por corrida o convertir `pfs` a tupla #deps #qa #p3
- [ ] 🔁 **Puntaje relativo y rank reversal**: el puntaje es min-max sobre las opciones de la corrida, así que agregar una opción puede reordenar las demás. **Confirmado y medido con `hypothesis` en `test_properties.py` (`test_rank_reversal_topsis_with_dominated_third_option`)**: con $w=[0.25, 0.75]$, $A=[1.0, 7.0]$ y $B=[2.0, 6.0]$, $A$ gana inicialmente ($0.75 > 0.25$); al introducir $C=[0.0, 0.0]$ estrictamente dominada por ambas, el rango se expande de forma no uniforme y $B$ pasa a ganar ($0.8929 > 0.8750$). Evaluar funciones de valor por criterio fijadas por el decisor para evitar distorsión relativa #quant #p2
- [ ] 📐 **EVPPI sesgado hacia arriba con N chico**: el máximo de medias por bin con ruido supera el de las medias verdaderas. Medido con un factor de riesgo que no cambia la decisión: hasta 0,7 % de la media del ganador con N=1.000 y 0 con N=10.000. Corregirlo (p. ej. restar el EVPPI de un driver permutado) o exigir N mínimo; tampoco se hizo EVSI (información muestral) #quant #p3
- [ ] 📦 **Publicar en PyPI con versión etiquetada**: la versión ya tiene una sola fuente (`pyproject.toml`, y `test_readme_version_matches_pyproject` ata el README); faltan los tags de git (`v3.1.0`) #infra #p3
- [ ] 🧮 **La compuerta de ruina decide «no aplicable» por el rango de los puntajes, no por `normalize`**: con `normalize=False` y todos los puntajes en [0, 1] también dice «no aplicable» (correcto en el resultado, ninguno puede bajar de 0, pero por inferencia). Pasarle el flag explícito #quant #p3
- [ ] 📏 **`sqm_santiago`/`furniture_diy` siguen cortando en 5.0 y 3.5**: el texto ya dice «posición relativa», pero los umbrales absolutos sobre un puntaje min-max no significan nada. Quitarlos o ranquear #analyses #p3
- [ ] 🔬 **Correr los `power_supply_*` con `agy`**: ya no necesitan API key, pero no se corrieron enteros (~25 s por consulta). Los dos `process_*` leen los datasets que ellos generan, así que van después #analyses #p2
- [ ] 📡 **Cerrar la decisión de línea base del diagnóstico remoto**: E gana, pero (a) la fecha de ID-1476 decide entre E y D (escenario S4 en empate), (b) S6 sin verificar: si los arreglos que le faltan a v4.2.0 importan en un VHF de campo, (c) S2: clientes instalados por línea. Fijar semilla para que S4 sea reproducible #analyses #p1
- [ ] ♻️ **Re-correr lo que usó datos por factor entre 2026-08-23 y 2026-09-29**: `factor_stats`/`raw_factor_data` eran los de la última opción. Sólo afecta reportes de sensibilidad, explicabilidad, antifrágil o genético; los rankings están sanos ([[results-catalog]]) #analyses #p2
- [ ] 🌿 **Rama por defecto de GitHub en `main`**: se sincronizó `improve-computer-decision` con `main` (mismo HEAD). La cuenta de `gh` (`arturoSigmadev`) tiene push pero no admin; cambiar la default branch a `main` en Settings → Default branch de GitHub cuando sea conveniente #infra #p2
- [ ] 🧱 **`commandmessage_*` fallan en un clon limpio**: escriben en `results/` sin crearlo. Y los `sniffertelemetry` v1–v4 comparten nombres de opción, así que sus `analysis_*.json` genéricos no se distinguen #analyses #p3
- [ ] 🔍 **Huecos que quedan en los checkers**: anclas `#...` no se verifican; `check_obsidian_language.py` detecta archivo con una ventana de 400 caracteres y no saca fences `~~~`; `dev_agents_linter.py` indexa UX-01 por nombre de función y dos métodos homónimos se pisan #qa #p3
- [ ] 📝 **Documentar módulos auxiliares restantes**: crear notas para submódulos de soporte secundario en `src/decision_maker/core/` (como `config_runner.py`, `jsonl_store.py`) #docs #p3

## 🚧 En Curso (In Progress)

Sin tarjetas.

## 🔍 En Revisión & QA (Review)

Sin tarjetas.

## ✅ Completado (Done)

- [x] 🧩 **Un solo transporte de LLM** (2026-10-18): `gemini_helper.ask_llm` decide API o `agy` en un único lugar (`select_backend`); `GeminiDeepResearchAgent` delega en él en vez de tener su copia, y la segunda clase con el mismo nombre en el adaptador legacy se eliminó. `devils_advocate` queda: es un consumidor, no un transporte #core
- [x] 💼 **`CareerOption` se queda como adaptador, recortado** (2026-10-18): 4 análisis activos corren sobre él y retirarlo es reescribir el modelo de cada uno en sus términos técnicos —un cambio de modelado por análisis—. Se le quitó lo muerto (`_calculate_overall_score`) y lo duplicado; su encabezado dice que es legacy y que lo nuevo usa `DecisionOption`. Cada análisis migra cuando se reabra #analyses
- [x] 🧹 **Limpieza del 18-Oct, segunda tanda** (2026-10-18): 6 versiones superadas de análisis a `analyses/archive/` (sniffer v1–v3, minería v1, dos de CommandMessage); 12 notas históricas, `archive/`, Jira y el roadmap duplicado retirados del repo (recuperables desde `0aecd52`, índice en [[legacy-docs]]); el análisis de power supply de la raíz movido junto a su investigación; un solo roadmap ([[roadmap]]) #docs
- [x] 🪶 **`seaborn` eliminado** (2026-10-18): lo usaban 4 llamadas de gráficos, reemplazadas por matplotlib + scipy. `scikit-learn` se queda: lo usan 3 motores experimentales y volverlo opcional agregaba ramas; se resuelve al podar esos motores #infra
- [x] 🎲 **Semilla fija por defecto** (2026-10-18): `MonteCarloEngine` usa `DEFAULT_SEED`; mismo modelo, mismos números. `seed=None` explícito para azar real #quant
- [x] 🏷️ **Sin nombres de marketing** (2026-10-18): `_add_god_mode_metrics` → `_add_advanced_engine_metrics`; la API se llama «Decision Maker API» #core
- [x] 📐 **TOPSIS queda como segunda opinión** (2026-10-18): la matemática no cambia; la recomendación de los reportes pasa a ser la del Monte Carlo, igual que `commitment_draft`. Antes el reporte recomendaba al ganador de TOPSIS y el borrador al del Monte Carlo: una misma corrida podía recomendar dos opciones distintas ([[topsis]]) #quant
- [x] 🏷️ **Motores experimentales: etiquetados, no ocultos** (2026-10-18): ocultarlos rompía las claves que leen los 44 análisis. Cada sección del reporte lleva la madurez de su motor (`validated`, `characterized`, `experimental`), leída de `engine_maturity.py` #quant
- [x] ✂️ **Penalización de cola retirada** (2026-10-18): recortaba el 5 % peor de cada opción, que toda opción tiene, así que no medía ruina. Antes y después en los 44 análisis: 0 ganadores cambiados más allá del ruido de semilla. El riesgo de cola queda en `cvar_95` y la ruina real en [[decision-gates]] con umbral explícito #quant
- [x] 🧬 **Genetic en la ruta `advanced`** (2026-10-18): el modo fijo lo corría y el router automático no; ahora coinciden, con test y control negativo #core
- [x] 🚨 **Advertencia falsa de escala reemplazada** (2026-10-18): «Scale mismatch» comparaba magnitudes crudas que la normalización ya anula y saltaba en casi todos los análisis. Ahora avisa lo que sí importa: una diferencia menor al 5 % entre opciones que igual recibe el peso entero (`_check_range_amplification`, 3 tests con control negativo) #quant
- [x] 🎚️ **La plantilla pondera por recorrido** (2026-10-18): `SWING` con la pregunta «¿qué factor moverías primero de su peor a su mejor valor?» y `WeightDerivationEngine.swing_weights` #analyses
- [x] 🧾 **Los tests ya no escriben en `results/`** (2026-10-18): `DM_RESULTS_DIR` para los almacenes y reportes; verificado por el efecto, la suite completa deja los tres JSONL idénticos byte a byte #qa
- [x] 🌐 **API del ledger** (2026-10-18): `GET /ledger?status=all|open|due|closed` y `GET /ledger/calibration`, sólo lectura. La API escucha en `127.0.0.1` por defecto: no tiene auth y el ledger guarda decisiones personales #api
- [x] 🧭 **Ledger de decisiones: una corrida ya no compromete nada** (2026-10-18): `core/decision_commitment.py` exige fecha de revisión ISO futura, una métrica observable (rechaza `mean_score`, `p95`…: el modelo no puede calificarse a sí mismo) y confianza en (0, 1]. El orquestador devuelve `commitment_draft`; el compromiso lo registra una persona con `decision-maker decide`. `review`, `close` y `calibration` (Brier/ECE sobre decisiones cerradas) en `ledger_cli.py`. Archivo versionado `decisions/ledger.jsonl` ([[decision-ledger]]) #process #core
- [x] ⚖️ **Robustez ante los pesos** (2026-10-18): `core/weight_robustness.py`, en modo `standard`. Cada sorteo del Monte Carlo lleva su propio vector de pesos: lectura informada (Dirichlet alrededor de los pesos declarados) y sin información (uniforme). Validada contra la cola de una Beta en forma cerrada; control negativo hecho ([[weight-robustness]]) #quant #core
- [x] 🔗 **La correlación nunca funcionó, y fallaba en silencio** (2026-10-18): la permutación de Iman-Conover estaba invertida (ρ=0,8 pedido daba Spearman 0,003), y una matriz de forma equivocada, asimétrica o no definida positiva se ignoraba con un warning. Ahora se aplica (test mide Spearman 0,786) y lo inválido lanza `ValueError` #quant #core
- [x] ↩️ **Regret invertido** (2026-10-18): `OutcomeTracker` daba regret 0 en cada fallo; el test `>= 0.0` no podía fallar. Corregido con el valor fijado #core #qa
- [x] 📦 **Análisis fuera del paquete** (2026-10-18): los 44 análisis a `analyses/` y los 7 scripts a `analyses/research/`; hacks de `sys.path` quitados, dos imports rotos reparados, `metadata.json` retirado (cubría 5 de 37 y lo reemplaza la tabla de [[decision-analyses]], que tiene ratchet). `test_analyses_imports.py` verifica cada import con control negativo #analyses
- [x] 🏷️ **Versión con una sola fuente** (2026-10-18): `pyproject.toml` 3.1.0, atado al README por test #infra
- [x] 📊 **Distribución PERT** (2026-10-18): `[mín, más probable, máx]`, para costos y plazos; la plantilla deja de modelar costos con una normal que admite negativos #quant
- [x] 🔐 **El ledger se versiona en este repo** (2026-10-18, decidido por el dueño): el repo es privado y de un solo dueño. Lo que lo cambiaría: que alguien más lo clone; entonces `DM_LEDGER_PATH` a un repo privado #process
- [x] 🗑️ **Dashboard React borrado** (2026-10-18, decidido por el dueño): era la plantilla de Vite con un payload de demo fijo; queda Streamlit (`src/decision_maker/dashboard/app.py`) como única interfaz web #infra
- [x] 🧷 **mypy como mecanismo y `orchestrator.py` bajo 500 líneas** (2026-10-18): 82 → 0 errores, paso en CI; 685 → 494 líneas con `orchestrator_steps.py`. Destapó 4 defectos reales: REPL de what-if, barbell con empates, **vía negativa que nunca quitaba factores** y probabilidades bayesianas contaminadas por el grafo causal ([[bitacora]]) #qa #core
- [x] 🔌 **Esquema publicado del ledger y `--json`** (2026-10-18): `decisions/ledger.schema.json` con conformidad contra el productor; `review --json`, `calibration --json` #api
- [x] 🗂️ **Tablero y bitácora con la convención de los demás repos** (2026-10-18): `docs/Tablero.md` y `docs/bitacora/AAAA-MM-DD.md`; el worklog único se dividió por fecha sin reescribir el contenido #docs

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
