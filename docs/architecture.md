---
aliases: [Architecture, Arquitectura]
tags: [narrative, lumina, quant, architecture]
id: DOC-ARCH
title: "Decision Maker Architecture"
type: architecture
category: governance
status: stable
related: ["[[index]]", "[[guide]]", "[[unified-orchestrator]]", "[[adr/001-use-rust-for-math-engine]]"]
created: 2026-08-10
updated: 2026-10-01
---

# Architecture

Dual Python + Rust framework for multi-criteria decision analysis under uncertainty. 19 motores ruteables, 554 tests (plus a smoke suite that runs every analysis: `uv run pytest -m smoke`). The Monte Carlo engine runs in Python/NumPy; the `rust_core/` crate implements the same normalization but is not on the execution path (see [[adr/001-use-rust-for-math-engine]]).

## Building Blocks

### Entry Point: `UnifiedDecisionFramework`

```python
from decision_maker.core.orchestrator import UnifiedDecisionFramework
fw = UnifiedDecisionFramework(correlation_matrix=None)
fw.add_factor(Factor(...))
fw.add_option(DecisionOption(...))
results = await fw.run_analysis(mode="standard")
```

### Engines

| Engine | File | Purpose | Mode |
|--------|------|---------|------|
| Game Theory | `game_theory.py` | Pure Nash equilibria, competitive-robustness labels | advanced |
| Real Options (ROA) | `roa.py` | Flexibility value via Black-Scholes | advanced |
| ML Surrogate | `ml_surrogate.py` | Neural/tree surrogates replacing full Monte Carlo in genetic passes | advanced |
| Monte Carlo | `monte_carlo.py` | Stochastic simulation of N scenarios | all |
| TOPSIS | `topsis.py` | Fuzzy multi-criteria ranking | all |
| Pareto | `pareto.py` | Efficient frontier / dominated options | all |
| Decision Theory | `decision_theory.py` | Maximax, Maximin, Hurwicz, Laplace, Minimax Regret | standard+ |
| Sensitivity | `sensitivity.py` | Weight/score shock analysis | standard+ |
| PROMETHEE (uncertainty) | `promethee.py` | Averaged net flow across p5/mean/p95 | standard+ |
| Robust | `robust.py` | Worst-case score under weight shocks | standard+ |
| Rank Aggregation | `aggregator.py` | Borda count across methods | standard+ |
| PROMETHEE II (crisp) | `promethee.py` | Deterministic net flow | advanced |
| Bayesian | `bayesian.py` | Posterior probability of being best | advanced |
| Genetic | `genetic.py` | Evolve ideal composite option | advanced |
| Bootstrap | `bootstrap.py` | Confidence intervals on rankings | advanced |
| AI Agent | `gemini_agent.py` | External research via Gemini (API key) or the Antigravity CLI `agy` (`agy_backend.py`, `DM_LLM_BACKEND`) | advanced |
| What-If | `what_if.py` | Interactive weight/score tweaking with live recomputation | standalone |
| Antifragile | `antifragile.py` | Barbell strategy, convexity, fragility indexing, via negativa | standalone |
| Group Decision | `group_decision.py` | Multi-stakeholder consensus ranking | standalone |
| Information Theory | `information_theory.py` | Mutual information factor influence analysis | standalone |
| Portfolio | `portfolio.py` | Mean-variance resource allocation | standalone |
| Weight Derivation | `weight_derivation.py` | Swing, AHP, PAPRIKA from human judgment | standalone |
| Explainability | `explainability.py` | Waterfall charts, counterfactuals, narrative reports | standalone |
| Topology | `topology.py` | MDS/Isomap embedding, clustering, ranking stability | standalone |
| Visualization | `visualization.py` | Matplotlib/seaborn plots (Pareto, tornado, distributions) | standalone |
| Registry | `registry.py` | SQLite-backed persistent decision store | standalone |
| Rust Math Core | `rust_core/` (Rust) | Native Monte Carlo Min-Max normalization (pyo3 + rayon). **Not imported by any `core/` module** — see [[adr/001-use-rust-for-math-engine]] | library |
| Ergodicity | `ergodicity.py` | Time-average vs ensemble growth, ruin probability | standalone |
| Kelly Criterion | `kelly.py` | Optimal bet sizing under uncertainty (field-benchmark win threshold) | standalone |
| Fuzzy Weighted Sum | `fuzzy_weighted_sum.py` | Weighted-sum aggregation with fuzzy membership | standalone |

This table is a **module index**, not an engine count. Of the rows above, 19 are engines the router dispatches to and their names come from `ENGINE_UNIVERSE` in `core/adaptive_router.py`; the rest are analysis, presentation or infrastructure modules the router never calls (Visualization, Topology, Registry, What-If, the Rust core). Two rows are the same engine as another: `PROMETHEE (uncertainty)` and `PROMETHEE II (crisp)` are both `PROMETHEE`. `Genetic` is in the universe and in no recommended route — see docs/kanban.md.
| Learning System | `outcome_tracker.py`, `calibration.py`, `decision_journal.py`, `adaptive_router.py` | Outcome tracking, confidence calibration, journal, adaptive routing | library |
| Meta-Learning | `action_threshold.py`, `reasoning_trace.py`, `unknown_scanner.py`, `meta_calibration.py` | Action threshold, reasoning trace, unknown scanner, meta-calibration | library |
| Decision Gates | `decision_gates.py` | Veto power: ergodicity, ruin, causal DAG, commitment | library |
| AHP | `ahp.py` | Pairwise weight calibration | library |
| Config Runner | `config_runner.py` | YAML-based decision config | library |

