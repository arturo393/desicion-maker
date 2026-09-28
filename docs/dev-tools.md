---
aliases: [Dev Tools, Herramientas de Desarrollo, Tooling y QA, Dev-Tools]
tags: [tools, qa, scripts, lumina, infrastructure, archive]
id: TOOL-DEV
title: "Herramientas de Desarrollo, Linters y QA"
type: meta
category: infrastructure
status: active
related: ["[[database-hub]]", "[[decision-maker-moc]]", "[[note-schema]]", "[[index]]"]
created: 2026-09-28
updated: 2026-09-28
---

# 🛠️ Herramientas de Desarrollo, Linters y QA (`scripts/`)

Este documento indexa y detalla las herramientas de automatización, validadores de fidelidad y scripts de aseguramiento de calidad del repositorio ubicados en `scripts/` y entornos de migración.

Hub general de base de datos: [[database-hub]] | Esquema canónico de notas: [[note-schema]].

---

## 🔬 1. Validadores del Vault de Obsidian y Documentación

| Script | Propósito y Función | Regla de Fallo |
|:---|:---|:---|
| `scripts/check_docs_links.py` | Validador exhaustivo de enlaces en Markdown (wikilinks y enlaces relativos) para todo el vault y archivos externos. | Falla si existe un enlace roto o apuntador inexistente. |
| `scripts/check_obsidian_language.py` | Ratchet lingüístico. Enumera cada nota por el idioma de su cuerpo y marca palabras del otro. | Falla si una nota lleva un token del idioma contrario. **No** impone qué idioma debe tener la nota: el vault es mixto a propósito. Fuera de notas con tag `archive` (25 de 54, número fijado en `test_docs_schema.py`). |
| `scripts/check_obsidian_fidelity.py` | Verificador de fidelidad contra el árbol real de `src/decision_maker/`. Resuelve 5 clases de afirmación: (1) cada heading `## \`modulo.py\`` existe; (2) cada bullet `**\`Clase\`**` es una clase real **del módulo dueño de su sección**; (3) cada `from decision_maker… import X` resuelve en runtime; (4) cada módulo tiene **un solo dueño** y los tres canales de propiedad —heading, frontmatter `module:`, fila de [[database-hub]]— concuerdan; (5) cada literal `.py` en prosa existe. | Falla si una afirmación no se sostiene contra el código. Clases e imports van por AST y por import real: dos instrumentos, para que uno tape el punto ciego del otro. Un literal `.py` en nota `archive` no falla: se cuenta y se imprime, porque una nota histórica que se lee como inventario vigente es su propia mentira. |

---

## 🏗️ 2. Automatización y Gestión de Tareas

| Script / Módulo | Propósito y Función | Integración |
|:---|:---|:---|
| `scripts/jira_manager.py` | Cliente automatizado para la API REST v3 de Jira Cloud. Permite sincronización de tareas de refactorización como [DM-25](../jira/DM-25.md). | Jira Cloud Atlassian REST API |
| `scripts/dev_agents_linter.py` | Linter AST que verifica las convenciones de código de la Dev-Agents Foundation (límite de parámetros, modelos Pydantic). | Calidad de código Python |
| `alembic/` / `alembic.ini` | Motor de migraciones y evolución de esquema relacional SQLite documentado en [Alembic README](../alembic/README.md). | SQLAlchemy / SQLite |

---

## ⚡ 3. Ejecución de la Batería de QA

Para ejecutar las verificaciones locales antes de commit:

```bash
# Validar enlaces de documentación
uv run python scripts/check_docs_links.py

# Validar que la raíz del vault siga siendo docs/ y no haya contenido generado dentro
uv run python scripts/check_docs_scope.py

# Validar consistencia de idiomas
uv run python scripts/check_obsidian_language.py

# Validar fidelidad de las afirmaciones contra el código
uv run python scripts/check_obsidian_fidelity.py

# Ratchets del esquema: fijan los conteos que la prosa no enumera
uv run pytest src/decision_maker/tests/test_docs_schema.py src/decision_maker/tests/test_docs_fidelity.py

# Ejecutar suite de pruebas unitarias
uv run pytest
```
