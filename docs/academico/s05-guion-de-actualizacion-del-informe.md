# NETLAB360 · Guion de incorporación académica de la fase S05

**Corte técnico verificable:** 11 de noviembre de 2026. **Estado editorial:** contenido de apoyo **todavía NO incorporado al archivo Word maestro** del equipo. El objetivo es actualizar **el mismo informe académico único**, no redactar un segundo informe. Se respeta la organización documentada en `docs/entregables/00-politica-editorial-y-entrega-acumulativa.md`: capítulos 5 Implementación, 6 Pruebas y validación, 7 Análisis de resultados y 8 Conclusiones y recomendaciones; sin capítulo de anexos. La numeración final de figuras/tablas se decidirá comparando el último Word/PDF, no inventando correlativos.

## Resumen del estado S05 para redacción

| Función | Estado técnico verificado | Presentación académica |
| --- | --- | --- |
| Plataforma de tres sedes HQ/S1/S2 | Tres routers FRR y tres switches; nueve VLAN y nueve hosts, cuatro WAN primaria/respaldo, 12 namespaces LAN S02 | Arquitectura previa reusada; **no** presentarla como creada enteramente por S05 |
| Piloto LACP P1, multistream | IEEE 802.3ad en enlaces `veth`, dos miembros, `layer3+4`, 1 flujo 120,06 Mb/s y 8 flujos 959,81 Mb/s con límite de 120 Mb/s por flujo; conmutación de puertos 2→1→2; 553 retransmisiones TCP en prueba de falla/retorno | Resultado de laboratorio aislado; no capacidad nominal de NIC ni garantía de pérdidas cero |
| Comparación LACP P1B | 1 flujo/2 miembros 70,21 Gb/s; 8/2 113,30 Gb/s; 8/1 127,39 Gb/s; 8/2 restaurados 118,30 Gb/s; CPU y entorno virtual condicionan interpretación | No concluir que un enlace único es intrínsecamente superior ni extrapolar a 10/40/100 GbE físico |
| Topología corporativa NOC | Visor web con tres sedes, VLAN, routers/switches, WAN principales y de respaldo, inspector FIB, indicadores de estado y leyenda, hora Panamá de la VM | Distinguir estados reales (active, offline, unknown) de selección visual del usuario |
| Failover observado HQ–S1 | Primaria `s1p` → respaldo `s1b` → primaria `s1p`, next-hop `10.78.0.2→10.78.0.6→10.78.0.2`, observador JSONL 119 muestras (55 PRINCIPAL, 64 RESPALDO), ventana de falla 25s; S2 estable y gestión intacta | Conmutación **de ruta FIB** y continuidad de conectividad; no afirmar servicio HTTP disponible ni cero pérdida |
| Persistencia del NOC | Helper de lectura root de comando fijo `snapshot` y dos servicios `systemd` como usuario normal; Lote 84R-I y J pasaron, S04 `source_ok=True`, NOC `routing.available=True` | Instalación validada en VM, **pendiente prueba de reinicio/reconexión SSH para acreditar independencia completa de sesión** |
| HA de servidores | Precheck S05 HA válido: VLAN servicios HQ120/S1220/S2320; IPs candidatas sin asignación observada; script de red con plan/rollback versionado, **sin despliegue HA** | Solo diseño y preflight; no describir dos servidores HA como activos |
| OVS/Faucet S05 | Issue #23 abierta, no despliegue real S05 | Mantener como alcance previsto, no como resultado experimental |

## Propuesta de incorporación al capítulo 5 — Implementación

### Texto base 5.x: Redundancia WAN y operación visual multisede

La implementación de NETLAB360 amplió la plataforma multisede compuesta por una sede central (HQ) y dos sucursales (S1 y S2), manteniendo el enrutamiento dinámico de FRRouting y las redes LAN segmentadas por VLAN. Se utilizó una topología corporativa interactiva que integra tres routers, tres switches virtuales, nueve segmentos VLAN con equipos de prueba y cuatro circuitos WAN, diferenciando las rutas principales de las conexiones de respaldo. El visor consulta el estado de la infraestructura y la información de encaminamiento del router de la sede central, lo que permite identificar la interfaz seleccionada por la tabla FIB y distinguirla de la disponibilidad administrativa de una interfaz.

### Texto base 5.x: Agregación de enlaces LACP

Se desarrollaron dos experimentos complementarios de agregación de enlaces mediante IEEE 802.3ad, utilizando pares de interfaces virtuales y la política de distribución `layer3+4`. El primer experimento comparó la transmisión de un único flujo TCP con ocho flujos simultáneos, bajo una limitación de 120 Mb/s por flujo. El segundo experimento repitió escenarios de uno y ocho flujos sin ese limitador, incorporando afinidad de CPU y pruebas con dos enlaces, uno solo y posterior restauración. Ambas ejecuciones se mantuvieron aisladas de la interfaz administrativa de la máquina virtual y conservaron registros originales para contrastar las mediciones.

### Texto base 5.x: Supervisión persistente con privilegios mínimos

Para desacoplar la observabilidad de las conexiones SSH interactivas, el colector S04 y el visor topológico S05 se configuraron como servicios independientes administrados por `systemd`. Los procesos HTTP permanecen vinculados a la dirección local de la máquina virtual y se ejecutan bajo una cuenta no privilegiada. Las consultas a los contenedores FRRouting y a las rutas FIB se realizan a través de un componente auxiliar de lectura restringida, que verifica los identificadores esperados de los routers y limita sus operaciones a la obtención de información de interfaces y rutas. La instalación y el acceso a las fuentes se validaron en la VM, quedando por confirmar el funcionamiento tras una reconexión remota independiente.

