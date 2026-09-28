#!/usr/bin/env python3
"""Language ratchet for the docs/ vault. Enumerates notes by the language of their
body and flags words from the other one, so a slip is caught by a check that can
fail rather than by reading.

Usage:  uv run python scripts/check_obsidian_language.py
Exit 0 when clean, 1 when any note carries a foreign word.

What is enforced (note-schema.md, "Regla de Idioma"): a note carries no word
from the other language. What is NOT enforced: which language a note must be in.
The vault is deliberately mixed — 17 Spanish and 12 English among the 29 verified
— so the choice is the maintainer's and the checker only polices the intruders.

The `archive` tag is scoped out: 25 of 54 notes, including two of the most
linked. That count is pinned in test_docs_schema.py, so mistaking `archive` for
`deprecated` turns CI red instead of silently shrinking what is verified.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

VAULT = Path(__file__).resolve().parent.parent / "docs"

# Function words plus the inflections that actually show up in these notes.
ENGLISH = {
    "the", "and", "or", "of", "to", "in", "is", "are", "not", "does", "with",
    "for", "from", "that", "this", "which", "whose", "what", "when", "where",
    "how", "but", "all", "any", "each", "more", "most", "than", "then", "they",
    "their", "there", "these", "those", "has", "have", "had", "was", "were",
    "will", "would", "can", "could", "should", "must", "into", "over",
    "returns", "return", "takes", "take", "gives", "handles", "uses", "using",
    "converts", "computes", "calculates", "performs", "combines", "bundles",
    "without", "per", "via", "one", "two", "only", "also", "same",
}
SPANISH = {
    "el", "la", "los", "las", "un", "una", "unos", "unas", "de", "del", "al",
    "y", "o", "u", "que", "qué", "en", "con", "sin", "por", "para", "como",
    "pero", "más", "mas", "muy", "todo", "toda", "este", "esta", "esto",
    "ese", "esa", "es", "son", "ser", "está", "estan", "fue", "era", "se",
    "su", "sus", "lo", "ya", "sólo", "solo", "cada", "entre", "hasta",
    "desde", "donde", "cuál", "cual", "cuando", "aún", "aun", "también",
    "tambien", "así", "asi", "sobre", "bajo", "tras", "hace", "hay", "calcula", "devuelve", "toma", "usa", "convierte", "combina",
    "permite", "hacen", "están", "ningún", "ningun",
    "único", "unico", "además", "ademas", "mientras", "aunque",
}

# Split words but keep intra-word hyphens/underscores as one token.
WORD = re.compile(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]+(?:[-_][A-Za-zÁÉÍÓÚÜÑáéíóúüñ]+)*")
# Runs of word characters, Latin or not, used to spot a foreign script spliced
# *into* a Latin word. Greek is deliberately absent from FOREIGN_LETTER: σ and Σ
# are notation in two notes. A single foreign letter beside Latin is also notation
# (σa²), so the signal is a run of two or more.
MIXED_RUN = re.compile(r"[^\W\d_]+", re.UNICODE)
LATIN_LETTER = re.compile(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]")
FOREIGN_LETTER = r"[Ͱ-᳿가-힯Ѐ-ӿ　-鿿＀-￯]"
FOREIGN_RUN = re.compile(FOREIGN_LETTER + "{2,}")


def body_of(path: Path) -> str:
    """Note body with frontmatter, fenced code and inline code stripped."""
    text = path.read_text(encoding="utf-8")
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            text = text[end + 4 :]
    text = re.sub(r"```.*?```", " ", text, flags=re.S)   # fences
    text = re.sub(r"`[^`]*`", " ", text)                   # inline code
    text = re.sub(r"\[\[[^\]]*\]\]", " ", text)             # wikilink targets
    text = re.sub(r"https?://\S+", " ", text)               # URLs
    return text


def words_of(path: Path) -> list[str]:
    return [w.lower() for w in WORD.findall(body_of(path))]


def is_archive(path: Path) -> bool:
    """True when the note's own frontmatter declares it archive material.

    The language rule governs the notes someone maintains, not the record of what
    was decided in 2024. Scoping by tag rather than by path keeps the exclusion
    visible in the vault: a live note can be excluded from the rule, but only by
    saying so in its own frontmatter, where the next reader sees it.
    """
    head = path.read_text(encoding="utf-8")[:400]
    lines = head.splitlines()
    if not lines or lines[0].strip() != "---":
        return False
    for line in lines[1:]:          # skip the opening delimiter
        if line.strip() == "---":   # closing delimiter ends the frontmatter
            break
        if not line.startswith("tags:"):
            continue
        # Compare whole tags. A substring test would let `archive-2024-review`
        # exclude a live note by accident, and the exclusion is supposed to be a
        # decision the note states, not a coincidence in its spelling.
        body = line[len("tags:"):].strip()
        items = (
            [t.strip().strip("'\"") for t in body.splitlines()]
            if body.startswith("-")
            else [t.strip().strip("'\"") for t in re.split(r"[,\[\]]", body)]
        )
        return any(t == "archive" for t in items)
    return False


def non_latin(text: str) -> list[tuple[str, str]]:
    """Tokens that mix a foreign script into a Latin word.

    This is not a language rule, it is a corruption check, and it exists because
    the corruption happened: a note read "rankea opciones многlicriterio" — Cyrillic
    spliced into a Spanish word — and the worklog read "设计aba". Both were
    introduced while rewriting notes during the September reorganisation, and both
    are invisible to a word-list comparison, because the corrupted token simply is
    not in ENGLISH or SPANISH and so matches neither.

    Scoped twice, both times because a broad version reported correct notes. The
    first flagged any character outside Latin-1 and caught σ for standard deviation
    and Σ in `-Σ p ln p`; the second flagged any token mixing scripts and caught
    `σa²`, where the subscript `a` is Latin — which is how that notation is written.
    A single foreign character next to Latin has a notation reading; a sustained
    sequence of them inside a Latin word does not. So the rule is a run of TWO or
    more: it catches "многlicriterio" and "设计aba" and leaves σa² alone.

    The limit is deliberate and worth stating: a wholly foreign word standing alone
    in a Spanish note, or a single corrupted character, still passes.
    """
    out: dict[str, set[str]] = {}
    for run in MIXED_RUN.findall(text):
        if not LATIN_LETTER.search(run):
            continue
        spans = FOREIGN_RUN.findall(run)
        if spans:
            out.setdefault(run, set()).update(" / ".join(spans))
    return [(tok, "".join(sorted(chars))) for tok, chars in sorted(out.items())]


def main() -> int:
    every = sorted(p for p in VAULT.rglob("*.md") if p.is_file())
    if not every:
        print(f"no notes found under {VAULT}")
        return 1

    notes = [p for p in every if not is_archive(p)]
    skipped = [p for p in every if is_archive(p)]
    print(f"{'note':<34} {'lang':<9} {'en':>5} {'es':>5}  intruders")
    print("-" * 78)

    offenders: list[tuple[str, str, str]] = []
    corrupted: list[tuple[str, str, str]] = []
    for note in notes:
        tokens = words_of(note)
        en = [t for t in tokens if t in ENGLISH]
        es = [t for t in tokens if t in SPANISH]
        lang = "english" if len(en) >= len(es) else "spanish"
        foreign = sorted(set(es if lang == "english" else en))
        if foreign:
            for w in foreign:
                offenders.append((note.name, lang, w))
        for token, chars in non_latin(note.read_text(encoding="utf-8")):
            corrupted.append((note.name, token, chars))
        flag = ", ".join(foreign[:6]) + ("..." if len(foreign) > 6 else "")
        print(f"{note.name:<34} {lang:<9} {len(en):>5} {len(es):>5}  {flag or '-'}")

    print("-" * 78)

    # A green that cannot go red is worse than no check: it manufactures
    # confidence. Classify a synthetic note built to be Spanish with exactly one
    # English intruder, and require that the same code path flags it. Anything
    # less would pass even if the comparison were inverted.
    def intruders_in(tokens: list[str]) -> list[str]:
        toks = [t.lower() for t in tokens]          # same normalisation as words_of
        en = [t for t in toks if t in ENGLISH]
        es = [t for t in toks if t in SPANISH]
        lang = "english" if len(en) >= len(es) else "spanish"
        return sorted(set(es if lang == "english" else en))

    # Spanish body carrying exactly one English intruder: it must be reported.
    with_intruder = "la decisión se toma con los datos del proyecto y el informe the " * 6
    # Pure English body: it must come back clean, or the comparison is inverted.
    pure_english = "the engine returns the value of the option and the rank " * 3
    probe_en = intruders_in(WORD.findall(with_intruder))
    probe_es = intruders_in(WORD.findall(pure_english))
    control_ok = "the" in probe_en and not probe_es
    print(
        f"negative control (flags an intruder in a synthetic note): "
        f"{'PASS' if control_ok else 'FAIL'}"
        + ("" if control_ok else f"  flagged={probe_en} clean={probe_es}")
    )
    print(f"scoped out as archive: {len(skipped)} note(s)")

    # Second control, for the corruption check. Two halves, because the first
    # version of this rule was too broad and had to be narrowed: it must catch the
    # substitution that actually shipped, and it must NOT catch the σ and Σ that
    # the fragility and Bayesian notes legitimately use as notation. A rule that
    # only has the first half would force those two notes to be corrupted.
    ctl_corrupt = non_latin("rankea opciones многlicriterio contra una solución")
    ctl_clean = non_latin("rankea opciones multicriterio contra una solución ideal")
    ctl_notation = non_latin("normalizado por σ y medido como -Σ p ln p, con σa²")
    corrupt_ok = bool(ctl_corrupt) and not ctl_clean and not ctl_notation
    print(
        f"negative control (flags a foreign script spliced into a word):  "
        f"{'PASS' if corrupt_ok else 'FAIL'}"
        + ("" if corrupt_ok else f"  spliced={ctl_corrupt} clean={ctl_clean} notation={ctl_notation}")
    )

    if corrupted:
        print(
            f"FAIL: {len(corrupted)} token(s) with a foreign script spliced into a word\n"
        )
        for name, token, chars in corrupted:
            detail = ", ".join(f"{ch!r} U+{ord(ch):04X}" for ch in chars)
            print(
                f"  {name}: {token!r} contains {detail} — the corrupted token matches "
                f"neither ENGLISH nor SPANISH, so the word check above cannot see it"
            )
        return 1

    if offenders:
        print(f"FAIL: {len(offenders)} foreign word(s)\n")
        for name, lang, word in offenders:
            print(f"  {name}: {word!r} in a {lang} note")
        return 1

    if not corrupt_ok:
        return 1

    print(f"OK: {len(notes)} notes, no foreign words, no spliced scripts")
    return 0


if __name__ == "__main__":
    sys.exit(main())
