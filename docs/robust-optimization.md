---
aliases: [Robust Optimization, Robust Optimizer]
tags: [module, lumina, quant, optimization, robust]
id: MOD-ROBUST
title: "Robust Optimization Engine"
type: module
category: optimization
status: stable
module: "decision_maker.core.robust"
class: "RobustOptimizer"
related: ["[[unified-orchestrator]]", "[[sensitivity-analysis]]", "[[antifragile-engine]]"]
created: 2026-08-10
updated: 2026-09-27
---

# Robust Optimization Engine

## `robust.py`

> Optimización distributionalmente robusta: qué decisión sobrevive a que los pesos y las distribuciones estén equivocados.
> Uso: `from decision_maker.core.robust import RobustOptimizer`
> No: generar gráficos ni reportes.

Dos análisis en `analyze()`:

1. **Weight Shock Sensitivity (local)** — aplica `weight_shock = 0.2` a los pesos e identifica qué factores son capaces de voltear la decisión.
2. **Distributionally Robust Expectation (global)** — con `epsilon = 0.05` como radio de ambigüedad Wasserstein: el peor caso dentro de la bola de distribuciones a distancia `epsilon`. El score es `mean - epsilon * sqrt(variance)`.

> **Sobre el "peor decil".** Una versión anterior decía que los parámetros se estresaban "hacia el peor decil posible" y que el motor computaba "min-max regret rankings". Ninguna de las dos cosas existe en el repositorio: `regret` no aparece en `robust.py` y no hay estratificación por deciles. El mecanismo real es un radio Wasserstein y un shock de pesos del 20%.

> **No:** optimizar asignaciones de portafolio financiero.

### Clases Principales

- **`RobustOptimizer`**: `analyze(mc_results, factors, epsilon=0.05, weight_shock=0.2)`. Devuelve `robust_ranking`, `dro_scores`, `stability_metrics` y `weight_sensitivity`.

Consume las salidas de [[monte-carlo-engine]]; el contraparte de robustez de [[antifragile-engine]] es [[sensitivity-analysis]].
