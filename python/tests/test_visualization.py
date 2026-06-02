import os
import tempfile

import numpy as np
import pytest

from python.core.visualization import VisualizationEngine
from python.core.models import Factor, Statistics


@pytest.fixture
def mock_mc_results():
    n = 1000
    return {
        "Option_A": Statistics(
            option_name="Option_A",
            mean_score=0.7, std_dev=0.1,
            min_score=0.3, max_score=0.95,
            percentile_5=0.5, percentile_95=0.85,
            success_rate=0.9,
            factor_stats={"Cost": {"mean": 100, "std": 10, "p5": 85, "p95": 115}},
            var_95=0.5, cvar_95=0.45,
            raw_scores=np.random.rand(n) * 0.5 + 0.5,
            raw_factor_data={"Cost": np.random.rand(n) * 50 + 75},
        ),
        "Option_B": Statistics(
            option_name="Option_B",
            mean_score=0.5, std_dev=0.15,
            min_score=0.1, max_score=0.85,
            percentile_5=0.25, percentile_95=0.75,
            success_rate=0.6,
            factor_stats={"Cost": {"mean": 150, "std": 15, "p5": 125, "p95": 175}},
            var_95=0.25, cvar_95=0.2,
            raw_scores=np.random.rand(n) * 0.4 + 0.3,
            raw_factor_data={"Cost": np.random.rand(n) * 50 + 125},
        ),
    }


@pytest.fixture
def factors():
    return [Factor("Cost", 1.0, maximize=False)]


@pytest.fixture
def future_metrics(mock_mc_results):
    return {
        "info_theory": {
            "Option_A": {"Cost": 1.0},
        },
        "robust_optimizer": {
            "dro_scores": {"Option_A": 0.65, "Option_B": 0.45},
            "stability_metrics": {"Option_A": 0.9, "Option_B": 0.7},
        },
    }


class TestVisualizationEngine:
    def test_generate_all_plots_creates_files(self, mock_mc_results, factors, future_metrics):
        with tempfile.TemporaryDirectory() as tmpdir:
            engine = VisualizationEngine()
            paths = engine.generate_all_plots(
                mock_mc_results, factors, future_metrics, tmpdir, "test_timestamp",
            )
            assert len(paths) == 3
            for p in paths:
                assert os.path.exists(p)

    def test_generate_all_plots_empty_info_theory(self, mock_mc_results, factors):
        with tempfile.TemporaryDirectory() as tmpdir:
            engine = VisualizationEngine()
            paths = engine.generate_all_plots(
                mock_mc_results, factors, {}, tmpdir, "test_timestamp",
            )
            assert len(paths) == 1

    def test_risk_distribution_plot(self, mock_mc_results, factors):
        with tempfile.TemporaryDirectory() as tmpdir:
            engine = VisualizationEngine()
            path = engine.plot_risk_distributions(mock_mc_results, tmpdir, "ts")
            assert os.path.exists(path)
