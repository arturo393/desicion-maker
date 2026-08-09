from __future__ import annotations

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client(monkeypatch, tmp_path):
    from sqlmodel import SQLModel, create_engine

    from decision_maker.core import (
        db,
        db_models,  # noqa: F401  (registers tables on SQLModel.metadata)
    )

    db_path = tmp_path / "api_test.db"
    engine = create_engine(
        f"sqlite:///{db_path}",
        connect_args={"check_same_thread": False},
    )
    monkeypatch.setattr(db, "engine", engine)
    db._initialized = False
    SQLModel.metadata.create_all(engine)
    db._initialized = True

    from decision_maker.api.server import app

    with TestClient(app) as c:
        yield c

    db._initialized = False


class TestApiServer:
    def test_health(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json() == {"status": "ok"}

    def test_list_templates(self, client):
        resp = client.get("/templates")
        assert resp.status_code == 200
        body = resp.json()
        assert isinstance(body, dict)
        assert len(body) > 0

    def test_analyze_returns_results(self, client):
        payload = {
            "name": "API Test",
            "description": "",
            "mode": "express",
            "use_ai": False,
            "factors": [{"name": "Cost", "weight": 0.5, "maximize": False}],
            "options": [
                {
                    "name": "A",
                    "variables": {"Cost": {"distribution": "deterministic", "params": [50]}},
                },
                {
                    "name": "B",
                    "variables": {"Cost": {"distribution": "deterministic", "params": [100]}},
                },
            ],
        }
        resp = client.post("/analyze", json=payload)
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert body["status"] == "completed"
        assert "session_id" in body
        assert "mc_results" in body
        assert set(body["mc_results"].keys()) == {"A", "B"}

    def _create_session(self, client, name):
        payload = {
            "name": name,
            "mode": "express",
            "factors": [{"name": "Cost", "weight": 1.0, "maximize": False}],
            "options": [
                {
                    "name": "A",
                    "variables": {"Cost": {"distribution": "deterministic", "params": [10]}},
                }
            ],
        }
        resp = client.post("/analyze", json=payload)
        assert resp.status_code == 200, resp.text
        return resp.json()["session_id"]

    def test_list_sessions_and_get(self, client):
        session_id = self._create_session(client, "Sess Test")

        resp = client.get("/sessions")
        assert resp.status_code == 200
        assert any(s["id"] == session_id for s in resp.json())

        resp = client.get(f"/sessions/{session_id}")
        assert resp.status_code == 200
        assert resp.json()["name"] == "Sess Test"

    def test_get_missing_session_returns_404(self, client):
        resp = client.get("/sessions/does-not-exist")
        assert resp.status_code == 404

    def test_register_outcome(self, client):
        session_id = self._create_session(client, "Outcome Test")

        resp = client.post(
            f"/sessions/{session_id}/outcome",
            json={"actual_winner": "A", "actual_score": 0.9, "notes": "verified"},
        )
        assert resp.status_code == 200, resp.text
        assert resp.json()["actual_winner"] == "A"

    def test_register_outcome_missing_session(self, client):
        resp = client.post(
            "/sessions/nope/outcome",
            json={"actual_winner": "A", "actual_score": 0.5},
        )
        assert resp.status_code == 404

    def test_calibration_endpoint(self, client):
        session_id = self._create_session(client, "Calib Test")

        # Register two outcomes: one hit, one miss, with predicted winner + confidence.
        client.post(
            f"/sessions/{session_id}/outcome",
            json={
                "actual_winner": "A",
                "actual_score": 0.9,
                "predicted_winner": "A",
                "confidence": 0.8,
            },
        )
        client.post(
            f"/sessions/{session_id}/outcome",
            json={
                "actual_winner": "B",
                "actual_score": 0.5,
                "predicted_winner": "A",
                "confidence": 0.9,
            },
        )

        resp = client.get("/calibration")
        assert resp.status_code == 200
        body = resp.json()
        assert body["n_outcomes"] == 2
        assert body["hit_rate"] == 0.5
        assert body["mean_confidence"] == pytest.approx(0.85)
        assert body["verdict"] in ("moderately_calibrated", "poorly_calibrated", "overconfident")
