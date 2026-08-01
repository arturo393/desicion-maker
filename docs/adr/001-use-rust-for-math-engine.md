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
