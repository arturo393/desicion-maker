from __future__ import annotations

import pytest
from sqlmodel import Session

from decision_maker.core import db
from decision_maker.core.db_models import AnalysisSession


@pytest.fixture
def in_memory_db(monkeypatch):
    from sqlmodel import SQLModel, create_engine

    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        echo=False,
    )
    monkeypatch.setattr(db, "engine", engine)
    db._initialized = False
    yield engine
    db._initialized = False


class TestDbAutoInitialization:
    def test_create_session_creates_tables(self, in_memory_db):
        session = next(db.create_session())
        assert isinstance(session, Session)
        with in_memory_db.connect() as conn:
            assert in_memory_db.dialect.has_table(conn, "analysissession")

    def test_ensure_initialized_is_idempotent(self, in_memory_db):
        db.ensure_initialized()
        db.ensure_initialized()
        assert db._initialized is True

    def test_save_and_load_session(self, in_memory_db):
        from decision_maker.core.db import create_session

        s = next(create_session())
        record = AnalysisSession(name="Test", description="desc", factors_json=[], options_json=[])
        s.add(record)
        s.commit()
        s.refresh(record)
        sid = record.id

        s2 = next(create_session())
        loaded = s2.get(AnalysisSession, sid)
        assert loaded is not None
        assert loaded.name == "Test"
