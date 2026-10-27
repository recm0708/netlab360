**CORTE ACADEMICO VIGENTE — borrador 4.6, 27/10/2026:** informe único de **113 páginas** revisado frente a la guía docente `1457-Formato Proyecto Final.pdf`: portada, introducción, objetivos, problema, fundamento, diseño, implementación, pruebas, análisis, conclusiones, referencias y anexos técnicos remitidos al TAR separado previsto para la entrega final. Contiene **20 figuras (1–20), 13 tablas (1–13), 10 referencias** y **122 PNG oficiales** (S01=83, S02=9, S03=8, S04=22). Capítulos 7.10 y 8 actualizados al cierre técnico de S04; el SLO del 99 % sigue **candidato**, con muestra real 60 min 97,586 %. **Cierre editorial interno del texto hasta S04: validado; aprobación docente pendiente**. S01 conserva cierre SSH/compatibilidad/aceptación; S03 decisiones SoT y alcance de OpenTofu externo; S04 ratificación SLO y aceptación interna/docente. Fechas de revisión previstas: 30/10 y 13/11, no presumir realizadas. La VM se apagó ordenadamente, con sesión SSH cerrada; estado gráfico Powered Off aún por constatar.

*Las menciones posteriores a PDF 4.4/4.5 son registros históricos y no sustituyen este corte vigente.*

# NETLAB360 — Matriz G0–G6 de aceptación técnica S04

**Corte técnico:** 27/10/2026. La validación funcional de los módulos S04 se realizó sobre la VM Ubuntu en operación real. Las decisiones académicas de alcance continúan abiertas.

| Puerta | Resultado verificable | Dictamen |
|---|---|---|
| G0 | Colector, Prometheus y NOC offline con controles sin falsas alarmas | **Aprobada** |
| G1 | FRR HQ/S1/S2, cuatro WAN, nueve VLAN; OSPF 4/2/2, FIB 6/6, ICMP 6/6 y LAN 9/9+6/6 | **Aprobada** |
| G2 | Colector 9110, 25 series, 8 WAN/9 VLAN, Prometheus 9091 y NOC 9120 CENTRAL/HQ/S1/S2 | **Aprobada** |
| G3 | Caída administrativamente controlada HQ/s1p 60s: pending→firing; respaldo s1b, S2 estable; enlace recuperado | **Aprobada** |
| G4 | TSDB tras reinicio 68/68 WAN y 28/28 muestras firing; colector UNKNOWN sin falsas WAN; SQLite 3/3 conservado tras reinicio NOC | **Aprobada** |
| G5 | Scrapes 15m 450/450 (100 %) y 60m 1698/1740 (97,586 %), 42 fallos y error budget candidato −25 | **Mediciones aprobadas; ratificación de 99 % SLO candidato pendiente** |
| G6 | Postcheck operativo, auditoría SHA/CI, respaldos, desmontaje seguro e integración académica hasta cap.6 | **Verificación técnica aprobada; aceptación académica pendiente** |

## Evidencias de la fase

**22 PNG S04 auténticas**, conservadas en [fase4](../../evidencias/capturas/fase4/README.md) con tres manifiestos SHA256 validados: 7 en lote01, 8 en lote02 y 7 en lote03. El repositorio contiene **122 PNG oficiales acumuladas**: 83 S01, 9 S02, 8 S03, 22 S04. Integridad y regresión verificadas por GitHub Actions; los datos dinámicos y el historial SQLite permanecen fuera del repositorio.

## Protección, recuperación y apagado

La prueba WAN G3 mantuvo la interfaz administrativa `ens33` separada y estable. G4 verificó reinicios independientes de Prometheus y NOC sin modificar la topología. G6 documentó prechecks/postchecks, la conservación de TSDB y SQLite, retirada de 12 namespaces LAN, cuatro WAN y tres contenedores FRR. El respaldo TSDB final obtuvo SHA-256 `e7602327d233fcb7dccd60f57fc3230202b1998c592655ec75ed20ef06ba49c1` y el operador ejecutó `sudo systemctl poweroff`; el servidor cerró SSH. **Confirmación externa VMware Powered Off aún pendiente**.

## Límites de aceptación

Las métricas `admin_up` corresponden a interfaces, no latencia, paquetes o disponibilidad contractual. `up` corresponde a scrapes, no servicio de aplicaciones; `source_up` depende de muestras presentes. La TSDB tiene retención limitada y SQLite conserva transiciones, no datos universales de red. No se acreditó entrega de avisos externos, SLO formal aprobado ni IA.

**Escrito:** borrador 4.4 (110 pp) incorpora 5.6 y 6.9, Figuras 16–20 y Tabla 13. Falta análisis S04 en capítulo 7, ajuste de conclusiones/recomendaciones, la secuencia verificada de tablas 1–13, los conteos oficiales e índices/referencias. La reunión Teams del 30/10 y ratificación de SLO aún no han ocurrido al corte.

[Decisión G5](s04-g5-decision-medida-notificaciones-locales.md) · [Plan de continuidad](../REANUDAR-AQUI.md) · [Informe único](../entregables/01-proyecto-investigacion-maestro.md).
