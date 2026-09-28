---
aliases: [Decision Maker Worklog, Worklog, Decision_Maker_Worklog]
tags: [worklog, lumina, quant]
kanban-plugin: board
id: WORKLOG-DM
title: "Decision Maker Worklog"
type: worklog
category: project-management
status: active
related: ["[[kanban]]", "[[decision-maker-moc]]", "[[database-hub]]", "[[index]]"]
created: 2026-08-10
updated: 2026-09-27
---

## Decision Maker Worklog

## Hecho

- [x] Auditar `docs/` con 4 agentes de límites negativos disjuntos (taxonomía / cuerpo / links / fidelidad)
- [x] Verificar a mano cada hallazgo Critical/High contra el código
- [x] Reescribir [[monte-carlo-engine]], [[antifragile-engine]] y [[bayesian-inference-engine]] contra la implementación real
- [x] Reparar 3 clases inexistentes: `AntifragileAnalyzer`→`AntifragileEngine`, `RobustnessAnalyzer`→`RobustOptimizer`, `BootstrapSimulator`→`BootstrapRanking`
- [x] Reparar 2 imports falsos: `AHPEngine`→`AHPHelper`, `validate_config`→`config_runner`
- [x] 9 placeholders `[What it does]` rellenados
- [x] 17 bullets `Sin docstring` sustituidos por el rol real de cada clase
- [x] Header de 3 líneas: 3 párrafos de blockquote separados, ya no se renderizan como uno
- [x] Tag `component` eliminado de 12 notas (no distinguía nada); `lumina`/`quant` en las 15
- [x] `---` final colgante eliminado de 12 notas
- [x] 6 wikilinks del MOC reparados; los 3 de personas pasan a texto plano
- [x] `docs/index.md`: `ARCHITECTURE.md`→`architecture.md`, `jira/DM-25.md`→`../jira/DM-25.md`
- [x] Enlace al vault desde `docs/index.md` — las 15 notas quedan alcanzables
- [x] ADR 001 + `architecture.md` + `index.md` reconciliados con el estado real de Rust
- [x] `[[note-schema]]`: esqueleto canónico, 4 ejes de tags, regla de idioma
- [x] Vault Obsidian en `docs/.obsidian/` + plugin Kanban 2.0.51
- [x] 3 checks de docs, con control negativo, conectados a CI

### Reorganización de nombres y raíz del vault (27-Sep-2026)

- [x] **Raíz del vault movida de `docs/obsidian/` a `docs/`.** Motivo: con la raíz en `docs/obsidian/`, `index.md`, `architecture.md`, `guide.md`, `adr/` y `reorganization/` quedaban fuera del grafo y ningún wikilink podía alcanzarlos. Verificado que `docs/` no contiene `results/`, `.venv/` ni generados.
- [x] **Los 15 módulos de nota movidos a la raíz de `docs/`.**
- [x] **Convención única `lowercase-with-hyphens`** en los 54 archivos (única excepción: `README.md`). UPPER_SNAKE restante: ninguno.
- [x] **`docs/docs/sw-diagnosticoremoto/` aplanado** a `docs/sw-diagnosticoremoto/` — un `docs` dentro de `docs` era ruido de layout heredado del repo hermano.
- [x] **Back-compat de aliases completo**: los 15 nombres viejos (con `_` y con mayúsculas) resuelven otra vez, 15/15.
- [x] **Alcanzabilidad 54/54** desde `[[decision-maker-moc]]` y desde `[[index]]`, verificate por grafo. Sin huérfanas.
- [x] **3 instrumentos reparados** — cada uno daba verde sin medir:
  - `KNOWN_BROKEN` era por archivo, no por target: un link roto nuevo en `reorganization/` quedaba enmascarado para siempre. Ahora es por target exacto.
  - `is_archive` comparaba por substring: `tags: [archive-2024-review]` excluía una nota viva por accidente. Ahora compara el tag entero.
  - `VAULT` de los 3 checks apuntaba a `docs/obsidian` (inexistente) y usaba `glob` no recursivo: medían 0 notas y salían rojos. Ahora `docs/` con `rglob` → 54 notas.
