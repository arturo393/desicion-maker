---
aliases: [Bayesian Inference Engine, Bayesian_Inference_Engine]
tags: [module, lumina, quant, stochastic, bayesian, jaynes]
id: MOD-BAYESIAN
title: "Bayesian Inference Engine"
type: module
category: stochastic
status: stable
module: "decision_maker.core.bayesian"
class: "BayesianEngine"
related: ["[[monte-carlo-engine]]", "[[unified-orchestrator]]"]
created: 2026-08-10
updated: 2026-09-27
---

## `bayesian.py`

> Calcula P(esta opción es la óptima) remuestreando las distribuciones de puntaje y contando quién gana.
> Uso: `from decision_maker.core.bayesian import BayesianEngine`
> No: construir una red bayesiana completa ni calibrar desde datos históricos.

### El método

`analyze(mc_results, evidence, num_posterior_samples=10000, seed=42)` no calcula una densidad — **empieza el resultado con un argmax repetido**:

```
repetir num_posterior_samples veces:
    para cada opción: sortear un puntaje
    sumar el shift de evidence si hay
    contar quién quedó arriba
posterior = victorias / num_posterior_samples
```

Es un estimador de Monte Carlo de P(gana), no un álgebra de Bayes. Con `seed=42` por defecto es reproducible. Casos borde: sin resultados devuelve `{}`; con una sola opción devuelve `1.0` para ella.

### El sortea: empírico primero, gaussiano como red de seguridad

```
if s.raw_scores is not None and len(s.raw_scores) > 0:
    score = rng.choice(s.raw_scores)          # remuestreo empírico
else:
    score = rng.normal(s.mean_score, s.std_dev)   # fallback gaussiano
```

La ruta primaria **no asume ninguna forma de distribución** — remuestrea los puntajes crudos que dejó [[monte-carlo-engine]], así que las colas pesadas se propagan en vez de aplanarse.

> La versión anterior titulaba esto "sin asunciones Gaussianas" y describía un Principio de Máxima Entropía de Jaynes. **No hay MaxEnt en el módulo**: `bayesian.py` son 75 líneas y no calcula entropía ni `-Σ p ln p`. Y la asunción gaussiana sí está, sólo que como red de seguridad: se activa cuando `raw_scores` es `None`. La afirmación correcta es "empírico por defecto, gaussiano si no hay datos crudos" — que es una garantía distinta y más débil.

### El shift de evidencia

```
score += evidence[names[i]] * max(s.std_dev, 1e-12)
```

La evidencia entra como un desplazamiento de verosimilitud escalado por la desviación de la propia opción. Es monótona y proporcional, no un multiplicador ad-hoc: por eso el orden de adquisición de los datos no cambia el resultado.

### `CausalNode` es un stub

`bayesian.py:17-21` define `CausalNode` con `name`, `parents` y `probabilities = {}` — con el comentario del propio código: `# CPTs would go here in a real implementation`. **No hay lógica de inferencia**: sin independencia condicional, sin bloqueo de colisionadores, sin nada.

Lo único que hace el motor con los nodos es puramente decorativo: si se registró algún nodo, adjunta al resultado un `_causal_graph` con el mapa de padres. Es metadato de salida, no cómputo.

> Existe un **segundo** `CausalNode` en `causal_dag.py:21`, que sí tiene `edges`, `validate_acyclic` y docstring. Es el que usa el orquestador. El nombre está duplicado en el paquete y esta nota no debería señalar el stub como si fuera la infraestructura causal.

### Clases Principales

- **`BayesianEngine`**: Estimador de P(óptima) por remuestreo. `add_node()` registra estructura causal que luego sólo se refleja en la salida.
- **`CausalNode`**: Pares `name`/`parents`. **Placeholder** — sin tablas de probabilidad condicional.
