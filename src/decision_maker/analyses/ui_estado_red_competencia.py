"""
Decision Analysis - Diagnostico remoto: como se presenta el ESTADO DE LA RED al operador minero
Purpose: Elegir la vista principal de development simplificado (plan del 5-Oct-2026) frente a lo
         que ofrece la competencia en monitoreo de leaky feeder.
Created: 2026-10-05
Version: 1.0

EVIDENCIA (no son supuestos)
----------------------------
 C1. Becker Smartflow, modulo de monitoreo leaky feeder: «single line diagram online» en «3D Web
     interface», «immediate location of faults», alertas de atenuacion y tension por amplificador,
     medicion de distancias.            becker-mining.com/en/products/leaky-feeder-network-monitoring-module
 C2. PBE Centrian: «full reporting, geographical maps, diagnostics, and alarms»; integra a Vantage.
     No dice si el mapa es esquematico o geografico.        pbeaxell.com/products/data/leaky-feeder
 C3. Becker RNG-AMP / BSC-AMP: tension DC de linea, potencia RF de bajada y ganancia por web.
 U1. development YA tiene (verificado en origin/development):
       - primera falla en ORDEN DE SERIE + cuantos callaron despues (utils/cadenaVlad.js primeraFalla)
       - atribucion de la salida baja a LINEA vs AMPLIFICADOR por el AGC (veredictoSalida)
       - edad de cada dato (utils/frescura) y grupos = ramas (vlad_grupos)
       - lista por rama con detalle (GruposTabla.jsx + DetalleEquipoVlad.jsx)
 U2. Despliegue: un mini servidor por cliente, offline. Ninguna opcion depende de internet.
 U3. El mapa de planta (SmartTag, D3) entra igual en todas las opciones: es la fase 3 del plan.
     Lo que se decide aca es la vista de ESTADO, no si hay mapa.

SUPUESTOS (juicio, se marcan)
-----------------------------
 S1. tiempo_falla = segundos desde que el operador abre la vista hasta nombrar el equipo que fallo,
     con una rama de ~10 equipos. Juicio, no medido con operadores.
 S2. esfuerzo en dias-persona con agentes.
 S3. Escalas 0..10 para el resto.
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from decision_maker.core.models import DecisionOption, DistributionType, Factor, UncertainVariable
from decision_maker.core.orchestrator import UnifiedDecisionFramework

TRI = DistributionType.TRIANGULAR

factors = [
    Factor("paridad_competencia", weight=0.20, maximize=True),   # C1, C2
    Factor("tiempo_falla_s", weight=0.20, maximize=False),       # S1
    Factor("simplicidad_operador", weight=0.18, maximize=True),  # lo que pidio Arturo
    Factor("diferenciacion", weight=0.14, maximize=True),        # U1: lo que C1/C2 no declaran
    Factor("esfuerzo_dias", weight=0.10, maximize=False),        # S2
    Factor("reutilizacion", weight=0.10, maximize=True),         # U1
    Factor("uso_en_movil", weight=0.08, maximize=True),          # el tecnico en terreno
]


def opt(name, desc, **v):
    return DecisionOption(name=name, description=desc,
                          variables={k: UncertainVariable(k, TRI, list(t)) for k, t in v.items()})


options = [
    opt("A. Lista por rama",
        "VLAD General ampliado: una tabla por rama con las tres preguntas y la primera falla en el encabezado.",
        paridad_competencia=(4, 5, 6),      # sin unifilar: C1 lo vende
        tiempo_falla_s=(10, 15, 25),        # se lee el encabezado de la rama
        simplicidad_operador=(7, 8, 9),
        diferenciacion=(6, 7, 8),           # U1 completo, pero en texto
        esfuerzo_dias=(2, 3, 5),            # casi todo existe
        reutilizacion=(8, 9, 10),
        uso_en_movil=(7, 8, 9)),
    opt("B. Unifilar por rama",
        "Cada rama como diagrama: nodos en serie, color por estado, valores al pasar o tocar.",
        paridad_competencia=(7, 8, 9),      # iguala a C1 (sin el 3D)
        tiempo_falla_s=(5, 8, 15),          # el rojo se ve de un vistazo
        simplicidad_operador=(5, 6, 7.5),   # los valores quedan escondidos detras del hover
        diferenciacion=(5, 6, 7),           # la atribucion linea/amp no cabe en un nodo
        esfuerzo_dias=(6, 8, 12),
        reutilizacion=(4, 5, 6),
        uso_en_movil=(3, 4, 6)),            # un diagrama ancho no entra en un telefono
    opt("C. Lista por rama + franja unifilar",
        "Arriba de cada rama, una fila de nodos en serie con la primera falla marcada; abajo, la lista.",
        paridad_competencia=(7.5, 8.5, 9.5),
        tiempo_falla_s=(4, 7, 12),          # la franja dice DONDE, la lista dice POR QUE
        simplicidad_operador=(6.5, 7.5, 8.5),
        diferenciacion=(7.5, 8.5, 9.5),     # U1 visible y ademas en el diagrama
        esfuerzo_dias=(4, 5, 8),            # la franja sale de primeraFalla
        reutilizacion=(7, 8, 9),
        uso_en_movil=(6, 7, 8)),            # la franja se envuelve en filas
    opt("D. Solo el mapa",
        "El estado se lee en el mapa de planta (color por equipo); sin vista de lista.",
        paridad_competencia=(5, 6, 7),      # C2 tiene mapas
        tiempo_falla_s=(10, 20, 40),        # depende del plano y del zoom
        simplicidad_operador=(6, 7, 8),
        diferenciacion=(4, 5, 6),
        esfuerzo_dias=(4, 6, 9),
        reutilizacion=(5, 6, 7),
        uso_en_movil=(2, 3, 5)),
]


async def _run(fs, os_):
    fw = UnifiedDecisionFramework()
    for f in fs:
        fw.add_factor(f)
    for o in os_:
        fw.add_option(o)
    return await fw.run_analysis(mode="standard")


def _shock(base, name, mult):
    raw = {f.name: f.weight * (mult if f.name == name else 1.0) for f in base}
    tot = sum(raw.values())
    return [Factor(f.name, weight=raw[f.name] / tot, maximize=f.maximize) for f in base]


async def main():
    r = await _run(factors, options)
    ranked = sorted(r["mc_results"].items(), key=lambda kv: kv[1].mean_score, reverse=True)
    print("\n  RANKING — vista de estado de la red")
    for i, (n, st) in enumerate(ranked, 1):
        print(f"  {i}  {n:<40} p5={st.percentile_5:.3f} mean={st.mean_score:.3f} p95={st.percentile_95:.3f}")
    winner = ranked[0][0]
    print(f"\n  Estrategias: {r.get('strategies')}")
    print(f"  Pareto dominadas: {r.get('pareto', {}).get('dominated_options')}")
    print("\n  Shocks de peso (x2 / x0.25) que cambian al ganador:")
    flips = 0
    for f in factors:
        for mult in (2.0, 0.25):
            w = max((await _run(_shock(factors, f.name, mult), options))["mc_results"].items(),
                    key=lambda kv: kv[1].mean_score)[0]
            if w != winner:
                flips += 1
                print(f"    {f.name:<22} x{mult:<5} -> {w}")
    if not flips:
        print("    ninguno")


if __name__ == "__main__":
    asyncio.run(main())
