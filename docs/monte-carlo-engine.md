---
aliases: [Monte Carlo Engine, Monte_Carlo_Engine]
tags: [module, lumina, quant, stochastic, monte-carlo]
id: MOD-MONTE-CARLO
title: "Monte Carlo Engine"
type: module
category: stochastic
status: stable
module: "decision_maker.core.monte_carlo"
class: "MonteCarloEngine"
related: ["[[bayesian-inference-engine]]", "[[antifragile-engine]]", "[[topsis]]", "[[unified-orchestrator]]", "[[data-models-and-schemas]]"]
created: 2026-08-10
updated: 2026-10-01
---

## `monte_carlo.py`

> Genera distribuciones de puntaje por opción simulando cada variable con su distribución declarada.
> Uso: `from decision_maker.core.monte_carlo import MonteCarloEngine`
> No: deducir la estructura de correlación — la recibe del llamador.

### Correlación: cópula gaussiana, no causalidad

`_apply_correlation` correlaciona los factores **si y sólo si** el llamador pasa una `correlation_matrix`. El mecanismo es una cópula gaussiana rank-based:

1. Cada factor se convierte a rangos y de ahí a puntajes normales.
2. Se aplica la factorización de Cholesky `L` de la matriz.
3. Se vuelve a uniformes y se reordena para **preservar los marginales originales** — la correlación no deforma la distribución de cada variable.

Una matriz que el motor no puede aplicar es un error de modelado y lanza `ValueError`: forma distinta de `(n_factores, n_factores)`, asimétrica o no definida positiva. Hasta el 18-Oct-2026 cada uno de esos casos dejaba un warning y seguía **sin correlación**, así que el resultado mostraba una dispersión más angosta que la modelada sin decirlo.

**Y la correlación válida tampoco se aplicaba.** El paso 3 asignaba con `template[rangos] = ordenados`, que aplica la permutación inversa —una permutación cualquiera—: con ρ = 0,8 pedido, la muestra salía con Spearman 0,003. El test viejo sólo comprobaba que la media fuera finita. Ahora `test_correlation_matrix_applied` mide la dependencia en las muestras (Spearman 0,786 = 6/π·asin(0,4)) y falla contra el código viejo.

> **Lo que este motor no es.** La matriz es una estructura **estadística** que entra por parámetro. El motor no la deriva, no la valida contra los datos y no tiene noción de causalidad. El DAG causal vive en `causal_dag.py` y lo invoca el orquestador — no este motor. Una versión anterior de esta nota afirmaba que el motor "rechaza la falacia de sustitución perfecta" y "evita condicionar sobre colliders"; ninguna de las dos cosas está en el código.

### Normalización: min-max global, y es deliberado

Con `normalize=True` (el default), cada factor se lleva a `[0,1]` con los **límites globales compartidos entre todas las opciones**, y luego:

- `maximize` → `norm * peso`
- `minimize` → `(1 - norm) * peso`

Que los límites sean globales y no por opción es lo que hace comparables los puntajes. La fórmula está en `MonteCarloEngine.run()`, en el bloque que empieza con el comentario `# Normalize exactly like the Rust MonteCarloEngine`, que apunta a que replica el motor de Rust.

### Sin penalización de cola (retirada el 18-Oct-2026)

Hasta el 18-Oct-2026 el motor restaba una fracción a las trayectorias en o bajo el percentil 5 **de la propia opción**. Como toda opción tiene un 5 % peor por construcción, el recorte caía igual sobre una opción segura que sobre una ruinosa (medido: N(0,1) y N(0,1000) recibían el mismo factor 0,95). No medía riesgo: era un recorte fijo.

Se retiró en vez de rediseñarse, por simplicidad. El puntaje de cada sorteo es exactamente la suma ponderada (`test_score_is_exactly_the_weighted_value`). El riesgo de cola sigue a la vista en `var_95` y `cvar_95`, y una línea de ruina de verdad —«perder más de X»— se declara en [[decision-gates]], con un umbral que pone quien decide.

**Efecto medido sobre los análisis del repo:** se corrieron los 44 análisis antes y después y se comparó el ganador de cada una de las 83 corridas del motor. Cambiaron 2, las dos en `uqomm_adopcion_v6_leakyfeeder`, y las dos son empates técnicos (diferencia menor a 0,006) que cambian de ganador entre dos corridas del mismo código, porque ese análisis no fija semilla. Ningún ganador cambió por la penalización.

### Semilla: reproducible por defecto

Desde el 18-Oct-2026 `MonteCarloEngine` usa `DEFAULT_SEED` (42) si no se le pasa otra: el mismo modelo da los mismos números. Antes usaba entropía nueva en cada corrida, y como 42 de los 44 análisis no fijaban semilla, un empate técnico podía cambiar de ganador entre dos corridas del mismo código. Para azar real, `seed=None` explícito. La semilla de cada corrida queda en la traza `DM_MC_TRACE`.

### Qué devuelve

Por opción: `mean_score`, `std_dev`, `min_score`, `max_score`, `percentile_5`, `percentile_95`, `success_rate`, `var_95` (= p5), `cvar_95` (media de los puntajes ≤ p5), **`raw_scores`**, `factor_stats` (mean/std/p5/p95 por factor) y `raw_factor_data` (muestras por factor), ambos de la propia opción (antes de `41c33a3`, 2026-09-29, eran los de la última opción para todas; ver [[results-catalog]]).

Dos detalles que importan aguas abajo:

- `success_rate` es la fracción de simulaciones donde la opción **supera la media cross-option**, no donde su puntaje es > 0. El comentario de `success_rate` en `MonteCarloEngine.run()` documenta el cambio: con puntajes normalizados a `[0,1]`, `score > 0` siempre es cierto.
- `raw_scores` se conserva completo. Es lo que permite el remuestreo empírico de [[bayesian-inference-engine]] y la covarianza empírica de [[antifragile-engine]]. Si se perdiera, ambos caerían a aproximaciones.

### Clases Principales

- **`MonteCarloEngine`**: Simulador de N escenarios. Default `num_simulations=10000`; la correlación es opcional y llega por parámetro.

El remuestreo que consume estas salidas vive en [[bootstrap-ranking]], que es la nota que posee `bootstrap.py`.
