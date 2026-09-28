---
aliases: [Legacy Documentation, Archivo Legacy, Documentos Históricos]
tags: [archive, lumina, quant, legacy]
id: DOC-LEGACY-HUB
title: "Catálogo de Documentación Histórica y Legacy"
type: moc
category: legacy
status: archive
related: ["[[database-hub]]", "[[decision-maker-moc]]", "[[index]]"]
created: 2025-12-01
updated: 2026-09-27
---

# 🏛️ Catálogo de Documentación Histórica y Legacy

Este documento centraliza e indexa los documentos y especificaciones históricas que residen fuera de la carpeta `docs/`, principalmente en `archive/legacy/` y prototipos anteriores. Permite acceder a todo el material técnico original directamente desde Obsidian sin que quede documentación dispersa.

Hub general de base de datos: [[database-hub]].

---

## 📚 1. Guías y Casos de Estudio en `archive/legacy/`

| ID | Documento Fuente | Tema / Eje | Descripción | Enlace al Archivo |
|:---|:---|:---|:---|:---|
| `ARCH-MINING-GUIDE` | `MINING_CAREER_GUIDE.md` | `carrera / minería` | Guía completa de análisis de carrera en minería con Gemini Deep Research y 13 metodologías cuantitativas | [Ver Guía](../archive/legacy/MINING_CAREER_GUIDE.md) |
| `ARCH-ENHANCED-COMP` | `ENHANCED_COMPARISON.md` | `trading / negocios` | Comparativa estocástica entre simulación básica vs 10 factores (alertas de trading, arbitraje cripto, SaaS) | [Ver Comparativa](../archive/legacy/ENHANCED_COMPARISON.md) |
| `ARCH-SUPER-POWERED` | `README_SUPER_POWERED.md` | `algoritmos / mcda` | Especificación de algoritmos cuantitativos (AHP, PROMETHEE, TOPSIS) con ejemplos de evaluación | [Ver Documento](../archive/legacy/README_SUPER_POWERED.md) |
| `ARCH-UNIFIED-FRAMEWORK` | `README_UNIFIED_FRAMEWORK.md` | `arquitectura` | Diseño original del framework unificado de decisiones estocásticas y multicriterio | [Ver Framework](../archive/legacy/README_UNIFIED_FRAMEWORK.md) |
| `ARCH-INTEG-SYSTEM` | `INTEGRATED_SYSTEM_README.md` | `integración` | Arquitectura del sistema integrado y acoplamiento de modelos matemáticos | [Ver Sistema](../archive/legacy/INTEGRATED_SYSTEM_README.md) |
| `ARCH-SYSTEM-COMPLETION` | `SYSTEM_COMPLETION_SUMMARY.md` | `calidad / métricas` | Resumen de completitud, cobertura de pruebas y verificación de seguridad de llaves | [Ver Resumen](../archive/legacy/SYSTEM_COMPLETION_SUMMARY.md) |
| `ARCH-INTEG-SUMMARY` | `INTEGRATION_SUMMARY.md` | `integración` | Resumen técnico de la primera fase de integración de motores | [Ver Resumen](../archive/legacy/INTEGRATION_SUMMARY.md) |
| `ARCH-LEGACY-INDEX` | `INDEX.md` | `índice histórico` | Índice temático original de la versión previa del repositorio | [Ver Índice](../archive/legacy/INDEX.md) |
| `ARCH-LEGACY-OLD` | `README_OLD.md` | `portada histórica` | Portada original del proyecto antes de la migración a v3.0 | [Ver Readme](../archive/legacy/README_OLD.md) |
| `ARCH-LEGACY-BACKUP` | `README.backup.md` | `backup` | Copia de respaldo previa a la refactorización modular | [Ver Backup](../archive/legacy/README.backup.md) |

---

## 💻 2. Prototipos Web y Herramientas Anteriores

| ID | Componente | Directorio | Descripción | Enlace |
|:---|:---|:---|:---|:---|
| `ARCH-STOCHASTIC-ARCH` | Stochastic Decision Architect | `archive/stochastic-decision-architect/` | Prototipo frontend en React + TypeScript con integración directa a Gemini | [Ver Readme](../archive/stochastic-decision-architect/README.md) |
| `COMP-DASHBOARD` | Dashboard Vite / React | `dashboard/` | Frontend web moderno para visualización de decisiones | [Ver Readme](../dashboard/README.md) |

---

## 🎯 3. Relación con el Framework Actual (v3.1)

Todos los algoritmos y casos de estos documentos fueron formalizados y absorbidos en la arquitectura moderna:
- Los análisis de carrera y trading inspiraron los scripts en `src/decision_maker/analyses/` catalogados en [[decision-analyses]].
- Los algoritmos AHP, TOPSIS y PROMETHEE se convirtieron en los motores formales [[ahp]], [[topsis]], [[promethee]], [[pareto-frontier]] y [[monte-carlo-engine]].
- El prototipo web inspiró el dashboard Streamlit oficial (`src/decision_maker/dashboard/app.py`) y la API REST FastAPI (`src/decision_maker/api/server.py`).
