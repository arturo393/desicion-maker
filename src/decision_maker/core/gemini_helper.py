"""
SDK-agnostic Gemini search helper for analyses that query Google Generative AI.
Usage: from decision_maker.core.gemini_helper import ask_llm, search_with_gemini, GEMINI_AVAILABLE
Does NOT: Manage API keys for the framework agent (see gemini_agent) or run decision algorithms.

Without an SDK or a key it answers through the Antigravity CLI (`agy`); see core/agy_backend.py.
"""

from __future__ import annotations

import os

from decision_maker.core.agy_backend import AgyError, agy_available, ask_agy, llm_backend

__all__ = ["GEMINI_AVAILABLE", "LLMUnavailable", "ask_llm", "search_with_gemini"]

# SDK detection
try:
    from google import genai as _new_genai

    GEMINI_SDK = "new"
except ImportError:
    try:
        import google.generativeai as _old_genai

        GEMINI_SDK = "old"
    except ImportError:
        GEMINI_SDK = "none"

GEMINI_SDK_AVAILABLE = GEMINI_SDK != "none"
# True when ANY backend can answer: the SDK, or agy as fallback.
GEMINI_AVAILABLE = GEMINI_SDK_AVAILABLE or agy_available()


class LLMUnavailable(RuntimeError):
    """No backend can answer: no SDK + GEMINI_API_KEY, and no agy on PATH."""


def ask_llm(query: str, model_name: str = "gemini-2.0-flash") -> str:
    """Answer `query` with the API (either SDK) if it has a key, else `agy`. Raises on failure."""
    api_key = os.environ.get("GEMINI_API_KEY")
    backend = llm_backend(api_ready=GEMINI_SDK_AVAILABLE and bool(api_key))
    if backend == "none":
        raise LLMUnavailable("no SDK + GEMINI_API_KEY, and no agy on PATH")
    if backend == "agy":
        return ask_agy(query)
    if GEMINI_SDK == "new":
        client = _new_genai.Client(api_key=api_key)
        return client.models.generate_content(model=model_name, contents=query).text
    _old_genai.configure(api_key=api_key)
    return _old_genai.GenerativeModel(model_name).generate_content(query).text


def search_with_gemini(query: str, model_name: str = "gemini-2.0-flash") -> str:
    """Like ask_llm, but returns the failure as text — the contract the older analyses rely on."""
    try:
        return ask_llm(query, model_name)
    except LLMUnavailable as e:
        return f"Gemini not available ({e})"
    except (AgyError, ConnectionError, TimeoutError, ValueError) as e:
        return f"Gemini error: {e}"
