#!/usr/bin/env python3
"""Ratchet for the vault's frontmatter vocabulary.

`note-schema.md` declares four tag axes and the field table, but it deliberately
does NOT enumerate the 58 tag values. An index of 58 values written in prose is
an index nobody maintains — when the schema was last reviewed it already named 44
values that did not exist.

So the schema states the RULES and this test pins the COUNTS. It goes red both
ways: when a value is added without deciding which axis it belongs to, and when
one is removed without updating the number. That second direction is the point —
a ratchet that only counts up is just a tripwire, not a contract.

Run:  uv run pytest src/decision_maker/tests/test_docs_schema.py -v
"""
from __future__ import annotations

import collections
import re
from pathlib import Path

import pytest

VAULT = Path(__file__).resolve().parents[3] / "docs"

# Measured 28-Sep-2026. Change these on purpose, never by accident.
EXPECTED_NOTES = 54
EXPECTED_TAGS = 58
EXPECTED_ARCHIVE = 25
EXPECTED_MODULE_NOTES = 21

REQUIRED_FIELDS = {
    "aliases", "tags", "id", "title", "type", "category", "status", "related", "updated",
}
OPTIONAL_FIELDS = {"created", "module", "class", "kanban-plugin"}
KNOWN_FIELDS = REQUIRED_FIELDS | OPTIONAL_FIELDS

# The 12 values the `type` field accepts, which are also the Tipo tag axis.
KNOWN_TYPES = {
    "module", "archive", "moc", "meta", "narrative", "adr", "architecture",
    "changelog", "worklog", "guide", "kanban", "roadmap",
}

FIELD_RE = re.compile(r"^([a-zA-Z_][\w-]*):\s*(.*)$")


