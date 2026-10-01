"""
Contract tests for core/agy_backend.py against a fake `agy` executable (no network, no real agent).
Run: uv run pytest src/decision_maker/tests/test_agy_backend.py -v
Does NOT: call the real Antigravity CLI.
"""

from __future__ import annotations

import asyncio
import stat
from pathlib import Path

import pytest

from decision_maker.core import gemini_helper
from decision_maker.core.agy_backend import AgyError, ask_agy, llm_backend
from decision_maker.core.gemini_agent import GeminiDeepResearchAgent


def _fake_agy(tmp_path: Path, body: str) -> Path:
    exe = tmp_path / "agy"
    exe.write_text(f"#!/bin/sh\n{body}\n")
    exe.chmod(exe.stat().st_mode | stat.S_IEXEC)
    return exe


@pytest.fixture
def agy_ok(tmp_path, monkeypatch):
    # Echo the argv back so the test can see the flags agy was called with.
    exe = _fake_agy(tmp_path, 'echo "ANSWER $*"')
    monkeypatch.setenv("AGY_BIN", str(exe))
    monkeypatch.setenv("DM_LLM_BACKEND", "agy")
    return exe


def test_ask_agy_returns_stdout_and_runs_in_plan_mode(agy_ok):
    out = ask_agy("hola")
    assert out.startswith("ANSWER -p hola")
    assert "--mode plan" in out
    assert "--sandbox" in out


def test_ask_agy_raises_on_nonzero_exit(tmp_path, monkeypatch):
    monkeypatch.setenv("AGY_BIN", str(_fake_agy(tmp_path, 'echo "error: bad model" >&2; exit 1')))
    with pytest.raises(AgyError, match="exited 1: error: bad model"):
        ask_agy("x")


def test_ask_agy_raises_on_empty_answer(tmp_path, monkeypatch):
    monkeypatch.setenv("AGY_BIN", str(_fake_agy(tmp_path, "exit 0")))
    with pytest.raises(AgyError, match="empty answer"):
        ask_agy("x")


def test_ask_agy_raises_when_missing(monkeypatch):
    monkeypatch.setenv("AGY_BIN", "agy-does-not-exist-xyz")
    with pytest.raises(AgyError, match="not found"):
        ask_agy("x")


def test_backend_selection(agy_ok, monkeypatch):
    monkeypatch.setenv("DM_LLM_BACKEND", "auto")
    assert llm_backend(api_ready=True) == "api"
    assert llm_backend(api_ready=False) == "agy"
    monkeypatch.setenv("DM_LLM_BACKEND", "api")
    assert llm_backend(api_ready=False) == "none"
    monkeypatch.setenv("DM_LLM_BACKEND", "bogus")
    with pytest.raises(ValueError, match="DM_LLM_BACKEND"):
        llm_backend(api_ready=True)


def test_search_with_gemini_goes_through_agy(agy_ok):
    assert gemini_helper.search_with_gemini("pregunta").startswith("ANSWER -p pregunta")


def test_search_with_gemini_reports_agy_failure(tmp_path, monkeypatch):
    monkeypatch.setenv("DM_LLM_BACKEND", "agy")
    monkeypatch.setenv("AGY_BIN", str(_fake_agy(tmp_path, "exit 3")))
    assert gemini_helper.search_with_gemini("x").startswith("Gemini error: agy exited 3")


def test_research_agent_uses_agy_without_a_key(agy_ok):
    agent = GeminiDeepResearchAgent(api_key=None)
    assert agent.backend == "agy"
    assert agent.is_available
    assert asyncio.run(agent.research("tema")).startswith("ANSWER -p")


def test_suite_default_never_reaches_agy():
    """conftest pins DM_LLM_BACKEND=api with no key: nothing is available."""
    agent = GeminiDeepResearchAgent(api_key=None)
    assert agent.backend == "none"
