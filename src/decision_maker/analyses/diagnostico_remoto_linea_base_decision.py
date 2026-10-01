"""
Decision Analysis - Diagnostico remoto: sobre QUE LINEA se sigue construyendo
Purpose: development (Go + monitor-serial, 634 commits propios) se alejo de las lineas que se
         VENDEN: VHF (v4.1.1-fixed, tag v4.2.0) y su hermana UHF (ulad / uhf-v1.1.0, 250 commits
         propios). Decidir si se unifica, sobre cual base, o si se separan a proposito — sabiendo
         que cada cliente tiene SU mini servidor instalado.
Created: 2026-09-30
Last Updated: 2026-10-01
Version: 1.2

CAMBIOS v1.2 (01-Oct-2026): solo coherencia, ningun valor del modelo cambia. Purpose y las
descripciones de B, C2 y D seguian hablando de dos lineas con UHF como la vendida; H9 vuelve a su
lugar; la parte no medida de H11 pasa a supuesto (S6); type hints y multiplicadores de shock como
constantes. Resultado de la corrida v1.1 (30-Sep): gana E (MC 0.752, TOPSIS 0.837) y D segunda
(0.719). Cambia a D con costo_mantencion x0.25. En el escenario S4 «VLAD25 con fecha» E y D quedan
en el filo: sin semilla, una corrida dio D (30-Sep) y otra E (01-Oct). No es un ganador, es un empate.

CAMBIOS v1.1 (30-Sep-2026): la linea VENDIDA es VHF = rama v4.1.1-fixed, tag v4.2.0 (70fa4e16,
8-Sep-2026), no ulad. ulad/uhf-v1.x es su hermana UHF: las dos salen de v4.1.0 (29-Abr-2026). Son
TRES lineas, no dos. Se agrega la opcion E.

NEXT STEPS (lo que puede cambiar al ganador, en orden):
- [ ] Fecha de ID-1476 (S4): con fecha cercana E y D empatan; esa fecha decide entre las dos.
- [ ] Verificar S6 en un diag VHF: si los arreglos de H11 no importan en campo, E pierde su ventaja
      de calidad sobre B.
- [ ] Contar clientes instalados por linea (S2): hoy no alimenta ninguna variable.

HECHOS MEDIDOS EN EL REPO (git, 30-Sep-2026; no son supuestos)
--------------------------------------------------------------
 H1. Divergencia: merge-base 9ddacd36 (10-Mar-2026). 250 commits solo en uhf-v1.1.0, 634 solo en
     development.
 H2. Servicios no-frontend:
       UHF : backend Go (2.7 k loc, SOLO ruido/tinySA: /sweep, /alerts, 2 websockets)
             monitor Python (3.4 k) + legacy_shared_libs (6.4 k) -> polling LoRa, escribe rtData
             serial Go (4.6 k, tinySA) + redis + rabbitmq + mongo 4.4
       DEV : backend Go (12.7 k loc, 11.3 k de tests; ~60 rutas: vlad, vlad-telemetry,
             netreference, becker-varis, gateway, fota, system, email)
             monitor-serial Python (10.7 k, 13.8 k de tests) + serial Go + rabbitmq + mongo 4.4
     Tests fuera del frontend: UHF ~2.5 k loc, DEV ~25 k loc.
 H3. En UHF la logica de equipos vive EN EL FRONTEND: 36 rutas Next pages/api que leen y escriben
     Mongo directo (devices, rtData, users, roles, config, email_log, gateway_config, type).
     El backend Go de UHF no sabe nada de amplificadores.
 H4. En DEV el camino es monitor-serial -> RabbitMQ -> backend Go -> colecciones propias
     (vlad_measurements, vlad_telemetry_measurements, becker_varis_measurements, ...).
     NADIE en development escribe rtData, que es la coleccion que lee el frontend UHF.
 H5. development NO decodifica ULAD (las coincidencias de "ulad" son la palabra "acumulado").
     El ULAD es lo que emparejan los tags uhf-v1.0.0 / uhf-v1.1.0 (firmware ULAD v2.4.0).
 H6. Familias: UHF = ULAD, VLAD legacy rev23, ruido. DEV = VLAD legacy (paridad con el .112,
     con oraculo), VLAD25 telemetria, NetReference, Becker Varis, DRX pilot, SmartRing, ruido.
 H7. Frontend UHF: Next 11 + React 17 (sin soporte), 162 archivos. DEV: Next 15.5 + React 18.3.
 H8. 47 de los 250 commits UHF son de Ignacio Ulloa: regla vigente de no editar su codigo sin
     acordarlo con el.
 H9. Despliegue: un mini servidor por cliente (sin nube). Cada cambio de arquitectura es una
     migracion EN SITIO por cliente, con su Mongo y sus datos.
 H10. VHF v4.2.0 tiene la MISMA arquitectura que UHF (monitor Python, 35 pages/api, backend Go
      solo ruido, redis). Familias: VLAD, rev23, TG. Sin ULAD. Diverge de ulad en solo 11 commits
      (arreglos de grafico, socket, sesion y el split ttyS0/ttyS1) contra 100 de ulad.
 H11. v4.2.0 NO tiene arreglos que ulad/sync/112 si (y development por la paridad): largo de 2 B en
      set_attenuation (con 1 B el diag lee 0), es_ack (setAttenuation daba True sin mirar), y
      _level_dbm que con ref 0 daba 0 dBm. (Si afectan al diag VHF es S6, no un hecho.)

SUPUESTOS (juicio, NO medidos — son los que hay que corregir)
------------------------------------------------------------
 S1. Esfuerzos en persona-semanas de una persona con agentes, no de un equipo.
 S2. La cantidad de clientes instalados con la linea UHF es > 1 y < 10.
 S3. La auth (usuarios/roles) de UHF vive en pages/api; el backend Go de DEV no tiene auth
     Observado en el banco .140, no verificado en el codigo de ninguna de las lineas: por eso es
     supuesto y no hecho.
 S4. ID-1476 «VLAD REV25 300 unidades» necesita que el software VENDIDO muestre VLAD25 en algun
     momento; no se sabe cuando. Es el shock mas importante: ver el escenario «VLAD25 con fecha»
     al final de main().
 S5. Escalas 0..10 para riesgo, foco, calidad, cobertura, reversibilidad.
 S6. Los arreglos que le faltan a v4.2.0 (H11) afectan al diag VHF en campo. SIN VERIFICAR: si no
     lo afectan, la ventaja de calidad de E sobre B se achica.
"""

