"""
Wrapper client for querying Gemini models to analyze decision options and factors.
Usage: from decision_maker.core.gemini_agent import GeminiDeepResearchAgent
Does NOT: Fallback silently without raising configured API exceptions.
"""

from __future__ import annotations

__all__ = ["GeminiDeepResearchAgent"]

import logging
import os

from dotenv import load_dotenv

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

    @property
    def is_available(self) -> bool:
        return self._client is not None

    async def research(self, topic: str, context: str = "") -> str:
        client = self._client
        if client is None:
            return "AI Disabled."
        try:
            response = client.models.generate_content(
                model=self.model,
                contents=research_prompt(topic, context),
            )
            return response.text
        except (ConnectionError, TimeoutError, ValueError) as e:
            return f"Error: {e}"

    async def calibrate_priors(self, context_data: str) -> dict:
        """
        Uses the LLM to dynamically adjust probability distribution priors
        (e.g., standard deviation and mean adjustments) based on real-world context.
        """
        client = self._client
        if client is None:
            return {}
        try:
            response = client.models.generate_content(
                model=self.model,
                contents=calibration_prompt(context_data),
            )
            import json
            import re

            text = response.text
            match = re.search(r"\{.*\}", text, re.DOTALL)
            if match:
                return json.loads(match.group(0))
            return {}
        except (ConnectionError, TimeoutError, ValueError, json.JSONDecodeError) as e:
            logger.error(f"Gemini API Error: {e}")
            return {}
