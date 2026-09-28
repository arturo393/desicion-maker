---
aliases: [AHP]
tags: [module, lumina, quant, mcda, ahp]
id: MOD-AHP
title: "Analytic Hierarchy Process"
type: module
category: mcda
status: stable
module: "decision_maker.core.ahp"
class: "AHPHelper"
related: ["[[topsis]]", "[[promethee]]", "[[unified-orchestrator]]"]
created: 2026-08-10
updated: 2026-09-27
---

## `ahp.py`

> Analytic Hierarchy Process: convierte comparaciones por pares en pesos, con verificación de consistencia.
> Uso: `from decision_maker.core.ahp import AHPHelper`
> No: los algoritmos multicriterio que no son por pares, como TOPSIS o PROMETHEE.

### Clases Principales

- **`AHPHelper`**: `calculate_weights(matrix, labels)` es un método estático. Toma la matriz de comparación por pares, deriva los pesos, y devuelve un `dict[str, float | None]` indexado por etiqueta — un valor `None` marca una etiqueta cuya prioridad no se pudo resolver. Incluye el índice de inconsistencia de Saaty (`RI_TABLE`) para el ratio de consistencia.

> El módulo exporta `AHPHelper`, no `AHPEngine` (`ahp.py:9`). Una versión anterior de esta nota decía `from decision_maker.core.ahp import AHPEngine`, que no existe en el repositorio y falla con `ImportError`. El docstring del propio módulo ya decía `AHPHelper`; la nota era lo que estaba desactualizado.
