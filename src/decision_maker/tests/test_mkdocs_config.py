"""Tests for the MkDocs configuration, which was never buildable.

mkdocs.yml sat at the repo root unparsed by anything: not in CI, not in the test
extra, and not even valid YAML. Line 27 was `- 001: Rust Math Engine: adr/...`,
an unquoted colon inside a mapping value, so `mkdocs build` aborted in the
parser before it ever looked at the vault. Nothing noticed because nothing
invoked it.

These tests assert the config PARSES and that its nav resolves against
`docs_dir`, which is the two things that were wrong. They do not assert the
vault is publishable through MkDocs — it is not: the notes are an Obsidian
vault full of `[[wikilinks]]`, which MkDocs does not render without a plugin.

Run:  uv run pytest src/decision_maker/tests/test_mkdocs_config.py -v
"""
from __future__ import annotations

from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parents[3]
CONFIG = REPO / "mkdocs.yml"


@pytest.fixture(scope="module")
def config() -> dict:
    return yaml.safe_load(CONFIG.read_text(encoding="utf-8"))


def _nav_targets(nav: list) -> list[str]:
    """Every file path named anywhere in the nested nav structure."""
    out: list[str] = []
    for entry in nav:
        if isinstance(entry, str):
            out.append(entry)
        elif isinstance(entry, dict):
            out.extend(_nav_targets(list(entry.values())))
    return out


def test_mkdocs_yml_is_valid_yaml():
    """The defect: the config did not parse at all."""
    assert isinstance(yaml.safe_load(CONFIG.read_text(encoding="utf-8")), dict)


def test_nav_targets_all_exist_under_docs_dir(config):
    """The prior claim was that `index.md` did not resolve. It does."""
    docs_dir = REPO / config.get("docs_dir", "docs")
    for target in _nav_targets(config["nav"]):
        assert (docs_dir / target).is_file(), f"nav target missing: {docs_dir / target}"


def test_a_colon_in_a_nav_label_needs_quoting():
    """Negative control: the exact shape that broke line 27 must fail to parse.

    Without this, the parsing test above could pass for the wrong reason and
    nobody would learn whether it can actually detect the defect.
    """
    broken = "nav:\n  - 001: Rust Math Engine: adr/001.md\n"
    with pytest.raises(yaml.YAMLError):
        yaml.safe_load(broken)


def test_unquoted_colon_is_valid_once_quoted():
    """The same nav, fixed, parses and keeps the label intact."""
    fixed = yaml.safe_load('nav:\n  - "001: Rust Math Engine": adr/001.md\n')
    assert fixed["nav"][0] == {"001: Rust Math Engine": "adr/001.md"}