import asyncio
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent.parent))

from decision_maker.core.models import DecisionOption, DistributionType, Factor, UncertainVariable
from decision_maker.core.orchestrator import UnifiedDecisionFramework

TRI = DistributionType.TRIANGULAR

# Shocks de sensibilidad: cada peso se duplica y se reduce a un cuarto, uno por vez.
WEIGHT_SHOCKS: tuple[float, ...] = (2.0, 0.25)
# Escenario S4: si el VLAD25 tiene fecha, la cobertura pesa el triple y el plazo la mitad.
S4_COVERAGE_MULT = 3.0
S4_DEADLINE_MULT = 0.5

factors = [
    Factor("semanas_a_vender", weight=0.20, maximize=False),       # hasta el proximo cliente
    Factor("riesgo_instalados", weight=0.18, maximize=False),      # romper un mini servidor en sitio
    Factor("costo_mantencion", weight=0.15, maximize=False),       # carga continua, 0..10
    Factor("cobertura_producto", weight=0.12, maximize=True),      # familias que atiende
    Factor("persona_semanas", weight=0.12, maximize=False),        # esfuerzo total
    Factor("calidad_verificable", weight=0.10, maximize=True),     # tests y oraculos
    Factor("foco_gerencial", weight=0.08, maximize=True),          # una historia clara
    Factor("reversibilidad", weight=0.05, maximize=True),
]


