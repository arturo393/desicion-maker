# GitHub Issues Update (v2.1)

Status update for the repository issues following the pivot to a Generic Python Library.

## ✅ Completed / Closed

### [Issue #1] Add New Distributions
-   **Status**: Closed.
-   **Resolution**: Implemented `DistributionType.NORMAL`, `TRIANGULAR`, `LOGNORMAL`, `GAMMA`, `DETERMINISTIC`, `UNIFORM` in `UnifiedDecisionFramework`.

### [Issue #3] Implement Unit Tests
-   **Status**: Closed.
-   **Resolution**: Added `tests/` directory with `test_core.py`. Verified functionality of basic engines.

### [Issue #4] Create Example Case: Mac Upgrade
-   **Status**: Closed.
-   **Resolution**: Moved `cases/mac_upgrade_decision.py` to `examples/mac_upgrade_example.py` to convert it from a core feature to just an example.

### [Issue #5] Remove Web UI (Streamlit)
-   **Status**: Closed (New).
-   **Resolution**: Deleted `python/app.py` to streamline the library for developers.

---

## 🚧 In Progress / Roadmap

### [Issue #6] Generic CLI Tool for AHP
-   **Priority**: High.
-   **Description**: Create a command-line utility (`tools/set_weights.py`) to replace the functionality of the "Weighting Studio" tab.

### [Issue #7] AI Parameter Fetching
-   **Priority**: Medium.
-   **Description**: Implement `opt.add_variable(type=AI_FETCH)` to automatically retrieve market data using Gemini.
