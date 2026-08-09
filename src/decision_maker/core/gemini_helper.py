"""
SDK-agnostic Gemini search helper for analyses that query Google Generative AI.
Usage: from decision_maker.core.gemini_helper import search_with_gemini, GEMINI_AVAILABLE
Does NOT: Manage API keys for the framework agent (see gemini_agent) or run decision algorithms.
"""

from __future__ import annotations

import os

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

GEMINI_AVAILABLE = GEMINI_SDK != "none"


def search_with_gemini(query: str, model_name: str = "gemini-2.0-flash") -> str:
    """Query Gemini with the given prompt. Handles both SDK versions."""
    if not GEMINI_AVAILABLE:
        return "Gemini not available"
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return "GEMINI_API_KEY not configured"
    try:
        if GEMINI_SDK == "new":
            client = _new_genai.Client(api_key=api_key)
            response = client.models.generate_content(model=model_name, contents=query)
            return response.text
        else:
            _old_genai.configure(api_key=api_key)
            model = _old_genai.GenerativeModel(model_name)
            response = model.generate_content(query)
            return response.text
    except (ConnectionError, TimeoutError, ValueError) as e:
        return f"Gemini error: {e}"
