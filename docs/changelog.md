---
aliases: [Changelog, Historial de Cambios, Version History]
tags: [changelog, lumina, quant, archive]
id: DOC-CHANGELOG
title: "Historial de Cambios y Versiones"
type: changelog
category: project-management
status: active
related: ["[[index]]", "[[decision-maker-moc]]", "[[kanban]]", "[[adr/001-use-rust-for-math-engine]]"]
created: 2026-08-10
updated: 2026-09-27
---

# 📜 Historial de Cambios (Changelog)

Registro histórico de cambios del Decision Maker Framework dentro del vault de Obsidian. Archivo canónico en la raíz: [CHANGELOG.md](../CHANGELOG.md).

---

## [v3.1] - 2026-08-23

Rediseño arquitectónico cuantitativo e integración de componentes críticos:

### 🦀 Núcleo Rust y Normalización
- Extensión nativa `rust_core/` documentada en [[adr/001-use-rust-for-math-engine]].
- [[monte-carlo-engine]]: `normalize=True` usa límites globales idénticos entre Python y Rust.

### 🧠 Aprendizaje y Meta-Aprendizaje
- **Sistema de Aprendizaje**: `outcome_tracker`, `calibration`, `decision_journal`, `adaptive_router`.
- **Meta-Aprendizaje**: `action_threshold`, `reasoning_trace`, `unknown_scanner`, `meta_calibration`.

### 🚦 Compuertas de Decisión y Control de Ruina
- Veto por ergodicidad, probabilidad de ruina estocástica, validación de DAG causal y compromiso de decisión.
- Ergodicity Analyzer y Kelly Criterion para dimensionamiento estocástico.

### 🗄️ Base de Datos y Gobernanza
- [[database-hub]]: Centro unificado de base de datos relacional en Obsidian.
- [[kanban]]: Tablero Kanban interactivo para control del proyecto.
- [[note-schema]]: Esquema canónico y reglas de integridad.
