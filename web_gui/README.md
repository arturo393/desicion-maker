# 🖥️ GUI del Decision Maker

¡Ya tienes **3 opciones** para usar el sistema con interfaz gráfica!

## 🚀 Opción 1: GUI Simple (Recomendada)

**La más fácil de usar - Solo abre el archivo en tu navegador**

```bash
# Navega a la carpeta
cd web_gui

# Abre el archivo simple.html en tu navegador favorito
# En macOS:
open simple.html
# En Linux:
xdg-open simple.html
# En Windows:
start simple.html
```

**Características:**
- ✅ **No requiere servidor** - Funciona directo del archivo
- ✅ **Interfaz limpia y moderna**
- ✅ **Simulaciones Monte Carlo completas**
- ✅ **Resultados con gráficos y recomendaciones**
- ✅ **Funciona en cualquier navegador moderno**

## 🌐 Opción 2: GUI Avanzada con Servidor

**Para una experiencia más profesional con gráficos interactivos**

```bash
# Navega a la carpeta
cd web_gui

# Inicia el servidor
python3 server.py

# Se abrirá automáticamente en: http://localhost:8000
```

**Características:**
- ✅ **Gráficos interactivos** con Chart.js
- ✅ **Múltiples tipos de decisión** (computadora, auto, trabajo)
- ✅ **Interfaz bootstrap profesional**
- ✅ **Análisis estadístico avanzado**
- ✅ **Exportación de resultados**

## 💻 Opción 3: Seguir con C++

**Para máximo control y performance**

```bash
# Compila cualquier ejemplo
g++ -std=c++17 examples/decision_computadora_arturo.cpp -o decision_arturo

# Ejecuta
./decision_arturo
```

## 🎯 ¿Cuál elegir?

### Para usuarios normales: **GUI Simple** ⭐⭐⭐⭐⭐
- Abres el archivo y listo
- Perfecta para decisiones rápidas
- No necesitas instalar nada

### Para análisis profundo: **GUI Avanzada** ⭐⭐⭐⭐
- Gráficos interactivos
- Múltiples tipos de decisión
- Análisis estadístico completo

### Para desarrolladores: **C++** ⭐⭐⭐
- Control total del algoritmo
- Máxima personalización
- Performance óptima

## 📱 ¿Cómo usar la GUI Simple?

1. **Abre `simple.html`** en tu navegador
2. **Configura tus opciones:**
   - Cambia nombres, costos, satisfacción
   - Ajusta el número de simulaciones
   - Define el horizonte temporal

3. **Ejecuta la simulación** (5,000-10,000 iteraciones)
4. **Ve los resultados:**
   - Costo promedio de cada opción
   - Satisfacción esperada
   - Análisis de riesgo
   - Recomendación final

## 🛠️ Personalización

### Cambiar los valores por defecto:
Edita las líneas 100-110 en `simple.html`:

```javascript
const defaultOptions = [
    { name: 'Tu opción 1', cost: 100, satisfaction: 8.0, reliability: 9.0 },
    { name: 'Tu opción 2', cost: 200, satisfaction: 7.5, reliability: 8.5 },
    // Añade más opciones...
];
```

### Cambiar el algoritmo de simulación:
Modifica la función `simulateOption()` en línea 200+ de `simple.html`

## 🎲 Ejemplos de Uso

### 💻 **Decisión de Computadora (Tu caso)**
- Seguir con MacBook 2019: $50, satisfacción 6.5
- Mini PC AMD: $290, satisfacción 8.7
- Mac Mini usado: $280, satisfacción 7.5

### 🚗 **Decisión de Auto**
- Toyota Corolla usado: $15,000, satisfacción 7.5
- Honda Civic nuevo: $25,000, satisfacción 8.5
- Nissan Versa usado: $12,000, satisfacción 6.0

### 💼 **Decisión de Trabajo**
- Startup: $80k, satisfacción 9.0, estabilidad 5.0
- Empresa grande: $95k, satisfacción 7.0, estabilidad 9.0
- Freelance: $90k, satisfacción 8.5, estabilidad 4.0

## 🔧 Solución de Problemas

### La GUI Simple no carga:
- Asegúrate de tener un navegador moderno (Chrome, Firefox, Safari)
- Abre las herramientas de desarrollador (F12) para ver errores

### El servidor no inicia:
```bash
# Si puerto 8000 está ocupado:
python3 server.py 8001

# O usa Python 2 si no tienes Python 3:
python server.py
```

### Los resultados no parecen correctos:
- Verifica que los valores de entrada sean razonables
- Aumenta el número de simulaciones para mayor precisión
- Revisa que satisfaction y reliability estén entre 1-10

## 📊 Interpretación de Resultados

### **Costo Promedio**: 
El gasto esperado considerando mantenimiento, depreciación, y valor residual

### **Satisfacción**: 
Qué tan feliz estarás con la decisión (1-10)

### **Score Valor**: 
Satisfacción por cada $100 invertidos (mayor = mejor)

### **Problemas**: 
Tiempo perdido esperado por problemas técnicos

## 🎯 ¡Tu Turno!

1. **Abre `simple.html`** ahora mismo
2. **Configura tu decisión real** (computadora, auto, etc.)
3. **Ejecuta 5,000 simulaciones**
4. **Toma tu decisión** basada en datos, no en intuición

¡La diferencia entre adivinar y usar Monte Carlo puede ahorrarte cientos de dólares y mucha frustración!