---
aliases: [ADR 001]
tags: [adr, lumina, architecture]
id: ADR-001
title: "Use Rust for Math Engine"
type: adr
category: architecture
status: active
related: ["[[architecture]]", "[[monte-carlo-engine]]", "[[unified-orchestrator]]"]
created: 2026-08-10
updated: 2026-09-27
---

# ADR 001: Use Rust for Math Engine

## Status
Accepted

## Context
The decision framework relies heavily on Monte Carlo simulations and advanced mathematical models (TOPSIS, Genetic Algorithms). Running millions of iterations in pure Python introduces significant performance bottlenecks, particularly due to the Global Interpreter Lock (GIL) preventing true multithreading.

## Decision
We will extract the computationally intensive algorithms into a Rust crate (`rust_core`), compiled as a native Python extension using `PyO3` and `Maturin`. We will utilize `rayon` for fearless, zero-cost concurrency. Python will remain the orchestration, API, and UI layer.

## Consequences
- **Positive:** Massive speedup in simulations. True multithreading capabilities. Memory safety guarantees.
- **Negative:** Introduces a new language (Rust) and build toolchain (Cargo/Maturin) to the project dependencies.

## Addendum 2026-09-27: what actually shipped

The crate exists, builds, and is exercised by `tests/test_rust_engine.py`. **It is not on the framework's execution path.**

`grep -rln decision_maker_core src/ --include=*.py` returns three files: the extension's own
`src/decision_maker_core/__init__.py` and two test modules. **No module under
`src/decision_maker/core/` imports it.** `MonteCarloEngine` runs pure Python/NumPy
(`monte_carlo.py:101` logs `"Running {n} Monte Carlo simulations in Python…"`). The
"massive speedup" consequence above is therefore unrealised in the framework today.

**The normalization is duplicated, not shared.** `monte_carlo.py:141-148` and `lib.rs:180-196`
each implement the global min/max → `[0,1]` rule. The two agree on that formula — the Python
comment cites the Rust phase it mirrors — so no test has caught the drift. They have since
diverged on the statistic that follows it:

| | Python (`monte_carlo.py`) | Rust (`lib.rs`) |
|---|---|---|
| `success_rate` | `mean(total_scores > cross_option_mean)` (`:186`) | `count(total_scores > 0.0) / n` (`:207`) |
| Ruin penalty | percentile-5 multiplicative penalty (`:169-174`) | absent |

`score > 0.0` is the definition Python *replaced* — its own comment at `:181-184` explains that
with scores normalised to `[0,1]` it is always true. The Rust side still computes it. If the
extension is ever wired in, the two paths return different `success_rate` for the same input,
and every consumer of that number inherits the difference.

`ndarray` is declared in `rust_core/Cargo.toml` but never appears in `lib.rs`; all tensors there
are `Vec<f64>`.

### Decision

Keep the crate. The ADR is not reverted — the fallback-free path is the one that works today and
it needs no build step. The duplication is accepted **only** while the extension is unreachable,
because an unreachable second implementation cannot produce a wrong answer.

This changes when the extension is wired into `MonteCarloEngine.run()`: the `success_rate`
divergence must be resolved first, in the direction of the cross-option mean. Until then, a
test that asserts the two implementations agree is what would have caught this — the current
`test_engine_runs_without_rust_module` cannot, because it monkeypatches a module `monte_carlo.py`
never imports.

