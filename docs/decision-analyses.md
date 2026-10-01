---
aliases: [Decision Analyses, Catálogo de Análisis, Casos de Decisión]
tags: [analyses, database, lumina, quant, archive]
id: DB-ANALYSES
title: "Catálogo de Análisis de Decisiones Aplicadas"
type: moc
category: analyses
status: active
related: ["[[database-hub]]", "[[decision-maker-moc]]", "[[results-catalog]]", "[[index]]"]
created: 2026-08-10
updated: 2026-10-01
---

# 📊 Catálogo de Análisis de Decisiones Aplicadas

Este registro centraliza los 37 análisis de decisión cuantitativa en `src/decision_maker/analyses/` —más `_template.py`, la plantilla canónica, que no es un análisis y por eso no cuenta— y los 7 scripts auxiliares en `src/decision_maker/scripts/`. Cada archivo representa un caso concreto modelado con metodologías estocásticas y multicriterio.

Hub general de base de datos: [[database-hub]] | Catálogo de reportes y salidas: [[results-catalog]].

---

## 🏠 1. Decisiones Personales, de Carrera y Presupuesto

| ID | Script (`src/decision_maker/analyses/`) | Objetivo y Pregunta de Decisión | Metodologías Empleadas | Estado |
|:---|:---|:---|:---|:---|
| `ANA-CONCON` | `decision_concon.py` | Evaluación de vivienda y estilo de vida en Concón vs Santiago | [[monte-carlo-engine]], [[topsis]], lógica difusa | `active` |
| `ANA-VINA-CONCON` | `decision_vina_vs_concon.py` | Comparativa multicriterio Viña del Mar (Patmos) vs Concón | [[monte-carlo-engine]], [[promethee]], [[topsis]] | `active` |
| `ANA-LIFE-VINA` | `life_decision_vina_concon.py` | Análisis de costos iniciales y plan de ahorro para mudanza a Viña | Modelado de flujos estocásticos, punto de equilibrio | `active` |
| `ANA-MUDANZA-PATMOS` | `decision_mudanza_patmos_hijos.py` | Decisión de mudanza familiar y escolaridad Patmos | [[monte-carlo-engine]], evaluación de riesgo de ruina | `active` |
| `ANA-PATMOS-CALC` | `decision_patmos_calculator.py` | Calculadora de presupuestos y costos recurrentes comparados | Modelado determinista y estocástico | `active` |
| `ANA-FURNITURE` | `furniture_diy.py` | Compra de muebles DIY nuevos vs usados de segunda mano | [[monte-carlo-engine]], [[topsis]], [[pareto-frontier]] | `active` |
| `ANA-MINING-V2` | `mining_improved.py` | Carrera profesional en el sector minero (versión v2 mejorada) | [[monte-carlo-engine]], [[topsis]], [[sensitivity-analysis]] | `active` |
| `ANA-SQM` | `sqm_santiago.py` | Viabilidad y estrategia de proyecto para SQM en Santiago | [[topsis]], análisis de escenarios | `active` |
| `ANA-MINING-V1` | `mining_decision.py` | Carrera en minería (versión original histórica) | Árboles de decisión, valor esperado | `archive` |
| `ANA-REFACTOR` | `refactoring_decision.py` | Evaluación de refactorización de código FSK / LoRa legacy | Análisis de punto de equilibrio, payoff matrix | `completed` |

---

## 🛠️ 2. Hardware, Redes e Infraestructura Minera

