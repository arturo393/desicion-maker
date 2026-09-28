---
aliases: [PROMETHEE]
tags: [module, lumina, quant, mcda, promethee]
id: MOD-PROMETHEE
title: "PROMETHEE Outranking Engine"
type: module
category: mcda
status: stable
module: "decision_maker.core.promethee"
class: "PrometheeEngine"
related: ["[[topsis]]", "[[ahp]]", "[[unified-orchestrator]]"]
created: 2026-08-10
updated: 2026-09-27
---

## `promethee.py`

> PROMETHEE II: calcula flujos netos de preferencia entre pares de opciones.
> Uso: `from decision_maker.core.promethee import PrometheeEngine, PrometheeConfig`
> No: manejar lógica difusa o estocástica de forma nativa.

### Clases Principales

- **`PrometheeConfig`**: Agrupa las preferencias de criterio de PROMETHEE (Parameter Object) — tipo de función de preferencia y sus parámetros `q`, `p`, `s`.
- **`PrometheeEngine`**: `analyze(decision_matrix, config)` construye la función de preferencia de cada criterio con `_build_pref_func()`, puntúa los flujos de cada par de opciones y devuelve el **flujo neto** por opción. Es el método crisp; la variante que promedia p5/mean/p95 sobre incertidumbre vive en el mismo módulo y la orquesta `UnifiedDecisionFramework`.