- [x] **`index.md:67` corregido**: decía que `normalize=True` usa los bounds de `rust_core`. Falso — `monte_carlo.py:112-121` los calcula en Python, y la línea 12 del mismo archivo decía lo contrario.
- [x] **`guide.md` corregido**: apuntaba a `config/decision_config.yaml`, que no existe; el archivo real es `src/decision_maker/config/decision_config.yaml`.
- [x] **Links muertos fuera de `docs/`**: `README.md` → `docs/INDEX.md` y `docs/ARCHITECTURE.md`; `mkdocs.yml` → `ARCHITECTURE.md`; `README_POWER_SUPPLY_DECISION.md` → `docs/docs/…`.

## Auditoría de arquitectura — 28-Sep-2026

Una revisión estructural encontró cinco defectos Alta. Todos corregidos, y dos de ellos	maximizaron el alcance de lo que había que arreglar.

- [x] **El pool de clases del checker de fidelidad era la unión de la nota, no de la sección.** Una nota de un solo módulo detectaba una clase mal atribuida; una nota de dos módulos pasaba limpio. Cuatro notas declaran ≥2 módulos, o sea justo la forma donde se abría. Ahora la resolución es por sección, y `test_docs_fidelity.py` lo prueba con un caso de dos módulos.
- [x] **El defecto ya había explotado: `robust.py` tenía dos dueños** con contenido incompatible. `robust-optimization.md` decía "min-max **regret** rankings"; `regret` no aparece en `robust.py` (0 ocurrencias, verificado). El registro de [[database-hub]] señalaba a `robust-optimization` como dueño, así que el contenido verificado de [[antifragile-engine]] se movió allí y antifragile quedó con un puntero. Lo mismo con `bootstrap.py` / `bootstrap-ranking.md` contra [[monte-carlo-engine]].
- [x] **Un módulo, un dueño, verificado en tres canales**: heading `## \`modulo.py\``, frontmatter `module:` y fila del registro en [[database-hub]]. Los tres tienen que concordar; si no, falla. Esto no existía como invariante y es lo que dejó pasar los dos conflictos.
- [x] **Había dos `.obsidian/` byte-idénticos de 1.1 MB**, uno en la raíz del repo y otro en `docs/`, y ninguno en `.gitignore`. El de la raíz es el peligroso: abrir el repo en Obsidian convertiría **todo el repositorio** en el vault, que es el problema exacto que motivó mover la raíz a `docs/`. Se borró, se añadió `/.obsidian/` al `.gitignore` y se ignoraron los archivos compilados de cada complemento conservando su `manifest.json`.
- [x] **El criterio de reversión de la decisión "raíz = `docs/`" se cumplía solo**: decía que cambiaría si aparecía contenido generado dentro de `docs/`, y `.obsidian/` es exactamente eso. Redactado para excluir la metadata del vault, y la decisión pasó de prosa a `check_docs_scope.py`, que la puede fallar.
- [x] **La fila `MOD-AHP` del registro apuntaba a un nombre que no existe.** El archivo real es `core/ahp.py`; el nombre inventado no se escribe acá a propósito, porque el checker de fidelidad trata todo literal `.py` como una afirmación de que el archivo existe, y el nombre falso sería una afirmación falsa. Ese caso pasó a ser el claim 5.
- [x] **El schema declaraba 2 campos de frontmatter; hay 13 en uso**, y 44 de los 58 tags no estaban declarados. `note-schema.md` reescrito desde medición. El vocabulario de tags **no** se enumera: se declara la regla de los cuatro ejes y `test_docs_schema.py` fija los conteos, que se ponen rojos si cambian en cualquier dirección.
- [x] **`created` faltaba en 16 notas.** Rellenado: 10 desde el primer commit de git, 6 sin procedencia (fecha de entrada al vault, declarado como tal en el schema en vez de inventar precisión).
- [x] **Tres correcciones a la medición del propio informe**: la regex del registro no matcheaba `core/ahp.py` porque el slash no estaba en la clase, así que el tercer canal estaba muerto y no verificaba nada; la comparación registro-vs-nota daba 21 desacuerdos falsos por comparar un stem contra un filename; y el chequeo de `.gitignore` buscaba `/.obsidian/` como subcadena, que aparece dentro de `/docs/.obsidian/plugins/…`, así que reportaba presente una regla borrada. Los tres los detectó el control negativo, no la lectura.
- [x] **`aliases()` leía los primeros 400 caracteres del archivo**, no el bloque de frontmatter: trunca 9 de 54 frontmatters (hasta 453 chars), se metía en el cuerpo —donde `note-schema.md` tiene un `aliases:` dentro de un fence— y no parseaba la forma block-list de YAML. Ninguno fallaba hoy, pero un alias fantasma **hace resolver un enlace roto**, que es lo contrario de lo que el checker existe para hacer.
- [x] **La categoría `INERT` estaba en el docstring y en ningún otro lado.** El código nunca la emitía. Implementada: 6 strings con forma de enlace dentro de fences ahora se listan sin fallar, porque un ejemplo que se vuelve enlace real no lo nota nadie.
- [x] **El docstring del checker de idioma prometía una regla que ya no era cierta** ("fichas de módulo en inglés"). Las dos fichas que quedaban en inglés eran las dos que describían mal su módulo. Regla reescrita: el vault es mixto a propósito y lo que se vigila es la ausencia de intruders, no el idioma.
- [x] **Un token tenía letras de otro alfabeto pegadas dentro de una palabra española** —`мног`licriterio, en [[topsis]]— y el checker de idioma no lo veía, por una razón que vale la pena: el token corrupto no está ni en `ENGLISH` ni en `SPANISH`, así que la comparación de listas, que sólo puede atrapar palabras que conoce, lo deja pasar. Se agregó una regla para cirílico y chino pegados a una palabra, con **dos** controles negativos: tiene que marcar la sustitución que se coló y **no** marcar `σ` ni `Σ`, que son notación legítima en [[antifragile-engine]] y [[bayesian-inference-engine]]. La primera versión de la regla era demasiado ancha y los dos controles la rechazaron: señaló `σ` en la fórmula de fragilidad y `Σ` en `-Σ p ln p`, que son correctos. La segunda marcó `σa²`, donde el subíndice `a` es latino. Lo que separa la corrupción de la notación no es que se mezclen, sino que haya dos o más letras extranjeras en secuencia.

