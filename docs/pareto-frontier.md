---
aliases: [Pareto Frontier, Pareto Engine, Pareto]
tags: [module, lumina, quant, optimization, pareto]
id: MOD-PARETO
title: "Pareto Frontier Engine"
type: module
category: optimization
status: stable
module: "decision_maker.core.pareto"
class: "ParetoEngine"
related: ["[[unified-orchestrator]]", "[[topsis]]", "[[monte-carlo-engine]]"]
created: 2026-08-10
updated: 2026-09-27
---

# Pareto Frontier Engine

## `pareto.py`

> Identifies non-dominated alternatives forming the multi-objective Pareto efficient frontier.
>
> Usage: `from decision_maker.core.pareto import ParetoEngine`
> Does NOT: perform scalar weighting or rank aggregation.

### Clases Principales

- **`ParetoEngine`**: Computes non-dominated sets and identifies strictly dominated alternatives across multiple criteria dimensions.
