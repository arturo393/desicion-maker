---
aliases: [Sensitivity Analysis, Sensitivity Engine]
tags: [module, lumina, quant, stochastic, sensitivity]
id: MOD-SENSITIVITY
title: "Sensitivity Analysis Engine"
type: module
category: stochastic
status: stable
module: "decision_maker.core.sensitivity"
class: "SensitivityEngine"
related: ["[[unified-orchestrator]]", "[[robust-optimization]]", "[[monte-carlo-engine]]"]
created: 2026-08-10
updated: 2026-09-27
---

# Sensitivity Analysis Engine

## `sensitivity.py`

> Assesses how rank orderings change under deliberate parameter shocks and perturbations.
>
> Usage: `from decision_maker.core.sensitivity import SensitivityEngine`
> Does NOT: perform persistent database storage.

### Clases Principales

- **`ShockConfig`**: Configuration parameters defining factor perturbation magnitudes and directional weight sweeps.
- **`SensitivityEngine`**: Shocks individual criteria weights and scores systematically to measure stability thresholds where top rankings invert.
