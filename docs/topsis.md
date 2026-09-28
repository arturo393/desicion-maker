---
aliases: [TOPSIS]
tags: [module, lumina, quant, mcda, topsis]
id: MOD-TOPSIS
title: "TOPSIS MCDA Engine"
type: module
category: mcda
status: stable
module: "decision_maker.core.topsis"
class: "TOPSISEngine"
related: ["[[monte-carlo-engine]]", "[[promethee]]", "[[ahp]]", "[[unified-orchestrator]]"]
created: 2026-08-10
updated: 2026-09-27
---

## `topsis.py`

> TOPSIS: rankea opciones multicriterio contra una solución ideal y una anti-ideal.
> Uso: `from decision_maker.core.topsis import TOPSISEngine`
> No: manejar valores faltantes automáticamente.

### Clases Principales

- **`TOPSISEngine`**: `analyze(decision_matrix_fuzzy, weights, maximize)`. La matriz de entrada es un `dict[opción][factor] -> (p5, mean, p95)`, es decir **triplas de percentiles**, no escalares — por eso el motor es "fuzzy" en el sentido de incertidumbre, no de conjuntos difusos. El tercer parámetro se llama `maximize` (una lista de booleanos por factor), no `maximize_flags`.

> La firma exacta es `analyze(decision_matrix_fuzzy, weights, maximize)` (`topsis.py:20-25`). La versión anterior de esta nota decía `analyze(data, weights, maximize_flags)`, copiado del docstring del propio módulo, que también está equivocado.
