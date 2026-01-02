# ✅ Configuración UV - Completada

**Fecha**: 2024-12-28
**Estado**: ✅ OPERACIONAL

---

## 🎯 Lo que se configuró

### 1. Entorno Virtual con UV
```bash
uv venv
# Creado en: .venv/
# Python: 3.11.3
```

### 2. Dependencias Instaladas
```bash
uv pip install google-genai python-dotenv numpy pandas aiohttp
```

**Paquetes instalados (39 total)**:
- ✅ google-genai 1.56.0
- ✅ python-dotenv 1.2.1
- ✅ numpy 2.4.0
- ✅ pandas 2.3.3
- ✅ aiohttp 3.13.2
- + 34 dependencias más

### 3. Configuración .env
```bash
# Archivo: .env
GEMINI_API_KEY=AIzaSyDIuo2lfInFZKe...
```
 API Key configurado y funcional

---

## 🚀 Cómo usar UV

### Opción 1: Con `uv run` (Recomendado - No requiere activar)
```bash
# Ejecutar scripts directamente
uv run python core/deep_research_decision_agent.py

# Ejecutar con argumentos
uv run python core/mining_career_analyzer.py --verbose

# Ejecutar tests
uv run python test_gemini.py
```

### Opción 2: Activando el entorno
```bash
# Activar
source .venv/bin/activate

# Ahora puedes usar python normal
python core/deep_research_decision_agent.py

# Desactivar
deactivate
```

---

## 💡 Ventajas de UV vs pip

| Característica | UV | pip |
|---------------|-----|-----|
| **Velocidad** | 10-100x más rápido | Base |
| **Cache** | Inteligente global | Por proyecto |
| **Resolución deps** | Paralela | Secuencial |
| **Lock file** | uv.lock automático | Requiere pip-tools |
| **Uso** | `uv run` sin activar | Requiere activar venv |

---

## 🧪 Tests Ejecutados

### Test UV + Gemini
```bash
uv run python test_gemini.py
```

**Resultado**: ✅ 5/5 tests pasados

```
 Entorno UV:           OK
 google-genai:         OK (1.56.0)
 Dependencias:         OK
 Configuración .env:   OK
 Conexión Gemini:      OK
```

---

## 📦 Gestión de Dependencias

### Agregar nuevas dependencias
```bash
uv pip install nombre-paquete
```

### Ver paquetes instalados
```bash
uv pip list
```

### Actualizar paquetes
```bash
uv pip install --upgrade google-genai
```

### Eliminar paquetes
```bash
uv pip uninstall nombre-paquete
```

### Freezear dependencias
```bash
uv pip freeze > requirements.txt
```

---

## 🔧 Comandos Útiles

### Ver versión de UV
```bash
uv --version
# uv 0.9.17
```

### Crear nuevo proyecto con UV
```bash
uv init nuevo-proyecto
cd nuevo-proyecto
uv sync
```

### Limpiar cache de UV
```bash
uv cache clean
```

### Ver información del entorno
```bash
uv pip show google-genai
```

---

## 📁 Archivos Creados

```
python/
 .venv/                 # Virtual environment UV
 .env                   # API keys configuradas ✅
 .env.example           # Template
 test_gemini.py         # Test de configuración
 UV_SETUP.md            # Este archivo
 requirements.txt       # Dependencias (opcional)
 core/
   ├── deep_research_decision_agent.py
   └── mining_career_analyzer.py
 scripts/
    └── ...
```

---

## 🎯 Próximos Pasos

### 1. Ejecutar un análisis simple
```bash
cd python
uv run python -c "
from core.deep_research_decision_agent import DecisionAnalysisEngine
engine = DecisionAnalysisEngine()
print('✅ Framework cargado correctamente')
"
```

### 2. Ejecutar análisis completo con Gemini
```bash
# Ver casos en ../cases/mining/
uv run python core/mining_career_analyzer.py
```

### 3. Crear tu propia decisión
```python
# Ver ejemplos en core/deep_research_decision_agent.py
from core.deep_research_decision_agent import CareerOption, DecisionAnalysisEngine

option = CareerOption(
    name="Mi Decisión",
    salary_expected=1_000_000,
    probability_success=0.8,
    # ... más campos
)

engine = DecisionAnalysisEngine()
result = engine.analyze_option(option, [option])
print(result.recommendation)
```

---

## ⚡ Diferencias clave: `uv run` vs `source .venv/bin/activate`

### Con `uv run` (Moderno)
```bash
# No necesitas activar
uv run python script.py

# UV maneja el entorno automáticamente
# Más rápido
# Menos propenso a errores
```

### Con activación tradicional
```bash
# Activar manualmente
source .venv/bin/activate

# Ahora python está en el venv
python script.py

# Desactivar cuando termines
deactivate
```

**Recomendación**: Usa `uv run` - es más simple y moderno.

---

## 🐛 Troubleshooting

### Error: "uv: command not found"
```bash
# Instalar UV
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Error: "GEMINI_API_KEY not found"
```bash
# Verificar .env
cat .env | grep GEMINI_API_KEY

# Editar si es necesario
nano .env
```

### Error: "Module not found"
```bash
# Reinstalar dependencias
uv pip install -r requirements.txt
```

---

## ✨ Conclusión

### Estado: ✅ CONFIGURACIÓN COMPLETA

- ✅ UV instalado y funcional (0.9.17)
- ✅ Virtual environment creado
- ✅ 39 paquetes instalados
- ✅ google-genai 1.56.0 funcional
- ✅ Gemini API configurado y testeado
- ✅ Framework listo para usar

**Próximo paso**: Ejecutar un análisis de decisiones con Gemini

```bash
cd python
uv run python core/deep_research_decision_agent.py
```

---

**Documentación UV**: https://github.com/astral-sh/uv
**Gemini API**: https://ai.google.dev/
