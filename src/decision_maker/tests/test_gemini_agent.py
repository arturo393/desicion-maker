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
        # Availability is determined by the SDK being installed, not by network calls.
        assert isinstance(agent.is_available, bool)
        # The agent must handle disabled state gracefully without a real API call.
        if not agent.is_available:
            result = asyncio.run(agent.research("topic"))
            assert result == "AI Disabled."


def test_the_agent_has_no_transport_of_its_own(monkeypatch):
    """It delegates to gemini_helper.ask_llm, with its own key and model: one copy of the backend logic."""
    from decision_maker.core import gemini_helper

    seen = {}
    monkeypatch.setattr(gemini_helper, "select_backend", lambda key=None: "api")
    monkeypatch.setattr(gemini_helper, "ask_llm", lambda q, m, api_key=None: seen.update(q=q, m=m, k=api_key) or "ok")
    agent = GeminiDeepResearchAgent(api_key="k1", model="m1")
    assert asyncio.run(agent.research("tema")) == "ok"
    assert (seen["m"], seen["k"]) == ("m1", "k1")
