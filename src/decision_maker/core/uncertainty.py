"""
Uncertainty analysis: confidence-weighted winner and ranking confidence intervals.
Usage: from decision_maker.core.uncertainty import confidence_weighted_winner, ranking_confidence
Does NOT: Run Monte Carlo simulations (see monte_carlo) or generate reports.
"""

from __future__ import annotations

__all__ = ["confidence_weighted_winner", "ranking_confidence"]

import numpy as np

from decision_maker.core.models import Statistics


def confidence_weighted_winner(mc_results: dict[str, Statistics]) -> dict:
    """
    Return the winner weighted by both expected value and confidence.

    Confidence is derived from the ratio of signal (mean) to noise (std):
    higher signal/noise with a non-trivial edge -> higher confidence.

    Returns {winner, score, confidence, edge, runner_up}.
    """
    if not mc_results:
        return {"winner": None, "score": 0.0, "confidence": 0.0, "edge": 0.0, "runner_up": None}

    scored = []
    for name, stats in mc_results.items():
        noise = max(stats.std_dev, 1e-9)
        scored.append((name, stats.mean_score, noise))

    scored.sort(key=lambda x: x[1], reverse=True)
    winner, winner_score, winner_noise = scored[0]
    runner_up = scored[1][0] if len(scored) > 1 else None
    runner_score = scored[1][1] if len(scored) > 1 else 0.0
    runner_noise = scored[1][2] if len(scored) > 1 else 0.0
    edge = winner_score - runner_score

    # Confidence from the winner's edge over the runner-up relative to the
    # combined comparison noise. On normalized [0,1] scores, |mean| alone
    # inflates confidence (0 is the floor, not the neutral point), so the edge
    # over the field is the signal. Combined noise (both options) is the honest
    # denominator: a tiny edge over a very noisy runner-up yields low confidence.
    combined_noise = max((winner_noise ** 2 + runner_noise ** 2) ** 0.5, 1e-9)
    confidence = min(1.0, abs(edge) / (abs(edge) + combined_noise))

    return {
        "winner": winner,
        "score": float(winner_score),
        "confidence": float(confidence),
        "edge": float(edge),
        "runner_up": runner_up,
    }


def ranking_confidence(mc_results: dict[str, Statistics], n_resamples: int = 1000, seed: int = 42) -> dict:
    """
    Bootstrap-style confidence intervals for the ranking of each option.

    Resamples each option's raw scores (if available) with replacement and
    recomputes mean-based ranks, yielding CI on rank position + P(best).

    Returns {option: {mean_rank, ci_low, ci_high, p_best}}.
    """
    if not mc_results:
        return {}

    rng = np.random.default_rng(seed)
    names = list(mc_results.keys())
    n_opts = len(names)

    raw_scores = {}
    for name, stats in mc_results.items():
        if stats.raw_scores is not None and len(stats.raw_scores) > 1:
            raw_scores[name] = np.asarray(stats.raw_scores, dtype=float)
        else:
            raw_scores[name] = None

    rank_matrix = np.zeros((n_resamples, n_opts), dtype=int)
    p_best = np.zeros(n_opts)

    for b in range(n_resamples):
        resampled_means = np.zeros(n_opts)
        for i, name in enumerate(names):
            if raw_scores[name] is not None:
                sample = rng.choice(raw_scores[name], size=len(raw_scores[name]), replace=True)
                resampled_means[i] = sample.mean()
            else:
                resampled_means[i] = mc_results[name].mean_score
        order = np.argsort(-resampled_means)
        for rank_pos, idx in enumerate(order):
            rank_matrix[b, idx] = rank_pos + 1
        p_best[order[0]] += 1

    results = {}
    for i, name in enumerate(names):
        ranks = rank_matrix[:, i]
        results[name] = {
            "mean_rank": float(np.mean(ranks)),
            "ci_low": float(np.percentile(ranks, 5)),
            "ci_high": float(np.percentile(ranks, 95)),
            "p_best": float(p_best[i] / n_resamples),
        }
    return results
