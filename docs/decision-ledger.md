---
aliases: [Decision Ledger, Ledger de decisiones, Decision Commitment]
tags: [module, lumina, quant, learning, process]
id: MOD-DECISION-LEDGER
title: "Ledger de decisiones"
type: module
category: learning
status: stable
module: "decision_maker.core.decision_commitment"
class: "DecisionCommitment"
related: ["[[unified-orchestrator]]", "[[decision-gates]]", "[[guide]]"]
created: 2026-10-18
updated: 2026-10-18
---

# Ledger de decisiones

## `decision_commitment.py`

> Las decisiones que una persona efectivamente tomó, cada una con fecha de revisión y una métrica que el mundo puede contestar.
>
> Uso: `decision-maker decide --option B --confidence 0.7 --metric "piloto operativo en faena" --review-by 2026-12-01`
>
> No: corre análisis ni crea compromisos por su cuenta; una corrida del orquestador sólo deja un borrador.

### Clases Principales

- **`DecisionCommitment`**: el ledger. Crea, cierra y consulta decisiones, y calcula su calibración.
- **`Commitment`**: una decisión tomada; los nombres de campo se conservan para leer archivos viejos.

### Por qué existe

Un sistema de decisión se mide por si acierta, y eso sólo lo dice la confianza declarada contra lo que pasó. Hasta el 18-Oct-2026 cada corrida escribía un compromiso en `results/` (ignorado por git): **1300 entradas, las 1300 con fecha «REVIEW NEEDED», 3 resultados registrados en total**. Los módulos de calibración estaban bien testeados y no tenían con qué trabajar.

### El ciclo

```
analyses/x.py ──run──▶ orquestador ──▶ commitment_draft (nada se escribe)
                                             │ una persona decide
                                             ▼
                       decision-maker decide ──▶ decisions/ledger.jsonl (versionado)
                                             │ llega review_date
                                             ▼
                       decision-maker review ──▶ close <id> --success|--failure
                                             ▼
                       decision-maker calibration ──▶ Brier, ECE, veredicto
```

### Qué rechaza `create`

| Entrada | Por qué |
|---|---|
| `review_date` que no es fecha ISO, o pasada | una revisión sin fecha nunca ocurre: así quedaron las 1300 |
| `success_metric` vacía | sin métrica no hay forma de cerrar la decisión |
| `success_metric` con `mean_score`, `p95`, `cvar`… | el modelo calificándose a sí mismo; era el valor por defecto viejo |
| `confidence` fuera de (0, 1] | es la probabilidad de que funcione, y es lo que se califica |

### Dónde vive y cómo lo leen otros

`decisions/ledger.jsonl`, relativo al directorio de trabajo, o `$DM_LEDGER_PATH`. Una línea JSON por decisión, con los campos de `Commitment`: cualquier otro repo o plataforma lo lee sin importar este paquete.

El contrato está publicado al lado de los datos: `decisions/ledger.schema.json` (JSON Schema 2020-12). Su test de conformidad lee al **productor** —los campos del dataclass y una línea que `create()` escribió de verdad—, no un ejemplo escrito a mano, así que un campo nuevo en el código sin su entrada en el esquema pone el test en rojo. Para integrar sin parsear texto: `decision-maker review --json` y `decision-maker calibration --json`, o por HTTP `GET /ledger?status=all|open|due|closed` y `GET /ledger/calibration` (sólo lectura; la API escucha en `127.0.0.1` porque no tiene autenticación). Se versiona a propósito, a diferencia de `results/`; si el repo deja de ser privado, `DM_LEDGER_PATH` lo mueve a otro lado (decisión registrada en el [[Tablero]]).

Los tests nunca escriben en el ledger real: `conftest.py` apunta `DM_LEDGER_PATH` a un directorio temporal.
