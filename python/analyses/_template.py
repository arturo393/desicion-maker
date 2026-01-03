"""
Título: Análisis de Decisión - [NOMBRE]
Propósito: [Descripción de qué decisión se está tomando]
Fecha de Creación: [YYYY-MM-DD]
Última Actualización: [YYYY-MM-DD]
Versión: 1.0

CAMBIOS EN ESTA VERSIÓN:
- [Cambio 1]
- [Cambio 2]

PRÓXIMOS PASOS:
- [ ] Paso 1
- [ ] Paso 2

NOTAS:
- Agregar notas importantes aquí
"""

import sys
from pathlib import Path

# Agregar path al core del framework
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.deep_research_decision_agent import DeepResearchDecisionAgent
import json
from datetime import datetime

# ============================================================
# CONFIGURACIÓN DEL ANÁLISIS
# ============================================================

analysis_name = "TODO_CHANGE_ME"
analysis_date = datetime.now().isoformat()

# Definir la pregunta de investigación
research_question = """
[Tu pregunta de investigación aquí]
"""

# Definir alternativas
alternatives = [
    {
        "name": "Alternativa 1",
        "description": "Descripción de la alternativa 1",
        "initial_cost": 0,
        "monthly_cost": 0,
    },
    {
        "name": "Alternativa 2",
        "description": "Descripción de la alternativa 2",
        "initial_cost": 0,
        "monthly_cost": 0,
    },
]

# Criterios de decisión
criteria = {
    "cost": {"weight": 0.3, "type": "min"},  # Minimizar costo
    "quality": {"weight": 0.4, "type": "max"},  # Maximizar calidad
    "time": {"weight": 0.3, "type": "min"},  # Minimizar tiempo
}

# ============================================================
# EJECUTAR ANÁLISIS
# ============================================================

def main():
    print(f"🔍 Iniciando análisis: {analysis_name}")
    print(f"📅 Fecha: {analysis_date}")
    print("=" * 60)
    
    # Crear agente de decisión
    agent = DeepResearchDecisionAgent()
    
    # Configurar análisis
    agent.set_alternatives(alternatives)
    agent.set_criteria(criteria)
    
    # Ejecutar análisis
    print("\n📊 Ejecutando análisis con metodologías:")
    print("  - Monte Carlo Simulation")
    print("  - TOPSIS")
    print("  - Pareto Analysis")
    print("  - Sensitivity Analysis")
    
    results = agent.analyze(
        question=research_question,
        use_deep_research=False,  # Cambiar a True si necesitas Deep Research
        monte_carlo_iterations=10000,
    )
    
    # Mostrar resultados
    print("\n" + "=" * 60)
    print("📈 RESULTADOS DEL ANÁLISIS")
    print("=" * 60)
    print(f"\n🏆 Decisión Recomendada: {results['recommended_alternative']}")
    print(f"💡 Confianza: {results['confidence']:.1%}")
    print(f"\n📝 Razonamiento:\n{results['reasoning']}")
    
    # Guardar resultados
    output_dir = Path(__file__).parent.parent.parent / "results" / analysis_name
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / f"{analysis_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Resultados guardados en: {output_file}")
    print("\n✅ Análisis completado exitosamente")

if __name__ == "__main__":
    main()
