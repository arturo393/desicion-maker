#!/usr/bin/env python3
"""
🪑 GENERADOR DE ANÁLISIS DINÁMICO PARA SILLÓN
Ajusta los parámetros reales y regenera el análisis
"""

import json
from datetime import datetime
from typing import Dict

class SillonDecisionGenerator:
    def __init__(self):
        # Valores por defecto (basados en investigación de mercado)
        self.defaults = {
            "costo_botado_min": 50000,
            "costo_botado_max": 150000,
            "costo_botado_promedio": 85000,
            
            "costo_limpiar_min": 30000,
            "costo_limpiar_max": 50000,
            "costo_limpiar_promedio": 40000,
            
            "costo_reparar_min": 20000,
            "costo_reparar_max": 50000,
            
            "precio_venta_limpiar_min": 70000,
            "precio_venta_limpiar_max": 120000,
            
            "precio_venta_reparar_min": 120000,
            "precio_venta_reparar_max": 200000,
            
            "prob_venta_limpiar": 0.35,
            "prob_venta_reparar": 0.60,
            
            "tiempo_venta_dias": 12  # promedio
        }
        
        self.usuario_inputs = {}
    
    def obtener_inputs(self):
        """Obtener valores del usuario vía input"""
        print("\n" + "="*70)
        print("🪑 CONFIGURAR ANÁLISIS DE DECISIÓN - SILLÓN")
        print("="*70)
        print("\n💡 Presiona ENTER para usar valores por defecto\n")
        
        print("📊 COSTOS DE BOTADO:")
        val = input(f"Costo mínimo botado (default {self.defaults['costo_botado_min']}): ").strip()
        if val: self.usuario_inputs['costo_botado_min'] = int(val)
        
        val = input(f"Costo máximo botado (default {self.defaults['costo_botado_max']}): ").strip()
        if val: self.usuario_inputs['costo_botado_max'] = int(val)
        
        print("\n🧹 COSTOS DE LIMPIEZA:")
        val = input(f"Costo limpieza mínimo (default {self.defaults['costo_limpiar_min']}): ").strip()
        if val: self.usuario_inputs['costo_limpiar_min'] = int(val)
        
        val = input(f"Costo limpieza máximo (default {self.defaults['costo_limpiar_max']}): ").strip()
        if val: self.usuario_inputs['costo_limpiar_max'] = int(val)
        
        print("\n🔧 COSTOS DE REPARACIÓN:")
        val = input(f"Costo reparación mínimo (default {self.defaults['costo_reparar_min']}): ").strip()
        if val: self.usuario_inputs['costo_reparar_min'] = int(val)
        
        val = input(f"Costo reparación máximo (default {self.defaults['costo_reparar_max']}): ").strip()
        if val: self.usuario_inputs['costo_reparar_max'] = int(val)
        
        print("\n💰 PRECIOS DE VENTA (Solo Limpieza):")
        val = input(f"Precio venta mínimo (default {self.defaults['precio_venta_limpiar_min']}): ").strip()
        if val: self.usuario_inputs['precio_venta_limpiar_min'] = int(val)
        
        val = input(f"Precio venta máximo (default {self.defaults['precio_venta_limpiar_max']}): ").strip()
        if val: self.usuario_inputs['precio_venta_limpiar_max'] = int(val)
        
        print("\n💰 PRECIOS DE VENTA (Limpiar + Reparar):")
        val = input(f"Precio venta mínimo (default {self.defaults['precio_venta_reparar_min']}): ").strip()
        if val: self.usuario_inputs['precio_venta_reparar_min'] = int(val)
        
        val = input(f"Precio venta máximo (default {self.defaults['precio_venta_reparar_max']}): ").strip()
        if val: self.usuario_inputs['precio_venta_reparar_max'] = int(val)
        
        print("\n📈 PROBABILIDADES:")
        val = input(f"Prob. venta (solo limpiar) 0-1 (default {self.defaults['prob_venta_limpiar']}): ").strip()
        if val: self.usuario_inputs['prob_venta_limpiar'] = float(val)
        
        val = input(f"Prob. venta (limpiar+reparar) 0-1 (default {self.defaults['prob_venta_reparar']}): ").strip()
        if val: self.usuario_inputs['prob_venta_reparar'] = float(val)
    
    def obtener_valor(self, key: str, default=None):
        """Obtener valor: usuario > defaults"""
        if key in self.usuario_inputs:
            return self.usuario_inputs[key]
        return self.defaults.get(key, default)
    
    def generar_cpp_code(self) -> str:
        """Generar código C++ con parámetros actualizados"""
        
        template = f'''/**
 * @file sillon_decision_custom.cpp
 * @brief ANÁLISIS PERSONALIZADO DEL SILLÓN
 * 
 * Generado automáticamente con datos del usuario
 * Fecha: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
 */

#include "../src/unified_decision_framework.h"
#include <iomanip>

using namespace DecisionFramework;

int main() {{
    std::cout << "🪑 === DECISIÓN SILLÓN (ANÁLISIS PERSONALIZADO) ===\\n\\n";
    
    MonteCarloEngine mc_engine;
    mc_engine.setNumSimulations(10000);
    
    // Factores clave
    mc_engine.addFactor(Factor("Costo Neto", "Económico", 0.45, false));
    mc_engine.addFactor(Factor("Probabilidad Éxito", "Riesgo", 0.35, true));
    mc_engine.addFactor(Factor("Tiempo Resolución", "Velocidad", 0.20, false));
    
    // ========================================================================
    // OPCIÓN 1: BOTARLO
    // ========================================================================
    
    DecisionOption botar("1. Botar", "Pagar para que lo recojan");
    botar.addVariable("Costo Neto",
        UncertainVariable("costo", DistributionType::TRIANGULAR, 
            {self.obtener_valor('costo_botado_min')}, 
            {self.obtener_valor('costo_botado_promedio')}, 
            {self.obtener_valor('costo_botado_max')}));
    botar.addVariable("Probabilidad Éxito",
        UncertainVariable("prob", DistributionType::UNIFORM, 0.95, 1.0));
    botar.addVariable("Tiempo Resolución",
        UncertainVariable("tiempo", DistributionType::UNIFORM, 2, 5));
    botar.setSimulator([](const std::map<std::string, double>& values, std::mt19937& gen) {{
        SimulationResult result;
        result.factor_values = values;
        result.events["Éxito"] = true;
        result.success = true;
        return result;
    }});
    mc_engine.addOption(botar);
    
    // ========================================================================
    // OPCIÓN 2: SOLO LIMPIAR
    // ========================================================================
    
    DecisionOption limpiar("2. Solo Limpiar", "Limpieza profunda");
    limpiar.addVariable("Costo Neto",
        UncertainVariable("costo", DistributionType::TRIANGULAR,
            {self.obtener_valor('costo_limpiar_min')},
            {self.obtener_valor('costo_limpiar_promedio')},
            {self.obtener_valor('costo_limpiar_max')}));
    limpiar.addVariable("Probabilidad Éxito",
        UncertainVariable("prob", DistributionType::UNIFORM, 
            {max(0.2, self.obtener_valor('prob_venta_limpiar') - 0.05)}, 
            {min(0.9, self.obtener_valor('prob_venta_limpiar') + 0.05)}));
    limpiar.addVariable("Tiempo Resolución",
        UncertainVariable("tiempo", DistributionType::UNIFORM, 10, 20));
    limpiar.setSimulator([](const std::map<std::string, double>& values, std::mt19937& gen) {{
        SimulationResult result;
        result.factor_values = values;
        double prob = values.at("Probabilidad Éxito");
        std::bernoulli_distribution venta(prob);
        if (venta(gen)) {{
            std::uniform_real_distribution<> precio({self.obtener_valor('precio_venta_limpiar_min')}, 
                                                    {self.obtener_valor('precio_venta_limpiar_max')});
            double venta_precio = precio(gen);
            result.factor_values["Costo Neto"] = values.at("Costo Neto") - venta_precio;
            result.events["Se Vendió"] = true;
        }} else {{
            result.factor_values["Costo Neto"] = values.at("Costo Neto") + {self.obtener_valor('costo_botado_promedio')};
            result.events["No Se Vendió"] = true;
        }}
        result.success = true;
        return result;
    }});
    mc_engine.addOption(limpiar);
    
    // ========================================================================
    // OPCIÓN 3: LIMPIAR + REPARAR (RECOMENDADA)
    // ========================================================================
    
    DecisionOption reparar("3. Limpiar + Reparar", "Limpieza + reparación mecánica");
    reparar.addVariable("Costo Neto",
        UncertainVariable("costo", DistributionType::TRIANGULAR,
            {self.obtener_valor('costo_limpiar_min') + self.obtener_valor('costo_reparar_min')},
            {(self.obtener_valor('costo_limpiar_promedio') + (self.obtener_valor('costo_reparar_min') + self.obtener_valor('costo_reparar_max')) // 2) // 2},
            {self.obtener_valor('costo_limpiar_max') + self.obtener_valor('costo_reparar_max')}));
    reparar.addVariable("Probabilidad Éxito",
        UncertainVariable("prob", DistributionType::UNIFORM,
            {max(0.3, self.obtener_valor('prob_venta_reparar') - 0.05)},
            {min(0.9, self.obtener_valor('prob_venta_reparar') + 0.05)}));
    reparar.addVariable("Tiempo Resolución",
        UncertainVariable("tiempo", DistributionType::UNIFORM, 10, 25));
    reparar.setSimulator([](const std::map<std::string, double>& values, std::mt19937& gen) {{
        SimulationResult result;
        result.factor_values = values;
        double prob = values.at("Probabilidad Éxito");
        std::bernoulli_distribution venta(prob);
        if (venta(gen)) {{
            std::uniform_real_distribution<> precio({self.obtener_valor('precio_venta_reparar_min')},
                                                    {self.obtener_valor('precio_venta_reparar_max')});
            double venta_precio = precio(gen);
            result.factor_values["Costo Neto"] = values.at("Costo Neto") - venta_precio;
            result.events["Se Vendió"] = true;
        }} else {{
            result.factor_values["Costo Neto"] = values.at("Costo Neto") + {self.obtener_valor('costo_botado_promedio')};
            result.events["No Se Vendió"] = true;
        }}
        result.success = true;
        return result;
    }});
    mc_engine.addOption(reparar);
    
    // Ejecutar
    std::cout << "⚙️  Ejecutando 10,000 simulaciones...\\n\\n";
    auto results = mc_engine.run();
    
    std::cout << "📈 RESULTADOS:\\n";
    std::cout << std::string(70, '=') << "\\n";
    for (const auto& [name, stats] : results) {{
        std::cout << "\\n🎯 " << name << "\\n";
        std::cout << "   Score: " << std::fixed << std::setprecision(0) 
                  << stats.mean_score << " (±" << stats.score_stddev << ")\\n";
    }}
    
    return 0;
}}
'''
        return template
    
    def guardar_config(self, filename="sillon_config.json"):
        """Guardar configuración en JSON"""
        config = {
            "timestamp": datetime.now().isoformat(),
            "defaults": self.defaults,
            "usuario_inputs": self.usuario_inputs
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        
        return config
    
    def mostrar_resumen(self):
        """Mostrar resumen de la configuración"""
        print("\n" + "="*70)
        print("📊 RESUMEN DE PARÁMETROS UTILIZADOS")
        print("="*70 + "\n")
        
        print("💰 COSTO BOTADO:")
        print(f"  Rango: ${self.obtener_valor('costo_botado_min'):,} - ${self.obtener_valor('costo_botado_max'):,} CLP")
        print(f"  Promedio: ${self.obtener_valor('costo_botado_promedio'):,} CLP\n")
        
        print("🧹 COSTO LIMPIEZA:")
        print(f"  Rango: ${self.obtener_valor('costo_limpiar_min'):,} - ${self.obtener_valor('costo_limpiar_max'):,} CLP")
        print(f"  Promedio: ${self.obtener_valor('costo_limpiar_promedio'):,} CLP\n")
        
        print("🔧 COSTO REPARACIÓN:")
        print(f"  Rango: ${self.obtener_valor('costo_reparar_min'):,} - ${self.obtener_valor('costo_reparar_max'):,} CLP\n")
        
        print("💵 PRECIO VENTA (Solo Limpiar):")
        print(f"  Rango: ${self.obtener_valor('precio_venta_limpiar_min'):,} - ${self.obtener_valor('precio_venta_limpiar_max'):,} CLP\n")
        
        print("💵 PRECIO VENTA (Limpiar + Reparar):")
        print(f"  Rango: ${self.obtener_valor('precio_venta_reparar_min'):,} - ${self.obtener_valor('precio_venta_reparar_max'):,} CLP\n")
        
        print("📈 PROBABILIDADES:")
        print(f"  Prob. venta (solo limpiar): {self.obtener_valor('prob_venta_limpiar')*100:.1f}%")
        print(f"  Prob. venta (limpiar+reparar): {self.obtener_valor('prob_venta_reparar')*100:.1f}%\n")

def main():
    generator = SillonDecisionGenerator()
    
    print("\n" + "="*70)
    print("🪑 GENERADOR DE ANÁLISIS - DECISIÓN DEL SILLÓN")
    print("="*70)
    print("\nEste script genera un análisis personalizado basado en TUS DATOS")
    print("\nOpciones:")
    print("  1. Usar valores por defecto (recomendado para empezar)")
    print("  2. Ingresar tus propios valores")
    
    choice = input("\nElige opción (1 o 2): ").strip()
    
    if choice == "2":
        generator.obtener_inputs()
    
    # Mostrar resumen
    generator.mostrar_resumen()
    
    # Generar código C++
    print("\n✅ Generando código C++ personalizado...")
    cpp_code = generator.generar_cpp_code()
    
    # Guardar archivos
    with open("/Users/arturo/development/GitHub/desicion-maker/examples/sillon_decision_custom.cpp", 'w') as f:
        f.write(cpp_code)
    
    config = generator.guardar_config("/Users/arturo/development/GitHub/desicion-maker/sillon_config.json")
    
    print("✅ Archivo generado: examples/sillon_decision_custom.cpp")
    print("✅ Configuración guardada: sillon_config.json")
    
    print("\nCompila y ejecuta con:")
    print("  cd /Users/arturo/development/GitHub/desicion-maker")
    print("  g++ -std=c++17 -O2 examples/sillon_decision_custom.cpp -o bin/sillon_custom")
    print("  ./bin/sillon_custom")

if __name__ == "__main__":
    main()
