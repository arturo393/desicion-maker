"""
Every import in analyses/ (and analyses/research/) resolves: framework names exist, bare modules are installed or siblings.
Run: uv run pytest src/decision_maker/tests/test_analyses_imports.py
Does NOT: execute the scripts (the smoke suite runs analyses/*.py; research/ needs network and is never run in CI).

Why: when the scripts lived inside the package, two of them imported `scripts.gemini_query` and a bare
`deep_research_decision_agent` — names that only resolved with a sys.path hack pointing at a directory
that had moved. Nothing ran them, so nothing noticed (found 2026-10-18 while moving them out).
"""

from __future__ import annotations

import ast
import importlib
import importlib.util
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
ANALYSES = REPO / "analyses"
FILES = sorted(ANALYSES.rglob("*.py"))

# Optional extras: imported behind a guard or only on the online path. Declared, not guessed.
OPTIONAL = {"google", "requests"}


def _imports(path: Path) -> list[tuple[str, list[str]]]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    found: list[tuple[str, list[str]]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            found += [(alias.name, []) for alias in node.names]
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            found.append((node.module, [a.name for a in node.names]))
    return found


def test_the_glob_sees_both_directories() -> None:
    """Negative control on the instrument: an empty glob would make every case below pass."""
    assert any(p.parent == ANALYSES for p in FILES)
    assert any(p.parent.name == "research" for p in FILES)


@pytest.mark.parametrize("path", FILES, ids=lambda p: str(p.relative_to(ANALYSES)))
def test_every_import_resolves(path: Path) -> None:
    broken: list[str] = []
    for module, names in _imports(path):
        top = module.split(".")[0]
        if top in OPTIONAL:
            continue
        if (path.parent / f"{top}.py").exists():  # sibling script, on sys.path[0] when run directly
            continue
        if importlib.util.find_spec(top) is None:
            broken.append(module)
            continue
        if top == "decision_maker":
            mod = importlib.import_module(module)
            broken += [f"{module}.{n}" for n in names if n != "*" and not hasattr(mod, n)]
    assert not broken, f"{path.name} imports names that do not resolve: {broken}"
