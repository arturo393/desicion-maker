---
aliases: [What-If Engine, What If, Interactive What-If]
tags: [module, lumina, quant, stochastic, what-if]
id: MOD-WHAT-IF
title: "What-If Analysis Engine"
type: module
category: stochastic
status: stable
module: "decision_maker.core.what_if"
class: "WhatIfEngine"
related: ["[[unified-orchestrator]]", "[[sensitivity-analysis]]"]
created: 2026-08-10
updated: 2026-09-27
---

# What-If Analysis Engine

## `what_if.py`

> Facilitates real-time interactive exploration of parameter adjustments and immediate score recomputation.
>
> Usage: `from decision_maker.core.what_if import WhatIfEngine`
> Does NOT: modify persisted scenario configuration on disk.

### Clases Principales

- **`WhatIfEngine`**: Manages interactive parameter tweaking workflows, allowing real-time adjustment of factor weights and criteria directions without re-executing full Monte Carlo simulations.
