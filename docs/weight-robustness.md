---
aliases: [Weight Robustness, Robustez ante los pesos, SMAA]
tags: [module, lumina, quant, mcda, robustness]
id: MOD-WEIGHT-ROBUSTNESS
title: "Robustez ante los pesos"
type: module
category: mcda
status: stable
module: "decision_maker.core.weight_robustness"
class: "WeightRobustness"
related: ["[[monte-carlo-engine]]", "[[sensitivity-analysis]]", "[[unified-orchestrator]]"]
created: 2026-10-18
updated: 2026-10-18
---

# Robustez ante los pesos

## `weight_robustness.py`

> Probabilidad de que cada opción gane cuando los pesos también son inciertos, no sólo los puntajes.
>
> Uso: `weight_robustness(mc_results, factors, concentration=20, seed=1)`; o la clave `weight_robustness` del resultado en modo `standard`.
>
> No: deriva pesos a partir de juicios ([[ahp]], `swing_weights`), ni mide riesgo de cola (`cvar_95` del [[monte-carlo-engine]]).

### Clases Principales

- **`WeightRobustness`**: resultado inmutable con el ganador declarado, las dos lecturas, la matriz de aceptabilidad por rango, los pesos centrales de cada opción y el veredicto.

### Qué pregunta contesta

Todos los demás motores ordenan con **un** vector de pesos, escrito a mano. La pregunta real es otra: si otra persona, igual de razonable, pesara distinto, ¿seguiría ganando la misma opción? Cada sorteo del Monte Carlo se empareja con su propio sorteo de pesos, así que un solo número lleva las dos incertidumbres.

La idea es el índice de aceptabilidad de rango de SMAA (Lahdelma y Salminen); la implementación y el informe en dos lecturas son de este framework.

| Lectura | Pesos | Se lee como |
|---|---|---|
| `informed` | Dirichlet(`concentration` × pesos declarados) | «si mis pesos están más o menos bien» |
| `uninformed` | Dirichlet(1, …, 1), uniforme en el símplex | «si no supiera nada de los pesos» |

Una opción que gana la lectura sin información no necesita la discusión de pesos.

### Parámetros y umbrales

- `concentration = 20`: con Dirichlet(k·w) un peso w tiene desvío √(w(1−w)/(k+1)); con k = 20 un 0,30 declarado queda en ±0,10, el desacuerdo típico entre dos personas que pesan el mismo criterio.
- Veredicto sobre la aceptabilidad informada del ganador declarado: `robust` desde 0,75, `fragile` bajo 0,5, `contested` entre medio.
- Con dos opciones el veredicto nunca es `fragile`: si la media de la Beta queda del lado ganador, la mediana también. Hace falta una tercera opción que compita (`test_fragile_when_a_specialist_edges_out_a_balanced_option`).

### Cómo se validó

- Contra una forma cerrada: con A=(1,0) y B=(0,1), A gana sii w₁ > ½, y P(A primero) es la cola de una Beta(0,7k; 0,3k). El test compara con `scipy.stats.beta.sf` para k = 2, 10 y 50.
- Propiedades: opción dominante gana siempre; la matriz de aceptabilidad es doblemente estocástica; con k → ∞ reproduce los pesos declarados; con semilla, idéntico.
- Control negativo: fijar la concentración en 20 dentro del módulo pone rojos cuatro tests.
