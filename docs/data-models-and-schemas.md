---
aliases: [Data Models and Schemas, Data_Models_and_Schemas]
tags: [module, lumina, quant, infrastructure, storage]
id: MOD-SCHEMAS
title: "Data Models and Normalization Schemas"
type: module
category: infrastructure
status: stable
module: "decision_maker.core.models"
class: "DecisionOption"
related: ["[[unified-orchestrator]]", "[[reporting-and-registry]]"]
created: 2026-08-10
updated: 2026-09-27
---

## `models.py`

> Domain models for options, factors, uncertainty and the statistics that come back out of an analysis.
> Usage: `from decision_maker.core.models import DecisionOption`
> Does NOT: implement execution logic or orchestration.

### Clases Principales

- **`DistributionType`**: `StrEnum` of the supported distributions — `DETERMINISTIC`, `NORMAL`, `UNIFORM`, `TRIANGULAR`, `BETA`, `LOGNORMAL`, `GAMMA`, `EXPONENTIAL`, `POISSON`, `BERNOULLI`. A `StrEnum` so the value serialises as its own name in a config file.
- **`UncertainVariable`**: One named variable of an option and the distribution it is drawn from. `params` is positional, so its meaning depends on `dist_type` — `[mean, std]` for NORMAL, `[min, mode, max]` for TRIANGULAR.
- **`Factor`**: What matters in the decision: name, `weight` (must be > 0), `maximize`, `category`, and optional `stakeholder_weights` for group decisions.
- **`Statistics`**: What one option produced. Carries the percentiles, `success_rate`, `factor_stats` and — crucially — `raw_scores` and `raw_factor_data`, both `exclude=True` so they stay out of a JSON dump while remaining available in memory for downstream engines.
- **`DecisionOption`**: A candidate: name, description, and a `dict` of `UncertainVariable` keyed by factor name.

## `schemas.py`

> Pydantic models describing the YAML/JSON payload a whole decision is configured from.
> Usage: `from decision_maker.core.schemas import RootConfig`
> Does NOT: execute decision algorithms or manage database storage.

### Clases Principales

- **`VariableConfig`**: Distribution name plus positional params for one variable, defaulting to `deterministic`.
- **`OptionConfig`**: Name, description and the variable mapping.
- **`FactorConfig`**: Name, `weight` (≥ 0), direction, category.
- **`DecisionConfig`**: A whole decision — name, `mode`, `simulations`, factors, options, and optional `correlation` and `promethee_pref_type`. Both collections have `min_length=1`, so an empty decision cannot be constructed.
- **`RootConfig`**: Top-level wrapper holding a single `DecisionConfig`.

> The entry point for validation lives elsewhere: `validate_config` is defined in `config_runner.py:36`, not in this module. `schemas.py:9-15` exports the five pydantic models and nothing else — an earlier version of this note pointed here for `validate_config`, which does not exist in this file.

## `db_models.py`

> SQLModel table definitions for persisted analysis sessions and their outcomes.
> Usage: `from decision_maker.core.db_models import AnalysisSession, OutcomeRecord`
> Does NOT: open database connections or run migrations.

### Clases Principales

- **`AnalysisSession`**: A stored run. `id` is a generated UUID; `factors_json` and `options_json` are JSON columns holding the inputs as they were at that moment, so a session is replayable.
- **`OutcomeRecord`**: The world answering back — `actual_winner`, `actual_score`, `accuracy_percentage`, plus optional `predicted_winner`/`confidence` and notes. This is the table the calibration and meta-learning layers read.
