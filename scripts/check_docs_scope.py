#!/usr/bin/env python3
"""Vault-scope check for docs/.

The vault root is docs/, and that decision is load-bearing: it is what keeps
`results/` (~300 generated reports), `.venv/` and `src/` out of the Obsidian
graph. Two ways to undo it, and both are invisible until somebody opens the repo:

  1. a generated directory appears under docs/ — results/, .venv/, node_modules/
  2. a .obsidian/ directory appears at the REPO ROOT — which makes Obsidian treat
     the whole repository as the vault, putting everything back in the graph

Case 2 actually happened: two byte-identical 1.1 MB copies of .obsidian/ existed,
one per location, neither in .gitignore. A prose rule cannot catch that, because
the rule that was written at the time ("no generated files inside docs/") is
satisfied by .obsidian/ itself. So the decision is checked mechanically here, with
docs/.obsidian/ named as the exception instead of left implicit.

Usage:  uv run python scripts/check_docs_scope.py
Exit 0 when the vault scope holds, 1 otherwise.
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
VAULT = REPO / "docs"

# Directories Obsidian itself creates inside a vault. These are metadata, not
# project content — the scope rule is about the project's generated output.
ALLOWED = {".obsidian"}

# Directory names that mean "the build wrote this", wherever they appear.
GENERATED = {
    "results", ".venv", "venv", "node_modules", "__pycache__", ".pytest_cache",
    ".ruff_cache", ".mypy_cache", "target", "build", "dist", ".tox", ".idea",
}


def main() -> int:
    failures: list[str] = []

    # 1. A .obsidian at the repo root re-opens the whole repository as the vault.
    stray = REPO / ".obsidian"
    if stray.exists():
        failures.append(
            f"{stray.relative_to(REPO)}/ exists: Obsidian would treat the whole repo as the "
            f"vault and put results/, .venv/ and src/ in the graph. The vault root is docs/."
        )

    # 2. Generated directories under the vault.
    for path in sorted(VAULT.rglob("*")):
        if not path.is_dir() or path.name in ALLOWED:
            continue
        # Do not descend into an allowed directory to re-report its children.
        if any(parent.name in ALLOWED for parent in path.parents if parent != VAULT):
            continue
        if path.name in GENERATED:
            failures.append(
                f"{path.relative_to(REPO)}/ is generated content inside the vault; the vault "
                f"root moves back to a curated subdirectory if this is not a one-off."
            )

    # 3. The root .gitignore must keep both out. A rule that is not in .gitignore
    #    is a rule that only holds on this machine.
    #    Matched line-by-line, not as a substring: `/.obsidian/` is a substring of
    #    `/docs/.obsidian/plugins/*/main.js`, so a substring test reports the rule
    #    present after it has been deleted.
    gi = REPO / ".gitignore"
    rules = {ln.strip() for ln in gi.read_text(encoding="utf-8").splitlines()} if gi.exists() else set()
    if "/.obsidian/" not in rules:
        failures.append(".gitignore does not pin `/.obsidian/` on a line of its own — the copy "
                        "at the repo root would be committable and would re-open the repo as "
                        "the vault")

    for f in failures:
        print(f"FAIL {f}")
    print("-" * 88)
    notes = len([p for p in VAULT.rglob("*.md")])
    print(f"vault root: {VAULT.relative_to(REPO)}/ — {notes} notes, no generated content, "
          f"no .obsidian at the repo root")
    print("RESULT:", "OK — vault scope holds" if not failures else "FAILED")
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