| ID | Script (`src/decision_maker/analyses/`) | Problema de Ingeniería Modelado | Motores Clave | Estado |
|:---|:---|:---|:---|:---|
| `ANA-SOPHOS` | `sophos_xg115_decision.py` | Evaluación de appliance Sophos XG115: firmware vs reemplazo | [[monte-carlo-engine]], [[topsis]], [[promethee]] | `active` |
| `ANA-BECKER-HW` | `becker_hardware_decision.py` | Hardware receptor FSK para Becker Varis en gateway | [[monte-carlo-engine]], [[decision-theory]] | `active` |
| `ANA-BECKER-RESP` | `becker_response_decision.py` | Estrategia de respuesta y compatibilidad con Becker Varis | [[decision-gates]], [[topsis]] | `active` |
| `ANA-FSK-EVAL` | `fsk_protocol_evaluation.py` | Protocolo serial que reemplaza al legacy 0x7E/0x7F del fsk-scanner. v2 (2026-10-01): gana VLAD25-V2 (0.659) muy cerca de Simple-framed (0.651) | [[unified-orchestrator]] (modo `standard`), [[monte-carlo-engine]], [[topsis]], [[decision-theory]] | `active` |
| `ANA-FSK-SCANNER` | `fsk_scanner_integration.py` | Dónde vive la integración del FSK scanner Becker Varis. v2 (2026-10-01): gana Hybrid fsk-scanner + monitor-serial (0.795) | [[unified-orchestrator]] (modo `standard`), [[monte-carlo-engine]], [[topsis]], [[pareto-frontier]] | `active` |
| `ANA-MINERIA-INT` | `mineria_integration.py` | Integración de datos RDSS a sistemas de control mineros | [[monte-carlo-engine]], [[ahp]] | `active` |
| `ANA-PLC-BRIDGE` | `plc_bridge_comparativa.py` | Comparativa entre PLC puente Modbus vs API CSV vs existentes | [[pareto-frontier]], [[topsis]] | `active` |
| `ANA-SNIFFER-V1` | `sniffertelemetry_destino.py` | Destino y arquitectura de repositorio `sw-sniffertelemetry` | [[decision-theory]], árboles de decisión | `archive` |
| `ANA-SNIFFER-V2` | `sniffertelemetry_destino_v2.py` | Destino con criterio de menor costo de mantenimiento | [[topsis]], ponderación de criterios | `active` |
| `ANA-SNIFFER-V3` | `sniffertelemetry_destino_v3_leakyfeeder.py` | Destino bajo restricción de red leaky feeder | [[robust-optimization]], [[decision-gates]] | `active` |
| `ANA-SNIFFER-V4` | `sniffertelemetry_destino_v4_hibrido.py` | Arquitectura híbrida elegida: diagnóstico + demo + exportador | [[portfolio-optimizer]], [[topsis]] | `active` |
| `ANA-EXPORTADOR-V5` | `exportador_nms_protocolo_v5.py` | Protocolo del exportador hacia NMS (Modbus vs API REST) | [[decision-theory]], [[bootstrap-ranking]] | `active` |
| `ANA-SPECTRUM` | `spectrum_analyzer_selection.py` | Selección de analizador de espectro para banco de pruebas RF | [[topsis]], [[ahp]] | `active` |
| `ANA-TABLERO` | `tablero_cabinet_decision.py` | Selección de gabinete industrial para tablero de seguridad | [[topsis]], [[pareto-frontier]] | `active` |
| `ANA-MINA-MONIT` | `tech_eval_monitoreo_mina.py` | Evaluación de tecnologías de monitoreo en la nube para faenas | [[monte-carlo-engine]], [[unified-orchestrator]] | `active` |
| `ANA-UQOMM-V6` | `uqomm_adopcion_v6_leakyfeeder.py` | Estrategia para máxima adopción de mercado en leaky feeder | [[monte-carlo-engine]], [[antifragile-engine]] | `active` |
| `ANA-VLAD25` | `vlad25_modo_diagnostico_decision.py` | Coexistencia de modo polling legacy y push para VLAD25 | [[bayesian-inference-engine]], [[topsis]] | `active` |
| `ANA-DIAG-LINEA-BASE` | `diagnostico_remoto_linea_base_decision.py` | Sobre qué línea de sw-diagnosticoremoto seguir construyendo (development, VHF v4.2.0 vendida, UHF ulad): unificar, sobre cuál base, o separarlas | [[unified-orchestrator]] (modo `standard`), [[monte-carlo-engine]], [[topsis]], [[decision-theory]], [[sensitivity-analysis]] | `active` |

---

## ⚡ 3. Diagnóstico e Investigación de Fuentes de Poder

