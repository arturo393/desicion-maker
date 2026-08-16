---
aliases: [Reporting and Registry]
tags: [module, component]
---

# Reporting and Registry

## `reporting.py`

> Report generation suite saving analysis outcomes to JSON, Markdown, HTML, and terminal outputs.
Usage: from decision_maker.core.reporting import save_report, ReportData
Does NOT: Perform primary decision matrix computations or optimizations.

### Clases Principales
- **`ReportData`**: Bundles all data needed for report generation.

---
## `registry.py`

> Registry for saving, retrieving, and managing decision configurations and templates.
Usage: from decision_maker.core.registry import DecisionRegistry
Does NOT: Execute decision calculations or generate reports.

### Clases Principales
- **`SaveDecisionRequest`**: Bundles a decision record for persistence (Parameter Object).
- **`SaveTemplateRequest`**: Bundles a template record for persistence (Parameter Object).
- **`DecisionRegistry`**: SQLite-backed persistent registry for decision analyses.
- **`_Encoder`**: Sin docstring.

---
## `db.py`

> SQLAlchemy engine, session factory, and idempotent schema initialization.
Usage: from decision_maker.core.db import create_session, ensure_initialized
Does NOT: Define table schemas (see db_models) or run Alembic migrations.


---
