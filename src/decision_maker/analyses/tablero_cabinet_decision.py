#!/usr/bin/env python3
"""
Título: Análisis de Decisión - Preparación Profesional del Tablero de Seguridad
Propósito: Decidir la mejor estrategia para completar etiquetado, diagrama unlineal
           y cableado del tablero eléctrico/seguridad, bajo restricciones de tiempo,
           costo, y experiencia.
Fecha de Creación: 2026-08-17
Versión: 1.0

CONTEXTO:
- Tablero físicamente armado
- FALTA: etiquetado, diagrama unlineal, posibilidad de cambio de cableado
- Equipo NUNCA ha hecho diagrama ni etiquetado antes
- Técnico armador en Valparaíso (disponibilidad desconocida)
- Deadline suave: viernes 21 agosto (entrega al cliente)
- Deadline real: septiembre (inicio de uso)
- Hoy es lunes 17 agosto 2026

VENTANAS DE TIEMPO:
- Mar 18: en Viña del Mar
- Mié 19: en Viña del Mar
- Jue 20: de vuelta en Santiago, medio tiempo
- Vie 21: deadline suave cliente
- Sept: deadline real

METODOLOGÍAS:
- Monte Carlo Simulation (10,000 iteraciones)
- TOPSIS (ranking multi-criterio)
- PROMETHEE II (outranking con incertidumbre)
- Análisis de sensibilidad
- Teoría de decisión (Maximax, Maximin, Hurwicz, Laplace)
- Robustez bajo shocks de pesos

CREADO POR: Decision Maker Framework v3.0
"""

import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from decision_maker.core.models import DecisionOption, DistributionType, Factor, UncertainVariable
from decision_maker.core.orchestrator import UnifiedDecisionFramework

# ============================================================
# METADATA
# ============================================================

analysis_name = "Tablero Cabinet - Estrategia de Preparación"
analysis_date = datetime.now().isoformat()

# ============================================================
# FACTORES / CRITERIOS
# ============================================================
#
# 1. Costo (minimizar): inversión total estimada en CLP
# 2. Calidad/Cumplimiento (maximizar): profesionalismo, cumplimiento normativo (0-100)
# 3. Rapidez (maximizar): qué tan rápido queda listo en días (0-100)
# 4. Riesgo (minimizar): probabilidad de resultado negativo (0-100, 0=sin riesgo)
# 5. Aprendizaje (maximizar): capacidad construida para futuros tableros (0-100)
#
# Pesos reflejan prioridades:
# - Calidad alta porque es seguridad eléctrica (normativa)
# - Costo importante pero no fundamental
# - Rapidez media (deadline suave viernes, real en septiembre)
# - Riesgo medio (un tablero mal hecho puede ser peligroso)
# - Aprendizaje bajo pero positivo (habilidad futura)

factors = [
    Factor(name="Costo", weight=0.20, maximize=False),
    Factor(name="Calidad", weight=0.30, maximize=True),
    Factor(name="Rapidez", weight=0.15, maximize=True),
    Factor(name="Riesgo", weight=0.25, maximize=False),
    Factor(name="Aprendizaje", weight=0.10, maximize=True),
]

# ============================================================
# OPCIONES / ALTERNATIVAS
# ============================================================
#
# A) Hacerlo yo mismo (sin experiencia, progreso avanzado)
# B) Contratar externo profesional
# C) Técnico original de Valparaíso
# D) Híbrido: yo hago lo que puedo, externo revisa/completa partes críticas
# E) Auto-capacitación rápida + hacerlo todo

# --- Escala de Costos (CLP) ---
# Materiales básicos: ~30,000-50,000
# Externo local (Santiago): ~150,000-350,000
# Técnico + viático Valparaíso: ~100,000-250,000
# Híbrido: materiales + revisión externa: ~80,000-180,000

# --- Escala de Calidad (0-100) ---
# 100 = cumple normativa, diagrama profesional, etiquetado completo
# 70-80 = profesional con experiencia
# 40-60 = aceptable pero con errores posibles
# 20-40 = riesgo de no cumplir normativa

# --- Escala de Rapidez (0-100) ---
# 100 = listo en 1 día
# 70-80 = 2-3 días
# 40-60 = 4-5 días
# 20-30 = más de una semana

# ── Normalización de Costo a escala 0-100 ──
# 0 = costo más alto (400k CLP = peor) → 100 = costo más bajo (20k CLP = mejor)
# Fórmula: score = 100 * (1 - (costo - min_ref) / (max_ref - min_ref))
# Donde min_ref=20000, max_ref=400000
COST_MIN_REF = 20000.0
COST_MAX_REF = 400000.0

