import numpy as np
import pytest


@pytest.fixture(autouse=True)
def seed_random():
    np.random.seed(42)
    return


@pytest.fixture(autouse=True)
def no_real_llm(monkeypatch):
    """The suite never reaches a real LLM: without this, a workstation with `agy` on PATH
    would shell out to it from every test that leaves use_ai at its default."""
    monkeypatch.setenv("DM_LLM_BACKEND", "api")
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