## Propuesta de incorporación al capítulo 6 — Pruebas y validación

### Texto base 6.x: Resultados de LACP

En el experimento LACP limitado, un flujo obtuvo aproximadamente 120,06 Mb/s y ocho flujos alcanzaron 959,81 Mb/s, sin retransmisiones TCP durante esas dos mediciones. En la simulación de falla y recuperación de un miembro, los agregadores pasaron de dos enlaces activos a uno y retornaron a dos, con un rendimiento medio de 960,31 Mb/s y 553 retransmisiones. La presencia de retransmisiones impide presentar el evento como una transición sin degradación. En la comparación sin limitador, se registraron aproximadamente 70,21 Gb/s con un flujo, 113,30 Gb/s con ocho flujos y dos miembros, 127,39 Gb/s con ocho flujos y uno solo, y 118,30 Gb/s tras restaurar el segundo miembro. Las tasas se interpretan como indicadores del comportamiento de una topología virtual sometida a restricciones de procesamiento.

### Texto base 6.x: Conmutación observada por el NOC

La verificación del failover HQ–S1 se instrumentó mediante un observador que registró 119 muestras de estado, de las cuales 55 correspondieron a la ruta principal y 64 al respaldo. Durante la prueba se deshabilitó temporalmente el enlace WAN principal de S1, se constató el cambio de la FIB desde `s1p` (siguiente salto `10.78.0.2`) hacia `s1b` (`10.78.0.6`) y se comprobó el retorno a `s1p` tras restaurar el enlace. La sucursal S2 mantuvo su ruta principal, mientras la interfaz de administración de la VM conservó la dirección `192.168.47.40/24` y su gateway `192.168.47.2`. Los registros JSONL, las salidas del simulador y los manifiestos SHA-256 permiten contrastar estos resultados.

### Texto base 6.x: Regresiones y persistencia del NOC

Las pruebas automatizadas más recientes ejecutaron 50 casos de S05 sin errores, abarcando la topología, el estado del encaminamiento, los componentes de observabilidad y los contratos de lectura segura. En la máquina virtual también se verificó que el observador privilegiado reconociera los tres routers y devolviera las rutas principales esperadas, y que ambos servicios `systemd` quedaran activos con telemetría y FIB disponibles. El siguiente control operativo consiste en desconectar la sesión SSH y verificar la permanencia de los servicios desde una conexión nueva, sin reiniciarlos manualmente.

## Propuesta de incorporación al capítulo 7 — Análisis de resultados

El escenario experimental muestra dos aspectos diferentes de la redundancia. La agregación LACP distribuyó flujos TCP entre miembros activos y permitió observar la reducción y recuperación del conjunto de puertos, pero sus mediciones no determinan el ancho de banda disponible en enlaces físicos equivalentes. Por otra parte, la conmutación de WAN evidenció la selección automática de un camino alternativo mediante la FIB, y el visor NOC representó esa transición de forma coherente con la información del router. Estas evidencias no acreditan por sí solas alta disponibilidad de servidores ni continuidad ininterrumpida de una aplicación: ambas propiedades requieren pruebas adicionales de servicios y un mecanismo de conmutación de backend, previstos en los siguientes componentes de S05.

## Tablas y figuras sugeridas (sin numeración definitiva)

- **Tabla de LACP:** escenario, flujos, miembros, tasa observada, retransmisiones, consideraciones de CPU y límite.
- **Tabla de conmutación:** estado inicial, falla, respaldo, recuperación; interfaz FIB, next-hop y fuente de observación.
- **Figura del NOC:** mapa HQ–S1–S2 con WAN principal/respaldo y leyenda legible; separar panorama normal del estado de failover.
- **Figura de servicios persistentes:** diagrama conceptual `systemd → S04/NOC → helper de lectura → FRR/FIB`; no presentarlo como infraestructura HA física.
- **Figuras de HA y OVS/Faucet:** solo después del despliegue y pruebas reales.

## Pendientes editoriales y fuentes de evidencia

1. Comparar el último Word/PDF maestro con el control interno del 01/11 (borrador 4.6, 113 páginas, 20 figuras, 13 tablas, 122 capturas S01–S04). Los números **no** son un conteo vigente confirmado después de S05.
2. Insertar únicamente los párrafos técnicos respaldados por salidas, ajustar tiempo verbal y nomenclatura; incorporar S05 a capítulos 5/6/7 y conclusiones cuando existan pruebas de HA y SDN.
3. Validar las capturas S05_29–33 y los registros TAR/JSONL; no afirmar que las imágenes están versionadas por GitHub hasta efectuar importación binaria y hashes.
4. No agregar bibliografía inventada; incorporar citas y referencias APA 7 solo cuando se usan afirmaciones derivadas de literatura externa, mientras los resultados de la VM son evidencia primaria del proyecto.
5. Mantener este archivo como **guion de trabajo**, no como documento final ni segundo informe.

**Referencias internas:** `docs/sesiones/2026-11-10-s05-lacp-multistream-piloto-validado.md`, `docs/sesiones/2026-11-10-s05-lacp-p1b-capacidad-validada.md`, `docs/sesiones/2026-11-11-s05-observacion-failover-s1-validada.md`, `docs/operacion/s05-servicios-systemd-sin-tmux.md`, issues [#5](https://github.com/recm0708/netlab360/issues/5), [#31](https://github.com/recm0708/netlab360/issues/31), [#32](https://github.com/recm0708/netlab360/issues/32), [#64](https://github.com/recm0708/netlab360/issues/64).