def _cost_score(low: float, mode: float, high: float) -> list[float]:
    """Convierte costos CLP a scores 0-100 (100=barato)."""
    def _norm(v: float) -> float:
        return max(0.0, min(100.0, 100.0 * (1.0 - (v - COST_MIN_REF) / (COST_MAX_REF - COST_MIN_REF))))
    return [_norm(low), _norm(mode), _norm(high)]

options = [
    # ── OPCIÓN A: Hacerlo yo mismo ──
    DecisionOption(
        name="A) Hago yo (DIY)",
        description=(
            "Hacer etiquetado y diagrama sin experiencia previa. "
            "Progreso avanzado en algunas áreas. Riesgo de errores normativos."
        ),
        variables={
            # Costo: solo materiales (~20-70k CLP → score ~82-95)
            "Costo": UncertainVariable(
                "Costo", DistributionType.TRIANGULAR, _cost_score(20000, 40000, 70000)
            ),
            # Calidad: alta incertidumbre, sin experiencia
            "Calidad": UncertainVariable(
                "Calidad", DistributionType.TRIANGULAR, [20, 45, 70]
            ),
            # Rapidez: disponible miércoles y jueves, pero inexperiencia ralentiza
            "Rapidez": UncertainVariable(
                "Rapidez", DistributionType.TRIANGULAR, [30, 50, 70]
            ),
            # Riesgo: alto (puede quedar mal, no cumplir norma)
            "Riesgo": UncertainVariable(
                "Riesgo", DistributionType.TRIANGULAR, [40, 65, 85]
            ),
            # Aprendizaje: alto (aprendes mucho haciendo)
            "Aprendizaje": UncertainVariable(
                "Aprendizaje", DistributionType.TRIANGULAR, [60, 80, 95]
            ),
        },
    ),

    # ── OPCIÓN B: Contratar externo profesional ──
    DecisionOption(
        name="B) Externo profesional",
        description=(
            "Contratar electricista/ingeniero externo en Santiago. "
            "Calidad garantizada, pero costo mayor y disponibilidad incierta."
        ),
        variables={
            # Costo: profesional + materiales (150-400k CLP → score ~0-66)
            "Costo": UncertainVariable(
                "Costo", DistributionType.TRIANGULAR, _cost_score(150000, 250000, 400000)
            ),
            # Calidad: profesional con experiencia
            "Calidad": UncertainVariable(
                "Calidad", DistributionType.TRIANGULAR, [75, 88, 98]
            ),
            # Rapidez: rápido si hay disponibilidad (2-4 días)
            "Rapidez": UncertainVariable(
                "Rapidez", DistributionType.TRIANGULAR, [55, 75, 90]
            ),
            # Riesgo: bajo (profesional con experiencia)
            "Riesgo": UncertainVariable(
                "Riesgo", DistributionType.TRIANGULAR, [5, 15, 30]
            ),
            # Aprendizaje: bajo (solo supervisas)
            "Aprendizaje": UncertainVariable(
                "Aprendizaje", DistributionType.TRIANGULAR, [10, 25, 40]
            ),
        },
    ),

    # ── OPCIÓN C: Técnico original de Valparaíso ──
    DecisionOption(
        name="C) Técnico Valparaíso",
        description=(
            "El técnico que armó el tablero viene de Valparaíso. "
            "Conoce el armado pero disponibilidad y viáticos son inciertos."
        ),
        variables={
            # Costo: viáticos + trabajo (100-280k CLP → score ~32-74)
            "Costo": UncertainVariable(
                "Costo", DistributionType.TRIANGULAR, _cost_score(100000, 180000, 280000)
            ),
            # Calidad: conoce el armado pero puede no ser experto en diagramas
            "Calidad": UncertainVariable(
                "Calidad", DistributionType.TRIANGULAR, [60, 75, 90]
            ),
            # Rapidez: BAJA - disponibilidad desconocida, viaje Viña→Santiago
            "Rapidez": UncertainVariable(
                "Rapidez", DistributionType.TRIANGULAR, [15, 40, 65]
            ),
            # Riesgo: medio (depende de disponibilidad, puede no llegar)
            "Riesgo": UncertainVariable(
                "Riesgo", DistributionType.TRIANGULAR, [25, 45, 70]
            ),
            # Aprendizaje: medio (puedes aprender viéndolo)
            "Aprendizaje": UncertainVariable(
                "Aprendizaje", DistributionType.TRIANGULAR, [30, 50, 70]
            ),
        },
    ),

    # ── OPCIÓN D: Híbrido (yo + externo revisa) ──
    DecisionOption(
        name="D) Híbrido (yo + revisión)",
        description=(
            "Hago lo que puedo (etiquetado básico, preparación), luego un externo "
            "revisa las partes críticas (diagrama, cumple normativa). Balance costo/calidad."
        ),
        variables={
            # Costo: materiales + tarifa reducida de revisión (70-190k CLP → score ~50-82)
            "Costo": UncertainVariable(
                "Costo", DistributionType.TRIANGULAR, _cost_score(70000, 120000, 190000)
            ),
            # Calidad: buena (trabajo propio + revisión experta)
            "Calidad": UncertainVariable(
                "Calidad", DistributionType.TRIANGULAR, [65, 80, 93]
            ),
            # Rapidez: moderada (depende de coordinación)
            "Rapidez": UncertainVariable(
                "Rapidez", DistributionType.TRIANGULAR, [45, 65, 82]
            ),
            # Riesgo: bajo-medio (revisión mitiga errores críticos)
            "Riesgo": UncertainVariable(
                "Riesgo", DistributionType.TRIANGULAR, [10, 25, 45]
            ),
            # Aprendizaje: alto (haces + aprendes de la revisión)
            "Aprendizaje": UncertainVariable(
                "Aprendizaje", DistributionType.TRIANGULAR, [55, 75, 90]
            ),
        },
    ),

    # ── OPCIÓN E: Auto-capacitación rápida + hacerlo todo ──
    DecisionOption(
        name="E) Capacitación + DIY",
        description=(
            "Investigar normativa y técnicas (1-2 días), luego ejecutar todo. "
            "Más tiempo total pero mejor resultado que DIY puro. "
            "Usa martes-miércoles en Viña para estudiar, jueves-viernes ejecutar."
        ),
        variables={
            # Costo: materiales + cursos/referencias (35-95k CLP → score ~75-91)
            "Costo": UncertainVariable(
                "Costo", DistributionType.TRIANGULAR, _cost_score(35000, 55000, 95000)
            ),
            # Calidad: mejor que DIY puro, peor que profesional
            "Calidad": UncertainVariable(
                "Calidad", DistributionType.TRIANGULAR, [45, 65, 82]
            ),
            # Rapidez: MENOR - 1-2 días estudio + ejecución
            "Rapidez": UncertainVariable(
                "Rapidez", DistributionType.TRIANGULAR, [25, 45, 65]
            ),
            # Riesgo: medio (mejor preparado pero sin experiencia real)
            "Riesgo": UncertainVariable(
                "Riesgo", DistributionType.TRIANGULAR, [25, 40, 60]
            ),
            # Aprendizaje: muy alto (estudias + aplicas)
            "Aprendizaje": UncertainVariable(
                "Aprendizaje", DistributionType.TRIANGULAR, [70, 88, 98]
            ),
        },
    ),
]

