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

Dos guardas el motor de una matriz inválida: si la forma no es `(n_factores, n_factores)` o si no es definida positiva, se registra un warning y se sigue **sin correlación**.

> **Lo que este motor no es.** La matriz es una estructura **estadística** que entra por parámetro. El motor no la deriva, no la valida contra los datos y no tiene noción de causalidad. El DAG causal vive en `causal_dag.py` y lo invoca el orquestador — no este motor. Una versión anterior de esta nota afirmaba que el motor "rechaza la falacia de sustitución perfecta" y "evita condicionar sobre colliders"; ninguna de las dos cosas está en el código.

### Normalización: min-max global, y es deliberado

Con `normalize=True` (el default), cada factor se lleva a `[0,1]` con los **límites globales compartidos entre todas las opciones**, y luego:

- `maximize` → `norm * peso`
- `minimize` → `(1 - norm) * peso`

Que los límites sean globales y no por opción es lo que hace comparables los puntajes. La fórmula está en `MonteCarloEngine.run()`, en el bloque que empieza con el comentario `# Normalize exactly like the Rust MonteCarloEngine`, que apunta a que replica el motor de Rust.

### Penalización de cola

`RUIN_THRESHOLD_PERCENTILE = 5.0`. Las trayectorias en o por debajo del percentil 5 **de la propia opción** pierden una fracción de su magnitud:

```
ruin_penalty = 1 - (ruin_count / num_simulations)
score_cola  -= |score_cola| * (1 - ruin_penalty)
```

**Qué mide en realidad:** como el umbral es el percentil 5 de la misma opción, `ruin_count` es ~5 % de las trayectorias por construcción y el factor queda en ~0.95 para cualquier distribución continua, tenga cola fina o masiva (medido: N(0,1) y N(0,1000) dan 0.9500). No distingue colas; es un recorte fijo del ~5 % inferior. Solo cambia con empates (distribuciones discretas), y ahí de una forma que no depende del tamaño de la cola.

Se resta `|s|` en vez de multiplicar para que con `normalize=False` y puntajes negativos la penalización empeore la cola en vez de acercarla a cero (antes de 2026-10-01 la mejoraba). En el camino por defecto (`normalize=True`, puntajes en [0,1]) las dos fórmulas coinciden.

Para que castigue colas de verdad, el umbral tendría que ser común a todas las opciones (p. ej. el percentil 5 de la matriz conjunta). Se mantiene el umbral por opción porque cambiarlo reordena todos los análisis ya hechos; la señal para revisarlo es un caso donde dos opciones con colas distintas reciban la misma penalización y eso decida el ranking.

### Qué devuelve

Por opción: `mean_score`, `std_dev`, `min_score`, `max_score`, `percentile_5`, `percentile_95`, `success_rate`, `var_95` (= p5), `cvar_95` (media de los puntajes ≤ p5), **`raw_scores`**, `factor_stats` (mean/std/p5/p95 por factor) y `raw_factor_data` (muestras por factor), ambos de la propia opción (antes de `41c33a3`, 2026-09-29, eran los de la última opción para todas; ver [[results-catalog]]).

Dos detalles que importan aguas abajo:

- `success_rate` es la fracción de simulaciones donde la opción **supera la media cross-option**, no donde su puntaje es > 0. El comentario de `success_rate` en `MonteCarloEngine.run()` documenta el cambio: con puntajes normalizados a `[0,1]`, `score > 0` siempre es cierto.
- `raw_scores` se conserva completo. Es lo que permite el remuestreo empírico de [[bayesian-inference-engine]] y la covarianza empírica de [[antifragile-engine]]. Si se perdiera, ambos caerían a aproximaciones.

### Clases Principales

- **`MonteCarloEngine`**: Simulador de N escenarios. Default `num_simulations=10000`; la correlación es opcional y llega por parámetro.

El remuestreo que consume estas salidas vive en [[bootstrap-ranking]], que es la nota que posee `bootstrap.py`.
