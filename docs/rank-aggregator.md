---
aliases: [Rank Aggregator, Borda Aggregator]
tags: [module, lumina, quant, mcda, aggregator]
id: MOD-AGGREGATOR
title: "Rank Aggregator Engine"
type: module
category: mcda
status: stable
module: "decision_maker.core.aggregator"
class: "RankAggregator"
related: ["[[unified-orchestrator]]", "[[topsis]]", "[[promethee]]"]
created: 2026-08-10
updated: 2026-09-27
---

# Rank Aggregator Engine

## `aggregator.py`

> Combines heterogeneous rankings across multiple evaluation methods into one consensus ranking.
>
> Usage: `from decision_maker.core.aggregator import RankAggregator`
> Does NOT: execute underlying multi-criteria engines.

### Clases Principales

- **`RankAggregator`**: Implements Borda count consensus, Copeland pairwise tournament aggregation, and rank variance scoring across divergent methodology outputs.
