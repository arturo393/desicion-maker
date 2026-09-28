---
aliases: [Reporting and Registry, Reporting_and_Registry]
tags: [module, lumina, quant, infrastructure, storage, reporting]
id: MOD-REGISTRY
title: "Reporting and SQLite Registry"
type: module
category: infrastructure
status: stable
module: "decision_maker.core.reporting"
class: "ReportData"
related: ["[[data-models-and-schemas]]", "[[unified-orchestrator]]", "[[topological-data-analysis]]"]
created: 2026-08-10
updated: 2026-09-27
---

## `reporting.py`

> Renders analysis results as JSON, Markdown, HTML or terminal output.
> Uso: `from decision_maker.core.reporting import save_report, ReportData`
> No: perform the decision matrix computations it is reporting on.

`save_report(data: ReportData) -> dict[str, str]` is the module-level entry point. It takes
**one** argument and writes all four formats in one call — `save_json_report` (`reporting.py:188`),
`save_markdown_report` (`:218`), the HTML writer (`:316`) and the terminal writer (`:400`) — returning
the path of each. It fills `results_dir` and `timestamp` on the `ReportData` if they are unset.

### Clases Principales

- **`ReportData`**: Everything a report needs, in one bundle (Parameter Object).

## `registry.py`

> SQLite-backed store for decision configurations and reusable templates.
> Usage: `from decision_maker.core.registry import DecisionRegistry`
> Does NOT: execute decision calculations or generate reports.

### Clases Principales

- **`SaveDecisionRequest`**: One decision record destined for persistence (Parameter Object).
- **`SaveTemplateRequest`**: One reusable template record (Parameter Object).
- **`DecisionRegistry`**: The public surface. `sqlite3` directly — no ORM, no migration layer.

> `_Encoder` is a private `json.JSONEncoder` subclass (`registry.py:335`) used to serialise the request objects, and it is excluded from `__all__`. An earlier version of this note listed it as a principal class, which inverted the public surface: it told a reader that the module's third-class detail was one of its three main ideas.

## `db.py`

> SQLAlchemy engine, session factory and idempotent schema initialisation for the SQLModel tables.
> Usage: `from decision_maker.core.db import create_session, ensure_initialized`
> Does NOT: define the table schemas — see `db_models` — or run Alembic migrations.

### Clases Principales

- None. This module exposes module-level functions, not classes: `ensure_initialized` (`db.py:24`) creates the tables if they are missing, and `create_session` (`db.py:35`) hands out a session. Both are idempotent by design, so calling initialisation twice is not an error.
