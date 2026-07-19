from __future__ import annotations

__all__ = ["GeminiDeepResearchAgent"]

import os
from typing import Optional

from dotenv import load_dotenv


class GeminiDeepResearchAgent:
    DEFAULT_MODEL = "gemini-2.0-flash"

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
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
                contents=f"Research Topic: {topic}\nContext: {context}\nProvide analysis.",
            )
            return response.text
        except (ConnectionError, TimeoutError, ValueError) as e:
            return f"Error: {e}"
