# NETLAB360 — Punto de reanudación

**Corte técnico: 10/11/2026; mantenimiento S05/P0 ejecutado y sincronización GitHub corregida.** S01–S04 están cerradas por criterios internos, con 28/28 issues de esas cuatro milestones cerradas y todas las casillas de aceptación marcadas. Los **contadores nativos de GitHub ya muestran 100 % en S01–S04** y S05 reconoce sus siete issues abiertas. Ver [auditoría y solución verificada](control/06-tablero-porcentajes-cierre-fases-2026-10-25.md). La profesora confirmó en la sesión del **30/10/2026** que el avance estaba bien y que continuáramos con el siguiente entregable, según informó el equipo. El proyecto semestral **aún no está entregado ni aprobado en su totalidad**.

## Estado

| Fase | Resultado | Issue |
|---|---|---|
| S01 | VMware/Ubuntu, red protegida, OSPF, VLAN/ACL, LACP, SSH ED25519 endurecido | [#1](https://github.com/recm0708/netlab360/issues/1) |
| S02 | HQ/S1/S2, 4 WAN, 9 VLAN, OSPF 4/2/2, fallos y recuperación | [#2](https://github.com/recm0708/netlab360/issues/2) |
| S03 | SoT candidate, Ansible FRR 8/8, drift 100→150→100, OpenTofu metadata-only 17/17 y CI | [#3](https://github.com/recm0708/netlab360/issues/3) |
| S04 | Colector/NOC/Prometheus, alertas y eventos, TSDB/SQLite, SLI medidos | [#4](https://github.com/recm0708/netlab360/issues/4) |
| S05 | Redundancia avanzada, SDN OVS/Faucet y visualización de topología | [#5](https://github.com/recm0708/netlab360/issues/5) |

**S03:** OpenTofu no gestionó recursos externos; ampliación reprogramada a [#17](https://github.com/recm0708/netlab360/issues/17) sin darla por implementada. **S04:** SLI 15m 450/450 (100 %) y 60m 1698/1740 (**97,586 %**, 42 fallos). El umbral 99 % se adoptó como referencia interna, incumplida en 60m; no es SLA ni aprobación individual docente del indicador. Avisos únicamente locales.

**Documento:** borrador 4.6, 113 páginas, figuras 1–20 y tablas 1–13. **Evidencias:** 122 PNG oficiales (83/9/8/22) y manifiestos SHA-256. El próximo encuentro docente previsto es **13/11/2026**, con fundamento técnico y diseño [#48](https://github.com/recm0708/netlab360/issues/48). No se ha celebrado aún.

## Reanudar S05 sin repetir S01–S04

1. Encender la **misma VM** `netlab360-lab` solo cuando se retome el trabajo; no clonar ni restaurar snapshots sin necesidad.
2. Comprobar `ens33=192.168.47.40/24`, gateway `192.168.47.2` y acceso por clave ED25519 desde Windows.
3. Ejecutar `git pull --ff-only origin main` después de confirmar un árbol local limpio.
4. Diseñar primero prechecks, fuentes de estado y reversión para LACP multistream, OVS/Faucet, alta disponibilidad y grafo NOC [#64](https://github.com/recm0708/netlab360/issues/64). Sin inventar tráfico ni alterar la interfaz administrativa.
5. Conservar las pruebas y documentación S01–S04 como historial ya aceptado; crear nuevas evidencias solo para funcionalidades realmente implementadas.


## Plan de arranque S05 preparado documentalmente — 10/11/2026

**Estado:** diseño y backlog preparados en #5, #23, #24, #31, #32 y #64. El [precheck S05/P0 de solo lectura](../scripts/validacion/s05-precheck-solo-lectura.sh) quedó versionado el 10/11/2026, y **se ejecutó y revalidó contra la VM original el 10/11/2026**: 0 fallos, 1 aviso esperado por acceso no privilegiado al socket Docker; SQLite S04 `quick_check=ok`, gestión y Git correctos. Las capturas P0 de precheck fueron confirmadas por el operador. El mantenimiento del SO/kernel/Snap se completó y verificó sin alterar la red; registro en [sesión S05 mantenimiento](sesiones/2026-11-10-s05-mantenimiento-precheck.md). Aún **no** se ha ejecutado LACP multistream, HA ni SDN. El orden operativo recomendado es:

1. **P0, baseline seguro (HECHO 10/11/2026):** comprobados VM, SSH, `ens33`, Git `main`, topología desmontada, SQLite/TSDB. Precheck 0 fallos. Sistema actualizado, validado tras reinicio. No restaurar snapshots permanentes ni duplicar VMs.
2. **P1, LACP medido (#31):** [piloto acotado de 1 y 8 flujos con iperf3](../scripts/laboratorio/s05-lacp-multistream-piloto.sh) preparado, **sin ejecutar aún**. Medir tasa recibida, distribución por miembro, 2→1→2 y continuidad; luego planificar ensayo de capacidad sin límite en condiciones seguras. No extrapolar el límite configurado de 120 Mb/s por flujo a capacidad física. Reutilizar pruebas S01 solo como referencia.
3. **P2, redundancia de equipo/servicio (#32):** aislar ensayos de router/switch/servidor alterno, comprobar servicio extremo a extremo bajo falla de equipo y retorno, y preservar la gestión VMnet8. No equiparar caída de interfaz con alta disponibilidad física.
4. **P3, dominio SDN aislado (#23):** instalar y comprobar OVS/Faucet dentro del laboratorio autorizado, con control de bucles, VLAN/ACL, pruebas de fallo/restauración y rollback. Evaluar #24 (WireGuard/sede extra) como opcional por retorno académico.
5. **P4, NOC gráfico (#64):** reutilizar el exporter S04, Prometheus y SoT candidata mediante un modelo de estado **solo lectura**. Representar HQ/S1/S2, 3 FRR, 4 WAN principal/respaldo, 3 switches, 9 VLAN y 9 hosts, sumando equipos SDN/HA exclusivamente cuando existan. Verde: ruta principal elegida; azul: respaldo en uso; turquesa/discontinuo: respaldo standby; ámbar: transición/degradación; rojo: fallo observado; gris: UNKNOWN/offline. Animación de paquetes solo con contadores de tráfico válidos; si se conoce solo ruta, etiquetar *ruta seleccionada* y no inventar tráfico.
6. **P5, aceptación:** verificar baseline, failover S1 sin afectar S2, restauración, UNKNOWN, tests offline, historial/tiempos y evidencia `S05_*`. Actualizar informe único y manifiestos SHA-256 con resultados efectivos.

**Restricciones:** no publicar NOC en `0.0.0.0`, no modificar `ens33 192.168.47.40/24`, no ejecutar infraestructura de prueba en red administrativa, no borrar recursos de otros proyectos y no activar acciones de reparación automáticas sin aprobación humana. Empezar la ejecución real con una auditoría de solo lectura y validar sus salidas antes de cambiar la topología.

El 01/11 la VM estaba **encendida** durante el cierre de S01; su apagado final de sesión se verificará desde VMware antes de apagar el PC. No deducir estado Powered Off de la bitácora anterior de octubre.

[Control de fases](control/06-tablero-porcentajes-cierre-fases-2026-10-25.md) · [Corte académico](academico/s04-guion-de-actualizacion-del-informe.md).
