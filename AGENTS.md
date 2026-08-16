# Decision Maker Framework - Agent Guidelines

## Project Map (hermanos del dominio)
Este repo pertenece al dominio **Lumina** (cuantitativo), junto con:
- `../monteCarlo` — bot de trading C++ que comparte la base conceptual Monte Carlo
  (backtest, simulación de caminos, walk-forward). Si una tarea toca validación de
  edge/riesgo en trading, consultar `monteCarlo` (AGENTS.md es la referencia).
- `../../dev-agents` — conocimiento general SE/firmware/brands (referencia global).
- `../../SafetyMind/` — dominio SEPARADO (edge AI industrial). No mezclar trabajo.
- `../../curriculum` — proyecto personal, no relacionado.

Regla: si una tarea toca modelado de riesgo/decisión Monte Carlo para trading,
revisar `monteCarlo` primero. Si toca hardware/edge AI, NO asumir relación con
SafetyMind sin preguntar.

## Build & Test
```bash
# Python library, uv-based
uv sync
uv run pytest          # run unit tests
```

## Conventions
- Python 3.12+, typed (type hints obligatorios).
- Monte Carlo: N caminos suficientes para convergencia; nunca 1 trayectoria única.
- Decision analysis: separar modelado (Python) de presentación (dashboard/streamlit).
- Configurable values en config, no magic numbers.
