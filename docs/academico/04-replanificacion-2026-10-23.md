# NETLAB360 — Replanificación de recuperación, 23/10/2026

**Alcance:** planificación INTERNA adaptable, sin modificar fechas académicas comunicadas ni prometer capacidad todavía no probada. Este archivo contiene decisiones de trabajo del proyecto, no materiales de clase.

## Situación al 23 de octubre
- S01 produjo VM Ubuntu/VMware + gestión VMnet8/SSH, inventario IPAM, demostraciones individuales VLAN/ACL, OSPF HQ–S1 doble WAN, LACP/bonding, automatización B2, NOC/Prometheus y diagnóstico estadístico; 86 PNG y 7 CSV históricas. Pendientes integrales transferidos a S02–S07, **NO declarar S01 completada** ni 72/100 como nota.
- S02 inventario tres sedes/nueve VLAN/cuatro WAN **validado estática y contra rutas actuales**. FRR S02 tres configuraciones generadas y 4/4 tests. Primer Compose `up` FALLÓ al tener `runtime` incompleto: R-HQ/daemons sin frr.conf/vtysh.conf, S1 y S2 vacíos. `docker compose down` retiró solo tres contenedores, logs preservados en Ubuntu. Estado tras reinicio 23/10: Ubuntu/SSH/Docker/open-vm-tools activos, ens33 `192.168.47.40/24`, gateway `.2`, Git `5eed059` al reanudar, cero contenedores S02.
- **No hay routers WAN S02 ni VLAN multisede activos aún**. Captura `S02_05` anterior NO acredita éxito.
- Causa exacta de salida anticipada del paso original no registrada; las comprobaciones `grep` exactas de `daemons` son **hipótesis** porque se observó `R-HQ/daemons` pero faltaron los dos ficheros siguientes. Nuevo preparador elimina ese fallo potencial generando entradas zebra/ospfd explícitas y verificando todo antes de publicar runtime.

## Prioridad académica NO NEGOCIABLE
- **30/10/2026 (faltan 7 días desde 23/10):** mostrar mismo borrador de Word en Teams: introducción, objetivo general/específicos, planteamiento del problema. Issue #47. Título ya enviado, aprobación de docente por confirmar #46. No crear PowerPoint para este corte.
- **13/11/2026:** fundamento técnico y diseño, issue #48. Integrar diagramas y evidencia conforme topología realmente probada hasta entonces.
- Informe final único >=40 páginas y anexos ZIP permitidos junto al informe; defensa final con demostración EN VIVO, PPT al cerrar informe. Fecha final/OVA por confirmar.

## Recuperación técnica en paralelo
1. **P0 S02: cierre de arranque FRR**. Ejecutar tests offline del preparador `tests/test_s02_runtime.py`, `scripts/automatizacion/preparar-runtime-frr-s02.py` con respaldo histórico y `scripts/laboratorio/s02-routers-start.sh` que bloquea up si falta cualquier config/permisos o red de gestión. No tocar `ens33`, ni borrar respaldos; verificar 3 contenedores RUNNING y FRR limpio. Repetir S02_05 solo en éxito real.
2. **P0 S02: WAN OSPF**. Añadir cuatro enlaces veth exclusivamente entre namespaces de los routers mediante script con propiedad/rollback, confirmar cuatro adyacencias FULL desde HQ y dos por sucursal, FIB y rutas de costo 10 frente a 100. Baseline/falla/restauración y logs, sin alterar routing host.
3. **P0 S02: LAN/VLAN**. Crear switches VLAN-aware y 9 VLAN (inicialmente 1 cliente+servicio por sucursal), HTTP y ACL cliente→servidor, luego completar sedes; no equiparar intención IPAM con implementación.
4. **P1 S03 en paralelo**. SoT/Ansible/OpenTofu sobre FRR live SOLO cuando esté funcional el WAN/LAN; preparar archivos y tests offline mientras tanto. Drift histórico en copias no es corrección live.
5. **P1 S04+**. NOC multisedes, LACP/SDN y diagnóstico AIOps progresivos basados en escenario integrado. **IA real/ML evaluado S06 sigue pendiente**; no consumir esta semana replicando pruebas aisladas aprobadas.
6. **Informe en paralelo**: textos de corte 30/10 y 13/11 desde borrador institucional existente, con referencias APA 7; pruebas de S02 alimentan capítulos 7–9. No empezar Manual 02 independiente ni PPT final ahora.

## Mecanismo de avance acelerado
- Ejecutar 3–6 pasos por respuesta **cuando las precondiciones son comprobables y el procedimiento tiene parada por error**; favorecer scripts versionados y tests sobre pegados heredoc extensos.
- No ejecutar `up` tras un fallo de preparación: scripts de gate obligatorios.
- Una captura obligatoria por hito funcional, comando y salida legibles; no usar S02_05 hasta routers 3/3 saludables. Evitar copiar logs de errores de operador como capturas para informe.
- A cada prueba: precheck→estímulo→resultado observado→evidencia→rollback/postcheck, guardar hashes del propio proyecto sin adjuntar materiales docentes.
- Si hace falta reducir carga, aplazar funcionalidad opcional, **NO** omitir requisitos confirmados ni afirmar éxito no demostrado.
