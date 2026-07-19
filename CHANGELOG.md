# Changelog

All notable changes to this project will be documented in this file.

## [v3.0] - 2026-06-02

### 🧠 10 New Decision Engines
- **Antifragile** — Taleb-inspired barbell strategy, convexity/optionality, fragility indexing, and via negativa analysis.
- **Group Decision** — Multi-stakeholder weight aggregation into consensus rankings using statistical methods.
- **Information Theory** — Mutual information analysis to quantify non-linear influence of each factor on scores.
- **Portfolio Optimization** — Mean-variance resource allocation across options with efficient frontier.
- **What-If Analysis** — Interactive engine to tweak weights/directions and see scores recomputed in real time (includes REPL).
- **Weight Derivation** — Swing weighting, AHP pairwise comparison, and PAPRIKA to derive weights from human judgment.
- **Explainability** — Factor-contribution waterfalls, counterfactuals, and narrative generation for human-readable decision reports.
- **Topological Data Analysis** — MDS/Isomap embedding, clustering, and ranking stability analysis.
- **Visualization Engine** — Matplotlib/seaborn plots (Pareto frontier, tornado, distributions) with dark theme.
- **Decision Registry** — SQLite-backed persistent store for querying, comparing, and tracking outcomes across analyses.

### 🌐 API & Dashboard
- **REST API** (`python/api/server.py`) — FastAPI server exposing the full decision framework via Pydantic-schematized endpoints.
- **Web Dashboard** (`python/dashboard/app.py`) — Interactive frontend for running analyses and visualizing results.

### 🖥️ CLI Overhaul
- **`decision-maker` CLI** — Typer-based entry point with subcommands for running configs and distribution listing.
- **`run` command** — Execute decision configs from YAML/JSON files, with `--what-if` flag for interactive REPL mode.
- **`list-distributions` command** — Show all available probability distributions and their parameters.

### ⚙️ Core Improvements
- Removed legacy `unified_decision_framework.py` — logic fully migrated into `orchestrator.py`.
- Cleaned up old test artifacts (`old_framework.py`, `old_gemini.py`, `old_gemini_flash.py`, `old_structure.py`, `test_integration_bdd.py`).
- Updated reporting engine with enhanced HTML templates.
- Improved Monte Carlo and robust optimization internals.
- Enhanced genetic optimizer convergence logic.

### 🧪 Test Suite
- **322 tests passing** across all 24 engines.
- New test suites for: antifragile, explainability, group_decision, information_theory, portfolio, registry, topology, visualization, weight_derivation, what_if.
- Updated existing test suites for genetic, monte_carlo, robust, and unified workflows.

### 📦 Dependencies
- Added `matplotlib`, `seaborn`, `scikit-learn`, `aiohttp`, `pydantic`, `typer`, `jinja2`.
- Added optional `google-genai` dependency for AI-powered research.

## [v2.2] - 2026-05-12

### 🔌 Full Engine Integration
-   **PROMETHEE with uncertainty** (`_promethee_with_uncertainty`) now runs in `standard` mode (previously only `advanced`), averaging PROMETHEE net flows across p5/mean/p95 percentiles.
-   **Robust Optimizer** now runs in `standard` mode, computing worst-case scores under weight shocks.
-   **Rank Aggregation (Borda)** now runs in both `standard` and `advanced` modes. `standard` aggregates 3 methods (TOPSIS, MC, PROMETHEE uncertainty); `advanced` aggregates 4 (adds crisp PROMETHEE).
-   **Scale mismatch detection** (`_check_scale_mismatch`) warns when factor scales differ by >10x.
-   Weights and max/min bools are computed once and reused across all engines.

### 🧪 Test Suite
-   Updated `test_orchestrator.py` and `test_integration_bdd.py` to verify new standard-mode engines.
-   **199 tests passing** across all 18 engines.

### 📊 Comparison Script
-   Added `examples/mac_upgrade_comparison.py` to run the Mac upgrade case in all 3 modes (express/standard/advanced) and compare results side-by-side.

## [v2.1] - 2026-02-17

### 🚀 Major Improvements
-   **Pivot to Generic Python Library**: The project is no longer a specific Mac Upgrade app but a generic decision support framework.
-   **New Generic Template**: Added `generic_template.py` as the primary entry point for users to model *any* decision.
-   **Refactored Examples**: Moved `cases/mac_upgrade_decision.py` to `examples/mac_upgrade_example.py`.

### 🗑️ Removals
-   **Removed Web UI (`app.py`)**: Streamlit Dashboard removed to focus on a pure Python library experience.
-   **Removed `cases/` directory**: Replaced by `examples/`.

### ✨ New Features
-   **Interactive AHP (CLI)**: Although the Web UI was removed, the `AHPHelper` class remains available for programmatic weight calculation.
-   **Frankenstein Logic**: `GeneticOptimizer` now calculates the theoretical maximum score based on the best traits of all options.

## [v2.0] - 2026-02-13

### Added
-   **Unified Decision Framework**: Consolidated 18 methodologies into a single Python class.
-   **Advanced Methodologies**: Added Pareto Analysis, Sensitivity Analysis, and Future Horizons (Bayesian, ROA, MDP, Genetic).
-   **AI Integration**: Added support for Google Gemini to provide qualitative insights.