> The `File` column is **code, not notes**: `monte_carlo.py` lives in `src/decision_maker/core/`, so no
> wikilink can resolve it and none should be written. Where a module also has a vault card, the card
> is reached from [[decision-maker-moc]] — [[monte-carlo-engine]], [[topsis]], [[promethee]], [[ahp]],
> [[genetic-algorithms]], [[bayesian-inference-engine]], [[antifragile-engine]], [[portfolio-optimizer]],
> [[topological-data-analysis]], [[unified-orchestrator]]. [[pareto-frontier]], [[decision-theory]], [[sensitivity-analysis]] and [[rank-aggregator]] own
> `pareto.py`, `decision_theory.py`, `sensitivity.py` and `aggregator.py` through their `module:` field.
> The only first-class pipeline module without a card is `config_runner.py`.

## Runtime Flow

```
run_analysis(mode)
  |
  +-- MonteCarloEngine.run()             # simulate N scenarios
  +-- _check_scale_mismatch()            # warn if scales differ >10x
  |
  +-- TOPSISEngine.analyze(fuzzy)        # rank by distance to ideal
  +-- ParetoEngine.analyze()             # find efficient frontier
  |
  +-- if standard+:
  |    +-- DecisionTheoryEngine.analyze()      # game-theory lenses
  |    +-- SensitivityEngine.analyze()         # weight shocks
  |    +-- _promethee_with_uncertainty()       # PROMETHEE avg p5/p95
  |    +-- RobustOptimizer.analyze()           # worst-case scores
  |    +-- RankAggregator.aggregate()          # Borda of TOPSIS+MC+PROMETHEE
  |
  +-- if advanced:
       +-- PROMETHEE (crisp data)
       +-- BayesianEngine.analyze()
       +-- GeneticOptimizer.evolve_ideal()
       +-- BootstrapRanking.confidence_intervals()
       +-- RankAggregator.aggregate()       # Borda of all 4 methods
```

Standalone engines (Antifragile, Group Decision, Information Theory, Portfolio, What-If, Weight Derivation, Explainability, Topology, Visualization, Registry) can be invoked independently or composed via the orchestrator ([[unified-orchestrator]]). Cards exist for Antifragile ([[antifragile-engine]]), Portfolio ([[portfolio-optimizer]]), Topology ([[topological-data-analysis]]) and Registry ([[reporting-and-registry]]); the rest are described only by the table above.

## Modes

| Mode | Engines | Use Case |
|------|---------|----------|
| `express` | MC + TOPSIS + Pareto | Quick exploratory ranking |
| `standard` | express + decision theory + sensitivity + PROMETHEE uncertainty + robust + Borda | Balanced analysis |
| `advanced` | standard + crisp PROMETHEE + Bayesian + Genetic + Bootstrap | Deep research |

## Data Model

```
DecisionOption
  +-- name: str
  +-- description: str
  +-- variables: Dict[str, UncertainVariable]
       +-- DistributionType (DETERMINISTIC, NORMAL, UNIFORM, TRIANGULAR, etc.)
            +-- params: List[float]

Factor
  +-- name: str
  +-- weight: float
  +-- maximize: bool

Statistics (per option after MC)
  +-- mean_score, std_dev, min_score, max_score
  +-- percentile_5, percentile_95
  +-- var_95, cvar_95, success_rate
  +-- factor_stats: Dict[str, {mean, std, p5, p95, contribution}]
```

## Key Decisions

1. **Monte Carlo first** -- all downstream engines consume MC statistics (means, percentiles). This propagates uncertainty through every method.
2. **Fuzzy TOPSIS** -- uses (p5, mean, p95) tuples instead of point estimates, making ranking uncertainty-aware.
3. **PROMETHEE with uncertainty** -- averages net flows across p5/mean/p95 scenarios rather than a single deterministic run.
4. **Borda aggregation** -- combines rankings from multiple methods into a consensus, reducing method bias.
5. **Weights computed once** -- factor weights and maximize/minimize flags are built once and reused across all engines.
6. **Normalized scale is the shared contract** -- `MonteCarloEngine.run(normalize=True)` normalizes each factor to [0,1] via the global min/max across all options. All scale-dependent consumers (Kelly, via_negativa, success_rate, confidence, decision matrix) must compare on that same normalized scale. The rule is currently implemented twice -- here in `MonteCarloEngine.run()` (the block under `# Normalize exactly like the Rust MonteCarloEngine`) and in `rust_core/src/lib.rs` (`// Phase 3`) -- and the Rust copy is **not on the execution path** (no module under `core/` imports the extension). They agree on the formula but not on `success_rate`; see [[adr/001-use-rust-for-math-engine]].

## Test Coverage

554 tests across all engines, plus the smoke suite (`-m smoke`, one per analysis). Run with:

```bash
uv run pytest src/decision_maker/tests/ -v
```
