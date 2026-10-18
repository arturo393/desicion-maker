---
aliases: [Roadmap, Roadmap v3, Roadmap v3.0, ROADMAP_v3.0, Project Roadmap]
tags: [roadmap, lumina, quant, archive]
id: DOC-ROADMAP
title: "Roadmap de Desarrollo Cuantitativo"
type: roadmap
category: project-management
status: active
related: ["[[Tablero]]", "[[decision-maker-moc]]", "[[index]]", "[[architecture]]"]
created: 2026-08-10
updated: 2026-10-18
---

# 🗺️ Roadmap: Decision Intelligence Framework

Una sola hoja de ruta, y corta a propósito: **la dirección** vive acá, **las tareas** en el [[Tablero]]. Hasta el 18-Oct-2026 había tres copias —`ROADMAP_v3.0.md` en la raíz, esta nota y el Backlog del Tablero— con las mismas cinco mejoras escritas tres veces; se dejó esta.

## Dónde está (v3.1)

- Motor validado: [[monte-carlo-engine]], con correlación entre factores, escenarios comunes y valor de la información.
- [[weight-robustness]]: si el ganador sobrevive a otros pesos razonables.
- [[decision-ledger]]: las decisiones tomadas, su revisión y la calibración de la confianza.
- 19 motores ruteables: 2 validados, 1 caracterizado ([[topsis]], segunda opinión), 16 experimentales y etiquetados como tales en cada reporte.

## Hacia dónde (criterios del dueño, 18-Oct-2026)

1. **Que el sistema sepa si acierta.** Cerrar decisiones reales en el ledger; con unas 20 cerradas la calibración empieza a decir algo.
2. **Simplicidad.** Menos motores, mejor validados; un solo almacén de resultados; una sola capa de LLM.
3. **Calidad del modelo de valor.** Funciones de valor por criterio y ayuda para estimar rangos, con spec aprobada antes.
4. **Conectividad.** Todo lo que otro repo lea sale con esquema publicado y `--json`.

Las tareas concretas de cada punto, con prioridad, están en el [[Tablero]].
