---
aliases: [Roadmap, Roadmap v3, Project Roadmap]
tags: [roadmap, lumina, quant, archive]
id: DOC-ROADMAP
title: "Roadmap de Desarrollo Cuantitativo"
type: roadmap
category: project-management
status: active
related: ["[[kanban]]", "[[decision-maker-moc]]", "[[index]]", "[[architecture]]"]
created: 2026-08-10
updated: 2026-09-27
---

# 🗺️ Roadmap: Decision Intelligence Framework

Vista integrada en el vault de Obsidian para la hoja de ruta del proyecto. Archivo fuente en la raíz del repositorio: [ROADMAP_v3.0.md](../ROADMAP_v3.0.md).

Tablero de ejecución en tiempo real: [[kanban]].

---

## 🎯 Estado Actual (v3.0)

El framework dispone de **19 motores ruteables**, API REST, interfaz web interactiva y CLI.

### Motores Completados
- **Antifrágil**: [[antifragile-engine]] — estrategia Barbell, convexidad, indexación de fragilidad y vía negativa.
- **Simulación Estocástica**: [[monte-carlo-engine]] — simulación de $N$ escenarios, cópula gaussiana para correlación.
- **Inferencia Empírica**: [[bayesian-inference-engine]] — probabilidades posteriores por opción.
- **MCDA**: [[topsis]], [[promethee]], [[ahp]] — ordenamiento multicriterio y jerarquías.
- **Optimización y Topología**: [[portfolio-optimizer]], [[genetic-algorithms]], [[topological-data-analysis]].
- **Infraestructura**: [[unified-orchestrator]], [[data-models-and-schemas]], [[reporting-and-registry]].

---

## 🚀 Próximas Mejoras (v3.1+)

1. 🤖 **AI-Powered Parameter Estimation**: Inferencia empírica de distribuciones mediante Gemini (`DistributionType.AI_FETCH`).
2. ⚖️ **Interactive AHP CLI Wizard**: Asistente interactivo guiado por terminal para comparaciones por pares.
3. 📉 **Funciones de Utilidad Dinámica**: Funciones de utilidad no lineal (rendimientos decrecientes, curvas S).
4. 📊 **Enhanced Visualization Suite**: Visualizaciones interactivas con Plotly exportables a HTML interactivo.
5. 🐳 **Docker Deployment**: Dockerfile y docker-compose para despliegue productivo de API y Dashboard.
