# Históricos de issues S08 antes de reconciliación al cierre de 145B

No ejecutar tareas marcadas históricas. Ver checklists actuales de GitHub.


---

# ISSUE 27 [019] Informe maestro 4.6 hasta S04; incorporar S05 tras aceptación práctica (estado open)

# Informe académico único NETLAB360

**Corte 01/11/2026:** borrador **4.6 de 113 páginas**, revisado internamente frente a la guía. Contiene **20 figuras numeradas (1–20)**, **13 tablas (1–13)**, **10 referencias** y los resultados de S01–S04. Se conserva un documento académico único en Word/PDF; el TAR técnico se entrega por separado conforme al acuerdo académico.

## Contenido acreditado

- [x] Portada, introducción, objetivos, planteamiento, fundamento y diseño.
- [x] Capítulo 5: implementación de S01–S04, incluidas secciones S03 5.5 y S04 5.6.
- [x] Capítulo 6: pruebas y validación hasta S04, incluyendo métricas 15m 450/450 y 60m 1698/1740 (97,586 %) y el umbral 99 % **no alcanzado** en 60m.
- [x] Capítulo 7: interpretación de S04 en 7.10 y correspondencia con las tablas.
- [x] Capítulo 8: conclusiones y recomendaciones incorporan S04.
- [x] Auditoría de figuras, tablas, coherencia cuantitativa, referencias y 122 PNG oficiales (83/9/8/22).
- [x] Revisión académica de avance del **30/10/2026 realizada**; según el equipo, la profesora indicó que todo estaba bien y autorizó continuar con el siguiente entregable.

## Trabajo restante de este artefacto (S08)

- [ ] Incorporar únicamente resultados **reales** de S05–S08 cuando existan, con análisis y citas correspondientes.
- [ ] Atender las observaciones, si las hubiera, en la siguiente revisión del **13/11/2026**.
- [ ] Preparar exportación Word/PDF final, índices y referencias al cierre del proyecto.
- [ ] Completar TAR de scripts/configuraciones y PowerPoint de demostración por sus issues propias.

