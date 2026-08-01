#!/usr/bin/env python3
"""
ANALYSIS: Strategy for Samba slowness on server 192.168.60.200
Context: Samba server (dataserver) with 24+ concurrent users,
load average ~67 on CPU 4 cores, backup rsync consuming I/O.
Uses the decision framework with 13+ methodologies.

NOTE: This script uses a legacy API (CareerOption, DecisionAnalysisEngine)
that no longer exists. It needs to be rewritten to use UnifiedDecisionFramework.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from decision_maker.core.models import DecisionOption, DistributionType, Factor
    from decision_maker.core.orchestrator import UnifiedDecisionFramework
except ImportError:
    print("ERROR: Cannot import decision framework. Run from project root.")
    sys.exit(1)

import os

from dotenv import load_dotenv

_base = Path(__file__).parent.parent
load_dotenv(_base / ".env")
load_dotenv(_base / ".env.gemini", override=True)


def create_samba_strategy_options() -> list[CareerOption]:
    """
    6 estrategias para resolver lentitud Samba en dataserver.

    Mapeo de campos CareerOption -> criterios tecnicos:
      salary_expected       -> performance ganada (score 0-10M)
      probability_success   -> probabilidad de exito sin efectos secundarios
      timeline_months       -> esfuerzo de implementacion (dias ficticios como meses)
      tech_growth           -> calidad/sostenibilidad de la solucion (0-10)
      income_stability      -> estabilidad / sin downtime (0-10)
      work_life_balance     -> simplicidad de mantenimiento (0-10)
      prestige              -> aplicabilidad a otros proyectos (0-10)
      remote_flexibility    -> independencia del cliente (0-10)
      learning_opportunity  -> reduccion de deuda tecnica (0-10)
      career_ceiling        -> escalabilidad futura (0-10)
      unemployment_risk     -> riesgo de no funcionar en prod
      burnout_risk          -> riesgo de falla silenciosa
      market_risk           -> riesgo de obsolescencia
    """

    # -------------------------------------------------------------------------
    # OPCION A: Quick Wins (matar backup + tuning Samba)
    # Matar rsync, optimizar smb.conf, cambiar I/O scheduler
    # -------------------------------------------------------------------------
    option_a = CareerOption(
        name="A: Quick Wins (matar backup + tuning Samba + I/O scheduler)",
        salary_expected=8_500_000,   # Alto impacto inmediato
        probability_success=0.95,     # Muy seguro, cambios en caliente
        timeline_months=0,            # Horas

        tech_growth=5.0,              # Solucion parche, no aborda raiz estructural
        income_stability=8.0,         # Mejora inmediata pero puede revertir
        work_life_balance=9.0,        # Unico cambio de config
        prestige=4.0,                 # Solucion de parcheo
        remote_flexibility=8.0,       # No requiere cambios en clientes
        learning_opportunity=4.0,     # No cambia la arquitectura
        career_ceiling=4.0,           # No escala a futuro

        unemployment_risk=0.05,       # Muy bajo riesgo
        burnout_risk=0.15,            # backup podria volver a ejecutarse
        market_risk=0.10,

        description="""
        1. Matar proceso rsync (kill -TERM 6278) para liberar I/O inmediatamente
        2. Agregar tuning a /etc/samba/smb.conf:
           socket options = TCP_NODELAY IPTOS_LOWDELAY SO_RCVBUF=131072 SO_SNDBUF=131072
           read raw = yes, write raw = yes, strict locking = no
           use sendfile = yes, min receivefile size = 16384
           aio read/write size = 16384, log level = 0
        3. Cambiar I/O scheduler de CFQ a deadline:
           echo deadline > /sys/block/sdX/queue/scheduler
        4. Desactivar full_audit VFS temporalmente
        5. Reprogramar fwbackups para Sabado 00:00-06:00
        6. Agregar --bwlimit=50000 al rsync
        """,
        pros=[
            "Impacto inmediato (horas)",
            "Sin riesgo de perdida de datos",
            "Sin cambios en clientes",
            "Costo $0",
        ],
        cons=[
            "No soluciona problema estructural (HDD vs SSD)",
            "Samba 4.5.14 EOL sigue siendo vulnerable",
            "Backup puede volver a saturar si crece el volumen",
            "CFQ scheduler vuelve al default tras reboot si no se persiste",
        ]
    )

    # -------------------------------------------------------------------------
    # OPCION B: Reorganizar archivos por subdirectorios anio/cliente
    # Mover archivos sueltos y organizar /home/server por anio + cliente
    # -------------------------------------------------------------------------
    option_b = CareerOption(
        name="B: Reorganizar archivos en subdirectorios por anio/cliente",
        salary_expected=5_000_000,
        probability_success=0.80,
        timeline_months=1,             # Semanas de trabajo

        tech_growth=7.0,               # Mejora organizacional real
        income_stability=7.0,          # Reduce fragmentacion, mejora I/O
        work_life_balance=6.0,         # Mantenimiento requiere disciplina
        prestige=6.0,                  # Buena practica de administracion
        remote_flexibility=6.0,        # Clientes deben actualizar paths
        learning_opportunity=6.0,      # Establece cultura de organizacion
        career_ceiling=6.0,            # Mejora pero no cambia hardware

        unemployment_risk=0.20,        # Riesgo de romper referencias
        burnout_risk=0.20,             # Usuarios pueden desordenar de nuevo
        market_risk=0.05,

        description="""
        Reorganizar /home/server/:
        /home/server/Anio/Cliente/Proyecto/
        - Mover ~10 archivos sueltos de la raiz a subdirectorios
        - Establecer politica de organizacion
        - Crear carpetas por anio (2024, 2025, 2026) y dentro por cliente
        - Migrar datos de departamentos a estructura estandar
        - Actualizar paths en smb.conf si es necesario
        """,
        pros=[
            "Reduce tiempo de escaneo de directorios",
            "Mejora performance de backups incrementales",
            "Establece orden y facilita busquedas",
            "Sin costo de hardware",
        ],
        cons=[
            "Requiere coordinacion con todos los departamentos",
            "Usuarios pueden resistirse al cambio",
            "Riesgo de perder referencias a archivos",
            "No soluciona el problema de I/O de los HDD",
        ]
    )

    # -------------------------------------------------------------------------
    # OPCION C: Migrar a NFSv4 (reemplazar Samba)
    # Clientes Linux usan NFSv4, mejor performance nativa
    # -------------------------------------------------------------------------
    option_c = CareerOption(
        name="C: Migrar a NFSv4 para clientes Linux (reemplazar Samba)",
        salary_expected=6_500_000,
        probability_success=0.65,
        timeline_months=1,             # 1-2 semanas implementacion

        tech_growth=8.0,               # Solucion nativa Unix
        income_stability=8.5,          # NFS es mas rapido que Samba en Linux
        work_life_balance=7.0,         # Configuracion simple
        prestige=8.0,                  # Arquitectura profesional
        remote_flexibility=4.0,        # Clientes Windows no pueden usar NFS nativo
        learning_opportunity=7.0,      # Aprendizaje de NFS
        career_ceiling=7.0,            # Escala bien en clusters Linux

        unemployment_risk=0.25,        # Incompatible con clientes Windows puros
        burnout_risk=0.15,
        market_risk=0.15,              # Samba sigue siendo estandar en mixtos

        description="""
        Reemplazar Samba por NFSv4 en el servidor:
        - Instalar y configurar nfs-kernel-server
        - Exportar /home/server via NFSv4 con Kerberos opcional
        - Configurar montajes en clientes Linux via autofs
        - Clientes Windows seguiran usando Samba (se mantiene)
        - NFS reduce overhead de protocolo vs SMB en redes Linux-Linux
        """,
        pros=[
            "NFSv4 es significativamente mas rapido que Samba en Linux-Linux",
            "Menor overhead de CPU en el servidor",
            "Configuracion mas simple que Samba",
            "Mejor integracion con Kerberos/LDAP",
        ],
        cons=[
            "Clientes Windows no pueden usar NFS sin extras",
            "Requiere mantener ambos servicios (NFS + Samba)",
            "Menos familiar para administradores actuales",
            "Riesgo de lock issues con aplicaciones que usan SMB",
        ]
    )

    # -------------------------------------------------------------------------
    # OPCION D: Separar shares en multiples discos
    # Distribuir departamentos entre /hdd1, /hdd2, /backup
    # -------------------------------------------------------------------------
    option_d = CareerOption(
        name="D: Separar shares en discos independientes (balance I/O)",
        salary_expected=7_500_000,
        probability_success=0.85,
        timeline_months=1,             # 1-2 semanas

        tech_growth=8.5,               # Arquitectura distribuida
        income_stability=9.0,          # Aisla I/O entre departamentos
        work_life_balance=7.5,         # Una vez configurado, facil
        prestige=8.5,                  # Diseno profesional
        remote_flexibility=8.0,        # Transparente para clientes
        learning_opportunity=8.0,      # Aprendizaje de LVM/mounts
        career_ceiling=8.0,            # Permite crecer en discos

        unemployment_risk=0.12,
        burnout_risk=0.10,
        market_risk=0.05,

        description="""
        Distribuir los shares departamentales en discos fisicos separados:
        - /hdd1 (sdc): Administrativo, Finanzas, SII (I/O moderado)
        - /hdd2 (sdd): Ingenieria, Desarrollo, TSG, Taller (I/O intensivo)
        - /home (sistema): Bodega, Compras (I/O bajo)
        - /backup (sdb): Backup de todos los shares
        Cada disco tiene su propio canal I/O, balanceando la carga.
        """,
        pros=[
            "Balancea I/O entre 3 discos fisicos",
            "Transparente para usuarios (mismos puntos de montaje)",
            "Reduce contention en el bus I/O",
            "Aisla fallos: si un disco falla, solo afecta a esos shares",
        ],
        cons=[
            "Requiere mover datos entre discos (migracion)",
            "Riesgo de quedarse sin espacio en un disco especifico",
            "No soluciona lentitud intrinseca de HDD vs SSD",
            "Requiere reconfigurar paths en smb.conf",
        ]
    )

    # -------------------------------------------------------------------------
    # OPCION E: Actualizar Samba + migrar a SSD
    # Solucion definitiva: Samba moderno + datos en SSD
    # -------------------------------------------------------------------------
    option_e = CareerOption(
        name="E: Actualizar Samba + migrar datos a SSD (solucion definitiva)",
        salary_expected=9_500_000,
        probability_success=0.90,
        timeline_months=2,             # 2-4 semanas

        tech_growth=10.0,              # Solucion definitiva
        income_stability=10.0,         # SSD elimina I/O bottleneck
        work_life_balance=9.0,         # Mantenimiento minimo
        prestige=9.5,                  # Mejor practica de la industria
        remote_flexibility=9.0,        # Cero cambios en clientes
        learning_opportunity=9.0,      # Actualizacion tecnologica
        career_ceiling=10.0,           # Escala a futuro sin problemas

        unemployment_risk=0.08,
        burnout_risk=0.05,
        market_risk=0.02,

        description="""
        Migracion completa:
        1. Adquirir SSD NVMe/SATA de 2-4 TB para datos activos
        2. Migrar /home/server a SSD
        3. Actualizar Samba a version 4.19+ (o Samba AD DC)
        4. Configurar smb.conf optimizado desde el inicio
        5. HDDs existentes quedan para backups y datos frios
        6. Configurar backup automatizado de SSD -> HDD
        7. Establecer politicas de retencion y archivado
        """,
        pros=[
            "Solucion definitiva: elimina bottleneck de I/O",
            "Samba moderno con features de seguridad y performance",
            "HDDs existentes sirven como backup integrado",
            "Mejora la experiencia de todos los usuarios",
            "Reduce consumo electrico vs discos mecanicos",
        ],
        cons=[
            "Requiere inversion en hardware (SSD)",
            "Requiere downtime para migracion (planificado)",
            "Riesgo menor de compatibilidad con Samba nuevo",
            "SSD de 4TB tiene costo significativo",
        ]
    )

    # -------------------------------------------------------------------------
    # OPCION F: Caching local con sync (like Dropbox)
    # Cada workstation tiene copia local, sync en background
    # -------------------------------------------------------------------------
    option_f = CareerOption(
        name="F: Caching local con rsync sincronizado (modo Dropbox local)",
        salary_expected=6_000_000,
        probability_success=0.60,
        timeline_months=2,             # 2-4 semanas

        tech_growth=7.0,
        income_stability=5.0,          # Depende de sync en cada maquina
        work_life_balance=4.0,         # Mucho mantenimiento por cliente
        prestige=5.0,                  # Solucion compleja de administrar
        remote_flexibility=7.0,        # Cada maquina tiene su copia
        learning_opportunity=6.0,
        career_ceiling=5.0,            # No escala a muchos clientes

        unemployment_risk=0.35,        # Complejidad alta
        burnout_risk=0.30,
        market_risk=0.20,

        description="""
        Cada workstation tiene una copia local de los archivos que usa:
        - Script rsync en cada maquina que sincroniza cambios cada 5 min
        - Los archivos se abren desde el disco local (latencia ~3ms)
        - Sync en background: solo transfiere cambios incrementales
        - En el servidor: los archivos se escriben normalmente
        - Similar al modelo de Dropbox/OneDrive pero en red local
        """,
        pros=[
            "Acceso local = velocidad maxima",
            "Trabajo offline posible",
            "Reduce carga I/O en el servidor",
            "Sin inversion en hardware de servidor",
        ],
        cons=[
            "Complejidad alta de administracion (N clientes)",
            "Riesgo de conflictos de versiones",
            "Duplicacion de espacio en disco en cada maquina",
            "Dificil de implementar con 24+ usuarios heterogeneos",
            "No es transparente: requiere cambios en habito de trabajo",
        ]
    )

    return [option_a, option_b, option_c, option_d, option_e, option_f]


import sys


def safe_print(text: str) -> None:
    """Print avoiding UnicodeEncodeError on Windows console"""
    try:
        print(text)
    except UnicodeEncodeError:
        clean = text.encode(sys.stdout.encoding, errors='replace').decode(sys.stdout.encoding)
        print(clean)


def print_results(options: list[CareerOption], results: list) -> None:
    """Imprime el analisis comparativo"""
    safe_print("\n" + "="*80)
    safe_print("   RESULTADOS DEL ANALISIS - Estrategia Samba Performance")
    safe_print("="*80)

    sorted_results = sorted(results, key=lambda r: r.overall_score, reverse=True)

    for i, result in enumerate(sorted_results, 1):
        option = next(o for o in options if o.name == result.option_name)
        pareto = "Pareto" if result.pareto_optimal else "   "
        safe_print(f"\n{'-'*80}")
        safe_print(f"  #{i} [{pareto}] {result.option_name}")
        safe_print(f"      Score general:   {result.overall_score:.2f}/10")
        safe_print(f"      Monte Carlo:     {result.monte_carlo_score:.2f}")
        safe_print(f"      TOPSIS rank:     #{result.topsis_rank}")
        safe_print(f"      Riesgo:          {result.risk_score:.2f}")
        safe_print(f"      Robustez:        {result.scenario_robustness:.2f}")
        safe_print(f"      Confianza:       {result.confidence*100:.0f}%")
        safe_print(f"      Recomendacion:   {result.recommendation}")

    winner = sorted_results[0]
    safe_print(f"\n{'='*80}")
    safe_print(f"   GANADOR: {winner.option_name}")
    safe_print(f"   Score: {winner.overall_score:.2f}/10 | Confianza: {winner.confidence*100:.0f}%")
    safe_print("="*80)

    # Resumen ejecutivo
    safe_print("\nRESUMEN EJECUTIVO:")
    safe_print("-" * 80)
    safe_print("  Las 3 mejores opciones:")
    for i, r in enumerate(sorted_results[:3], 1):
        safe_print(f"  {i}. {r.option_name} ({r.overall_score:.1f}/10)")
    safe_print("")
    safe_print("  Recomendacion de implementacion:")
    safe_print("  1. FASE 0 (hoy): Quick Wins - matar rsync, tuning Samba")
    safe_print("  2. FASE 1 (1 sem): Separar shares en discos independientes")
    safe_print("  3. FASE 2 (2-4 sem): Migrar a SSD + actualizar Samba")
    safe_print("")


async def run_with_gemini(options: list[CareerOption]) -> None:
    """Ejecuta analisis completo con Gemini IA"""
    from deep_research_decision_agent import GeminiDeepResearchAgent

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("GEMINI_API_KEY no encontrada, ejecutando solo con metodologias")
        run_offline(options)
        return

    print("\nGemini IA habilitado - ejecutando deep research...\n")

    engine = DecisionAnalysisEngine(debug=True)
    agent = GeminiDeepResearchAgent(debug=True)

    context = """
    Contexto tecnico:
    - Servidor: dataserver (192.168.60.200), Intel Xeon E3-1220 v3, 4 cores sin HT
    - RAM: 11GB, Discos: HDD 3.7TB x3 (sdc, sdd, sdb) + sistema en RAID1
    - OS: Fedora, Samba 4.5.14 (EOL 2018), XFS en todos los discos
    - 24 usuarios concurrentes via SMB3_11 (clientes Windows y Linux)
    - Problema: load average ~67, causado por rsync backup que corre 11+ horas
    - Share principal: /home/server con 18 subdirectorios departamentales
    - Sin tuning de performance en Samba, full_audit VFS activado
    - Backup: fwbackups-run ejecutando rsync de /home/server a /hdd1/longtime_backup/
    Evalua la mejor estrategia para resolver la lentitud considerando:
    1. Que es un servidor productivo usado a diario
    2. Hay presupuesto limitado para hardware
    3. La solucion debe ser mantenible por el equipo actual
    4. Los usuarios necesitan acceso rapido y confiable
    """

    results = []
    for option in options:
        result = engine.analyze_option(option, options)
        results.append(result)

    sorted_results = sorted(results, key=lambda r: r.overall_score, reverse=True)
    top_names = {sorted_results[0].option_name, sorted_results[1].option_name}

    for option in options:
        if option.name in top_names:
            print(f"\nInvestigando con Gemini: {option.name}")
            try:
                research_result = await agent.research_option(option, context)
                for r in results:
                    if r.option_name == option.name:
                        r.deep_research = research_result.deep_research
                        safe_print(f"   Research completado ({len(r.deep_research)} chars)")
                        if r.deep_research:
                            safe_print("\n   Fragmento del research Gemini:\n")
                            safe_print("   " + r.deep_research[:800].replace("\n", "\n   "))
                        break
            except Exception as e:
                safe_print(f"   Gemini no disponible: {e} - continuando con analisis offline")

    print_results(options, results)


def run_offline(options: list[CareerOption]) -> None:
    """Ejecuta solo las 13 metodologias sin Gemini"""
    print("\nEjecutando 13 metodologias de decision (modo offline)...\n")

    engine = DecisionAnalysisEngine(debug=False)
    results = []

    for option in options:
        print(f"  Analizando: {option.name[:50]}...")
        result = engine.analyze_option(option, options)
        results.append(result)

    print_results(options, results)


def main():
    print("\n" + "="*80)
    print("   DECISION: Estrategia optima para lentitud Samba en dataserver")
    print("   192.168.60.200 - 24 usuarios - Load avg ~67 - Samba 4.5.14")
    print("="*80 + "\n")

    options = create_samba_strategy_options()

    print(f"  Opciones a analizar: {len(options)}")
    for i, o in enumerate(options, 1):
        print(f"    {i}. {o.name}")

    run_offline(options)


if __name__ == "__main__":
    main()
