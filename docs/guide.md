# Guide: Modeling a Decision

## Step 1: Create Your Script

```bash
cp src/decision_maker/analyses/_template.py my_decision.py
```

## Step 2: Define Factors

Factors are what you care about. Each has a name, weight (importance), and direction (maximize or minimize).

```python
from decision_maker.core.models import Factor

fw.add_factor(Factor("Cost",       0.30, maximize=False))
fw.add_factor(Factor("Quality",    0.40, maximize=True))
fw.add_factor(Factor("Time",       0.20, maximize=False))
fw.add_factor(Factor("Flexibility", 0.10, maximize=True))
```

Weights should sum to 1.0 for interpretability but the framework normalizes internally.

## Step 3: Define Options

Each option has variables matching your factor names. Choose a distribution type for uncertainty:

```python
from decision_maker.core.models import DecisionOption, DistributionType

opt = DecisionOption("Option A", "description")
opt.add_variable("Cost",        DistributionType.NORMAL,       1000, 200)     # mean=1000, std=200
opt.add_variable("Quality",     DistributionType.TRIANGULAR,   5, 8, 9)      # min, mode, max
opt.add_variable("Time",        DistributionType.DETERMINISTIC, 12)           # fixed
opt.add_variable("Flexibility", DistributionType.UNIFORM,      1, 10)        # min, max
fw.add_option(opt)
```

### Available Distributions

| Type | Params | Use |
|------|--------|-----|
| `DETERMINISTIC` | `value` | Known with certainty |
| `NORMAL` | `mean, std` | Natural variation around a mean |
| `UNIFORM` | `min, max` | Range with equal probability |
| `TRIANGULAR` | `min, mode, max` | Range with most likely value |
| `BETA` | `alpha, beta` | Bounded [0,1] distributions |
| `LOGNORMAL` | `mu, sigma` | Positive-skewed (prices, salaries) |
| `GAMMA` | `shape, scale` | Waiting times, costs |
| `EXPONENTIAL` | `scale` | Time between events |
| `POISSON` | `lam` | Count events |
| `BERNOULLI` | `p` | Binary outcomes |

## Step 4: Run

```python
import asyncio

async def main():
    result = await fw.run_analysis(mode="advanced")  # or "express", "standard"
    print(result["files"])  # paths to generated reports

asyncio.run(main())
```

Reports are saved to `results/` as JSON, Markdown, and HTML.

## Step 5: Interpret Results

The result dict contains:

| Key | Content |
|-----|---------|
| `mc_results` | Per-option Monte Carlo statistics (mean, std, VaR, CVaR) |
| `topsis_scores` | Fuzzy TOPSIS ranking |
| `strategies` | Maximax, Maximin, Hurwicz, Laplace, Minimax Regret |
| `pareto` | Efficient frontier and dominated options |
| `sensitivity` | Robustness score and winner-flip scenarios |
| `future.promethee_uncertainty` | PROMETHEE net flows (averaged) |
| `future.robust_optimizer` | Worst-case ranking under weight shocks |
| `future.rank_aggregation` | Borda consensus ranking |
| `future.promethee_scores` | Crisp PROMETHEE II net flows (advanced) |
| `future.bayesian_probs` | Posterior probability each option is best (advanced) |
| `future.ideal_option` | Theoretical best composite (advanced) |
| `future.bootstrap_ci` | Confidence intervals on ranking (advanced) |

## Example: 3 Mac Upgrade Options

See [`examples/mac_upgrade_comparison.py`](../examples/mac_upgrade_comparison.py) for a complete comparison across all 3 modes.

## Using YAML Config

```bash
# Edit config/decision_config.yaml
uv run python -c "
from decision_maker.core.config_runner import build_framework_from_config, load_decision_config
import yaml

with open('config/decision_config.yaml') as f:
    config = yaml.safe_load(f)
fw = build_framework_from_config(config)
import asyncio
result = asyncio.run(fw.run_analysis())
"
```

## AI Research (Optional)

```bash
export GEMINI_API_KEY="your_key"
# Then pass use_ai=True to run_analysis:
result = await fw.run_analysis(use_ai=True)
```