def opt(name: str, desc: str, **v: tuple[float, float, float]) -> DecisionOption:
    return DecisionOption(
        name=name,
        description=desc,
        variables={k: UncertainVariable(k, TRI, list(t)) for k, t in v.items()},
    )


options = [
    opt(
        "A. Todo a development",
        "Portar ULAD a DEV, rehacer la UX UHF en el frontend DEV, migrar cada cliente.",
        semanas_a_vender=(8, 12, 20),       # H5: ULAD no existe en DEV; H4: sin rtData
        riesgo_instalados=(6, 7.5, 9),      # H9: arquitectura y colecciones distintas por cliente
        costo_mantencion=(3, 4, 6),         # una linea, pero la grande
        cobertura_producto=(8, 9, 10),
        persona_semanas=(10, 14, 22),
        calidad_verificable=(7, 8, 9),      # H2: 25 k loc de tests
        foco_gerencial=(3, 4, 6),           # sigue la expansion que ya se fue de las manos
        reversibilidad=(3, 4, 6),
    ),
    opt(
        "B. Volver a UHF y congelar development",
        "La arquitectura vendida (VHF v4.2.0 / UHF ulad) es la base; DEV queda en git y se porta solo lo que un cliente pague.",
        semanas_a_vender=(0, 1, 3),
        riesgo_instalados=(1, 2, 3.5),
        costo_mantencion=(4, 5.5, 7),       # H7: Next 11/React 17 sin soporte, H2: pocos tests
        cobertura_producto=(3, 4, 5.5),     # H6: sin VLAD25, NetReference, Becker
        persona_semanas=(1, 2, 4),
        calidad_verificable=(3, 4.5, 6),
        foco_gerencial=(8, 9, 10),
        reversibilidad=(6, 7, 8),
    ),
    opt(
        "C. Backend DEV + frontend nuevo con la UX UHF (de una vez)",
        "Lo que se propuso: reemplazar monitor Python + 36 pages/api UHF por DEV, frontend nuevo.",
        semanas_a_vender=(10, 16, 26),      # H3 + H5 + S3: ULAD, rtData, auth, 36 rutas
        riesgo_instalados=(5, 6.5, 8.5),    # misma cara, camino de datos entero nuevo
        costo_mantencion=(2.5, 3.5, 5),
        cobertura_producto=(8, 9, 10),
        persona_semanas=(14, 20, 30),
        calidad_verificable=(6.5, 7.5, 9),
        foco_gerencial=(5, 6.5, 8),
        reversibilidad=(4, 5, 6),
    ),
    opt(
        "C2. Estrangulamiento: UHF vende, DEV reemplaza pieza por pieza",
        "VHF y UHF siguen siendo el producto; cada pieza pasa a DEV solo con oraculo de paridad contra ellas.",
        semanas_a_vender=(0, 1, 3),
        riesgo_instalados=(2, 3, 4.5),      # un cambio por release, cada uno reversible
        costo_mantencion=(4, 5, 6.5),       # dos lineas durante la transicion
        cobertura_producto=(6, 7.5, 9),
        persona_semanas=(12, 18, 28),       # igual que C, pero repartido
        calidad_verificable=(6, 7, 8.5),
        foco_gerencial=(6, 7, 8.5),
        reversibilidad=(7, 8, 9),
    ),
    opt(
        "D. Dos lineas por producto, a proposito",
        "VHF v4.2.0 y UHF ulad = producto en mantenimiento; DEV = VLAD25/banco. Solo contratos y decoders comunes.",
        semanas_a_vender=(0, 1, 3),
        riesgo_instalados=(1, 2, 3.5),
        costo_mantencion=(6, 7, 8.5),       # H10: son TRES lineas, cada arreglo se hace tres veces
        cobertura_producto=(7, 8, 9),       # cada producto cubre lo suyo
        persona_semanas=(3, 5, 8),
        calidad_verificable=(5.5, 6.5, 8),
        foco_gerencial=(6.5, 7.5, 9),
        reversibilidad=(7, 8, 9),
    ),
    opt(
        "E. Una linea de producto VHF+UHF; development queda de laboratorio",
        "Llevar los 11 commits de v4.2.0 a ulad (misma arquitectura), vender VHF y UHF desde ahi.",
        semanas_a_vender=(0.5, 1.5, 3),     # H10: 11 commits sobre la misma arquitectura
        riesgo_instalados=(1.5, 2.5, 4),    # cliente VHF actualiza a ulad; guarda ULAD por contenido
        costo_mantencion=(3.5, 4.5, 6),     # una linea de producto + un laboratorio
        cobertura_producto=(6, 7, 8),       # VHF + UHF + ruido; VLAD25 sigue en development
        persona_semanas=(1, 2, 4),
        calidad_verificable=(4.5, 5.5, 7),  # H11: hereda los arreglos y los tests de ulad (S6)
        foco_gerencial=(7.5, 8.5, 9.5),
        reversibilidad=(6.5, 7.5, 8.5),
    ),
]


