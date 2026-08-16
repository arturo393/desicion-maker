---
aliases: [Antifragile Engine, Barbell Strategy]
tags: [module, component, taleb, ergodicity, convexity]
---

# Antifragile Engine

## `antifragile.py` & `robust.py`

> Escudo Estocástico contra el Extremistán (Taleb-Compliant).
> Cuantifica la asimetría de cola (convexidad) e identifica vulnerabilidades catastróficas.

### 🛡️ La Física de la Ruina y la Convexidad (Nassim N. Taleb)

El verdadero riesgo no es la volatilidad diaria, sino el Colapso por Falsa Ergodicidad. Este módulo es el auditor final del portafolio.

#### 1. Ruptura de la Ergodicidad y Estados Absorbentes
- **El Problema:** La estadística clásica cree que el promedio esperado de un portafolio de opciones de decisión a lo largo del tiempo es igual al promedio en un punto específico.
- **La Solución Estocástica:** Si un sistema tiene un estado absorbente (la bancarrota, iliquidez total), el **valor esperado a largo plazo es CERO**. El motor rastrea el "riesgo de ruina", asegurando que ninguna trayectoria única golpee la pared de absorción temporal, sin importar cuán altos parezcan los retornos promedio.

#### 2. Convexidad y Eliminación de Truncamientos (Min-Max)
- **Cero Techos Artificiales:** El motor ha sido expurgado de cualquier normalización Min-Max que corte las colas derechas de la distribución. Las opciones deben ser juzgadas por su potencial de escalar exponencialmente (*Convexidad*).
- **Adiós a la Varianza como Riesgo:** Se prohíbe el uso conceptual de la Desviación Estándar ($\sigma$) como única medida de riesgo (debido a la varianza infinita de las colas pesadas). En cambio, se utilizan heurísticas de diseño asimétrico (Downside Semi-Variance y medición explícita de colas vía percentiles P99).

#### 3. El Portafolio Barbell y Covarianza Empírica
En el diseño de portafolios *Barbell* (protección extrema a un lado, riesgo salvaje al otro), el cálculo del riesgo estocástico conjunto **nunca** asume correlación nula de manera ingenua.
- **Implementación Matemática:** Se utiliza estrictamente la Matriz de Covarianza Empírica ($\Sigma$) extraída directamente de las trayectorias de Monte Carlo. Esto destapa las debilidades estructurales sistémicas donde ambos lados del Barbell podrían colapsar juntos.

### Clases Principales
- **`AntifragileAnalyzer`**: Motor que escanea las trayectorias buscando convexidad asimétrica pura.
- **`RobustnessAnalyzer`**: Verifica qué opción sobrevive mejor a escenarios donde todos los parámetros de entrada se estresan hacia el peor decil posible.

---
