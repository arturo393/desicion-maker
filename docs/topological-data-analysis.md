---
aliases: [Topological Data Analysis, Topological_Data_Analysis]
tags: [module, lumina, quant, topology, visualization]
id: MOD-TOPOLOGY
title: "Topological Data Analysis"
type: module
category: topology
status: stable
module: "decision_maker.core.topology"
class: "TopologicalDataAnalysis"
related: ["[[topsis]]", "[[reporting-and-registry]]"]
created: 2026-08-10
updated: 2026-09-27
---

## `topology.py`

> Maps the structure of the decision space with multidimensional scaling and manifold embedding.
> Uso: `from decision_maker.core.topology import TopologicalDataAnalysis`
> No: perform financial portfolio optimization.

### Clases Principales

- **`TopologicalDataAnalysis`**: Embeds the options into a low-dimensional space (MDS at `topology.py:75`, Isomap at `:86`) and reports how stable the resulting ranking is under that projection. Useful for spotting clusters of options that a single score hides.
