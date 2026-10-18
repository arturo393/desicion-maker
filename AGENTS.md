---
aliases: [Agent Guidelines, Reglas de Agentes]
tags: [agents, guidelines, lumina, rules]
id: GOV-AGENTS
title: "Decision Maker Framework - Agent Guidelines"
type: meta
category: governance
status: active
related: ["[[docs/index|index]]", "[[docs/note-schema|note-schema]]"]
created: 2026-08-10
updated: 2026-10-01
---

# Decision Maker Framework - Agent Guidelines

## Project Map (hermanos del dominio)
Este repo pertenece al dominio **Lumina** (cuantitativo), junto con:
- `../montecarlo` — bot de trading C++ que comparte la base conceptual Monte Carlo
  (backtest, simulación de caminos, walk-forward). Si una tarea toca validación de
  edge/riesgo en trading, consultar `../montecarlo` (AGENTS.md es la referencia).
- `~/.config/opencode/dev-agents` — conocimiento general SE/firmware/brands (referencia global).
- `../../safetymind/` — dominio SEPARADO (edge AI industrial). No mezclar trabajo.
- `curriculum` — proyecto personal, no relacionado. No existe en esta máquina (verificado 2026-10-01 con `find ~ -maxdepth 3 -iname '*curriculum*'`); se nombra para que no se lo confunda con este repo si aparece.

Regla: si una tarea toca modelado de riesgo/decisión Monte Carlo para trading,
revisar `../montecarlo` primero. Si toca hardware/edge AI, NO asumir relación con
SafetyMind (`../../safetymind/`) sin preguntar.

## Build & Test
```bash
# Python library, uv-based
uv sync
uv run pytest          # run unit tests
```

## Conventions
- Python 3.11+, typed (type hints obligatorios). El piso es `>=3.11` de `pyproject.toml` y la CI corre la matriz 3.11/3.12; antes decía 3.12+, que era más restrictivo que lo que el código y la CI exigen. Si alguna vez se sube el piso, se suben las tres cosas juntas, no sólo esta línea.
- Monte Carlo: N caminos suficientes para convergencia; nunca 1 trayectoria única.
- Decision analysis: separar modelado (Python) de presentación (dashboard/streamlit).
- Configurable values en config, no magic numbers.

## Criterios de diseño (pedidos por el dueño el 2026-10-18)
- **Simplicidad**: menos motores y mejor validados antes que motores nuevos. Un motor nuevo entra con
  validación contra una referencia externa o una forma cerrada, y su nivel en `core/engine_maturity.py`.
- **Escalabilidad**: cálculo vectorizado sobre los sorteos (sin bucles por sorteo en Python) y sin
  estado oculto: todo lo aleatorio recibe semilla.
- **Conectividad**: lo que otro repo o plataforma tenga que leer sale en un formato plano con esquema
  publicado y test de conformidad contra el productor (ej. `decisions/ledger.schema.json`), y los
  comandos del CLI que otros consumen tienen `--json`.

## Dónde va cada cosa
- `src/decision_maker/` es la librería instalable. Los casos de uso van en `analyses/` (y los scripts
  de investigación con red en `analyses/research/`), fuera del paquete.
- Una corrida nunca compromete nada: devuelve `commitment_draft`. Las decisiones reales se registran con
  `decision-maker decide` en `decisions/ledger.jsonl` (versionado) y se cierran con `close`.
- Tablero en `docs/Tablero.md`; bitácora en `docs/bitacora/AAAA-MM-DD.md`, un archivo por día.