# ============================================================
# EJECUCIÓN DEL ANÁLISIS
# ============================================================

async def main():
    print("\n" + "=" * 72)
    print("   ANÁLISIS DECISIONAL: PREPARACIÓN PROFESIONAL DEL TABLERO")
    print("   Fecha:", analysis_date)
    print("=" * 72)

    print("\n📋 CONTEXTO:")
    print("   • Tablero armado, falta etiquetado + diagrama unlineal")
    print("   • Equipo sin experiencia en diagramas/etiquetado")
    print("   • Deadline suave: viernes 21 ago | Real: septiembre 2026")
    print("   • Ubicación: en Santiago (jue-vie), en Viña (mar-mié)")

    print("\n📐 CRITERIOS Y PESOS:")
    for f in factors:
        dir_str = "maximizar" if f.maximize else "minimizar"
        print(f"   • {f.name}: peso={f.weight:.0%} ({dir_str})")

    print(f"\n🔄 Opciones a evaluar: {len(options)}")
    for o in options:
        print(f"   • {o.name}: {o.description[:70]}...")

    # Crear framework
    fw = UnifiedDecisionFramework()

    for f in factors:
        fw.add_factor(f)
    for o in options:
        fw.add_option(o)

    # ── EJECUTAR ANÁLISIS ESTÁNDAR (Monte Carlo + TOPSIS + PROMETHEE + Sensitivity) ──
    print("\n" + "=" * 72)
    print("   EJECUTANDO ANÁLISIS ESTÁNDAR")
    print("=" * 72 + "\n")

    results = await fw.run_analysis(mode="standard")

    # ── EJECUTAR ANÁLISIS AVANZADO (Bayesian + Bootstrap + Genetic) ──
    print("\n" + "=" * 72)
    print("   EJECUTANDO ANÁLISIS AVANZADO")
    print("=" * 72 + "\n")

    fw2 = UnifiedDecisionFramework()
    for f in factors:
        fw2.add_factor(f)
    for o in options:
        fw2.add_option(o)

    results_adv = await fw2.run_analysis(mode="advanced")

    # ── RESUMEN EJECUTIVO ──
    print("\n" + "=" * 72)
    print("   RESUMEN EJECUTIVO")
    print("=" * 72)

    if results.get("mc_results"):
        print("\n📊 Monte Carlo - Estadísticas por opción:")
        print(f"   {'Opción':<30} {'Media':>8} {'P5':>8} {'P95':>8} {'StdDev':>8}")
        print("   " + "-" * 62)
        for name, stats in results["mc_results"].items():
            print(f"   {name:<30} {stats.mean_score:>8.1f} {stats.percentile_5:>8.1f} "
                  f"{stats.percentile_95:>8.1f} {stats.std_dev:>8.1f}")

    if results.get("topsis_scores") is not None and not results["topsis_scores"].empty:
        print("\n🏆 TOPSIS - Ranking:")
        for rank, (name, score) in enumerate(results["topsis_scores"].items(), 1):
            emoji = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else "  "
            print(f"   {emoji} #{rank} {name}: {score:.4f}")

    if results.get("strategies"):
        print("\n🎯 Teoría de Decisión:")
        for strat_name, strat_data in results["strategies"].items():
            if isinstance(strat_data, dict):
                winner = strat_data.get("best_option", "N/A")
                print(f"   • {strat_name}: {winner}")
            else:
                print(f"   • {strat_name}: {strat_data}")

    if results.get("sensitivity"):
        print("\n📈 Análisis de Sensibilidad:")
        for factor_name, sens_data in results["sensitivity"].items():
            if isinstance(sens_data, dict) and sens_data:
                print(f"   • Sensibilidad a '{factor_name}':")
                for opt_name, val in list(sens_data.items())[:5]:
                    try:
                        print(f"     - {opt_name}: {float(val):.4f}")
                    except (TypeError, ValueError):
                        print(f"     - {opt_name}: {val}")
            elif sens_data:
                print(f"   • {factor_name}: {sens_data}")

    if results_adv.get("future"):
        future = results_adv["future"]
        if "bayesian_probs" in future:
            print("\n🧮 Probabilidades Bayesianas (opción óptima):")
            for name, prob in future["bayesian_probs"].items():
                print(f"   • {name}: {prob:.1%}")

        if "rank_aggregation" in future:
            print("\n🗳️  Agregación Borda (consenso multi-método):")
            for name, score in future["rank_aggregation"].items():
                try:
                    print(f"   • {name}: {float(score):.2f}")
                except (TypeError, ValueError):
                    print(f"   • {name}: {score}")

        if "bootstrap_ci" in future:
            print("\n📊 Intervalos de Confianza (Bootstrap):")
            for name, ci in future["bootstrap_ci"].items():
                print(f"   • {name}: {ci}")

    if results.get("uncertainty"):
        unc = results["uncertainty"]
        if "confidence_weighted_winner" in unc:
            cw = unc["confidence_weighted_winner"]
            if isinstance(cw, dict):
                print(f"\n🎯 Ganador por confianza ponderada: {cw.get('winner', 'N/A')}")
                print(f"   Score: {cw.get('score', 0):.2f} | Confianza: {cw.get('confidence', 0):.1%}")
                print(f"   Ventaja sobre segundo: {cw.get('edge', 0):.2f} pts")
                print(f"   Segundo: {cw.get('runner_up', 'N/A')}")
            else:
                print(f"\n🎯 Ganador por confianza ponderada: {cw}")
        if "ranking_confidence" in unc:
            rc = unc["ranking_confidence"]
            if isinstance(rc, dict):
                print("   Confianza en ranking:")
                for name, conf in rc.items():
                    if isinstance(conf, dict):
                        print(f"   • {name}: rank {conf.get('mean_rank', '?')} "
                              f"(CI: {conf.get('ci_low', '?')}-{conf.get('ci_high', '?')})")
                    else:
                        try:
                            print(f"   • {name}: {float(conf):.1%}")
                        except (TypeError, ValueError):
                            print(f"   • {name}: {conf}")

    # ── GUARDAR RESULTADOS ──
    output_dir = Path(__file__).parent.parent.parent.parent / "results"
    output_dir.mkdir(exist_ok=True)

    output_file = output_dir / "tablero_cabinet_decision.json"
    serializable_results = {}
    for key, val in results.items():
        try:
            json.dumps(val)
            serializable_results[key] = val
        except (TypeError, ValueError):
            serializable_results[key] = str(val)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump({
            "name": analysis_name,
            "date": analysis_date,
            "results": serializable_results,
        }, f, indent=2, ensure_ascii=False, default=str)

    print(f"\n💾 Resultados guardados en: {output_file}")
    print("\n" + "=" * 72)

    return results


if __name__ == "__main__":
    asyncio.run(main())
