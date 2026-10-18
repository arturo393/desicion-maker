"""
Weight robustness: probability that each option wins when the weights are uncertain as well as the scores.
Usage: r = weight_robustness(mc_results, factors, concentration=20, seed=1); r.informed, r.uninformed, r.verdict
Does NOT: elicit weights (weight_derivation), or measure tail risk (cvar_95 in MonteCarloEngine).

Why: every other engine ranks with one weight vector, typed by hand. Whether the winner survives a
different, equally defensible vector is the question a decision maker actually has, and nothing
answered it. Each Monte Carlo draw is paired with its own weight draw, so one number carries both
uncertainties. The idea is the rank acceptability index of SMAA (Lahdelma & Salminen); the
implementation and the two-reading report below are this framework's.

Two readings, always both:
- informed: weights ~ Dirichlet(concentration * stated). "If my weights are roughly right."
- uninformed: weights ~ Dirichlet(1, ..., 1), uniform on the simplex. "If I knew nothing about them."
An option that wins the uninformed reading does not need the weight discussion at all.
"""

from __future__ import annotations

__all__ = ["WeightRobustness", "weight_robustness", "DEFAULT_CONCENTRATION"]

from dataclasses import dataclass

import numpy as np

from decision_maker.core.models import Factor, Statistics

# Dirichlet(k * w): a weight w has standard deviation sqrt(w(1-w)/(k+1)). k=20 puts a stated 0.30
# at about ±0.10 — the disagreement two people typically have when they weight the same criterion.
DEFAULT_CONCENTRATION = 20.0

# Verdict on the stated winner's informed first-rank acceptability. Above ROBUST it wins in three
# out of four plausible weightings; below FRAGILE it loses more often than it wins.
ROBUST = 0.75
FRAGILE = 0.5


@dataclass(frozen=True)
class WeightRobustness:
    stated_winner: str
    informed: dict[str, float]  # P(first) with weights around the stated ones
    uninformed: dict[str, float]  # P(first) with weights uniform on the simplex
    rank_acceptability: dict[str, list[float]]  # informed P(rank k), k = 1..n
    central_weights: dict[str, dict[str, float]]  # mean informed weights over the draws each option won
    concentration: float
    verdict: str  # robust | contested | fragile

    def to_dict(self) -> dict:
        return {
            "stated_winner": self.stated_winner,
            "informed": self.informed,
            "uninformed": self.uninformed,
            "rank_acceptability": self.rank_acceptability,
            "central_weights": self.central_weights,
            "concentration": self.concentration,
            "verdict": self.verdict,
        }


def weight_robustness(
    mc_results: dict[str, Statistics],
    factors: list[Factor],
    concentration: float = DEFAULT_CONCENTRATION,
    seed: int | None = None,
) -> WeightRobustness:
    """Rank acceptability of every option under joint score and weight uncertainty."""
    names = list(mc_results)
    if len(names) < 2:
        raise ValueError("weight robustness needs at least two options")
    if concentration <= 0:
        raise ValueError(f"concentration must be > 0, got {concentration}")

    values = _normalized_values(mc_results, factors)  # (options, draws, factors)
    n_draws = values.shape[1]
    stated = np.array([f.weight for f in factors], dtype=float)
    stated = stated / stated.sum()
    rng = np.random.default_rng(seed)

    informed_w = rng.dirichlet(np.maximum(stated * concentration, 1e-9), size=n_draws)
    uninformed_w = rng.dirichlet(np.ones(len(factors)), size=n_draws)

    informed_ranks = _ranks(values, informed_w)
    uninformed_ranks = _ranks(values, uninformed_w)
    stated_ranks = _ranks(values, np.broadcast_to(stated, informed_w.shape))

    n = len(names)
    acceptability = {
        name: [float(np.mean(informed_ranks[i] == k)) for k in range(n)] for i, name in enumerate(names)
    }
    informed = {name: acceptability[name][0] for name in names}
    uninformed = {name: float(np.mean(uninformed_ranks[i] == 0)) for i, name in enumerate(names)}
    stated_winner = names[int(np.argmax([np.mean(stated_ranks[i] == 0) for i in range(n)]))]

    central = {}
    for i, name in enumerate(names):
        won = informed_ranks[i] == 0
        mean_w = informed_w[won].mean(axis=0) if won.any() else np.full(len(factors), np.nan)
        central[name] = {f.name: float(w) for f, w in zip(factors, mean_w, strict=True)}

    p = informed[stated_winner]
    verdict = "robust" if p >= ROBUST else "fragile" if p < FRAGILE else "contested"
    return WeightRobustness(stated_winner, informed, uninformed, acceptability, central, concentration, verdict)


def _normalized_values(mc_results: dict[str, Statistics], factors: list[Factor]) -> np.ndarray:
    """Per-draw factor values scaled to [0, 1] with the engine's rule: global min/max, minimize inverted."""
    for name, st in mc_results.items():
        if st.raw_factor_data is None:
            raise ValueError(f"{name} has no raw_factor_data: run MonteCarloEngine.run() first")
    raw = [st.raw_factor_data for st in mc_results.values() if st.raw_factor_data is not None]
    out = []
    for f in factors:
        cols = np.stack([np.asarray(data[f.name], dtype=float) for data in raw])
        lo, hi = cols.min(), cols.max()
        scaled = (cols - lo) / (hi - lo) if hi > lo else np.ones_like(cols)
        out.append(scaled if f.maximize else 1.0 - scaled)
    return np.stack(out, axis=-1)


def _ranks(values: np.ndarray, weights: np.ndarray) -> np.ndarray:
    """0-based rank of each option in each draw (0 = best). Ties go to the earlier option."""
    scores = np.einsum("odf,df->od", values, weights)
    order = np.argsort(-scores, axis=0, kind="stable")
    ranks = np.empty_like(order)
    np.put_along_axis(ranks, order, np.arange(scores.shape[0])[:, None], axis=0)
    return ranks
