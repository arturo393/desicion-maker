#!/usr/bin/env python3
"""Run the repo's standalone checkers as tests, so they cannot rot unobserved.

Each of these lives in `scripts/` as a runnable file with its own `exit 1`.
CI invokes them as separate steps, which means the suite is fully green while a
checker is broken — the exact shape of "a test file that is not in the build
list is zero coverage, silently". Nothing in `pytest` was asserting they run.

They are invoked here as subprocesses with `sys.executable` on purpose, not
imported: their contract is their exit code, and importing them would let an
import-time side effect stand in for a real run. `sys.executable` also means the
checker runs on the interpreter running the suite, which is the whole point
after the venv was found to be missing its test extra (see the worklog).

Run:  uv run pytest src/decision_maker/tests/test_checkers_run.py -v
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]

# (script, argv-after-the-script-name, what it is supposed to protect)
CHECKERS = [
    ("check_docs_links.py", [], "every [[wikilink]] in the vault resolves"),
    ("check_docs_scope.py", [], "the vault root is docs/ and holds no generated content"),
    ("check_obsidian_fidelity.py", [], "the notes match the source they describe"),
    ("check_obsidian_language.py", [], "no cross-language drift inside the vault"),
    ("dev_agents_linter.py", ["src/decision_maker/core"], "the @dev-agents code rules"),
]


def _run(script: str, args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, f"scripts/{script}", *args],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
        check=False,
    )


@pytest.mark.parametrize(("script", "args", "protects"), CHECKERS, ids=[c[0] for c in CHECKERS])
def test_checker_passes(
    script: str, args: list[str], protects: str
) -> None:
    """Each checker exits 0, which is what CI reads and nothing else verifies."""
    result = _run(script, args)
    assert result.returncode == 0, (
        f"scripts/{script} exited {result.returncode}; it is supposed to protect: {protects}\n"
        f"--- stdout ---\n{result.stdout}\n--- stderr ---\n{result.stderr}"
    )


@pytest.mark.parametrize("script", [c[0] for c in CHECKERS], ids=[c[0] for c in CHECKERS])
def test_checker_exists_and_is_runnable(script: str) -> None:
    """A checker that was renamed or deleted must fail here, not vanish.

    Without this, deleting a checker would remove its test with it, and the
    protection would disappear with no failure anywhere.
    """
    path = REPO / "scripts" / script
    assert path.is_file(), f"scripts/{script} no longer exists but CI still runs it"
    assert path.read_text(encoding="utf-8").strip(), f"scripts/{script} is empty"
