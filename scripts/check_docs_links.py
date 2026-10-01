#!/usr/bin/env python3
"""Link-graph check for docs/. Resolves every wikilink and every relative markdown
link against the filesystem, so "0 broken" means "nothing to fix" rather than
"the instrument could not see".

Usage:  uv run python scripts/check_docs_links.py
Exit 0 when every live link resolves, 1 otherwise.

Resolution is case-sensitive first, with a case-insensitive retry reported
separately as BROKEN(case) — the difference matters on Linux and on GitHub, where
`architecture.md` does not open `ARCHITECTURE.md`.

Link-shaped strings inside fenced code are reported as INERT, not broken: they
are proposed content, not links. A fence that never closes is a failure, because
it would otherwise silence every link after it.

Checked: [[wikilinks]], [text](path), ![image](path) and [ref]: path definitions.
NOT checked: #anchors (the part after `#` is dropped), <a href> in HTML, http(s) URLs.
An exemption in KNOWN_BROKEN that no longer matches anything is a failure too, so
the table cannot outlive the breakage it documents.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import unquote

sys.path.insert(0, str(Path(__file__).resolve().parent))  # loadable by path, not only as `python scripts/x.py`
from _fences import fence_mask  # noqa: E402

REPO = Path(__file__).resolve().parent.parent
DOCS = REPO / "docs"
VAULT = DOCS

WIKILINK = re.compile(r"\[\[([^\[\]]+?)\]\]")
MDLINK = re.compile(r"!?\[([^\]\[]*)\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
REFDEF = re.compile(r"^\s{0,3}\[([^\]]+)\]:\s*(\S+)\s*$")
INLINE_CODE = re.compile(r"`[^`]*`")

# Pre-existing breakage that is not ours to fix silently. Keyed by file AND by
# the exact link target, never by file alone: an exemption scoped to the file
# would mask every dead link added to it afterwards, which is the opposite of
# what this table is for. A new link in one of these files still goes red.
KNOWN_BROKEN: dict[str, dict[str, str]] = {
    "docs/reorganization/deliverables.md": {
        t: "proposed documentation tree from a plan that was never executed; "
           "the targets do not exist anywhere, so rewriting the paths fixes nothing"
        for t in (
            "./ANALISIS_REORGANIZACION_FINAL.md", "./README_REORGANIZATION.md",
            "./REORGANIZATION_COMPLETE.md", "./REORGANIZATION_PLAN.md",
            "./REORGANIZATION_SUMMARY.md", "./docs/CREAR_NUEVO_SCRIPT.md",
            "./docs/QUICK_START.md",
        )
    } | {
        # NOT the same case as the ones above, and it used to be filed with them:
        # this is a directory that never existed, not a doc from the phantom tree.
        "./python/scripts/": "proposed script directory from the same unexecuted plan; "
                            "the path does not exist on disk either way",
    },
    "docs/reorganization/plan.md": {
        "./REORGANIZATION_PLAN.md#ejecución":
            "plan/proposal document; the link-shaped string is proposed content"
    },
}


def frontmatter_aliases(text: str) -> list[str]:
    """Alias entries from the YAML frontmatter, in either YAML form.

    Reads the frontmatter BLOCK, not the first N characters of the file. Three
    things were wrong with the previous version and none of them was firing yet,
    which is the part worth remembering:

      - a `[:400]` window truncated 9 of the 54 frontmatters, which are up to 453
        chars. `aliases:` is the first field so nothing was lost *today*; one
        reordering away, it would have been.
      - the window continued into the body, so an `aliases:` line in prose or in a
        fenced template registered a phantom alias. note-schema.md carries exactly
        that line inside its ```markdown skeleton.
      - the block-list form (`aliases:` then `  - Name`) parsed as zero aliases.
        No note uses it yet; a note that adopts it would lose every alias.

    A phantom alias is not harmless: it makes a broken link resolve, which is the
    one thing this checker exists to prevent.
    """
    if not text.startswith("---"):
        return []
    parts = text.split("---", 2)
    if len(parts) < 3:
        return []
    fm = parts[1]

    out: list[str] = []
    in_block = False
    for line in fm.splitlines():
        if re.match(r"^aliases:\s*$", line):
            in_block = True
            continue
        if in_block:
            item = re.match(r"^\s*-\s+(.*)$", line)
            if item:
                out.append(item.group(1).strip().strip("'\""))
                continue
            if line.strip():  # block ended
                in_block = False
        m = re.match(r"^aliases:\s*(.*)$", line)
        if m:
            out += [p.strip().strip("'\"") for p in re.split(r"[,\[\]]", m.group(1))]
    return [a for a in out if a]


def aliases() -> dict[str, Path]:
    """Every `aliases:` entry in the vault, mapped to its note.

    Keyed three ways so the table can see every form Obsidian accepts: the bare
    stem, the vault-relative path, and the path with `.md`. Nested notes need the
    path forms because `[[a/b]]` is a legal link and `b` alone is not the same
    target once two folders hold a note of that name.
    """
    table: dict[str, Path] = {}
    for note in sorted(VAULT.rglob("*.md")):
        rel = note.relative_to(VAULT).with_suffix("")
        for key in (note.stem, rel.as_posix()):
            table.setdefault(key, note)
        for part in frontmatter_aliases(note.read_text(encoding="utf-8")):
            table.setdefault(part, note)
    return table


def resolve_wiki(target: str, alias_table: dict[str, Path]) -> tuple[str, Path | None]:
    clean = re.split(r"[|#^]", target, maxsplit=1)[0].strip()
    if clean in alias_table:
        return "alias", alias_table[clean]
    for name, path in alias_table.items():          # case-insensitive retry
        if name.lower() == clean.lower():
            return "BROKEN(case)", path
    return "DANGLING", None


def main() -> int:
    notes = sorted(p for p in DOCS.rglob("*.md"))
    if not notes:
        print("no notes under docs/")
        return 1

    alias_table = aliases()
    rows: list[tuple[str, str, str]] = []
    live_broken = 0
    unclosed: list[str] = []
    used_exemptions: set[tuple[str, str]] = set()

    for note in notes:
        raw_lines = note.read_text(encoding="utf-8").splitlines()
        fenced, open_line = fence_mask(raw_lines)
        rel = str(note.relative_to(REPO))
        if open_line is not None:
            unclosed.append(f"{rel}:{open_line}")
        exempt = KNOWN_BROKEN.get(rel, {})

        for n, line in enumerate(raw_lines, start=1):
            where = f"{rel}:{n}"
            # A wikilink inside `backticks` renders as code, not as a link.
            line = INLINE_CODE.sub(" ", line)

            for m in WIKILINK.finditer(line):
                kind, path = resolve_wiki(m.group(1), alias_table)
                target_name = m.group(1).split("|")[0].split("#")[0].strip()
                target = f"[[{target_name}]]"
                known = target in exempt
                if known:
                    used_exemptions.add((rel, target))
                if kind in {"alias", "BROKEN(case)"} and path is not None:
                    rows.append((where, m.group(0), f"RESOLVED {kind} -> {path.name}", known))
                else:
                    rows.append((where, m.group(0), "DANGLING", known))
                if fenced[n - 1]:
                    rows[-1] = (where, m.group(0), "INERT (in a code fence)", known)
                if kind in {"DANGLING", "BROKEN(case)"} and not fenced[n - 1] and not known:
                    live_broken += 1

            md_targets = [(m.group(0), m.group(2)) for m in MDLINK.finditer(line)]
            ref = REFDEF.match(line)
            if ref:
                md_targets.append((ref.group(0).strip(), ref.group(2)))
            for text, raw in md_targets:
                if raw.startswith(("http:", "https:", "mailto:", "//")):
                    continue
                path_part = unquote(raw.split("#")[0].split("?")[0])
                if not path_part:
                    continue                      # pure #anchor: not checked, see the docstring
                target = (note.parent / path_part).resolve()
                known = raw in exempt
                if known:
                    used_exemptions.add((rel, raw))
                if not target.is_relative_to(REPO):
                    rows.append((where, text, "BROKEN(escapes repo)", known))
                    if not fenced[n - 1] and not known:
                        live_broken += 1
                elif target.exists():
                    rows.append((where, text, f"RESOLVED -> {target.relative_to(REPO)}", known))
                else:
                    verdict = "BROKEN"
                    if target.with_name(target.name.lower()).exists() or \
                       target.with_name(target.name.upper()).exists():
                        verdict = "BROKEN(case)"
                    rows.append((where, text, verdict, known))
                    if fenced[n - 1]:
                        rows[-1] = (where, text, "INERT (in a code fence)", known)
                    if not fenced[n - 1] and not known:
                        live_broken += 1

    for where, text, verdict, known in rows:
        mark = "  " if verdict.startswith("RESOLVED") else ("~~" if known else "!!")
        note_txt = " (known)" if known and not verdict.startswith("RESOLVED") else ""
        print(f"{mark} {where:<44} {text[:44]:<46} {verdict}{note_txt}")

    live_rows = [r for r in rows if not r[2].startswith("INERT")]
    ok = sum(1 for r in live_rows if r[2].startswith("RESOLVED"))
    known_bad = sum(1 for r in live_rows if r[3] and not r[2].startswith("RESOLVED"))
    inert = [r for r in rows if r[2].startswith("INERT")]
    print("-" * 108)
    print(f"{len(live_rows)} live links: {ok} resolved, {len(live_rows) - ok} not resolved "
          f"({known_bad} documented as pre-existing, {live_broken} NEW)")
    if inert:
        print(f"{len(inert)} INERT: link-shaped strings inside fenced code. Not links and not "
              f"failures, but nobody validates them either — when an example becomes a real "
              f"link, nothing here notices:")
        for where, text, _, _ in inert:
            print(f"   ~ {where:<43} {text[:44]}")
    for rel, why in KNOWN_BROKEN.items():
        print(f"  known: {rel} — {why}")

    # Negative control: a target that cannot exist must be reported DANGLING.
    kind, _ = resolve_wiki("Esta_Nota_No_Existe_XYZ", alias_table)
    control = kind == "DANGLING"
    print(f"negative control (fake wikilink detected): {'PASS' if control else 'FAIL'}")

    for where in unclosed:
        print(f"!! {where}: code fence opened here never closes")
    stale = [(f, t) for f, ts in KNOWN_BROKEN.items() for t in ts if (f, t) not in used_exemptions]
    for f, t in stale:
        print(f"!! {f}: KNOWN_BROKEN exemption {t!r} no longer matches any link — remove it")

    return 0 if live_broken == 0 and control and not unclosed and not stale else 1


if __name__ == "__main__":
    sys.exit(main())
