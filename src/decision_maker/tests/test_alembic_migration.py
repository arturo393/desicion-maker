from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
ALEMBIC_INI = PROJECT_ROOT / "alembic.ini"


class TestAlembicMigration:
    @pytest.mark.skipif(not ALEMBIC_INI.exists(), reason="alembic.ini not present")
    def test_migration_creates_expected_tables(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "migrated.db"
            env = {**os.environ, "DATABASE_URL": f"sqlite:///{db_path}"}
            result = subprocess.run(
                [sys.executable, "-m", "alembic", "-c", str(ALEMBIC_INI), "upgrade", "head"],
                cwd=PROJECT_ROOT,
                env=env,
                capture_output=True,
                text=True,
            )
            assert result.returncode == 0, result.stderr

            import sqlite3

            conn = sqlite3.connect(db_path)
            tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
            assert "analysissession" in tables
            assert "outcomerecord" in tables

            session_cols = {r[1] for r in conn.execute("PRAGMA table_info(analysissession)")}
            assert {"id", "name", "description", "factors_json", "options_json"} <= session_cols

            outcome_cols = {r[1] for r in conn.execute("PRAGMA table_info(outcomerecord)")}
            assert {"id", "session_id", "actual_winner", "actual_score", "accuracy_percentage", "notes"} <= outcome_cols
