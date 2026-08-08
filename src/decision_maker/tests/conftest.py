import numpy as np
import pytest


@pytest.fixture(autouse=True)
def seed_random():
    np.random.seed(42)
    return
