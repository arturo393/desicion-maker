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
updated: 2026-09-27
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

Que los límites sean globales y no por opción es lo que hace comparables los puntajes. El fórmula está en `monte_carlo.py:141-148` y su comentario apunta a que replica el motor de Rust.

### Penalización de cola

`RUIN_THRESHOLD_PERCENTILE = 5.0`. Las trayectorias en o por debajo del percentil 5 reciben un factor **multiplicativo**:

```
ruin_penalty = 1 - (ruin_count / num_simulations)
```

El factor se encoge a medida que más trayectorias caen en la cola, así que una distribución con cola masiva se castiga más que una con una sola cola. Es una penalización geométrica sobre el ~5% inferior, no una suma ponderada.

### Qué devuelve

Por opción: `mean_score`, `std_dev`, `min_score`, `max_score`, `percentile_5`, `percentile_95`, `success_rate`, `var_95` (= p5), `cvar_95` (media de los puntajes ≤ p5) y **`raw_scores`**.

Dos detalles que importan aguas abajo:

- `success_rate` es la fracción de simulaciones donde la opción **supera la media cross-option**, no donde su puntaje es > 0. El comentario en `monte_carlo.py:181-184` documenta el cambio: con puntajes normalizados a `[0,1]`, `score > 0` siempre es cierto.
- `raw_scores` se conserva completo. Es lo que permite el remuestreo empírico de [[bayesian-inference-engine]] y la covarianza empírica de [[antifragile-engine]]. Si se perdiera, ambos caerían a aproximaciones.

### Clases Principales

- **`MonteCarloEngine`**: Simulador de N escenarios. Default `num_simulations=10000`; la correlación es opcional y llega por parámetro.

El remuestreo que consume estas salidas vive en [[bootstrap-ranking]], que es la nota que posee `bootstrap.py`.
