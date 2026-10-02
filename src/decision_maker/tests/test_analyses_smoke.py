"""
Smoke test: every analysis in analyses/ runs offline, and the Monte Carlo engine told its options apart.
Run: uv run pytest -m smoke src/decision_maker/tests/test_analyses_smoke.py   (~70 s, 8 in parallel)
Does NOT: judge whether a model is right; reach an LLM (DM_LLM_BACKEND=api, no key); run by default.

Why: five analyses compared 0.0 against 0.0 for months and exited 0; FSK crashed at import for three;
none of it was seen until an audit ran them by hand (2026-10-01). New files are picked up by the glob,
so an analysis cannot be added without being run. Scripts that write next to the repo write to
results/, which git ignores; everything that honours the cwd writes to a temp dir.

The check reads the engine's own trace (DM_MC_TRACE, one line per MonteCarloEngine.run), not the
script's output: the first version checked the JSON reports, and its negative control — the old
silent engine put back — stayed green, because the five broken analyses write no report at all.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest

pytestmark = pytest.mark.smoke

REPO = Path(__file__).resolve().parents[3]
ANALYSES = REPO / "src" / "decision_maker" / "analyses"
SCRIPTS = sorted(p for p in ANALYSES.glob("*.py") if p.name != "_template.py")
TIMEOUT_S = 900
WORKERS = 8

# Analyses that never call the framework's Monte Carlo engine. Measured 2026-10-02. Exact both ways:
# a listed script that starts calling the engine fails too. BLIND SPOT: for these the smoke test only
# proves they run — whether their own TOPSIS/MC tells the options apart is not checked here.
OWN_TOPSIS = "own numpy TOPSIS, not the framework engine"
OWN_MC = "own numpy Monte Carlo + TOPSIS, not the framework engine"
NO_ENGINE: dict[str, str] = {
    "becker_hardware_decision": OWN_TOPSIS,
    "mineria_integration": OWN_TOPSIS,
    "spectrum_analyzer_selection": OWN_TOPSIS,
    "plc_bridge_comparativa": OWN_TOPSIS,
    "commandmessage_refactor_decision": OWN_MC,
    "commandmessage_refactor_llm_20260823": OWN_MC,
    "decision_concon": "closed-form scoring, no engine",
    "decision_vina_vs_concon": "closed-form scoring, no engine",
    "decision_patmos_calculator": "calculator, no ranking",
    "power_supply_research": "report generator, no engine",
    "refactoring_commandmessage": "prints a hand-written analysis, no engine",
}

# Analyses that MUST fail offline, and the text that says why. Failing loudly is the contract here:
# before 2026-10-02 these wrote "Error: ..." into a results file and exited 0.
EXPECTED_FAILURE: dict[str, str] = {
    "power_supply_deep_research_simple": "consultas fallaron",
    "power_supply_gemini_deep_research": "consultas fallaron",
    "power_supply_utility_research": "consultas fallaron",
    "process_research_results": "No existe",
    "process_utility_analysis": "No existe",
}


def _run(script: Path, tmp: Path) -> tuple[Path, subprocess.CompletedProcess[str]]:
    cwd = tmp / script.stem
    cwd.mkdir()
    env = {k: v for k, v in os.environ.items() if k != "GEMINI_API_KEY"}
    env |= {
        "DM_LLM_BACKEND": "api",
        "MPLBACKEND": "Agg",
        "POWER_SUPPLY_OUTPUT_DIR": str(cwd / "ps_out"),
        "DM_MC_TRACE": str(cwd / "mc_trace.jsonl"),
    }
    proc = subprocess.run(
        [sys.executable, str(script)], cwd=cwd, env=env, capture_output=True, text=True,
        timeout=TIMEOUT_S, stdin=subprocess.DEVNULL, check=False,
    )
    return cwd, proc


@pytest.fixture(scope="module")
def runs(tmp_path_factory) -> dict[str, tuple[Path, subprocess.CompletedProcess[str]]]:
    tmp = tmp_path_factory.mktemp("analyses")
    with ThreadPoolExecutor(WORKERS) as pool:
        done = list(pool.map(lambda s: _run(s, tmp), SCRIPTS))
    return {s.stem: r for s, r in zip(SCRIPTS, done, strict=True)}


def test_expected_failures_still_exist() -> None:
    """A stale entry would silently exempt nothing; a renamed script would silently stop failing loudly."""
    assert set(EXPECTED_FAILURE) <= {s.stem for s in SCRIPTS}


@pytest.mark.parametrize("name", [s.stem for s in SCRIPTS])
def test_analysis_runs(name: str, runs) -> None:
    _, proc = runs[name]
    out = proc.stdout + proc.stderr
    assert "Traceback" not in out, f"{name} crashed:\n{out[-2000:]}"
    if name in EXPECTED_FAILURE:
        assert proc.returncode != 0, f"{name} must fail without an LLM/data, and exited 0:\n{out[-1500:]}"
        assert EXPECTED_FAILURE[name] in out, f"{name} failed without saying why:\n{out[-1500:]}"
    else:
        assert proc.returncode == 0, f"{name} exited {proc.returncode}:\n{out[-2000:]}"


def _trace(cwd: Path) -> list[dict[str, float]]:
    path = cwd / "mc_trace.jsonl"
    if not path.exists():
        return []
    return [json.loads(line)["means"] for line in path.read_text(encoding="utf-8").splitlines() if line]


def test_no_engine_entries_still_exist() -> None:
    assert set(NO_ENGINE) <= {s.stem for s in SCRIPTS}


@pytest.mark.parametrize("name", [s.stem for s in SCRIPTS if s.stem not in EXPECTED_FAILURE])
def test_engine_ran_and_told_the_options_apart(name: str, runs) -> None:
    cwd, _ = runs[name]
    calls = _trace(cwd)
    if name in NO_ENGINE:
        assert not calls, f"{name} is listed as NO_ENGINE ({NO_ENGINE[name]}) but ran the engine {len(calls)} time(s)"
        return
    assert calls, f"{name} exited 0 without running the Monte Carlo engine once"
    for i, means in enumerate(calls):
        # An empty run is the defect itself: the legacy shim registered no option at all.
        assert means, f"{name}: engine run #{i} scored no option"
        if len(means) >= 2:
            spread = max(means.values()) - min(means.values())
            assert spread > 1e-9, f"{name}: engine run #{i} scored every option {next(iter(means.values()))}"


@pytest.mark.parametrize("name", [s.stem for s in SCRIPTS if s.stem not in EXPECTED_FAILURE])
def test_written_results_rank_the_options(name: str, runs) -> None:
    """Every framework report it wrote has >= 2 options whose mean scores are not all equal."""
    cwd, _ = runs[name]
    for report in cwd.rglob("analysis_*.json"):
        mc = json.loads(report.read_text(encoding="utf-8")).get("monte_carlo", {})
        means = [s["mean"] for s in mc.values() if isinstance(s, dict) and "mean" in s]
        assert len(means) >= 2, f"{report.name}: {len(means)} option(s) scored"
        assert max(means) - min(means) > 1e-9, f"{report.name}: every option scored {means[0]}"
