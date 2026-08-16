---
aliases: [Data Models and Schemas]
tags: [module, component]
---

# Data Models and Schemas

## `models.py`

> [What it does] Data models and type definitions for decision options, factors, distributions, and statistics.
[How to use it] Import necessary models (e.g., from decision_maker.core.models import DecisionOption)
[What it DOESN'T do] Does not implement execution logic or orchestration.

### Clases Principales
- **`DistributionType`**: Sin docstring.
- **`UncertainVariable`**: Sin docstring.
- **`Factor`**: Sin docstring.
- **`Statistics`**: Sin docstring.
- **`DecisionOption`**: Sin docstring.

---
## `schemas.py`

> Validation rules and JSON schemas for validating decision configuration payloads.
Usage: from decision_maker.core.schemas import validate_config
Does NOT: Execute decision algorithms or manage database storage.

### Clases Principales
- **`VariableConfig`**: Sin docstring.
- **`OptionConfig`**: Sin docstring.
- **`FactorConfig`**: Sin docstring.
- **`DecisionConfig`**: Sin docstring.
- **`RootConfig`**: Sin docstring.

---
## `db_models.py`

> SQLModel table definitions for analysis sessions and outcome records.
Usage: from decision_maker.core.db_models import AnalysisSession, OutcomeRecord
Does NOT: Open database connections or run migrations.

### Clases Principales
- **`AnalysisSession`**: Sin docstring.
- **`OutcomeRecord`**: Sin docstring.

---
