#!/usr/bin/env python3
"""
🧪 Test rápido del framework Python reorganizado
No requiere API keys ni dependencias externas
"""

import sys
import os
from pathlib import Path

# Add core to path
sys.path.insert(0, str(Path(__file__).parent / 'core'))

def test_imports():
    """Test 1: Verificar que los módulos se pueden importar"""
    print("🧪 Test 1: Verificando imports...")
    
    try:
        from deep_research_decision_agent import (
            CareerOption,
            AnalysisResult,
            DecisionAnalysisEngine
        )
        print("   ✅ Imports correctos")
        return True, (CareerOption, AnalysisResult, DecisionAnalysisEngine)
    except Exception as e:
        print(f"   ❌ Error en imports: {e}")
        return False, None

def test_data_structures(modules):
    """Test 2: Verificar que las estructuras de datos funcionan"""
    print("\n🧪 Test 2: Verificando estructuras de datos...")
    
    try:
        CareerOption, AnalysisResult, DecisionAnalysisEngine = modules
        
        # Crear una opción simple
        option = CareerOption(
            name="Test Option",
            salary_expected=1_000_000,
            probability_success=0.8,
            timeline_months=12,
            tech_growth=7.0,
            income_stability=8.0,
            work_life_balance=6.0,
            prestige=7.5,
            remote_flexibility=5.0,
            learning_opportunity=8.0,
            career_ceiling=7.0,
            unemployment_risk=0.2,
            burnout_risk=0.3,
            market_risk=0.25,
            description="Test option for framework validation"
        )
        
        print(f"   ✅ CareerOption creada: {option.name}")
        print(f"      - Salario: ${option.salary_expected:,.0f}")
        print(f"      - Probabilidad éxito: {option.probability_success*100}%")
        
        return True, option
    except Exception as e:
        print(f"   ❌ Error creando estructuras: {e}")
        return False, None

def test_decision_engine(option, modules):
    """Test 3: Verificar que el motor de decisiones funciona"""
    print("\n🧪 Test 3: Verificando motor de decisiones...")
    
    try:
        CareerOption, AnalysisResult, DecisionAnalysisEngine = modules
        
        # Crear engine
        engine = DecisionAnalysisEngine(debug=False)
        print("   ✅ DecisionAnalysisEngine inicializado")
        
        # Crear opciones para comparación
        option2 = CareerOption(
            name="Alternative Option",
            salary_expected=1_200_000,
            probability_success=0.7,
            timeline_months=18,
            tech_growth=6.0,
            income_stability=7.0,
            work_life_balance=8.0,
            prestige=6.0,
            remote_flexibility=9.0,
            learning_opportunity=7.0,
            career_ceiling=6.5,
            unemployment_risk=0.25,
            burnout_risk=0.2,
            market_risk=0.3,
            description="Alternative for comparison"
        )
        
        all_options = [option, option2]
        
        # Analizar
        print("   🔄 Ejecutando análisis (13 metodologías)...")
        result = engine.analyze_option(option, all_options)
        
        print(f"\n   📊 RESULTADOS:")
        print(f"      - Monte Carlo Score: {result.monte_carlo_score:.2f}")
        print(f"      - TOPSIS Rank: {result.topsis_rank}")
        print(f"      - Pareto Optimal: {result.pareto_optimal}")
        print(f"      - Risk Score: {result.risk_score:.2f}")
        print(f"      - Overall Score: {result.overall_score:.2f}/10")
        print(f"      - Confidence: {result.confidence*100:.1f}%")
        print(f"      - Recommendation: {result.recommendation}")
        
        return True, result
    except Exception as e:
        print(f"   ❌ Error en motor de decisiones: {e}")
        import traceback
        traceback.print_exc()
        return False, None

def test_methodologies(result):
    """Test 4: Verificar que todas las metodologías corrieron"""
    print("\n🧪 Test 4: Verificando metodologías...")
    
    try:
        methodologies = {
            "Monte Carlo": result.monte_carlo_score > 0,
            "TOPSIS": result.topsis_rank > 0,
            "Pareto": result.pareto_optimal is not None,
            "Regret": result.regret_analysis >= 0,
            "Risk (VaR)": result.risk_score >= 0,
            "Scenario": result.scenario_robustness >= 0,
        }
        
        all_passed = all(methodologies.values())
        
        for name, passed in methodologies.items():
            status = "✅" if passed else "❌"
            print(f"      {status} {name}")
        
        if all_passed:
            print(f"\n   ✅ Todas las metodologías funcionan correctamente")
        else:
            print(f"\n   ⚠️  Algunas metodologías tienen problemas")
        
        return all_passed
    except Exception as e:
        print(f"   ❌ Error verificando metodologías: {e}")
        return False

def main():
    """Ejecutar todos los tests"""
    print("\n" + "="*70)
    print("   🚀 TEST DEL FRAMEWORK REORGANIZADO")
    print("="*70 + "\n")
    
    # Test 1: Imports
    success1, modules = test_imports()
    if not success1:
        print("\n❌ Test fallido en imports. Abortando.")
        return False
    
    # Test 2: Data structures
    success2, option = test_data_structures(modules)
    if not success2:
        print("\n❌ Test fallido en estructuras. Abortando.")
        return False
    
    # Test 3: Decision engine
    success3, result = test_decision_engine(option, modules)
    if not success3:
        print("\n❌ Test fallido en motor de decisiones.")
        return False
    
    # Test 4: Methodologies
    success4 = test_methodologies(result)
    
    # Resumen final
    print("\n" + "="*70)
    if success1 and success2 and success3 and success4:
        print("   ✅ TODOS LOS TESTS PASARON")
        print("\n   🎉 Framework Python funcionando correctamente!")
        print("   📁 Estructura reorganizada: OPERACIONAL")
    else:
        print("   ⚠️  ALGUNOS TESTS FALLARON")
        print("\n   ℹ️  El framework está parcialmente funcional")
    print("="*70 + "\n")
    
    return success1 and success2 and success3 and success4

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrumpido por usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
