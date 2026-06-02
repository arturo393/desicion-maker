from __future__ import annotations

import numpy as np
import pytest

from python.core.antifragile import AntifragileEngine
from python.core.models import Factor, Statistics


@pytest.fixture
def three_options_two_factors():
    np.random.seed(42)
    n_sims = 1000
    # OptA: safe, moderate scores
    # OptB: risky high-upside
    # OptC: risky low-upside
    opt_a_raw = {
        "Cost": np.random.normal(100, 5, n_sims),
        "Return": np.random.normal(10, 1, n_sims),
    }
    opt_b_raw = {
        "Cost": np.random.normal(200, 40, n_sims),
        "Return": np.random.normal(20, 5, n_sims),
    }
    opt_c_raw = {
        "Cost": np.random.normal(150, 30, n_sims),
        "Return": np.random.normal(8, 2, n_sims),
    }
    factors = [
        Factor("Cost", 0.5, maximize=False),
        Factor("Return", 0.5, maximize=True),
    ]

    def _make(name, raw):
        total = np.zeros(n_sims)
        for f in factors:
            vals = raw[f.name]
            total += vals * f.weight if f.maximize else -vals * f.weight
        return Statistics(
            option_name=name,
            mean_score=float(np.mean(total)),
            std_dev=float(np.std(total)),
            min_score=float(np.min(total)),
            max_score=float(np.max(total)),
            percentile_5=float(np.percentile(total, 5)),
            percentile_95=float(np.percentile(total, 95)),
            success_rate=float(np.mean(total > 0)),
            factor_stats={
                fn: {
                    "mean": float(np.mean(v)),
                    "std": float(np.std(v)),
                    "p5": float(np.percentile(v, 5)),
                    "p95": float(np.percentile(v, 95)),
                }
                for fn, v in raw.items()
            },
            var_95=float(np.percentile(total, 5)),
            cvar_95=float(np.mean(total[total <= np.percentile(total, 5)])),
            raw_scores=total,
            raw_factor_data=raw,
        )

    return {
        "SafeOptA": _make("SafeOptA", opt_a_raw),
        "RiskyOptB": _make("RiskyOptB", opt_b_raw),
        "WeakOptC": _make("WeakOptC", opt_c_raw),
    }, factors


@pytest.fixture
def mc_results(three_options_two_factors):
    return three_options_two_factors[0]


@pytest.fixture
def factors(three_options_two_factors):
    return three_options_two_factors[1]


class TestBarbellAnalysis:
    def test_requires_three_options(self, factors):
        two_opts = {
            "A": Statistics("A", 0.5, 0.1, 0.2, 0.8, 0.3, 0.7, 0.6, {"X": {"mean": 5}}, 0.3, 0.25),
            "B": Statistics("B", 0.4, 0.15, 0.1, 0.7, 0.2, 0.6, 0.5, {"X": {"mean": 3}}, 0.2, 0.15),
        }
        result = AntifragileEngine.barbell_analysis(two_opts, factors)
        assert "Need at least 3 options" in result["summary"]

    def test_returns_barbells(self, mc_results, factors):
        result = AntifragileEngine.barbell_analysis(mc_results, factors)
        assert "barbells" in result
        assert "best_single" in result
        for b in result["barbells"]:
            assert "option_a" in b
            assert "option_b" in b
            assert "portfolio_score" in b

    def test_barbell_score_is_average(self, mc_results, factors):
        result = AntifragileEngine.barbell_analysis(mc_results, factors)
        for b in result["barbells"]:
            expected = (b["a_score"] + b["b_score"]) / 2.0
            assert abs(b["portfolio_score"] - expected) < 1e-6

    def test_empty_returns_empty_dict(self):
        result = AntifragileEngine.barbell_analysis({}, [Factor("X", 1.0)])
        assert "Need at least 3 options" in result["summary"]


class TestConvexityAnalysis:
    def test_returns_convexity_scores(self, mc_results, factors):
        result = AntifragileEngine.convexity_analysis(mc_results, factors)
        assert len(result) > 0
        for opt_name, scores in result.items():
            for fn, info in scores.items():
                assert "convexity_coefficient" in info
                assert "verdict" in info
                assert "deltas" in info

    def test_convexity_verdict_is_valid(self, mc_results, factors):
        result = AntifragileEngine.convexity_analysis(mc_results, factors)
        for scores in result.values():
            for info in scores.values():
                assert info["verdict"] in ("antifragile", "fragile", "neutral")

    def test_empty_returns_empty_dict(self):
        assert AntifragileEngine.convexity_analysis({}, []) == {}

    def test_no_raw_data_skips(self):
        stats = Statistics("X", 0.5, 0.1, 0.3, 0.7, 0.4, 0.6, 0.8, {"F": {"mean": 10}}, 0.4, 0.35)
        result = AntifragileEngine.convexity_analysis(
            {"X": stats}, [Factor("F", 1.0, maximize=True)],
        )
        assert result == {}


class TestFragilityIndex:
    def test_returns_all_options(self, mc_results, factors):
        result = AntifragileEngine.fragility_index(mc_results)
        assert "options" in result
        assert "ranking" in result
        for name in mc_results:
            assert name in result["options"]

    def test_fragility_score_in_range(self, mc_results, factors):
        result = AntifragileEngine.fragility_index(mc_results)
        for info in result["options"].values():
            assert 0.0 <= info["fragility_score"] <= 1.0

    def test_verdict_is_valid(self, mc_results, factors):
        result = AntifragileEngine.fragility_index(mc_results)
        for info in result["options"].values():
            assert info["verdict"] in ("fragile", "robust", "moderate")

    def test_ranking_most_fragile_first(self, mc_results, factors):
        result = AntifragileEngine.fragility_index(mc_results)
        scores = [r["fragility_score"] for r in result["ranking"]]
        for i in range(len(scores) - 1):
            assert scores[i] >= scores[i + 1]

    def test_empty_returns_empty_dict(self):
        assert AntifragileEngine.fragility_index({}) == {}


class TestViaNegativa:
    def test_returns_candidates(self, mc_results, factors):
        result = AntifragileEngine.via_negativa(mc_results, factors)
        assert len(result) > 0
        for c in result:
            assert "removed_factor" in c
            assert "original_winner" in c
            assert "score_changes" in c

    def test_score_changes_contain_all_options(self, mc_results, factors):
        result = AntifragileEngine.via_negativa(mc_results, factors)
        for c in result:
            for name in mc_results:
                assert name in c["score_changes"]

    def test_empty_returns_empty_list(self):
        assert AntifragileEngine.via_negativa({}, [Factor("X", 1.0)]) == []

    def test_empty_factors_returns_empty(self, mc_results):
        assert AntifragileEngine.via_negativa(mc_results, []) == []


class TestFullAnalyze:
    def test_analyze_returns_all_keys(self, mc_results, factors):
        result = AntifragileEngine.analyze(mc_results, factors)
        assert "barbell" in result
        assert "convexity" in result
        assert "fragility" in result
        assert "via_negativa" in result

    def test_analyze_empty(self):
        result = AntifragileEngine.analyze({}, [])
        assert result == {
            "barbell": {},
            "convexity": {},
            "fragility": {},
            "via_negativa": [],
        }
