#!/usr/bin/env python3
"""Tests for the countable claims the docs make about the repo.

Every other doc check verifies that a claim about the CODE is true. These verify
that a claim about a COUNT is true, because the two fail differently: a `.py`
literal goes stale when the code moves, but a total like "521 tests" goes stale
by nobody touching anything — the number only has to be wrong by one.

Four of the five claims below were wrong when this file was written:

* `architecture.md` and `index.md` said 495 tests. There were 521.
* `decision-analyses.md` said 36 scripts while its own table listed 37 rows.
* `results-catalog.md` said the repository holds 295 files in `results/`. That
  directory is in `.gitignore` with zero tracked files, so the number was
  unreproducible for anyone but the machine that wrote it. Fixed by not
  counting, and `test_results_stays_unversioned` below makes the count
  structurally impossible to reintroduce.
* `AGENTS.md` demanded Python 3.12+ while `pyproject.toml` declared `>=3.11`
  and CI's lowest matrix cell is 3.11.

The engine count is now DERIVED, not compared. It used to be the opposite: three
notes said 24, `adaptive_router.py`'s own docstring said 24, and the three route
lists summed to 19 — the notes agreed with each other and all three were wrong,
which is exactly what a test that only compares copies of a number cannot see.
`ENGINE_UNIVERSE` and `ROUTES` in `core/adaptive_router.py` are now the single
source, and the tests read the number off them.

Run:  uv run pytest src/decision_maker/tests/test_docs_claims.py -v
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

from decision_maker.core.adaptive_router import ENGINE_UNIVERSE, ROUTES

REPO = Path(__file__).resolve().parents[3]
DOCS = REPO / "docs"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _claims_test_count(request: pytest.FixtureRequest) -> bool:
    """True when this run collected the whole suite, so its total is comparable.

    `session.items` is already filtered by `-k`, `-m` and any path argument, so a
    subset run would report a smaller number and the ratchet would go red for a
    reason that has nothing to do with the docs. Skip instead, and say why.

    Read through `getattr`: the option names differ between pytest versions and a
    missing one raised AttributeError here, which made the guard crash instead of
    skipping — the opposite of what it was written to do.
    """
    opts = request.config.option
    return not any(
        getattr(opts, name, None)
        for name in ("keyword", "markexpr", "lf", "last_failed", "file_or_dir", "deselect", "ignore")
    )


@pytest.mark.usefixtures("request")
def test_documented_test_count_matches_the_suite(request: pytest.FixtureRequest) -> None:
    """architecture.md and index.md must state the number that actually runs."""
    if not _claims_test_count(request):
        pytest.skip("subset run: `session.items` is filtered, so the total is not comparable")

    actual = len(request.session.items)
    for name in ("architecture.md", "index.md"):
        text = _read(DOCS / name)
        numbers = {int(n) for n in re.findall(r"(\d{3,})\s+tests", text)}
        assert numbers == {actual}, (
            f"{name} claims {sorted(numbers)} tests but the suite collects {actual}. "
            f"Add the test and update the number in the same commit."
        )


def test_every_analysis_file_is_in_the_table() -> None:
    """No orphan script in analyses/, and no row pointing at a file that is gone.

    Scoped to the `ANA-` rows on purpose. An earlier version matched every
    `` `something.py` `` in the file and reported ten phantoms, all of them real
    files in `examples/` that the doc also documents — a false alarm that would
    have taught everyone to ignore this test.
    """
    text = _read(DOCS / "decision-analyses.md")
    rows = re.findall(r"^\| `ANA-[^`]*`\s*\|\s*`([^`]+\.py)`", text, re.MULTILINE)
    on_disk = {p.name for p in (REPO / "src" / "decision_maker" / "analyses").glob("*.py")}

    assert len(rows) == len(on_disk), (
        f"the table lists {len(rows)} analyses but analyses/ holds {len(on_disk)} files"
    )
    assert not (set(rows) - on_disk), f"the table lists files that do not exist: {sorted(set(rows) - on_disk)}"
    assert not (on_disk - set(rows)), f"analyses/ has files the table omits: {sorted(on_disk - set(rows))}"


def test_prose_analysis_count_excludes_the_template() -> None:
    """The prose says 37; the directory holds 38 because `_template.py` is not an analysis."""
    text = _read(DOCS / "decision-analyses.md")
    prose = re.search(r"los (\d+) an[aá]lisis de decisi[oó]n cuantitativa", text)
    assert prose, "decision-analyses.md no longer states the analysis count in the expected form"

    on_disk = {p.name for p in (REPO / "src" / "decision_maker" / "analyses").glob("*.py")}
    assert "_template.py" in on_disk, "the template moved; this test's premise needs revisiting"

    claimed = int(prose.group(1))
    assert claimed == len(on_disk) - 1, (
        f"prose claims {claimed} analyses but analyses/ holds {len(on_disk)} files, "
        f"one of which is the template. Either the count or the directory is wrong."
    )


def test_results_stays_unversioned() -> None:
    """`results/` is generated output. If it ever gets versioned, counting it becomes possible.

    The claim it blocks was "el repositorio registra 295 archivos en results/".
    That was unverifiable because the directory is ignored, so every clone other
    than the author's had a different number. This test fails if the situation
    changes, which is the signal to revisit results-catalog.md on purpose rather
    than let it rot.
    """
    gitignore = _read(REPO / ".gitignore")
    assert re.search(r"^results/?$", gitignore, re.MULTILINE), (
        "results/ is no longer in .gitignore. If it is now versioned, results-catalog.md "
        "can state a real file count again — and should."
    )

    # Belt and braces: no note may claim a count of files in an unversioned directory.
    #
    # Two explicit relations, not a distance window. A ±60-character window was the
    # first attempt and it was wrong twice: it flagged a sentence reading "los 54
    # archivos `.md` son todos documentación ... y no hay `results/`", which counts
    # the vault and mentions results/ in a negation, and tuning the window until
    # that passes is how an instrument gets taught to look the other way.
    #
    #   1. results/ is followed closely by a count  -> "results/ (17 archivos)"
    #   2. a count is bound to results/ by en/de    -> "295 archivos en `results/`"
    #
    # "y no hay `results/`" matches neither, which is the point.
    #
    # Paths are relative to the repo root, not basenames: the first version of this
    # printed `improvement-analysis.md:84` for a file that actually lives in
    # docs/reorganization/, which is the same basename collision that made two
    # instruments disagree about the inbound links to database-hub.
    count = r"\d{2,}\s+(?:archivos|artefactos|reportes)"
    relations = (
        re.compile(rf"results/[^\n]{{0,30}}?\(?\s*{count}", re.IGNORECASE),
        re.compile(rf"{count}\s+(?:en|de)\s+`?results/`?", re.IGNORECASE),
    )
    offenders: list[str] = []
    for p in sorted(DOCS.rglob("*.md")):
        for i, line in enumerate(_read(p).splitlines(), 1):
            if any(pat.search(line) for pat in relations):
                offenders.append(f"{p.relative_to(REPO)}:{i}")
    assert not offenders, (
        f"these notes state a file count in results/, which is gitignored and therefore "
        f"unreproducible: {offenders}"
    )


def test_routes_cover_exactly_the_engine_universe() -> None:
    """Every routed engine is declared, and every declared engine is routed somewhere.

    This is the invariant that makes the doc's number derivable. It was added with
    `ENGINE_UNIVERSE`, and it fails in both directions: an engine in a route that
    nobody declared, and a declared engine that no route ever reaches.
    """
    routed = {name for recommended, skipped in ROUTES.values() for name in (*recommended, *skipped)}
    declared = set(ENGINE_UNIVERSE)

    assert len(ENGINE_UNIVERSE) == len(declared), "ENGINE_UNIVERSE repeats an engine name"
    assert not routed - declared, f"routed but never declared: {sorted(routed - declared)}"
    assert not declared - routed, f"declared but no route ever reaches it: {sorted(declared - routed)}"


def test_documented_engine_count_is_the_derived_one() -> None:
    """The notes must state the number the code produces, not a remembered one.

    The old version of this test compared the three notes to each other, which
    proved they agreed and nothing else: they all said 24 while the routes summed
    to 19, and the docstring said 24 too. Comparing copies of a number cannot
    detect the number being wrong — only reading it off the source can.
    """
    expected = len(ENGINE_UNIVERSE)
    for name in ("architecture.md", "roadmap.md", "kanban.md"):
        # "N motores" a secas tambien matchea prosa sobre una cantidad parcial ("faltan
        # tres motores"), asi que se exige la frase canonica del total.
        match = re.search(r"(\d+)\s+motores ruteables", _read(DOCS / name), re.IGNORECASE)
        assert match, f"{name} no longer states an engine count, or states it unreadably"
        assert int(match.group(1)) == expected, (
            f"{name} says {match.group(1)} engines, but ENGINE_UNIVERSE has {expected}. "
            f"Add the engine to core/adaptive_router.py first, then update the note."
        )


def test_every_engine_is_named_in_the_architecture_table() -> None:
    """The `### Engines` table must name every engine the router can dispatch to.

    Three routable engines were missing from it (GameTheory, ROA, MLSurrogate) for
    as long as it existed: the table was maintained by hand and the router by hand,
    and nothing compared them. Matching is on letters only, so `DecisionTheory`
    matches a row titled "Decision Theory".
    """
    text = _read(DOCS / "architecture.md")
    table = text[text.index("### Engines") :]
    end = table.find("\n## ", 1)
    if end != -1:
        table = table[:end]
    squashed = re.sub(r"[^a-z]", "", table.lower())

    for engine in ENGINE_UNIVERSE:
        assert re.sub(r"[^a-z]", "", engine.lower()) in squashed, (
            f"{engine} is routable but the ### Engines table never names it"
        )


def test_agents_python_floor_matches_pyproject() -> None:
    """AGENTS.md and pyproject.toml must state the same minimum.

    These are two answers to one question — what Python does this need — and they
    were 3.12+ and >=3.11. A reader who trusted the stricter one would reject a
    runtime that CI's lowest cell actively tests.
    """
    floor = re.search(r'requires-python\s*=\s*">=(\d+)\.(\d+)"', _read(REPO / "pyproject.toml"))
    assert floor, "could not read requires-python out of pyproject.toml"
    major, minor = floor.group(1), floor.group(2)

    agents = _read(REPO / "AGENTS.md")
    claimed = re.search(r"Python (\d+)\.(\d+)\+", agents)
    assert claimed, "AGENTS.md no longer states a Python floor in the expected form"

    assert (claimed.group(1), claimed.group(2)) == (major, minor), (
        f"AGENTS.md says Python {claimed.group(1)}.{claimed.group(2)}+ but pyproject.toml "
        f"declares >={major}.{minor}. One of them is lying about what the code needs."
    )
