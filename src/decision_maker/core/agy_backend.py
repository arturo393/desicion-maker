"""
LLM backend that answers prompts through the Antigravity CLI (`agy -p`) instead of a Gemini API key.
Usage: from decision_maker.core.agy_backend import ask_agy, llm_backend; text = ask_agy("prompt")
Does NOT: let agy edit files (runs in plan mode, sandboxed, in a throwaway directory) or swallow failures.

Why it exists: the Gemini analyses needed `google-generativeai` plus `GEMINI_API_KEY`, and neither is in
the venv, so they could not run. `agy` is already logged in on the workstation. The backend is chosen
by `DM_LLM_BACKEND`: `auto` (default — the API if there is a key and an SDK, otherwise agy), `api`, `agy`.
"""

from __future__ import annotations

__all__ = ["AgyError", "agy_available", "ask_agy", "llm_backend"]

import os
import shutil
import subprocess
import tempfile

AGY_BIN = "agy"
# A research prompt took 10-25 s on 2026-10-01; deep research can take minutes.
AGY_TIMEOUT_S = 600
BACKENDS = ("auto", "api", "agy")


class AgyError(RuntimeError):
    """agy is missing, timed out, exited non-zero or answered nothing."""


def agy_available() -> bool:
    return shutil.which(os.getenv("AGY_BIN", AGY_BIN)) is not None


def llm_backend(api_ready: bool) -> str:
    """Resolve DM_LLM_BACKEND to `api`, `agy` or `none`. An unknown value is an error, not a default."""
    choice = os.getenv("DM_LLM_BACKEND", "auto").strip().lower()
    if choice not in BACKENDS:
        raise ValueError(f"DM_LLM_BACKEND={choice!r}; expected one of {BACKENDS}")
    if choice == "api":
        return "api" if api_ready else "none"
    if choice == "agy":
        return "agy" if agy_available() else "none"
    if api_ready:
        return "api"
    return "agy" if agy_available() else "none"


def ask_agy(prompt: str, model: str | None = None, timeout_s: float = AGY_TIMEOUT_S) -> str:
    """Return agy's answer to `prompt`. Raises AgyError on any failure — never returns an error string."""
    binary = shutil.which(os.getenv("AGY_BIN", AGY_BIN))
    if binary is None:
        raise AgyError(f"'{AGY_BIN}' not found on PATH")
    cmd = [binary, "-p", prompt, "--mode", "plan", "--sandbox", "--print-timeout", f"{int(timeout_s)}s"]
    model = model or os.getenv("AGY_MODEL")
    if model:
        cmd += ["--model", model]
    # A throwaway cwd: agy is an agent, and the repo is not its workspace.
    with tempfile.TemporaryDirectory(prefix="dm-agy-") as workdir:
        try:
            proc = subprocess.run(
                cmd, cwd=workdir, capture_output=True, text=True, timeout=timeout_s + 30, check=False
            )
        except subprocess.TimeoutExpired as exc:
            raise AgyError(f"agy did not answer within {timeout_s:.0f} s") from exc
    if proc.returncode != 0:
        detail = (proc.stderr or proc.stdout).strip().splitlines()
        raise AgyError(f"agy exited {proc.returncode}: {detail[0] if detail else 'no output'}")
    answer = proc.stdout.strip()
    if not answer:
        raise AgyError("agy exited 0 with an empty answer")
    return answer
