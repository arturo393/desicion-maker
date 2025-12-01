# Guía de Inicio Rápido - Decision Maker Framework

## 🚀 Compilación y Ejecución Rápida

### Opción 1: Usando Make (Recomendado para principiantes)

```bash
# Clonar/navegar al proyecto
cd /Users/arturo/development/GitHub/desicion-maker

# Compilar todo
make all

# Ejecutar ejemplos
make run-example-basic_dice          # Ejemplo básico con dados
make run-example-simple_decision     # Decisión del paraguas
make run-example-investment_vs_education  # Ejemplo complejo

# Limpiar si necesitas recompilar
make clean
```

### Opción 2: Usando CMake (Para usuarios avanzados)

```bash
# Crear directorio de build
mkdir build && cd build

# Configurar proyecto
cmake ..

# Compilar
make all

# Ejecutar ejemplos
./basic_dice
./simple_decision
./investment_vs_education

# Ver ayuda
make help-custom
```

## 📚 Aprendizaje Progresivo

### Paso 1: Conceptos Básicos (`basic_dice.cpp`)
- Comprende qué es Monte Carlo
- Aprende la estructura básica del framework
- Ve cómo crear escenarios simples
- Entiende distribuciones estadísticas

### Paso 2: Decisiones Reales (`simple_decision.cpp`)
- Modela incertidumbre en decisiones cotidianas
- Aprende a comparar alternativas
- Ve análisis de sensibilidad básico
- Comprende utilidad y costos

### Paso 3: Casos Complejos (`investment_vs_education.cpp`)
- Decisiones multi-criterio
- Análisis estadístico avanzado
- Visualizaciones y reportes
- Optimización de parámetros

## 🛠️ Crear Tu Propio Escenario

### Template Básico

```cpp
#include "src/core/MonteCarloEngine.h"
#include "src/distributions/Distributions.h"

using namespace DecisionMaker;

class MiEscenario : public DecisionScenario {
public:
    MiEscenario() : DecisionScenario("Mi Decisión", "Descripción") {}
    
    SimulationResult runSimulation(std::mt19937& rng) const override {
        // 1. Obtener parámetros y distribuciones
        const auto* dist = parameters_.getDistribution("mi_parametro");
        double valor = dist->sample(rng);
        
        // 2. Lógica de tu decisión
        double resultado = calcularResultado(valor);
        
        // 3. Determinar éxito
        bool exito = resultado > umbral_exito;
        
        // 4. Crear resultado
        SimulationResult result(resultado, exito);
        result.metrics["metrica1"] = valor;
        
        return result;
    }
    
    bool validateConfiguration() const override {
        return parameters_.hasParameter("mi_parametro");
    }
    
    std::vector<std::string> getRequiredParameters() const override {
        return {"mi_parametro"};
    }
    
private:
    double calcularResultado(double input) const {
        // Tu lógica aquí
        return input * 2.0;
    }
};

int main() {
    // Crear escenario
    MiEscenario escenario;
    
    // Configurar parámetros
    escenario.getParameters().setDistribution("mi_parametro",
        std::make_unique<NormalDistribution>(100, 20));
    
    // Ejecutar simulación
    MonteCarloEngine engine(10000);
    auto resultados = engine.simulate(escenario);
    
    // Analizar
    std::cout << "Resultado promedio: " << resultados.getMean() << std::endl;
    std::cout << "Probabilidad éxito: " << resultados.getSuccessProbability() << std::endl;
    
    return 0;
}
```

## 📊 Tipos de Distribuciones Disponibles

```cpp
// Normal (Gaussiana)
auto normal = std::make_unique<NormalDistribution>(media, desviacion);

// Uniforme
auto uniforme = std::make_unique<UniformDistribution>(min, max);

// Exponencial
auto exponencial = std::make_unique<ExponentialDistribution>(lambda);

// Triangular
auto triangular = std::make_unique<TriangularDistribution>(min, max, modo);

// Log-Normal
auto lognormal = std::make_unique<LogNormalDistribution>(mu, sigma);

// Beta
auto beta = std::make_unique<BetaDistribution>(alpha, beta, min, max);

// Gamma
auto gamma = std::make_unique<GammaDistribution>(forma, escala);

// Discreta personalizada
std::vector<double> valores = {1, 2, 3, 4, 5};
std::vector<double> probabilidades = {0.1, 0.2, 0.4, 0.2, 0.1};
auto discreta = std::make_unique<DiscreteDistribution>(valores, probabilidades);
```

