---
aliases: [Decision Maker Docs, Índice, Docs]
tags: [narrative, lumina, quant, architecture]
id: DOC-INDEX
title: "Decision Maker Documentation Portal"
type: narrative
category: governance
status: stable
related: ["[[decision-maker-moc]]", "[[database-hub]]", "[[kanban]]", "[[architecture]]", "[[guide]]"]
created: 2026-08-10
updated: 2026-10-01
---

# Decision Maker Framework

Dual Python + Rust library for multi-criteria decision analysis under uncertainty.

## Context

Analyze decisions with 20+ quantitative methods — Monte Carlo, TOPSIS, PROMETHEE, Pareto, Bayesian, Genetic, Robust optimization, Sensitivity analysis, Bootstrap ranking, Rank aggregation, classical decision theory, Ergodicity/Kelly, plus a Learning System and Meta-Learning loop. A native Rust extension (`rust_core/`) is built and tested but **not imported by the engine, by decision (ADR-001)**: it gets wired in only once its `success_rate` divergence from the Python engine is resolved. Monte Carlo runs in Python/NumPy; see [[adr/001-use-rust-for-math-engine]]. Optional AI research via Gemini.

## Quick Start

```bash
uv sync
cp src/decision_maker/analyses/_template.py my_decision.py  # then edit
uv run python my_decision.py
```

## Documents

**One vault, not two layers.** The Obsidian vault root is `docs/` itself — its config lives at
`docs/.obsidian/` — and this narrative sits inside it as three ordinary notes. There is no separate
"vault" to cross into; the two layers only ever described two *reading modes* of the same notes.

| Note | What it is | Read it when |
|---|---|---|
| **This file** | The front door: what the framework is, plus the map below | First visit |
| [[architecture]] | The narrative — runtime flow, engine table, key decisions | Learning the internals |
| [[guide]] | The narrative — how to model and run one decision | Writing your first analysis |
| [[decision-maker-moc]] | **The vault's primary index** — one card per module | Looking up a module, or working in Obsidian |
| [[database-hub]] | **Database Hub** — relational catalog, Dataview queries and database tables | Exploring the documentation as a database |
| [[kanban]] | **Kanban Board** — repository tasks, backlog and sprints | Tracking development status |

The MOC and Database Hub form the navigation layer; the three notes above are the runtime story. They are not
alternatives: [[decision-maker-moc]] indexes the notes, and [[database-hub]] exposes them as structured database records. Where they describe the same engine, **the code is the authority**: both were found
making claims the code contradicted, and the vault was corrected against the source.

- [[database-hub]] — structured database views and Dataview queries
- [[kanban]] — interactive repository Kanban board
- [[decision-analyses]] — catalog of applied real-world decision scripts
- [[legacy-docs]] — historical archive and specifications outside docs
- [[roadmap]] — quantitative development roadmap (source: [ROADMAP_v3.0.md](../ROADMAP_v3.0.md))
- [[changelog]] — version history log (source: [CHANGELOG.md](../CHANGELOG.md))
- [[unified-orchestrator]] — the `UnifiedDecisionFramework` behind the quick start
- [[monte-carlo-engine]] — the simulation every other engine consumes
- [[note-schema]] — how a note in this vault is written (tags, skeleton)
- [Examples](../examples/mac_upgrade_comparison.py) — reference implementations
- [Jira tracking](../jira/DM-25.md) — executive summary + work log (ID-1846)

> The four markdown links above leave the vault (they resolve to `../CHANGELOG.md`,
> `../ROADMAP_v3.0.md`, `../examples/…`, `../jira/DM-25.md`). They stay markdown links **on purpose**:
> they point at repo files, not at notes, so there is no wikilink target to resolve. Do not convert
> them — Obsidian cannot open a note that does not exist in the vault.

## Archive

- [[reorganization/README|Reorganización]] — historical records of the 2026 reorganization
- [[sw-diagnosticoremoto/README|sw-diagnosticoremoto]] — remote diagnostics: power supply analysis and mine monitoring proposal

> Both are **folders**, and a folder is not a note. The `README.md` inside each is the closest thing
> to a landing page, so that is what the link points at.

## Project Layout

```
├── src/decision_maker/
│   ├── core/                 # engines (orchestrator, monte_carlo, topsis, …)
│   │   ├── orchestrator.py   # UnifiedDecisionFramework
│   │   ├── monte_carlo.py    # normalize=True computes its own global bounds
│   │   ├── kelly.py          # Kelly criterion (field-benchmark win threshold)
│   │   ├── antifragile.py    # barbell, convexity, fragility, via_negativa
│   │   ├── outcome_tracker.py, calibration.py, decision_journal.py, adaptive_router.py  # learning system
│   │   ├── action_threshold.py, reasoning_trace.py, unknown_scanner.py, meta_calibration.py  # meta-learning
│   │   ├── decision_gates.py # veto: ergodicity, ruin, causal DAG, commitment
│   │   └── fuzzy_weighted_sum.py
│   ├── analyses/             # decision scripts (decision_concon, sophos_xg115, vlad25…)
│   ├── api/server.py         # FastAPI REST
│   ├── dashboard/app.py      # Streamlit UI
│   └── tests/                # 551 tests
├── rust_core/                # Rust crate decision_maker_core (pyo3 + rayon)
├── examples/
├── docs/                     # Obsidian vault root (config: docs/.obsidian/)
├── jira/                     # local Jira tracking (DM-25.md ↔ ID-1846)
└── README.md
```

