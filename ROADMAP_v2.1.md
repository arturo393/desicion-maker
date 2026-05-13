# 🗺️ Roadmap v2.2: Generic Python Decision Library

Current State: We have pivoted from a specific "Mac Upgrade App" to a **Generic Decision Framework**. The Streamlit Dashboard has been removed to keep the core pure.

## ✅ Completed (v2.2)

### 5. 🔌 Full Engine Integration in All Modes
- **Goal**: `_check_scale_mismatch`, `_promethee_with_uncertainty`, `RobustOptimizer`, `RankAggregator` now run in `standard` mode (previously only `advanced`).
- **Goal**: `advanced` mode includes full rank aggregation across all 4 methods (TOPSIS, MC, PROMETHEE crisp, PROMETHEE uncertainty).
- **Files**: `python/core/orchestrator.py`
- **Status**: ✅ Shipped

### 6. 📋 Test Suite Updated
- **Goal**: All 199 tests pass across all engines and modes.
- **Files**: `python/tests/test_orchestrator.py`, `python/tests/test_integration_bdd.py`
- **Status**: ✅ Shipped

## 🚀 Phase 1: Smart Inputs (CLI & Library)

### 1. 🤖 AI-Powered Parameter Estimation (Python API)
*   **Goal**: `opt.add_variable("Price", DistributionType.AI_FETCH)`
*   **Mechanism**: The framework calls Gemini API to fetch real-world distributions for a given label.

### 2. ⚖️ Interactive AHP (CLI Tool)
*   **Goal**: A command-line wizard to set weights scientifically.
*   **Usage**: `uv run python tools/set_weights.py`
    *   Asks: "What is more important: A or B?"
    *   Output: Prints a dictionary of weights to copy into your script.

## 🔮 Phase 2: Advanced Reporting

### 3. 📊 Static Visualizations (Matplotlib/Plotly)
*   **Goal**: Generate PNG/HTML charts without a server.
*   **Usage**: `framework.save_charts(output_dir="plots/")`
*   **Charts**:
    *   Pareto Efficient Frontier (Scatter Plot).
    *   Sensitivity Tornado Chart.
    *   Risk Distribution Histograms.

### 4. 📉 Dynamic Utility Functions
*   **Goal**: Support non-linear utility (Diminishing returns).
*   **Code**: `framework.add_factor(Factor("Money", utility_func=log_utility))`

---

> **Focus:** Make the Python API as flexible and powerful as possible for developers and analysts.
