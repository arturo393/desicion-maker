"""
Wrapper client for querying Gemini models to analyze decision options and factors.
Usage: from decision_maker.core.gemini_agent import GeminiDeepResearchAgent
Does NOT: Fallback silently without raising configured API exceptions.

Without a key or SDK it answers through the Antigravity CLI (`agy`); see core/agy_backend.py.
"""

from __future__ import annotations

__all__ = ["GeminiDeepResearchAgent"]

import json
import logging
import os
import re

from dotenv import load_dotenv

from decision_maker.core.agy_backend import AgyError, ask_agy, llm_backend
from decision_maker.core.content import calibration_prompt, research_prompt

logger = logging.getLogger(__name__)


class GeminiDeepResearchAgent:
    DEFAULT_MODEL = "gemini-2.0-flash"

    def __init__(self, api_key: str | None = None, model: str | None = None):
        load_dotenv()
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model = model or os.getenv("GEMINI_MODEL", self.DEFAULT_MODEL)
        self._client = None
        if self.api_key:
            try:
                from google import genai as _genai

                self._client = _genai.Client(api_key=self.api_key)
            except ImportError:
                pass
        self.backend = llm_backend(api_ready=self._client is not None)

    @property
    def is_available(self) -> bool:
        return self.backend != "none"

    def _generate(self, prompt: str) -> str:
        if self.backend == "agy":
            return ask_agy(prompt)
        response = self._client.models.generate_content(model=self.model, contents=prompt)
        return response.text

    async def research(self, topic: str, context: str = "") -> str:
        if not self.is_available:
            return "AI Disabled."
        try:
            return self._generate(research_prompt(topic, context))
        except (ConnectionError, TimeoutError, ValueError, AgyError) as e:
            return f"Error: {e}"

    async def calibrate_priors(self, context_data: str) -> dict:
        """
        Uses the LLM to dynamically adjust probability distribution priors
        (e.g., standard deviation and mean adjustments) based on real-world context.
        """
        if not self.is_available:
            return {}
        try:
            text = self._generate(calibration_prompt(context_data))
            match = re.search(r"\{.*\}", text, re.DOTALL)
            if match:
                return json.loads(match.group(0))
            return {}
        except (ConnectionError, TimeoutError, ValueError, json.JSONDecodeError, AgyError) as e:
            logger.error(f"Gemini API Error: {e}")
            return {}
