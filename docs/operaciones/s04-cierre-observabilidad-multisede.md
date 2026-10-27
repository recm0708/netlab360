# NETLAB360 — Plan verificable de cierre de la fase 4

**Corte:** 26 de octubre de 2026, posterior al primer lote S04 offline. **Estado:** fase 4 ABIERTA, con exporter, Prometheus y NOC central/por sede ya comprobados sobre infraestructura desmontada. Este plan contiene puertas técnicas, no da por ejecutadas pruebas futuras. La [issue #4](https://github.com/recm0708/netlab360/issues/4) es la matriz viva de aceptación.

## Hechos comprobados

- Ubuntu 26.04.1 LTS, `ens33=192.168.47.40/24`, puerta de enlace `192.168.47.2`, 3 routers esperados, 4 WAN/8 extremos, 9 VLAN declaradas en SoT S03 `candidate`.
- PR [#55](https://github.com/recm0708/netlab360/pull/55): colector solo lectura `127.0.0.1:9110`, 8 pruebas offline. Prueba real: `source_ok=true`, `topology=offline`, 3 sedes, 25 series, muestra 3,86 segundos.
- PR [#56](https://github.com/recm0708/netlab360/pull/56): Prometheus 3.7.0, `127.0.0.1:9091`, 4 reglas específicas y cuatro escenarios sintéticos promtool; en Ubuntu `scrape_up=1`, `source_up=1`, cero falsas alertas.
- PR [#57](https://github.com/recm0708/netlab360/pull/57): NOC en `127.0.0.1:9120`, vistas central/HQ/S1/S2, 12 pruebas NOC (20 S04 offline en total), API agregada y panel visual en Windows mediante túnel SSH. El panel central completo utiliza dos capturas `S04_03-1` y `S04_03-2`.
- NOC, Prometheus y exporter detenidos normalmente. Postcheck: 9091/9110/9120 libres, Docker/netns vacíos, SSH/gestión intactos, rama `main` limpia.
- Primer lote **7 PNG y 1 CSV SHA-256** auditado y **publicado** mediante [PR #58](https://github.com/recm0708/netlab360/pull/58); inventario remoto comprobado: **114 PNG** totales (S01=90, S02=9, S03=8, S04=7).

## Puertas de aceptación S04

| Puerta | Evidencia exigida | Estado |
|---|---|---|
| G0: exporter/API/Prometheus/NOC OFFLINE | `S04_01` a `S04_06`, manifest de 7 PNG, 20/20 tests, API real, postcheck | **CERRADA:** siete PNG publicados por PR #58 |
| G1: infraestructura activa | 3 FRR, 4 WAN y 9 VLAN realmente desplegadas, OSPF Full 4/2/2, rutas preferidas y 9/9 gateways; `ens33` sin cambios | **CERRADA:** WAN 4/4, OSPF Full 4/2/2, FIB 6/6, loopback ICMP 6/6, LAN 9/9 gateways e ICMP 6/6, gestión intacta |
| G2: telemetría activa | exporter observa los enlaces y VLAN esperados en vivo, Prometheus scrape y series confiables, NOC actualiza las tres sedes; no confundir `active` de Docker con conectividad probada | **Funcionalmente comprobada por APIs reales:** exporter 25 series/3.21 s, WAN 8/8 y VLAN 9/9; Prometheus 9091 target UP, 0 alertas; NOC 9120 tres sedes, fuente fresca y scrape UP. NOC Windows comprobado y capturas S04_07–S04_09 recibidas y auditadas localmente; pendiente publicación de lote 02 |
| G3: incidente y restitución | corte **controlado** de primaria S1 y/o S2 con `ip link` mediante script con `finally`; regla WAN realmente `pending→firing→resolved`, timestamps y ruta backup→primaria; otra sede estable, postcheck | **ACEPTADA TÉCNICAMENTE (S1):** HQ/s1p DOWN 06:05:04Z; alerta pending 06:05:07Z y firing 06:05:13Z en NOC, respaldo s1b, S2 estable, ICMP OK; UP 06:06:07Z, retorno s1p, alerta ausente 06:06:18Z. Pendiente postcheck regresivo y publicación de PNG de G6 |
| G4: disponibilidad de fuentes e histórico | comprobar `UNKNOWN` si falla Docker/permisos o scrape; conservación de series/alertas después de restart según alcance y TSDB real | Pendiente |
| G5: SLI/SLO y notificación | definir SLI comprobable y ventana de muestra, SLO y método de cálculo, o documentar decisión de posponer capacidades concretas; probar envío externo si se incorpora Alertmanager | Pendiente de decisión y prueba |
| G6: aceptación y escritura | capturas con SHA256, pruebas regresión, límites, informe único con sección fase 4 en 5/6/7/8 y aceptación registrada | Pendiente |

## Secuencia protegida para observabilidad ACTIVA

1. **Publicar primero el lote de 7 PNG mediante PR**, sin incluir secretos o state, y verificar hash remoto. La publicación en Git exige árbol limpio antes de repetir S02.
2. **Precheck solamente lectura:** `git status`, red `ens33` y default, estado de Docker/netns, `~/netlab360-bootstrap/s02/runtime/` de los tres FRR, ausencia de estados WAN/LAN operativos previos, versión de binarios, espacio libre y tests. Validar nombres/interfaces contra `inventario/ipam/topologia-s02.yaml` y SoT. Leer `scripts/diagnostico/precheck-s02.sh`, `s02-routers-start.sh`, `s02-wan-links.py`, `s02-lan-vlan.py` y planes. **Nunca reutilizar viejos state de respaldo como activo**.
3. **Snapshot obligatorio de VMware confirmado antes de `up`.** El flag `--snapshot-confirmado` no toma la instantánea por sí mismo; documentar su nombre y fecha, comprobar en VMware Workstation y solo entonces invocar los modos `up` de WAN/LAN. Controlar IP/rutas de gestión antes y después.
4. Arranque por dependencias: **routers FRR aislados → WAN → OSPF/FIB → LAN VLAN y gateways → exporter 9110 → Prometheus 9091 → NOC 9120**. Los validadores S02 originales se utilizan como pruebas de infraestructura activa, **no como un segundo cierre S02**. Verificar cada puerta antes de continuar.
5. Capturas nuevas propuestas: `S04_07_Exporter_Estado_Activo_Tres_Sedes_WAN_VLAN`, `S04_08_Prometheus_Metricas_Activas_Scrape`, `S04_09_NOC_Tres_Sedes_Enlaces_Activos`, `S04_10_Incidente_WAN_Principal_Alerta_Firing`, `S04_11_Recuperacion_WAN_Alerta_Resuelta`, `S04_12_Cierre_Postcheck_Servicios_Red`. Los nombres quedan reservados; no marcar capturas realizadas sin resultado real.
6. Para caída de WAN primaria: usar únicamente `scripts/laboratorio/s02-failover-wan.py S1` o `S2`, que valida propiedad de recursos, conserva otra sede y restaura primaria en `finally`. El evento debe observarse simultáneamente desde Prometheus/NOC. No inducir fallos sin verificar que los servicios de monitoreo están recolectando métricas frescas. `active` de Docker no garantiza OSPF Full.
7. **Orden de retirada:** detener pruebas HTTP/ACL temporales si existieran; NOC → Prometheus → exporter mediante Ctrl+C; **LAN `down` → WAN `down` → Docker Compose de tres routers `down`** únicamente tras validar pertenencia/state; postcheck `ens33`, gateway, contenedores, namespaces, puertos y Git. La instancia B3 no interviene. Nunca ejecutar `docker system prune` ni borrar `terraform.tfstate`.

## Límites técnicos

- `netlab360_s04_wan_admin_up` representa flags administrativos UP/DOWN, no estado OSPF, portadora física ni alcance HTTP. Un apagado voluntario de topología completa da `offline`, series `-1` y **no genera WAN DOWN**.
- Las reglas S04 de `WANAdminDown` y `VLANAdminDown` requieren lectura confiable y `admin_up=0`. No debe afirmarse que una alerta `firing` implica aviso externo entregado.
- Los primeros datos de disponibilidad/SLI se limitan a observaciones realmente recolectadas; no inventar SLA, SLO, latencia o tiempos de convergencia. Cualquier ampliación AIOps/SDN corresponde a fases posteriores.
- La issue #3 de S03 conserva el contrato SoT `candidate` y alcance de recursos externos OpenTofu; el trabajo S04 puede usar el SoT como referencia sin declararlo aceptado globalmente.
- **El informe no contiene anexos**. Código y capturas completas se preparan para TAR técnico independiente de fase 8; redactar el avance S04 en secciones 5/6/7/8 solo con pruebas y figuras finales.

**Continuidad:** revisar [REANUDAR-AQUI](../REANUDAR-AQUI.md), [issue S04 #4](https://github.com/recm0708/netlab360/issues/4), [NOC #15](https://github.com/recm0708/netlab360/issues/15), [telemetría #20](https://github.com/recm0708/netlab360/issues/20), [alertas/SLI #21](https://github.com/recm0708/netlab360/issues/21), [catálogo de incidentes #22](https://github.com/recm0708/netlab360/issues/22).


## Corte de ejecución real — 26/10/2026, 23:58:53 (hora Panamá)

G1 completa con evidencia de terminal real; G2 con muestra `--once` confiable pero sin arranque aún de Prometheus/NOC en la topología activa. [Bitácora](../sesiones/2026-10-26-s04-g1-lan-y-muestra-activa.md). Mantener FRR, WAN y LAN funcionando. Los controles G3–G6 siguen pendientes.

**Política de fases:** S01 y S03 pueden permanecer abiertas mientras se avanza S04–S08; los hitos compartidos solo modifican el estado de la fase a la que pertenezca su criterio. Ninguna dependencia posterior se dará por probada anticipadamente.


## Actualización del 27/10/2026 — G2 funcional validada en red activa

Los tres procesos exporter 9110, Prometheus 9091 y NOC 9120 quedaron iniciados y con APIs comprobadas sobre G1 operativa; [bitácora de resultados](../sesiones/2026-10-27-s04-g2-servicios-activos.md). Pendiente la visualización en Windows y los PNG S04_07–S04_09, que no se presumen capturados. Consolidar Terminal 1 en sesión interactiva SSH con reenvío 9120, y reservar Terminales 2–4 para los tres procesos persistentes. No interrumpir G1/G2 mientras se organiza G3.


## 27/10/2026 — G3 ejecutada y fotografiada

- [Bitácora real G3](../sesiones/2026-10-27-s04-g3-incidente-real-y-recuperacion.md): 60 segundos de corte controlado HQ/s1p, alerta `pending→firing` en Prometheus/NOC, rutas S1 por respaldo s1b, S2 primaria estable, conectividad ICMP y restitución de s1p y alarma. La recuperación se acredita por fuente fresca, métrica `admin_up=1` y ausencia de alerta entre activas, no como notificación externa.
- El operador aportó y se auditó un lote de ocho PNG originales S04_07–11, con S04_09 dividida en cuatro vistas; **ZIP/CSV SHA-256 listos fuera de Git**. Falta transferir al repositorio, validar y publicar; contador de GitHub sin cambios (114 PNG).
- Historial durable básico de incidentes, TSDB, fuente `UNKNOWN` y SLI/SLO constituyen trabajo G4/G5; [topología gráfica animada/semántica avanzada corresponde a S05](https://github.com/recm0708/netlab360/issues/64). La fase S04 **continúa abierta**.
