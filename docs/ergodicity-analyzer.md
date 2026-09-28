---
aliases: [Ergodicity Analyzer, Ergodicity Engine, Kelly Criterion]
tags: [module, lumina, quant, stochastic, ergodicity, taleb]
id: MOD-ERGODICITY
title: "Ergodicity and Ruin Analyzer"
type: module
category: stochastic
status: stable
module: "decision_maker.core.ergodicity"
class: "ErgodicityAnalyzer"
related: ["[[monte-carlo-engine]]", "[[antifragile-engine]]", "[[decision-gates]]"]
created: 2026-08-10
updated: 2026-09-27
---

# Ergodicity and Ruin Analyzer

## `ergodicity.py`

> Analyzes time-average growth versus ensemble expectations and evaluates absorbing barrier ruin risks.
>
> Usage: `from decision_maker.core.ergodicity import ErgodicityAnalyzer`
> Does NOT: build neural network representations.

### Clases Principales

- **`ErgodicityResult`**: Structured output dataclass encapsulating time-average growth rates, ruin probabilities, drawdown metrics, and non-ergodicity indicators.
- **`ErgodicityAnalyzer`**: Evaluates cumulative multiplicative growth processes, calculates absorbing ruin thresholds, and computes Kelly betting allocations.
