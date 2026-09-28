#!/usr/bin/env python3
"""
Calculadora de Diferencias: Santiago (Actualizado sin arriendo) vs Viña/Concón (Patmos x 2)
"""
import json


def calculate_decision():
    # Escenario 1: Santiago Actual (Según datos precisos del usuario)
    # Gasolina escolar: 70.000/semana -> 280.000/mes
    # Colegio + Jardin: 900.000/mes
    # Viajes Stgo-Viña (Lu y Mi = 8 viajes/mes). Peaje + Gasolina aprox 34.000/viaje -> 272.000/mes
    # TAG escolar/urbano estimado: 50.000/mes

    santiago = {
        "vivienda": 0,
        "colegio_y_jardin": 900000,
        "traslado_escolar_gasolina": 280000, # 70k semanal
        "traslado_escolar_tag_estimado": 50000,
        "traslado_stgo_vina": 272000, # 8 viajes x 34.000 (peajes+bencina)
        "traslado_tiempo_escolar": 20.0, # ~1 hr diaria x 20 dias
        "traslado_tiempo_stgo_vina": 28.0, # 8 viajes x 3.5 hrs
    }
    santiago["total_dinero"] = sum(v for k, v in santiago.items() if "tiempo" not in k)
    santiago["total_tiempo"] = santiago["traslado_tiempo_escolar"] + santiago["traslado_tiempo_stgo_vina"]

    # Escenario 2: Mudanza Viña (Patmos x 2, Casa Cerca, Trabajo Los Quillayes)
    mudanza = {
        "vivienda": 950000,
        "colegio": 720000, # 360k x 2 (Patmos)
        "traslado_diario_total": 70000, # bencina diaria a colegio cercano y Los Quillayes
        "traslado_tiempo_total": 15.0, # 45 min diarios total x 20 dias
    }
    mudanza["total_dinero"] = sum(v for k, v in mudanza.items() if "tiempo" not in k)
    mudanza["total_tiempo"] = mudanza["traslado_tiempo_total"]

    # Escenario 3: Mudanza 2027 (Trabajo Camino Intl)
    mudanza_2027 = {
        "vivienda": 950000,
        "colegio": 720000,
        "traslado_diario_total": 40000, # pique mas corto
        "traslado_tiempo_total": 8.0, # 25 min diarios total x 20 dias
    }
    mudanza_2027["total_dinero"] = sum(v for k, v in mudanza_2027.items() if "tiempo" not in k)
    mudanza_2027["total_tiempo"] = mudanza_2027["traslado_tiempo_total"]

    # Deltas (Mudanza - Santiago)
    delta_mudanza_dinero = mudanza["total_dinero"] - santiago["total_dinero"]
    delta_mudanza_tiempo = mudanza["total_tiempo"] - santiago["total_tiempo"]

    print(json.dumps({
        "santiago": santiago,
        "mudanza": mudanza,
        "mudanza_2027": mudanza_2027,
        "impacto_hoy": {"costo_extra": delta_mudanza_dinero, "tiempo_ahorrado": -delta_mudanza_tiempo}
    }, indent=2))

if __name__ == "__main__":
    calculate_decision()
