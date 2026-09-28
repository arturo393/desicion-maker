---
aliases: [Bootstrap Ranking, Bootstrap Simulator]
tags: [module, lumina, quant, stochastic, bootstrap]
id: MOD-BOOTSTRAP
title: "Bootstrap Ranking Engine"
type: module
category: stochastic
status: stable
module: "decision_maker.core.bootstrap"
class: "BootstrapRanking"
related: ["[[unified-orchestrator]]", "[[monte-carlo-engine]]", "[[rank-aggregator]]"]
created: 2026-08-10
updated: 2026-09-27
---

# Bootstrap Ranking Engine

## `bootstrap.py`

> Re-muestrea la matriz difusa para medir qué tan estable es el ranking frente a ruido.
> Uso: `from decision_maker.core.bootstrap import BootstrapRanking, BootstrapConfig`
> No: generar escenarios desde distribuciones — necesita las entradas empíricas de [[monte-carlo-engine]].

### Clases Principales

- **`BootstrapConfig`**: Agrupa los parámetros del remuestreo (weights, maximize, `n_bootstrap=1000`, `alpha=0.05`).
- **`BootstrapRanking`**: `confidence_intervals()` es un método estático. Perturba la matriz con `BOOTSTRAP_NOISE_SCALE = 0.1`, re-ranking cada iteración con [[topsis]], y devuelve `mean_rank`, `ci_low`, `ci_high` y `p_best` por opción. Responde "si los datos fueran un poco distintos, ¿cambiaría el ganador?".
