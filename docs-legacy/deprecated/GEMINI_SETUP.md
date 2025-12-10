# 🚀 GEMINI API - QUICK START

## Opción 1: Usa variable de entorno 🔐

```bash
# Establecer la API key (una sola vez)
export GEMINI_API_KEY="tu_api_key_aqui"

# Verificar que está seteada
echo $GEMINI_API_KEY

# Ejecutar script
python3 scripts/gemini_market_research.py --sillon
```

## Opción 2: Pasar API key por línea de comando 🔑

```bash
python3 scripts/gemini_market_research.py \
  --api-key "tu_api_key_aqui" \
  --sillon \
  --output "resultados.json"
```

## Opción 3: Extraer de Git Bash 💾

Si tienes la key en `git bash`:

```bash
# Leer de bashrc
cat ~/.bashrc | grep GEMINI_API_KEY

# Luego úsala:
export GEMINI_API_KEY=$(cat ~/.bashrc | grep GEMINI_API_KEY | cut -d= -f2)

# Verificar
echo $GEMINI_API_KEY

# Ejecutar
python3 scripts/gemini_market_research.py --sillon
```

## Instalación requerida (una sola vez)

```bash
pip3 install google-generativeai
```

## ¿Dónde obtener API Key?

1. Ir a: https://aistudio.google.com/app/apikey
2. Click en "Create API key"
3. Copiar la key
4. Guardar en variable de entorno

## Ejemplos de uso

### Análisis del sillón
```bash
python3 scripts/gemini_market_research.py --sillon
```

### Búsqueda custom
```bash
python3 scripts/gemini_market_research.py --query "precio sillón usado Santiago"
```

### Con salida personalizada
```bash
python3 scripts/gemini_market_research.py \
  --sillon \
  --output "mi_analisis.json"
```

## Output

Genera:
- `gemini_results.json` - Datos completos en JSON
- `src/gemini_api_integration.h` - Código C++ para integración

## Integración con análisis actual

```bash
# 1. Obtener datos reales del mercado
python3 scripts/gemini_market_research.py --sillon

# 2. Leer resultados y actualizar precios
cat gemini_results.json

# 3. Regenerar análisis con datos nuevos
python3 scripts/generate_sillon_analysis.py

# 4. Compilar y ejecutar
g++ -std=c++17 -o bin/sillon_decision examples/sillon_decision_v2.cpp
./bin/sillon_decision
```

---

**¿Necesitas ayuda?** Revisa `/scripts/gemini_market_research.py` línea 30 para ver todas las opciones.
