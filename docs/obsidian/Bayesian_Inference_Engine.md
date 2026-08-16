---
aliases: [Bayesian Inference Engine]
tags: [module, component, jaynes, maxent, cox-theorem]
---

# Bayesian Inference Engine

## `bayesian.py`

> Motor de Inferencia Bayesiana Empírica sin Asunciones Gaussianas (Jaynes-Compliant).
> Provee actualización de probabilidades respetando los axiomas extendidos de la lógica estricta.

### 🧠 Fundamento Epistemológico (E.T. Jaynes)
Este módulo no trata a la probabilidad como una frecuencia física, sino como el grado de información o incertidumbre racional (**Teorema de Cox**). 

#### 1. Principio de Máxima Entropía (MaxEnt)
Antes de asimilar nueva evidencia empírica, el motor asume la distribución que maximiza la Entropía de Shannon ($H = -\sum p_i \ln p_i$).
- **No se inventa información:** A diferencia de sistemas ingenuos que asignan distribuciones normales o uniformes sin justificación, el motor *BayesianEngine* delega la incertidumbre estructural al muestreo empírico bruto (KDE o Muestreo Empírico de Monte Carlo) garantizando máxima ignorancia sobre dinámicas no observadas.

#### 2. Inferencia y Teorema de Cox
La actualización frente a nueva información evita los *multiplicadores ad-hoc*. Toda inyección de `evidence` funciona como un *Log-Likelihood Shift* paramétrico, garantizando que el razonamiento del algoritmo sea consistente e independiente de la secuencia u orden en que se adquieran los datos.

### Clases Principales
- **`CausalNode`**: Nodo de un Grafo Causal (DAG) para bloqueos estocásticos de correlación espuria (ver MC Engine).
- **`BayesianEngine`**: Orquestador principal que ejecuta la lógica de actualización empírica (KDE sampling) condicionado a la evidencia observable.

---
