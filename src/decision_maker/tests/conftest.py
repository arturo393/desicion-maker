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


@pytest.fixture(autouse=True)
def isolated_ledger(monkeypatch, tmp_path):
    """The decision ledger is versioned: no test may append to the real decisions/ledger.jsonl."""
    monkeypatch.setenv("DM_LEDGER_PATH", str(tmp_path / "ledger.jsonl"))


@pytest.fixture(autouse=True)
def isolated_results(monkeypatch, tmp_path):
    """Generated stores and reports go to a temp dir, never to the repo's results/."""
    monkeypatch.setenv("DM_RESULTS_DIR", str(tmp_path / "results"))
