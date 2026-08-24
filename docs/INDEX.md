# Decision Maker Framework

Dual Python + Rust library for multi-criteria decision analysis under uncertainty.

## Context

Analyze decisions with 20+ quantitative methods — Monte Carlo, TOPSIS, PROMETHEE, Pareto, Bayesian, Genetic, Robust optimization, Sensitivity analysis, Bootstrap ranking, Rank aggregation, classical decision theory, Ergodicity/Kelly, plus a Learning System and Meta-Learning loop. A native Rust extension (`rust_core/`) runs the performance-critical Monte Carlo normalization. Optional AI research via Gemini.

## Quick Start

```bash
uv sync
cp src/decision_maker/analyses/_template.py my_decision.py  # then edit
uv run python my_decision.py
```

## Documents

- [Architecture](architecture.md) — building blocks, runtime flow, engines
- [Guide](guide.md) — how to model and run decisions
- [Changelog](../CHANGELOG.md) — version history
- [Roadmap](../ROADMAP_v3.0.md) — planned features
- [Examples](../examples/) — reference implementations
- [Jira tracking](jira/DM-25.md) — executive summary + work log (ID-1846)

## Project Layout

```
├── src/decision_maker/
│   ├── core/                 # engines (orchestrator, monte_carlo, topsis, …)
│   │   ├── orchestrator.py   # UnifiedDecisionFramework
│   │   ├── monte_carlo.py    # normalize=True uses rust_core bounds
│   │   ├── kelly.py          # Kelly criterion (field-benchmark win threshold)
│   │   ├── antifragile.py    # barbell, convexity, fragility, via_negativa
│   │   ├── outcome_tracker.py, calibration.py, decision_journal.py, adaptive_router.py  # learning system
│   │   ├── action_threshold.py, reasoning_trace.py, unknown_scanner.py, meta_calibration.py  # meta-learning
│   │   ├── decision_gates.py # veto: ergodicity, ruin, causal DAG, commitment
│   │   └── fuzzy_weighted_sum.py
│   ├── analyses/             # decision scripts (decision_concon, sophos_xg115, vlad25…)
│   ├── api/server.py         # FastAPI REST
│   ├── dashboard/app.py      # Streamlit UI
│   └── tests/                # 495 tests
├── rust_core/                # Rust crate decision_maker_core (pyo3 + rayon + ndarray)
├── examples/
├── docs/
├── jira/                     # local Jira tracking (DM-25.md ↔ ID-1846)
└── README.md
```

