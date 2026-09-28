---
aliases: [Unified Orchestrator, Unified_Orchestrator]
tags: [module, lumina, quant, infrastructure, orchestrator]
id: MOD-ORCHESTRATOR
title: "Unified Decision Framework Orchestrator"
type: module
category: infrastructure
status: stable
module: "decision_maker.core.orchestrator"
class: "UnifiedDecisionFramework"
related: ["[[data-models-and-schemas]]", "[[monte-carlo-engine]]", "[[topsis]]", "[[promethee]]"]
created: 2026-08-10
updated: 2026-09-27
---

## `orchestrator.py`

> The entry point every other engine is called from: owns the factors, the options, and the mode pipeline.
> Usage: `from decision_maker.core.orchestrator import UnifiedDecisionFramework`
> Does NOT: implement the individual algorithms — it sequences them.

### The mode pipeline

`UnifiedDecisionFramework` is the class in every example. The pipeline is layered, each mode a superset of the one before it:

| Mode | Adds |
|---|---|
| `express` | Monte Carlo → TOPSIS → Pareto |
| `standard` | decision theory, sensitivity, PROMETHEE over uncertainty, robust, Borda aggregation |
| `advanced` | crisp PROMETHEE, Bayesian, Genetic, Bootstrap |

Everything downstream consumes the same `dict[str, Statistics]` that `MonteCarloEngine.run()` returns, so the engines never generate trajectories of their own.

### What it owns besides sequencing

- **Veto power.** `DecisionGate` is constructed at `:175` and applied at `:369`; a vetoed option is dropped from `mc_results` at `:390`. The gates can remove an option from the result set — they are not a warning, they are a filter.
- **The causal DAG.** `CausalDAG.build()` is called at `:285` and its output is attached to the result at `:383` and `:474`. This is where causal structure enters the framework — **not** in the Monte Carlo engine, which only accepts a correlation matrix it is handed.
- **Persistence.** `save_session` / `load_session` round-trip a decision through the registry. `load_session` is a `classmethod`, so a stored session reopens without a live instance.
- **The AI agent is conditional.** `GeminiDeepResearchAgent` is constructed at `:153`, but it only runs at `:408` when `use_ai` is passed **and** `is_available` is true — which needs a configured API key. In the default path it is silently absent from the result.

### Clases Principales

- **`AdvancedAnalysis`**: Bundles everything the advanced pass needs (data, weights, modes) so `_run_advanced_analysis` does not take a long positional list (Parameter Object).
- **`UnifiedDecisionFramework`**: The facade. `__init__` accepts `correlation_matrix`; `add_option` / `add_factor` build the problem; `run_analysis(mode=...)` returns the results.
