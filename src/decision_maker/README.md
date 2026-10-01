---
aliases: [Python Decision Framework, Package Readme]
tags: [package, lumina, quant, infrastructure]
id: DOC-PKG-README
title: "Python Decision Framework Package Readme"
type: narrative
category: infrastructure
status: active
related: ["[[docs/index|index]]", "[[docs/database-hub|database-hub]]", "[[docs/decision-analyses|decision-analyses]]"]
created: 2026-01-03
updated: 2026-10-01
---

# Paquete `decision_maker`

El paquete Python del framework: `core/` (motores y orquestador), `analyses/` (casos de decisión), `api/` (FastAPI), `dashboard/` (Streamlit), `cli.py` (comando `decision-maker`), `scripts/` (utilitarios) y `tests/`.

Instalación, uso y arquitectura están en un solo lugar, no acá:

- [README.md](../../README.md) — quick start, motores, modos y requisitos.
- [docs/index.md](../../docs/index.md) — portal de la documentación.

Esta nota fue un README propio del paquete y quedó desactualizado entero (`requirements.txt`, imports `python.core`, conteo de tests, herramientas de formato que el repo ya no usa, enlaces rotos). Se decidió reducirla a un puntero porque ningún checker la cubre —`check_docs_links.py` revisa sólo `docs/`— y una segunda copia de la documentación sin control vuelve a derivar. Si el paquete se publicara por separado y necesitara su propio README, esa es la señal para reescribirlo.
