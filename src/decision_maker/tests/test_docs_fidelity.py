#!/usr/bin/env python3
"""Tests for the docs/ fidelity instrument.

These exist because the instrument was wrong and nothing noticed. The defect:
`check_obsidian_fidelity.py` resolved a note's class bullets against the UNION of
the modules that note declared, so a note documenting two engines could attribute
a class to the wrong one. A single-module note was caught; a two-module note was
not. In the vault that let `robust.py` end up with two owners contradicting each
other while the checker printed RESULT: OK.

So the tests below do not assert that the vault is clean. They assert that the
checker can FAIL — driving it against synthetic vaults built in tmp_path, which
is only possible because `check()` takes vault and package as arguments.

Run:  uv run pytest src/decision_maker/tests/test_docs_fidelity.py -v
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
SCRIPT = REPO / "scripts" / "check_obsidian_fidelity.py"


def _load():
    """Import the checker by path: scripts/ is not a package."""
    spec = importlib.util.spec_from_file_location("check_obsidian_fidelity", SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


fid = _load()


@pytest.fixture
def vault(tmp_path: Path) -> Path:
    """A synthetic package: core/ahp.py owns AHPHelper, core/topsis.py does not."""
    pkg = tmp_path / "src" / "decision_maker"
    (pkg / "core").mkdir(parents=True)
    (pkg / "core" / "__init__.py").write_text("", encoding="utf-8")
    (pkg / "core" / "ahp.py").write_text("class AHPHelper:\n    pass\n", encoding="utf-8")
    (pkg / "core" / "topsis.py").write_text("class TOPSISEngine:\n    pass\n", encoding="utf-8")
    v = tmp_path / "docs"
    v.mkdir()
    return v


def _failures_mentioning(vault: Path, pkg: Path, needle: str) -> list[str]:
    failures, _, _ = fid.check(vault, pkg)
    return [f for f in failures if needle in f]


class TestPerSectionClassResolution:
    """The defect: a union pool let a class be attributed to the wrong module."""

    def test_two_module_note_misattributing_a_class_fails(self, vault, tmp_path):
        pkg = tmp_path / "src" / "decision_maker"
        # AHPHelper belongs to ahp.py but is claimed under the topsis.py section.
        (vault / "engine.md").write_text(
            "# Engine\n\n"
            "## `topsis.py`\n\n"
            "### Clases Principales\n\n"
            "- **`AHPHelper`**: imported from the wrong section.\n\n"
            "## `ahp.py`\n\n"
            "### Clases Principales\n\n"
            "- **`AHPHelper`**: its real owner.\n",
            encoding="utf-8",
        )
        assert _failures_mentioning(vault, pkg, "AHPHelper is not defined in topsis.py"), (
            "a class attributed to the wrong section of a two-module note must be caught"
        )

    def test_two_module_note_with_correct_ownership_passes(self, vault, tmp_path):
        pkg = tmp_path / "src" / "decision_maker"
        (vault / "engine.md").write_text(
            "# Engine\n\n"
            "## `topsis.py`\n\n"
            "### Clases Principales\n\n"
            "- **`TOPSISEngine`**: ranking.\n\n"
            "## `ahp.py`\n\n"
            "### Clases Principales\n\n"
            "- **`AHPHelper`**: weights.\n",
            encoding="utf-8",
        )
        failures, _, _ = fid.check(vault, pkg)
        assert failures == []

    def test_class_outside_any_module_section_is_reported(self, vault, tmp_path):
        pkg = tmp_path / "src" / "decision_maker"
        (vault / "loose.md").write_text(
            "# Loose\n\n### Clases Principales\n\n- **`AHPHelper`**: no owning section.\n",
            encoding="utf-8",
        )
        assert _failures_mentioning(vault, pkg, "claimed outside any module section")


class TestOneOwnerPerModule:
    def test_module_claimed_by_two_notes_fails(self, vault, tmp_path):
        pkg = tmp_path / "src" / "decision_maker"
        for name in ("first.md", "second.md"):
            (vault / name).write_text(
                f"# {name}\n\n## `ahp.py`\n\n- **`AHPHelper`**: claimed twice.\n",
                encoding="utf-8",
            )
        assert _failures_mentioning(vault, pkg, "one module, one owner")

    def test_registry_disagreeing_with_the_owning_note_fails(self, vault, tmp_path):
        pkg = tmp_path / "src" / "decision_maker"
        (vault / "real-owner.md").write_text(
            "# Owner\n\n## `ahp.py`\n\n- **`AHPHelper`**: owner.\n", encoding="utf-8"
        )
        (vault / "database-hub.md").write_text(
            "# Hub\n\n| id | note | file |\n|---|---|---|\n"
            "| `MOD-AHP` | [[somewhere-else]] | `core/ahp.py` | `x` | `stable` | — |\n",
            encoding="utf-8",
        )
        assert _failures_mentioning(vault, pkg, "registry points at somewhere-else")

    def test_frontmatter_claiming_a_module_with_no_heading_fails(self, vault, tmp_path):
        pkg = tmp_path / "src" / "decision_maker"
        (vault / "orphan.md").write_text(
            "---\nmodule: \"decision_maker.core.ahp\"\n---\n\n# Orphan\n",
            encoding="utf-8",
        )
        assert _failures_mentioning(vault, pkg, "claims an owner that does not exist")


class TestPyLiterals:
    """Claim 5: a `.py` literal in prose claims the file exists.

    Found by a separate instrument from claims 1-4, and it caught a live one: the
    database-hub.md registry row for MOD-AHP pointed at `core/ahp_helper.py` when
    the file is `core/ahp.py`.
    """

    def test_missing_py_literal_fails(self, vault, tmp_path):
        pkg = tmp_path / "src" / "decision_maker"
        (vault / "n.md").write_text(
            "# N\n\nThe orchestrator lives in `core/does_not_exist.py`.\n", encoding="utf-8"
        )
        assert _failures_mentioning(vault, pkg, "`core/does_not_exist.py` does not exist")

    def test_existing_py_literal_passes(self, vault, tmp_path):
        pkg = tmp_path / "src" / "decision_maker"
        (vault / "n.md").write_text(
            "# N\n\nWeights come from `core/ahp.py`.\n", encoding="utf-8"
        )
        failures, _, _ = fid.check(vault, pkg)
        assert failures == []

    def test_archive_note_is_reported_not_failed(self, vault, tmp_path, capsys):
        pkg = tmp_path / "src" / "decision_maker"
        (vault / "old.md").write_text(
            "---\ntags: [archive, lumina]\ntype: archive\n---\n\n"
            "# Old\n\nBitácora histórica. It used `core/gone.py`.\n",
            encoding="utf-8",
        )
        failures, _, skipped = fid.check(vault, pkg)
        assert failures == [], "a historical claim about a deleted file is not a failure"
        assert skipped["historical .py literals"] == 1
        assert "no longer exists" in capsys.readouterr().out, (
            "it must still be surfaced: an archive note that reads like a current "
            "inventory is its own kind of lie"
        )


class TestProseExtraction:
    def test_class_bullet_inside_a_code_fence_is_not_a_claim(self):
        claims = fid.prose_lines("```\n- **`Ghost`**: template\n```\n- **`Real`**: x\n")
        text = "\n".join(line for _, line in claims)
        assert "Ghost" not in text, "a class bullet inside a fence is a template, not a claim"
        assert "Real" in text, "a class bullet in prose is a claim"

    def test_line_quoting_a_stale_claim_is_not_a_claim(self):
        claims = fid.prose_lines("Una versión anterior decía - **`Ghost`**: x\n")
        assert claims == []


class TestRealVaultIsClean:
    """The live vault must pass — and if it ever regresses, this is what says so."""

    def test_vault_has_no_fidelity_failures(self):
        failures, checked, _ = fid.check(fid.VAULT, fid.PKG)
        assert failures == [], "\n".join(failures)
        assert checked["notes"] >= 50
        assert checked["owners"] >= 20

    def test_every_module_has_exactly_one_owner(self):
        _, _, _ = fid.check(fid.VAULT, fid.PKG)
        owners: dict[str, list[str]] = {}
        for note in fid.VAULT.rglob("*.md"):
            for module, _, _ in fid.sections(fid.prose_lines(note.read_text(encoding="utf-8"))):
                if module:
                    owners.setdefault(module, []).append(note.name)
        dupes = {m: o for m, o in owners.items() if len(set(o)) > 1}
        assert dupes == {}, f"modules with more than one owning note: {dupes}"
