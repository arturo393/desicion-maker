---
aliases: [SW Diagnosticoremoto, Power Supply Diagnostic, sw-diagnosticoremoto]
tags: [sw-diagnosticoremoto, lumina, power-supply, monitoring, diagnostics]
id: SW-README
title: "SW Diagnóstico Remoto"
type: narrative
category: remote-diagnostics
status: active
related: ["[[decision-maker-moc]]", "[[database-hub]]", "[[index]]"]
created: 2026-08-10
updated: 2026-10-01
---

# SW Diagnóstico Remoto

Material de diagnóstico y propuesta arquitectónica para sistemas de monitoreo remoto.

## Contenido

Los targets son rutas relativas a la raíz del vault (`docs/`). Se escriben completas
y no como nombre de archivo suelto: el vault aplanó esta carpeta y renombró los
archivos a minúsculas, así que un `[[nombre-archivo]]` a secas depende de que ningún
otro documento del vault repita ese nombre.

### 05-Power-Supply / Investigación
- [[sw-diagnosticoremoto/05-power-supply/investigacion/analisis-vistas|Análisis de vistas y dashboards]]
- [[sw-diagnosticoremoto/05-power-supply/investigacion/estado-del-arte|Estado del arte: software de diagnóstico de fuentes de poder]]
- [[sw-diagnosticoremoto/05-power-supply/investigacion/planificacion-desarrollo|Planificación de desarrollo]]
- [[sw-diagnosticoremoto/05-power-supply/investigacion/recomendaciones-tecnicas|Recomendaciones técnicas]]

### Monitoreo-Mina
- [[sw-diagnosticoremoto/monitoreo-mina/propuesta-arquitectura|Propuesta de arquitectura — Monitoreo general en la nube para faenas mineras]]

### Decisión de línea base

El análisis `diagnostico_remoto_linea_base_decision.py` (en `src/decision_maker/analyses/`, v1.2 del 2026-10-01) decide sobre qué línea de sw-diagnosticoremoto se sigue construyendo. Son tres líneas, no dos: `development` (Go + monitor-serial), la VHF vendida (rama v4.1.1-fixed, tag v4.2.0) y su hermana UHF (ulad / uhf-v1.1.0); las dos vendidas salen de v4.1.0 y comparten arquitectura. Cada cliente tiene su propio mini servidor, así que cualquier cambio de arquitectura es una migración en sitio por cliente.

Compara seis opciones (A todo a `development`, B volver a UHF y congelar `development`, C reemplazo de una vez, C2 estrangulamiento, D dos líneas a propósito, E una línea VHF+UHF) con el modo `standard` del orquestador. Corre offline. Hace 18 llamadas a `run_analysis` (el caso base, los shocks de peso y el escenario S4) y cada una deja su juego de reportes en la carpeta `results` del directorio de trabajo, así que conviene correrlo desde la raíz del repo, donde esa carpeta está en `.gitignore`.

**Resultado:** gana **E** —una sola línea de producto VHF+UHF, con `development` como laboratorio—: Monte Carlo 0.752 y TOPSIS 0.836 (0.837 en la corrida v1.1). D queda segunda con 0.719. El ganador cambia a D solo si el peso de `costo_mantencion` baja a un cuarto.

Lo que limita la conclusión:

- Los hechos H1–H11 están medidos en git; los supuestos S1–S6 son juicio.
- **S6 está sin verificar**: que los arreglos que le faltan a v4.2.0 (H11: largo de 2 B en `set_attenuation`, `es_ack`, `_level_dbm` con referencia 0) afecten al diagnóstico VHF en campo. Si no lo afectan, la ventaja de calidad de E sobre B se achica.
- **En el escenario S4 «VLAD25 con fecha» E y D empatan**: sin semilla, una corrida dio D (30-Sep) y otra E (01-Oct). No es un ganador; la fecha de ID-1476 es lo que decide entre las dos.
