# NETLAB360 — Estado consolidado

**Actualizado: 01/11/2026.** Cerramos técnicamente las fases S01–S04 conforme a los resultados implementados. La aceptación académica y la ratificación del objetivo SLO S04 continúan pendientes; el trabajo funcional S05–S08 aún no se ha ejecutado.

## Componentes demostrados

Desplegamos un laboratorio HQ/S1/S2 con cuatro enlaces WAN, nueve VLAN, costos OSPF preferidos y de respaldo, verificación Ansible FRR y 17 metadatos OpenTofu. En S04 incorporamos colector multisede, Prometheus, NOC e historial de eventos persistente. La funcionalidad externa de OpenTofu quedó reprogramada y no se considera implementada.

**Métricas S04:** 15m: 450/450 (100 %); 60m: 1698/1740 (97,586 %, 42 fallos). El objetivo 99 % es candidato no ratificado. No demostramos SLA de aplicaciones ni avisos externos.

## Evidencias y escrito

Conservamos 122 PNG oficiales (83/9/8/22) sometidas a manifiestos SHA-256. El informe único, borrador 4.6, consta de 113 páginas, 20 figuras y 13 tablas, con resultados hasta S04. La revisión docente sigue sin dictamen registrado.

## Administración de la VM

La VM `netlab360-lab` funciona en `192.168.47.40/24`, `ens33`, gateway `192.168.47.2`. Verificamos acceso SSH ED25519, respaldo privado de configuración, consola de recuperación y contraseñas remotas deshabilitadas el 01/11. La VM volvió a encenderse ese día; el apagado anterior de S04 es histórico, no su estado actual.

[Reanudación](REANUDAR-AQUI.md) · [Fases](control/06-tablero-porcentajes-cierre-fases-2026-10-25.md).
