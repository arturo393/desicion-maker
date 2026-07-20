# Decision Maker Framework

Generic Python library for multi-criteria decision analysis under uncertainty.

## Context

Analyze decisions with 18+ quantitative methods — Monte Carlo, TOPSIS, PROMETHEE, Pareto, Bayesian, Genetic, Robust optimization, Sensitivity analysis, Bootstrap ranking, Rank aggregation, and classical decision theory. Optional AI research via Gemini.

## Quick Start

```bash
uv sync
cp python/analyses/_template.py my_decision.py  # then edit
uv run python my_decision.py
```

## Documents

- [Architecture](architecture.md) — building blocks, runtime flow, engines
- [Guide](guide.md) — how to model and run decisions
- [Changelog](../CHANGELOG.md) — version history
- [Roadmap](../ROADMAP_v3.0.md) — planned features
- [Examples](../examples/) — reference implementations

## Project Layout

```
├── generic_template.py       # start here
├── python/
│   ├── core/                 # engines
│   │   ├── orchestrator.py   # UnifiedDecisionFramework
│   │   ├── monte_carlo.py
│   │   ├── topsis.py
│   │   ├── promethee.py
│   │   ├── pareto.py
│   │   ├── sensitivity.py
│   │   ├── bayesian.py
│   │   ├── genetic.py
│   │   ├── decision_theory.py
│   │   ├── robust.py
│   │   ├── bootstrap.py
│   │   ├── aggregator.py
│   │   ├── reporting.py
│   │   ├── models.py
│   │   ├── ahp.py
│   │   ├── config_runner.py
│   │   └── gemini_agent.py
│   └── tests/                # 199+ tests
├── examples/
│   ├── mac_upgrade_example.py
│   └── mac_upgrade_comparison.py
├── docs/
├── results/
└── README.md
```
