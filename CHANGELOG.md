# Changelog

All notable changes to this project will be documented in this file.

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
