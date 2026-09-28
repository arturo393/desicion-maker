---
aliases: [Propuesta de Arquitectura]
tags: [archive, lumina, sw-diagnosticoremoto]
id: SW-MINA
title: "Propuesta de Arquitectura Monitoreo Mina"
type: archive
category: remote-diagnostics
status: archive
related: ["[[database-hub]]", "[[index]]"]
created: 2026-09-27
updated: 2026-09-27
---

# Propuesta de arquitectura — Monitoreo general en la nube para faenas mineras

**Qué es:** Propuesta de stack tecnológico para un sistema de monitoreo remoto en la nube,
destinado a faenas mineras con conectividad a internet intermitente. Cada sitio corre un
agente edge autónomo que sincroniza con la nube cuando hay enlace.
**Cómo usar:** Leer el stack recomendado (Opción A) y la justificación MCDM; reejecutar la
evaluación con `decision-maker` si se quieren ajustar pesos/criterios.
**Qué NO es:** No es un diseño de implementación completo ni un plan de despliegue. No cubre
seguridad de perímetro ni modelado de datos de cada equipo (se reusa lo existente en
`sw-diagnosticoremoto`).

---

## 1. Contexto y restricción

- **Entorno:** faenas mineras donde el acceso a internet es difícil/intermitente. El edge
  (servidor en la mina) puede pasar horas o días sin link estable.
- **Objetivo:** monitoreo *general en la nube* — muchos sitios, cada uno con un servidor que
  recolecta equipos locales y sube telemetría a un agregador central.
- **Restricción dura:** el edge debe funcionar **offline-first**. Cualquier componente que
  requiera internet para operar queda descartado en el edge.
- **`decision-maker` NO es un componente del stack.** Se usó aquí solo como la herramienta de
  *evaluación* de tecnologías (corrió offline en el lado de diseño). No se instala en las minas.

## 2. Metodología de evaluación

Se corrió un análisis MCDM con `@decision-maker` (`UnifiedDecisionFramework`, modo
`"standard"`: Monte Carlo + TOPSIS + teorías de decisión + sensibilidad + robust + Borda).

- Script: `src/decision_maker/analyses/tech_eval_monitoreo_mina.py`
- Resultado: `results/tech_eval_monitoreo_mina.json`
- Reejecutar (offline, sin display):
  ```bash
  cd /home/arturo/lumina/desicion-maker
  MPLBACKEND=Agg .venv/bin/python src/decision_maker/analyses/tech_eval_monitoreo_mina.py
  ```

**Criterios (peso):** OfflineResilience 0.25 · EdgeInstallEase 0.15 · CostoEficiencia 0.15 ·
Escalabilidad 0.15 · Seguridad 0.15 · Madurez 0.10 · BajoConsumo 0.05.

**Opciones evaluadas:**
- A: MQTT edge (Mosquitto) + TimescaleDB + Grafana
- B: HTTP batch + MongoDB + dashboard propio (reusa stack sw-diagnosticoremoto)
- C: RabbitMQ + Mongo + Go (stack actual) federado por sitio
- D: Kafka / Redpanda edge + cloud
- E: LoRaWAN / IIoT gateway nativo + nube gestionada
- F: Prometheus (remote_write) + Grafana + Alertmanager

## 3. Resultado

| Opción | Score / 1.0 | Veredicto por teoría de decisión |
|---|---|---|
| **A: MQTT edge + TimescaleDB + Grafana** | **0.684** | **Ganador** en las 5 teorías (P95 0.73, P5 0.64, Hurwicz 0.68, Laplace 0.68, regret 0.15) |
| **F: Prometheus (remote_write) + Grafana + Alertmanager** | **0.667** | **Empate técnico** con A (gap 0.017). Gana a A si `OfflineResilience` sube a 0.27 (+7%) |
| D: Kafka / Redpanda | ~0.57 | Lejos; solo compite si se sobrepone offline por sobre todo |
| B / C / E | < A,F | B y C maduros pero pesados en edge; E muy liviano pero ancho de banda tiny |

**Sensibilidad:** A y F están dentro del ruido (0.017). F le gana a A si el peso de
`OfflineResilience` pasa de 0.25 a **0.27** (+7%). D solo supera a A si ese peso llega a 0.36.

**Drivers del ganador (A):** OfflineResilience + EdgeInstallEase + CostoEficiencia (Mosquitto es un
binario único, open source, store-and-forward nativo). F pierde por poco porque su
`OfflineResilience` (remote_write WAL+retry) se modeló 8.5 vs 9 de Mosquitto, y porque Prometheus
es central (el edge no lo instala).

