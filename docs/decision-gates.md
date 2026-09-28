---
aliases: [Decision Gates, Veto Gates]
tags: [module, lumina, quant, infrastructure, governance, taleb]
id: MOD-GATES
title: "Decision Gates Engine"
type: module
category: infrastructure
status: stable
module: "decision_maker.core.decision_gates"
class: "DecisionGate"
related: ["[[unified-orchestrator]]", "[[ergodicity-analyzer]]", "[[antifragile-engine]]"]
created: 2026-08-10
updated: 2026-09-27
---

# Decision Gates Engine

## `decision_gates.py`

> Enforces strict veto barriers that disqualify options violating catastrophic risk constraints.
>
> Usage: `from decision_maker.core.decision_gates import DecisionGate`
> Does NOT: compute compensatory criteria weights.

### Clases Principales

- **`GateVerdict`**: Enumeration of verification verdicts designating whether an alternative passes, warns, or encounters an absolute veto.
- **`GateResult`**: Output recording the gate identifier, veto state, and explanatory diagnostic rationale.
- **`DecisionGate`**: Evaluates non-negotiable threshold filters including ruin probability limits, non-ergodicity flags, and causal DAG consistency checks.
