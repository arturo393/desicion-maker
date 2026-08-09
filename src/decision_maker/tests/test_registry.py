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
