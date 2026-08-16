---
aliases: [Monte Carlo Engine]
tags: [module, component, mcelreath, causal-inference, dag]
---

# Monte Carlo Engine

## `monte_carlo.py` & `bootstrap.py`

> Motor de Generación Causal y Simulación Estocástica de Flujos (McElreath-Compliant).
> Genera distribuciones estocásticas mediante modelado generativo y penalización geométrica.

### 🕸️ Arquitectura Causal (Richard McElreath)
Este motor abandona el modelado directo de datos empíricos (curve-fitting) a favor del **Modelo Generativo**. Simulamos la mecánica subyacente que forzaría al sistema a transicionar entre estados.

#### 1. Grafo Acíclico Dirigido (DAG) y Bloqueo de Colisionadores
- **El Problema del Colisionador:** Si dos variables independientes tienen un efecto común, observar ese efecto crea una correlación espuria matemáticamente comprobable.
- **La Solución:** Las estructuras paramétricas alimentadas a este motor deben estar basadas en un DAG. El motor rechaza la falacia de sustitución perfecta (suma lineal) e implementa arquitecturas probabilísticas que evitan condicionar sobre *colliders* durante las simulaciones.

#### 2. Simulación de Priors Predictivos
Antes de realizar inferencia, el motor estocástico itera decenas de miles de trayectorias (Priors) usando estrictamente la configuración inicial (sin contaminación de datos posteriores). 
Si los priors arrojan estados físicamente imposibles (ej. probabilidades negativas, iliquidez no detectada), el algoritmo detecta la fractura en la topología causal antes de que cause daño.

#### 3. Adiós a la Falsa Aditividad Lineal
Los puntajes finales ya **no son una suma ponderada ciega**. Se aplica una **penalización geométrica dinámica** frente a colas extremas, impidiendo que el motor asuma que la ruina en un factor se puede compensar con el éxito en otro.

### Clases Principales
- **`MonteCarloEngine`**: Ejecuta las simulaciones respetando la correlación causal estructural (Matriz $\Sigma$) e impone bloqueos geométricos en colas negativas.
- **`BootstrapSimulator`**: Evalúa intervalos de confianza y significancia estadística sobre el generador de Monte Carlo.

---
