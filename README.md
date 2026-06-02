# Decision Maker Framework (v3.0)

Generic Python library for multi-criteria decision analysis under uncertainty. Combines Monte Carlo simulation, multi-criteria optimization, robust decision theory, AI-powered research, and interactive tools.

## Quick Start

```bash
uv sync
cp generic_template.py my_decision.py  # then edit
uv run python my_decision.py
```

Or use the CLI:

```bash
uv run decision-maker run config.yaml
uv run decision-maker what-if
```

## The Engines

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

## Modes

- **express** — MC + TOPSIS + Pareto (quick exploration)
- **standard** — express + decision theory + sensitivity + PROMETHEE uncertainty + robust + Borda
- **advanced** — standard + crisp PROMETHEE + Bayesian + Genetic + Bootstrap

## API & Dashboard

- **REST API** — `uv run uvicorn python.api.server:app` for programmatic access
- **Dashboard** — `uv run streamlit run python/dashboard/app.py` for interactive web UI

## CLI

```bash
uv run decision-maker --help
```

Commands: `run` (from YAML config), `what-if` (interactive REPL), `simulate` (parameter sweeps).

## Documentation

- [Index](docs/index.md) — overview and layout
- [Architecture](docs/architecture.md) — building blocks, runtime flow
- [Guide](docs/guide.md) — how to model a decision step by step
- [Changelog](CHANGELOG.md) — version history
- [Roadmap](ROADMAP_v3.0.md) — planned features
- [Examples](examples/) — reference implementations

## Requirements

- Python 3.11+
- `uv` (or `pip` + `requirements.txt`)
- Google Gemini API key (optional, for AI research)
