import numpy as np
import pytest

from python.core.models import DecisionOption, DistributionType, Factor, Statistics


@pytest.fixture(autouse=True)
def seed_random():
    np.random.seed(42)
    yield
