#!/usr/bin/env python3
"""
Comparativa Cualitativa y Cuantitativa: Viña (Patmos) vs Concón (Colegio Local)
Incluye modelado del impacto logístico y red de apoyo según las edades de los hijos.
"""
import json


def calcular_penalizacion_por_edad(edades):
    """
    Calcula un sobrecosto y penalización de utilidad basado en cuán pequeños son los niños.
    Niños menores a 7 años tienen alta probabilidad de enfermedades (virus de jardín)
    y emergencias de salida temprana.
    """
    factor_riesgo = 0
    for edad in edades:
        if edad <= 4:
            factor_riesgo += 0.5  # Muy alta dependencia (Ej. 3 años)
        elif edad <= 7:
            factor_riesgo += 0.3  # Alta dependencia (Ej. 5 años)
        else:
            factor_riesgo += 0.1  # Independencia básica

    # El riesgo se traduce en un sobrecosto estimado mensual (ej. niñera de urgencia,
    # perder medio día de trabajo, transporte imprevisto) si no hay red de apoyo cerca.
    costo_urgencia_mensual_base = 150000
    return factor_riesgo, int(costo_urgencia_mensual_base * factor_riesgo)

def calculate():
    # Parámetros del modelo
    edades_hijos = [3, 5]
    costo_mudanza_inicial = 300000

    factor_riesgo, costo_urgencias = calcular_penalizacion_por_edad(edades_hijos)

    # Escenario 1: Viña del Mar (Colegio Patmos) - Red de apoyo (Abuelos) cerca
    # Asumimos que los abuelos absorben el 100% de este costo/riesgo.
    vina_patmos = {
        "vivienda": 900000,
        "colegio": 720000,
        "traslado_trabajo": 60000,
        "costo_urgencias_infantiles": 0, # Absorbed by grandparents
        "red_apoyo": 100,
        "entorno_playa": 50,
        "tiempo_traslado_trabajo": 15,
    }
    vina_patmos["total_mensual"] = vina_patmos["vivienda"] + vina_patmos["colegio"] + vina_patmos["traslado_trabajo"] + vina_patmos["costo_urgencias_infantiles"]

    # Escenario 2: Concón (Colegio tipo Alcántara/Altazor) - Red de apoyo lejos
    # Al estar lejos, se asume el impacto completo del riesgo logístico.
    concon_colegio = {
        "vivienda": 1100000,
        "colegio": 720000,
        "traslado_trabajo": 30000,
        "costo_urgencias_infantiles": costo_urgencias, # Penalización aplicada
        "red_apoyo": 30,
        "entorno_playa": 100,
        "tiempo_traslado_trabajo": 5,
    }
    concon_colegio["total_mensual"] = concon_colegio["vivienda"] + concon_colegio["colegio"] + concon_colegio["traslado_trabajo"] + concon_colegio["costo_urgencias_infantiles"]

    # Generar salida
    output = {
        "parametros": {
            "edades_hijos": edades_hijos,
            "costo_inicial_mudanza": costo_mudanza_inicial,
            "factor_riesgo_logistico": factor_riesgo
        },
        "opciones": {
            "vina_patmos_con_abuelos": vina_patmos,
            "concon_colegio_sin_abuelos": concon_colegio
        },
        "conclusion": "Viña del Mar es la opcion ganadora" if vina_patmos["total_mensual"] < concon_colegio["total_mensual"] else "Concon es la opcion ganadora"
    }

    print(json.dumps(output, indent=2))

if __name__ == "__main__":
    calculate()
