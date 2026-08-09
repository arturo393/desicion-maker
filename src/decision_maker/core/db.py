"""
Core db module.
Provides db capabilities.
Does NOT perform UI rendering.
"""
import os
import threading

from sqlmodel import Session, SQLModel, create_engine

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///decision_maker.db")

engine = create_engine(DATABASE_URL, echo=False)

_initialized = False
_init_lock = threading.Lock()


def create_db_and_tables():
    """Create all tables if they do not already exist. Idempotent."""
    SQLModel.metadata.create_all(engine)


def ensure_initialized() -> None:
    """Ensure the database schema exists exactly once, guarded against races."""
    global _initialized
    if _initialized:
        return
    with _init_lock:
        if not _initialized:
            create_db_and_tables()
            _initialized = True


def create_session():
    ensure_initialized()
    with Session(engine) as session:
        yield session