### Limpieza de `ruff` — todo el repo, no un directorio

- [x] **`ruff` quedó limpio en todo el repo**: 115 hallazgos, 96 por autofix y 19 a mano. CI pasó de `ruff check src/decision_maker` a `ruff check .`; con el comando anterior, "ruff pasa" era cierto para un directorio y no decía nada del resto.
- [x] **Dos de los 19 no eran estilo, eran bugs.** Uno: `json.dump({...}, open(out, "w"))` en `uqomm_adopcion_v6_leakyfeeder.py` dejaba el archivo abierto y dependía del GC de CPython para cerrarlo. Otro: `zip(confidences, correct)` sin `strict=` en `test_calibration_scorer.py` truncaba en silencio si las listas midieran distinto; los 9 call sites miden igual, así que hoy no ocultaba nada, y `strict=True` lo vuelve ruidoso si alguno deja de hacerlo.
- [x] **`np.random.seed(20260823)` estaba asignado a `rng`.** `seed()` devuelve `None`, así que `rng` valía `None`: el seed se aplicaba por efecto colateral y la variable era un `None` esperando a ser usado. Ruff lo marcó como `F841` y la lectura lo confirmó.
- [x] **`raise ... from None` en `registry.py` cambiaba comportamiento y no estaba cubierto**, así que se escribió el test. Escribirlo corrigió el supuesto del test: `from None` **no** borra `__context__`, pone `__cause__` en `None` y `__suppress_context__` en `True`. La aserción que yo tenía, de que el contexto quedara vacío, era un test que no podía pasar. Control negativo hecho: quitar el `from None` lo pone rojo.
- [x] **`alembic/versions` quedó excluido de ruff, con el motivo escrito en `pyproject.toml`.** Son migraciones ya aplicadas, el registro congelado de lo que corrió contra una base real; reescribirlas cambia historia que nadie puede reproducir. `alembic/env.py` sí se lintea, porque es un archivo vivo. Verificado que la exclusión es lo que silencia los 10 hallazgos: sin ella, `ruff check .` los reporta.
- [x] **`UP017` (6) es seguro aquí, verificado y no inferido**: el autofix convirtió `timezone.utc` en `datetime.UTC`, que existe desde 3.11. `pyproject.toml` declara `requires-python = ">=3.11"` y el runtime es 3.11.15.

