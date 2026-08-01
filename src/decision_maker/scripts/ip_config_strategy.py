#!/usr/bin/env python3
"""
🎯 ANÁLISIS: Estrategia para actualizar IP en frontend instalado directamente en Ubuntu
Contexto: Frontend Next.js sin Docker, Ubuntu + netplan, IP de la máquina cambia.
Usando el framework de decisiones con 13 metodologías + Gemini IA
"""

import sys
from pathlib import Path

# Add core to path
sys.path.insert(0, str(Path(__file__).parent.parent / "core"))

import asyncio
import os

from deep_research_decision_agent import CareerOption, DecisionAnalysisEngine
from dotenv import load_dotenv

# Cargar tanto .env como .env.gemini (el framework usa .env.gemini para la API key)
_base = Path(__file__).parent.parent
load_dotenv(_base / ".env")
load_dotenv(_base / ".env.gemini", override=True)

def create_ip_strategy_options() -> list[CareerOption]:
    """
    Las 5 estrategias para manejar el cambio de IP en un frontend
    instalado directamente en Ubuntu (sin Docker) con netplan.

    Mapeo de campos CareerOption -> criterios técnicos:
      salary_expected       -> velocidad de respuesta al cambio (ms ficticio)
      probability_success   -> probabilidad de que funcione sin bugs
      timeline_months       -> esfuerzo de implementación (semanas ficticias como meses)
      tech_growth           -> calidad/elegancia de la solución (0-10)
      income_stability      -> estabilidad / sin downtime (0-10)
      work_life_balance     -> simplicidad de mantenimiento (0-10)
      prestige              -> aplicabilidad a otros proyectos (0-10)
      remote_flexibility    -> independencia del equipo de frontend (0-10)
      learning_opportunity  -> reducción de deuda técnica (0-10)
      career_ceiling        -> escalabilidad futura (0-10)
      unemployment_risk     -> riesgo de no funcionar en prod
      burnout_risk          -> riesgo de falla silenciosa
      market_risk           -> riesgo de obsolescencia
    """

    # -------------------------------------------------------------------------
    # OPCIÓN A: Adaptar config-ip-addr → netplan + systemd restart
    # Misma lógica que el DRS pero con las herramientas de Ubuntu sin Docker
    # -------------------------------------------------------------------------
    option_a = CareerOption(
        name="A: Adaptar config-ip-addr (netplan + systemd restart)",
        salary_expected=1_000_000,   # Solución básica
        probability_success=0.75,
        timeline_months=0,           # Horas de trabajo

        tech_growth=4.0,             # Poco elegante, copy-paste del actual
        income_stability=5.0,        # Requiere restart del frontend (~downtime 30s)
        work_life_balance=7.0,       # Fácil de mantener, código conocido
        prestige=4.0,                # Solución de parcheo
        remote_flexibility=3.0,      # Frontend debe coordinarse con este servicio
        learning_opportunity=3.0,    # No resuelve el problema raíz
        career_ceiling=3.0,          # No escala a múltiples apps/máquinas

        unemployment_risk=0.25,      # Hay edge cases con systemd restart
        burnout_risk=0.20,           # netplan apply puede fallar silencioso
        market_risk=0.10,

        description="""
        Adapta la app config-ip-addr existente para:
        1. Editar /etc/netplan/01-netcfg.yaml con nueva IP
        2. Ejecutar 'netplan apply'
        3. Actualizar .env del frontend con nueva IP
        4. Ejecutar 'systemctl restart frontend.service'
        Sin Docker, misma arquitectura conocida.
        """,
        pros=[
            "Reutiliza código existente del DRS",
            "Bajo esfuerzo de implementación",
            "El equipo ya conoce la arquitectura",
        ],
        cons=[
            "Downtime ~30s en cada cambio de IP",
            "No resuelve el problema raíz (IP hardcodeada)",
            "Requiere reconstruir el frontend si es Next.js con build-time env vars",
            "Frágil: si falla el restart queda en estado inconsistente",
        ]
    )

    # -------------------------------------------------------------------------
    # OPCIÓN B: Runtime config.json (frontend lee IP en cada request)
    # El frontend hace fetch('/config.json') en cada carga
    # -------------------------------------------------------------------------
    option_b = CareerOption(
        name="B: Runtime config.json (sin restart del frontend)",
        salary_expected=3_000_000,
        probability_success=0.85,
        timeline_months=1,           # 1 día de trabajo en frontend

        tech_growth=7.0,             # Patrón estándar en enterprise frontend
        income_stability=8.5,        # Sin downtime, frontend sigue corriendo
        work_life_balance=7.5,       # Mantenimiento simple, 1 archivo JSON
        prestige=7.0,                # Patrón conocido (usado en Kubernetes configs)
        remote_flexibility=6.0,      # Requiere modificar el frontend
        learning_opportunity=6.0,    # Elimina hardcodeo de IP en build-time
        career_ceiling=7.0,          # Escala a múltiples variables de configuración

        unemployment_risk=0.15,      # Requiere fetch funcional desde el cliente
        burnout_risk=0.10,           # JSON simple, difícil que falle
        market_risk=0.05,

        description="""
        El frontend hace `fetch('/config.json')` al cargar.
        config-ip-addr solo escribe /opt/frontend/public/config.json + netplan apply.
        Sin restart del frontend, sin npm rebuild.
        El archivo es servido estáticamente por Next.js desde /public.
        """,
        pros=[
            "Sin downtime (0ms interrupción del servicio)",
            "No requiere rebuild ni restart del frontend",
            "Patrón estándar (usado en Docker, Kubernetes, Electron apps)",
            "Generalizable a cualquier variable de configuración",
        ],
        cons=[
            "Requiere modificar el código del frontend (1 día)",
            "Cada cliente hace 1 request extra al cargar",
            "Si el frontend está muy acoplado a process.env puede ser difícil refactorizar",
        ]
    )

    # -------------------------------------------------------------------------
    # OPCIÓN C: Self-discovery (el frontend detecta su propia IP con os.networkInterfaces)
    # El servidor Next.js lee su IP en runtime, no la necesita configurada
    # -------------------------------------------------------------------------
    option_c = CareerOption(
        name="C: Self-discovery de IP (Node.js os.networkInterfaces)",
        salary_expected=4_000_000,
        probability_success=0.90,
        timeline_months=1,           # 1 día en server components

        tech_growth=9.0,             # Elimina el problema de raíz
        income_stability=9.5,        # Siempre correcto, sin intervención manual
        work_life_balance=9.0,       # Cero mantenimiento después de implementar
        prestige=8.5,                # Solución elegante y profesional
        remote_flexibility=9.0,      # config-ip-addr solo maneja netplan, no el app
        learning_opportunity=8.0,    # Deja de depender de configuración manual
        career_ceiling=9.0,          # Funciona aunque no corras config-ip-addr

        unemployment_risk=0.10,      # Edge case: múltiples interfaces (wifi + eth)
        burnout_risk=0.05,           # Muy difícil que falle
        market_risk=0.05,

        description="""
        En Server Components de Next.js:
          import { networkInterfaces } from 'os'
          export function getLocalIP() {
            return Object.values(networkInterfaces())
              .flat()
              .find(i => i?.family === 'IPv4' && !i.internal)?.address ?? 'localhost'
          }
        config-ip-addr solo ejecuta 'netplan apply', el frontend
        siempre sabe su propia IP sin configuración externa.
        """,
        pros=[
            "Elimina el problema de raíz: IP siempre correcta automáticamente",
            "Funciona aunque no se ejecute config-ip-addr",
            "Cero downtime, cero configuración en producción",
            "1 día de refactoring, 0 días de mantenimiento después",
        ],
        cons=[
            "Solo aplica cuando el frontend NECESITA su propia IP (URLs, QR codes, etc.)",
            "Requiere modificar el frontend (Server Components únicamente)",
            "No aplica si la IP que necesita es la de otro servidor/backend",
        ]
    )

    # -------------------------------------------------------------------------
    # OPCIÓN D: mDNS/Avahi hostname fijo (minipc.local reemplaza la IP)
    # Instalar avahi-daemon y usar hostname estático en toda la configuración
    # -------------------------------------------------------------------------
    option_d = CareerOption(
        name="D: mDNS/Avahi hostname fijo (minipc.local)",
        salary_expected=4_500_000,
        probability_success=0.88,
        timeline_months=0,           # Horas (solo Ansible + hostnamectl)

        tech_growth=9.5,             # Elimina el problema para siempre
        income_stability=9.0,        # El hostname nunca cambia aunque cambie la IP
        work_life_balance=10.0,      # Cero mantenimiento, cero cambios en frontend
        prestige=9.0,                # Arquitectura profesional (usado en IoT, edge computing)
        remote_flexibility=10.0,     # CERO cambios en el frontend
        learning_opportunity=8.0,    # Aprenden sobre mDNS/DNS-SD
        career_ceiling=9.5,          # Escala: mismo hostname para N máquinas

        unemployment_risk=0.12,      # Requiere avahi en todos los clientes (Linux/macOS OK, Windows necesita Bonjour)
        burnout_risk=0.08,           # avahi-daemon muy estable
        market_risk=0.05,

        description="""
        Ansible instala avahi-daemon + hostnamectl set-hostname minipc-sistema.
        Todos los clientes usan http://minipc-sistema.local en lugar de IP.
        Cuando la IP cambia, el hostname sigue resolviendo.
        config-ip-addr solo hace: netplan apply (no toca el frontend nunca más).
        """,
        pros=[
            "CERO cambios en el frontend",
            "CERO mantenimiento posterior",
            "Funciona nativamente en Linux, macOS, Windows 10+ (Bonjour integrado)",
            "config-ip-addr queda simplificado: solo netplan apply",
            "Escalable: N máquinas con hostnames diferentes",
        ],
        cons=[
            "Windows clientes más viejos necesitan instalar Bonjour",
            "No funciona entre subredes (solo LAN local)",
            "Requiere que todos los clientes soporten mDNS (mayormente sí en 2026)",
        ]
    )

    # -------------------------------------------------------------------------
    # OPCIÓN E: Nginx como capa de abstracción (proxy inverso local)
    # Frontend siempre habla con localhost, Nginx redirige al backend real
    # -------------------------------------------------------------------------
    option_e = CareerOption(
        name="E: Nginx proxy inverso (frontend habla con localhost siempre)",
        salary_expected=3_500_000,
        probability_success=0.92,
        timeline_months=1,           # 1 día configurar nginx

        tech_growth=8.0,             # Separación clara frontend/backend/red
        income_stability=9.5,        # nginx -s reload: milisegundos, sin downtime
        work_life_balance=8.0,       # 1 archivo nginx.conf, fácil de entender
        prestige=9.0,                # Arquitectura profesional estándar
        remote_flexibility=8.5,      # Frontend 100% independiente de la IP real
        learning_opportunity=7.5,    # Aprenden nginx, reverse proxy
        career_ceiling=8.5,          # Escala: SSL, load balancing, caching incluidos

        unemployment_risk=0.08,      # nginx es extremadamente estable
        burnout_risk=0.05,           # nginx -s reload nunca tumba el frontend
        market_risk=0.05,

        description="""
        Nginx corre en la máquina como proxy:
          upstream backend { server 192.168.x.x:8080; }
          server {
            listen 80;
            location /api/ { proxy_pass http://backend; }
            location / { proxy_pass http://localhost:3000; }
          }
        config-ip-addr actualiza solo el bloque upstream + nginx -s reload.
        El frontend siempre usa /api/... (relativo), nunca una IP hardcodeada.
        """,
        pros=[
            "CERO cambios en el frontend si ya usa paths relativos /api/",
            "nginx -s reload: ~10ms, sin downtime absoluto",
            "Bonus: SSL, compresión, caching, logging centralizado gratis",
            "Estándar de la industria para microservicios",
            "config-ip-addr solo edita 1 línea en nginx.conf",
        ],
        cons=[
            "Requiere configurar nginx (1 día)",
            "Si el frontend hardcodea la URL completa (https://192.168.x.x/api) no aplica directamente",
            "Un servicio más para monitorear (aunque nginx es extremadamente estable)",
        ]
    )

    return [option_a, option_b, option_c, option_d, option_e]


