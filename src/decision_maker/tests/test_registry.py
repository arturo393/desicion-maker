import sqlite3
import tempfile
from pathlib import Path

import pytest

from decision_maker.core.registry import DecisionRegistry, SaveDecisionRequest, SaveTemplateRequest


@pytest.fixture
def registry():
    with tempfile.TemporaryDirectory() as d:
        db = str(Path(d) / "test.db")
        r = DecisionRegistry(db)
        yield r


class TestDecisionRegistry:
    def test_save_and_get_decision(self, registry):
        fid = registry.save_decision(
            SaveDecisionRequest(
                name="Test Decision",
                mode="standard",
                num_simulations=1000,
                factors=[{"name": "Cost", "weight": 0.5}],
                options=[{"name": "OptA"}, {"name": "OptB"}],
                results={"winner": "OptA"},
                description="A test",
                tags=["test"],
            )
        )
        assert fid > 0
        got = registry.fetch_decision(fid)
        assert got is not None
        assert got["name"] == "Test Decision"
        assert got["tags"] == ["test"]

    def test_list_decisions(self, registry):
        registry.save_decision(SaveDecisionRequest("D1", "express", 100, [], [], {}))
        registry.save_decision(SaveDecisionRequest("D2", "standard", 200, [], [], {}))
        items = registry.list_decisions()
        assert len(items) >= 2

    def test_list_with_search(self, registry):
        registry.save_decision(SaveDecisionRequest("Alpha Beta", "express", 100, [], [], {}))
        registry.save_decision(SaveDecisionRequest("Gamma Delta", "standard", 200, [], [], {}))
        items = registry.list_decisions(search="Alpha")
        assert len(items) == 1
        assert items[0]["name"] == "Alpha Beta"

    def test_list_with_tag(self, registry):
        registry.save_decision(SaveDecisionRequest("Tagged", "express", 100, [], [], {}, tags=["urgent"]))
        registry.save_decision(SaveDecisionRequest("Normal", "standard", 200, [], [], {}, tags=["normal"]))
        items = registry.list_decisions(tag="urgent")
        assert len(items) == 1

    def test_delete_decision(self, registry):
        fid = registry.save_decision(SaveDecisionRequest("ToDelete", "express", 100, [], [], {}))
        assert registry.delete_decision(fid) is True
        assert registry.fetch_decision(fid) is None

    def test_update_decision(self, registry):
        fid = registry.save_decision(SaveDecisionRequest("OldName", "express", 100, [], [], {}))
        assert registry.update_decision(fid, name="NewName", status="archived") is True
        got = registry.fetch_decision(fid)
        assert got["name"] == "NewName"
        assert got["status"] == "archived"

    def test_get_nonexistent(self, registry):
        assert registry.fetch_decision(99999) is None

    def test_save_and_get_template(self, registry):
        tid = registry.save_template(
            SaveTemplateRequest(
                name="Test Template",
                factors=[{"name": "X", "weight": 1.0}],
                description="Template desc",
                category="Test",
            )
        )
        assert tid > 0
        got = registry.fetch_template(tid)
        assert got["name"] == "Test Template"

    def test_get_template_by_name(self, registry):
        registry.save_template(SaveTemplateRequest("UniqueName", [{"name": "X", "weight": 1.0}]))
        got = registry.fetch_template_by_name("UniqueName")
        assert got is not None
        assert got["name"] == "UniqueName"

    def test_list_templates_by_category(self, registry):
        registry.save_template(SaveTemplateRequest("T1", [], category="A"))
        registry.save_template(SaveTemplateRequest("T2", [], category="B"))
        registry.save_template(SaveTemplateRequest("T3", [], category="A"))
        items = registry.list_templates(category="A")
        assert len(items) == 2

    def test_delete_template(self, registry):
        tid = registry.save_template(SaveTemplateRequest("DelTpl", []))
        assert registry.delete_template(tid) is True

    def test_seed_default_templates(self, registry):
        registry.seed_default_templates()
        items = registry.list_templates()
        assert len(items) >= 4
        names = [i["name"] for i in items]
        assert "Vendor Selection" in names
        assert "Project Prioritization" in names

    def test_second_save_updates_and_returns_the_same_id(self, registry):
        """The upsert path: the second save hits IntegrityError, falls back to UPDATE,
        and then re-reads the id. That re-read is the write's own verification — the
        id is not taken from the UPDATE cursor, which does not have one."""
        first = registry.save_template(SaveTemplateRequest("UpsertMe", [{"name": "X", "weight": 1.0}]))
        second = registry.save_template(
            SaveTemplateRequest("UpsertMe", [{"name": "X", "weight": 0.5}], description="updated")
        )
        assert first == second
        assert registry.fetch_template_by_name("UpsertMe")["description"] == "updated"

    def test_unresolvable_template_id_raises_without_inheriting_the_integrity_error(self, registry):
        """If the re-read after the upsert returns no row, save_template raises.

        The display of the chain matters as much as the raise. The IntegrityError
        was handled — the code recovered by updating the row — so the missing row
        is a NEW failure and must not be presented as its consequence. Chained, the
        traceback says "during handling of the above exception, another exception
        occurred" and sends the reader to hunt a duplicate-key bug that is already
        fixed.

        Writing the test corrected the assumption behind it: `from None` does NOT
        clear `__context__`, it sets `__cause__` to None and `__suppress_context__`
        to True, which is what hides the chain. So the assertions below are about
        the suppression, not about the context being absent — asserting the context
        was cleared would have been a test that cannot pass.
        """
        registry.save_template(SaveTemplateRequest("Vanish", []))

        # The connection lives in a thread-local and is handed out by a read-only
        # property, so the swap happens on the thread-local. Everything except the
        # id re-read behaves normally, which means the IntegrityError and the
        # UPDATE that precede it are real rather than staged.
        real_conn = registry._conn

        def execute(sql, *args, **kwargs):
            cursor = real_conn.execute(sql, *args, **kwargs)
            if "SELECT id FROM templates" in sql:
                return _EmptyRowCursor(cursor)
            return cursor

        registry._local.conn = _ConnectionProxy(real_conn, execute)
        try:
            with pytest.raises(sqlite3.Error) as exc:
                registry.save_template(SaveTemplateRequest("Vanish", []))
        finally:
            registry._local.conn = real_conn

        assert "after upsert" in str(exc.value)
        # No explicit cause, and the handled IntegrityError is suppressed from the
        # traceback even though Python still records it as the context.
        assert exc.value.__cause__ is None
        assert exc.value.__suppress_context__ is True


class _ConnectionProxy:
    """A connection whose `execute` can be replaced.

    Delegating via __getattr__ keeps commit, rollback and every other call on the
    real connection, so the test exercises the real transaction behaviour.
    """

    def __init__(self, inner, execute):
        self._inner = inner
        self.execute = execute

    def __getattr__(self, name):
        return getattr(self._inner, name)


class _EmptyRowCursor:
    """Delegates to a real cursor but reports that the row is gone.

    Stands in for the failure where the UPDATE succeeded and the following SELECT
    finds nothing. Simulating it with a real database would mean racing a delete,
    and stubbing the whole connection would test the stub instead of the method.
    """

    def __init__(self, inner):
        self._inner = inner

    def fetchone(self):
        return None

    def __getattr__(self, name):
        return getattr(self._inner, name)
