"""
🔧 Configuración de modelos Gemini
Gestiona qué modelo usar según tus necesidades
"""

import os
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ============================================================================
# MODELOS GEMINI DISPONIBLES
# ============================================================================

GEMINI_MODELS = {
    # Modelo más barato y rápido (Flash)
    "flash": {
        "name": "gemini-2.0-flash-exp",
        "description": "Más rápido y barato - Perfecto para tests",
        "cost_per_1k_input": 0.00,  # Gratis en preview
        "cost_per_1k_output": 0.00,  # Gratis en preview
        "max_tokens": 8192,
        "use_case": "Tests, prototipado rápido, análisis simples"
    },
    
    # Modelo balanceado (Pro)
    "pro": {
        "name": "gemini-1.5-pro-latest",
        "description": "Balanceado - Buena calidad/precio",
        "cost_per_1k_input": 0.00125,  # $1.25 por 1M tokens
        "cost_per_1k_output": 0.005,    # $5 por 1M tokens
        "max_tokens": 8192,
        "use_case": "Análisis de decisiones, research profundo"
    },
    
    # Modelo más potente pero caro
    "ultra": {
        "name": "gemini-1.5-pro-002",
        "description": "Más potente - Mejor calidad",
        "cost_per_1k_input": 0.00125,
        "cost_per_1k_output": 0.005,
        "max_tokens": 8192,
        "use_case": "Análisis críticos, decisiones importantes"
    }
}

# ============================================================================
# CONFIGURACIÓN ACTUAL
# ============================================================================

class GeminiConfig:
    """Gestiona la configuración de Gemini"""
    
    def __init__(self):
        # Cargar desde .env o usar default
        self.selected_model = os.getenv("GEMINI_MODEL", "flash")  # Default: flash (más barato)
        self.temperature = float(os.getenv("GEMINI_TEMPERATURE", "0.7"))
        self.max_tokens = int(os.getenv("GEMINI_MAX_TOKENS", "2048"))
        self.api_key = os.getenv("GEMINI_API_KEY")
        
    def get_model_config(self) -> Dict[str, Any]:
        """Obtener configuración del modelo seleccionado"""
        if self.selected_model not in GEMINI_MODELS:
            print(f"⚠️  Modelo '{self.selected_model}' no encontrado, usando 'flash'")
            self.selected_model = "flash"
        
        return GEMINI_MODELS[self.selected_model]
    
    def get_model_name(self) -> str:
        """Obtener nombre del modelo para la API"""
        return self.get_model_config()["name"]
    
    def estimate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Estimar costo de una llamada"""
        config = self.get_model_config()
        
        input_cost = (input_tokens / 1000) * config["cost_per_1k_input"]
        output_cost = (output_tokens / 1000) * config["cost_per_1k_output"]
        
        return input_cost + output_cost
    
    def print_config(self):
        """Imprimir configuración actual"""
        config = self.get_model_config()
        
        print("\n" + "="*70)
        print("   🤖 CONFIGURACIÓN GEMINI")
        print("="*70)
        print(f"\n   Modelo seleccionado: {self.selected_model.upper()}")
        print(f"   Nombre API: {config['name']}")
        print(f"   Descripción: {config['description']}")
        print(f"   Caso de uso: {config['use_case']}")
        print(f"\n   💰 Costos:")
        print(f"   - Input: ${config['cost_per_1k_input']:.5f} por 1K tokens")
        print(f"   - Output: ${config['cost_per_1k_output']:.5f} por 1K tokens")
        
        if config['cost_per_1k_input'] == 0:
            print(f"   🎉 ¡GRATIS en preview!")
        
        print(f"\n   ⚙️  Parámetros:")
        print(f"   - Temperature: {self.temperature}")
        print(f"   - Max tokens: {self.max_tokens}")
        print("="*70 + "\n")
    
    def print_all_models(self):
        """Imprimir todos los modelos disponibles"""
        print("\n" + "="*70)
        print("   📋 MODELOS GEMINI DISPONIBLES")
        print("="*70 + "\n")
        
        for key, model in GEMINI_MODELS.items():
            is_current = "👉" if key == self.selected_model else "  "
            cost_label = "GRATIS" if model['cost_per_1k_input'] == 0 else f"${model['cost_per_1k_input']:.5f}/1K"
            
            print(f"{is_current} {key.upper():<10} {model['name']:<30}")
            print(f"   {model['description']}")
            print(f"   💰 Costo: {cost_label}")
            print(f"   📝 Uso: {model['use_case']}")
            print()
        
        print("="*70)
        print(f"\nPara cambiar modelo, edita .env y agrega:")
        print(f"GEMINI_MODEL=flash   # o 'pro' o 'ultra'")
        print("="*70 + "\n")


# ============================================================================
# FUNCIÓN HELPER
# ============================================================================

def get_config() -> GeminiConfig:
    """Obtener configuración global"""
    return GeminiConfig()


# ============================================================================
# CLI para seleccionar modelo
# ============================================================================

if __name__ == "__main__":
    import sys
    
    config = GeminiConfig()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "list":
            config.print_all_models()
        
        elif command == "current":
            config.print_config()
        
        elif command == "set" and len(sys.argv) > 2:
            new_model = sys.argv[2]
            
            if new_model in GEMINI_MODELS:
                # Actualizar .env
                env_path = os.path.join(os.path.dirname(__file__), ".env")
                
                # Leer .env actual
                env_lines = []
                if os.path.exists(env_path):
                    with open(env_path, 'r') as f:
                        env_lines = f.readlines()
                
                # Buscar y reemplazar GEMINI_MODEL
                found = False
                for i, line in enumerate(env_lines):
                    if line.startswith("GEMINI_MODEL="):
                        env_lines[i] = f"GEMINI_MODEL={new_model}\n"
                        found = True
                        break
                
                # Si no existe, agregar
                if not found:
                    env_lines.append(f"\n# Modelo Gemini\nGEMINI_MODEL={new_model}\n")
                
                # Escribir
                with open(env_path, 'w') as f:
                    f.writelines(env_lines)
                
                print(f"\n✅ Modelo cambiado a: {new_model.upper()}")
                print(f"📁 Actualizado en: .env")
                
                # Mostrar nueva config
                config = GeminiConfig()
                config.print_config()
            else:
                print(f"\n❌ Modelo '{new_model}' no válido")
                print(f"Modelos disponibles: {', '.join(GEMINI_MODELS.keys())}")
        
        elif command == "estimate":
            if len(sys.argv) > 3:
                input_tokens = int(sys.argv[2])
                output_tokens = int(sys.argv[3])
                
                cost = config.estimate_cost(input_tokens, output_tokens)
                
                print(f"\n💰 Estimación de costo:")
                print(f"   Modelo: {config.selected_model.upper()}")
                print(f"   Input: {input_tokens:,} tokens")
                print(f"   Output: {output_tokens:,} tokens")
                print(f"   Costo: ${cost:.6f}")
                
                if cost == 0:
                    print(f"   🎉 ¡GRATIS!")
                print()
            else:
                print("\nUso: python config.py estimate <input_tokens> <output_tokens>")
        
        else:
            print("\nUso:")
            print("  python config.py list              # Ver todos los modelos")
            print("  python config.py current           # Ver configuración actual")
            print("  python config.py set <modelo>      # Cambiar modelo (flash|pro|ultra)")
            print("  python config.py estimate <in> <out>  # Estimar costo")
    
    else:
        config.print_config()
