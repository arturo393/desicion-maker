# Architecture

Python framework for multi-criteria decision analysis under uncertainty. 18+ engines, 199+ tests.

## Building Blocks

### Entry Point: `UnifiedDecisionFramework`

```python
from python.core.orchestrator import UnifiedDecisionFramework
fw = UnifiedDecisionFramework(correlation_matrix=None)
fw.add_factor(Factor(...))
fw.add_option(DecisionOption(...))
results = await fw.run_analysis(mode="standard")
```

### Engines

| Engine | File | Purpose | Mode |
|--------|------|---------|------|
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
| AI Agent | `gemini_agent.py` | External research via Gemini | advanced |
| AHP | `ahp.py` | Pairwise weight calibration | library |
| Config Runner | `config_runner.py` | YAML-based decision config | library |

## Runtime Flow

```
run_analysis(mode)
  │
  ├─ MonteCarloEngine.run()             # simulate N scenarios
  ├─ _check_scale_mismatch()            # warn if scales differ >10x
  │
  ├─ TOPSISEngine.analyze(fuzzy)        # rank by distance to ideal
  ├─ ParetoEngine.analyze()             # find efficient frontier
  │
  └─ if standard+:
       ├─ DecisionTheoryEngine.analyze()      # game-theory lenses
       ├─ SensitivityEngine.analyze()         # weight shocks
       ├─ _promethee_with_uncertainty()       # PROMETHEE avg p5/p95
       ├─ RobustOptimizer.analyze()           # worst-case scores
       └─ RankAggregator.aggregate()          # Borda of TOPSIS+MC+PROMETHEE
     │
     └─ if advanced:
          ├─ PROMETHEE (crisp data)
          ├─ BayesianEngine.analyze()
          ├─ GeneticOptimizer.evolve_ideal()
          ├─ BootstrapRanking.confidence_intervals()
          └─ RankAggregator.aggregate()       # Borda of all 4 methods
```

## Modes

| Mode | Engines | Use Case |
|------|---------|----------|
| `express` | MC + TOPSIS + Pareto | Quick exploratory ranking |
| `standard` | express + decision theory + sensitivity + PROMETHEE uncertainty + robust + Borda | Balanced analysis |
| `advanced` | standard + crisp PROMETHEE + Bayesian + Genetic + Bootstrap | Deep research |

## Data Model

```
DecisionOption
  ├─ name: str
  ├─ description: str
  └─ variables: Dict[str, UncertainVariable]
       └─ DistributionType (DETERMINISTIC, NORMAL, UNIFORM, TRIANGULAR, etc.)
            └─ params: List[float]

Factor
  ├─ name: str
  ├─ weight: float
  └─ maximize: bool

Statistics (per option after MC)
  ├─ mean_score, std_dev, min_score, max_score
  ├─ percentile_5, percentile_95
  ├─ var_95, cvar_95, success_rate
  └─ factor_stats: Dict[str, {mean, std, p5, p95, contribution}]
```

## Key Decisions

1. **Monte Carlo first** — all downstream engines consume MC statistics (means, percentiles). This propagates uncertainty through every method.
2. **Fuzzy TOPSIS** — uses (p5, mean, p95) tuples instead of point estimates, making ranking uncertainty-aware.
3. **PROMETHEE with uncertainty** — averages net flows across p5/mean/p95 scenarios rather than a single deterministic run.
4. **Borda aggregation** — combines rankings from multiple methods into a consensus, reducing method bias.
5. **Weights computed once** — factor weights and maximize/minimize flags are built once and reused across all engines.

## Test Coverage

199+ tests across all engines. Run with:

```bash
uv run pytest python/tests/ -v
```
