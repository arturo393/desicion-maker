"""
Registry for saving, retrieving, and managing decision configurations and templates.
Usage: from decision_maker.core.registry import DecisionRegistry
Does NOT: Execute decision calculations or generate reports.
"""

from __future__ import annotations

__all__ = ["DecisionRegistry"]

import json
import logging
import sqlite3
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np

logger = logging.getLogger(__name__)


class DecisionRegistry:
    """
    SQLite-backed persistent registry for decision analyses.

    Stores full analysis results with metadata for querying,
    comparison, and outcome tracking over time.
    """

    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            db_path = str(Path.home() / ".decision_maker" / "registry.db")
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._local = threading.local()
        self._init_db()

    @property
    def _conn(self) -> sqlite3.Connection:
        if not hasattr(self._local, "conn") or self._local.conn is None:
            self._local.conn = sqlite3.connect(self.db_path)
            self._local.conn.row_factory = sqlite3.Row
            self._local.conn.execute("PRAGMA journal_mode=WAL")
            self._local.conn.execute("PRAGMA foreign_keys=ON")
        return self._local.conn

    def _init_db(self) -> None:
        conn = self._conn
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS decisions (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                name        TEXT NOT NULL,
                description TEXT DEFAULT '',
                mode        TEXT NOT NULL DEFAULT 'standard',
                num_simulations INTEGER DEFAULT 10000,
                created_at  TEXT NOT NULL DEFAULT (datetime('now')),
                updated_at  TEXT NOT NULL DEFAULT (datetime('now')),
                tags        TEXT DEFAULT '[]',
                status      TEXT DEFAULT 'completed',
                notes       TEXT DEFAULT '',
                results_json TEXT,
                factors_json TEXT,
                options_json TEXT
            );
            CREATE TABLE IF NOT EXISTS templates (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                name        TEXT NOT NULL UNIQUE,
                description TEXT DEFAULT '',
                category    TEXT DEFAULT '',
                factors_json TEXT NOT NULL,
                options_json TEXT,
                created_at  TEXT NOT NULL DEFAULT (datetime('now'))
            );
            CREATE INDEX IF NOT EXISTS idx_decisions_created ON decisions(created_at DESC);
            CREATE INDEX IF NOT EXISTS idx_decisions_name ON decisions(name);
            CREATE INDEX IF NOT EXISTS idx_templates_category ON templates(category);
        """)
        conn.commit()

    def close(self) -> None:
        if hasattr(self._local, "conn") and self._local.conn is not None:
            self._local.conn.close()
            self._local.conn = None

    # ── Decisions CRUD ───────────────────────────────────────────────

    def save_decision(
        self,
        name: str,
        mode: str,
        num_simulations: int,
        factors: List[Dict[str, Any]],
        options: List[Dict[str, Any]],
        results: Dict[str, Any],
        description: str = "",
        tags: Optional[List[str]] = None,
        notes: str = "",
    ) -> int:
        conn = self._conn
        now = datetime.now(timezone.utc).isoformat()
        conn.execute(
            """INSERT INTO decisions
               (name, description, mode, num_simulations, created_at, updated_at,
                tags, notes, results_json, factors_json, options_json)
               VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
            (
                name,
                description,
                mode,
                num_simulations,
                now,
                now,
                json.dumps(tags or []),
                notes,
                json.dumps(results, default=str, cls=_Encoder),
                json.dumps(factors, default=str),
                json.dumps(options, default=str),
            ),
        )
        conn.commit()
        decision_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        logger.info(f"Saved decision #{decision_id}: {name}")
        return decision_id

    def list_decisions(
        self,
        limit: int = 20,
        offset: int = 0,
        tag: Optional[str] = None,
        search: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        query = "SELECT id, name, description, mode, num_simulations, created_at, tags, status FROM decisions"
        params: List[Any] = []
        conditions = []
        if tag:
            conditions.append("tags LIKE ?")
            params.append(f'%"{tag}"%')
        if search:
            conditions.append("(name LIKE ? OR description LIKE ?)")
            params.extend([f"%{search}%", f"%{search}%"])
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        rows = self._conn.execute(query, params).fetchall()
        return [dict(r) for r in rows]

    def get_decision(self, decision_id: int) -> Optional[Dict[str, Any]]:
        row = self._conn.execute("SELECT * FROM decisions WHERE id = ?", (decision_id,)).fetchone()
        if row is None:
            return None
        result = dict(row)
        for key in ("tags", "results_json", "factors_json", "options_json"):
            if result.get(key):
                try:
                    result[key] = json.loads(result[key])
                except (json.JSONDecodeError, TypeError):
                    pass
        return result

    def delete_decision(self, decision_id: int) -> bool:
        cur = self._conn.execute("DELETE FROM decisions WHERE id = ?", (decision_id,))
        self._conn.commit()
        return cur.rowcount > 0

    def update_decision(
        self,
        decision_id: int,
        **fields,
    ) -> bool:
        allowed = {"name", "description", "notes", "tags", "status"}
        updates = {k: v for k, v in fields.items() if k in allowed}
        if not updates:
            return False
        updates["updated_at"] = datetime.now(timezone.utc).isoformat()
        if "tags" in updates and isinstance(updates["tags"], list):
            updates["tags"] = json.dumps(updates["tags"])
        set_clause = ", ".join(f"{k} = ?" for k in updates)
        values = list(updates.values()) + [decision_id]
        cur = self._conn.execute(f"UPDATE decisions SET {set_clause} WHERE id = ?", values)
        self._conn.commit()
        return cur.rowcount > 0

    # ── Templates CRUD ───────────────────────────────────────────────

    def save_template(
        self,
        name: str,
        factors: List[Dict[str, Any]],
        description: str = "",
        category: str = "",
        options: Optional[List[Dict[str, Any]]] = None,
    ) -> int:
        try:
            cur = self._conn.execute(
                """INSERT INTO templates (name, description, category, factors_json, options_json)
                   VALUES (?,?,?,?,?)""",
                (name, description, category, json.dumps(factors, default=str), json.dumps(options or [], default=str)),
            )
            self._conn.commit()
            return cur.lastrowid
        except sqlite3.IntegrityError:
            logger.warning(f"Template '{name}' already exists, updating")
            cur = self._conn.execute(
                """UPDATE templates SET description=?, category=?, factors_json=?, options_json=?
                   WHERE name=?""",
                (description, category, json.dumps(factors, default=str), json.dumps(options or [], default=str), name),
            )
            self._conn.commit()
            return cur.lastrowid

    def list_templates(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        if category:
            rows = self._conn.execute(
                "SELECT id, name, description, category, created_at FROM templates WHERE category = ? ORDER BY name",
                (category,),
            ).fetchall()
        else:
            rows = self._conn.execute(
                "SELECT id, name, description, category, created_at FROM templates ORDER BY category, name"
            ).fetchall()
        return [dict(r) for r in rows]

    def _hydrate_template(self, row: Optional[sqlite3.Row]) -> Optional[Dict[str, Any]]:
        if row is None:
            return None
        result = dict(row)
        for key in ("factors_json", "options_json"):
            if result.get(key):
                try:
                    result[key] = json.loads(result[key])
                except (json.JSONDecodeError, TypeError):
                    pass
        return result

    def get_template(self, template_id: int) -> Optional[Dict[str, Any]]:
        row = self._conn.execute("SELECT * FROM templates WHERE id = ?", (template_id,)).fetchone()
        return self._hydrate_template(row)

    def get_template_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        row = self._conn.execute("SELECT * FROM templates WHERE name = ?", (name,)).fetchone()
        return self._hydrate_template(row)

    def delete_template(self, template_id: int) -> bool:
        cur = self._conn.execute("DELETE FROM templates WHERE id = ?", (template_id,))
        self._conn.commit()
        return cur.rowcount > 0

    def seed_default_templates(self) -> None:
        defaults = [
            {
                "name": "Vendor Selection",
                "description": "Compare technology vendors across cost, quality, support, and risk",
                "category": "Procurement",
                "factors": [
                    {"name": "Cost", "weight": 0.3, "maximize": False, "category": "Financial"},
                    {"name": "Quality", "weight": 0.3, "maximize": True, "category": "Technical"},
                    {"name": "Support", "weight": 0.2, "maximize": True, "category": "Service"},
                    {"name": "Risk", "weight": 0.2, "maximize": False, "category": "Financial"},
                ],
            },
            {
                "name": "Project Prioritization",
                "description": "Rank projects by strategic value, feasibility, cost, and ROI",
                "category": "Strategy",
                "factors": [
                    {"name": "Strategic Value", "weight": 0.35, "maximize": True, "category": "Strategy"},
                    {"name": "Feasibility", "weight": 0.25, "maximize": True, "category": "Technical"},
                    {"name": "Cost", "weight": 0.2, "maximize": False, "category": "Financial"},
                    {"name": "ROI", "weight": 0.2, "maximize": True, "category": "Financial"},
                ],
            },
            {
                "name": "Career Decision",
                "description": "Evaluate job offers or career paths across key dimensions",
                "category": "Personal",
                "factors": [
                    {"name": "Salary", "weight": 0.25, "maximize": True, "category": "Compensation"},
                    {"name": "Growth", "weight": 0.25, "maximize": True, "category": "Career"},
                    {"name": "Culture", "weight": 0.2, "maximize": True, "category": "Workplace"},
                    {"name": "Location", "weight": 0.15, "maximize": True, "category": "Lifestyle"},
                    {"name": "Risk", "weight": 0.15, "maximize": False, "category": "Financial"},
                ],
            },
            {
                "name": "Investment Analysis",
                "description": "Compare investment opportunities across return, risk, and liquidity",
                "category": "Finance",
                "factors": [
                    {"name": "Expected Return", "weight": 0.35, "maximize": True, "category": "Financial"},
                    {"name": "Risk", "weight": 0.3, "maximize": False, "category": "Financial"},
                    {"name": "Liquidity", "weight": 0.2, "maximize": True, "category": "Financial"},
                    {"name": "Time Horizon", "weight": 0.15, "maximize": False, "category": "Financial"},
                ],
            },
        ]
        for t in defaults:
            try:
                self.save_template(**t)
            except (sqlite3.Error, ValueError) as e:
                logger.warning(f"Could not seed template '{t['name']}': {e}")


class _Encoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)
