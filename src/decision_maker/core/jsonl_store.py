"""
Generic JSONL append-only store with per-line corruption tolerance.
Usage: from decision_maker.core.jsonl_store import JsonlStore
Does NOT: Know about any specific domain model or business logic.
"""

from __future__ import annotations

__all__ = ["JsonlStore"]

import json
import logging
from dataclasses import asdict
from pathlib import Path
from typing import Any, Generic, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")


class JsonlStore(Generic[T]):
    """
    Base class for JSONL-backed stores.

    Encapsulates the four duplicated patterns across outcome/journal/
    commitment/trace stores:
      1. Load: per-line try/except so one corrupt line doesn't drop the rest
      2. Save: rewrite from memory (append-only log semantics)
      3. entries(): return all records
      4. get_entry(id): find by a field

    Subclasses provide the dataclass type, a path, and the id field name.
    """

    def __init__(self, path: str | Path | None, default_path: str, id_field: str = "decision_id"):
        self.path = Path(path or default_path)
        self.id_field = id_field
        self._entries: list[T] = []
        self._load()

    def _load(self) -> None:
        if not self.path.exists():
            return
        with open(self.path) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    self._entries.append(self._deserialize(data))
                except (json.JSONDecodeError, TypeError, ValueError) as e:
                    logger.warning(f"Skipping corrupt line in {self.path.name}: {e}")

    def _deserialize(self, data: dict[str, Any]) -> T:
        raise NotImplementedError

    def _save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.path, "w") as f:
            for entry in self._entries:
                f.write(json.dumps(asdict(entry)) + "\n")

    def entries(self) -> list[T]:
        return list(self._entries)

    def get_entry(self, entry_id: str) -> T | None:
        for entry in self._entries:
            if getattr(entry, self.id_field) == entry_id:
                return entry
        return None
