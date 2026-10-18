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
updated: 2026-10-18
---

# 📦 Documentación histórica retirada

El 18-Oct-2026 se retiró del repositorio todo el material histórico que ya no describía el código: ocupaba espacio en el vault, aparecía en las búsquedas y nadie lo leía. **No se perdió**: está en git y se recupera con un comando.

```bash
git show 0aecd52:<ruta>            # ver un archivo
git checkout 0aecd52 -- <carpeta>  # traer una carpeta entera
```

| Qué era | Ruta en `0aecd52` | Por qué se retiró |
|---|---|---|
| Guías y READMEs de versiones previas (10 archivos: guía de carrera en minería, comparativas, el framework unificado original, portadas viejas) | `archive/legacy/` | Describían versiones anteriores a v3.0 |
| Prototipo web React + TypeScript con Gemini | `archive/stochastic-decision-architect/` | Prototipo abandonado; la interfaz web es Streamlit |
| Plan y análisis de la reorganización (8 notas) | `docs/reorganization/` | Plan de enero 2026, ya ejecutado o descartado |
| Bitácora de la reorganización de dic 2024 (3 notas) | `docs/session-logs/` | Anterior a git; su contenido vigente pasó a [[index]] |
| Resultado de una meta-decisión de prueba | `docs/tests-results/` | Corrida de prueba sin uso posterior |
| Seguimiento en Jira (`DM-25.md`) y su cliente | `jira/`, `scripts/jira_manager.py` | Jira suspendido desde el 01-Oct-2026; el seguimiento pasó al Sistema de Gestión I+D |
| Roadmap duplicado | `ROADMAP_v3.0.md` | Tercera copia de las mismas mejoras; queda [[roadmap]] |
| Dashboard React de demo | `dashboard/` | Plantilla de Vite con datos fijos; decidido por el dueño |

Las versiones reemplazadas de análisis no se borraron: están en `analyses/archive/`, listadas en [[decision-analyses]].
