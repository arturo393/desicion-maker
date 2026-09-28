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

### Lo que este trabajo NO verificó

- **Ninguno de los 4 checkers corre en el harness de tests.** Se ejecutan como scripts en CI. Un test que verifica que el archivo aparece en la salida de CI sigue sin existir.
- **Los 13 enlaces rotos preexistentes siguen rotos.** Están documentados por target exacto en `KNOWN_BROKEN` porque apuntan a un árbol de documentación propuesto que nunca se ejecutó; reescribir los paths no arregla nada.
- **2 literales `.py` en notas `archive` no se verifican contra el árbol**: están en la bitácora de Dic-2025 y el checker los lista como NOTA, no como fallo, porque son afirmaciones sobre el pasado. Los nombres y las líneas están en la salida del propio checker, que es donde se leen; no se repiten acá porque un literal `.py` en esta nota se verifica contra el árbol actual.
- **`ruff check src/decision_maker` reporta 113 errores preexistentes** en archivos de test que no son de esta tarea. Los 4 de los scripts de docs (`UP031`, `B033` en la lista de palabras, y los de `dev_agents_linter.py`) no los lintea CI, que sólo corre `src/decision_maker`.
- **No se ha hecho commit.** `ci.yml` llama a 4 scripts que siguen sin trackear: commitear el workflow antes que los scripts rompe el pipeline en el push.

## En curso

- [ ] Falta nota para 41 módulos anunciados en `[[architecture]]` — entre ellos `pareto.py`, `decision_theory.py`, `sensitivity.py`, `aggregator.py` y `config_runner.py`, todos de primera clase en el pipeline `standard`

## Pendiente

- [ ] `ndarray` sigue declarado en `rust_core/Cargo.toml` sin usarse en `lib.rs`, y `README.md:3`, `README.md:47` y `docs/index.md:43` lo siguen anunciando como parte del stack
- [ ] `mkdocs.yml` (raíz del repo, no `docs/mkdocs.yml`) declara `nav: Home: index.md`, que no matchea `docs/index.md` en disco
- [ ] `check_obsidian_fidelity.py` agrupa las clases por nota, no por sección `## \`modulo.py\``: una nota podría mandar a importar `AHPHelper` desde TOPSIS y el check lo aprobaría
- [ ] `docs/.obsidian/` sin regla en `.gitignore` raíz: commitearlo arrastra 968 KB de `main.js` vendorizado del plugin Kanban
- [ ] Falta decidir si `reorganization/` y `session-logs/` se fusionan (el análisis dice que no, por diff de contenido)

## Descartado

- [x] 12 links rotos en `reorganization/DELIVERABLES.md` — el plan nunca se ejecutó; los targets no existen en ningún lado, así que arreglar los paths no arregla nada. Quedan declarados como pre-existentes en `KNOWN_BROKEN`
- [x] `docs/reorganization/` y `docs/session-logs/` no se fusionan: se verificó por diff que tienen contenido distinto (256 vs 307 líneas). Sólo falta declarar cuál es el canónico
- [x] Archivo de histórico: [[reorganization/README|reorganization]] — documentación de la reorganización de 2026