## 🎯 Casos de Uso Comunes

### Finanzas
- Análisis de inversiones
- Gestión de riesgos
- Optimización de portafolios
- Planificación de retiro

### Negocios
- Lanzamiento de productos
- Análisis de mercado
- Gestión de inventarios
- Planificación de capacidad

### Personal
- Decisiones de carrera
- Compra de casa/auto
- Planificación de vacaciones
- Elección de seguros

### Ingeniería
- Análisis de confiabilidad
- Optimización de procesos
- Gestión de calidad
- Planificación de mantenimiento

## 🔧 Personalización Avanzada

### Configuración del Motor

```cpp
auto config = MonteCarloConfigBuilder()
    .withSimulations(100000)     // Más simulaciones = mayor precisión
    .withThreads(8)              // Usar múltiples núcleos
    .withVerbose(true)           // Mostrar progreso
    .withConvergenceCheck(true)  // Parar cuando converja
    .build();

MonteCarloEngine engine(config);
```

### Análisis Estadístico

```cpp
#include "src/utils/Analysis.h"
using namespace DecisionMaker::Utils;

// VaR y CVaR
double var95 = StatisticalAnalyzer::calculateVaR(resultados, 0.95);
double cvar95 = StatisticalAnalyzer::calculateCVaR(resultados, 0.95);

// Ratio de Sharpe
double sharpe = StatisticalAnalyzer::calculateSharpeRatio(resultados, tasa_libre_riesgo);

// Comparar escenarios
ScenarioComparator comparador;
comparador.addScenario("Opción A", resultados_a);
comparador.addScenario("Opción B", resultados_b);
std::cout << comparador.generateReport();
```

## 📈 Visualización y Reportes

```cpp
#include "src/utils/Analysis.h"

// Histograma en texto
std::cout << TextVisualizer::generateHistogram(resultados);

// Box plot
std::cout << TextVisualizer::generateBoxPlot(resultados);

// Reporte completo
auto reporte = ReportGenerator::generateFullReport(escenario, resultados);
ReportGenerator::exportReport(reporte, "mi_reporte.txt");

// Exportar datos
resultados.exportToCSV("datos.csv");
```

## 🆘 Solución de Problemas

### Error de Compilación
```bash
# Verificar dependencias
make check-deps

# Limpiar y recompilar
make clean
make all
```

### Simulación Muy Lenta
```cpp
// Reducir simulaciones para pruebas
MonteCarloEngine engine(1000);  // En lugar de 100000

// Usar menos threads si hay problemas de memoria
auto config = MonteCarloConfigBuilder()
    .withSimulations(10000)
    .withThreads(2)  // En lugar de usar todos los núcleos
    .build();
```

### Resultados Inconsistentes
```cpp
// Fijar semilla para reproducibilidad
auto config = MonteCarloConfigBuilder()
    .withSeed(12345)
    .build();

// Aumentar número de simulaciones
MonteCarloEngine engine(100000);  // Más simulaciones = más estabilidad
```

## 📖 Recursos Adicionales

- **Documentación completa**: Ejecutar `make docs` (requiere Doxygen)
- **Código fuente**: Explorar `src/` para entender implementación
- **Más ejemplos**: Crear variaciones de los ejemplos existentes
- **Tests**: Ejecutar `make tests` para verificar funcionamiento

## 🤝 Contribuir

1. Crear nuevos escenarios en `src/scenarios/`
2. Agregar nuevas distribuciones en `src/distributions/`
3. Mejorar utilidades de análisis en `src/utils/`
4. Agregar ejemplos en `examples/`
5. Escribir tests en `tests/`

¡El framework está diseñado para ser extensible y fácil de usar!