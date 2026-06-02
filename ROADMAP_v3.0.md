# 🗺️ Roadmap v3.0: Decision Intelligence Framework

**Current State**: v3.0 ships 24 decision engines, a REST API, web dashboard, and CLI. The core library is feature-complete for most multi-criteria decision analysis workflows.

## ✅ Completed (v3.0)

### 10 New Engines
| Engine | Description |
|--------|-------------|
| Antifragile | Barbell strategy, convexity, fragility indexing, via negativa |
| Group Decision | Multi-stakeholder weight aggregation and consensus ranking |
| Information Theory | Mutual information factor influence analysis |
| Portfolio | Mean-variance resource allocation |
| What-If | Interactive weight/direction tweaking with live scores |
| Weight Derivation | Swing, AHP, PAPRIKA from human judgment |
| Explainability | Waterfall charts, counterfactuals, narrative reports |
| Topology | MDS/Isomap clustering and ranking stability |
| Visualization | Publication-ready plots (Pareto, tornado, histograms) |
| Registry | SQLite-backed persistent decision store |

### API & Dashboard
- **REST API** — FastAPI server with full Pydantic schemas
- **Web Dashboard** — Streamlit interactive frontend

### CLI
- Typer-based `decision-maker` CLI with `run`, `what-if`, `simulate` commands

### Quality
- **322 tests passing** across all engines
- Cleaned up legacy code and old test artifacts

## 🚀 Next: v3.1+

### 1. 🤖 AI-Powered Parameter Estimation
- `add_variable("Price", DistributionType.AI_FETCH)` — Gemini fetches real-world distributions for a label.
- **Status**: Design phase

### 2. ⚖️ Interactive AHP CLI Wizard
- Guided pairwise comparison wizard: "What is more important: A or B?"
- Outputs a ready-to-use weights dictionary.
- **Status**: `AHPHelper` class exists; CLI wizard pending

### 3. 📉 Dynamic Utility Functions
- Non-linear utility support (diminishing returns, S-curves).
- `add_factor(Factor("Money", utility_func=log_utility))`
- **Status**: Not started

### 4. 📊 Enhanced Visualization Suite
- Interactive Plotly charts (replace static matplotlib).
- Export to PNG/SVG/HTML.
- **Status**: Static matplotlib done; interactive pending

### 5. 🐳 Docker Deployment
- Dockerfile for API server and dashboard.
- docker-compose for one-command deploy.
- **Status**: Not started

---

> **Focus**: Polish the interactive experience (AI-assisted inputs, CLI wizards, dynamic reporting).
