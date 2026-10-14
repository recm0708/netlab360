# NETLAB360 — Selección editorial de figuras y tablas para DOS documentos

**Corte 14/10/2026; índices de los dos documentos aprobados por el usuario:** 86 PNG publicados y siete CSV; lista basada en rutas reales del repositorio. **No insertar automáticamente todos los PNG.** Las numeraciones de «Figura N» y «Tabla N» serán continuas pero **independientes para cada documento**, a lo largo de las fases ejecutadas. Las portadas son responsabilidad del usuario.

## Documento 01 — Diseño, desarrollo y evaluación del proyecto

Las figuras del trabajo académico deben justificar una explicación de arquitectura, un resultado o un análisis. Selección inicial:

| Apartado | Imagen/tablas candidatas | Motivo |
|---|---|---|
| Arquitectura general y topología | Esquema elaborado desde IPAM; por dibujar y validar | Mostrar diseño previsto y distinguirlo de escenarios probados |
| Configuración de rutas WAN y OSPF | `IAC_B2_03_OSPF_y_Rutas_IAC.png` | Relacionar decisiones de enrutamiento con observaciones |
| Observabilidad y detección de falla | `B3_12_Alerta_Prometheus_WAN_Down.png` | Evidenciar alarma real |
| Análisis estadístico de S01 | `B4_05_Perfil_Estadistico_Real.png` | Presentar resultados descriptivos y limitaciones, no métricas ML |
| Comparación entre objetivos y cobertura | Tabla propia basada en matriz S01 | Interpretar conformidad parcial y condiciones sin completar |

En el relato de **incidentes técnicos reales**, usar una figura específica solo cuando documente el síntoma, la mitigación o la verificación. Si el log es suficiente, se cita sin forzar figura. No incorporar errores personales ni forzar historia de errores donde no los hubo.

## Documento 02 — Manual técnico integral (implementación + administración + uso)

Figuras de procedimientos reales, seleccionadas para explicar preparación, comandos, pruebas y comportamiento de usuario:

| Módulo/caso de uso | Ruta del PNG comprobada |
|---|---|
| Trunk 802.1Q | `evidencias/capturas/B2_L2_02_Trunk_8021Q_VLAN110_120.png` |
| ACL HTTP | `evidencias/capturas/B2_L2_06_ACL_HTTP_Permitido_Bloqueado.png` |
| WAN principal | `evidencias/capturas/B2_L3_01_HTTP_WAN_Principal.png` |
| WAN respaldo | `evidencias/capturas/B2_L3_02_HTTP_WAN_Respaldo.png` |
| WAN restaurada | `evidencias/capturas/B2_L3_03_HTTP_WAN_Restaurada.png` |
| LACP dos enlaces (4 fragmentos) | `evidencias/capturas/B2_LACP_01_Agregacion_Dos_Enlaces-1.png` a `-4.png` |
| LACP superviviente (4 fragmentos) | `evidencias/capturas/B2_LACP_02_Falla_Un_Enlace-1.png` a `-4.png` |
| Bond activo-respaldo virtual | `evidencias/capturas/B2_DUALNIC_02_Conmutacion_Respaldo.png` |
| IaC→FRR OSPF real | `evidencias/capturas/IAC_B2_03_OSPF_y_Rutas_IAC.png` |
| Drift y reconciliación de archivos, no FRR vivo | `evidencias/capturas/IAC_S01_08_Drift_Detectado.png` y `IAC_S01_09_Reconciliacion.png` |
| Panel NOC realmente disponible | `evidencias/capturas/B3_08_Dashboard_NOC_En_Vivo.png` |
| Alerta firing y recuperación | `evidencias/capturas/B3_12_Alerta_Prometheus_WAN_Down.png` y `B3_13_Alerta_Prometheus_Resuelta.png` |
| Diagnóstico y resultados históricos | `evidencias/capturas/B4_08_Diagnostico_Reglas_Reales.png` |
| Sensibilidad descriptiva del umbral | `evidencias/capturas/B4_10_Sensibilidad_Umbral_RTT.png` |
| Postcheck de la VM | `LOTE06_Postcheck_Publicacion.png` recibido, **NO versionado/auditado como PNG de Git** al corte |

El manual debe incluir posteriormente capturas de **instalación desde cero** si son necesarias y realmente están disponibles o se generan en una reproducción autorizada. No inventar instalación visual que no exista.

## APA 7 — Convención obligatoria de figuras y tablas

Primero introducir/analizar la figura o tabla en el texto y referirse a «Figura 1» o «Tabla 1»; después número en negrita y título en cursiva (figura/tabla, estilo APA7), contenido y **Nota.** si aclara fuente, elaboración, abreviaturas, contexto de medición o alcance. Para capturas propias, señalar su procedencia de pruebas NETLAB360, cuando corresponda. Las tablas deben interpretarse con un párrafo anterior y uno posterior si procede; no presentar métricas sin unidad ni metodología.

No hay un tercer documento de usuario aparte. **Las capturas de operación del NOC forman parte del Documento 02**. Ningún texto de manual debe narrar la secuencia histórica de fallos del equipo: usar soluciones preventivas contextuales.
