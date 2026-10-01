"""
Smoke tests for the two FSK analyses: they run end to end and the MC winner agrees with the weighted sum.
Run: uv run pytest src/decision_maker/tests/test_fsk_analyses.py -v
Does NOT: check the judgements themselves (they are the author's scores, not measurements).

Why: v1 of both crashed at import (`CareerOption(pros=...)`) and nothing noticed for three months.
"""

from __future__ import annotations

import asyncio
import importlib.util
import json
from pathlib import Path

import pytest

ANALYSES = Path(__file__).resolve().parents[1] / "analyses"


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, ANALYSES / f"{name}.py")
    assert spec is not None
    assert spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.mark.parametrize("name", ["fsk_protocol_evaluation", "fsk_scanner_integration"])
def test_fsk_analysis_runs_and_agrees_with_weighted_sum(name, tmp_path, monkeypatch):
    mod = _load(name)
    monkeypatch.setattr(mod, "REPO", tmp_path)  # results/ goes to tmp, not the repo
    asyncio.run(mod.main())
    (out,) = (tmp_path / "results" / name).glob("eval_*.json")
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["recommended"] == data["recommended_by_weighted_sum"]
    assert set(data["results"]) == {a["name"] for a in mod.ALTERNATIVES}
