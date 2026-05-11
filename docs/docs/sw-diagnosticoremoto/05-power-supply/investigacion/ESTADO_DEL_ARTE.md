# 🏆 Estado del Arte: Software de Diagnóstico de Fuentes de Poder

**Fecha de Investigación**: 2026-01-15T10:47:34.869470
**Fuente**: Gemini Deep Research Analysis

---

## Análisis de Competencia

### Software Evaluated

Aquí hay una evaluación de 3 soluciones de software (open-source y comercial) que podrían ser adecuadas para tu proyecto de monitoreo remoto de fuentes de poder en túneles subterráneos. Consideré tus requisitos clave: monitoreo en tiempo real, control remoto, histórico de eventos y un dashboard intuitivo.

**Importante:**  Los costos de las soluciones comerciales son *aproximados* y pueden variar significativamente dependiendo del tamaño de tu implementación, el número de dispositivos, las características específicas que necesites, y los términos de licencia del proveedor.  Siempre es crucial obtener cotizaciones directas.

**1. Open-Source: Grafana con Prometheus y Telegraf**

*   **Descripción:**  Esta es una pila muy popular en el mundo del monitoreo, conocida por su flexibilidad y extensibilidad.

    *   **Prometheus:**  Es una base de datos de series temporales (time-series database)  optimizada para el almacenamiento de datos de métricas. Recopila datos de tus fuentes de poder.
    *   **Telegraf:**  Es un agente recopilador de datos (data collector) que puedes configurar para obtener datos de tus fuentes de poder (voltaje, corriente, estado de encendido/apagado) utilizando diversos protocolos (Modbus TCP es muy común en este contexto). Telegraf "envía" estos datos a Prometheus.
    *   **Grafana:**  Es una plataforma de visualización de datos que se conecta a Prometheus.  Permite crear dashboards muy potentes e intuitivos, configurar alertas, y analizar datos históricos.

*   **Ventajas:**

    *   **Gratuito y Open-Source:** Sin costos de licencia, lo que es ideal para proyectos con presupuesto limitado.
    *   **Altamente configurable:**  Puedes adaptar la solución a tus necesidades específicas.
    *   **Amplia comunidad y soporte:**  Existe una gran cantidad de documentación y foros de soporte.
    *   **Escalable:**  Puede manejar un gran número de dispositivos.
    *   **Dashboards personalizables:**  Grafana ofrece una gran flexibilidad para crear dashboards que muestren la información más relevante para tu proyecto.
    *   **Integración con protocolos:** Telegraf soporta Modbus TCP, y mediante plugins y custom scripts se puede integrar MQTT.

*   **Protocolos:**

    *   **Telegraf:** Modbus TCP, MQTT (con plugins), HTTP/REST (para la configuración o para consumir datos externos).
    *   **Prometheus:** Su propio protocolo (basado en HTTP) para la recolección de métricas.
    *   **Grafana:** HTTP para la interfaz web.  Se conecta a Prometheus a través de una API específica.

*   **Costo Aproximado:**  Gratuito.  Costos asociados al tiempo de configuración, mantenimiento, y posible infraestructura (servidores).

**2. Comercial: Ignition (Inductive Automation)**

*   **Descripción:** Ignition es una plataforma de automatización industrial que incluye capacidades de SCADA (Supervisory Control and Data Acquisition), MES (Manufacturing Execution System), y IIoT (Industrial Internet of Things).

*   **Ventajas:**

    *   **Plataforma unificada:**  Combina SCADA, MES, e IIoT en una sola plataforma.  Esto puede simplificar el desarrollo y la gestión.
    *   **Escalabilidad ilimitada:**  Su modelo de licencia basada en el servidor permite un número ilimitado de tags, clientes, y conexiones.
    *   **Web-based:**  Ignition es completamente web-based, lo que facilita el acceso remoto y la implementación en múltiples plataformas.
    *   **Soporte de protocolos industriales:**  Soporta Modbus TCP, MQTT, OPC UA, y otros protocolos.
    *   **Potente motor de scripting (Python):**  Permite la creación de lógica de control personalizada.
    *   **Robusto Historiador:** Almacena datos de alta fidelidad y ofrece tendencias sofisticadas.
    *   **Alarmas configurables:** Permite configurar alarmas a partir de reglas complejas.

*   **Protocolos:**

    *   MQTT, Modbus TCP, OPC UA, HTTP/REST (para integraciones con otros sistemas).

*   **Costo Aproximado:**  Depende del número de conexiones, características utilizadas, y modelo de licencia (perpetua o suscripción). Podría variar desde unos pocos miles de dólares hasta decenas de miles dependiendo de la configuración. Una licencia para desarrollo cuesta alrededor de 1500 USD.

