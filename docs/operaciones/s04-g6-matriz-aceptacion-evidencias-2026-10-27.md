# NETLAB360 — Matriz de aceptación técnica G0–G6 de S04

**Ensayos ejecutados el 27/10/2026; cierre interno documentado el 01/11/2026.** Comprobamos el comportamiento de observabilidad multisede con incidentes y recuperación reales. La profesora consideró adecuado el avance presentado el 30/10 y autorizó continuar, según confirmó el equipo. No atribuimos a esa sesión una evaluación final del proyecto ni aprobación individual de un SLA.

| Puerta | Evidencia de ejecución | Resultado |
|---|---|---|
| G0 | Colector, Prometheus y NOC en condición offline; reglas sin falsas alarmas | **Validada** |
| G1 | FRR HQ/S1/S2, cuatro WAN y nueve VLAN; OSPF 4/2/2, FIB/ICMP 6/6, LAN 9/9 y 6/6 | **Validada** |
| G2 | Exportador 9110, 25 series, 8 extremos WAN y 9 VLAN; Prometheus 9091 y NOC 9120 | **Validada** |
| G3 | Caída controlada HQ/s1p durante 60s, alerta pending→firing, selección del respaldo, recuperación y S2 estable | **Validada** |
| G4 | TSDB persistente: 68/68 series WAN y 28/28 muestras de alerta tras reinicio; `UNKNOWN` sin alarmas WAN ficticias; historial SQLite 3/3 tras reinicio del NOC | **Validada** |
| G5 | Scrapes 15m 450/450 (100 %) y 60m 1698/1740 (97,586 %), 42 fallos; presupuesto experimental restante −25 al 99 % | **Medición válida; umbral 99 % NO cumplido en 60m** |
| G6 | Pruebas de regresión, preservación de TSDB/SQLite, integridad SHA/CI y desmontaje LAN→WAN→FRR | **Validada** |

## Decisión y límites

Adoptamos **99 % como referencia académica interna de comparación** y los avisos visuales/locales NOC/SQLite/CSV como alcance implementado. No lo denominamos SLA, no ocultamos el incumplimiento del SLI de recolección de 60m y no afirmamos envío externo de mensajes. `up`, `source_up` y `admin_up` son señales de monitoreo; no acreditan por sí solas disponibilidad extremo a extremo, latencia, jitter ni volumen real de tráfico de usuarios.

## Evidencias preservadas

Mantenemos **22 PNG S04 originales**, registrados en [fase4](../../evidencias/capturas/fase4/README.md) y manifiestos por tres lotes: 7+8+7. Total oficial del proyecto hasta S04: **122 PNG** (83/9/8/22), sin duplicar las capturas administrativas nuevas. El histórico SQLite y la TSDB permanecen fuera de Git con sus respaldos.

La interfaz `ens33` y el gateway VMware se mantuvieron aislados durante los ensayos. El desmontaje original S04 retiró namespaces y contenedores experimentales, con apagado ordenado de Ubuntu en octubre. **La VM se encendió de nuevo el 01/11 para cerrar S01**, así que el estado `Powered Off` actual debe comprobarse únicamente después del apagado de la sesión vigente.

## Relación con el informe

Nuestro borrador **4.6 (113 páginas)** integra implementación S04, pruebas 6.9, análisis 7.10 y conclusiones. Incluye 20 figuras, 13 tablas y 10 referencias. La revisión de avance del 30/10 quedó consignada, sin adelantar los contenidos aún pendientes de S05–S08.

[Medición G5](s04-g5-decision-medida-notificaciones-locales.md) · Continuidad · [Seguimiento S04](https://github.com/recm0708/netlab360/issues/4).