def _frontmatter(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return ""
    return text.split("---", 2)[1]


def _notes() -> list[Path]:
    return sorted(VAULT.rglob("*.md"))


def _tags() -> set[str]:
    out: set[str] = set()
    for p in _notes():
        m = re.search(r"^tags:\s*\[(.*?)\]\s*$", _frontmatter(p), re.M)
        if m:
            out |= {t.strip().strip("'\" ") for t in m.group(1).split(",") if t.strip()}
    return out


def _archive_notes() -> list[Path]:
    out = []
    for p in _notes():
        m = re.search(r"^tags:\s*\[(.*?)\]\s*$", _frontmatter(p), re.M)
        if m and "archive" in {t.strip().strip("'\" ") for t in m.group(1).split(",")}:
            out.append(p)
    return out


class TestCountsArePinned:
    def test_note_count(self):
        assert len(_notes()) == EXPECTED_NOTES, (
            f"the vault has {len(_notes())} notes, the pinned count is {EXPECTED_NOTES}. "
            f"Update EXPECTED_NOTES in this test and the count in note-schema.md together."
        )

    def test_tag_vocabulary_size(self):
        tags = _tags()
        assert len(tags) == EXPECTED_TAGS, (
            f"{len(tags)} distinct tags, pinned at {EXPECTED_TAGS}. Diff: added="
            f"{sorted(tags)[:0] or sorted(tags - set())} — decide the axis before bumping."
        )

    def test_archive_scope(self):
        n = len(_archive_notes())
        assert n == EXPECTED_ARCHIVE, (
            f"{n} notes tagged archive, pinned at {EXPECTED_ARCHIVE}. This tag is excluded "
            f"from the language check, so drift here means silently unverified notes."
        )

    def test_module_note_count(self):
        mods = [p for p in _notes() if re.search(r"^type:\s*module\s*$", _frontmatter(p), re.M)]
        assert len(mods) == EXPECTED_MODULE_NOTES


class TestFieldVocabulary:
    def test_only_known_fields_are_used(self):
        unknown: dict[str, set[str]] = collections.defaultdict(set)
        for p in _notes():
            for line in _frontmatter(p).splitlines():
                m = FIELD_RE.match(line)
                if m and m.group(1) not in KNOWN_FIELDS:
                    unknown[m.group(1)].add(p.name)
        assert not unknown, f"undeclared frontmatter fields: {dict(unknown)}"

    def test_prose_field_count_matches_the_table(self):
        """The count of fields stated in the schema prose must equal the fields the
        table declares, and both must equal the fields the vault actually uses.

        Added because the prose said "12 campos en uso" while the table had 13 rows
        and the notes carried 13 distinct keys. Everything green: the existing test
        compared field *names* against the set, never the *count*, and the checker
        verified literals, not schema arithmetic. So a reader counting the table and
        a reader trusting the sentence got different documents, unreported.

        Goes red if a field is added, dropped, or miscounted in any direction.
        """
        prose = (VAULT / "note-schema.md").read_text(encoding="utf-8")
        m = re.search(r"hay \*\*(\d+) campos en uso\*\*", prose)
        assert m, "note-schema.md no longer states a field count; update this test"

        table = {
            match.group(1)
            for match in re.finditer(r"^\|\s*`([a-z-]+)`\s*\|", prose, re.M)
        }
        used: set[str] = set()
        for p in _notes():
            for line in _frontmatter(p).splitlines():
                m2 = FIELD_RE.match(line)
                if m2:
                    used.add(m2.group(1))

        assert int(m.group(1)) == len(KNOWN_FIELDS), (
            f"prose says {m.group(1)} fields, KNOWN_FIELDS declares {len(KNOWN_FIELDS)}"
        )
        assert table == KNOWN_FIELDS, (
            f"schema table declares {sorted(table)}, KNOWN_FIELDS has {sorted(KNOWN_FIELDS)}"
        )
        assert used == KNOWN_FIELDS, (
            f"notes use {sorted(used)}, KNOWN_FIELDS declares {sorted(KNOWN_FIELDS)}"
        )

    def test_required_fields_present_in_every_note(self):
        missing: dict[str, list[str]] = collections.defaultdict(list)
        for p in _notes():
            fm = _frontmatter(p)
            for field in REQUIRED_FIELDS:
                if not re.search(rf"^{field}:", fm, re.M):
                    missing[field].append(p.name)
        assert not missing, f"notes missing a required field: {dict(missing)}"

    def test_created_is_everywhere(self):
        """`created` is required by the schema, and this test held the line.

        It was red for 16 notes after the schema was written: the field was
        declared but absent, and the note said so instead of carrying an exception
        list. The dates were filled — 10 from the first commit of each file, 6 with
        the vault-entry date declared as such in the schema — and the test went
        green on its own. The docstring that used to claim it was "intentionally
        red" was itself a stale claim, which is the same defect this suite hunts.
        """
        missing = [p.name for p in _notes() if not re.search(r"^created:", _frontmatter(p), re.M)]
        assert missing == [], (
            f"{len(missing)} notes have no `created` date, which note-schema.md lists as "
            f"required. Either fill them in from git history or change the schema."
        )


class TestTypeVocabulary:
    def test_types_are_declared(self):
        bad = set()
        for p in _notes():
            m = re.search(r"^type:\s*[\"']?([\w-]+)[\"']?\s*$", _frontmatter(p), re.M)
            if m and m.group(1) not in KNOWN_TYPES:
                bad.add(m.group(1))
        assert not bad, f"`type` values the schema does not declare: {sorted(bad)}"


class TestSchemaMatchesReality:
    """The schema must not state a number the vault contradicts."""

    @pytest.fixture(scope="class")
    def schema(self) -> str:
        return (VAULT / "note-schema.md").read_text(encoding="utf-8")

    def test_schema_states_the_real_note_count(self, schema):
        assert f"los {EXPECTED_NOTES} archivos" in schema or \
               f"{EXPECTED_NOTES} de {EXPECTED_NOTES} notas" in schema or \
               f"las {EXPECTED_NOTES} notas" in schema, (
            "note-schema.md no states the current note count — the count it used to state (37) "
            "was wrong for months"
        )

    def test_schema_states_the_real_tag_count(self, schema):
        assert f"{EXPECTED_TAGS} valores" in schema, (
            "note-schema.md must state the tag vocabulary size it refuses to enumerate"
        )
