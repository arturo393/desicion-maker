# Decision Maker Framework (v2.2)

Generic Python library for multi-criteria decision analysis under uncertainty. Combines Monte Carlo simulation, multi-criteria optimization, robust decision theory, and AI-powered research.

## Quick Start

```bash
uv sync
cp generic_template.py my_decision.py  # then edit
uv run python my_decision.py
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

## Modes

- **express** — MC + TOPSIS + Pareto (quick exploration)
- **standard** — express + decision theory + sensitivity + PROMETHEE uncertainty + robust + Borda
- **advanced** — standard + crisp PROMETHEE + Bayesian + Genetic + Bootstrap

## Documentation

- [Index](docs/index.md) — overview and layout
- [Architecture](docs/architecture.md) — building blocks, runtime flow
- [Guide](docs/guide.md) — how to model a decision step by step
- [Changelog](CHANGELOG.md) — version history
- [Roadmap](ROADMAP_v2.1.md) — planned features
- [Examples](examples/) — reference implementations

## Requirements

- Python 3.11+
- `uv` (or `pip` + `requirements.txt`)
- Google Gemini API key (optional, for AI research)
