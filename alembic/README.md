---
aliases: [Alembic Migrations, Migraciones de Base de Datos, Database Migrations]
tags: [alembic, database, migrations, lumina, infrastructure, archive]
id: DB-MIGRATIONS
title: "Alembic Database Migrations"
type: meta
category: infrastructure
status: active
related: ["[[database-hub]]", "[[reporting-and-registry]]", "[[data-models-and-schemas]]"]
created: 2026-08-10
updated: 2026-09-28
---

# 🗄️ Alembic Database Migrations

Este directorio contiene las migraciones del esquema relacional SQLite gestionadas por **Alembic** para el almacenamiento estructurado del framework cuantitativo.

Hub general de base de datos: [[database-hub]] | Esquemas de datos: [[data-models-and-schemas]] | Registro persistente: [[reporting-and-registry]].

---

## 📋 Historial de Versiones (`alembic/versions/`)

| Revisión | Archivo | Descripción del Cambio de Esquema |
|:---|:---|:---|
| `6fe4a5425df6` | `6fe4a5425df6_initial_schema.py` | Esquema relacional inicial: tablas de ejecuciones, alternativas, factores y métricas estocásticas. |
| `8906f4fcd17b` | `8906f4fcd17b_add_predicted_winner_and_confidence_to_.py` | Incorporación de campos `predicted_winner` y `confidence_interval` a la tabla de decisiones. |
| `c17e9e99571b` | `c17e9e99571b_add_outcome_record_table.py` | Creación de la tabla `outcome_records` para tracking y calibración posterior de compromisos. |

---

## ⚙️ Uso y Comandos

```bash
# Aplicar migraciones pendientes
uv run alembic upgrade head

# Generar una nueva migración automática
uv run alembic revision --autogenerate -m "descripcion_del_cambio"

# Revertir la última migración
uv run alembic downgrade -1
```
Configuración global en `alembic.ini`.
