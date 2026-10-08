"""
Test-ratchet for Engine Maturity declarations.

Verifies:
1. Every engine in ENGINE_UNIVERSE has a declared maturity entry.
2. Every evidence path declared in ENGINE_MATURITY exists on disk.
3. No engine declared as 'validated' lacks supporting evidence.
4. Correct dispatch of maturity levels by mode and engine name.
"""

from __future__ import annotations

from pathlib import Path

from decision_maker.core.adaptive_router import ENGINE_UNIVERSE
from decision_maker.core.engine_maturity import (
    ENGINE_MATURITY,
    resolve_engine_maturity,
    resolve_run_engine_maturity,
)

REPO_ROOT = Path(__file__).resolve().parents[3]


class TestEngineMaturityRatchet:
    def test_every_engine_in_universe_has_maturity_entry(self) -> None:
        """Every engine in ENGINE_UNIVERSE must have an entry in ENGINE_MATURITY."""
        declared_engines = set(ENGINE_MATURITY.keys())
        universe_engines = set(ENGINE_UNIVERSE)

        missing = universe_engines - declared_engines
        extra = declared_engines - universe_engines

        assert not missing, f"Engines in ENGINE_UNIVERSE missing from ENGINE_MATURITY: {sorted(missing)}"
        assert not extra, f"Engines in ENGINE_MATURITY not in ENGINE_UNIVERSE: {sorted(extra)}"

    def test_all_declared_evidence_paths_exist(self) -> None:
        """Every evidence path declared in ENGINE_MATURITY must exist on disk."""
        missing_paths: list[str] = []
        for engine, entry in ENGINE_MATURITY.items():
            for path_str in entry["evidence"]:
                full_path = REPO_ROOT / path_str
                if not full_path.exists():
                    missing_paths.append(f"{engine} -> {path_str}")

        assert not missing_paths, (
            f"Evidence paths declared in ENGINE_MATURITY that do not exist: {missing_paths}"
        )

    def test_no_validated_engine_without_evidence(self) -> None:
        """No engine may be marked 'validated' without at least one evidence path."""
        unbacked_validated: list[str] = []
        for engine, entry in ENGINE_MATURITY.items():
            if entry["level"] == "validated" and not entry["evidence"]:
                unbacked_validated.append(engine)

        assert not unbacked_validated, (
            f"Engines marked 'validated' without evidence paths: {unbacked_validated}"
        )

    def test_expected_maturity_levels_for_benchmarked_engines(self) -> None:
        """MonteCarlo and PROMETHEE are validated, TOPSIS is characterized."""
        assert resolve_engine_maturity("MonteCarlo") == "validated"
        assert resolve_engine_maturity("PROMETHEE") == "validated"
        assert resolve_engine_maturity("TOPSIS") == "characterized"
        assert resolve_engine_maturity("GameTheory") == "experimental"

    def test_resolve_run_engine_maturity_by_mode(self) -> None:
        """resolve_run_engine_maturity maps active engines to their maturity levels."""
        express_maturity = resolve_run_engine_maturity("express")
        assert "MonteCarlo" in express_maturity
        assert express_maturity["MonteCarlo"] == "validated"
        assert "TOPSIS" in express_maturity
        assert express_maturity["TOPSIS"] == "characterized"
        assert "DecisionTheory" in express_maturity
        assert express_maturity["DecisionTheory"] == "experimental"
