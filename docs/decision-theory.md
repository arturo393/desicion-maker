---
aliases: [Decision Theory Engine, Decision Theory]
tags: [module, lumina, quant, stochastic, decision-theory]
id: MOD-DECISION-THEORY
title: "Decision Theory Engine"
type: module
category: stochastic
status: stable
module: "decision_maker.core.decision_theory"
class: "DecisionTheoryEngine"
related: ["[[unified-orchestrator]]", "[[monte-carlo-engine]]", "[[topsis]]"]
created: 2026-08-10
updated: 2026-09-27
---

# Decision Theory Engine

## `decision_theory.py`

> Evaluates classic non-probabilistic decision criteria under complete uncertainty.
>
> Usage: `from decision_maker.core.decision_theory import DecisionTheoryEngine`
> Does NOT: run stochastic Monte Carlo trajectory simulations.

### Clases Principales

- **`DecisionTheoryEngine`**: Computes classical decision benchmarks including Maximax, Maximin, Hurwicz optimism-pessimism index, Laplace equal likelihood, and Minimax Regret.
