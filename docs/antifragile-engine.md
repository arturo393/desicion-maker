---
aliases: [Antifragile Engine, Barbell Strategy, Antifragile_Engine]
tags: [module, lumina, quant, portfolio, antifragile, taleb]
id: MOD-ANTIFRAGILE
title: "Antifragile Engine"
type: module
category: portfolio
status: stable
module: "decision_maker.core.antifragile"
class: "AntifragileEngine"
related: ["[[monte-carlo-engine]]", "[[portfolio-optimizer]]", "[[unified-orchestrator]]"]
created: 2026-08-10
updated: 2026-09-27
---

## `antifragile.py`

> Auditor de asimetría de cola: qué opción se rompe con eventos extremos y cuál se beneficia de la volatilidad.
> Uso: `from decision_maker.core.antifragile import AntifragileEngine`
> No: calcular la matriz multicriterio lineal — consume las estadísticas que produce [[monte-carlo-engine]].

Cuatro modos de análisis, todos consuming `dict[str, Statistics]` como entrada. Ninguno genera trayectorias propias.

### 1. Índice de fragilidad — lacola como entrada de primera clase

`fragility_index()` compone cuatro términos ponderados en un score en `[0, 1]`, donde 1 es más frágil:

| Término | Peso | Qué mide |
|---|---|---|
| `cvar_gap` | **0.4** | Qué tan lejos está el CVaR de la media, normalizado por σ y escalado por `FRAGILITY_CVAR_SCALE = 5.0` |
| `var_ratio` | **0.3** | σ relativo a la media: `std / (abs(mean) + EPSILON)` |
| `tail_gap` | **0.2** | Qué tan lejos está el **percentil 5** de la media, escalado por `FRAGILITY_TAIL_SCALE = 5.0` |
| `1 - success_rate` | 0.1 | Fracción de simulaciones que la opción no gana |

Veredicto: `> FRAGILE_THRESHOLD (0.6)` → `fragile`; `< ROBUST_THRESHOLD (0.3)` → `robust`; en medio → `moderate`.

> **Sobre la desviación estándar.** Una versión anterior de esta nota decía que el motor "prohíbe el uso de σ como riesgo" y que medía la cola con percentiles P99. Ninguna de las dos cosas es así: `FRAGILITY_VAR_WEIGHT = 0.3` convierte a σ en el segundo término más pesado del score, y la cola se mide en el **percentil 5** — `P99` no aparece en el archivo. La cola se mira por el lado que puede matar la decisión, no por el lado que se puede contabilizar.

### 2. Barbell — covarianza empírica con fallback

`barbell_analysis()` necesita al menos 3 opciones. Por cada par `(a, b)`:

```
portfolio_score = (score_a + score_b) / 2
portfolio_risk  = sqrt(0.25·σa² + 0.25·σb² + 2·0.25·cov_ab)
```

`cov_ab` sale de `np.cov` sobre los `raw_scores` de ambas opciones — pero **sólo si las dos los tienen**. Si falta alguno, el fallback es `cov_ab = 0.0`, es decir correlación nula.

> La versión anterior decía "nunca asume correlación nula". La rama existe (`antifragile.py:111-112`) y es exactamente el caso que la frase niega. Lo que sí es cierto es que cuando hay datos crudos, la covarianza es empírica y no una suposición — lo cual es la mitad del argumento de Taleb, no todo.

### 3. Convexidad

`convexity_analysis()` perturba los valores con `CONVEXITY_PERTURBATIONS = [0.5, 0.8, 1.2, 1.5]` y mide si la opción mejora cuando el mundo empeora. `CONVEXITY_THRESHOLD = 0.01` separa la ganancia real del ruido.

**Usa min-max.** `antifragile.py:404` normaliza con `(vals - b["min"]) / (b["max"] - b["min"])` contra límites globales, con un comentario que lo dice explícitamente para que coincida con los límites que usa [[monte-carlo-engine]]. Una versión anterior de esta nota afirmaba que el motor estaba "expurgado de cualquier normalización Min-Max"; el código hace min-max, y lo hace a propósito. `docs/architecture.md` describe el mismo comportamiento — la nota era la que mentía.

### 4. Vía Negativa

`via_negativa()` no suma: pregunta qué habría que **quitar**.

### Clases Principales

- **`AntifragileEngine`**: Los cuatro modos más `analyze()` como despachador. Todo métodos estáticos.
- **`Perturbation`**: Agrupa una perturbación de factor sobre una opción (Parameter Object).

La variante de robustez sobre pesos y distribuciones está en [[robust-optimization]], que es la nota que posee `robust.py`.
