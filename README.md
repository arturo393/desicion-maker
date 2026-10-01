---
aliases: [Decision Maker README, Project Overview]
tags: [readme, lumina, quant, overview]
id: ROOT-README
title: "Decision Maker Framework"
type: narrative
category: overview
status: active
related: ["[[docs/index|index]]", "[[docs/database-hub|database-hub]]", "[[docs/kanban|kanban]]", "[[docs/architecture|architecture]]"]
created: 2026-08-10
updated: 2026-10-01
---

# Decision Maker Framework (v3.1)

Dual Python + Rust library for multi-criteria decision analysis under uncertainty. Combines Monte Carlo simulation, multi-criteria optimization, robust decision theory, AI-powered research, learning/meta-learning loops, and interactive tools. The engine runs in Python/NumPy. The `rust_core/` crate (pyo3 + rayon) implements the Monte Carlo normalization too, but it is not on the execution path — nothing under `src/decision_maker/core/` imports it (see [docs/adr/001-use-rust-for-math-engine.md](docs/adr/001-use-rust-for-math-engine.md)).

## Quick Start

```bash
uv sync
cp src/decision_maker/analyses/_template.py my_decision.py  # then edit
uv run python my_decision.py
```

Or use the CLI:

```bash
uv run decision-maker run --config config.yaml
uv run decision-maker run --config config.yaml --what-if   # interactive REPL after analysis
uv run decision-maker list-distributions
```

## The Engines

Module index, not an engine count: 19 are routable (`ENGINE_UNIVERSE` in `src/decision_maker/core/adaptive_router.py`).

| Method | What it does |
|--------|-------------|
| Monte Carlo | Simulates N scenarios per option (p5/mean/p95) |
| Fuzzy TOPSIS | Multi-criteria ranking with uncertainty |
| PROMETHEE II | Net flow outranking (crisp + uncertainty-aware) |
| Pareto | Efficient frontier, dominated options |
| Decision Theory | Maximax, Maximin, Hurwicz, Laplace, Minimax Regret |
| Sensitivity | Weight/score shock analysis |
| Robust | Worst-case ranking under parameter shocks |
| Bayesian | Posterior probability each option is best |
| Genetic | Evolves the ideal composite option |
| Bootstrap | Confidence intervals on rankings |
| Rank Aggregation | Borda consensus across methods |
| AI Agent | External research via Gemini |
| What-If | Interactive weight/score tweaking with live recomputation |
| Antifragile | Barbell strategy, convexity, fragility indexing, via negativa |
| Group Decision | Multi-stakeholder consensus ranking |
| Information Theory | Mutual information factor influence analysis |
| Portfolio | Mean-variance resource allocation |
| Weight Derivation | Swing, AHP, PAPRIKA from human judgment |
| Explainability | Waterfall charts, counterfactuals, narrative reports |
| Topology | MDS/Isomap clustering and stability analysis |
| Visualization | Publication-ready plots (Pareto, tornado, distributions) |
| Registry | SQLite-backed persistent decision store |
| Rust Math Core | Monte Carlo Min-Max normalization in Rust (pyo3 + rayon); built and tested, not imported by the framework |
| Ergodicity | Time-average vs ensemble growth, ruin probability, Kelly criterion |
| Learning System | Outcome tracking, confidence calibration, decision journal, adaptive routing |
| Meta-Learning | Action threshold, reasoning trace, unknown scanner, meta-calibration |
| Decision Gates | Veto power: ergodicity, ruin, causal DAG, commitment |

## Modes

- **express** — MC + TOPSIS + Pareto (quick exploration)
- **standard** — express + decision theory + sensitivity + PROMETHEE uncertainty + robust + Borda
- **advanced** — standard + crisp PROMETHEE + Bayesian + Genetic + Bootstrap

## API & Dashboard

- **REST API** — `uv run uvicorn src.decision_maker.api.server:app` for programmatic access
- **Dashboard** — `uv run streamlit run src/decision_maker/dashboard/app.py` for interactive web UI

## CLI

```bash
uv run decision-maker --help
```

Commands: `run` (from YAML config, with `--what-if` for interactive REPL), `list-distributions` (show available distributions).

## Documentation

- [Index](docs/index.md) — overview and layout
- [Database Hub](docs/database-hub.md) — Obsidian relational database views, tables & Dataview queries
- [Kanban Board](docs/kanban.md) — interactive project Kanban board
- [Architecture](docs/architecture.md) — building blocks, runtime flow
- [Guide](docs/guide.md) — how to model a decision step by step
- [Changelog](CHANGELOG.md) — version history
- [Roadmap](ROADMAP_v3.0.md) — planned features
- [Examples](examples/) — reference implementations

## Requirements

- Python 3.11+
- `uv` (`uv.lock` is versioned)
- Rust toolchain (optional, only to build and test `rust_core`; the framework does not import it)
- Google Gemini API key (optional, for AI research)
