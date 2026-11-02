# NETLAB360 — Reanudar aquí

**Corte 01/11/2026.** Fases S01, S02 y S03 **cerradas internamente**. S04 validada técnicamente; ratificación del SLO académico y reporte de revisión docente pendientes. Fases S05–S08 aún no completadas.

## Estado de los componentes

- **S01:** plataforma VMware/Ubuntu operativa; SSH endurecido y acceso por clave ED25519 verificado, respaldo de configuración y recuperación local VMware comprobados. [Cierre #1](https://github.com/recm0708/netlab360/issues/1) y [seguridad #38](https://github.com/recm0708/netlab360/issues/38).
- **S02:** 3 sedes HQ/S1/S2, cuatro WAN, nueve VLAN, OSPF Full 4/2/2 y failover, HTTP/ACL. [Cierre #2](https://github.com/recm0708/netlab360/issues/2).
- **S03:** SoT `candidate` validada **para laboratorio**, Ansible FRR 8/8 y reconciliación de drift, OpenTofu de **17 metadatos `terraform_data`**, CI/GitOps. [Cierre #3](https://github.com/recm0708/netlab360/issues/3). La integración de recursos externos se **reprogramó S05+** en [#17](https://github.com/recm0708/netlab360/issues/17), sin considerarla ejecutada.
- **S04:** colector, Prometheus, NOC, alerta WAN real, estado UNKNOWN y persistencia TSDB/SQLite comprobados. Scrapes 15m 450/450 (100 %) y 60m 1698/1740 (**97,586 %**, 42 fallos); 99 % sigue siendo objetivo académico candidato. [Fase #4](https://github.com/recm0708/netlab360/issues/4) y [decisión SLO #21](https://github.com/recm0708/netlab360/issues/21) abiertas.
- **Escrito:** informe único 4.6, 113 páginas, figuras 1–20 y tablas 1–13, con S01–S04 analizadas; aprobación docente no confirmada.
- **Evidencias:** 83+9+8+22 = **122 PNG oficiales** con manifiestos de integridad.

## VM y continuidad

`netlab360-lab` utiliza `192.168.47.40/24` en `ens33` y gateway `192.168.47.2`. Fue encendida el 01/11 para cerrar S01; no asumir que siga apagada por el cierre histórico S04. Verificar el estado VMware cuando se termine la sesión y usar apagado ordenado. Los respaldos y credenciales permanecen fuera de Git.

**Prioridad inmediata:** resolver la aceptación interna de S04 sin reproducir sus incidentes; registrar qué ocurrió realmente en la revisión del 30/10 y después comenzar S05. No repetir FRR, Ansible, OpenTofu ni los ensayos WAN de fases cerradas.

[Control de fases](control/06-tablero-porcentajes-cierre-fases-2026-10-25.md) · [S01–S03](control/07-puertas-cierre-fases1-a-3-2026-10-25.md) · [Github Issues](https://github.com/recm0708/netlab360/issues).