### Lo que este trabajo NO verificó

- **Ninguno de los 4 checkers corre en el harness de tests.** Se ejecutan como scripts en CI. Un test que verifica que el archivo aparece en la salida de CI sigue sin existir.
- **De los enlaces rotos preexistentes, dos no estaban rotos.** Están documentados por target exacto en `KNOWN_BROKEN` porque apuntan a un árbol de documentación propuesto que nunca se ejecutó; reescribir los paths no arregla nada.
- **2 literales `.py` en notas `archive` no se verifican contra el árbol**: están en la bitácora de Dic-2025 y el checker los lista como NOTA, no como fallo, porque son afirmaciones sobre el pasado. Los nombres y las líneas están en la salida del propio checker, que es donde se leen; no se repiten acá porque un literal `.py` en esta nota se verifica contra el árbol actual.
- **El fix del `open()` con context manager no se ejecutó en runtime.** El script es de análisis, necesita red y asyncio, y la suite no lo cubre. Lo verificado es que el archivo compila y que el patrón es la equivalencia directa del original.
- **`AGENTS.md` decía "Python 3.12+" y `pyproject.toml` exige `>=3.11`.** Corregido a 3.11+, que es el piso que la CI prueba en su celda más baja. Ver abajo.

### Segunda ronda: cifras declaradas contra código medido

La ronda anterior verificó que las afirmaciones sobre el código fueran ciertas. Estas son las que hablan de **conteos**, que envejecen distinto: un literal `.py` queda viejo cuando el código se mueve, pero un total como "521 tests" queda viejo sin que nadie toque nada. Cuatro estaban mal:

- **`architecture.md` e `index.md` decían 495 tests; había 521.** Ahora 539, que es el total real con los seis tests de este ratchet y los diez de `test_checkers_run.py` incluidos. El número volvió a moverse en el mismo commit en que se escribió el test que lo vigila, que es exactamente lo que debería pasar.
- **`decision-analyses.md` decía 36 scripts y su propia tabla listaba 37 filas.** La 37 es `_template.py`, la plantilla canónica, que no es un análisis. El texto ahora lo dice en vez de dejar que la prosa y la tabla se contradigan.
- **`results-catalog.md` afirmaba que el repositorio registraba 295 archivos, en `results/`.** `results/` está en `.gitignore` con **cero** archivos versionados, así que ese número sólo podía reproducirlo la máquina que lo escribió — y ahora hay 2081 archivos ahí, porque las corridas siguieron. Dos claims más del mismo tipo aparecieron al escribir el detector: `improvement-analysis.md` ("17 archivos") y una mención de "~300 reportes" en [[note-schema]]. Los tres se reemplazaron por la regla de nomenclatura, que sí es reproducible. Nota sobre esta línea: el texto va redactado así a propósito. La primera redacción citaba el claim literal y el ratchet la marcó a sí mismo, porque no distingue entre afirmar un conteo y citar uno viejo. Se prefirió la regla simple y estricta antes que enseñarle al regex a reconocer el pasado.
- **Los 37 enlaces entrantes de [[database-hub]] no correspondían a ninguna métrica.** Medido: 28 notas distintas y 42 instancias.

#### Tres instrumentos que mentían, y uno de ellos era mío

El conteo de enlaces salía **27** por un script y **28** por `grep`. La diferencia era el script: usaba `p.name` como clave de diccionario, y el árbol tiene **dos** `README.md`, así que uno pisaba al otro. Con ruta completa los dos instrumentos dan 28 y coinciden. El mismo bug de basename estaba en el mensaje del detector de `results/`, que reportaba `improvement-analysis.md:84` para un archivo que vive en `docs/reorganization/`. La lección no es "usar grep": es que un número que dos instrumentos no coinciden no es un número, es el síntoma de que falta un control.

