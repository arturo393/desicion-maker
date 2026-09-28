#!/usr/bin/env python3
"""Source-fidelity check for the docs/ vault.

A vault note that names a class which does not exist is worse than one that
names nothing: the reader trusts it and writes an import that raises. This
resolves every claim the notes make against src/decision_maker/ — the producer,
not the docstring the note was copied from.

Usage:  uv run python scripts/check_obsidian_fidelity.py
Exit 0 when every claim holds, 1 otherwise.

Four claims are checked:
  1. every `## \\`module.py\\`` heading names a real module
  2. every `**\\`ClassName\\`** bullet names a real top-level class *in the module
     that owns its section* — not in any module the note happens to mention
  3. every `from decision_maker... import X` in backticks resolves at runtime
  4. every module has exactly one owning note, and the three ownership channels
     agree: the `## \\`module.py\\`` heading, the `module:` frontmatter field and
     the row in database-hub.md

Claim 2 runs against the AST, claim 3 against an actual import — two instruments,
so one can catch the other's blind spot.

Why claim 2 is scoped per section: a note documenting two engines is the normal
case here (monte-carlo-engine.md owns monte_carlo.py and bootstrap.py), and a
union pool would let it attribute a class to the wrong engine. That is not
hypothetical — it shipped, and robust.py ended up with two owners disagreeing
about the mechanism while this checker printed RESULT: OK.

`check()` takes the vault and package as arguments so tests can drive it against a
synthetic vault. An instrument that cannot be pointed at a fixture cannot be shown
to fail, and the defect above survived precisely because nothing could ask it to.
"""
from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
VAULT = REPO / "docs"
PKG = REPO / "src" / "decision_maker"

MODULE_HEADING = re.compile(r"^##\s+`([a-z_0-9]+\.py)`", re.M)
CLASS_BULLET = re.compile(r"^-\s+\*\*`([A-Za-z_][A-Za-z_0-9]*)`\*\*", re.M)
IMPORT = re.compile(r"`(from decision_maker[.\w]*\s+import\s+[^`]+)`")
# A `.py` literal in prose is a claim that the file exists. Not a heading claim, not a
# class claim: found by a separate instrument, and the two that mattered were a
# registry row pointing at `core/ahp_helper.py` (the file is `core/ahp.py`) and the
# "min-max regret" description of robust.py.
PY_LITERAL = re.compile(r"`([A-Za-z_][\w/]*\.py)`")
FENCE = re.compile(r"^\s*(```|~~~)")

# A note that documents a stale claim quotes the broken form on purpose, and the
# skeleton in note-schema.md contains a fenced template. Neither is a claim about
# the codebase, so both are skipped — and counted, so the skipping stays visible
# instead of quietly widening what the check ignores.
COUNTEREXAMPLE = re.compile(r"versión anterior|earlier version|stale claim", re.I)


def prose_lines(text: str) -> list[tuple[int, str]]:
    """Lines that make claims: outside code fences, not quoting a stale claim."""
    out, fenced = [], False
    for n, line in enumerate(text.splitlines(), start=1):
        if FENCE.match(line):
            fenced = not fenced
            continue
        if fenced or COUNTEREXAMPLE.search(line):
            continue
        out.append((n, line))
    return out


def sections(claims: list[tuple[int, str]]) -> list[tuple[str | None, int, str]]:
    """Attribute each claiming line to the module whose heading precedes it.

    Returns (module_or_None, line_no, line) in document order. A class bullet that
    precedes any `## `module.py`` heading gets None: it names a class but claims no
    owner, so it cannot be resolved — reported, not quietly allowed.
    """
    out, current = [], None
    for n, line in claims:
        m = MODULE_HEADING.match(line)
        if m:
            current = m.group(1)
        out.append((current, n, line))
    return out


def module_path(pkg: Path, module: str) -> Path | None:
    """Resolve a module filename against the package, preferring core/."""
    for base in (pkg / "core", pkg):
        if (base / module).exists():
            return base / module
    return None


def frontmatter_module(text: str) -> str | None:
    """The `module:` field of the YAML frontmatter, as a module filename."""
    if not text.startswith("---"):
        return None
    m = re.search(r"^module:\s*[\"']?([\w.]+)[\"']?\s*$", text, re.M)
    return f"{m.group(1).rsplit('.', 1)[-1]}.py" if m else None


def registry_owners(vault: Path) -> dict[str, str]:
    """module -> note name, from the database-hub.md module registry table."""
    hub = vault / "database-hub.md"
    if not hub.exists():
        return {}
    owners: dict[str, str] = {}
    for line in hub.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|"):
            continue
        note = re.search(r"\[\[([^\]|]+)", line)
        # The module column holds a path (`core/ahp.py`), not a bare name. Matching
        # a dotted word only would silently yield no owners at all — the channel
        # would look present and verify nothing.
        mod = re.search(r"`([\w./-]+\.py)`", line)
        if note and mod:
            owners[Path(mod.group(1)).name] = note.group(1).strip()
    return owners


