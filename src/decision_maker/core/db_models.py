import uuid
from typing import Optional
from sqlmodel import SQLModel, Field
from sqlalchemy import Column
from sqlalchemy.dialects.sqlite import JSON

class AnalysisSession(SQLModel, table=True):
    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    name: str
    description: Optional[str] = None
    
    # Store options and factors as JSON arrays of serialized dictionaries
    # to maintain compatibility with the complex domain models.
    factors_json: list = Field(default_factory=list, sa_column=Column(JSON))
    options_json: list = Field(default_factory=list, sa_column=Column(JSON))

class OutcomeRecord(SQLModel, table=True):
    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    session_id: str = Field(foreign_key="analysissession.id")
    actual_winner: str
    actual_score: float
    accuracy_percentage: float
    notes: Optional[str] = None