async def _run(fs: list[Factor], os_: list[DecisionOption]) -> dict[str, Any]:
    fw = UnifiedDecisionFramework()
    for f in fs:
        fw.add_factor(f)
    for o in os_:
        fw.add_option(o)
    return await fw.run_analysis(mode="standard")


def _shock(base: list[Factor], name: str, mult: float) -> list[Factor]:
    raw = {f.name: f.weight * (mult if f.name == name else 1.0) for f in base}
    tot = sum(raw.values())
    return [Factor(f.name, weight=raw[f.name] / tot, maximize=f.maximize) for f in base]


async def main() -> None:
    r = await _run(factors, options)
    mc = r["mc_results"]
    topsis = r.get("topsis_scores")
    ranked = sorted(mc.items(), key=lambda kv: kv[1].mean_score, reverse=True)
    print("\n  RANKING — sobre que linea seguir")
    print(f"  {'#':<3} {'Opcion':<62} {'p5':>7} {'mean':>7} {'p95':>7} {'TOPSIS':>7}")
    for i, (n, st) in enumerate(ranked, 1):
        t = float(topsis.get(n, float("nan"))) if topsis is not None and len(topsis) else float("nan")
        print(f"  {i:<3} {n[:62]:<62} {st.percentile_5:>7.3f} {st.mean_score:>7.3f} "
              f"{st.percentile_95:>7.3f} {t:>7.3f}")
    winner = ranked[0][0]
    print(f"\n  Ganador (media MC): {winner}")
    print(f"  Estrategias: {r.get('strategies')}")
    print(f"  Pareto dominadas: {r.get('pareto', {}).get('dominated_options')}")

    print(f"\n  Shocks de peso ({' / '.join(f'x{m:g}' for m in WEIGHT_SHOCKS)}) que CAMBIAN al ganador:")
    flips = 0
    for f in factors:
        for mult in WEIGHT_SHOCKS:
            w = max((await _run(_shock(factors, f.name, mult), options))["mc_results"].items(),
                    key=lambda kv: kv[1].mean_score)[0]
            if w != winner:
                flips += 1
                print(f"    {f.name:<22} x{mult:<5} -> {w}")
    if not flips:
        print("    ninguno")

    # S4: si el VLAD25 tiene fecha, la cobertura deja de ser un criterio de 12 %.
    urg = _shock(_shock(factors, "cobertura_producto", S4_COVERAGE_MULT), "semanas_a_vender", S4_DEADLINE_MULT)
    w = max((await _run(urg, options))["mc_results"].items(), key=lambda kv: kv[1].mean_score)[0]
    print(f"\n  Escenario 'VLAD25 con fecha' (cobertura x{S4_COVERAGE_MULT:g}, "
          f"plazo x{S4_DEADLINE_MULT:g}): gana {w}")


if __name__ == "__main__":
    asyncio.run(main())