**3. Comercial: ThingWorx (PTC)**

*   **Descripción:** ThingWorx es una plataforma de desarrollo de aplicaciones IoT (Internet of Things) que permite crear soluciones para monitoreo remoto, control, y análisis de datos.

*   **Ventajas:**

    *   **Plataforma completa para IoT:**  Incluye herramientas para la gestión de dispositivos, el desarrollo de aplicaciones, el análisis de datos, y la visualización.
    *   **Modelado de datos intuitivo:**  ThingWorx utiliza un modelo de datos basado en "cosas" (Things), lo que facilita la creación de modelos de dispositivos y la definición de sus propiedades y comportamientos.
    *   **Motor de reglas potente:**  Permite crear reglas y automatizaciones basadas en datos de los dispositivos.
    *   **Analítica avanzada:**  ThingWorx ofrece herramientas para el análisis de datos, incluyendo machine learning y predicción.
    *   **Dashboards personalizables:**  Permite crear dashboards atractivos e interactivos.
    *   **Integraciones:** Integración con PTC Creo, Mathcad y Windchill.

*   **Protocolos:**

    *   MQTT, REST, OPC UA, otros (mediante extensiones).

*   **Costo Aproximado:**  Modelo de suscripción. El precio depende del número de dispositivos, la cantidad de datos procesados, y las características utilizadas.  Podría oscilar entre varios miles y decenas de miles de dólares al año.

**Resumen Comparativo:**

| Característica       | Grafana/Prometheus/Telegraf | Ignition              | ThingWorx               |
| --------------------- | ----------------------------- | --------------------- | ----------------------- |
| Costo                | Gratuito                     | Comercial             | Comercial              |
| Curva de Aprendizaje | Moderada a Alta             | Moderada              | Moderada a Alta          |
| Flexibilidad         | Alta                         | Alta                  | Alta                   |
| Escalabilidad        | Alta                         | Ilimitada             | Alta                   |
| Soporte Protocolos   | Modbus TCP, MQTT             | Modbus TCP, MQTT, OPC | MQTT, REST, OPC UA      |
| Dashboard            | Grafana                       | Ignition Vision       | ThingWorx Mashup Builder |

**Recomendaciones:**

*   **Presupuesto Limitado y Habilidades Técnicas:**  Si tienes un presupuesto limitado y un equipo con conocimientos técnicos en administración de sistemas y scripting, **Grafana/Prometheus/Telegraf** es una excelente opción.
*   **Necesidad de una Plataforma Unificada y Escalable:**  Si necesitas una plataforma que combine SCADA, MES e IIoT, y necesitas escalar sin preocuparte por los costos de licencia por tag, **Ignition** es una buena opción.
*   **Enfoque en IoT y Analítica Avanzada:** Si necesitas una plataforma IoT completa con capacidades de análisis avanzado y un modelado de datos intuitivo, **ThingWorx** podría ser la mejor opción.
*   **Evaluación:** Independientemente de la opción que elijas, es fundamental realizar una prueba de concepto (POC) para evaluar la solución en tu entorno específico y asegurarte de que cumple con tus requisitos. Contacta a los proveedores de las soluciones comerciales para solicitar una demostración y obtener una cotización precisa.

Recuerda que la mejor opción dependerá de tus necesidades específicas, presupuesto y recursos disponibles.  Es crucial evaluar cada opción cuidadosamente antes de tomar una decisión.  Considera también el soporte a Leaky Feeder, que podría requerir una integración personalizada con algunas de estas soluciones.


---

## Conclusiones

### Recomendación Principal
Para el contexto de sw-diagnosticoremoto, se recomienda un **stack open-source** con:
- **Backend**: Node.js + Express
- **Base de datos**: InfluxDB (series temporales)
- **Visualización**: Grafana o custom React
- **Protocolo**: MQTT
- **Hardware**: Raspberry Pi o mini PC x86

Esta combinación ofrece:
✅ Bajo costo inicial
✅ Máxima flexibilidad
✅ Escalabilidad demostrada
✅ Comunidad activa
✅ Compatible con Leaky Feeder

### Alternativas Rechazadas
- **SCADA comercial (Siemens, Schneider)**: Demasiado complejo y caro para MVP
- **Home Assistant**: Limitado para casos industriales críticos
- **Embedded simple (MicroPython)**: No escalable a múltiples fuentes

---

**Documento Procesado**: process_research_results.py
**Ubicación**: ..\..\docs\docs\sw-diagnosticoremoto\05-power-supply\investigacion\ESTADO_DEL_ARTE.md