| ID | Archivo / Dataset (`analyses/`) | Descripción del Análisis | Formato |
|:---|:---|:---|:---|
| `ANA-PWR-RESEARCH` | `power_supply_research.py` | Análisis cuantitativo principal de fuentes de poder para mina | Script Python |
| `ANA-PWR-SIMPLE` | `power_supply_deep_research_simple.py` | Versión sintética de análisis de módulos de alimentación | Script Python |
| `ANA-PWR-GEMINI` | `power_supply_gemini_deep_research.py` | Integración de investigación profunda con Gemini API | Script Python |
| `ANA-PWR-UTIL-RES` | `power_supply_utility_research.py` | Investigación de funciones de utilidad para telemetría de poder | Script Python |
| `ANA-PWR-PROC-RES` | `process_research_results.py` | Procesamiento y generación de reportes Markdown para ingeniería | Script Python |
| `ANA-PWR-PROC-UTIL` | `process_utility_analysis.py` | Cálculo de matrices de utilidad multicriterio y exportación | Script Python |
| `DATA-PWR-RES` | `power_supply_research_results.json` | Dataset de resultados de investigación de mercado de fuentes | JSON generado por `power_supply_deep_research_simple.py`, no versionado (`.gitignore`) — no existe en un clon limpio |
| `DATA-PWR-UTIL-AN` | `power_supply_utility_analysis.json` | Dataset con scores de utilidad ponderada por fabricante | JSON generado por `process_utility_analysis.py`, no versionado (`.gitignore`) — no existe en un clon limpio |
| `DATA-PWR-UTIL-RES` | `power_supply_utility_results.json` | Dataset final de resultados de utilidad procesados | JSON generado por `power_supply_utility_research.py`, no versionado (`.gitignore`) — no existe en un clon limpio |

---

## 🔄 4. Refactorización de Protocolos y Plantillas

| ID | Script (`src/decision_maker/analyses/`) | Alcance | Metodologías |
|:---|:---|:---|:---|
| `ANA-CMDMSG-REFACTOR` | `commandmessage_refactor_decision.py` | Refactorización de CommandMessage (protocolo RDSS) | [[antifragile-engine]], [[robust-optimization]] |
| `ANA-CMDMSG-LLM` | `commandmessage_refactor_llm_20260823.py` | Evaluación de refactor asistido por LLM vs manual | [[decision-gates]], [[monte-carlo-engine]] |
| `ANA-CMDMSG-CPP` | `refactoring_commandmessage.py` | Análisis de impacto de modularización C++ en firmware | [[sensitivity-analysis]], matriz payoff |
| `ANA-TEMPLATE` | `_template.py` | Plantilla canónica estandarizada para nuevos análisis de decisión | Plantilla Python tipada |

---

## 🔍 5. Scripts de Utilidad y Búsqueda (`src/decision_maker/scripts/`)

| ID | Script | Propósito y Función |
|:---|:---|:---|
| `SCRIPT-IDEAS` | `analyze_researched_ideas.py` | Procesador y rankeador de ideas de negocio investigadas |
| `SCRIPT-BIZ-SEARCH` | `autonomous_business_search.py` | Motor de búsqueda autónoma de oportunidades de mercado |
| `SCRIPT-GEMINI-QRY` | `gemini_query.py` | Cliente utilitario para consultas directas a Google Gemini API |
| `SCRIPT-IP-CONFIG` | `ip_config_strategy.py` | Modelo de decisión para actualización de IPs en frontends distribuidos |
| `SCRIPT-LEAKY-RES` | `research_leaky_feeder.py` | Extractor de especificaciones para monitoreo de redes leaky feeder |
| `SCRIPT-SAMBA-OPT` | `samba_performance_strategy.py` | Estrategia de optimización para rendimiento Samba en red local |
| `SCRIPT-FURN-SEARCH` | `search_furniture_prices_chile.py` | Scraper y estimador de precios de mobiliario en mercado chileno |

---

## 💡 6. Casos de Estudio y Ejemplos (`examples/`)

| ID | Script de Ejemplo | Descripción |
|:---|:---|:---|
| `EX-FURNITURE` | `diy_furniture_secondhand.py` | Ejemplo didáctico: Hacer mueble DIY vs comprar usado vs nuevo |
| `EX-MAC-COMP` | `mac_upgrade_comparison.py` | Comparativa de niveles de ejecución (Express vs Standard vs Advanced) |
| `EX-MAC-CASE` | `mac_upgrade_example.py` | Caso completo de decisión de actualización de hardware Mac |

---

## 📊 7. Visualización y Salidas

Todos los scripts canalizan sus resultados hacia `results/`, catalogados detalladamente en [[results-catalog]]:
- Reportes ejecutivos Markdown: `results/report_*.md`
- Vistas web interactivas: `results/report_*.html`
- Gráficos de auditoría: `results/risk_profiles_*.png`, `results/factor_importance_*.png`, `results/robustness_audit_*.png`
- Registro estructurado SQLite persistente gestionado por [[reporting-and-registry]]
