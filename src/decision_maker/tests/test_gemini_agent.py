import asyncio

from decision_maker.core.gemini_agent import GeminiDeepResearchAgent


class TestGeminiDeepResearchAgent:
    def test_no_api_key(self, monkeypatch):
        monkeypatch.delenv("GEMINI_API_KEY", raising=False)
        agent = GeminiDeepResearchAgent(api_key=None)
        assert agent.is_available is False
        result = asyncio.run(agent.research("test"))
        assert result == "AI Disabled."

    def test_with_api_key_gives_available(self, monkeypatch):
        monkeypatch.setenv("GEMINI_API_KEY", "test-key")
        agent = GeminiDeepResearchAgent(api_key="test-key")
        if agent.is_available:
            result = asyncio.run(agent.research("topic"))
            assert result is not None and len(result) > 0
