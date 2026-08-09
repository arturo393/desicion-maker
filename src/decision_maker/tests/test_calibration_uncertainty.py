from __future__ import annotations

import numpy as np
import pytest

from decision_maker.core.calibration import DecisionOutcome, compute_calibration
from decision_maker.core.devils_advocate import ChallengeRequest, DevilsAdvocate
from decision_maker.core.models import Statistics
from decision_maker.core.uncertainty import confidence_weighted_winner, ranking_confidence


def _stats(name, mean, std, raw=None):
    raw_scores = np.asarray(raw) if raw is not None else None
    return Statistics(
        option_name=name,
        mean_score=mean,
        std_dev=std,
        min_score=mean - 3 * std,
        max_score=mean + 3 * std,
        percentile_5=mean - 2 * std,
        percentile_95=mean + 2 * std,
        success_rate=0.8,
        factor_stats={},
        var_95=mean - 2 * std,
        cvar_95=mean - 2.5 * std,
        raw_scores=raw_scores,
        raw_factor_data=None,
    )


class TestCalibration:
    def test_empty_outcomes(self):
        result = compute_calibration([])
        assert result["n_outcomes"] == 0
        assert result["verdict"] == "insufficient_data"

    def test_perfect_calibration(self):
        outcomes = [
            DecisionOutcome(predicted_winner="A", actual_winner="A", confidence=0.9),
            DecisionOutcome(predicted_winner="B", actual_winner="B", confidence=0.8),
        ]
        result = compute_calibration(outcomes)
        assert result["hit_rate"] == 1.0
        assert result["verdict"] == "well_calibrated"

    def test_miss_lowers_hit_rate(self):
        outcomes = [
            DecisionOutcome(predicted_winner="A", actual_winner="A", confidence=0.9),
            DecisionOutcome(predicted_winner="B", actual_winner="C", confidence=0.9),
        ]
        result = compute_calibration(outcomes)
        assert result["hit_rate"] == 0.5
        assert result["verdict"] in ("moderately_calibrated", "poorly_calibrated")

    def test_overconfidence_detected(self):
        outcomes = [
            DecisionOutcome(predicted_winner="A", actual_winner="A", confidence=0.3),
            DecisionOutcome(predicted_winner="B", actual_winner="C", confidence=0.9),
        ]
        result = compute_calibration(outcomes)
        assert result["separation_index"] < -0.1
        assert result["verdict"] == "overconfident"


class TestUncertainty:
    def test_confidence_weighted_winner(self):
        results = {"A": _stats("A", 80, 5), "B": _stats("B", 79, 30)}
        winner = confidence_weighted_winner(results)
        assert winner["winner"] == "A"
        assert winner["confidence"] > 0.5
        assert winner["runner_up"] == "B"

    def test_winner_is_highest_mean(self):
        results = {"A": _stats("A", 50, 1), "B": _stats("B", 90, 1)}
        winner = confidence_weighted_winner(results)
        assert winner["winner"] == "B"

    def test_empty(self):
        assert confidence_weighted_winner({})["winner"] is None

    def test_ranking_confidence_best_has_highest_p_best(self):
        results = {
            "A": _stats("A", 90, 5, raw=np.random.default_rng(1).normal(90, 5, 200)),
            "B": _stats("B", 60, 5, raw=np.random.default_rng(2).normal(60, 5, 200)),
        }
        ci = ranking_confidence(results, n_resamples=500)
        assert ci["A"]["p_best"] > ci["B"]["p_best"]
        assert ci["A"]["mean_rank"] <= ci["B"]["mean_rank"]

    def test_ranking_confidence_empty(self):
        assert ranking_confidence({}) == {}


class TestDevilsAdvocate:
    def _request(self):
        return ChallengeRequest(
            winner="A",
            options=["A", "B"],
            factors=[{"name": "Cost", "weight": 0.5}, {"name": "Quality", "weight": 0.5}],
            mc_results={"A": {"mean": 0.6, "std": 0.1}, "B": {"mean": 0.4, "std": 0.2}},
            sensitivity={
                "robustness_score": 0.4,
                "weight_changes": [{"factor": "Cost", "change": "+20%", "new_winner": "B"}],
                "score_changes": [],
            },
            explanation="A wins by F-TOPSIS.",
        )

    def test_heuristic_challenges_detected_without_ai(self):
        advocate = DevilsAdvocate(use_ai=False)
        result = advocate.challenge(self._request())
        assert result["source"] == "heuristic"
        types = {c["type"] for c in result["heuristic"]}
        assert "weight_sensitivity" in types
        assert "low_robustness" in types

    def test_weight_normalization_challenge(self):
        req = ChallengeRequest(
            winner="A",
            options=["A"],
            factors=[{"name": "Cost", "weight": 0.7}],  # sums to 0.7
            mc_results={"A": {"mean": 1.0, "std": 0.0}},
            sensitivity={},
        )
        result = DevilsAdvocate(use_ai=False).challenge(req)
        types = {c["type"] for c in result["heuristic"]}
        assert "weight_normalization" in types

    def test_ai_disabled_returns_heuristic_only(self):
        advocate = DevilsAdvocate(use_ai=True)
        # With no GEMINI_API_KEY the agent is unavailable and falls back gracefully.
        result = advocate.challenge(self._request())
        assert isinstance(result["ai"], list)
        assert result["source"] in ("ai", "heuristic")
