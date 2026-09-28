---
aliases: [Portfolio Optimizer, Portfolio_Optimizer]
tags: [module, lumina, quant, portfolio, optimization]
id: MOD-PORTFOLIO
title: "Portfolio Optimizer"
type: module
category: optimization
status: stable
module: "decision_maker.core.portfolio"
class: "PortfolioOptimizer"
related: ["[[antifragile-engine]]", "[[genetic-algorithms]]", "[[unified-orchestrator]]"]
created: 2026-08-10
updated: 2026-09-27
---

## `portfolio.py`

> Mean-variance portfolio optimization: allocates a budget across decision options under risk constraints.
> Uso: `from decision_maker.core.portfolio import PortfolioOptimizer`
> No: conduct deep research queries.

### Clases Principales

- **`SearchConfig`**: Bundles the portfolio search parameters (Parameter Object).
- **`PortfolioOptimizer`**: Allocates budget or resources across options. The objective at `portfolio.py:59` is mean-variance — return against the variance of the allocation — so it treats each option as a position rather than as a candidate to be ranked.
