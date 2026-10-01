"""Shared fenced-code parser for the docs checkers (check_docs_links, check_obsidian_fidelity).

Usage: `inside, unclosed = fence_mask(lines)`; a non-None `unclosed` is the 1-based line of a
fence that never closes, which the caller must report as a failure. Not a full CommonMark parser.

Why it exists: both checkers toggled a flag on every ``` / ~~~ line. An unclosed fence then
silenced every link and claim after it, and a ```` fence containing ``` inverted the parity —
both measured as rc=0 over a broken link. A closing fence must use the same character and be at
least as long as the opening one (CommonMark rule), and an unclosed fence is an error, not silence.
"""

from __future__ import annotations

import re

FENCE = re.compile(r"^\s{0,3}(`{3,}|~{3,})(.*)$")


def fence_mask(lines: list[str]) -> tuple[list[bool], int | None]:
    """(True for lines inside a fence or on a fence line, 1-based line of an unclosed opener)."""
    inside = [False] * len(lines)
    opener: tuple[str, int, int] | None = None  # (char, length, line number)
    for i, line in enumerate(lines):
        m = FENCE.match(line)
        if opener is None:
            if m:
                opener = (m.group(1)[0], len(m.group(1)), i + 1)
                inside[i] = True
            continue
        inside[i] = True
        char, length, _ = opener
        if m and m.group(1)[0] == char and len(m.group(1)) >= length and not m.group(2).strip():
            opener = None
    return inside, (opener[2] if opener else None)
