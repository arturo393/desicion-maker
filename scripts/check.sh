#!/usr/bin/env bash
# Local CI: the checks that used to run on GitHub Actions, run on this machine instead.
# Usage: scripts/check.sh          full gate (~8 min): + smoke, coverage, Python 3.12
#        scripts/check.sh --fast   pre-push gate (~2 min): lock, lint, types, docs, tests
# Does NOT: build the Rust wheel separately (uv sync builds the extension through maturin) or publish anything.
set -euo pipefail
cd "$(dirname "$0")/.."

fast=false
[[ "${1:-}" == "--fast" ]] && fast=true

step() { printf '\n\033[1m==> %s\033[0m\n' "$1"; }

# --frozen fails when uv.lock no longer matches pyproject.toml: drift must break the gate, not resolve silently.
step "Install from the frozen lock";            uv sync --frozen --extra dev -q
step "Lint (ruff)";                             uv run ruff check .
step "Types (mypy)";                            uv run mypy
step "dev-agents linter";                       uv run python scripts/dev_agents_linter.py src/decision_maker/core
step "Docs: every link resolves";               uv run python scripts/check_docs_links.py > /dev/null
step "Docs: vault root holds no generated content"; uv run python scripts/check_docs_scope.py
step "Docs: notes match the source";            uv run python scripts/check_obsidian_fidelity.py > /dev/null
step "Docs: no cross-language drift";           uv run python scripts/check_obsidian_language.py > /dev/null
step "Tests";                                   uv run pytest --tb=short -q

if $fast; then
    printf '\n\033[32mFast gate passed.\033[0m Full gate: scripts/check.sh\n'
    exit 0
fi

step "Smoke: every analysis runs and the engine tells its options apart"
uv run pytest -m smoke --tb=short -q src/decision_maker/tests/test_analyses_smoke.py
step "Coverage gate (core >= 80%)"
uv run coverage run --source=src/decision_maker/core -m pytest --tb=short -q > /dev/null
uv run coverage report --fail-under=80 | tail -1
# The lower bound of requires-python is 3.11; 3.12 resolves newer numpy stubs. A 3.12-only mypy error
# reached main on 2026-10-19 because only 3.11 was checked locally.
step "Python 3.12: types and tests";            uv run --python 3.12 --isolated --extra dev mypy
uv run --python 3.12 --isolated --extra dev pytest --tb=short -q

printf '\n\033[32mFull gate passed.\033[0m\n'