El primer detector de claims en `results/` tampoco servía: emparejaba un conteo con la mención de `results/` por **co-ocurrencia en la línea**, y marcó una frase que dice "los 54 archivos `.md` son todos documentación" y, tres cláusulas más, da `results/` como razón del cambio de raíz. Dos hechos ajenos compartiendo línea. Probé una ventana de ±60 caracteres y la siguió marcando, porque ajustar la distancia hasta que el falso positivo del propio instrumento desaparece es la forma de enseñarle a mirar para otro lado. Quedó con dos relaciones explícitas en vez de una distancia: `results/` seguido de cerca por un conteo, o un conteo unido a `results/` por *en*/*de*. "y no hay `results/`" no matchea ninguna de las dos, que es justo el objetivo.

#### Lo que el ratchet no puede verificar

`test_engine_count_is_consistent_across_notes` comprueba que `architecture.md`, `roadmap.md` y el kanban digan el mismo número de motores. **No comprueba que 24 sea cierto.** No existe registro de motores en el código: ni `ENGINES`, ni un `__all__` en `core/` que los enumere, y `core/` tiene 57 módulos de los que sólo un subconjunto son motores. El test es más débil a propósito y lo dice en su docstring. Queda en el kanban como pendiente de una lista explícita; cuando exista, el número se deriva en vez de repetirse en tres lugares.

Los seis tests tienen control negativo: se reintrodujo cada defecto uno por uno y los seis lo detectaron. El del conteo de tests sólo corre en la suite completa — con un path o un `-k`, `session.items` ya viene filtrado y el total no es comparable, así que skipea con el motivo escrito en vez de ponerse rojo por una razón que no tiene que ver con la documentación.

### Tercera ronda: qué se versiona, qué está muerto, qué resuelve el solver

Tres instrumentos nuevos. Los anteriores habían mirado lo que la documentación afirma; estos miraron lo que el repositorio *contiene* y lo que el solver *resuelve*.

**Ronda 1 — qué existe en disco y qué está en git.** Ningún `.py` sin versionar: el código no tiene trabajo invisible. Pero `.gitignore` ignora `uv.lock`, y ese archivo existe en disco con 623 KB de versiones resueltas. Nunca estuvo versionado —la regla se agregó en el commit de v3.0—, así que no es una regresión sino una decisión que nunca se revisó. Las consecuencias se miden en la ronda 3.

**Ronda 2 — código muerto, y un bug en el propio detector.** El instrumento enumeró **87** símbolos de primer nivel sin referenciar. Leídos uno por uno: 80 son clases `Test*` que pytest recolecta sin nombrarlas, 4 son handlers de FastAPI registrados por decorador, uno es un comando de Typer y otro un fixture `autouse=True`. Es decir, **cero código muerto** — y casi lo reporto como 87.

El near-miss importa más que el resultado. El detector nunca recursaba dentro de `ast.Attribute`, así que en una llamada encadenada como `_rank_scores(...).items()` veía el `.items` y cortaba el camino: la referencia interna era invisible. Marcaba como muerta una función con dos call sites vivos, y borrarla habría roto la preparación de la matriz de decisión. Reescrito con `ast.walk`, que es completo por construcción, el mismo detector baja de 87 a 6 —los 6 decorados de antes, todos falsos positivos.

Un conteo de 87 que resulta ser cero no es un audit con 87 hallazgos: es un detector roto. La diferencia entre los dos números es entera la información.

**Ronda 3 — qué resuelve el solver, y qué permite.** Las 20 dependencias declaradas tienen **cota inferior y ninguna superior**, CI instala con `pip install -e ".[test]"` sin lockfile, sin constraints y sin hashes. Con `uv.lock` ignorado, cada corrida de CI resuelve a la última versión publicada en ese momento. Un CI en verde no es reproducible desde el repositorio, y un release upstream puede romperlo sin que haya commit al que culpar: el fallo aparece en un commit que no lo tocó. Es la misma clase que el resto de esta auditoría —una confirmación que no se puede reproducir—, aplicada al pipeline. Local y CI además resuelven por mecanismos distintos: `uv` acá, `pip` allá, sin fuente de verdad común. Los pins existen; están en el disco y el repo los descarta.

Dos pendientes del kanban medidos en el camino, sin abrir nada nuevo: `ndarray = "0.15"` está declarado en `rust_core/Cargo.toml` y tiene **cero usos** en el único archivo `.rs` del crate, así que la dependencia está sin usar; y `mkdocs.yml` declara 4 entradas de navegación contra 54 notas, o sea 50 inalcanzables desde el nav del generador estático, aunque las 4 entradas apuntan a archivos reales.


### Cuarta ronda: el entorno que nadie estaba mirando

Las tres rondas anteriores_operandaron sobre el código. Esta se abrió porque
`cargo check` falló con un error que no era del código, y resultó ser el más
importante de los cuatro.

**La suite no se estaba corriendo en el entorno del proyecto.** `uv run pytest`
resolvía a `/home/arturo/.local/bin/pytest` — un Python 3.14.4 del
site-packages del usuario — porque `.venv/` se había creado sin el extra `test`
y por lo tanto sin `pytest`. Lo que se medía en las rondas anteriores era:

| | intérprete | numpy | scipy | pytest |
|---|---|---|---|---|
| **lo que se medía** | `/usr/bin/python3` 3.14.4 | 2.5.2 | 1.18.0 | 8.3.5 (global) |
| **el proyecto** | `.venv/bin/python` 3.11.15 | 2.4.6 | 1.17.1 | no estaba instalado |

O sea, tres entornos distintos: el que se testeaba, el que declara `pyproject.toml`
y el que construía CI. La afirmación "el runtime es 3.11.15" de la sección de
`ruff` era cierta para `uv run python` y falsa para los tests.

Al sincronizar el venv aparecieron 8 errores que no existían: `uvicorn` no está
declarado en el extra `test` — a propósito, porque los tests ejercitan rutas y
no el proceso que sirve — pero `api/server.py` lo importaba a nivel de módulo, lo
que hacía el archivo inimportable sin un servidor ASGI. El import se movió a
`run_server()`, que es el único lugar donde se usa. Los 8 tests de
`test_api_server.py` son el ratchet: devolver el import arriba los rompe.

**El linter de dev-agents llevaba rojo desde `74d116e`.** CI corre
`dev_agents_linter.py src/decision_maker/core` y el paso salía con 1. Nueve
violaciones, de las cuales dos eran defectos reales y las otras siete eran parámetros:

- `reporting.py` — `except Exception` alrededor de la carga del template de
  Jinja2. Ahora `(TemplateError, OSError)`, que es lo que `get_template` puede
  levantar de verdad.
- `jsonl_store.get_entry` → `entry`, que era el otro nombre con prefijo `get_`
  del repo, y empareja con el `entries()` que ya existía.

Las siete de UX-01 (5 a 14 parámetros) no se refactorizaron: convertir
`log_decision` y `create` en Parameter Objects es un rediseño de API sobre
cuatro módulos y ~40 call sites, que necesita spec propia. Lo que sí se hizo es
convertir la regla en un ratchet de dos vías en `dev_agents_linter.py`: falla si
se **agrega** una violación y también si se **arregla** una sin actualizar la
tabla, así que el número sólo puede bajar y nadie lo baja en silencio. Los tres
controles negativos están verificados.

Y el mismo criterio para los checkers: `scripts/` se ejecutaba como pasos
suitos de CI, así que la suite podía estar 100% verde con un checker roto.
`test_checkers_run.py` los corre como subprocesos y verifica su código de
salida.

### Quinta ronda: tres cards del kanban describían defectos que no existían (28-Sep-2026)

El kanban abría tres frentes que, medidos uno por uno, no eran lo que decían —
misma clase que el conteo «24 motores» de la ronda anterior. Se midió cada uno
antes de tocar código, y en dos casos el instrumento era el que estaba mal:

| Card decía | Medición | Qué se hizo |
|---|---|---|
| `nav: index.md` no resuelve contra `docs/index.md` | **Sí resuelve**: mkdocs arma los targets de `nav` contra `docs_dir` | Nada; el problema real era otro |
| 13 enlaces rotos, «los targets no existen en ningún lado» | **Dos sí existen** un nivel arriba | Se arreglaron; ver abajo |
| Fidelidad agrupa clases por nota, no por sección | **Ya resuelve por sección** (`sections()` + claim 2, con test dedicado) | Nada; ya estaba corregido |

**El defecto real de `mkdocs.yml` era peor que el reportado: el archivo no era
YAML válido.** La línea 27 era `- 001: Rust Math Engine: adr/...`, con un `:` sin
comillas dentro del valor, así que `mkdocs build` abortaba en el parser antes de
mirar el vault. Nunca se había compilado, y no podía: no está en CI, ni en el
extra `test`, ni instalado.

Se arregló el YAML y se midió el build: 49 warnings, de los cuales **8 son links
rotos reales** (los mismos que quedan declarados) y **41 son mkdocs sin ver fuera
de `docs_dir`** — `../README.md` desde `docs/` apunta al root del repo y existe,
sólo que mkdocs no lo resuelve. Con eso medido, la pregunta correcta no era cómo
terminar de arreglarlo sino **si debía existir**. Fue creado en `3279d14`
(31-Jul-2026, la fase "God-Mode") como template genérico; ningún session-log lo
menciona, ninguna decisión lo adoptó, y no puede leer los 512 `[[wikilinks]]` del
vault sin un plugin externo ni ver fuera de `docs_dir`, con un nav que cubría 4 de
54 notas.

**Retirado.** Se borraron `mkdocs.yml`, el extra `docs` de `pyproject.toml` y el
ratchet de 4 tests que se había escrito — se escribe un ratchet para proteger algo
que va a vivir, no para custodiar lo que se retira. El repo ya es un vault de
Obsidian con cuatro checkers encima; un publicador HTML sin audiencia era un
segundo árbol de documentación esperando a divergir. Si algún día hace falta
sitio, se genera desde el vault.

Sobre los enlaces: once entradas estaban declaradas en `KNOWN_BROKEN` con una
justificación **en bloque** («los targets no existen en ningún lado») que era
falsa para dos de ellas. Al medir una por una, `./docs/architecture.md` y
`./docs/index.md` desde `docs/reorganization/` resolvían a `../architecture.md` y
`../index.md`, que existen. Se corrigieron y se sacaron de la lista: **11 → 9**.
`./python/scripts/` quedó con su propia razón porque es un directorio que nunca
existió, no un documento del árbol fantasma — la justificación agrupada lo había
tapado.

Deuda al cerrar la ronda: **539 tests**.

## En curso

- [ ] Falta nota para 41 módulos anunciados en `[[architecture]]` — entre ellos `pareto.py`, `decision_theory.py`, `sensitivity.py`, `aggregator.py` y `config_runner.py`, todos de primera clase en el pipeline `standard`

## Pendiente

*(nada abierto en esta familia: ver Descartado)*

## Descartado

- [x] Enlaces rotos en `reorganization/deliverables.md` y `plan.md` — el plan nunca se ejecutó. Once entradas quedaron declaradas en `KNOWN_BROKEN` con una justificación en bloque, y al medir una por una dos eran falsas: `./docs/architecture.md` y `./docs/index.md` tienen destino real un nivel arriba. Corregidas; quedan 9, cada una con su razón, y `./python/scripts/` aparte porque es un directorio inexistente y no un documento del árbol fantasma
- [x] `docs/reorganization/` y `docs/session-logs/` no se fusionan, y tampoco había que declarar un canónico: **ninguno lo es**. Son dos mitades del mismo archivo, complementarias y sin solape real — `reorganization/` (8 notas) es el *plan y análisis* de enero 2026 (propuesta, entregables, antes/después, deuda), `session-logs/` (3 notas) es la *bitácora de ejecución* (qué se movió, verificación posterior, tests de esa corrida), más `tests-results/meta-decision-result`. El diff lo confirma: los dos "summary" comparten 9 líneas de ~270 y ~320. El canónico del estado actual es `[[index]]`, y `[[reorganization/README]]` ya es la puerta de entrada del archivo — indexa las tres carpetas y lo dice explícitamente. La card pedía declarar algo que el README ya declaraba
- [x] Una fecha que parecía imposible, y no lo era. `session-logs/` decía `2024-12-24` y el repo arranca el 2025-11-28, así que la leí como error. **Me equivoqué**: el primer commit trae dos archivos (`.gitignore`, `README.md`) y nunca hubo 54 archivos en la raíz dentro de git — el "54 → 19" y el backup `desicion-maker-backup-20241224-194148` son de un proyecto **pre-git** en `/Users/arturo/development/lumina`. La fecha es real. El defecto verdadero estaba en `[[reorganization/README]]`, que atribuía todo a "enero 2026": ahora distingue la reorganización de **dic 2024** (`session-logs/`, anterior a git) del **plan de enero 2026** (`reorganization/`). La fecha no se tocó
- [x] Archivo de histórico: [[reorganization/README|reorganization]] — documentación de la reorganización de 2026