### Prometheus vs TimescaleDB — la decisión real está en el modelo de datos

No es una cuestión de resiliencia offline: **ambos** usan el mismo edge (Mosquitto + SQLite buffer)
y empujan a la nube (remote_write en el caso de F). La diferencia es qué guardás en la nube:

- **TimescaleDB (A):** Postgres + extensión temporal. SQL completo, joins con metadata de equipos,
  contratos y tablas relacionales. Mejor si los datos son *híbridos* (métricas + estado + config).
- **Prometheus (F):** TSDB de métricas, PromQL, **Alertmanager** (alertas nativas) y ecosistema
  enorme. Mejor si es *monitoreo puro de métricas* y querés alertas/reglas estándar. Para
  multi-sitio y retención larga necesita Thanos/Mimir/Cortex (agrega complejidad).

**Recomendación:** A y F son co-ganadores. Elegí A como default por la flexibilidad relacional
(encaja con los contratos existentes de `sw-diagnosticoremoto`), pero si el producto es
monitoreo de métricas puro, **F (Prometheus + Alertmanager) es la opción más natural** y apenas
0.017 debajo.

## 4. Arquitectura recomendada — Opción A

### Edge (por faena / servidor mina) — offline-first
1. **Mosquitto (MQTT)** — broker local. Sesiones persistentes + store-and-forward. Instalación
   offline (binario o wheel vendorizado), sin dependencias de red.
2. **Buffer local SQLite** — cola de telemetría y estado de equipos. No requiere DB externa ni
   servicio adicional en el edge.
3. **Agente de monitoreo local** — recolecta los equipos del sitio. Reusa `monitor-serial` /
   gateway del stack `sw-diagnosticoremoto` ya existente.
4. **Bridge MQTT→TLS** — cuando hay enlace, vacía el buffer hacia la nube (retry/backoff,
   dedupe). No bloquea la operación local si el link cae.
5. **Dashboard local (streamlit u otro)** — *opcional*, para el operador en faena.

### Nube central
- **TimescaleDB** *(o Prometheus, ver §3)* — serie temporal de toda la flota.
  - Si TimescaleDB: el agregador escribe vía SQL; aprovecha joins con metadata/contratos.
  - Si Prometheus: el bridge edge hace **remote_write** (WAL + retry); **Alertmanager** para
    alertas y **Grafana** para dashboards. Para multi-sitio/largo plazo, añadir Thanos/Mimir.
- **Grafana** — dashboards por sitio y agregados.
- **Agregador / ingest** — recibe los bridges.
- **`decision-maker` central (opcional)** — acá **sí** puede correr, incluido el extra `ai`
  (Gemini) en batch, para análisis de flota. Nunca como dependencia de runtime del edge.

## 5. Principio de datos que se aplica

- Distinguir **"sin dato"** de **"dato cero"**. En la nube se muestra la *antigüedad*
  (staleness / "visto hace X"), no el último valor como si fuera actual. La UI y la alarma usan
  el mismo umbral de edad, leído del mismo lugar.

## 6. Por qué no las otras

- **B/C (HTTP batch / RabbitMQ+Go):** funcionales y maduros, pero requieren más servicios en el
  edge (Mongo, Rabbit, Go) → peor `EdgeInstallEase` y `BajoConsumo` en sitios sin red para
  instalar/parchear.
- **D (Kafka/Redpanda):** excelente escalabilidad, pero JVM/Redpanda es pesado y difícil de
  instalar offline; solo compite si se sobrepone la resiliencia offline por sobre todo lo demás.
- **E (LoRaWAN/IIoT):** muy liviano, pero el ancho de banda es tiny — adecuado para sensores
  puntuales, no para monitoreo general de equipos.

## 7. Siguientes pasos sugeridos

- [ ] Definir modelo de datos de telemetría por equipo (reusar contratos de `sw-diagnosticoremoto`).
- [ ] Prototipar el edge: Mosquitto + agente `monitor-serial` + buffer SQLite + bridge.
- [ ] Definir estrategia de autenticación edge→nube (TLS mutuo / tokens por sitio).
- [ ] (Opcional) Crear issue en Jira para trackear el diseño de implementación.

## 8. Referencias

- Análisis: `src/decision_maker/analyses/tech_eval_monitoreo_mina.py`
- Resultado: `results/tech_eval_monitoreo_mina.json`
- Framework: `decision-maker` (núcleo Rust + Python, 100% local; extra `ai` solo en la nube)
- Stack base reutilizable: `sw-diagnosticoremoto` (`monitor-serial`, gateway, contratos)
