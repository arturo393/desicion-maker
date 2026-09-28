---
aliases: [Genetic Algorithms, Genetic_Algorithms]
tags: [module, lumina, quant, optimization, genetic]
id: MOD-GENETIC
title: "Genetic Algorithms Engine"
type: module
category: optimization
status: stable
module: "decision_maker.core.genetic"
class: "GeneticOptimizer"
related: ["[[portfolio-optimizer]]", "[[unified-orchestrator]]"]
created: 2026-08-10
updated: 2026-09-27
---

## `genetic.py`

> Genetic algorithm optimizer for finding composite decision solutions.
> Uso: `from decision_maker.core.genetic import GeneticOptimizer`
> No: run topological data analysis or Bayesian belief networks.

### Clases Principales

- **`GeneticOptimizer`**: Evolves an "ideal option" by harvesting the best traits (genes) from the options that scored well, rather than picking a winner outright. The result is a synthetic composite, useful when the real question is what the best available traits look like combined.
