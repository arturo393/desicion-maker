import numpy as np
import pytest

from python.core.models import DecisionOption, DistributionType, Factor, Statistics


@pytest.fixture(autouse=True)
def seed_random():
    np.random.seed(42)
    yield


@pytest.fixture
def simple_option():
    opt = DecisionOption("Test Option", "Test")
    opt.add_variable("Value", DistributionType.DETERMINISTIC, 100)
    return opt


@pytest.fixture
def simple_factor():
    return Factor("Value", 1.0, maximize=True)


@pytest.fixture
def two_options_two_factors():
    opts = [
        DecisionOption("OptA", "Option A"),
        DecisionOption("OptB", "Option B"),
    ]
    opts[0].add_variable("Cost", DistributionType.DETERMINISTIC, 50)
    opts[0].add_variable("Benefit", DistributionType.DETERMINISTIC, 150)
    opts[1].add_variable("Cost", DistributionType.DETERMINISTIC, 80)
    opts[1].add_variable("Benefit", DistributionType.DETERMINISTIC, 200)

    factors = [
        Factor("Cost", 0.2, maximize=False),
        Factor("Benefit", 0.8, maximize=True),
    ]
    return opts, factors


@pytest.fixture
def mc_results():
    return {
        "OptA": Statistics(
            option_name="OptA",
            mean_score=110.0,
            std_dev=10.0,
            min_score=80.0,
            max_score=140.0,
            percentile_5=90.0,
            percentile_95=130.0,
            success_rate=0.95,
            factor_stats={
                "Cost": {"mean": 50.0, "std": 0.0, "p5": 50.0, "p95": 50.0},
                "Benefit": {"mean": 150.0, "std": 0.0, "p5": 150.0, "p95": 150.0},
            },
            var_95=90.0,
            cvar_95=85.0,
        ),
        "OptB": Statistics(
            option_name="OptB",
            mean_score=120.0,
            std_dev=15.0,
            min_score=70.0,
            max_score=160.0,
            percentile_5=85.0,
            percentile_95=150.0,
            success_rate=0.90,
            factor_stats={
                "Cost": {"mean": 80.0, "std": 0.0, "p5": 80.0, "p95": 80.0},
                "Benefit": {"mean": 200.0, "std": 0.0, "p5": 200.0, "p95": 200.0},
            },
            var_95=85.0,
            cvar_95=72.0,
        ),
    }
