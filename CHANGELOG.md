# Changelog

All notable changes to this project will be documented in this file.

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