def print_results(options: list[CareerOption], results: list) -> None:
    """Imprime el análisis comparativo"""
    print("\n" + "="*75)
    print("   📊 RESULTADOS DEL ANÁLISIS — IP Configuration Strategy")
    print("="*75)

    # Ordenar por overall_score
    sorted_results = sorted(results, key=lambda r: r.overall_score, reverse=True)

    for i, result in enumerate(sorted_results, 1):
        option = next(o for o in options if o.name == result.option_name)
        pareto = "✅ Pareto" if result.pareto_optimal else "   "
        print(f"\n{'─'*70}")
        print(f"  #{i} [{pareto}] {result.option_name}")
        print(f"      Score general:   {result.overall_score:.2f}")
        print(f"      Monte Carlo:     {result.monte_carlo_score:.2f}")
        print(f"      TOPSIS rank:     #{result.topsis_rank}")
        print(f"      Riesgo:          {result.risk_score:.2f}")
        print(f"      Robustez:        {result.scenario_robustness:.2f}")
        print(f"      Confianza:       {result.confidence*100:.0f}%")
        print(f"      Recomendación:   {result.recommendation}")

    print(f"\n{'='*75}")
    print("   🏆 GANADOR:", sorted_results[0].option_name)
    print("="*75 + "\n")


async def run_with_gemini(options: list[CareerOption]) -> None:
    """Ejecuta análisis completo con Gemini IA"""
    from deep_research_decision_agent import GeminiDeepResearchAgent

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY no encontrada, ejecutando solo con metodologías")
        run_offline(options)
        return

    print("\n🤖 Gemini IA habilitado — ejecutando deep research...\n")

    engine = DecisionAnalysisEngine(debug=True)
    agent = GeminiDeepResearchAgent(debug=True)

    context = """
    Contexto técnico:
    - Frontend: Next.js instalado directamente en Ubuntu (sin Docker)
    - Gestión de red: Ubuntu + netplan
    - Problema: La IP de la máquina cambia y el frontend tiene la IP hardcodeada como build-time env var
    - App actual: 'config-ip-addr' (Next.js) que cambia IPs remotamente via Ansible
    - Restricción: No se puede hacer rebuild del frontend en producción (tarda demasiado)
    - Contexto industria: Sistema embebido tipo MiniPC en instalaciones industriales (minería/leaky feeder)
    Evalúa qué estrategia de arquitectura es mejor para este caso.
    """

    results = []
    # Usar análisis offline (engine) para todas las opciones
    # Deep research de Gemini solo para la más prometedora (ahorra cuota)
    for option in options:
        result = engine.analyze_option(option, options)
        results.append(result)

    # Deep research de Gemini para las top 2
    sorted_results = sorted(results, key=lambda r: r.overall_score, reverse=True)
    top_names = {sorted_results[0].option_name, sorted_results[1].option_name}

    for option in options:
        if option.name in top_names:
            print(f"\n🔍 Investigando con Gemini: {option.name}")
            try:
                research_result = await agent.research_option(option, context)
                # Actualizar el resultado con el research de Gemini
                for r in results:
                    if r.option_name == option.name:
                        r.deep_research = research_result.deep_research
                        print(f"   ✅ Research completado ({len(r.deep_research)} chars)")
                        print("\n   📄 Fragmento del research Gemini:\n")
                        print("   " + r.deep_research[:800].replace("\n", "\n   "))
                        break
            except Exception as e:
                print(f"   ⚠️  Gemini unavailable: {e} — continuando con análisis offline")

    print_results(options, results)


def run_offline(options: list[CareerOption]) -> None:
    """Ejecuta solo las 13 metodologías sin Gemini"""
    print("\n📐 Ejecutando 13 metodologías de decisión (modo offline)...\n")

    engine = DecisionAnalysisEngine(debug=False)
    results = []

    for option in options:
        print(f"  ⚙️  Analizando: {option.name[:50]}...")
        result = engine.analyze_option(option, options)
        results.append(result)

    print_results(options, results)


def main():
    print("\n" + "="*75)
    print("   🌐 DECISIÓN: Estrategia óptima para cambio de IP")
    print("   Frontend Next.js en Ubuntu bare-metal (sin Docker) + netplan")
    print("="*75 + "\n")

    options = create_ip_strategy_options()

    print(f"  📋 Opciones a analizar: {len(options)}")
    for i, o in enumerate(options, 1):
        print(f"    {i}. {o.name}")

    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        print("\n  ✅ GEMINI_API_KEY detectada — se usará IA para top 2 opciones")
        asyncio.run(run_with_gemini(options))
    else:
        print("\n  ⚠️  Sin GEMINI_API_KEY — análisis offline con 13 metodologías")
        run_offline(options)


if __name__ == "__main__":
    main()
