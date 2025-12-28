# ✅ Gemini Flash - Configurado y Testeado

**Fecha**: 2024-12-28
**Modelo**: Gemini 2.0 Flash (Experimental)
**Costo**: 🎉 **GRATIS** (en preview)

---

## 🚀 Qué se configuró

### 1. Archivo de Configuración (`config.py`)

Sistema para gestionar modelos Gemini:

```python
from config import GeminiConfig

config = GeminiConfig()
config.print_config()  # Ver configuración actual
```

**3 modelos disponibles**:
- ✅ **flash** - Gratis, rápido, perfecto para tests
- **pro** - Balanceado ($1.25/1M tokens)
- **ultra** - Más potente ($1.25/1M tokens)

### 2. Modelo Flash Configurado

```bash
# Ver modelos disponibles
uv run python config.py list

# Cambiar modelo
uv run python config.py set flash

# Ver configuración actual
uv run python config.py current

# Estimar costo
uv run python config.py estimate 1000 500
```

### 3. Tests Ejecutados

```bash
uv run python test_gemini_flash.py
```

**Resultados**: ✅ 2/2 tests pasados

---

## 📊 Tests Realizados

### Test 1: Query Simple ✅

**Pregunta**: "¿Cuál es la capital de Chile?"  
**Respuesta**: "Santiago"  
**Costo**: $0.00 (GRATIS)  

### Test 2: Análisis de Decisión ✅

**Escenario**: Compra de laptop (usada vs nueva)  
**Respuesta**: Recomendación detallada en 3 líneas  
**Costo**: $0.00 (GRATIS)  

---

## 💰 Comparación de Costos

| Modelo | Costo Input | Costo Output | Uso Recomendado |
|--------|-------------|--------------|-----------------|
| **Flash** | **GRATIS** | **GRATIS** | Tests, prototipos, análisis simples ⭐ |
| Pro | $1.25/1M | $5/1M | Análisis complejos, research profundo |
| Ultra | $1.25/1M | $5/1M | Decisiones críticas, máxima calidad |

**Para análisis de 10,000 tokens**:
- Flash: **$0.00** 🎉
- Pro: **~$0.06**
- Ultra: **~$0.06**

---

## 
```bash
# Modelo seleccionado
GEMINI_MODEL=flash

# API Key (ya configurado)
GEMINI_API_KEY=AIzaSyD...

# Parámetros opcionales
GEMINI_TEMPERATURE=0.7
GEMINI_MAX_TOKENS=2048
```

---

## 🎯 Cómo Usar en tus Scripts

### Opción 1: Usar config.py

```python
from config import GeminiConfig
from google import genai
import os

# Cargar configuración
config = GeminiConfig()
config.print_config()  # Opcional: ver config

# Inicializar cliente
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Usar el modelo configurado
response = client.models.generate_content(
    model=config.get_model_name(),  # Usa el modelo de .env
    contents="Tu pregunta aquí"
)

print(response.text)
```

### Opción 2: Integrar con Decision Framework

```python
# En core/deep_research_decision_agent.py
from config import GeminiConfig

class GeminiDeepResearchAgent:
    def __init__(self, debug: bool = True):
        self.config = GeminiConfig()  # Usa config
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.client = genai.Client(api_key=self.api_key)
        self.agent_name = self.config.get_model_name()  # Modelo dinámico
```

---

## 📋 Comandos Útiles

### Gestión de Modelos
```bash
# Ver todos los modelos disponibles
uv run python config.py list

# Ver configuración actual
uv run python config.py current

# Cambiar a modelo más barato (Flash)
uv run python config.py set flash

# Cambiar a modelo balanceado (Pro)
uv run python config.py set pro

# Cambiar a modelo potente (Ultra)
uv run python config.py set ultra
```

### Estimación de Costos
```bash
# Estimar costo de una consulta
uv run python config.py estimate <input_tokens> <output_tokens>

# Ejemplo: 1000 tokens input, 500 output
uv run python config.py estimate 1000 500
```

### Tests
```bash
# Test completo con análisis
uv run python test_gemini_flash.py

# Test solo configuración
uv run python test_gemini.py
```

---

## 🎨 Casos de Uso por Modelo

### Flash (GRATIS) - Usa para:
- ✅ Tests y prototipos
- ✅ Análisis simples y rápidos
- ✅ Validación de ideas
- ✅ Experimentación sin costo
- ✅ Queries frecuentes con respuestas cortas

### Pro ($1.25/1M) - Usa para:
- 📊 Análisis de decisiones complejas
- 🔍 Research profundo de mercado
- 📈 Análisis financieros detallados
- 💼 Decisiones de negocio importantes

### Ultra ($1.25/1M) - Usa para:
- 🎯 Decisiones críticas
- 🧠 Análisis que requieren máxima precisión
- 💎 Cuando la calidad es más importante que el costo

---

## 📈 Estimación de Uso Real

### Análisis de Decisión Típico
- **Input**: ~1,000 tokens (descripción del problema)
- **Output**: ~500 tokens (análisis y recomendación)
- **Total**: 1,500 tokens

**Costos**:
- Flash: **$0.00** 🎉
- Pro: **$0.00375** (~$0.004)
- Ultra: **$0.00375** (~$0.004)

### 100 Análisis al Mes
- Flash: **$0.00** 🎉
- Pro: **$0.38**
- Ultra: **$0.38**

**Conclusión**: Flash es perfecto para la mayoría de los casos.

---

## ⚠️ Limitaciones de Flash

1. **Preview Experimental**: Puede cambiar o discontinuarse
2. **Rate Limits**: Posibles límites de requests/min
3. **Calidad**: Buena pero no la mejor (suficiente para la mayoría)

**Recomendación**: Usa Flash para desarrollo y tests, considera Pro/Ultra solo si necesitas mejor calidad.

---

## 🔄 Migración Entre Modelos

Cambiar de modelo es instantáneo:

```bash
# Desarrollo/Testing → Flash
uv run python config.py set flash

# Producción/Análisis Importantes → Pro
uv run python config.py set pro

# Decisiones Críticas → Ultra  
uv run python config.py set ultra
```

No necesitas cambiar tu código, solo el `.env` 🎉

---

## 📝 Ejemplo Completo

```python
#!/usr/bin/env python3
"""Ejemplo: Análisis de decisión con modelo configurable"""

from config import GeminiConfig
from google import genai
import os
from dotenv import load_dotenv

load_dotenv()

# Setup
config = GeminiConfig()
config.print_config()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Query
decision = """
Tengo que decidir si aceptar un trabajo en minería en Chile:
- Salario: $4,500,000 CLP/mes
- Ubicación: Antofagasta (lejos de Santiago)
- Contrato: 2 años

Qué factores debería considerar?
"""

# Generar respuesta
response = client.models.generate_content(
    model=config.get_model_name(),
    contents=decision
)

print(response.text)

# Estimar costo
cost = config.estimate_cost(input_tokens=100, output_tokens=200)
print(f"\nCosto: ${cost:.6f}")
```

---

## ✅ Estado Final

| Componente | Estado |
|-----------|--------|
| Config System | ✅ Implementado |
| Gemini Flash | ✅ Configurado |
| Tests | ✅ 2/2 Pasados |
| Costo | 🎉 GRATIS |
| Documentación | ✅ Completa |

**Próximo paso**: Usar en análisis reales del framework

```bash
cd python
uv run python core/deep_research_decision_agent.py
```

---

**🎉 Todo listo para analizar decisiones con IA gratis!**