**No corresponde volver a editar S01–S04 solo para actualizar títulos de issues.** La conformidad de un avance no implica que el informe final completo haya sido calificado.
[Revisión del 30/10](https://github.com/recm0708/netlab360/issues/47) · [S08](https://github.com/recm0708/netlab360/issues/8).

## Continuidad 14/11/2026

- [x] Estado de S05 recopilado en [tablero vigente](https://github.com/recm0708/netlab360/blob/main/docs/gestion/s05-tablero-vigente.md): HTTP HA real y bond HQ operativos; no afirmar que OVS/Faucet o LACP S1/S2 estén realizados.
- [x] [Guion S05](https://github.com/recm0708/netlab360/blob/main/docs/academico/s05-guion-de-actualizacion-del-informe.md) marcado como **obsoleto en partes** y enlazado al estado actualizado para evitar copiar resultados superados.
- [ ] Tras la aceptación de S05, incorporar implementación/pruebas/análisis/conclusiones al **mismo Word/PDF maestro** y rehacer coherencia de figuras, tablas, citas APA7; esta edición **no se ha ejecutado**.
- [ ] Confirmar dictamen de revisión docente 13/11 ([#48](https://github.com/recm0708/netlab360/issues/48)) sin atribuir aprobación no documentada.

La exportación final y otros entregables permanecen en S08.


---

# ISSUE 34 [026] Compatibilidad base validada; extensiones S05–S08 pendientes (estado open)

# NETLAB360 — Compatibilidad y versiones S01–S08

**Corte de revisión:** 01/11/2026. S01 cuenta con identificación completa del entorno de arranque y almacenamiento disponible; el origen exacto de la imagen/ISO de instalación **no es verificable** con los datos preservados y se registra como limitación de procedencia, no como falla de compatibilidad.

## Base técnica comprobada (S01–S04)

- [x] VMware Workstation Pro 26.0.1, `netlab360-lab` en VMware Virtual Platform y Ubuntu Desktop 26.04.1 LTS, kernel 7.0.0-38-generic.
- [x] Firmware virtual BIOS 6.00 fechado 17/02/2026, arranque `BIOS_LEGACY`; no se detectó EFI en `/sys/firmware/efi`.
- [x] Disco virtual `sda` de 160 GB, partición `sda2` raíz ext4 y partición auxiliar `sda1` de 1 MiB.
- [x] `ens33` con `192.168.47.40/24`, ruta por defecto `via 192.168.47.2`; SSH, Docker y open-vm-tools activos.
- [x] Laboratorios FRRouting 10.7.1, OSPF dual-WAN, VLAN/ACL, Ansible Core 2.20.1, OpenTofu 1.13.1 y Python 3.14.4 comprobados con las pruebas de S01–S04.
- [x] **Limitación declarada:** ISO/imagen exacta de origen de la instalación no documentada; no se deduce del firmware y no es preciso reinstalar Ubuntu para cerrarla.

## Seguimiento transversal, no bloqueante de S01

- [ ] Evaluar compatibilidad OVS/Faucet al implementarlos en S05; no se atribuyen verificaciones a componentes aún inexistentes.
- [ ] Consolidar dependencias de análisis/IA y actualización de documentación de compatibilidad al ejecutar S06.
- [ ] Preparar matriz de versiones definitiva y pruebas de entrega del TAR técnico en S08.

**Alcance:** S01 se acepta con la limitación explícita del origen de instalación. Esta issue sigue abierta por trabajos futuros S05–S08, no por un fallo del firmware S01.

[S01](https://github.com/recm0708/netlab360/issues/1) · [Continuidad](https://github.com/recm0708/netlab360/blob/main/docs/REANUDAR-AQUI.md)



---

# ISSUE 36 [028] Hitos académicos: 30/10 realizado; dictamen 13/11 por confirmar y cierre S08 pendiente (estado open)

## Estado académico actualizado 14/11/2026 — seguimiento S05/S08

- [x] Evidencias S05 de HTTP HA, NOC y LACP HQ integradas en [tablero vigente](https://github.com/recm0708/netlab360/blob/main/docs/gestion/s05-tablero-vigente.md); las antiguas instrucciones operativas no deben repetirse.
La revisión docente prevista para el **13/11** aún no tiene dictamen verificable en los registros aportados. Las tareas vigentes están en la sección «Hitos todavía por acreditar»; la recuperación tras reinicio se sigue por [#106](https://github.com/recm0708/netlab360/issues/106).

## CORTE HISTÓRICO VALIDADO 11/11/2026 — servicios systemd S04/NOC ACTIVOS y 50 pruebas S05

- [x] **Regresión S05 ampliada:** el operador hizo `git pull --ff-only` de `2a3f899` a `8fde8ea`; **50 pruebas S05 pasaron**, incluyendo seis pruebas del observador seguro. El lote `84R-H` dejó de avanzar en `grep -Fq 'Ran 46 tests'`; no es un fallo de las pruebas sino un conteo desactualizado. Sus verificaciones posteriores de binarios, archivos destino y puertos no se ejecutaron en esa pasada; resultados equivalentes posteriores confirman instalación y APIs.
- [x] **Lote 84R-I ejecutado en VM**: helper root-owned instalado en `/usr/local/libexec/netlab360-observer`, `sudoers` limitado a comando exacto, `sudo visudo -cf` da `parsed OK`; `sudo -n ... snapshot` verifica 3 routers y FIB S1 `s1p/10.78.0.2`, S2 `s2p/10.78.0.10`; `S05_OBSERVADOR_PRIVILEGIADO=OK`, `LOTE84R_I=OK`.
- [x] **Lote 84R-J ejecutado en VM**: dos units `netlab360-s04-exporter.service` y `netlab360-s05-noc.service` instaladas, habilitadas y **ambas active**. API S04 `source_ok=True`, `topology=active`; NOC `telemetry.available=True`, `routing.available=True`, FIB S1/S2 principal; `S05_SERVICIOS_SYSTEMD=OK`, `LOTE84R_J=OK`.
- [x] **Independencia SSH verificada:** reconexión en lotes 84R-L y comprobación posterior en 105/111D-S: exporter y NOC con `systemd` activos, APIs y FIB principal observados sin iniciarlos manualmente; hubo resets de SSH intermitentes cuya causa no está acreditada.
- [x] **Lotes 84–86 completados posteriormente:** tres namespaces HA, IP/gateway, ICMP desde S2, VLAN y ownership; lotes 87–94 completaron servidores HTTP HQ/S1, frontal HQ, fallo/retorno HTTP y observación NOC. Conservar servicios, no repetir `up`.
- [x] **Guion académico S05 preparado para Word único**, con advertencia editorial y [tablero vigente](https://github.com/recm0708/netlab360/blob/main/docs/gestion/s05-tablero-vigente.md). Word maestro no actualizado; **HA HTTP sí fue implementada y probada** después del corte original, **OVS/Faucet continúa pendiente**.

Las secciones posteriores más antiguas son **historial** y sus casillas de instalación aún pendientes quedaron superadas por las pruebas 84R-I/J aquí citadas. Milestone S05 sigue ABIERTA.

# Seguimiento académico NETLAB360

## Acuerdos y eventos

- [x] Informe académico **único** con estructura y referencias APA; anexos técnicos en TAR independiente conforme al acuerdo de entrega, sin segundo informe paralelo.
- [x] Evidencia real en GitHub, PowerPoint y demostración final a completar durante S08.
- [x] Título académico comunicado por Teams el 17/10/2026; consulta cerrada sin observaciones registradas [#46](https://github.com/recm0708/netlab360/issues/46), sin afirmar respuesta formal individual.
- [x] **30/10/2026:** revisión realizada. Según informó el equipo el 01/11, la profesora manifestó que el trabajo presentado estaba bien y autorizó pasar al siguiente entregable [#47](https://github.com/recm0708/netlab360/issues/47).
- [x] Informe de corte 4.6 (113 pp., 20 figuras, 13 tablas) revisado internamente hasta S04.

## Hitos todavía por acreditar

- [ ] **Revisión prevista 13/11/2026 (fecha ya transcurrida):** falta constancia verificable de realización y dictamen auténtico [#48](https://github.com/recm0708/netlab360/issues/48). No presumir aprobación ni ausencia de observaciones. Confirmar título definitivo para portada cuando corresponda.
- [ ] Incorporar S05–S08 al único informe y revisar citas, índices y conclusiones [#27](https://github.com/recm0708/netlab360/issues/27).
- [ ] Preparar presentación, demostración y TAR técnico sin credenciales [#44](https://github.com/recm0708/netlab360/issues/44), [#45](https://github.com/recm0708/netlab360/issues/45).
- [ ] Confirmar formato y fecha exacta de defensa final y si se solicita OVA/OVF; no asumir obligación de exportación.

**No confundir aprobación de un avance con aceptación final del proyecto**, ni crear un manual independiente fuera de requisitos.



---

# ISSUE 106 [S08] Restauración reproducible de namespaces y servicios tras reinicio de la VM (estado open)

## Motivación
Actualmente NETLAB360 S02, HA HTTP y LACP HQ dependen de network namespaces creados en tiempo de ejecución. Los servicios `systemd` de HTTP/monitor S05 no deben habilitarse al arranque mientras no exista restauración segura y ordenada de las redes. **No reiniciar la VM ahora**: se perdería el estado activo del laboratorio y podrían quedar servicios dependientes sin red.

## Alcance S08 (no ampliar artificialmente S05)

- [ ] Auditar dependencias de arranque: S02 switch/hosts/router FRR, redes S05 HA, clientes LACP, servicios NOC/observabilidad y monitor S2, systemd y permisos.
- [ ] Diseñar una reconstrucción **idempotente** por propietario, con orden de precheck/creación/verificación; no eliminar recursos ni archivos de otras prácticas.
- [ ] Probar apagado y reinicio de manera controlada **únicamente después de respaldos y evidencias completas**, con autorización operativa y mecanismo de recuperación.
- [ ] Verificar que las IP `ens33=192.168.47.40/24` / gateway `192.168.47.2`, OSPF, WAN, HA HTTP, NOC y LACP se restauran sin conflicto.
- [ ] Documentar procedimientos para entrega/demostración de la VM y requisitos de OVA/OVF solo si la docente lo exige (véase #29).

**No completar desde un snapshot antiguo ni hacer una prueba de reboot mientras S05 esté en desarrollo.**

Referencias: [tablero S05](https://github.com/recm0708/netlab360/blob/main/docs/gestion/s05-tablero-vigente.md), [entrega S08](https://github.com/recm0708/netlab360/issues/8).
## Priorización actualizada 14/11/2026 — reinicio Windows solo tras práctica y recuperación

El operador necesita reiniciar su **PC física Windows**, pero decidió hacerlo solamente cuando la parte práctica esté terminada y podamos actualizar el escrito. Los tres bonds HQ/S1/S2 operan con namespaces efímeros y pruebas 2→1→2 concluidas. **No reiniciar Windows con VMware corriendo ni ejecutar reboot de Ubuntu ahora.**

- [ ] Tras terminar S05/S06/S07, elaborar respaldo íntegro de evidencias/estado y verificar copia externa/hashes; evitar respaldos duplicados no verificados.
- [ ] Comprobar recuperación idempotente de S02, servicios HA, LACP HQ/S1/S2, NOC y SDN/IA que corresponda, con orden de dependencias y rollback.
- [ ] Ejecutar ensayo de apagado/reconstrucción únicamente cuando no se pongan en riesgo pruebas o datos y la ruta de recuperación sea verificable.
- [ ] Una vez verificada la reanudación, cerrar Ubuntu de manera ordenada, confirmar la VM VMware **apagada** y entonces reiniciar Windows; posteriormente restaurar la plataforma si hace falta para demostración.

[Plan de cierre de la práctica](https://github.com/recm0708/netlab360/blob/main/docs/gestion/plan-aceleracion-y-cierre-practico-20261114.md). Esta issue es una **dependencia técnica de seguridad** y se prioriza antes del reinicio, aunque su milestone administrativo siga siendo S08.

## Corte del 15/11/2026 — suspensión VMware solicitada y fallo de formato ICMP en 134B

- [x] **134A** completado: 10/10 tests offline; `S05_SDN_FAUCET_OPENFLOW=CONNECTED`, 25 reglas, pings A/B y aislamiento C correctos, gestión `ens33=192.168.47.40/24` GW `.2`, repo limpio.
- [x] **134B diagnosticado**, NO completado: estado SDN active, 31 reglas OpenFlow; ping negativo A→C regresó RC1 y `10 packets transmitted, 0 received, +10 errors, 100% packet loss`. El parser solo aceptaba `received, 100%` sin `+10 errors` y 2 enviados; abortó sin FIN_CAPTURA ni marcador OK. Reintento sufrió caída SSH; otro reprodujo lo mismo. **Captura S05_60 pendiente** y 134C no iniciado.
- [x] [PR #131](https://github.com/recm0708/netlab360/pull/131) CI OK y fusionada (commit `d49ff77b`): corregir parsing de salidas iputils con `+N errors` y múltiples transmisiones negativas de ARP, manteniendo RC1+0 recibidos+100% pérdida como gate, rechazando RC124/RC2/timeout, conservando exigencia 2/2 RC0 en A→B. Tests reproducen el caso real.
- [ ] **Pausa operativa antes de más pruebas:** usuario desea reiniciar Windows. Verificar espacio de volumen anfitrión vs RAM guest, baseline en TXT, sincronizar disco y **suspender completamente `netlab360-lab` en VMware Workstation** antes de reiniciar Windows. La suspensión aún **no está confirmada**, ni la reanudación. No reiniciar guest Ubuntu; los netns efímeros requieren estado de RAM conservado. No borrar .vmss/.vmem/.lck, no snapshots permanentes.
- [ ] Tras reanudar, verificar fecha, ens33/route, Faucet/OpenFlow, contenedor/3 namespaces, FRR/LACP/HA/NOC. Entonces repetir **solo** captura 60 con el parser corregido, usando un TXT nuevo que preserve el histórico fallido; completar regresión global y SHA256, y auditar PNG.

## Corte 15/11/2026 — VMware reanudada; LACP status detectó falso drift de tabla completa

- [x] VMware Workstation restauró el estado suspendido de Ubuntu tras reinicio Windows: NTP sincronizado, `ens33=192.168.47.40/24`, default GW `.2`, 21 namespaces y cuatro contenedores (FRR x3 y Faucet) activos.
- [x] SDN state active, OpenFlow connected con 28 reglas, VLAN410 A↔B comunicada y VLAN420 C aislado, baseline S02/FRR/gestión conservado.
- [ ] **LACP de HQ**: bonds 2/2 y cuatro pings OK, pero `status` lanzó `Red de gestión cambió respecto del precheck` al comparar texto literal de TODA la tabla de rutas. La diferencia exacta frente al state-hq.json aún requiere auditoría; S1/S2 y seis servicios no llegaron a validarse en esa ejecución. `NETLAB360_REANUDACION=OK` no apareció.
- [x] [PR #132](https://github.com/recm0708/netlab360/pull/132) CI OK fusionada (`78a03738`): HQ/S1/S2 comprueban ens33 IPv4 y rutas propias/defaults protegidas, no exigen rutas ajenas idénticas; no cambia JSON de state ni configuraciones. Seis pruebas de regresión rechazan drift real.
- [x] [PR #133](https://github.com/recm0708/netlab360/pull/133) fusionada: [lotes 135A/B/C](https://github.com/recm0708/netlab360/blob/main/docs/operacion/s05-lotes-135a-135c-reanudacion-y-captura60-20261115.md), sin acciones mutantes.
- [ ] Ejecutar 135A auditoría baseline actual, 135B revalidación completa HQ/S1/S2/SDN/HA/NOC, 135C evidencia 60 con parser ICMP corregido (PR #131). Logs históricos parciales 10/14/19 se preservan; PNG 60 sigue pendiente.

## Corte verificado 15/11/2026 — 135A/B/C completos, S05_60 obtenida; siguientes 136–138

- [x] **135A**: 23/23 tests aprobados (6 gestión+10 HQ+7 sucursales). La diferencia exacta de gestión es `docker0 172.17.0.0/16`: la ruta antigua tenía `linkdown` y la actual no; IPv4 `ens33=192.168.47.40/24` y ruta predeterminada `.2` iguales, las 3 sedes pasaron protección crítica.
- [x] **135B**: LACP HQ/S1/S2 2/2 en ambos extremos, 4 pings por sitio OK, HA/FIB/VLAN conservados; Faucet OpenFlow conectado 28 reglas, segmentación A/B-C correcta; rutas OSPF HQ→S1 por s1p, HQ→S2 por s2p, seis servicios activos, NTP, Git limpio. `LOTE135B_VMWARE_REANUDACION_COMPLETA=OK`.
- [x] **135C**: 13/13 tests de parser, OpenFlow 31 reglas; A→B `RC0 2/2`, A→C y C→A `RC1, 0 recibidos, 100% pérdida` (10 transmisiones por ARP). `S05_SDN_CAPTURA60=OK_BLOQUEO_VALIDADO_SIN_TIMEOUT_EXTERNO`, `LOTE135C_EVIDENCIA60=OK`. El operador **confirma haber guardado S05_60**; la existencia y SHA-256 del PNG original no se han auditado.
- [x] [PR #134](https://github.com/recm0708/netlab360/pull/134) fusionada (CI success, commit `9925ce62`): script S05 de pérdida/restauración **solo de sdna0** con precheck de ownership, timer restore-only systemd de 120s y pruebas ICMP/OpenFlow/servicios sin tocar ens33/FRR/LACP. [PR #135](https://github.com/recm0708/netlab360/pull/135) fusionada: punto de reanudación actualizado.
- [ ] **Próximas ejecuciones, aún NO realizadas en la VM:** [lotes 136, 137A, 137B y 138](https://github.com/recm0708/netlab360/blob/main/docs/operacion/s05-lotes-136-138-aceptacion-y-falla-sdn-20261115.md): hashes TXT estáticos, precheck, falla/retorno protegida puerto A y regresión. Capturas S05_61 y S05_62 pendientes. No repetir 135 ni fault LACP. La resiliencia de puerto SDN no es HA física/instancia.

