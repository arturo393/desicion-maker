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

from decision_maker.core import gemini_helper
from decision_maker.core.agy_backend import AgyError
from decision_maker.core.content import calibration_prompt, research_prompt

logger = logging.getLogger(__name__)


class GeminiDeepResearchAgent:
    DEFAULT_MODEL = "gemini-2.0-flash"

    def __init__(self, api_key: str | None = None, model: str | None = None):
        load_dotenv()
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model: str = model or os.getenv("GEMINI_MODEL") or self.DEFAULT_MODEL
        self.backend = gemini_helper.select_backend(self.api_key)

    @property
    def is_available(self) -> bool:
        return self.backend != "none"

    def _generate(self, prompt: str) -> str:
        # One transport for the whole framework: gemini_helper.ask_llm.
        return gemini_helper.ask_llm(prompt, self.model, api_key=self.api_key)

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
