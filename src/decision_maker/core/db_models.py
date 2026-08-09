"""
SQLModel table definitions for analysis sessions and outcome records.
Usage: from decision_maker.core.db_models import AnalysisSession, OutcomeRecord
Does NOT: Open database connections or run migrations.
"""
import uuid

from sqlalchemy import Column
from sqlalchemy.dialects.sqlite import JSON
from sqlmodel import Field, SQLModel


class AnalysisSession(SQLModel, table=True):
    id: str | None = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    name: str
    description: str | None = None

    # Store options and factors as JSON arrays of serialized dictionaries
    # to maintain compatibility with the complex domain models.
    factors_json: list = Field(default_factory=list, sa_column=Column(JSON))
    options_json: list = Field(default_factory=list, sa_column=Column(JSON))

class OutcomeRecord(SQLModel, table=True):
    id: str | None = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    session_id: str = Field(foreign_key="analysissession.id")
    actual_winner: str
    actual_score: float
    accuracy_percentage: float
    notes: str | None = None