def classes_in(path: Path) -> set[str]:
    """Top-level class names declared by a module."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    return {n.name for n in tree.body if isinstance(n, ast.ClassDef)}


def is_archive(text: str) -> bool:
    """True when the note declares itself historical.

    An archive note's claims are about the past, so a file it names may legitimately
    be gone. Those are counted and reported, never treated as failures — and never
    silently dropped either, because a historical note that reads like a current
    inventory is its own kind of lie.
    """
    m = re.search(r"^tags:\s*\[(.*?)\]\s*$", text, re.M)
    return bool(m and "archive" in {t.strip().strip("'\" ") for t in m.group(1).split(",")})


def check(vault: Path, pkg: Path) -> tuple[list[str], dict[str, int], dict[str, int]]:
    """Run all four claim checks. Returns (failures, counters, skipped_lines)."""
    notes = sorted(vault.rglob("*.md"))
    failures: list[str] = []
    checked = {"notes": len(notes), "modules": 0, "classes": 0, "imports": 0,
              "owners": 0, "py_literals": 0}
    skipped = {"fenced/counterexample lines": 0, "historical .py literals": 0}
    heading_owner: dict[str, list[str]] = {}
    fm_owner: dict[str, list[str]] = {}
    registry = registry_owners(vault)
    ast_cache: dict[str, set[str]] = {}

    for note in notes:
        text = note.read_text(encoding="utf-8")
        rel = note.name
        claims = prose_lines(text)
        skipped["fenced/counterexample lines"] += len(text.splitlines()) - len(claims)
        archived = is_archive(text)

        declared = sections(claims)
        modules = sorted({m for m, _, _ in declared if m})
        for module in modules:
            checked["modules"] += 1
            heading_owner.setdefault(module, []).append(rel)
            if module_path(pkg, module) is None:
                failures.append(f"{rel}: module {module} does not exist")

        fm = frontmatter_module(text)
        if fm:
            fm_owner.setdefault(fm, []).append(rel)

        # Claim 2: resolve against the module that owns the section, never the union.
        for module, lineno, line in declared:
            for name in CLASS_BULLET.findall(line):
                checked["classes"] += 1
                if module is None:
                    failures.append(f"{rel}:{lineno}: class {name} claimed outside any "
                                    f"module section — no owner to resolve it against")
                    continue
                if module not in ast_cache:
                    ast_cache[module] = classes_in(module_path(pkg, module))  # type: ignore[arg-type]
                if name not in ast_cache[module]:
                    failures.append(f"{rel}:{lineno}: class {name} is not defined in {module} "
                                    f"(this note's sections: {modules})")
            for raw in IMPORT.findall(line):
                checked["imports"] += 1
                try:
                    exec(compile(raw, "<note>", "exec"), {})  # noqa: S102
                except Exception as exc:  # noqa: BLE001 - report, never crash
                    failures.append(f"{rel}: import fails — {raw}  "
                                    f"({type(exc).__name__}: {exc})")

        # Claim 5: every `.py` literal in prose names a file that exists.
        for _module, lineno, line in declared:
            if MODULE_HEADING.match(line):
                continue  # claim 1 already covers the heading itself
            for raw in PY_LITERAL.findall(line):
                checked["py_literals"] += 1
                base = raw.rsplit("/", 1)[-1]
                if any((root / base).exists() for root in (vault.parent, pkg, pkg / "core")):
                    continue
                # One more place the real file may live: anywhere in the repo.
                found = any(p.name == base for p in vault.parent.rglob(base)
                            if ".venv" not in str(p) and "node_modules" not in str(p))
                if found:
                    continue
                if archived:
                    skipped["historical .py literals"] += 1
                    print(f"NOTE {rel}:{lineno}: `{raw}` no longer exists — archive note, "
                          f"claim about the past, not verified against the tree")
                else:
                    failures.append(f"{rel}:{lineno}: `{raw}` does not exist anywhere in the repo")

    # Claim 4: one owner per module, and the three ownership channels agree.
    for module, owners in sorted(heading_owner.items()):
        checked["owners"] += 1
        if len(owners) > 1:
            failures.append(f"{module}: claimed by {len(owners)} notes {sorted(set(owners))} — "
                            f"one module, one owner")
        reg = registry.get(module)
        # The registry stores a vault link target (a stem, no extension); the
        # owning note is a filename. Compare stems or every row looks like a
        # disagreement.
        if reg and len(set(owners)) == 1 and Path(owners[0]).stem != reg:
            failures.append(f"{module}: database-hub.md registry points at {reg} but the "
                            f"owning note is {owners[0]}")

    for module, owners in sorted(fm_owner.items()):
        if module not in heading_owner and module_path(pkg, module) is not None:
            failures.append(f"frontmatter `module: {module}` in {owners} but no note has a "
                            f"`## `{module}` heading — the field claims an owner that does not exist")

    return failures, checked, skipped


def main() -> int:
    notes = sorted(VAULT.rglob("*.md"))
    if not notes:
        print(f"no notes under {VAULT}")
        return 1

    failures, checked, skipped = check(VAULT, PKG)

    for f in failures:
        print(f"FAIL {f}")
    print("-" * 88)
    print(f"{checked['notes']} notes: {checked['modules']} modules, {checked['classes']} classes, "
          f"{checked['imports']} imports, {checked['owners']} owners, "
          f"{checked['py_literals']} .py literals verified")
    print(f"skipped {skipped['fenced/counterexample lines']} lines "
          f"(code fences + lines quoting a stale claim); "
          f"{skipped['historical .py literals']} historical .py literals in archive notes")

    # Negative control: an invented class and a broken import must be caught.
    ctl_ok = "AHPHelper" in classes_in(PKG / "core" / "ahp.py") and \
             "AHPHelper" not in classes_in(PKG / "core" / "topsis.py")
    try:
        exec("from decision_maker.core.ahp import AHPEngine", {})  # noqa: S102
        ctl_import_ok = False
    except ImportError:
        ctl_import_ok = True
    print(f"negative control (discriminates classes):  {'PASS' if ctl_ok else 'FAIL'}")
    print(f"negative control (catches bad import):     {'PASS' if ctl_import_ok else 'FAIL'}")

    ok = not failures and ctl_ok and ctl_import_ok
    print("RESULT:", "OK — every claim holds" if ok else "FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
